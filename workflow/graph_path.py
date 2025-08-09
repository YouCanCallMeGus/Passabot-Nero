import os
import requests
from dotenv import load_dotenv

load_dotenv()
 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def request_structured_output(system_prompt, json_schema, node_history):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json = {
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Trecho da conversa:\n\n{node_history}"}
        ],
        "temperature": 0.0,
        "response_format": {
            "type": "json_schema",
            "json_schema": json_schema
        }
    }

    resp = requests.post(API_URL, headers=headers, json=json)
    resp.raise_for_status()
    data = resp.json()
    result = data["choices"][0]["message"]["content"].split(":")[-1].split("}")[0].strip()

    return result


def get_node_history(conversation_history, node):

    node_history = []
    for message in conversation_history:
        if message["node"] == node:
            node_history.append(f"{message["role"]}: {message["content"]}\n")
    return node_history


def next_node(conversation_history, node):

    node_history = get_node_history(conversation_history, node)

    if node == "C_1":

        system_prompt = """
        Você é um assistente de IA muito prestativo que vai analisar um diálogo e
        dizer se há a confirmação que o atendente realmente corresponde ao hotel
        que o usuário deseja falar. Deve responder em: SIM, NAO ou INCONCLUSIVO.
        """

        json_schema = {
                    "name": "classify_hotel_confirmation",
                    "description": "Classifica se houve confirmação de que o atendente é do hotel desejado",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "string",
                                "description": "Classificação do histórico do chat entre SIM, NAO e INCONCLUSIVO",
                                "enum": ["SIM", "NAO", "INCONCLUSIVO"]
                            }
                        },
                        "required": ["result"],
                        "additionalProperties": False
                    }
                }
        
        result = request_structured_output(system_prompt, json_schema, node_history)
        print(result)
        if result == "SIM":
            return "C_2"
        elif result == "NAO":
            return "E_3"
        else:
            return "C_1"