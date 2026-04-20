"""LangGraph Orchestrator — wires all agents into a StateGraph pipeline.

Pipeline: Content Agent → Question Agent → Website Agent → Exam Manager Agent
(Evaluation and Analytics agents are triggered separately on submission)
"""

import asyncio
from langgraph.graph import StateGraph, END
from agents.state import ExamPipelineState
from agents.content_agent import content_agent
from agents.question_agent import question_agent
from agents.website_agent import website_agent
from agents.exam_manager_agent import exam_manager_agent


def _run_content(state: ExamPipelineState) -> ExamPipelineState:
    """Synchronous wrapper for Agent 1."""
    try:
        return content_agent(state)
    except Exception as e:
        return {**state, "error": f"Content Agent failed: {str(e)}", "status": "error"}


def _run_questions(state: ExamPipelineState) -> ExamPipelineState:
    """Synchronous wrapper for Agent 2."""
    try:
        return question_agent(state)
    except Exception as e:
        return {**state, "error": f"Question Agent failed: {str(e)}", "status": "error"}


def _run_website(state: ExamPipelineState) -> ExamPipelineState:
    """Synchronous wrapper for Agent 3."""
    try:
        return website_agent(state)
    except Exception as e:
        return {**state, "error": f"Website Agent failed: {str(e)}", "status": "error"}


def _run_exam_manager(state: ExamPipelineState) -> ExamPipelineState:
    """Run Agent 4 (needs DB access). Since LangGraph runs this in a thread, we must create a local loop."""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(exam_manager_agent(state))
        loop.close()
        return result
    except Exception as e:
        return {**state, "error": f"Exam Manager Agent failed: {str(e)}", "status": "error"}


def _should_continue(state: ExamPipelineState) -> str:
    """Check if pipeline should continue or stop on error."""
    if state.get("error"):
        return "error"
    return "continue"


def build_exam_pipeline():
    """Build the LangGraph exam generation pipeline."""

    # Create the state graph
    workflow = StateGraph(ExamPipelineState)

    # Add agent nodes
    workflow.add_node("content_agent", _run_content)
    workflow.add_node("question_agent", _run_questions)
    workflow.add_node("website_agent", _run_website)
    workflow.add_node("exam_manager_agent", _run_exam_manager)

    # Set entry point
    workflow.set_entry_point("content_agent")

    # Add conditional edges (stop on error)
    workflow.add_conditional_edges(
        "content_agent",
        _should_continue,
        {"continue": "question_agent", "error": END},
    )
    workflow.add_conditional_edges(
        "question_agent",
        _should_continue,
        {"continue": "website_agent", "error": END},
    )
    workflow.add_conditional_edges(
        "website_agent",
        _should_continue,
        {"continue": "exam_manager_agent", "error": END},
    )
    workflow.add_edge("exam_manager_agent", END)

    # Compile
    return workflow.compile()


# Pre-built pipeline instance
exam_pipeline = build_exam_pipeline()


async def run_exam_pipeline(input_state: dict) -> dict:
    """Run the full exam generation pipeline.

    Args:
        input_state: dict with subject, topic, syllabus, pdf_paths,
                     duration_minutes, num_mcq, num_short, num_long, created_by.

    Returns:
        Final pipeline state with exam_code, exam_id, questions, etc.
    """
    print("\n🚀 Starting Exam Generation Pipeline...")
    print("=" * 50)

    # Run the pipeline
    result = await exam_pipeline.ainvoke(input_state)

    if result.get("error"):
        print(f"\n❌ Pipeline failed: {result['error']}")
    else:
        print(f"\n🎉 Pipeline complete! Exam code: {result.get('exam_code')}")

    print("=" * 50)
    return result
