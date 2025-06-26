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

    @field_validator('icon_color_hex')
    @classmethod
    def validate_icon_color_hex(cls, v: str) -> str:
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('icon_color_hex must start with "#" and be exactly 7 characters long')
        return v
