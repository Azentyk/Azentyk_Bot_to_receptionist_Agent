# app/main.py
import os
import sys
import pysqlite3
sys.modules["sqlite3"]=pysqlite3
from fastapi import FastAPI
from answer_service import router as answer_router
from process_speech import router as speech_router
from call_status import router as call_router
from queue_service import fetch_pending_loop
from utils import get_queue_lock
import asyncio

app = FastAPI()

app.include_router(answer_router)
app.include_router(speech_router)
app.include_router(call_router)

@app.on_event("startup")
async def startup_event():
    await get_queue_lock()
    asyncio.create_task(fetch_pending_loop())
    print("[INFO] Polling loop started. Waiting for new appointments...")
