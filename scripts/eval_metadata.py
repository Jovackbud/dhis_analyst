from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.agent.intent import classify_intent


GOLDEN = [
    ("malaria cases", "fbfJHSPpUQD"),
    ("ANC coverage", "Uvn6LCg7dVU"),
    ("opv3 dropout", "rXoaHGAXWy9"),
    ("cholera suspected cases", "vc6J1qOWsNR"),
    ("coverage rate", "Jtf34kNZhzP"),
]


def main() -> None:
    hits = 0
    for term, expected_uid in GOLDEN:
        result = classify_intent(term)
        uid = result["metrics"][0]["uid"] if result["metrics"] else None
        ok = uid == expected_uid
        hits += int(ok)
        print(f"{term}: expected={expected_uid} actual={uid} ok={ok}")
    accuracy = hits / len(GOLDEN)
    print(f"top_1_accuracy={accuracy:.2%}")
    raise SystemExit(0 if accuracy >= 0.9 else 1)


if __name__ == "__main__":
    main()
