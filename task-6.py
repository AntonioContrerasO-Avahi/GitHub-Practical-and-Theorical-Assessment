# ============================================================================================================
# RAG CHATBOT CON MEMORIA Y GRADIO UI
# Chatbot con acceso a documentos vectoriales, memoria persistente y interfaz web
# ============================================================================================================

import json
import boto3
import sqlite3
import gradio as gr
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool
from langchain_community.vectorstores import SQLiteVec
import threading

# ============================================================================================================
# CONFIGURACIÓN
# ============================================================================================================
MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
REGION = "us-east-1"
DB_FILE = "./vector_store.db"
TABLE_NAME = "documents"
MEMORY_DB = "chatbot_memory.sqlite"

# ============================================================================================================
# CARGAR EMBEDDINGS (compartido entre threads)
# ============================================================================================================
print("📦 Cargando embeddings...")
embeddings = BedrockEmbeddings(
    region_name=REGION, model_id="amazon.titan-embed-text-v1"
)
print("✅ Embeddings cargados\n")

# ============================================================================================================
# THREAD-LOCAL STORAGE PARA VECTOR DB
# ============================================================================================================
thread_local = threading.local()


def get_vector_db():
    """
    Obtiene una instancia de vector_db específica para el thread actual
    """
    if not hasattr(thread_local, "vector_db"):
        # Crear nueva conexión para este thread
        connection = SQLiteVec.create_connection(db_file=DB_FILE)
        thread_local.vector_db = SQLiteVec(
            table=TABLE_NAME, embedding=embeddings, connection=connection
        )
    return thread_local.vector_db


# ============================================================================================================
# DEFINIR TOOL DE RAG (THREAD-SAFE)
# ============================================================================================================
@tool
def search_documents(query: str) -> str:
    """
    Busca información relevante en la base de datos de documentos.
    Usa esta herramienta cuando necesites información específica de los documentos cargados.

    Args:
        query: La pregunta o término de búsqueda

    Returns:
        Información relevante encontrada en los documentos
    """
    try:
        # Obtener vector_db específico para este thread
        vector_db = get_vector_db()

        # Buscar en el vector store
        results = vector_db.similarity_search(query, k=3)

        if not results:
            return "No se encontró información relevante en los documentos."

        # Formatear resultados
        context = "\n\n---\n\n".join(
            [
                f"📄 Fragmento {i+1}:\n{doc.page_content}\n(Fuente: página {doc.metadata.get('page', 'N/A')})"
                for i, doc in enumerate(results)
            ]
        )

        return f"Información encontrada en los documentos:\n\n{context}"

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en search_documents: {error_trace}")
        return f"Error al buscar en los documentos: {str(e)}"


# ============================================================================================================
# CREAR AGENTE CON MEMORIA Y HERRAMIENTAS
# ============================================================================================================
def create_rag_agent():
    """
    Crea un agente con memoria persistente, summarization y acceso a documentos
    """
    # Cargar modelo
    llm = ChatBedrock(model_id=MODEL_ID, region_name=REGION, streaming=False)

    # Crear memoria persistente con check_same_thread=False
    conn = sqlite3.connect(MEMORY_DB, check_same_thread=False)
    memory = SqliteSaver(conn)

    # Crear agente con herramientas
    agent = create_agent(
        model=llm,
        tools=[search_documents],
        checkpointer=memory,
        middleware=[
            SummarizationMiddleware(
                model=llm,
                trigger=("messages", 10),
                keep=("messages", 4),
            ),
        ],
        system_prompt=(
            "Eres un asistente útil con acceso a documentos sobre guías de estilo de Google. "
            "Cuando te pregunten sobre información específica de los documentos, usa la herramienta "
            "search_documents para buscar información relevante. "
            "Siempre cita las fuentes cuando uses información de los documentos."
        ),
    )

    return agent


print("🤖 Creando agente RAG...")
agent = create_rag_agent()
print("✅ Agente creado\n")

# ============================================================================================================
# CONFIGURACIÓN DE CONVERSACIÓN
# ============================================================================================================
import time

THREAD_ID = f"gradio_session_{int(time.time())}"
config = {"configurable": {"thread_id": THREAD_ID}}


# ============================================================================================================
# FUNCIÓN DE PREDICCIÓN PARA GRADIO
# ============================================================================================================
def predict(message, history):
    """
    Función de predicción para Gradio

    Args:
        message: Mensaje actual del usuario
        history: Historial de mensajes en formato Gradio

    Returns:
        Respuesta completa del asistente
    """
    try:
        # Invocar el agente
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]}, config=config
        )

        # Extraer la última respuesta del asistente
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                return last_message.content
            elif isinstance(last_message, dict) and "content" in last_message:
                return last_message["content"]

        return "No se recibió respuesta del modelo."

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        import traceback

        traceback.print_exc()
        return error_msg


# ============================================================================================================
# CREAR INTERFAZ GRADIO
# ============================================================================================================
print("🎨 Creando interfaz Gradio...")

demo = gr.ChatInterface(
    fn=predict,
    title="🤖 RAG Chatbot - Google Style Guide Assistant",
    description=(
        "Asistente inteligente con acceso a las guías de estilo de Google. "
        "Pregúntame sobre convenciones de código, estilo, o buenas prácticas!"
    ),
    examples=[
        "¿Cuáles son las principales guías de estilo?",
        "¿Cómo debo formatear código?",
        "¿Qué convenciones de nombres recomienda Google?",
        "Explícame las mejores prácticas de documentación",
    ],
)

print("✅ Interfaz creada")
print("\n" + "=" * 100)
print("🚀 INICIANDO SERVIDOR GRADIO")
print("=" * 100)
print("💡 Se generará una URL pública temporal")
print("💡 Presiona Ctrl+C para detener el servidor")
print("=" * 100 + "\n")

# Lanzar aplicación
demo.launch(share=True, server_name="0.0.0.0", server_port=7860, show_error=True)
