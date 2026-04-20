"""Admin routes — PDF upload and exam creation."""

import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from database import get_database
from utils.auth import require_admin
from config import UPLOAD_DIR
from agents.orchestrator import run_exam_pipeline
from bson import ObjectId

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ─── Schemas ─────────────────────────────────────────────────────────

class CreateExamRequest(BaseModel):
    subject: str
    topic: str
    syllabus: str = ""
    duration_minutes: int = 30
    num_mcq: int = 5
    num_short: int = 3
    num_long: int = 2
    marks_mcq: int = 1
    marks_short: int = 3
    marks_long: int = 5
    pdf_filenames: list[str]  # filenames from the upload step


# ─── Endpoints ───────────────────────────────────────────────────────

@router.post("/upload")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    admin: dict = Depends(require_admin),
):
    """Upload up to 5 PDF files for exam generation."""
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 5 PDF files")

    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Please select at least one PDF file")

    filenames = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. '{file.filename}' is not a PDF.")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        filenames.append(file.filename)

    return {
        "message": f"{len(filenames)} PDF(s) uploaded successfully",
        "filenames": filenames,
    }


@router.post("/create-exam")
async def create_exam(
    req: CreateExamRequest,
    admin: dict = Depends(require_admin),
):
    """Trigger the full multi-agent exam generation pipeline."""
    # Validate all PDF files exist
    pdf_paths = []
    for filename in req.pdf_filenames:
        pdf_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"PDF file '{filename}' not found. Upload it first.")
        pdf_paths.append(pdf_path)

    # Build pipeline input state
    input_state = {
        "subject": req.subject,
        "topic": req.topic,
        "syllabus": req.syllabus,
        "pdf_paths": pdf_paths,
        "duration_minutes": req.duration_minutes,
        "num_mcq": req.num_mcq,
        "num_short": req.num_short,
        "num_long": req.num_long,
        "marks_mcq": req.marks_mcq,
        "marks_short": req.marks_short,
        "marks_long": req.marks_long,
        "created_by": admin.get("sub", ""),
    }

    # Run the LangGraph pipeline
    result = await run_exam_pipeline(input_state)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "message": "Exam created successfully!",
        "exam_code": result.get("exam_code"),
        "exam_id": result.get("exam_id"),
        "total_questions": len(result.get("questions", [])),
        "duration_minutes": req.duration_minutes,
    }


@router.get("/exams")
async def list_exams(admin: dict = Depends(require_admin)):
    """List all exams created by this admin."""
    db = get_database()

    exams = await db.exams.find(
        {"created_by": admin.get("sub", "")},
        {"questions": 0}  # Exclude full questions for listing
    ).sort("created_at", -1).to_list(length=100)

    # Convert ObjectId to string
    for exam in exams:
        exam["_id"] = str(exam["_id"])

    return {"exams": exams}


@router.get("/exam/{exam_id}")
async def get_exam_details(exam_id: str, admin: dict = Depends(require_admin)):
    """Get full exam details including questions (admin only)."""
    db = get_database()

    exam = await db.exams.find_one({"_id": ObjectId(exam_id)})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    exam["_id"] = str(exam["_id"])
    return {"exam": exam}
