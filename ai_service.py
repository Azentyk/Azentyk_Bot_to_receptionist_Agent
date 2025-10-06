# app/services/ai_service.py
import asyncio, time
from bot_to_receptionist import part_1_graph  # Your AI assistant module

async def generate_ai_response(prompt: str, config: dict, min_wait: int = 0):
    """Call the conversational graph/LLM in a thread so it doesn't block the event loop."""
    start_time = time.monotonic()
    result = await asyncio.to_thread(
        part_1_graph.invoke,
        {"messages": ("user", prompt)},
        config=config,
    )
    elapsed = time.monotonic() - start_time
    remaining_wait = max(0, min_wait - elapsed)
    if remaining_wait > 0:
        await asyncio.sleep(remaining_wait)
    return result