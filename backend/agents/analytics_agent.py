"""Agent 7 — Analytics Agent.

Aggregates submission data to produce dashboard-ready analytics.
"""

from database import get_database
from bson import ObjectId


async def analytics_agent(exam_id: str) -> dict:
    """Generate analytics for an exam.

    Args:
        exam_id: MongoDB ObjectId string of the exam.

    Returns:
        dict with charts-ready analytics data.
    """
    print("📊 Agent 7: Analytics — generating dashboard data...")

    db = get_database()

    # Fetch exam and all submissions
    exam = await db.exams.find_one({"_id": ObjectId(exam_id)})
    if not exam:
        return {"error": "Exam not found"}

    submissions = await db.submissions.find({"exam_id": exam_id}).to_list(length=1000)

    if not submissions:
        return {
            "exam_title": exam.get("title", ""),
            "total_students": 0,
            "message": "No submissions yet",
        }

    # ─── Basic Stats ─────────────────────────────────────────────
    scores = [s.get("percentage", 0) for s in submissions]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    max_score_val = max(scores) if scores else 0
    min_score_val = min(scores) if scores else 0

    # ─── Student Rankings ────────────────────────────────────────
    # Pre-fetch user details for backward compatibility with legacy submissions
    student_ids = [ObjectId(s["student_id"]) for s in submissions if s.get("student_id") and len(s["student_id"]) == 24]
    users_cursor = db.users.find({"_id": {"$in": student_ids}})
    user_map = {str(u["_id"]): u async for u in users_cursor}

    rankings = []
    for s in sorted(submissions, key=lambda x: x.get("percentage", 0), reverse=True):
        sid = s.get("student_id", "")
        db_user = user_map.get(sid, {})
        
        # Determine actual name and email, falling back to db_user if missing in submission
        s_email = s.get("student_email") or db_user.get("email") or s.get("student_name", "Unknown")
        s_name = db_user.get("name") or s.get("student_name", "Unknown")
        
        # If the stored 'name' is literally the email, and we didn't find a real name, keep it as email
        
        rankings.append({
            "student_name": s_name,
            "student_email": s_email,
            "student_id": sid,
            "score": s.get("score", 0),
            "max_score": s.get("max_score", 0),
            "percentage": s.get("percentage", 0),
            "tab_switch_auto_submitted": s.get("tab_switch_auto_submitted", False),
            "anti_cheat_flags": s.get("anti_cheat_flags", []),
        })

    # ─── Score Distribution ──────────────────────────────────────
    distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for pct in scores:
        if pct <= 20:
            distribution["0-20"] += 1
        elif pct <= 40:
            distribution["21-40"] += 1
        elif pct <= 60:
            distribution["41-60"] += 1
        elif pct <= 80:
            distribution["61-80"] += 1
        else:
            distribution["81-100"] += 1

    # ─── Topic-wise Analysis ─────────────────────────────────────
    topic_scores = {}
    for s in submissions:
        for detail in s.get("evaluation_details", []):
            topic = "General"
            # Find topic from question
            qid = detail.get("question_id")
            for q in exam.get("questions", []):
                if q.get("id") == qid:
                    topic = q.get("topic", "General")
                    break

            if topic not in topic_scores:
                topic_scores[topic] = {"total": 0, "max": 0, "count": 0}
            topic_scores[topic]["total"] += detail.get("marks_obtained", 0)
            topic_scores[topic]["max"] += detail.get("marks_total", 0)
            topic_scores[topic]["count"] += 1

    topic_analysis = []
    for topic, data in topic_scores.items():
        avg = round((data["total"] / data["max"] * 100), 1) if data["max"] > 0 else 0
        topic_analysis.append({
            "topic": topic,
            "average_percentage": avg,
            "total_attempts": data["count"],
            "is_weak": avg < 50,
        })

    # ─── Difficulty Analysis ─────────────────────────────────────
    difficulty_stats = {"easy": {"correct": 0, "total": 0}, "medium": {"correct": 0, "total": 0}, "hard": {"correct": 0, "total": 0}}
    for s in submissions:
        for detail in s.get("evaluation_details", []):
            qid = detail.get("question_id")
            for q in exam.get("questions", []):
                if q.get("id") == qid:
                    diff = q.get("difficulty", "medium")
                    if diff in difficulty_stats:
                        difficulty_stats[diff]["total"] += 1
                        if detail.get("marks_obtained", 0) > 0:
                            difficulty_stats[diff]["correct"] += 1
                    break

    # ─── Anti-cheat Summary ──────────────────────────────────────
    suspicious_count = sum(
        1 for s in submissions
        if s.get("anti_cheat_flags") and len(s["anti_cheat_flags"]) > 0
    )

    analytics = {
        "exam_title": exam.get("title", ""),
        "exam_code": exam.get("exam_code", ""),
        "total_students": len(submissions),
        "average_score": avg_score,
        "highest_score": max_score_val,
        "lowest_score": min_score_val,
        "rankings": rankings,
        "score_distribution": distribution,
        "topic_analysis": topic_analysis,
        "difficulty_stats": difficulty_stats,
        "suspicious_students": suspicious_count,
        "pass_rate": round(sum(1 for s in scores if s >= 40) / len(scores) * 100, 1) if scores else 0,
    }

    print(f"   ✅ Analytics: {len(submissions)} students, avg={avg_score}%")
    return analytics
