from utils import get_queue_lock,now_ts,get_formatted_date
import state
import uuid
from config import PROCESSED_RETENTION_SECONDS
import asyncio
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PUBLIC_URL,RECEPTIONIST_NUMBER,TWILIO_CALLER_ID
from db_utils import get_pending_patient_information_data_from_db



client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# --------------------------
# Queue utilities
# --------------------------
async def enqueue_patient_doc(ele: dict):
    appt_id = ele.get("appointment_id")
    if not appt_id:
        return
    async with (await get_queue_lock()):
        if appt_id in state.queued_ids or appt_id in state.processed_ids:
            return
        patient_data = (
            f"Patient Name: {ele.get('username')}, "
            f"appointment_id: {ele.get('appointment_id')}, "
            f"Hospital Name: {ele.get('hospital_name')}, "
            f"Hospital Location: {ele.get('location')}, "
            f"Specialization: {ele.get('specialization')}, "
            f"Appointment Booking Date: {ele.get('appointment_booking_date')}, "
            f"Appointment Booking Time: {ele.get('appointment_booking_time')}"
        )
        thread_id = str(uuid.uuid4())
        config = {
            "appointment_id": appt_id,
            "configurable": {
                "patient_data": patient_data,
                "current_date": get_formatted_date(),
                "thread_id": thread_id,
            },
        }
        state.call_queue.append(config)
        state.queued_ids.add(appt_id)
        print(f"[QUEUE] Added appointment -> {appt_id}")

async def remove_from_queue_by_appt_id(appt_id: str):
    async with (await get_queue_lock()):
        state.call_queue[:] = [c for c in state.call_queue if c.get("appointment_id") != appt_id]
        state.queued_ids.discard(appt_id)
        if state.current_index >= len(state.call_queue):
            state.current_index = len(state.call_queue) - 1
        print(f"[QUEUE] Removed appointment from queue -> {appt_id}")

async def prune_processed_ids():
    cutoff = now_ts() - PROCESSED_RETENTION_SECONDS
    async with (await get_queue_lock()):
        for k in list(state.processed_ids.keys()):
            if state.processed_ids[k] < cutoff:
                del state.processed_ids[k]
                print(f"[PRUNE] processed_ids pruned -> {k}")


async def trigger_next_call():
    if state.current_index + 1 >= len(state.call_queue):
        print("[INFO] Queue empty ✅ Waiting for new patients...")
        state.is_calling = False
        return
    await asyncio.sleep(3)
    state.current_index += 1
    patient = state.call_queue[state.current_index]
    session_id = f"session_{uuid.uuid4()}"
    state.user_agents[session_id] = patient

    print(f"[INFO] 📞 Calling receptionist: {patient['configurable']['patient_data']}")
    try:
        call = client.calls.create(
            url=f"{PUBLIC_URL}/answer?session_id={session_id}",
            to=RECEPTIONIST_NUMBER,
            from_=TWILIO_CALLER_ID,
            status_callback=f"{PUBLIC_URL}/call_status?session_id={session_id}",
            status_callback_event=["completed", "failed", "busy", "no-answer"],
        )
        print(f"[CALL STARTED] SID={call.sid}, To={RECEPTIONIST_NUMBER}, From={TWILIO_CALLER_ID}")
        state.is_calling = True
    except Exception as e:
        print(f"[ERROR] Twilio call failed: {e}")
        state.is_calling = False

# --------------------------
# Refresh pending patients
# --------------------------
async def refresh_pending_patients():
    await prune_processed_ids()
    for ele in get_pending_patient_information_data_from_db():
        await enqueue_patient_doc(ele)

# --------------------------
# Background polling / startup
# --------------------------
async def fetch_pending_loop():
    while True:
        try:
            await refresh_pending_patients()
            async with (await get_queue_lock()):
                if not state.is_calling and state.call_queue:
                    print("[AUTO-START] queue has items -> starting calls")
                    state.current_index = -1
                    asyncio.create_task(trigger_next_call())
        except Exception as e:
            print(f"[ERROR] fetch_pending_loop: {e}")
        await asyncio.sleep(6)
