from typing import Optional
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, Text, Boolean, Float, DateTime
from datetime import datetime, timezone


class ParsedError(Base):
    __tablename__ = "parsed_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # raw input error log
    raw_error_log: Mapped[str] = mapped_column(String, nullable=False)
    # parsed fields
    error_type: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=True)
    framework: Mapped[str] = mapped_column(String, nullable=True)

    # location info
    file_name: Mapped[str] = mapped_column(String, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=True)
    function_name: Mapped[str] = mapped_column(String, nullable=True)

    # stack trace (array of stack frames)
    stack_trace: Mapped[dict] = mapped_column(JSON, nullable=True)

    # metadata
    confidence_score: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self):
        return f"<ParsedError(id={self.id}, type={self.error_type})>"


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Link to parsed error
    parsed_error_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Analysis results
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    solutions: Mapped[dict] = mapped_column(JSON, nullable=False)  # Array of solutions

    # Metadata
    sources_used: Mapped[int] = mapped_column(Integer, nullable=True)
    analysis_time: Mapped[int] = mapped_column(Integer, nullable=True)  # milliseconds
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self):
        return f"<Analysis(id={self.id}, error_id={self.parsed_error_id})>"


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Link to analysis
    analysis_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Which solution did they try?
    solution_index: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # 0, 1, or 2

    # Did it work?
    worked: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Optional user notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback(id={self.id}, analysis_id={self.analysis_id}, worked={self.worked})>"


class CostTracking(Base):
    __tablename__ = "cost_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # What operation?
    operation: Mapped[str] = mapped_column(
        String
    )  # 'embedding', 'analysis', 'baseline_eval'

    # Token usage
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost (in USD)
    cost: Mapped[float] = mapped_column(Float)

    # Model used
    model: Mapped[str] = mapped_column()

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CostTracking(operation={self.operation}, cost=${self.cost:.4f})>"
