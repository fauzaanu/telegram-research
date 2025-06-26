import unittest
from typing import List, Literal

import instructor
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from pydantic import BaseModel


class PreApplicationTests(unittest.TestCase):
    def setUp(self):
        ...

    def test_instructor_responds_with_structured_output(self):
        OLLAMA_BASE_URL = "http://localhost:11434/v1"
        OLLAMA_API_KEY = "ollama"
        LLM_MODEL = "llama3"
        LLM_MAX_RETRIES = 2000

        class Answer(BaseModel):
            answer: Literal["yes", "no"]

        model = LLM_MODEL
        openai_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

        SYSTEM_PROMPT = "You are a helpful assistant"
        prompt = "the sky is blue."

        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]

        client = instructor.from_openai(openai_client, mode=instructor.Mode.JSON)
        response = client.chat.completions.create(model=model, response_model=Answer, messages=messages, max_retries=LLM_MAX_RETRIES)
        print(response)
