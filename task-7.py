# ============================================================================================================
# PRACTICE 7: FUNCTION CALLING / TOOL USE CON GRADIO
# Agente con múltiples herramientas, logging detallado y UI web
# ============================================================================================================

import json
import boto3
import sqlite3
import logging
import gradio as gr
from datetime import datetime
from pathlib import Path
from langchain_aws import ChatBedrock
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from langchain.tools import tool
import math
import os
import threading

# ============================================================================================================
# CONFIGURACIÓN
# ============================================================================================================
MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
REGION = "us-east-1"
MEMORY_DB = "tool_agent_memory.sqlite"

# Thread-local storage para loggers
thread_local = threading.local()


# ============================================================================================================
# SETUP DE LOGGING POR SESIÓN
# ============================================================================================================
def get_session_logger(session_id: str):
    """
    Obtiene o crea un logger específico para una sesión
    """
    if not hasattr(thread_local, "loggers"):
        thread_local.loggers = {}

    if session_id not in thread_local.loggers:
        # Crear carpeta de logs si no existe
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"session_{session_id}_{timestamp}.log"

        # Configurar logger
        logger = logging.getLogger(f"session_{session_id}")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # Formato
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info("=" * 100)
        logger.info(f"📝 Nueva sesión iniciada: {session_id}")
        logger.info(f"📁 Log file: {log_file}")
        logger.info("=" * 100)

        thread_local.loggers[session_id] = logger

    return thread_local.loggers[session_id]


# ============================================================================================================
# DEFINIR HERRAMIENTAS
# ============================================================================================================


@tool
def get_current_time(session_id: str = "default") -> str:
    """
    Obtiene la fecha y hora actual.

    Returns:
        Fecha y hora actual en formato legible
    """
    logger = get_session_logger(session_id)
    logger.info("🕐 Tool called: get_current_time")
    now = datetime.now()
    result = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"✅ Result: {result}")
    return f"Fecha y hora actual: {result}"


@tool
def calculate(expression: str, session_id: str = "default") -> str:
    """
    Evalúa una expresión matemática.
    Soporta: +, -, *, /, **, sqrt, sin, cos, tan, log, etc.

    Args:
        expression: Expresión matemática (ej: "2 + 2", "sqrt(16)")
    """
    logger = get_session_logger(session_id)
    logger.info(f"🧮 Tool called: calculate('{expression}')")
    try:
        safe_dict = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "pow": pow,
        }
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        logger.info(f"✅ Result: {result}")
        return f"Resultado: {result}"
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return error_msg


@tool
def read_text_file(file_path: str, session_id: str = "default") -> str:
    """
    Lee el contenido de un archivo de texto.

    Args:
        file_path: Ruta al archivo
    """
    logger = get_session_logger(session_id)
    logger.info(f"📄 Tool called: read_text_file('{file_path}')")
    try:
        if not os.path.exists(file_path):
            return f"Archivo no encontrado: {file_path}"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        max_chars = 2000
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... (truncado)"

        logger.info(f"✅ Read {len(content)} characters")
        return f"Contenido:\n\n{content}"
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"Error: {str(e)}"


@tool
def list_files(directory: str = ".", session_id: str = "default") -> str:
    """
    Lista archivos en un directorio.

    Args:
        directory: Ruta del directorio
    """
    logger = get_session_logger(session_id)
    logger.info(f"📁 Tool called: list_files('{directory}')")
    try:
        if not os.path.exists(directory):
            return f"Directorio no encontrado: {directory}"

        items = []
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(full_path)
                items.append(f"📄 {item} ({size} bytes)")

        result = "\n".join(items) if items else "Directorio vacío"
        logger.info(f"✅ Listed {len(items)} items")
        return f"Contenido de '{directory}':\n\n{result}"
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"Error: {str(e)}"


@tool
def create_text_file(file_path: str, content: str, session_id: str = "default") -> str:
    """
    Crea un archivo de texto.

    Args:
        file_path: Ruta del archivo
        content: Contenido a escribir
    """
    logger = get_session_logger(session_id)
    logger.info(f"✍️  Tool called: create_text_file('{file_path}')")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"✅ Created file ({len(content)} chars)")
        return f"Archivo creado: {file_path}"
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"Error: {str(e)}"


@tool
def convert_units(
    value: float, from_unit: str, to_unit: str, session_id: str = "default"
) -> str:
    """
    Convierte entre unidades.
    Soporta: meters, feet, kilometers, miles, celsius, fahrenheit, kilograms, pounds
    """
    logger = get_session_logger(session_id)
    logger.info(f"🔄 Tool called: convert_units({value} {from_unit} -> {to_unit})")

    conversions = {
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x / 3.28084,
        ("kilometers", "miles"): lambda x: x * 0.621371,
        ("miles", "kilometers"): lambda x: x / 0.621371,
        ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("kilograms", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kilograms"): lambda x: x / 2.20462,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        logger.info(f"✅ Result: {result}")
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    else:
        return f"Conversión no soportada: {from_unit} -> {to_unit}"


@tool
def count_words(text: str, session_id: str = "default") -> str:
    """
    Cuenta palabras, caracteres y líneas.
    """
    logger = get_session_logger(session_id)
    logger.info(f"📊 Tool called: count_words")

    words = len(text.split())
    chars = len(text)
    lines = len(text.split("\n"))

    result = f"Palabras: {words} | Caracteres: {chars} | Líneas: {lines}"
    logger.info(f"✅ {result}")
    return result


# ============================================================================================================
# CREAR AGENTE
# ============================================================================================================
def create_tool_agent():
    """Crea agente con herramientas"""
    llm = ChatBedrock(model_id=MODEL_ID, region_name=REGION, streaming=False)

    conn = sqlite3.connect(MEMORY_DB, check_same_thread=False)
    memory = SqliteSaver(conn)

    tools = [
        get_current_time,
        calculate,
        read_text_file,
        list_files,
        create_text_file,
        convert_units,
        count_words,
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        system_prompt=(
            "Eres un asistente con múltiples herramientas. "
            "Usa las herramientas cuando sea necesario y explica qué estás haciendo."
        ),
    )

    return agent


print("🤖 Creando agente...")
agent = create_tool_agent()
print("✅ Agente creado\n")


# ============================================================================================================
# FUNCIÓN PARA GRADIO
# ============================================================================================================
def predict(message, history, session_id):
    """
    Función de predicción con session_id
    """
    try:
        # Obtener logger para esta sesión
        logger = get_session_logger(session_id)
        logger.info("=" * 80)
        logger.info(f"👤 User: {message}")

        # Configuración con session_id
        config = {"configurable": {"thread_id": session_id}}

        # Invocar agente
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]}, config=config
        )

        # Extraer respuesta
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                response = last_message.content
            elif isinstance(last_message, dict):
                response = last_message.get("content", "Sin respuesta")
            else:
                response = "Sin respuesta"

            logger.info(f"🤖 Assistant: {response}")
            return response

        return "Sin respuesta"

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return error_msg


# ============================================================================================================
# INTERFAZ GRADIO
# ============================================================================================================
print("🎨 Creando interfaz Gradio...")

with gr.Blocks(title="Tool Agent - Practice 7") as demo:
    gr.Markdown("# 🤖 Agente con Herramientas - Practice 7")
    gr.Markdown(
        """
    Agente con acceso a múltiples herramientas:
    - 🕐 Hora actual
    - 🧮 Calculadora matemática
    - 📄 Leer/crear archivos
    - 📁 Listar directorios
    - 🔄 Convertir unidades
    - 📊 Contar palabras
    
    **Logs guardados en:** `logs/session_{session_id}_{timestamp}.log`
    """
    )

    with gr.Row():
        session_input = gr.Textbox(
            label="Session ID",
            value="default",
            placeholder="Ingresa un ID de sesión único",
        )

    chatbot = gr.ChatInterface(
        fn=lambda msg, hist: predict(msg, hist, session_input.value),
        examples=[
            "¿Qué hora es?",
            "Calcula la raíz cuadrada de 144",
            "Lista los archivos en el directorio actual",
            "Convierte 100 fahrenheit a celsius",
            "Cuenta las palabras en: Python es genial",
        ],
        title=None,
    )

print("✅ Interfaz creada")
print("\n" + "=" * 100)
print("🚀 INICIANDO SERVIDOR GRADIO")
print("=" * 100)
print("💡 Cada sesión tendrá su propio archivo de log")
print("=" * 100 + "\n")

demo.launch(share=True, server_name="0.0.0.0", server_port=7860, show_error=True)
