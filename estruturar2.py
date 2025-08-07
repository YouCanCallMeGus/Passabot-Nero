from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
import time
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

class ClassifierHotel(Enum):

    SIM = "SIM"
    NAO = "NAO"
    INCONCLUSIVO = "INCONCLUSIVO"

class GetSchema(BaseModel):
    """Schema de bolo"""
    
    resultado: ClassifierHotel = Field(description="Classificação do histórico do chat entre SIM, NAO e INCONCLUSIVO")

t1 = time.time()
response = client.responses.parse(
    model="gpt-4.1-nano",
    max_output_tokens=16,
    temperature=0.0,
    input=[
        {"role": "system", "content": "Você é um assistente de IA muito prestativo que vai analisar um diálogo e dizer se há a confirmação que o atendente realmente corresponde ao hotel que o usuário deseja falar. Deve responder em: SIM, NAO ou INCONCLUSIVO."},
        {
            "role": "user",
            "content": "usuário: É do hotel tal?\n atendente: Não é não.",
        },
    ],
    text_format=GetSchema,
)

result = response.output_parsed
t2 = time.time()

print(result.resultado.value)

print(f"{(t2-t1):.3f} segundos")