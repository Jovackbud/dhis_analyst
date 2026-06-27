# DHIS2 Public Health Intelligence Assistant
## Final Consolidated System Specification

> Synthesised from five independent LLM proposals.  
> Audience: non-technical stakeholders (Part 1) and developers / AI coding agents (Part 2).  
> Status: production-grade, all phases detailed.

---

## Part 1 — For Non-Technical Stakeholders

### What this product is

This is a conversational AI assistant built for public health analysts. Instead of navigating complex database menus, writing queries, or manually copying data into Word and PowerPoint, an analyst types a plain-English question and the system responds with whatever is most useful — a quick answer, an interactive dashboard, a downloadable report, a slide deck, or a raw data table.

Example requests the system handles:

- "Show me malaria trends in Kaduna over the last three quarters."
- "Compare ANC coverage across districts and flag the bottom five."
- "Prepare a monthly programme review briefing with charts and recommendations."
- "Give me the raw numbers in Excel."
- "What does WHO say about recent cholera outbreaks in West Africa?"

The system works for two types of users in the same product:

- **Analysts with a DHIS2 account** — they log in once through the app and their data permissions are automatically respected. They only see the data DHIS2 already allows them to see.
- **External stakeholders without a DHIS2 account** — they access curated outputs (reports, dashboards, exports) through a separate login that controls what is shared with them.

### Key benefits

- Reduces hours of manual data extraction and report writing to minutes of conversation.
- Combines your organisation's internal DHIS2 data with real-time external context (WHO guidelines, outbreak news, policy updates) when useful.
- Outputs are professional and editable — analysts can revise a report in the browser before downloading it as Word, PDF, or PowerPoint.
- All data permissions are inherited from DHIS2 — no analyst sees data they are not authorised to view.
- Works with any major AI provider (OpenAI, Anthropic, local models) — no lock-in.

---

## Part 2 — Technical Specification

### Confirmed architectural decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI (Python, async) | Native asyncio for SSE streaming; well-tested in production |
| Agent orchestration | LangGraph | Explicit typed state machine; auditable branching logic |
| Primary data path | DHIS2 Analytics API | Respects permissions, stable across DHIS2 versions |
| SQL fallback | Read-only Postgres, validated queries | Safety-gated; for queries the API cannot express |
| Metadata resolution | pgvector semantic layer | Maps NL → DHIS2 UIDs; synced nightly |
| Web enrichment | Tavily (opt-in per query) | Clean LLM-ready snippets; restricted to trusted domains |
| LLM backend | Provider-agnostic via LiteLLM | Swap OpenAI / Claude / Ollama via env var; same code |
| Frontend framework | Preact + Vite | React component model at 3 KB; no heavy build overhead |
| Chart library | Plotly.js | Interactive; exports to PNG for embedding in DOCX/PPTX |
| Report editor | Tiptap (vanilla core) | Extensible; no React wrapper needed; Table extension included |
| DOCX generation | python-docx | Pure Python; covers all report needs |
| PPTX generation | python-pptx | Pure Python; chart images embedded as PNG |
| PDF generation | WeasyPrint (primary), Playwright (fallback for complex charts) | CSS-based; consistent branding |
| XLSX / CSV | openpyxl / pandas | Standard; three-sheet XLSX (Data, Metadata, Sources) |
| Deployment mode | `DEPLOYMENT_MODE=dhis2 \| standalone` env var | Single codebase; Vite build flag switches auth adapter |
| Evidence provenance | Evidence fusion layer on every insight | Source + confidence tag; on/off via `EVIDENCE_FUSION=true` |
| Web enrichment audit | Per-query audit log | On/off via `AUDIT_WEB_SEARCH=true` |
| On-prem LLM | Ollama / vLLM via LiteLLM | Activated by setting `LLM_PROVIDER=ollama` |

---

### Repository structure

```
dhis2-analyst/
├── backend/
│   ├── main.py                        # FastAPI entrypoint, CORS, auth middleware
│   ├── config.py                      # Settings (pydantic-settings); all env vars
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py               # LangGraph state machine definition
│   │   │   ├── state.py               # AgentState TypedDict
│   │   │   ├── intent.py              # Intent classifier node
│   │   │   ├── nodes/
│   │   │   │   ├── metadata_resolve.py
│   │   │   │   ├── fetch_dhis2.py
│   │   │   │   ├── fetch_sql.py
│   │   │   │   ├── enrich_web.py
│   │   │   │   ├── generate_content.py
│   │   │   │   └── evidence_fusion.py
│   │   │   └── renderers/
│   │   │       ├── conversational.py
│   │   │       ├── dashboard.py
│   │   │       ├── report.py
│   │   │       ├── presentation.py
│   │   │       └── export.py
│   │   ├── dhis2/
│   │   │   ├── client.py              # DHIS2 HTTP client (requests + PAT or service account)
│   │   │   ├── analytics.py           # Analytics API query builder
│   │   │   └── metadata_sync.py       # Nightly pgvector sync job
│   │   ├── generators/
│   │   │   ├── docx_gen.py
│   │   │   ├── pptx_gen.py
│   │   │   ├── pdf_gen.py
│   │   │   └── xlsx_gen.py
│   │   ├── auth/
│   │   │   ├── dhis2_adapter.py       # Extracts PAT from DHIS2 session
│   │   │   └── standalone_adapter.py  # JWT-based auth for external stakeholders
│   │   ├── db/
│   │   │   ├── metadata_index.py      # pgvector table schema + upsert
│   │   │   └── session.py             # SQLAlchemy async session
│   │   └── models.py                  # Pydantic schemas (IntentObject, AgentState, etc.)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.jsx                   # Preact app mount
│   │   ├── auth/
│   │   │   ├── dhis2Auth.js           # d2 library token adapter
│   │   │   └── standaloneAuth.js      # JWT login flow
│   │   ├── components/
│   │   │   ├── Chat.jsx               # Main conversation interface
│   │   │   ├── Dashboard.jsx          # Plotly chart grid (reactive)
│   │   │   ├── ReportEditor.jsx       # Tiptap editor + download bar
│   │   │   ├── DownloadBar.jsx        # DOCX / PDF / PPTX / XLSX buttons
│   │   │   ├── EvidenceTag.jsx        # Source + confidence badge (toggled by env)
│   │   │   └── ClarificationPrompt.jsx
│   │   └── lib/
│   │       ├── stream.js              # SSE event parser (typed events)
│   │       └── plotly.js              # Plotly wrapper utilities
│   └── manifest.webapp                # DHIS2 app manifest (used when DEPLOYMENT_MODE=dhis2)
├── scripts/
│   └── seed_metadata.py               # One-time metadata index seed
├── docker-compose.yml
└── .env.example
```

---

### Environment variables (`.env.example`)

```bash
# Deployment
DEPLOYMENT_MODE=standalone            # standalone | dhis2

# DHIS2
DHIS2_BASE_URL=https://play.dhis2.org/dev
DHIS2_SERVICE_ACCOUNT_USER=admin
DHIS2_SERVICE_ACCOUNT_PASS=district  # used only in standalone mode for metadata sync

# LLM — provider-agnostic via LiteLLM
LLM_PROVIDER=openai                   # openai | anthropic | ollama | azure
LLM_MODEL=gpt-4o                      # model string passed to LiteLLM
LLM_API_KEY=sk-...                    # not needed for Ollama
LLM_BASE_URL=                         # set for Ollama: http://localhost:11434

# Embedding model (for pgvector)
EMBEDDING_PROVIDER=openai             # openai | cohere | ollama
EMBEDDING_MODEL=text-embedding-3-small

# Tavily
TAVILY_API_KEY=tvly-...
TAVILY_TRUSTED_DOMAINS=who.int,cdc.gov,afro.who.int,unicef.org,.gov

# Features
EVIDENCE_FUSION=true                  # tag every insight with source + confidence
AUDIT_WEB_SEARCH=true                 # log all Tavily queries per session
ENABLE_DIRECT_SQL=false               # gate the Postgres fallback path

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dhis2_analyst

# Session
REDIS_URL=redis://localhost:6379
JWT_SECRET=change-me-in-production

# File storage
TEMP_FILE_DIR=/tmp/dhis2_analyst
MAX_FILE_AGE_SECONDS=3600
```

---

### Agent state object

```python
# backend/app/agent/state.py

from typing import TypedDict, Literal, Optional

class MetricRef(TypedDict):
    label: str
    uid: str                         # resolved DHIS2 UID
    uid_confidence: float            # 0.0–1.0 from pgvector cosine similarity
    object_type: str                 # dataElement | indicator | programIndicator

class OrgUnitRef(TypedDict):
    label: str
    uid: str
    level: int

class EvidenceItem(TypedDict):
    claim: str
    source: Literal["dhis2", "tavily", "llm"]
    source_detail: str               # DHIS2 indicator name or Tavily URL
    confidence: float                # 0.0–1.0

class AgentState(TypedDict):
    # Conversation
    messages: list
    session_id: str
    user_id: str
    user_role: Literal["dhis2_user", "external_stakeholder"]

    # Intent
    output_mode: Literal[
        "conversational", "dashboard", "report", "presentation", "export"
    ]
    metrics: list[MetricRef]
    org_unit: OrgUnitRef
    periods: list[str]              # DHIS2 period codes: ["2024Q1","2023Q4"]
    disaggregations: list[str]
    viz_types: list[str]
    needs_web_enrichment: bool
    web_search_queries: list[str]
    data_retrieval_strategy: Literal["analytics_api", "direct_sql", "both"]
    clarification_needed: bool
    clarification_question: Optional[str]

    # Data
    dhis2_data: dict                # normalised {rows, headers, metadata}
    web_context: list[dict]         # Tavily results

    # Evidence fusion (active when EVIDENCE_FUSION=true)
    evidence_items: list[EvidenceItem]

    # Output state
    active_report_html: str
    active_chart_configs: list
    active_slide_manifest: list
    generated_file_id: Optional[str]
```

---

### LangGraph state machine

```
[classify_intent]
        │
        ├─ clarification_needed=true → [return_clarification] → END (await user)
        │
        └─ clarification_needed=false
                │
                ▼
        [resolve_metadata]          # pgvector UID lookup; confidence gate
                │
                ├─ low_confidence → [return_disambiguation] → END (await user)
                │
                └─ resolved
                        │
                        ▼
                [fetch_dhis2]       # branches: analytics_api | direct_sql | both
                        │
                        ▼
                [enrich_web]        # conditional: only if needs_web_enrichment=true
                        │
                        ▼
                [evidence_fusion]   # conditional: only if EVIDENCE_FUSION=true
                        │
                        ▼
                [generate_content]
                        │
                        ▼
                [route_to_renderer]
                        │
                        ├─ conversational  → stream markdown + evidence tags
                        ├─ dashboard       → stream chart_config events
                        ├─ report          → stream report_html event
                        ├─ presentation    → stream slide_manifest event
                        └─ export          → stream data_ready event
```

---

### Intent classifier

The intent classifier is the most critical prompt in the system. A misclassified intent corrupts the entire pipeline. Engineering effort here pays the highest returns.

The system prompt for the classifier must include:

1. A compressed snapshot of available metadata (top 50 indicators, org unit levels, available period codes relative to today's injected as `{today}`).
2. Output mode definitions with decision criteria and trigger examples for each.
3. Web enrichment criteria: invoke when the query involves benchmarks, external guidelines, outbreak context, policy changes, or environmental factors.
4. Period resolver: translate "last quarter", "year to date", "2023" into DHIS2 period codes.
5. At least 10 few-shot examples covering ambiguous cases.

**Ambiguous case examples to include in the prompt:**

| User input | Correct classification |
|---|---|
| "Give me a quick look at ANC data" | dashboard, not report |
| "Why is OPV3 dropout high in Sokoto?" | conversational + web enrichment |
| "Prepare the monthly programme review" | report + presentation |
| "Numbers for last week" | export |
| "How does our coverage compare to the national target?" | conversational + web enrichment |

**Metadata confidence gate:** If top pgvector match confidence < 0.82, surface top 3 candidates to the user for disambiguation. Do not guess silently.

**Quality gate before Phase 2:** Run the UID resolver against 50 real analyst terms from your DHIS2 instance. Target ≥ 90% top-1 accuracy. If below, tune the embedding text (try appending associated dataset names), lower the confidence threshold to force more disambiguation prompts, and re-evaluate. This gate is non-negotiable — a wrong indicator silently poisons all downstream output.

---

### DHIS2 data retrieval

**Analytics API path (default):**

```python
# backend/app/dhis2/analytics.py

def build_analytics_params(state: AgentState) -> dict:
    dx = ",".join(m["uid"] for m in state["metrics"])
    ou = f"LEVEL-{state['org_unit']['level']};{state['org_unit']['uid']}"
    pe = ",".join(state["periods"])
    params = {
        "dimension": [f"dx:{dx}", f"ou:{ou}", f"pe:{pe}"],
        "displayProperty": "NAME",
        "outputIdScheme": "NAME",
        "skipMeta": "false",
    }
    if state["disaggregations"]:
        params["dimension"].append(f"co:{','.join(state['disaggregations'])}")
    return params
```

**Normalised result shape (all retrieval paths produce this):**

```python
{
    "rows": [["Kano", "2024Q1", 1240], ...],
    "headers": ["Organisation unit", "Period", "Malaria Confirmed Cases"],
    "metadata": {
        "indicators": [...],
        "org_units": [...],
        "periods": [...],
        "data_source": "analytics_api"   # or "direct_sql"
    }
}
```

**Direct SQL path (gated by `ENABLE_DIRECT_SQL=true`):**

- DB user is read-only, scoped to: `datavalue`, `analytics`, `analytics_*` materialized views, `organisationunit`, `dataelement`, `indicator`, `period`, `categoryoptioncombo`.
- All LLM-generated SQL is parsed and validated before execution. Reject any statement containing: `DROP`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `CREATE`, `ALTER`, `pg_`, `information_schema`, or any table not on the allowlist.
- Query timeout: 10 seconds. Row limit: 10,000.
- Every query logged with session ID for audit.

---

### Metadata sync (pgvector)

```sql
-- Run once on setup
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE metadata_index (
    uid TEXT PRIMARY KEY,
    object_type TEXT,           -- dataElement | indicator | orgUnit | dataSet | programIndicator
    name TEXT,
    short_name TEXT,
    description TEXT,
    dataset_names TEXT,         -- associated dataset names, appended for better embedding signal
    embedding vector(1536),     -- dimension depends on embedding model
    raw_metadata JSONB,
    last_synced_at TIMESTAMPTZ
);

CREATE INDEX ON metadata_index
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

Sync job runs nightly. Pulls from:
- `/api/dataElements?paging=false&fields=id,name,shortName,description,dataSetElements`
- `/api/indicators?paging=false&fields=id,name,shortName,description`
- `/api/organisationUnits?paging=false&fields=id,name,shortName,level`
- `/api/programIndicators?paging=false&fields=id,name,shortName,description`

Embedding text: `name + " " + shortName + " " + description + " " + dataset_names`

---

### Web enrichment (Tavily)

- Fires only when `intent.needs_web_enrichment = true`.
- Uses pre-formulated `web_search_queries` from the intent object — not improvised at enrichment time.
- Filter results to relevance score ≥ 0.7.
- Limit: 3 queries per turn, 5 results per query.
- Restrict to `TAVILY_TRUSTED_DOMAINS` (configurable via env).
- All queries logged when `AUDIT_WEB_SEARCH=true`.
- For sensitive deployments: swap Tavily for a self-hosted SearxNG instance by setting `TAVILY_ENDPOINT` to point at SearxNG's compatible API.

---

### Evidence fusion layer

Active when `EVIDENCE_FUSION=true`. Every insight the content generator produces is tagged with:

```python
EvidenceItem(
    claim="Malaria confirmed cases in Kano increased 26% in 2024Q1 vs 2023Q1",
    source="dhis2",
    source_detail="Malaria Confirmed Cases (indicator: s46m5MS0hxu)",
    confidence=0.97
)
```

The frontend renders these as small collapsible badges below each claim. The `EvidenceTag` component can be toggled off entirely with `EVIDENCE_FUSION=false` — the rest of the pipeline is unaffected.

---

### SSE event taxonomy

The `/api/chat` endpoint returns a Server-Sent Events stream. Every event carries a typed payload. The frontend stream parser routes on `event.type`.

```
event: token          → { text: "..." }                      # streamed text (conversational)
event: chart_config   → { title, type, series, axes, id }    # one per chart (dashboard)
event: report_html    → { html: "..." }                      # full report for Tiptap
event: slide_manifest → [{ type, title, content, data }]     # PPTX slide list
event: data_ready     → { file_id, format, row_count }       # export ready for download
event: clarification  → { question: "..." }                  # surface to user, pause pipeline
event: evidence       → EvidenceItem[]                       # provenance tags
event: error          → { code, user_message, detail }       # structured error
event: done           → {}                                   # stream complete
```

---

### Auth architecture (two-mode)

**DHIS2 user path (`DEPLOYMENT_MODE=dhis2`):**

- Frontend uses the `d2` library to extract the user's DHIS2 session token.
- All DHIS2 API calls are proxied through the backend using the user's Personal Access Token (PAT).
- DHIS2's own sharing rules enforce org unit and data element visibility — no extra layer needed.
- `manifest.webapp` is included in the Vite build and uploaded via DHIS2 App Management.

**External stakeholder path (`DEPLOYMENT_MODE=standalone` or combined):**

- Backend exposes a `/auth/login` endpoint that returns a signed JWT.
- JWT encodes the stakeholder's permitted DHIS2 org units and indicator groups (configured in the admin panel).
- All DHIS2 API calls for external stakeholders use the service account credentials, scoped by the JWT permissions.
- External stakeholders cannot trigger Tavily web search by default (configurable).

**Combined mode:** Both auth adapters run simultaneously. The frontend detects whether it is embedded in DHIS2 (checks `window.d2` availability) and activates the appropriate adapter. A single deployment serves both user types.

---

### File generation

**DOCX (`python-docx`):**
- Input: edited report HTML from Tiptap (`editor.getHTML()`).
- Process: parse HTML into python-docx paragraph/table/heading objects.
- Output: A4, Arial, proper heading hierarchy with `outlineLevel` for TOC, `ShadingType.CLEAR` on table cells.
- Charts embedded as PNG images (rendered by Plotly server-side via `plotly.io.to_image()`).

**PPTX (`python-pptx`):**
- Input: slide manifest JSON from the agent.
- Process: iterate manifest; each slide object maps to a layout (title, title+content, title+chart, title+table).
- Charts rendered to PNG by Plotly before embedding.
- Output: 16:9 widescreen, health-appropriate colour palette.

**PDF (WeasyPrint primary, Playwright fallback):**
- Input: report HTML with print-optimised CSS (page-break rules, no fixed-position elements).
- WeasyPrint handles text-heavy reports. Playwright headless Chrome used as fallback when charts need pixel-perfect rendering.
- Generated from the report HTML directly — not converted from DOCX — to preserve chart fidelity.

**XLSX (`openpyxl`):**
- Three sheets: Data (formatted DHIS2 result rows), Metadata (indicator definitions, org unit info, period descriptions), Sources (Tavily citations if web enrichment was used).

**File lifecycle:**
- Files written to `TEMP_FILE_DIR` with a UUID filename.
- Served via `GET /api/download/{file_id}` with `Content-Disposition: attachment`.
- Cleaned up after `MAX_FILE_AGE_SECONDS` (default 3600).
- In-memory `io.BytesIO()` used where possible to avoid disk writes for small files.

---

### API surface

```
POST  /api/chat                   # Main agent invocation — SSE stream
POST  /api/generate/docx          # Accepts edited report HTML → returns file_id
POST  /api/generate/pdf           # Accepts edited report HTML → returns file_id
POST  /api/generate/pptx          # Accepts slide manifest → returns file_id
POST  /api/export/xlsx            # Accepts data payload → returns file_id
POST  /api/export/csv             # Accepts data payload → returns file_id
GET   /api/download/{file_id}     # Stream file download
GET   /api/metadata/search        # UID resolver (for frontend autocomplete)
POST  /api/metadata/sync          # Trigger manual metadata re-sync
POST  /auth/login                 # Standalone mode: returns JWT
GET   /auth/me                    # Returns current user identity + permissions
GET   /health                     # Liveness check
```

---

### Frontend component map

```
<App>
├── <AuthGate>              # Detects DHIS2 vs standalone; activates correct adapter
├── <Chat>                  # Conversation thread; renders SSE token events as markdown
│   └── <ClarificationPrompt>   # Surfaces clarification events; pauses input
├── <Dashboard>             # Mounts on SSE chart_config events; Plotly grid
│   └── [Plotly chart] × N
├── <ReportEditor>          # Mounts on SSE report_html event; Tiptap editor
│   └── <DownloadBar>       # DOCX / PDF / PPTX buttons; POSTs current HTML
├── <EvidencePanel>         # Collapsible; renders EvidenceItem badges (env-toggled)
└── <AdminPanel>            # Stakeholder permission management (standalone mode)
```

Preact mounts only on `#dashboard-panel`, `#report-editor`, and `#evidence-panel`. The chat interface is plain DOM manipulation for streaming performance. Everything else is plain HTML + CSS.

---

### Phased delivery plan

#### Phase 1 — Core Q&A + data tables (weeks 1–2)

Goal: prove intent classifier and metadata resolver work on 20–30 real analyst queries.

- FastAPI skeleton, config, LiteLLM integration.
- LangGraph graph: `classify_intent` → `resolve_metadata` → `fetch_dhis2` (analytics API only) → `generate_content` (conversational only) → SSE stream.
- Minimal HTML chat UI (no Preact yet). Markdown rendering only.
- XLSX / CSV export via openpyxl / pandas.
- **Exit criterion:** UID resolver hits ≥ 90% top-1 accuracy on 50 real analyst terms. Do not proceed to Phase 2 until this is met.

#### Phase 2 — Dashboard + map (weeks 3–4)

- Add dashboard renderer (Plotly chart config generation).
- Mount Preact + Plotly frontend on `#dashboard-panel`.
- Add `enrich_web` node + Tavily integration.
- Add evidence fusion layer (initially just DHIS2 source tags).

#### Phase 3 — Reports + in-page editing (weeks 5–6)

- Add report renderer (structured markdown → HTML).
- Mount Tiptap editor on `#report-editor`.
- Implement DOCX generation (python-docx) and PDF (WeasyPrint).
- Add `DownloadBar` — POST edited HTML to `/api/generate/docx` and `/api/generate/pdf`.
- Add full evidence fusion (Tavily source tags + confidence scores).

#### Phase 4 — Presentations (week 7)

- Add slide manifest renderer.
- Implement PPTX generation (python-pptx + Plotly PNG chart rendering).
- Add `EvidencePanel` component (environment-toggled).

#### Phase 5 — External stakeholder mode + hardening (week 8)

- Implement standalone auth adapter (JWT login, permission scoping).
- Combined-mode detection in the frontend.
- DHIS2 custom app packaging (manifest.webapp, Vite build flag).
- Direct SQL path (gated behind `ENABLE_DIRECT_SQL=true`).
- Rate limiting (per user, per minute via Redis).
- Audit logging (web search queries, SQL queries, file downloads).
- Integration test suite against `play.dhis2.org/dev`.
- Docker Compose for full local stack (FastAPI + Postgres + pgvector + Redis).

---

### Testing strategy

**Unit tests:** Each agent node with mocked DHIS2 and Tavily responses. Each generator (DOCX, PPTX, PDF, XLSX) with a fixed input payload.

**Integration tests:** Real DHIS2 test instance (`play.dhis2.org/dev`) + test Tavily key. 30 golden prompts covering all output modes, verified against human-checked outputs.

**Security tests:**
- Attempt to access an org unit the authenticated user is not permitted to view via the NL interface — expect 403 from DHIS2.
- Attempt SQL injection via natural language — expect query validator to reject.
- Attempt to access another stakeholder's scoped data via JWT manipulation — expect 401.

**Metadata quality test:** Before Phase 2, run `scripts/eval_metadata.py` — 50 analyst terms vs pgvector resolver. Print top-1 accuracy. Gate is 90%.

---

### The one thing most likely to go wrong

Metadata resolution quality. If "ANC 4 coverage" resolves to the wrong indicator, everything downstream is wrong and the analyst loses trust immediately. Run the quality gate on your specific DHIS2 instance's metadata before any other Phase 2 work. The fix is almost always: richer embedding text (add dataset names and descriptions), or a lower confidence threshold that forces more disambiguation prompts rather than silent wrong answers. A system that asks "did you mean X or Y?" is far better than one that silently pulls the wrong indicator.

---

*End of specification. Proceed to Phase 1.*
