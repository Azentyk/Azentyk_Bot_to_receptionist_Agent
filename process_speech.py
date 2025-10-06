from fastapi import FastAPI, Request, Response
import state
import asyncio
from twilio.twiml.voice_response import VoiceResponse, Gather
from ai_service import generate_ai_response
import json
from prompt import bot_receptionist_doctor_appointment_patient_data_extraction
from model import llm_model
from db_utils import update_appointment_status
from utils import get_queue_lock,now_ts,get_formatted_date
from queue_service import remove_from_queue_by_appt_id
from config import PUBLIC_URL
import re
from fastapi import APIRouter, Request, Response

router = APIRouter()
llm = llm_model()

@router.post("/process_speech")
async def process_speech(request: Request):
    form_data = await request.form()
    caller = form_data.get("From", "")
    user_speech = (form_data.get("SpeechResult", "") or "").lower().strip()
    session_id = request.query_params.get("session_id")
    resp = VoiceResponse()

    print("user_speech :",user_speech)

    state1 = state.conversation_state.get(caller, {"counter": 0})
    state1["counter"] += 1

    if any(p in user_speech for p in ["thanks", "thank you", "ok thanks", "that's all"]):
        resp.say("You're welcome! Goodbye!")
        state.conversation_state.pop(caller, None)
        return Response(content=str(resp), media_type="text/xml")

    user_details = state.user_agents.get(session_id)
    if not user_details:
        return Response("Session not found", media_type="text/plain", status_code=404)

    result = await generate_ai_response(user_speech, user_details)
    last = result["messages"][-1].content.replace("<END_OF_TURN>", "").strip()
    print("[AI] reply:", last)
    
    if "appointment_status" in last:
        json_matches = re.findall(r"\{.*?\}", last)
        json_objects = [json.loads(m) for m in json_matches if m]
        if json_objects:
            status = json_objects[0].get("appointment_status")
            if status in ["confirmed", "rescheduled", "cancelled", "cancelling"]:
                patient_data = bot_receptionist_doctor_appointment_patient_data_extraction(llm).invoke(str(result["messages"]))
                appt_id = patient_data.get("appointment_id")
                if appt_id:
                    update_appointment_status(appt_id, patient_data.get("appointment_status"),patient_data.get("new_date"),patient_data.get("new_time"))
                    async with (await get_queue_lock()):
                        state.processed_ids[appt_id] = now_ts()
                        state.queued_ids.discard(appt_id)
                    await remove_from_queue_by_appt_id(appt_id)

                resp.say(f"Appointment {status}. Updating patient.", voice="Google.en-IN-Chirp3-HD-Puck")
                resp.hangup()
                return Response(content=str(resp), media_type="text/xml")

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
    state.conversation_state[caller] = state1
    return Response(content=str(resp), media_type="text/xml")
