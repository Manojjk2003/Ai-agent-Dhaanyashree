from fastapi import APIRouter

from app.graphs.daily_marketing_graph import run_daily_marketing_graph
from app.schemas.agent import DailyPlanRequest, DailyPlanResponse


router = APIRouter()


@router.post("/run-daily-plan", response_model=DailyPlanResponse)
def run_daily_plan(request: DailyPlanRequest) -> DailyPlanResponse:
    return run_daily_marketing_graph(request)
