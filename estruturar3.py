from pydantic import BaseModel, Field
from typing import List
from enum import Enum
import time
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

model = ChatGroq(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0,
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
    
    result: ClassifierHotel = Field(description="Classificação do histórico do chat entre SIM, NAO e INCONCLUSIVO")
    
strutured_model = model.with_structured_output(GetSchema)
chain = prompt | strutured_model

t1 = time.time()
resultado = chain.invoke({"query": "usuário: É do hotel tal?\n atendente: Não é não"})
t2 = time.time()

print(resultado.result.value)
print(f"{(t2-t1):.3f} segundos")