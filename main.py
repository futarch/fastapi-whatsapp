from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv
import os

import threading  
from typing_extensions import Annotated  
from fastapi import APIRouter, Query, HTTPException, Depends  
import message_service  
from schema import Payload, Message, Audio, User  

# Load environment variables from .env file
load_dotenv()

# Get verification token from environment variable
VERIFICATION_TOKEN = os.getenv("WHATSAPP_VERIFICATION_TOKEN")

app = FastAPI()


@app.get("/")
def verify_whatsapp(
    hub_mode: str = Query("subscribe", description="The mode of the webhook", alias="hub.mode"),
    hub_challenge: int = Query(..., description="The challenge to verify the webhook", alias="hub.challenge"),
    hub_verify_token: str = Query(..., description="The verification token", alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFICATION_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/readiness")
def readiness():
    return {"status": "ready"}
    

def parse_message(payload: Payload) -> Message | None:  
    if not payload.entry[0].changes[0].value.messages:  
        return None  
    return payload.entry[0].changes[0].value.messages[0]  

def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> User | None:  
    if not message:  
        return None  
    return message_service.authenticate_user_by_phone_number(message.from_)  

def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Audio | None:  
    if message and message.type == "audio":  
        return message.audio  
    return None  

def message_extractor(  
        message: Annotated[Message, Depends(parse_message)],  
        audio: Annotated[Audio, Depends(parse_audio_file)],  
):  
    if audio:  
        return message_service.transcribe_audio(audio)  
    if message and message.text:  
        return message.text.body  
    return None


@app.post("/", status_code=200)  
def receive_whatsapp(  
        user: Annotated[User, Depends(get_current_user)],  
        user_message: Annotated[str, Depends(message_extractor)],  
):  
    if not user and not user_message:  
        return {"status": "ok"}  
    if not user:  
        raise HTTPException(status_code=401, detail="Unauthorized")  
    if user_message:  
        thread = threading.Thread(
            target=message_service.respond_and_send_message, 
            args=(user_message, user)
        )  
        thread.daemon = True  
        thread.start()  
    return {"status": "ok"}
