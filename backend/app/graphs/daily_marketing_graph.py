from uuid import uuid4

from fastapi import HTTPException, status

from app.agents.caption_agent import generate_caption
from app.agents.content_strategy import choose_content_strategy
from app.agents.product_selector import select_product
from app.agents.prompt_agent import generate_poster_prompt
from app.schemas.agent import DailyPlanRequest, DailyPlanResponse
from app.schemas.auth import CurrentUser
from app.services.firebase_service import FirebaseService


def run_daily_marketing_graph(
    request: DailyPlanRequest,
    user: CurrentUser,
    firebase_service: FirebaseService,
) -> DailyPlanResponse:
    """First working daily marketing workflow.

    This is deterministic for now. It uses the same graph boundary where
    LangGraph nodes will later orchestrate LLM-backed agents.
    """
    business = firebase_service.get_business_profile(user)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create the business profile before generating a daily plan",
        )

    products = firebase_service.list_products(user)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add at least one product before generating a daily plan",
        )

    selected_product, selection_reason = select_product(business, products)
    content_type, content_idea = choose_content_strategy(business, selected_product)
    caption, hashtags = generate_caption(business, selected_product, content_idea)
    poster_prompt = (
        generate_poster_prompt(
            business,
            selected_product,
            content_type,
            content_idea,
        )
        if request.require_poster
        else None
    )

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
            f"Generated a {content_type.lower()} for {selected_product.name} "
            f"using {business.business_name}'s business profile and product memory."
        ),
        business_name=business.business_name,
        selected_product_id=selected_product.product_id,
        selected_product_name=selected_product.name,
        selection_reason=selection_reason,
        content_type=content_type,
        content_idea=content_idea,
        caption=caption,
        hashtags=hashtags,
        poster_prompt=poster_prompt,
    )
