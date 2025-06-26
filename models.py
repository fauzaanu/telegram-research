from typing import List

from pydantic import BaseModel, field_validator, validator


class AIQuestionTask(BaseModel):
    focused_question: str


class Tasks(BaseModel):
    tasks_list: List[AIQuestionTask]


class Passage(BaseModel):
    headline: str
    content: str


class SystemPrompt(BaseModel):
    system_prompt: str


class Answer(BaseModel):
    additional_questions_for_answer: List[AIQuestionTask] | None
    answer: str


class TelegramTopic(BaseModel):
    name: str
    icon_color_hex: str

    # TODO:  Color of the topic icon in RGB format. Currently, must be one of 0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, or 0xFB6F5F  #         :type icon_color: :obj:`int`
