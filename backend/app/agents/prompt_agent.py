from app.schemas.business import BusinessProfileResponse
from app.schemas.product import ProductResponse


def generate_poster_prompt(
    business: BusinessProfileResponse,
    product: ProductResponse,
    content_type: str,
    content_idea: str,
) -> str:
    benefits = ", ".join(product.benefits[:3]) if product.benefits else "key benefits"
    audience = (
        ", ".join(product.target_audience[:2])
        if product.target_audience
        else ", ".join(business.target_audience[:2])
    )
    audience_phrase = audience or "health-conscious customers"

    return (
        f"Commercial social media poster for {business.business_name}, featuring "
        f"{product.name}. Style: clean premium Indian small business advertising, "
        f"bright natural light, appetizing product presentation, readable space for "
        f"headline and CTA. Content theme: {content_type}. Idea: {content_idea}. "
        f"Highlight benefits: {benefits}. Target audience: {audience_phrase}."
    )
