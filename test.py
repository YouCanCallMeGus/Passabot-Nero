import time

t1 = time.time()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv(override=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = FAISS.load_local(
    "faiss_index", embeddings, allow_dangerous_deserialization=True
)

results = vector_store.similarity_search_with_score(
    "usuário: É do hotel tal?\n atendente: Não é não", k=5
)

list_sim, list_nao, list_inconclusivo = [], [], []
for res, score in results:
    if res.metadata['next_node'] == 'sim':
        list_sim.append(score)
    elif res.metadata['next_node'] == 'não':
        list_nao.append(score)
    elif res.metadata['next_node'] == 'inconclusivo':
        list_inconclusivo.append(score)
    print(res, score)

total_sim = sum(list_sim)
total_nao = sum(list_nao)
total_inconclusivo = sum(list_inconclusivo)
print(total_sim, total_nao, total_inconclusivo)

if total_sim > total_nao and total_sim > total_inconclusivo:
    print('sim')
elif total_nao > total_sim and total_nao > total_inconclusivo:
    print('não')
else:
    print('inconclusivo')

t2 = time.time()
deltaT = t2 - t1

print(f"Tempo de execução: {deltaT:.6f} segundos")