from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PORT = os.getenv("PORT")

app = FastAPI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.get("/", response_class=JSONResponse)
async def index():
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(PORT), reload=True)