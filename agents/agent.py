"""
CV Extraction Agent using AWS Bedrock and LangChain.
"""

from langchain_aws import ChatBedrock
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from templates import cv_chat_template, summary_template

# Use simple model ID instead of ARN
MODEL_ID = "us.amazon.nova-pro-v1:0"


def load_model() -> ChatBedrock:
    """
    Get Bedrock model client.
    Uses IAM authentication via the execution role.
    """
    return ChatBedrock(model_id=MODEL_ID)


class CVExtractionAgent:
    """
    Agent for analyzing and extracting information from CVs.
    """

    def __init__(self, cv_text: str):
        """
        Initialize the CV extraction agent.

        Args:
            cv_text: The raw CV text to analyze
        """
        self.cv_text = cv_text
        self.model = load_model()
        self.chat_history_store = {}

        # Create the main chat chain
        self.chat_chain = cv_chat_template | self.model

        # Create a chain with message history
        self.conversational_chain = RunnableWithMessageHistory(
            self.chat_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        # Create summary chain
        self.summary_chain = summary_template | self.model

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """
        Get or create chat history for a session.

        Args:
            session_id: Unique identifier for the chat session

        Returns:
            Chat message history for the session
        """
        if session_id not in self.chat_history_store:
            self.chat_history_store[session_id] = InMemoryChatMessageHistory()
        return self.chat_history_store[session_id]

    def chat(self, user_input: str, session_id: str = "default") -> str:
        """
        Chat with the agent about the CV.

        Args:
            user_input: User's question or request
            session_id: Session identifier for conversation history

        Returns:
            Agent's response
        """
        response = self.conversational_chain.invoke(
            {"input": user_input, "cv_text": self.cv_text},
            config={"configurable": {"session_id": session_id}},
        )
        return response.content

    def generate_summary(self) -> str:
        """
        Generate a professional summary of the CV.

        Returns:
            Professional summary text
        """
        response = self.summary_chain.invoke({"cv_text": self.cv_text})
        return response.content

    def clear_history(self, session_id: str = "default"):
        """
        Clear chat history for a session.

        Args:
            session_id: Session identifier to clear
        """
        if session_id in self.chat_history_store:
            del self.chat_history_store[session_id]
