"""Shared LangGraph state definition for the exam generation pipeline."""

from typing import TypedDict, Any


class ExamPipelineState(TypedDict, total=False):
    """State shared across all agents in the LangGraph pipeline."""

    # Input from admin
    subject: str
    topic: str
    syllabus: str
    pdf_paths: list[str]
    duration_minutes: int
    num_mcq: int
    num_short: int
    num_long: int
    marks_mcq: int
    marks_short: int
    marks_long: int
    created_by: str

    # Agent 1 — Content Understanding
    pdf_text: str
    chunks: list[str]
    topics: list[str]
    store_id: str

    # Agent 2 — Question Generator
    questions: list[dict]

    # Agent 3 — Website Builder
    exam_config: dict

    # Agent 4 — Exam Manager
    exam_code: str
    exam_id: str

    # Metadata
    error: str | None
    status: str
