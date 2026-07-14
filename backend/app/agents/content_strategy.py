from app.schemas.business import BusinessProfileResponse
from app.schemas.product import ProductResponse


def choose_content_strategy(
    business: BusinessProfileResponse,
    product: ProductResponse,
) -> tuple[str, str]:
    if product.benefits:
        primary_benefit = product.benefits[0]
        return (
            "Educational post",
            f"Show how {product.name} helps with {primary_benefit.lower()} in everyday life.",
        )

    if product.category:
        return (
            "Product spotlight",
            f"Introduce {product.name} as a useful {product.category.lower()} option from {business.business_name}.",
        )

    return (
        "Product promotion",
        f"Introduce {product.name} and explain why it belongs in the customer's routine.",
    )
