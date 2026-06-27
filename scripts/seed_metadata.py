from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import get_settings
from backend.app.dhis2.metadata_sync import sync_metadata


async def main() -> None:
    result = await sync_metadata(get_settings())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
