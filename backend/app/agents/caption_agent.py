from app.schemas.business import BusinessProfileResponse
from app.schemas.product import ProductResponse


def _hashtag(value: str) -> str:
    cleaned = "".join(ch for ch in value.title() if ch.isalnum())
    return f"#{cleaned}" if cleaned else ""


def generate_caption(
    business: BusinessProfileResponse,
    product: ProductResponse,
    content_idea: str,
) -> tuple[str, list[str]]:
    benefits = product.benefits[:2]
    benefit_line = ""
    if benefits:
        benefit_line = f"Known for {', '.join(benefits).lower()}, "

    audience_line = ""
    if product.target_audience:
        audience_line = f"Made for {', '.join(product.target_audience[:2]).lower()}. "
    elif business.target_audience:
        audience_line = f"Made for {', '.join(business.target_audience[:2]).lower()}. "

    caption = (
        f"Make today's routine healthier with {product.name}. "
        f"{benefit_line}{audience_line}"
        f"{content_idea} "
        f"Message {business.business_name} to order or learn more."
    )

    hashtags = [
        _hashtag(product.name),
        _hashtag(product.category),
        _hashtag(business.industry),
        "#HealthyChoices",
        "#SmallBusiness",
    ]
    return caption, [tag for tag in hashtags if tag]
