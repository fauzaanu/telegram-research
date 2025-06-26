import instructor
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
LLM_MAX_RETRIES = 2000


def get_ollama_client():
    oll_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    return instructor.from_openai(oll_client, mode=instructor.Mode.OPENROUTER_STRUCTURED_OUTPUTS)