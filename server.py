import uuid
import json
import base64
import asyncio
import uvicorn
import websockets

from websockets.protocol import State

from typing import Dict
from twilio.twiml.voice_response import VoiceResponse, Connect

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Chat.chat import ChatSession, Message

from Configs.config import HOST, PORT, OPENAI_API_KEY
from Configs.prompts import ONLINE_PROMPT, CALL_PROMPT
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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

chat_sessions: Dict[str, ChatSession] = {}

VOICE = 'alloy'

LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]

SHOW_TIMING_MATH = False

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

# TODO Make it so when user hangs up, AI summarizes so users dont have to redo entire conversation
# TODO Add postgres database 

async def LLM_text_response(websocket, session_id):
    print("Starting LLM response stream")
    full_response = ""
    
    async for response_chunk in llm_service.generate_response_stream(chat_sessions[session_id].messages, True):
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

async def receive_client_text(websocket, session_id):
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

@app.websocket("/chat")
async def main_page(websocket: WebSocket):
    try:
        print("New WebSocket connection attempt")
        session_id = await manager.connect(websocket)
        print(f"Connected with session_id: {session_id}")
        
        await websocket.send_json({"type": "session_id", "session_id": session_id})
        print(f"Sent session_id to client: {session_id}")

        welcome_message = "Hello! I'm your PulseLine personal assistant. How can I help you today?"
        chat_sessions[session_id].messages.append(Message(role="assistant", content=welcome_message))
        
        await websocket.send_json({
            "type": "initial_message",
            "content": welcome_message
        })
        
        print("Sent welcome message to client")
        
        start_message = {
                "role": "system",
                "content": ONLINE_PROMPT
            }
        
        chat_sessions[session_id].messages.insert(0, start_message)
        
        while True:
            await receive_client_text(websocket, session_id)
            
            try:
                await LLM_text_response(websocket, session_id)
                
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

# TODO Add transfering

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()

    # response.say(
    #     "Please wait while we connect your call to the A.I. voice assistant, powered by Twilio and GroqCloud"
    # )
    # response.pause(length=1)
    # response.say(
    #     "Please be aware, we can only help you with your prescription order, making an appointment, or transferring you to a medical professional. All other requests will be ignored."
    # )
    # response.pause(length=0.5)
    # response.say("O.K. you can start talking! How can I help you?")
    
    host = request.url.hostname
    
    connect = Connect()
    
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    await websocket.accept()
    print("Client connected")

    async with websockets.connect(
            "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03",
            additional_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as openai_ws:
        await initialize_session(openai_ws)

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None
        
        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.state is State.OPEN:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)

                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                        # Update last_assistant_item safely
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        print("Speech started detected.")
                        if last_assistant_item:
                            print(f"Interrupting response with id: {last_assistant_item}")
                            await handle_speech_started_event()
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": CALL_PROMPT,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)