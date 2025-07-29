import uuid
import json
import uvicorn

from typing import Dict

from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from Chat.chat import ChatSession, Message

from Configs.config import HOST, PORT
from Services.LLMService import LLMService

chat_sessions: Dict[str, ChatSession] = {}

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

# TODO Make it so when user hangs up, AI summarizes so users dont have to redo entire conversation

@app.get("/", response_class=JSONResponse)
async def main_page():
    return {"message": "Currently undergoing development"}

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    try:
        print("New WebSocket connection attempt")
        session_id = await manager.connect(websocket)
        print(f"Connected with session_id: {session_id}")
        
        await websocket.send_json({"type": "session_id", "session_id": session_id})
        print(f"Sent session_id to client: {session_id}")

        welcome_message = "Hello! I'm your BlahBlahBlah Incorporate's personal assistant. How can I help you today?"
        chat_sessions[session_id].messages.append(Message(role="assistant", message=welcome_message))
        
        await websocket.send_json({
            "type": "initial_message",
            "content": welcome_message
        })
        
        print("Sent welcome message to client")

        while True:
            print("Waiting for client message")
            data = await websocket.receive_text()
            print(f"Received message from client: {data[:50]}...")
            
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            chat_sessions[session_id].messages.append(Message(role="patient", message=user_message))
            
            await websocket.send_json({
                "type": "message_received",
                "status": "processing"
            })
            
            print("Sent processing acknowledgment")
            
            try:
                print("Starting LLM response stream")
                full_response = ""
                async for response_chunk in llm_service.generate_response_stream(chat_sessions[session_id].messages, 'llama-3.3-70b-versatile', False):
                    print(f"Streaming chunk: {response_chunk[:20]}...")
                    await websocket.send_json({
                        "type": "stream",
                        "content": response_chunk
                    })
                    full_response += response_chunk
                
                chat_sessions[session_id].messages.append(Message(role="Receptionist", message=full_response))
                print("LLM response complete, added to chat history")
                
                await websocket.send_json({
                    "type": "stream_end",
                    "session_id": session_id
                })
                
                print("Sent stream_end signal")
                
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

    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    pass

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)