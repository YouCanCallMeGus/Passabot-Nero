from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()
VAPI_KEY = os.getenv("VAPI_API_KEY")

app = Flask(__name__)

vapi_api_url = "https://api.vapi.ai/call"

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Agent Testing API!"

@app.route("/call", methods=["POST"])
def call():
    headers = {
        "Authorization": f"Bearer {VAPI_KEY}"
    }
    data = {
        "name": "test",
        "assistant": {},

    }
    response = requests.post(url=vapi_api_url, headers=headers, data=data)
    return response.json(), response.status_code

if __name__ == "__main__":
    app.run(debug=True)