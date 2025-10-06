from typing import Dict, Optional
import os, re, json, uuid, asyncio, time

conversation_state: Dict[str, dict] = {}
user_agents: Dict[str, dict] = {}
call_queue: list = []
queued_ids: set = set()
processed_ids: dict = {}
current_index = -1
processed_sessions: set = set()
is_calling = False
queue_lock: Optional[asyncio.Lock] = None