import os  
import json  
import requests  
import asyncio
from agent import run_agent_with_mcp_servers
from schema import User, Audio  
from typing import BinaryIO
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def download_file_from_facebook(file_id: str, file_type: str, mime_type: str) -> str | None:  
    # First GET request to retrieve the download URL  
    url = f"https://graph.facebook.com/v19.0/{file_id}"  
    headers = {"Authorization": f"Bearer {WHATSAPP_API_KEY}"}  
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  
        download_url = response.json().get('url')  
        # Second GET request to download the file  
        response = requests.get(download_url, headers=headers)  
        if response.status_code == 200:
            # Extract file extension from mime_type    
            file_extension = mime_type.split('/')[-1].split(';')[0]
            # Create file_path with extension
            file_path = f"{file_id}.{file_extension}"  
            with open(file_path, 'wb') as file:  
                file.write(response.content)  
            if file_type == "audio":  
                return file_path  
        raise ValueError(f"Failed to download file. Status code: {response.status_code}")  
    raise ValueError(f"Failed to retrieve download URL. Status code: {response.status_code}")


def transcribe_audio_file(audio_file: BinaryIO) -> str:  
    if not audio_file:  
        return "No audio file provided"  
    try:  
        transcription = llm.audio.transcriptions.create(  
            file=audio_file,  
            model="whisper-1",  
            response_format="text"  
        )  
        return transcription  
    except Exception as e:  
        raise ValueError("Error transcribing audio") from e


def transcribe_audio(audio: Audio) -> str:  
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)  
    with open(file_path, 'rb') as audio_binary:  
        transcription = transcribe_audio_file(audio_binary)  
    try:  
        os.remove(file_path)  
    except Exception as e:  
        print(f"Failed to delete file: {e}")  
    return transcription


def authenticate_user_by_phone_number(phone_number: str) -> User | None:  
    # Get allowed users from environment variables
    allowed_users_str = os.getenv("ALLOWED_USERS", "[]")
    try:
        allowed_users = json.loads(allowed_users_str)
    except json.JSONDecodeError:
        print("Error parsing ALLOWED_USERS from environment variables")
        return None
        
    for user in allowed_users:  
        if user["phone"] == phone_number:  
            return User(**user)  
    return None


def send_whatsapp_message(to, message):  
    url = f"https://graph.facebook.com/v18.0/289534840903017/messages"  
    headers = {  
        "Authorization": f"Bearer " + WHATSAPP_API_KEY,  
        "Content-Type": "application/json"  
    }  
    data = {  
        "messaging_product": "whatsapp",  
        "preview_url": False,  
        "recipient_type": "individual",  
        "to": to,  
        "type": "text",  
        "text": {  
            "body": message  
        }  
    }  

    response = requests.post(url, headers=headers, data=json.dumps(data))  
    return response.json()


async def respond_and_send_message(user_message: str, user: User):  
    # Run the agent and get the response
    response = await run_agent_with_mcp_servers(user_message)
    # Send the response via WhatsApp
    await send_whatsapp_message(user.phone, response)


