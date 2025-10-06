# --------------------------
# Helpers
# --------------------------
import os, re, json, uuid, asyncio, time
from datetime import datetime, timezone
import state


async def get_queue_lock() -> asyncio.Lock:
    if state.queue_lock is None:
        state.queue_lock = asyncio.Lock()
    return state.queue_lock

def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()

def get_formatted_date():
    return datetime.now().strftime("%Y-%m-%d")