"""Agent 5 — Evaluation Agent.

MCQs scored directly. Subjective answers scored via LLM semantic comparison.
"""

from services.llm_service import generate_json


async def evaluation_agent(questions: list, answers: list) -> dict:
    """Evaluate student answers against model answers.

    Args:
        questions: List of question dicts from the exam.
        answers: List of student answer dicts [{question_id, answer}].

    Returns:
        dict with score, max_score, percentage, and per-question details.
    """
    print("✅ Agent 5: Evaluation — scoring answers...")

    # Build answer lookup
    answer_map = {}
    for ans in answers:
        answer_map[str(ans.get("question_id"))] = ans.get("answer", "")

    evaluation_details = []
    total_score = 0
    max_score = 0

    for q in questions:
        qid_raw = q.get("id")
        qid = str(qid_raw) if qid_raw is not None else ""
        q_type = q.get("type", "mcq")
        marks = q.get("marks", 1)
        max_score += marks
        student_answer = answer_map.get(qid, "")

        if not student_answer or student_answer.strip() == "":
            evaluation_details.append({
                "question_id": qid_raw,
                "type": q_type,
                "marks_obtained": 0,
                "marks_total": marks,
                "feedback": "No answer provided.",
                "correct_answer": q.get("correct_answer", q.get("model_answer", "")),
            })
            continue

        if q_type == "mcq":
            # Direct comparison for MCQs
            correct = q.get("correct_answer", "")
            print(f"[DEBUG MCQ] student_answer='{student_answer}', correct='{correct}'")
            is_correct = student_answer.strip().lower() == correct.strip().lower()
            score = marks if is_correct else 0
            total_score += score

            evaluation_details.append({
                "question_id": qid_raw,
                "type": "mcq",
                "marks_obtained": score,
                "marks_total": marks,
                "is_correct": is_correct,
                "student_answer": student_answer,
                "correct_answer": correct,
                "feedback": "Correct! ✅" if is_correct else f"Incorrect. The correct answer is: {correct}",
                "explanation": q.get("explanation", ""),
            })
        else:
            # Semantic evaluation for short/long answers via LLM
            model_answer = q.get("model_answer", "")
            keywords = q.get("keywords", [])

            eval_prompt = f"""You are an exam evaluator. Score the student's answer against the model answer.

Question: {q.get('question', '')}
Question Type: {q_type} (max marks: {marks})
Model Answer: {model_answer}
Key Concepts: {', '.join(keywords)}
Student Answer: {student_answer}

Evaluate the student's answer and return JSON:
{{
  "marks_obtained": <number between 0 and {marks}>,
  "feedback": "<specific constructive feedback>",
  "key_points_covered": ["point1", "point2"],
  "key_points_missed": ["point1", "point2"]
}}

Be fair but rigorous. Give partial marks for partially correct answers."""

            try:
                eval_result = generate_json(eval_prompt)
                score = min(eval_result.get("marks_obtained", 0), marks)
                total_score += score

                evaluation_details.append({
                    "question_id": qid_raw,
                    "type": q_type,
                    "marks_obtained": score,
                    "marks_total": marks,
                    "student_answer": student_answer,
                    "model_answer": model_answer,
                    "feedback": eval_result.get("feedback", ""),
                    "key_points_covered": eval_result.get("key_points_covered", []),
                    "key_points_missed": eval_result.get("key_points_missed", []),
                })
            except Exception as e:
                # Fallback: simple keyword matching
                keyword_matches = sum(
                    1 for kw in keywords
                    if kw.lower() in student_answer.lower()
                )
                score = round(marks * keyword_matches / max(len(keywords), 1))
                score = min(score, marks)
                total_score += score

                evaluation_details.append({
                    "question_id": qid_raw,
                    "type": q_type,
                    "marks_obtained": score,
                    "marks_total": marks,
                    "student_answer": student_answer,
                    "model_answer": model_answer,
                    "feedback": f"Evaluated using keyword matching ({keyword_matches}/{len(keywords)} keywords found).",
                })

    percentage = round((total_score / max_score * 100), 1) if max_score > 0 else 0

    print(f"   ✅ Score: {total_score}/{max_score} ({percentage}%)")

    return {
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "evaluation_details": evaluation_details,
    }
