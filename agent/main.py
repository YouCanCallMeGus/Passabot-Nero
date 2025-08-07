from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketDisconnect
from websockets.client import connect
import uvicorn
from twilio.rest import Client
from dotenv import load_dotenv
import json
import os
import base64
import asyncio
from datetime import datetime
import logging
from data_model import User_data
import io
import wave
import pyaudio

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER_FROM = os.getenv('PHONE_NUMBER_FROM')
PHONE_NUMBER_TO = os.getenv('PHONE_NUMBER_TO')
DOMAIN = os.getenv("DOMAIN")
PORT = os.getenv("PORT")

logging.basicConfig(filename='conversation.log', level=logging.INFO)
conversation_history = []

app = FastAPI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

VOICE = "alloy"
system_message = ("")

with open("audio.wav", "r") as f:
    audio = f.read()
    with wave.open(io.BytesIO(audio), 'rb') as wf:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()
 

async def log_conversation(role: str, content: str, audio_data: str):
    """Add conversation logs"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content,
        "audio": audio_data
    }
    conversation_history.append(data)
    logging.info(json.dumps(data))

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    print("Attempting to connect to OpenAI...")
    async with connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17',
        extra_headers= [
            ("Authorization", f"Bearer {OPENAI_API_KEY}"),
            ("OpenAI-Beta", "realtime=v1")
        ],
    ) as openai_ws:
        print("Connected to OpenAI WebSocket")
        await initialize_session(openai_ws)
        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        try:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio
                                }
                            }
                            await websocket.send_json(audio_delta)
                        except Exception as e:
                            print(f"Error processing audio data: {e}")
                    elif response['type'] == 'response.audio_transcript.done':
                        await log_conversation(
                            role="AI",
                            content="[AI Response]",
                            audio_data=response['transcript']
                        )
                    elif response['type'] == 'conversation.item.input_audio_transcription.completed':
                        await log_conversation(
                            role="AI",
                            content="[AI Response]",
                            audio_data=response['transcript']
                        )
                        
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")
        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_initial_conversation_item(openai_ws):
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "Diga 'Olá'"
                    )
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))

async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    transcription_update = {
        "type": "transcription_session.update",
        "input_audio_format": "g711_ulaw", 
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
        }
    }
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "semantic_vad",
                               "eagerness": "high", 
                                "create_response": True, 
                                "interrupt_response": True},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": system_message,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
            "input_audio_transcription": {
                "language": "pt",
                "model": "gpt-4o-transcribe",
            }
        }
    }
    print('Sending session update:', json.dumps(session_update))
    logging.info(f"Session update: {json.dumps(session_update)}")
    await openai_ws.send(json.dumps(transcription_update))
    await openai_ws.send(json.dumps(session_update))
    print("Session initialized with OpenAI.")
    logging.info("Session initialized with OpenAI.")

    await send_initial_conversation_item(openai_ws)

async def check_number_allowed(to):
    """Check if a number is allowed to be called."""
    try:
        incoming_numbers = client.incoming_phone_numbers.list(phone_number=to)
        if incoming_numbers:
            return True

        outgoing_caller_ids = client.outgoing_caller_ids.list(phone_number=to)
        if outgoing_caller_ids:
            return True
        return False
    
    except Exception as e:
        print(f"Error checking phone number: {e}")
        return False
    
async def make_call(phone_number_to_call: str):
    """Make an outbound call."""
    if not phone_number_to_call:
        raise ValueError("Please provide a phone number to call.")

    is_allowed = await check_number_allowed(phone_number_to_call)
    if not is_allowed:
        raise ValueError(f"The number {phone_number_to_call} is not recognized as a valid outgoing number or caller ID.")

    outbound_twiml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Connect><Stream url="wss://{DOMAIN}/media-stream" /></Connect></Response>'
    )

    call = client.calls.create(
        from_=PHONE_NUMBER_FROM,
        to=phone_number_to_call,
        twiml=outbound_twiml
    )

    await log_call_sid(call.sid)

async def log_call_sid(call_sid):
    print(f"Call started with SID: {call_sid}")

def create_system_message(data: User_data):
    print(data)
    return (
        "Você está ligando para o hotel para confirmar dados, a pessoa a qual você está ligando não é o cliente que precisa ser confirmado!"
        "Você fala português brasileiro! Não tenha sotaque de Portugal"
        "Após isso confirme os dados:"
        f"Nome do hotel: {data.hotelName}"
        f"Número do hotel: {data.hotelPhone}"
        f"Nome do cliente: {data.name}"
        f"CPF do cliente: {data.cpf}"
        f"Código de reserva: {data.bookCode}"
        f"CheckIn: {data.checkIn}"
        f"CheckOut: {data.checkOut}"
        "Assim que o usuário tiver a primeira interação confirme se é realmente o hotel que está nos dados"
        "Sobre o código de reserva: Use *SEMPRE* o alfabeto alfanumérico para dizer, exemplo: 'a' = alpha, 'b' = beta ..."
        "Ao confirmar se todos os dados existem ou não encerre a ligação."
    ) if data != None else ""

@app.get("/", response_class=JSONResponse)
async def index():
    return {"message": "OK"}

@app.get("/conversation-history", response_class=JSONResponse)
async def get_conversation_history():
    """Full chat content"""
    return JSONResponse(conversation_history)

@app.post("/make_call", response_class=JSONResponse)
async def make_call_api(item: User_data):
    global system_message
    system_message = create_system_message(item)
    await make_call(PHONE_NUMBER_TO)
    return {"message": item}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(PORT), reload=True)