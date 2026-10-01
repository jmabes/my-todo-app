"""Pydantic schemas shared by the storage layer and the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

TITLE_MAX_LENGTH = 200


class TodoCreate(BaseModel):
    # Strip before validating so whitespace-only titles are rejected.
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)


class TodoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LENGTH)
    completed: bool | None = None


class Todo(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime
