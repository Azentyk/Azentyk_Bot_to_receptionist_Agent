from fastapi import FastAPI, Request, Response
import state
from queue_service import refresh_pending_patients,trigger_next_call
import asyncio

from fastapi import APIRouter, Request, Response

router = APIRouter()
# --------------------------
# Twilio Call Flow
# --------------------------
@router.post("/call_status")
async def call_status(request: Request):
    form_data = await request.form()
    call_status_text = form_data.get("CallStatus", "")
    session_id = request.query_params.get("session_id")
    print(f"[CALL_STATUS] session={session_id} status={call_status_text}")

    if session_id in state.processed_sessions:
        return Response(content="OK", media_type="text/plain")
    state.processed_sessions.add(session_id)

    state.user_agents.pop(session_id, None)

    # ✅ Move to next call here (single place)
    await refresh_pending_patients()
    await asyncio.sleep(0.2)
    asyncio.create_task(trigger_next_call())
    return Response(content="OK", media_type="text/plain")