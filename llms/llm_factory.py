# llm_factory.py - Maps LLM name strings to actual LLM objects
# Example: "kimi" -> ChatKimi(...), "openai" -> ChatOpenAI(...)

from langchain_ollama import ChatOllama
from config import LLM_MODEL, LLM_TEMPERATURE


def get_llm():
    """
    Creates and returns the configured LLM instance.
    Swap the LLM provider here without touching any other file.
    """
    return ChatOllama(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )