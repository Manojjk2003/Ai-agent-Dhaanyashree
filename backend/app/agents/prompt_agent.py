from app.schemas.business import BusinessProfileResponse
from app.schemas.product import ProductResponse
from app.schemas.reference_image import ReferenceImageResponse


def generate_poster_prompt(
    business: BusinessProfileResponse,
    product: ProductResponse,
    content_type: str,
    content_idea: str,
    reference_images: list[ReferenceImageResponse] | None = None,
) -> str:
    benefits = ", ".join(product.benefits[:3]) if product.benefits else "key benefits"
    brand_style = ", ".join(business.brand_kit.visual_style[:4]) or "clean premium"
    colors = ", ".join(
        color
        for color in [
            business.brand_kit.primary_color,
            business.brand_kit.secondary_color,
            business.brand_kit.accent_color,
        ]
        if color
    )
    audience = (
        ", ".join(product.target_audience[:2])
        if product.target_audience
        else ", ".join(business.target_audience[:2])
    )
    audience_phrase = audience or "health-conscious customers"
    image_notes = f" Product image notes: {product.image_notes}." if product.image_notes else ""
    reference_images = reference_images or []
    reference_notes = _format_reference_notes(reference_images)
    color_notes = f" Use brand colors: {colors}." if colors else ""
    font_notes = (
        f" Typography direction: use {business.brand_kit.heading_font_family} style for headline "
        f"and {business.brand_kit.font_family} style for body text."
    )
    contact_note = (
        f" Include website or CTA reference: {business.website_url}."
        if business.website_url
        else ""
    )
    logo_note = (
        " Include the brand logo mark at the top of the poster."
        if business.brand_kit.logo_url
        else " Leave clear top space for the brand logo."
    )

    return (
        f"Commercial social media poster for {business.business_name}, featuring "
        f"{product.name}. Style: {brand_style} Indian small business advertising, "
        f"bright natural light, appetizing product presentation, readable space for "
        f"headline and CTA. Content theme: {content_type}. Idea: {content_idea}. "
        f"Highlight benefits: {benefits}. Target audience: {audience_phrase}."
        f"{logo_note}{color_notes}{font_notes}{contact_note}{image_notes}{reference_notes} "
        "Use the uploaded product and reference visuals as truth for product appearance; "
        "do not invent unrelated packaging, logos, ingredients, or brand marks."
    )


def _format_reference_notes(reference_images: list[ReferenceImageResponse]) -> str:
    if not reference_images:
        return ""

    references: list[str] = []
    for reference in reference_images[:6]:
        labels = ", ".join(reference.labels[:5])
        note_parts = [
            reference.name,
            reference.reference_type,
            labels,
            reference.notes,
        ]
        references.append(" / ".join(part for part in note_parts if part))

    return f" Reference visual memory: {'; '.join(references)}."
