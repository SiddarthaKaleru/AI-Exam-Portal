"""Analytics routes — admin dashboard data."""

from fastapi import APIRouter, Depends, HTTPException
from utils.auth import require_admin
from agents.analytics_agent import analytics_agent

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/{exam_id}")
async def get_analytics(exam_id: str, admin: dict = Depends(require_admin)):
    """Get analytics dashboard data for an exam."""
    try:
        result = await analytics_agent(exam_id)
        if result.get("error"):
            raise HTTPException(status_code=404, detail=result["error"])
        return {"analytics": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
