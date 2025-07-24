import uvicorn
import websockets

from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse

from Configs.config import HOST, PORT

app = FastAPI()

@app.get("/", response_class=JSONResponse)
async def main_page():
    return {"message": "Currently undergoing development"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    
    response.say("Please wait while we connect your call to the A. I. voice assistant, powered by Twilio and the Open-A.I. Realtime API")
    response.pause(length=1)
    response.say("O.K. you can start talking!")
    response.pause(length=0.5)
    response.say("Please be aware, we can only help you with your prescription order, making a appointment, or transferring you to a medical professional. All other requests will be ignored.")
    
    host = request.url.hostname
    
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    
    response.append(connect)
    
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    print("Client connected")
    await websocket.accept()
    
    

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)