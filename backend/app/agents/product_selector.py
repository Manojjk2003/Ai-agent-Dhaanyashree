from app.schemas.business import BusinessProfileResponse
from app.schemas.product import ProductResponse


def select_product(
    business: BusinessProfileResponse,
    products: list[ProductResponse],
) -> tuple[ProductResponse, str]:
    active_products = [product for product in products if product.is_active]
    candidates = active_products or products

    selected = max(
        candidates,
        key=lambda product: (
            len(product.benefits),
            bool(product.description),
            product.name.lower(),
        ),
    )

    reason_parts = [
        f"{selected.name} has the strongest product memory available right now",
    ]

    if selected.benefits:
        reason_parts.append(f"benefits: {', '.join(selected.benefits[:3])}")

    if business.target_audience:
        reason_parts.append(
            f"matched to audience: {', '.join(business.target_audience[:2])}"
        )

    return selected, "; ".join(reason_parts)
