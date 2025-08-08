from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from operator import itemgetter
from dotenv import load_dotenv
import os

load_dotenv()
index_name = "FAQ"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=2048)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")
pinecone = pc.Index(name=index_name)
vectorStore = PineconeVectorStore(pinecone, embedding_model)

def handle_index_creation(index_name: str):
    global vectorStore, embedding_model, pc, pinecone
    try:
        if index_name in pc.list_indexes().names():
            pc.delete_index(index_name)
        
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "llama-text-embed-v2",
                "dimension": 2048,
                "field_map":{"text": "chunk_text"}
            }
        )
        pinecone = pc.Index(name=index_name)
        vectorStore = PineconeVectorStore(pinecone, embedding_model)
    except Exception as e:
        raise ValueError(f"Erro ao criar o índice: {e}")

def create_context():
    loader = PyPDFLoader("FAQ.pdf")
    faq_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    faq_chunks = text_splitter.split_documents(faq_docs)
    try:
        vectorStore.add_documents(faq_chunks)
    except Exception as e:
        raise ValueError(e)

def chat(query: str, chat_history):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você recebeu um arquivo e agora é especialista nele, responda de forma clara às perguntas do usuário. Não fuja do assunto (FAQ de viagens)"),
        ("human", "responda essa pergunta: {pergunta}"),
        ("human", "use isso de contexto {context} e essas mensagens anteriores: {chat_history}"),
    ])

    def format_docs(context: list[Document]) -> str:
        return "\n".join([doc.page_content for doc in context])

    chat = ChatOpenAI(model="gpt-4o-mini")

    retriever = vectorStore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    chain = {
        "pergunta": itemgetter("query"),
        "context": itemgetter("query") | retriever | format_docs,
        "chat_history": itemgetter("chat_history"),
    } | prompt | chat

    return chain.invoke({"query": query, "chat_history": chat_history})
