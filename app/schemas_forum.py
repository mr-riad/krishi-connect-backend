"""
Pydantic schemas for Community Forum
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ForumPostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    body: str = Field(..., min_length=5, max_length=5000)
    post_type: str = Field("question", description="question | experience")
    media_urls: list[str] = Field(default_factory=list, max_length=5)


class ForumPostOut(BaseModel):
    id: str
    title: str
    body: str
    post_type: str
    media_urls: list[str] = []
    author_id: str
    author_name: str | None = None
    author_upazila: str | None = None
    likes: int = 0
    liked_by: list[str] = []
    comment_count: int = 0
    is_deleted: bool = False
    created_at: datetime


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class CommentOut(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_name: str | None = None
    text: str
    is_deleted: bool = False
    created_at: datetime


class ReportCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500,
                        description="Reason for reporting (spam, inappropriate, etc.)")
