import os

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME") or 'gpt-4o-mini'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or None
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL") or None
GROQ_MODEL_NAME = os.environ.get("GROQ_MODEL_NAME") or 'llama-3.1-8b-instant'

if not OPENAI_API_KEY:
    raise NotImplementedError("OPEN_API_KEY is required")

if not GROQ_API_KEY:
    raise NotImplementedError("GROQ_API_KEY is required")

def get_openai_llm():
    openai_params = {
    "model": OPENAI_MODEL_NAME,
    "api_key": OPENAI_API_KEY,  
    }
    if OPENAI_BASE_URL:
        openai_params["base_url"] = OPENAI_BASE_URL
    return ChatOpenAI(**openai_params)

def get_groq_llm():
    openai_params = {
    "model": GROQ_MODEL_NAME,
    "api_key": GROQ_API_KEY,  
    }
    if GROQ_BASE_URL:
        openai_params["base_url"] = GROQ_BASE_URL
    return ChatGroq(**openai_params)


