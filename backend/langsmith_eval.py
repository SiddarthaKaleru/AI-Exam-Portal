"""LangSmith Evaluation Script for AI Exam Portal.

Creates datasets, runs evaluations, and pushes results to LangSmith.
Results are visible at https://smith.langchain.com under your project.

Usage:
    cd backend
    python langsmith_eval.py
"""

import os
import sys
import json
import asyncio

# Fix Windows console encoding (cp1252 can't handle some Unicode)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(__file__))

# Load config (sets LANGCHAIN_* env vars)
import config

from langsmith import Client
from langsmith.evaluation import evaluate

from services.llm_service import generate_text, generate_json
from agents.evaluation_agent import evaluation_agent


# ═══════════════════════════════════════════════════════════════════════
# 1. LangSmith Client
# ═══════════════════════════════════════════════════════════════════════

ls_client = Client()

DATASET_NAME = "exam-portal-evaluation"


# ═══════════════════════════════════════════════════════════════════════
# 2. Dataset Creation — Test Cases
# ═══════════════════════════════════════════════════════════════════════

def create_or_get_dataset():
    """Create the evaluation dataset if it doesn't exist."""
    # Check if dataset already exists
    try:
        datasets = list(ls_client.list_datasets(dataset_name=DATASET_NAME))
        if datasets:
            print(f"[OK] Dataset '{DATASET_NAME}' already exists. Deleting and re-creating...")
            ls_client.delete_dataset(dataset_id=datasets[0].id)
    except Exception:
        pass

    dataset = ls_client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Evaluation dataset for AI Exam Portal — tests question generation, "
                    "answer evaluation, and content extraction.",
    )

    # ── Test Case 1: MCQ Question Generation ──────────────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "question_generation",
            "subject": "Computer Science",
            "topic": "Data Structures",
            "content": (
                "A binary tree is a tree data structure in which each node has at most "
                "two children, referred to as the left child and the right child. "
                "A binary search tree (BST) is a binary tree where the left subtree "
                "contains only nodes with keys less than the parent node, and the right "
                "subtree only nodes with keys greater than the parent node. "
                "Tree traversal methods include in-order, pre-order, and post-order. "
                "In-order traversal visits left subtree, root, then right subtree."
            ),
            "num_questions": 3,
            "question_type": "mcq",
        },
        outputs={
            "expected_count": 3,
            "expected_type": "mcq",
            "expected_fields": ["question", "options", "correct_answer", "difficulty"],
            "topic_relevance": "Data Structures",
        },
    )

    # ── Test Case 2: Short Answer Question Generation ─────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "question_generation",
            "subject": "Computer Science",
            "topic": "Algorithms",
            "content": (
                "Sorting algorithms arrange elements in a specific order. "
                "Bubble sort repeatedly steps through the list, compares adjacent "
                "elements and swaps them if they are in the wrong order. "
                "Its time complexity is O(n²). Quick sort uses a divide-and-conquer "
                "strategy with average time complexity O(n log n). "
                "Merge sort also uses divide-and-conquer with guaranteed O(n log n) "
                "time complexity but requires O(n) extra space."
            ),
            "num_questions": 2,
            "question_type": "short",
        },
        outputs={
            "expected_count": 2,
            "expected_type": "short",
            "expected_fields": ["question", "model_answer", "keywords", "difficulty"],
            "topic_relevance": "Algorithms",
        },
    )

    # ── Test Case 3: MCQ Evaluation — Correct Answer ──────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "evaluation",
            "questions": [
                {
                    "id": 1,
                    "type": "mcq",
                    "question": "What is the time complexity of binary search?",
                    "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                    "correct_answer": "O(log n)",
                    "marks": 1,
                }
            ],
            "answers": [{"question_id": 1, "answer": "O(log n)"}],
        },
        outputs={
            "expected_score": 1,
            "expected_max_score": 1,
            "expected_percentage": 100.0,
        },
    )

    # ── Test Case 4: MCQ Evaluation — Wrong Answer ────────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "evaluation",
            "questions": [
                {
                    "id": 1,
                    "type": "mcq",
                    "question": "What is the time complexity of binary search?",
                    "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                    "correct_answer": "O(log n)",
                    "marks": 1,
                }
            ],
            "answers": [{"question_id": 1, "answer": "O(n)"}],
        },
        outputs={
            "expected_score": 0,
            "expected_max_score": 1,
            "expected_percentage": 0.0,
        },
    )

    # ── Test Case 5: Subjective Evaluation — Good Answer ──────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "evaluation",
            "questions": [
                {
                    "id": 1,
                    "type": "short",
                    "question": "Explain the difference between a stack and a queue.",
                    "model_answer": (
                        "A stack follows LIFO (Last In, First Out) order where the "
                        "last element added is the first to be removed. A queue follows "
                        "FIFO (First In, First Out) order where the first element added "
                        "is the first to be removed."
                    ),
                    "keywords": ["LIFO", "FIFO", "stack", "queue", "order"],
                    "marks": 3,
                }
            ],
            "answers": [
                {
                    "question_id": 1,
                    "answer": (
                        "A stack uses LIFO principle where the last element pushed is "
                        "the first one popped. A queue uses FIFO principle where the "
                        "first element enqueued is the first one dequeued."
                    ),
                }
            ],
        },
        outputs={
            "expected_min_score": 2,
            "expected_max_score": 3,
        },
    )

    # ── Test Case 6: Subjective Evaluation — Empty Answer ─────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "evaluation",
            "questions": [
                {
                    "id": 1,
                    "type": "short",
                    "question": "What is polymorphism in OOP?",
                    "model_answer": "Polymorphism allows objects to take many forms.",
                    "keywords": ["polymorphism", "objects", "forms"],
                    "marks": 3,
                }
            ],
            "answers": [{"question_id": 1, "answer": ""}],
        },
        outputs={
            "expected_score": 0,
            "expected_max_score": 3,
            "expected_percentage": 0.0,
        },
    )

    # ── Test Case 7: Topic Extraction ─────────────────────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "topic_extraction",
            "subject": "Computer Science",
            "content": (
                "Operating systems manage hardware and software resources. "
                "Process scheduling determines which process runs when. "
                "Memory management handles allocation and deallocation of memory. "
                "File systems organize data on storage devices. "
                "Deadlocks occur when processes wait for each other indefinitely."
            ),
        },
        outputs={
            "expected_min_topics": 3,
            "expected_max_topics": 8,
            "relevant_keywords": [
                "process", "scheduling", "memory", "file system", "deadlock",
                "operating system",
            ],
        },
    )

    # ── Test Case 8: Mixed Exam Evaluation ────────────────────────────
    ls_client.create_example(
        dataset_id=dataset.id,
        inputs={
            "task": "evaluation",
            "questions": [
                {
                    "id": 1,
                    "type": "mcq",
                    "question": "Which data structure uses FIFO?",
                    "options": ["Stack", "Queue", "Tree", "Graph"],
                    "correct_answer": "Queue",
                    "marks": 1,
                },
                {
                    "id": 2,
                    "type": "mcq",
                    "question": "What does CPU stand for?",
                    "options": [
                        "Central Processing Unit",
                        "Central Program Utility",
                        "Computer Personal Unit",
                        "Central Processor Unified",
                    ],
                    "correct_answer": "Central Processing Unit",
                    "marks": 1,
                },
                {
                    "id": 3,
                    "type": "short",
                    "question": "Define an array.",
                    "model_answer": (
                        "An array is a collection of elements stored at contiguous "
                        "memory locations, accessed by index."
                    ),
                    "keywords": ["collection", "contiguous", "memory", "index"],
                    "marks": 3,
                },
            ],
            "answers": [
                {"question_id": 1, "answer": "Queue"},
                {"question_id": 2, "answer": "Central Processing Unit"},
                {
                    "question_id": 3,
                    "answer": "An array stores elements in contiguous memory locations "
                              "and each element can be accessed using its index.",
                },
            ],
        },
        outputs={
            "expected_min_score": 4,
            "expected_max_score": 5,
        },
    )

    print(f"[OK] Created dataset '{DATASET_NAME}' with 8 test cases")
    return dataset


# ═══════════════════════════════════════════════════════════════════════
# 3. Target Function — what LangSmith evaluates
# ═══════════════════════════════════════════════════════════════════════

def target_function(inputs: dict) -> dict:
    """Run the appropriate agent based on the task type.
    
    This function is called by LangSmith's evaluate() for each dataset example.
    """
    task = inputs.get("task", "")

    if task == "question_generation":
        return _run_question_generation(inputs)
    elif task == "evaluation":
        return _run_evaluation(inputs)
    elif task == "topic_extraction":
        return _run_topic_extraction(inputs)
    else:
        return {"error": f"Unknown task: {task}"}


def _run_question_generation(inputs: dict) -> dict:
    """Generate questions using the LLM and return structured result."""
    q_type = inputs.get("question_type", "mcq")
    num_q = inputs.get("num_questions", 3)
    subject = inputs.get("subject", "General")
    content = inputs.get("content", "")

    if q_type == "mcq":
        prompt = f"""You are an expert exam question generator for the subject: {subject}.

Based on this content:
{content}

Generate exactly {num_q} Multiple Choice Questions (MCQs).
Mix difficulty levels: Easy, Medium, Hard.

Return JSON array with this EXACT structure:
[
  {{
    "type": "mcq",
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "difficulty": "easy",
    "topic": "Relevant Topic",
    "marks": 1,
    "explanation": "Brief explanation of correct answer"
  }}
]"""
    else:
        prompt = f"""You are an expert exam question generator for the subject: {subject}.

Based on this content:
{content}

Generate exactly {num_q} Short Answer Questions.
Mix difficulty levels. Each answer should be 2-4 sentences.

Return JSON array with this EXACT structure:
[
  {{
    "type": "short",
    "question": "Question text here?",
    "model_answer": "The expected answer in 2-4 sentences.",
    "difficulty": "medium",
    "topic": "Relevant Topic",
    "marks": 3,
    "keywords": ["key1", "key2", "key3"]
  }}
]"""

    result = generate_json(prompt)

    # Normalize dict to list
    if isinstance(result, dict):
        result = result.get("questions", result.get("mcqs", result.get("short_answers", [])))

    return {
        "questions": result,
        "count": len(result) if isinstance(result, list) else 0,
        "type": q_type,
    }


def _run_evaluation(inputs: dict) -> dict:
    """Run the evaluation agent on provided questions and answers."""
    questions = inputs.get("questions", [])
    answers = inputs.get("answers", [])

    # evaluation_agent is async, run it synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(evaluation_agent(questions, answers))
    finally:
        loop.close()

    return result


def _run_topic_extraction(inputs: dict) -> dict:
    """Extract topics from content using the LLM."""
    subject = inputs.get("subject", "General")
    content = inputs.get("content", "")

    prompt = f"""Analyze the following academic content and extract the main topics/concepts covered.
Subject: {subject}
Content:
{content}
Return a JSON array of topic strings. Example: ["Topic 1", "Topic 2", "Topic 3"]
Extract between 3-8 key topics from the content."""

    topics = generate_json(prompt)

    if isinstance(topics, dict):
        values = list(topics.values())
        topics = topics.get("topics", values[0] if values else [])

    if not isinstance(topics, list):
        topics = [str(topics)] if topics else []

    return {"topics": topics, "count": len(topics)}


# ═══════════════════════════════════════════════════════════════════════
# 4. Custom Evaluators
# ═══════════════════════════════════════════════════════════════════════

def question_quality_evaluator(run, example) -> dict:
    """Evaluate the quality of generated questions."""
    outputs = run.outputs or {}
    expected = example.outputs or {}
    task = example.inputs.get("task", "")

    if task != "question_generation":
        return {"key": "question_quality", "score": None, "comment": "N/A — not a question gen task"}

    questions = outputs.get("questions", [])
    expected_count = expected.get("expected_count", 0)
    expected_type = expected.get("expected_type", "")
    expected_fields = expected.get("expected_fields", [])

    score = 1.0
    comments = []

    # Check count
    actual_count = len(questions) if isinstance(questions, list) else 0
    if actual_count != expected_count:
        score -= 0.3
        comments.append(f"Expected {expected_count} questions, got {actual_count}")

    # Check structure
    if isinstance(questions, list) and questions:
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                score -= 0.2
                comments.append(f"Question {i+1} is not a dict")
                continue

            # Check type matches
            if q.get("type") != expected_type:
                score -= 0.1
                comments.append(f"Question {i+1} type mismatch: expected '{expected_type}', got '{q.get('type')}'")

            # Check required fields
            missing = [f for f in expected_fields if f not in q]
            if missing:
                score -= 0.1
                comments.append(f"Question {i+1} missing fields: {missing}")

            # For MCQs, check options count
            if expected_type == "mcq":
                opts = q.get("options", [])
                if len(opts) != 4:
                    score -= 0.1
                    comments.append(f"Question {i+1}: expected 4 options, got {len(opts)}")
                # Check correct_answer is in options
                if q.get("correct_answer") not in opts:
                    score -= 0.1
                    comments.append(f"Question {i+1}: correct_answer not in options")
    else:
        score = 0.0
        comments.append("No valid questions generated")

    score = max(0.0, score)
    comment = "; ".join(comments) if comments else "All checks passed ✅"

    return {"key": "question_quality", "score": score, "comment": comment}


def evaluation_accuracy_evaluator(run, example) -> dict:
    """Evaluate the accuracy of the evaluation agent."""
    outputs = run.outputs or {}
    expected = example.outputs or {}
    task = example.inputs.get("task", "")

    if task != "evaluation":
        return {"key": "evaluation_accuracy", "score": None, "comment": "N/A — not an evaluation task"}

    score = 1.0
    comments = []

    # Check exact score match for MCQ-only evaluations
    if "expected_score" in expected:
        actual_score = outputs.get("score", -1)
        expected_score = expected["expected_score"]
        if actual_score != expected_score:
            score -= 0.5
            comments.append(f"Score mismatch: expected {expected_score}, got {actual_score}")

    if "expected_percentage" in expected:
        actual_pct = outputs.get("percentage", -1)
        expected_pct = expected["expected_percentage"]
        if abs(actual_pct - expected_pct) > 5:  # 5% tolerance
            score -= 0.3
            comments.append(f"Percentage mismatch: expected {expected_pct}%, got {actual_pct}%")

    # Check score range for subjective answers
    if "expected_min_score" in expected:
        actual_score = outputs.get("score", -1)
        min_score = expected["expected_min_score"]
        max_score = expected["expected_max_score"]
        if not (min_score <= actual_score <= max_score):
            score -= 0.5
            comments.append(
                f"Score {actual_score} outside expected range [{min_score}, {max_score}]"
            )

    if "expected_max_score" in expected:
        actual_max = outputs.get("max_score", -1)
        if actual_max != expected["expected_max_score"]:
            score -= 0.2
            comments.append(
                f"Max score mismatch: expected {expected['expected_max_score']}, got {actual_max}"
            )

    score = max(0.0, score)
    comment = "; ".join(comments) if comments else "All checks passed ✅"

    return {"key": "evaluation_accuracy", "score": score, "comment": comment}


def topic_extraction_evaluator(run, example) -> dict:
    """Evaluate the quality of topic extraction."""
    outputs = run.outputs or {}
    expected = example.outputs or {}
    task = example.inputs.get("task", "")

    if task != "topic_extraction":
        return {"key": "topic_extraction", "score": None, "comment": "N/A — not a topic extraction task"}

    topics = outputs.get("topics", [])
    count = len(topics) if isinstance(topics, list) else 0
    min_topics = expected.get("expected_min_topics", 3)
    max_topics = expected.get("expected_max_topics", 8)
    relevant_keywords = expected.get("relevant_keywords", [])

    score = 1.0
    comments = []

    # Check topic count is in range
    if not (min_topics <= count <= max_topics):
        score -= 0.3
        comments.append(f"Topic count {count} outside [{min_topics}, {max_topics}]")

    # Check keyword coverage — at least some relevant keywords should appear
    if relevant_keywords and isinstance(topics, list):
        topic_text = " ".join(topics).lower()
        matches = sum(1 for kw in relevant_keywords if kw.lower() in topic_text)
        coverage = matches / len(relevant_keywords)
        if coverage < 0.3:
            score -= 0.4
            comments.append(
                f"Low keyword coverage: {matches}/{len(relevant_keywords)} "
                f"({coverage:.0%})"
            )
        elif coverage < 0.5:
            score -= 0.2
            comments.append(
                f"Moderate keyword coverage: {matches}/{len(relevant_keywords)} "
                f"({coverage:.0%})"
            )

    # Check topics are non-empty strings
    if isinstance(topics, list):
        empty = sum(1 for t in topics if not t or not str(t).strip())
        if empty:
            score -= 0.2
            comments.append(f"{empty} empty topic(s)")

    score = max(0.0, score)
    comment = "; ".join(comments) if comments else "All checks passed [PASS]"

    return {"key": "topic_extraction", "score": score, "comment": comment}


# ═══════════════════════════════════════════════════════════════════════
# 5. Main — Run Evaluation
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("[EVAL] AI Exam Portal - LangSmith Evaluation")
    print("=" * 60)
    print(f"Project: {os.environ.get('LANGCHAIN_PROJECT', 'default')}")
    print(f"Tracing: {os.environ.get('LANGCHAIN_TRACING_V2', 'false')}")
    print()

    # Step 1: Create dataset
    print("Step 1: Creating evaluation dataset...")
    create_or_get_dataset()
    print()

    # Step 2: Run evaluation
    print("Step 2: Running evaluations...")
    print("   This will make LLM calls - each one traced to LangSmith.")
    print()

    results = evaluate(
        target_function,
        data=DATASET_NAME,
        evaluators=[
            question_quality_evaluator,
            evaluation_accuracy_evaluator,
            topic_extraction_evaluator,
        ],
        experiment_prefix="exam-portal-eval",
        max_concurrency=1,  # Sequential to avoid rate limits
    )

    # Step 3: Print summary
    print()
    print("=" * 60)
    print("Evaluation Complete!")
    print("=" * 60)
    print()
    print("View results on LangSmith:")
    print("   1. Go to https://smith.langchain.com")
    print(f"   2. Select project: '{os.environ.get('LANGCHAIN_PROJECT', 'ai-exam-portal')}'")
    print("   3. Check 'Traces' tab for all LLM call details")
    print("   4. Check 'Datasets & Testing' for evaluation results")
    print()


if __name__ == "__main__":
    main()
