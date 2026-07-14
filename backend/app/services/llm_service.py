from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.schemas.business import BusinessProfileResponse
from app.schemas.generated_post import GeneratedPostResponse
from app.schemas.product import ProductResponse
from app.schemas.scheduled_post import ScheduleRecommendationResponse


GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


@dataclass(frozen=True)
class MarketingContent:
    content_type: str
    content_idea: str
    caption: str
    hashtags: list[str]
    poster_prompt: str | None
    generation_source: str = "gemini"


@dataclass(frozen=True)
class ScheduleRecommendation:
    recommended_at: str
    reason: str
    confidence: float
    alternative_slots: list[str]
    generation_source: str = "gemini"


def generate_marketing_content(
    business: BusinessProfileResponse,
    product: ProductResponse,
    selection_reason: str,
    require_poster: bool,
) -> MarketingContent | None:
    if settings.llm_provider.lower() != "gemini" or not settings.gemini_api_key:
        return None

    prompt = _build_prompt(business, product, selection_reason, require_poster)
    payload = {
        "model": settings.gemini_model,
        "system_instruction": (
            "You are a practical small-business marketing assistant. "
            "Return only valid JSON. Do not wrap the JSON in markdown."
        ),
        "input": prompt,
        "generation_config": {
            "temperature": 0.7,
            "thinking_level": "low",
        },
    }

    try:
        raw_response = _post_gemini(payload)
        output_text = _extract_output_text(raw_response)
        parsed = json.loads(_strip_json_fence(output_text))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return None

    return _coerce_content(parsed, require_poster)


def recommend_schedule_time(
    business: BusinessProfileResponse,
    product: ProductResponse,
    generated_post: GeneratedPostResponse,
    target_date: date | None,
    platforms: list[str],
) -> ScheduleRecommendationResponse:
    recommended_date = target_date or (date.today() + timedelta(days=1))

    if settings.llm_provider.lower() != "gemini" or not settings.gemini_api_key:
        return _fallback_schedule_recommendation(
            business,
            product,
            generated_post,
            recommended_date,
            platforms,
        )

    prompt = _build_schedule_prompt(
        business,
        product,
        generated_post,
        recommended_date,
        platforms,
    )
    payload = {
        "model": settings.gemini_model,
        "system_instruction": (
            "You are a practical social media scheduling strategist for small "
            "businesses. Return only valid JSON. Do not wrap JSON in markdown."
        ),
        "input": prompt,
        "generation_config": {
            "temperature": 0.4,
            "thinking_level": "low",
        },
    }

    try:
        raw_response = _post_gemini(payload)
        output_text = _extract_output_text(raw_response)
        parsed = json.loads(_strip_json_fence(output_text))
        recommendation = _coerce_schedule_recommendation(parsed, recommended_date)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        recommendation = None

    if not recommendation:
        return _fallback_schedule_recommendation(
            business,
            product,
            generated_post,
            recommended_date,
            platforms,
        )

    return ScheduleRecommendationResponse(
        recommended_at=recommendation.recommended_at,
        reason=recommendation.reason,
        confidence=recommendation.confidence,
        alternative_slots=recommendation.alternative_slots,
        generation_source="gemini",
    )


def _post_gemini(payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        GEMINI_INTERACTIONS_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key or "",
        },
    )

    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _build_prompt(
    business: BusinessProfileResponse,
    product: ProductResponse,
    selection_reason: str,
    require_poster: bool,
) -> str:
    return json.dumps(
        {
            "task": (
                "Create one daily Instagram marketing post for this business "
                "using the selected product."
            ),
            "rules": [
                "Use clear, friendly language for a real small business owner.",
                "Avoid medical cure claims or exaggerated health claims.",
                "Make the caption specific to the product and audience.",
                "Return 5 to 8 hashtags.",
                "If poster_prompt is requested, make it useful for image generation.",
            ],
            "required_json_shape": {
                "content_type": "short label such as Educational post or Offer post",
                "content_idea": "one practical post idea",
                "caption": "ready-to-post caption",
                "hashtags": ["#Example"],
                "poster_prompt": "image-generation prompt or null",
            },
            "require_poster": require_poster,
            "selection_reason": selection_reason,
            "business": {
                "name": business.business_name,
                "industry": business.industry,
                "description": business.description,
                "target_audience": business.target_audience,
                "brand_tone": business.brand_tone,
                "goals": business.goals,
            },
            "product": {
                "name": product.name,
                "category": product.category,
                "description": product.description,
                "benefits": product.benefits,
                "ingredients": product.ingredients,
                "price": product.price,
                "target_audience": product.target_audience,
            },
        }
    )


def _build_schedule_prompt(
    business: BusinessProfileResponse,
    product: ProductResponse,
    generated_post: GeneratedPostResponse,
    target_date: date,
    platforms: list[str],
) -> str:
    return json.dumps(
        {
            "task": "Recommend the best posting time for this approved content.",
            "target_date": target_date.isoformat(),
            "platforms": platforms,
            "rules": [
                "Recommend one exact local datetime on the target_date.",
                "Use ISO-like format YYYY-MM-DDTHH:MM:SS without timezone.",
                "Give 2 alternative local datetime slots on the same date.",
                "Use practical heuristics because no historical analytics are available yet.",
                "Consider audience routine, product category, content type, and platform.",
            ],
            "required_json_shape": {
                "recommended_at": f"{target_date.isoformat()}T09:00:00",
                "reason": "short practical explanation",
                "confidence": 0.75,
                "alternative_slots": [
                    f"{target_date.isoformat()}T12:30:00",
                    f"{target_date.isoformat()}T18:30:00",
                ],
            },
            "business": {
                "name": business.business_name,
                "industry": business.industry,
                "description": business.description,
                "target_audience": business.target_audience,
                "brand_tone": business.brand_tone,
                "goals": business.goals,
            },
            "product": {
                "name": product.name,
                "category": product.category,
                "description": product.description,
                "benefits": product.benefits,
                "ingredients": product.ingredients,
                "price": product.price,
                "target_audience": product.target_audience,
            },
            "content": {
                "content_type": generated_post.content_type,
                "content_idea": generated_post.content_idea,
                "caption": generated_post.caption,
                "hashtags": generated_post.hashtags,
            },
        }
    )


def _extract_output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]

    texts: list[str] = []
    for step in response.get("steps", []):
        model_output = step.get("model_output") or step.get("modelOutput") or step
        for content in model_output.get("content", []):
            text = content.get("text")
            if isinstance(text, dict) and isinstance(text.get("text"), str):
                texts.append(text["text"])
            elif isinstance(text, str):
                texts.append(text)

    if texts:
        return "\n".join(texts)

    raise ValueError("Gemini response did not include output text")


def _strip_json_fence(value: str) -> str:
    stripped = value.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
    return match.group(1).strip() if match else stripped


def _coerce_content(parsed: dict, require_poster: bool) -> MarketingContent | None:
    content_type = _clean_text(parsed.get("content_type"))
    content_idea = _clean_text(parsed.get("content_idea"))
    caption = _clean_text(parsed.get("caption"))
    hashtags = _clean_hashtags(parsed.get("hashtags"))
    poster_prompt = _clean_text(parsed.get("poster_prompt")) if require_poster else None

    if not content_type or not content_idea or not caption or not hashtags:
        return None

    return MarketingContent(
        content_type=content_type,
        content_idea=content_idea,
        caption=caption,
        hashtags=hashtags,
        poster_prompt=poster_prompt,
    )


def _coerce_schedule_recommendation(
    parsed: dict,
    target_date: date,
) -> ScheduleRecommendation | None:
    recommended_at = _coerce_datetime_on_date(parsed.get("recommended_at"), target_date)
    reason = _clean_text(parsed.get("reason"))
    confidence = _coerce_confidence(parsed.get("confidence"))
    alternative_slots = [
        slot
        for slot in (
            _coerce_datetime_on_date(value, target_date)
            for value in _coerce_list(parsed.get("alternative_slots"))
        )
        if slot and slot != recommended_at
    ][:3]

    if not recommended_at or not reason:
        return None

    return ScheduleRecommendation(
        recommended_at=recommended_at,
        reason=reason,
        confidence=confidence,
        alternative_slots=alternative_slots,
    )


def _fallback_schedule_recommendation(
    business: BusinessProfileResponse,
    product: ProductResponse,
    generated_post: GeneratedPostResponse,
    target_date: date,
    platforms: list[str],
) -> ScheduleRecommendationResponse:
    content_text = (
        f"{business.industry} {product.category} {generated_post.content_type} "
        f"{' '.join(product.target_audience or business.target_audience)}"
    ).lower()

    if any(word in content_text for word in ["breakfast", "food", "health", "family"]):
        primary_time = time(8, 30)
        alternatives = [time(12, 30), time(18, 30)]
        reason = (
            "Morning is a strong fit for food and health content because people "
            "are planning meals and routines."
        )
    elif any(word in content_text for word in ["offer", "sale", "discount", "promotion"]):
        primary_time = time(19, 0)
        alternatives = [time(12, 45), time(20, 30)]
        reason = (
            "Evening is a practical slot for promotional content because customers "
            "are more likely to browse and decide after work."
        )
    elif any(word in content_text for word in ["educational", "tip", "how"]):
        primary_time = time(11, 0)
        alternatives = [time(8, 30), time(17, 30)]
        reason = (
            "Late morning works well for educational content because it is easier "
            "to read and save during lighter browsing windows."
        )
    else:
        primary_time = time(18, 30)
        alternatives = [time(10, 0), time(13, 0)]
        reason = (
            "Early evening is a balanced default while there is no historical "
            "analytics data available."
        )

    if "instagram" in [platform.lower() for platform in platforms]:
        reason = f"{reason} Instagram also tends to work well around routine breaks."

    return ScheduleRecommendationResponse(
        recommended_at=_combine_date_time(target_date, primary_time),
        reason=reason,
        confidence=0.62,
        alternative_slots=[
            _combine_date_time(target_date, alternative_time)
            for alternative_time in alternatives
        ],
        generation_source="fallback",
    )


def _combine_date_time(target_date: date, target_time: time) -> str:
    return datetime.combine(target_date, target_time).isoformat()


def _coerce_datetime_on_date(value: object, target_date: date) -> str:
    raw_value = _clean_text(value)
    if not raw_value:
        return ""

    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        match = re.search(r"(\d{1,2}):(\d{2})", raw_value)
        if not match:
            return ""
        parsed = datetime.combine(
            target_date,
            time(int(match.group(1)), int(match.group(2))),
        )

    return datetime.combine(target_date, parsed.time().replace(microsecond=0)).isoformat()


def _coerce_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = 0.65

    return max(0, min(confidence, 1))


def _coerce_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _clean_text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _clean_hashtags(value: object) -> list[str]:
    if isinstance(value, str):
        raw_tags = re.split(r"[\s,]+", value)
    elif isinstance(value, list):
        raw_tags = [str(item) for item in value]
    else:
        raw_tags = []

    hashtags: list[str] = []
    for tag in raw_tags:
        cleaned = tag.strip()
        if not cleaned:
            continue
        if not cleaned.startswith("#"):
            cleaned = f"#{cleaned}"
        hashtags.append(cleaned)

    return hashtags[:8]
