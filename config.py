# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

TWILIO_ACCOUNT_SID = "ACaaaa83e9255e4d10cc5ca3168a510b07"
TWILIO_AUTH_TOKEN = "a0df54fad198cdc1e4abacfe79f5d119"
PUBLIC_URL = "https://azentyk-bot-to-receptionist-ajfeh8cwd6hqcbhj.centralus-01.azurewebsites.net" 
TWILIO_CALLER_ID = "+16812936895"  # Your Twilio number
VOICE_VOICE = "Google.en-IN-Chirp3-HD-Puck"
RECEPTIONIST_NUMBER = "+917010413012"
MONGO_URL = r"mongodb://azentyk-doctor-appointment-app-server:ROtcf6VzE2Jj2Etn0D3QY9LbrSTs4MEgld2hynMw3R46gl8cuL1D70qvx4DjQvogoyBDVO2z1MJxACDb04M0BA==@azentyk-doctor-appointment-app-server.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@azentyk-doctor-appointment-app-server@"
PROCESSED_RETENTION_SECONDS = 24 * 3600  # 24 hours
