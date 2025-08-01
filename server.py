import io
import uuid
import json
import uvicorn
import speech_recognition

from pydub import AudioSegment

from typing import Dict

from gtts import gTTS

from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Chat.chat import ChatSession, Message

from Configs.config import HOST, PORT
from Services.LLMService import LLMService

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        print("WebSocket connection accepted")

        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket
        chat_sessions[session_id] = ChatSession(id=session_id)

        return session_id

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            print(f"Disconnecting session {session_id}")
            del self.active_connections[session_id]

manager = ConnectionManager()
llm_service = LLMService()
app = FastAPI()

app.mount("/static", StaticFiles(directory="Static"), name="static")

templates = Jinja2Templates(directory="templates")

chat_sessions: Dict[str, ChatSession] = {}

# TODO Make it so when user hangs up, AI summarizes so users dont have to redo entire conversation

async def LLM_response(websocket, session_id):
    print("Starting LLM response stream")
    full_response = ""
    
    async for response_chunk in llm_service.generate_response_stream(chat_sessions[session_id].messages, 'llama-3.3-70b-versatile', True):
        print(f"Streaming chunk: {response_chunk[:20]}...")
        await websocket.send_json({
            "type": "stream",
            "content": response_chunk
        })
        full_response += response_chunk
    
    chat_sessions[session_id].messages.append(Message(role="assistant", content=full_response))
    print("LLM response complete, added to chat history")
    
    await websocket.send_json({
        "type": "stream_end",
        "session_id": session_id
    })
    
    print("Sent stream_end signal")

async def speech_to_text(audio_chunk, websocket, session_id):
    try:
        audio = AudioSegment.from_raw(
            io.BytesIO(audio_data),
            sample_width=2,
            frame_rate=8000,
            channels=1
        )
        
        wav_data = io.BytesIO()
        audio.export(wav_data, format="wav")
        wav_data.seek(0)
        
        recognizer = speech_recognition.Recognizer()
        
        with speech_recognition.AudioFile(wav_data) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        chat_sessions[session_id].messages.append(Message(role='user', content=text))
        print(f"Speech to text: {text}")
    except Exception as e:
        print(f"Speech recognition error: {e}")

async def text_to_speech(websocket, text):
    try:
        tts = gTTS(text=text, lang='en')
        
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        audio_data = audio_bytes.read()
        await websocket.send_bytes(audio_data)
        
        print(f"Sent {len(audio_data)} bytes of audio")
    
    except Exception as e:
        print(f"TTS error: {e}")

async def recieve_client_text(websocket, session_id):
    print("Waiting for client message")
    data = await websocket.receive_text()
    print(f"Received message from client: {data[:50]}...")
    
    message_data = json.loads(data)
    user_message = message_data.get("message", "")
    
    chat_sessions[session_id].messages.append(Message(role="user", content=user_message))
    
    await websocket.send_json({
        "type": "message_received",
        "status": "processing"
    })
    
    print("Sent processing acknowledgment")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", response_class=JSONResponse)
async def get_index():
    return {"message": "Twilio Media Stream Server is running!"}

@app.websocket("/chat")
async def main_page(websocket: WebSocket):
    try:
        print("New WebSocket connection attempt")
        session_id = await manager.connect(websocket)
        print(f"Connected with session_id: {session_id}")
        
        await websocket.send_json({"type": "session_id", "session_id": session_id})
        print(f"Sent session_id to client: {session_id}")

        welcome_message = "Hello! I'm your PulseLine Incorporate's personal assistant. How can I help you today?"
        chat_sessions[session_id].messages.append(Message(role="assistant", content=welcome_message))
        
        await websocket.send_json({
            "type": "initial_message",
            "content": welcome_message
        })
        
        print("Sent welcome message to client")

        while True:
            await recieve_client_text(websocket, session_id)
            
            try:
                await LLM_response(websocket, session_id)
                
            except Exception as e:
                print(f"Error during LLM call: {e}")
                
                await websocket.send_json({
                    "type": "error",
                    "message": "Sorry, there was an error processing your request."
                })
            
    except WebSocketDisconnect:
        print("WebSocket disconnected normally")
        if 'session_id' in locals():
            manager.disconnect(session_id)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        if 'session_id' in locals():
            manager.disconnect(session_id)

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()

    response.say(
        "Please wait while we connect your call to the A. I. voice assistant, powered by Twilio and the Open-A.I. Realtime API"
    )
    response.pause(length=1)
    response.say(
        "Please be aware, we can only help you with your prescription order, making a appointment, or transferring you to a medical professional. All other requests will be ignored."
    )
    response.pause(length=0.5)
    response.say("O.K. you can start talking!")

    host = request.url.hostname

    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")

    response.append(connect)

    xml_string = response.to_xml()
    print(f"XML content type: {type(xml_string)}")
    print(f"XML content: {xml_string}")
    return Response(content=xml_string, media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    try:
        print("New WebSocket connection attempt")
        session_id = await manager.connect(websocket)
        print(f"Connected with session_id: {session_id}")
        
        audio_buffer = b""
        
        async for message in websocket.iter_bytes():
            audio_buffer += message
            
        if audio_buffer:
            print(f"Processing {len(audio_buffer)} bytes of audio")
            response = await speech_to_text(audio_buffer, websocket, session_id)
            
            print("Starting LLM response stream")
            full_response = ""
            
            async for response_chunk in llm_service.generate_response_stream(chat_sessions[session_id].messages, 'llama-3.3-70b-versatile', True):
                print(f"Streaming chunk: {response_chunk[:20]}...")
                await websocket.send_json({
                    "type": "stream",
                    "content": response_chunk
                })
                full_response += response_chunk
                
            print(f"Response: {full_response}")
            
            await text_to_speech(websocket, full_response)
            
    except WebSocketDisconnect:
        print("Twilio disconnected")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)