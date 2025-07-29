from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()
VAPI_KEY = os.getenv("VAPI_API_KEY")
PHONE_ID = os.getenv("PHONEID")

app = Flask(__name__)

vapi_api_url = "https://api.vapi.ai/call"

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Agent Testing API!"

@app.route("/call", methods=["POST"])
def call():
    body_content = request.get_json()
    headers = {
        "Authorization": f"Bearer {VAPI_KEY}"
    }

    data = {
        "name": "test",
        "assistant": {
            "transcriber": {
                "provider": "openai",
                "model": "gpt-4o-transcribe",
                "language": "pt",
                
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
                            Você é um prestador de serviços que quer confirmar os dados de uma pessoa aleatória no hotel!
                            Você fala português brasileiro, mas não dê ênfase nisso durante a conversa.

                            Você tem os dados de um cliente que não faz parte dos membros do hotel e sua missão é confirmar se ele tem ou não vaga registrada no hotel {body_content["hotelName"]}.

                            Dados do cliente:
                            Nome: {body_content["name"]}
                            CPF: {body_content["cpf"]}
                            Código de confirmação: {body_content["bookCode"]}
                            CheckIn: {body_content["checkIn"]}
                            checkOut: {body_content["checkOut"]}

                            Ao terminar a verificação você deve apenas agradecer a confirmação com um "Obrigado pela confirmação!" e encerrar a ligação.
                        """
                    }
                ]
            },
            "firstMessage": f"Olá, tudo bem? Esse é o hotel {body_content["hotelName"]}?"
        },
        "customer": {
            "number": f"{body_content["hotelPhone"]}",
            "name": f"{body_content["hotelName"]}"
        },
        "phoneNumberId": PHONE_ID

    }
    response = requests.post(url=vapi_api_url, headers=headers, json=data)
    return response.json(), response.status_code

if __name__ == "__main__":
    app.run(debug=True)