from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VoteCreate(BaseModel):
    user_id: int
    article_id: int
    value: int


class VotePublic(BaseModel):
    id: int
    user_id: int
    article_id: int
    value: int
    created_at: datetime

    model_config = {"from_attributes": True}

class VotesPublic(BaseModel):
    data: list[VotePublic]

    model_config = {"from_attributes": True}