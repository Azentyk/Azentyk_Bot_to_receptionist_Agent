from fastapi import FastAPI, Request, Response
import state
# from queue_service import refresh_pending_patients,trigger_next_call
import asyncio
from twilio.twiml.voice_response import VoiceResponse, Gather
from ai_service import generate_ai_response
import json
from config import PUBLIC_URL
from fastapi import APIRouter, Request, Response

router = APIRouter()

@router.post("/answer")
async def answer_call(request: Request):
    form_data = await request.form()
    caller = form_data.get("From", "")
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response("Session ID missing", media_type="text/plain", status_code=400)

    resp = VoiceResponse()
    state.conversation_state[caller] = {"counter": 0}

    user_details = state.user_agents.get(session_id)
    if not user_details:
        return Response("Session not found", media_type="text/plain", status_code=404)

    initial = f"Patient Details: {user_details['configurable']['patient_data']}"
    result = await generate_ai_response(initial, user_details)
    last = result["messages"][-1].content.replace("<END_OF_TURN>", "").strip()

    gather = Gather(
        input="speech",
        action=f"{PUBLIC_URL}/process_speech?session_id={session_id}",
        method="POST",
        language="en-us",
        speech_timeout="auto",
        timeout=20,
        enhanced=True,
        speech_model="googlev2_long",
        hints="yes, no, confirm, cancel, reschedule, appointment",
    )
    gather.say(last, voice="Google.en-IN-Chirp3-HD-Puck")
    resp.append(gather)
    return Response(content=str(resp), media_type="text/xml")
