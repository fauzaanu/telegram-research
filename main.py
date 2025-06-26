import logging
import os
import uuid
from collections import deque
from typing import List

from dotenv import load_dotenv
from openai.types.chat import (ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam)
from telebot import TeleBot
from telebot.types import ForumTopic

from models import Answer, SystemPrompt, Tasks, TelegramTopic
from settings import LLM_MAX_RETRIES, get_ollama_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ResearchAgent:
    """TelegramResearchAgent"""

    def __init__(self, query: str):
        self.query = query
        self.hash_topic_dic = {}

    def _get_system_prompt(self, prompt):
        prompt = (f"User prompt: {prompt}"
                  "Given the above user_prompt,"
                  "generate exactly one ready-to-use system prompt (no explanations, no commentary) "
                  "that:\n"
                  "- Explicitly positions the model as an expert\n"
                  "Remmember that the system prompt should be based on the prompt. For example if the prompt is trying to answer a question regarding Heart dieseases, a good system prompt for that prompt would be (e.g. “You are a senior cardiologist with 15 years of clinical research experience”)")
        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content="You are an expert prompt engineer. "),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]
        client = get_ollama_client()
        response = self._get_response(client, SystemPrompt, messages)
        return response.system_prompt + "/no_think"

    def _form_meessages(self, prompt):
        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=self._get_system_prompt(prompt)),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]
        return messages

    def _get_response(self, client, pydantic_model, messages):
        # model = "llama3-8k"
        model = "qwen3-12k"
        # model = "deepseek-r1"
        response = client.chat.completions.create(model=model, max_tokens=8192, response_model=pydantic_model, messages=messages, max_retries=LLM_MAX_RETRIES)
        return response

    def create_tasks(self):
        logger.info("Creating tasks")
        prompt = (f"You are tasked with researching the topic: {self.query}.\n"
                  "Generate a list of **3 direct questions** "
                  "to explore this topic thoroughly.\n\n"
                  "Instructions:\n"
                  "- Do not ask questions where there is no definite answer or there is debate"
                  "- Make sure each question is specific, focused, clear, and well-structured and really short.\n")
        messages = self._form_meessages(prompt)
        client = get_ollama_client()
        response = self._get_response(client, Tasks, messages)

        return self.ask_questions(response.tasks_list)

    def _get_bot(self):
        load_dotenv()
        bot = TeleBot(os.getenv("TELEGRAM_TOKEN"))
        return bot

    def _create_telegram_topic(self, question) -> ForumTopic:

        prompt = (f"Create a telegram group topic to store messages related to the following question."
                  f"Also give a hex color code like #ffffff that resonates with the topic."
                  f"-------------"
                  f"{question}")
        messages = self._form_meessages(prompt)
        client = get_ollama_client()
        response = self._get_response(client, TelegramTopic, messages)
        bot = self._get_bot()
        topic = bot.create_forum_topic(chat_id=int(os.getenv("TELEGRAM_CHAT")), name=response.name, icon_color=response.icon_color_hex, icon_custom_emoji_id=None)
        return topic

    def ask_questions(self, questions_tasks: List):
        # initialize the queue with all primary tasks
        queue = deque([(task, uuid.uuid4().hex) for task in questions_tasks])

        while queue:
            task, task_hash = queue.popleft()

            if task_hash not in self.hash_topic_dic:
                topic: ForumTopic = self._create_telegram_topic(task.focused_question)
                self.hash_topic_dic[task_hash] = topic

            logger.info(f"Asking {task.focused_question}")
            prompt = (f"I am conducting in-depth research on the topic: {self.query}.\n"
                      "Please answer the following question in a very direct and concise way:\n"
                      f"{task.focused_question}\n\n"
                      "Instructions:\n"
                      "- Provide a clear and well-reasoned answer.\n"
                      "- Keep the tone academic.\n"
                      "- Avoid vague generalizations. Be specific and concise.\n"
                      "- Don’t include any unnecessary comments.\n")
            messages = self._form_meessages(prompt)
            client = get_ollama_client()
            response = self._get_response(client, Answer, messages)

            # write the answer
            self.write_article(response.answer, task.focused_question, task_hash)

            # any follow-ups inherit the same hash
            if response.additional_questions_for_answer:
                for follow in response.additional_questions_for_answer:
                    queue.append((follow, task_hash))

    def _send_telegram(self, hash, question, answer):
        tg_msg = f"""
__{hash}__
**{question}**

{answer}
"""
        bot = self._get_bot()
        topic_id = self.hash_topic_dic[hash].message_thread_id
        chat_id = int(os.getenv("TELEGRAM_CHAT"))
        bot.send_message(chat_id=chat_id, text=tg_msg, message_thread_id=topic_id, parse_mode='markdown')

    def write_article(self, answer_text, question, task_hash):

        self._send_telegram(task_hash, question, answer_text)

        main_path = os.path.join("research", task_hash)
        os.makedirs(main_path, exist_ok=True)

        filepath = os.path.join(main_path, f"{uuid.uuid4().hex}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {question}\n\n{answer_text}")


if __name__ == '__main__':
    ResearchAgent("How to get started to make home Solar energy").create_tasks()
