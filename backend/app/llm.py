"""LiteLLM-backed LLM adapter.

Routes all requests through litellm.acompletion(). Requires a configured
LLM provider (openai, anthropic, ollama, azure, etc.) and appropriate
credentials (LLM_API_KEY or LLM_BASE_URL).
"""
from __future__ import annotations

import logging
import time
from typing import Any

from backend.config import Settings

logger = logging.getLogger("dhis2_analyst.llm")


async def complete(
    messages: list[dict[str, str]],
    settings: Settings,
    *,
    json_mode: bool = False,
    temperature: float = 0.3,
) -> str:
    """Call the configured LLM provider and return the assistant message string.

    Args:
        messages:    OpenAI-format message list, e.g. [{"role": "user", "content": "..."}]
        settings:    Application settings.
        json_mode:   Request a JSON response object (provider must support it).
        temperature: Sampling temperature; lower = more deterministic.

    Returns:
        The assistant's response as a string.

    Raises:
        RuntimeError: If the LLM call fails and provider is not mock.
    """
    try:
        import litellm

        model = _resolve_model(settings)
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "timeout": settings.llm_timeout_seconds,
            "num_retries": 1,
        }

        if "gemini" not in settings.llm_provider.lower() and "gemini" not in model.lower():
            kwargs["temperature"] = temperature

        if settings.llm_base_url:
            kwargs["api_base"] = settings.llm_base_url
        if settings.llm_api_key:
            kwargs["api_key"] = settings.llm_api_key
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        logger.info(
            "llm_call",
            extra={
                "provider": settings.llm_provider,
                "model": model,
                "json_mode": json_mode,
                "message_count": len(messages),
            },
        )

        start = time.monotonic()
        response = await litellm.acompletion(**kwargs)
        content = response.choices[0].message.content or ""
        logger.info(
            "llm_call_ok",
            extra={
                "provider": settings.llm_provider,
                "chars": len(content),
                "duration_ms": int((time.monotonic() - start) * 1000),
            },
        )
        return content

    except Exception as exc:
        logger.error(
            "llm_call_failed",
            extra={"error": str(exc), "provider": settings.llm_provider, "model": settings.llm_model},
        )
        raise RuntimeError(f"LLM call failed ({settings.llm_provider}): {exc}") from exc


async def embed(text: str, settings: Settings) -> list[float]:
    """Generate a text embedding vector for semantic search.

    Falls back to an empty list on mock mode (pgvector disabled).
    """
    if settings.embedding_provider == "mock":
        return []

    try:
        import litellm

        model = settings.embedding_model
        if settings.embedding_provider not in {"openai"} and "/" not in model:
            model = f"{settings.embedding_provider}/{model}"

        logger.info(
            "embed_call",
            extra={
                "provider": settings.embedding_provider,
                "model": model,
                "text_len": len(text),
            },
        )
        start = time.monotonic()
        response = await litellm.aembedding(
            model=model,
            input=[text],
            api_key=settings.llm_api_key or None,
            api_base=settings.llm_base_url or None,
        )
        vector = response.data[0]["embedding"]
        logger.info(
            "embed_call_ok",
            extra={
                "provider": settings.embedding_provider,
                "dimensions": len(vector),
                "duration_ms": int((time.monotonic() - start) * 1000),
            },
        )
        return vector
    except Exception as exc:
        logger.error("embed_failed", extra={"error": str(exc)})
        return []


def _resolve_model(settings: Settings) -> str:
    """Build the LiteLLM model string from provider + model settings."""
    provider = settings.llm_provider
    model = settings.llm_model

    if provider == "ollama":
        return f"ollama/{model}"
    if provider in {"openai", "azure", "anthropic", "cohere"} and "/" not in model:
        return f"{provider}/{model}"
    return model


