from app.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ARRAY
from datetime import datetime


class StackOverFlowPost(Base):
    __tablename__ = "stackoverflow_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(Text)
    question_body: Mapped[str] = mapped_column(Text)
    answer_body: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    votes: Mapped[int] = mapped_column()
    url: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    scraped_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
