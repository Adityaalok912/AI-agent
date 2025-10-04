import os

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
# OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME") or 'gpt-4o-mini'
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or None
# GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL") or None
# GROQ_MODEL_NAME = os.environ.get("GROQ_MODEL_NAME") or 'llama-3.1-8b-instant'

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or None
GOOGLE_MODEL_NAME = os.environ.get("GOOGLE_MODEL_NAME") or 'gemini-2.5-flash'


# if not OPENAI_API_KEY:
#     raise NotImplementedError("OPEN_API_KEY is required")

# if not GROQ_API_KEY:
#     raise NotImplementedError("GROQ_API_KEY is required")

if not GOOGLE_API_KEY:
    raise NotImplementedError("GROQ_API_KEY is required")

#                          openai llm
# def get_openai_llm():
#     openai_params = {
#     "model": OPENAI_MODEL_NAME,
#     "api_key": OPENAI_API_KEY,  
#     }
#     if OPENAI_BASE_URL:
#         openai_params["base_url"] = OPENAI_BASE_URL
#     return ChatOpenAI(**openai_params)


#                          groq llm
# def get_groq_llm():
#     groq_params = {
#     "model": GROQ_MODEL_NAME,
#     "api_key": GROQ_API_KEY,  
#     }
#     if GROQ_BASE_URL:
#         groq_params["base_url"] = GROQ_BASE_URL
#     return ChatGroq(**groq_params)


#                         google llm
def get_groq_llm():
    google_params = {
    "model": GOOGLE_MODEL_NAME,
    "api_key": GOOGLE_API_KEY,  
    }
    # if GROQ_BASE_URL:
    #     groq_params["base_url"] = GROQ_BASE_URL
    return ChatGoogleGenerativeAI(**google_params)

