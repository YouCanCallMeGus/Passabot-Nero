from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
PHONE_ID = os.getenv("PHONE_ID")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

app = Flask(__name__)

vapi_api_url = "https://api.vapi.ai/call"

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Agent Testing API!"

@app.route("/call", methods=["POST"])
def create_call():
    body_content = request.get_json()

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}"
    }

    data = {
        "name": "passabot_d1",
        "workflowId": WORKFLOW_ID,
        "workflowOverrides": {
            "variableValues": {
                "hotelName": body_content["hotelName"],
                "name": body_content["name"],
                "cpf": body_content["cpf"],
                "bookCode": body_content["bookCode"],
                "checkIn": body_content["checkIn"],
                "checkOut": body_content["checkOut"]
            }
        },
        "customer": {
            "number": body_content["hotelPhone"],
            "name": body_content["hotelName"]
        },
        "phoneNumberId": PHONE_ID
    }

    response = requests.post(url=vapi_api_url, headers=headers, json=data)
    return response.json(), response.status_code




if __name__ == "__main__":
    app.run(debug=True)