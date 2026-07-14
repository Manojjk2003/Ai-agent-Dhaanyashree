from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.graphs.daily_marketing_graph import run_daily_marketing_graph
from app.schemas.auth import CurrentUser
from app.schemas.agent import DailyPlanRequest, DailyPlanResponse
from app.services.firebase_service import FirebaseService, get_firebase_service


router = APIRouter()


@router.post("/run-daily-plan", response_model=DailyPlanResponse)
def run_daily_plan(
    request: DailyPlanRequest,
    user: CurrentUser = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
) -> DailyPlanResponse:
    return run_daily_marketing_graph(request, user, firebase_service)
