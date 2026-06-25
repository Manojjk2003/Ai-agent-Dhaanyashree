from uuid import uuid4

from app.schemas.agent import DailyPlanRequest, DailyPlanResponse


def run_daily_marketing_graph(request: DailyPlanRequest) -> DailyPlanResponse:
    """Placeholder for the LangGraph daily marketing workflow.

    The real workflow will call business memory, trend, product selection,
    content strategy, caption, prompt, and poster agents in sequence.
    """
    run_id = f"run_{uuid4().hex[:12]}"
    content_plan_id = f"plan_{uuid4().hex[:12]}"
    post_id = f"post_{uuid4().hex[:12]}"
    poster_id = f"poster_{uuid4().hex[:12]}" if request.require_poster else None

    return DailyPlanResponse(
        run_id=run_id,
        content_plan_id=content_plan_id,
        post_id=post_id,
        poster_id=poster_id,
        status="ready_for_review",
        summary=(
            "Daily marketing graph scaffold completed. Agent implementation "
            "will be added after business memory and product data exist."
        ),
    )
