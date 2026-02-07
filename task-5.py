import json
import boto3
import sqlite3
from langchain_aws import ChatBedrock
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
import sys

MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

def load_model() -> ChatBedrock:
    """
    Get Bedrock model client.
    Uses IAM authentication via the execution role.
    """
    return ChatBedrock(
        model_id=MODEL_ID,
        region_name='us-east-1',
        streaming=True  # IMPORTANTE: Habilitar streaming
    )

def create_chatbot_with_memory():
    """
    Crea un chatbot con memoria persistente y summarization automática
    """
    # Cargar modelo
    llm = load_model()
    
    # Crear memoria persistente con SQLite
    conn = sqlite3.connect("chatbot_memory.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Crear agente con memoria y middleware de summarization built-in
    agent = create_agent(
        model=llm,
        tools=[],  # Sin herramientas por ahora
        checkpointer=memory,
        middleware=[
            SummarizationMiddleware(
                model=llm,
                trigger=("messages", 10),  # Resume después de 10 mensajes
                keep=("messages", 4),       # Mantiene los últimos 4 mensajes
            ),
        ],
    )
    
    return agent

def chat_session_terminal(thread_id="default_conversation"):
    """
    Sesión de chat interactiva en TERMINAL con streaming de tokens
    
    Args:
        thread_id: ID único para la conversación (permite múltiples conversaciones)
    """
    print("="*100)
    print("🤖 CHATBOT CON MEMORIA PERSISTENTE, STREAMING Y SUMMARIZATION AUTOMÁTICA")
    print("="*100)
    print(f"📌 Thread ID: {thread_id}")
    print("💡 Escribe 'salir' para terminar")
    print("💡 Escribe 'historial' para ver el historial de la conversación")
    print("💡 Escribe 'nuevo' para iniciar una nueva conversación")
    print("💡 Escribe 'stats' para ver estadísticas de la conversación")
    print("="*100 + "\n")
    
    # Crear chatbot
    agent = create_chatbot_with_memory()
    
    # Configuración con thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # Loop de conversación
    while True:
        try:
            # Input del usuario
            user_input = input("👤 Tú: ").strip()
            
            if not user_input:
                continue
                
            # Comandos especiales
            if user_input.lower() == 'salir':
                print("\n👋 ¡Hasta luego!")
                break
                
            if user_input.lower() == 'historial':
                # Obtener estado actual (historial)
                state = agent.get_state(config)
                if state and 'messages' in state.values:
                    print("\n" + "="*100)
                    print("📜 HISTORIAL DE CONVERSACIÓN:")
                    print("="*100)
                    for msg in state.values['messages']:
                        if isinstance(msg, (HumanMessage, AIMessage)):
                            role = "👤 Usuario" if isinstance(msg, HumanMessage) else "🤖 Asistente"
                            print(f"\n{role}: {msg.content}")
                    print("="*100 + "\n")
                else:
                    print("\n⚠️  No hay historial disponible\n")
                continue
                
            if user_input.lower() == 'stats':
                # Mostrar estadísticas
                state = agent.get_state(config)
                if state:
                    message_count = len(state.values.get('messages', []))
                    has_summary = 'summary' in state.values
                    print("\n" + "="*100)
                    print("📊 ESTADÍSTICAS DE LA CONVERSACIÓN:")
                    print("="*100)
                    print(f"  Mensajes actuales en memoria: {message_count}")
                    print(f"  ¿Tiene resumen?: {'Sí' if has_summary else 'No'}")
                    if has_summary and state.values.get('summary'):
                        print(f"  Longitud del resumen: {len(state.values['summary'])} caracteres")
                    print("="*100 + "\n")
                continue
                
            if user_input.lower() == 'nuevo':
                # Cambiar a un nuevo thread_id
                import time
                thread_id = f"conversation_{int(time.time())}"
                config = {"configurable": {"thread_id": thread_id}}
                print(f"\n🆕 Nueva conversación iniciada - Thread ID: {thread_id}\n")
                continue
            
            # Invocar el modelo con memoria y STREAMING DE TOKENS
            print("\n🤖 Asistente: ", end="", flush=True)
            
            # Usar stream_mode="messages" para streaming de tokens del LLM
            for message_chunk, metadata in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                stream_mode="messages"  # CAMBIO CLAVE: usar "messages" en lugar de "values"
            ):
                # message_chunk contiene los tokens individuales
                # Solo imprimir si hay contenido
                if message_chunk.content:
                    print(message_chunk.content, end="", flush=True)
            
            print("\n")  # Nueva línea al final
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupción detectada. Escribe 'salir' para terminar.\n")
            continue
        except EOFError:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

def main():
    """
    Función principal para ejecutar desde terminal
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Chatbot con memoria persistente")
    parser.add_argument(
        "--thread-id",
        type=str,
        default="default_conversation",
        help="ID del thread de conversación (default: default_conversation)"
    )
    
    args = parser.parse_args()
    
    try:
        chat_session_terminal(thread_id=args.thread_id)
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)

if __name__ == "__main__":
    main()