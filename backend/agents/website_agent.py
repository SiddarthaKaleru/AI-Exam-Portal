"""Agent 3 — Website Builder Agent.

Generates exam configuration JSON for the React frontend to render dynamically.
"""


def website_agent(state: dict) -> dict:
    """Generate exam configuration for the frontend."""
    print("🌐 Agent 3: Website Builder — creating exam config...")

    questions = state.get("questions", [])

    # Organize questions by type
    mcqs = [q for q in questions if q.get("type") == "mcq"]
    shorts = [q for q in questions if q.get("type") == "short"]
    longs = [q for q in questions if q.get("type") == "long"]

    # Calculate total marks
    total_marks = sum(q.get("marks", 1) for q in questions)

    # Build exam configuration
    exam_config = {
        "title": f"{state.get('subject', 'Exam')} — {state.get('topic', 'Assessment')}",
        "subject": state.get("subject", ""),
        "topic": state.get("topic", ""),
        "duration_minutes": state.get("duration_minutes", 30),
        "total_marks": total_marks,
        "total_questions": len(questions),
        "sections": [],
        "instructions": [
            "Read each question carefully before answering.",
            "MCQs have only one correct answer.",
            "Short answer questions should be answered in 2-4 sentences.",
            "Long answer questions require detailed explanations.",
            "The exam will auto-submit when the timer runs out.",
            "Do not switch tabs or copy-paste during the exam.",
        ],
        "ui": {
            "theme": "dark",
            "show_question_nav": True,
            "show_timer": True,
            "allow_review": True,
            "auto_submit": True,
        },
    }

    # Build sections
    if mcqs:
        exam_config["sections"].append({
            "name": "Multiple Choice Questions",
            "type": "mcq",
            "count": len(mcqs),
            "marks_each": mcqs[0].get("marks", 1) if mcqs else 1,
            "question_ids": [q["id"] for q in mcqs],
        })

    if shorts:
        exam_config["sections"].append({
            "name": "Short Answer Questions",
            "type": "short",
            "count": len(shorts),
            "marks_each": shorts[0].get("marks", 3) if shorts else 3,
            "question_ids": [q["id"] for q in shorts],
        })

    if longs:
        exam_config["sections"].append({
            "name": "Long Answer Questions",
            "type": "long",
            "count": len(longs),
            "marks_each": longs[0].get("marks", 5) if longs else 5,
            "question_ids": [q["id"] for q in longs],
        })

    print(f"   ✅ Exam config: {total_marks} marks, {len(exam_config['sections'])} sections")

    return {
        **state,
        "exam_config": exam_config,
        "status": "config_generated",
    }
