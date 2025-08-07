from pydantic import BaseModel, Field
from typing import List
from enum import Enum
import time
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.0,
    max_tokens=10
)

system_prompt = """
Você é um assistente de IA muito prestativo que vai analisar um diálogo e dizer se há a confirmação que o atendente realmente corresponde ao hotel que o usuário deseja falar. Deve responder em: SIM, NAO ou INCONCLUSIVO.
"""

prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt), 
            ("human", "Trecho da conversa: \n\n {query}")
        ]
)

class ClassifierHotel(Enum):

    SIM = "SIM"
    NAO = "NAO"
    INCONCLUSIVO = "INCONCLUSIVO"

class GetSchema(BaseModel):
    """Schema de bolo"""
    
    resultado: ClassifierHotel = Field(description="Classificação do histórico do chat entre SIM, NAO e INCONCLUSIVO")
    
strutured_model = model.with_structured_output(GetSchema)
chain = prompt | strutured_model

t1 = time.time()
result = chain.invoke({"query": "usuário: É do hotel tal?\n atendente: Não é não"})
t2 = time.time()

print(result.resultado.value)
print(f"{(t2-t1):.3f} segundos")