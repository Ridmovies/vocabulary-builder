from pydantic import BaseModel


class TypingCheckRequest(BaseModel):
    word_id: int
    answer: str