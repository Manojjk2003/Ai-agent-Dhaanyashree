from __future__ import annotations

import base64
import io
import html
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from app.config import BACKEND_DIR, settings
from app.schemas.business import BusinessProfileResponse
from app.schemas.generated_post import GeneratedPostResponse
from app.schemas.generated_poster import PosterTemplate
from app.schemas.product import ProductResponse
from app.schemas.reference_image import ReferenceImageResponse
from app.services.storage_service import upload_bytes_to_storage


GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
POSTER_DIR = BACKEND_DIR.parent / "generated" / "posters"


@dataclass(frozen=True)
class PosterImage:
    image_url: str
    storage_path: str
    mime_type: str
    provider: str
    error_message: str | None = None


@dataclass(frozen=True)
class VisualAssetContext:
    business: BusinessProfileResponse | None = None
    product: ProductResponse | None = None
    reference_images: tuple[ReferenceImageResponse, ...] = ()

    @property
    def logo_url(self) -> str:
        if not self.business:
            return ""
        return self.business.brand_kit.logo_url

    @property
    def product_image_url(self) -> str:
        if not self.product:
            return ""
        for image_url in self.product.image_urls:
            if image_url:
                return image_url
        return self.product.image_url


def generate_poster_image(
    generated_post: GeneratedPostResponse,
    business_id: str,
    logo_url: str | None = None,
    visual_context: VisualAssetContext | None = None,
    template: PosterTemplate = "auto",
) -> PosterImage:
    if visual_context is None and logo_url:
        visual_context = VisualAssetContext()

    if visual_context and visual_context.business:
        try:
            return _generate_layout_poster(
                generated_post,
                business_id,
                visual_context,
                template,
            )
        except Exception as exc:
            fallback_reason = f"Layout renderer failed: {_safe_error_message(exc)}"
            return _generate_fallback_poster(generated_post, business_id, fallback_reason)

    prompt = _build_poster_prompt(generated_post, visual_context)
    image_provider = settings.image_provider.lower()
    fallback_reason = None
    effective_logo_url = visual_context.logo_url if visual_context and visual_context.logo_url else logo_url

    if image_provider == "huggingface" and settings.hf_token:
        try:
            return _generate_huggingface_poster(
                prompt,
                business_id,
                generated_post.post_id,
                effective_logo_url,
                visual_context,
            )
        except Exception as exc:
            fallback_reason = _safe_error_message(exc)

    if image_provider == "gemini" and settings.gemini_api_key:
        try:
            return _generate_gemini_poster(
                prompt,
                business_id,
                generated_post.post_id,
                effective_logo_url,
                visual_context,
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            fallback_reason = _safe_error_message(exc)

    if image_provider == "huggingface" and not settings.hf_token:
        fallback_reason = "HF_TOKEN is not configured on the backend"
    elif image_provider == "gemini" and not settings.gemini_api_key:
        fallback_reason = "GEMINI_API_KEY is not configured on the backend"
    elif image_provider not in {"fallback", "gemini", "huggingface"}:
        fallback_reason = f"Unsupported IMAGE_PROVIDER value: {settings.image_provider}"

    return _generate_fallback_poster(generated_post, business_id, fallback_reason)


def _generate_huggingface_poster(
    prompt: str,
    business_id: str,
    post_id: str,
    logo_url: str | None,
    visual_context: VisualAssetContext | None,
) -> PosterImage:
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise ImportError(
            "huggingface_hub is not installed. Run pip install -r requirements.txt.",
        ) from exc

    client = InferenceClient(api_key=settings.hf_token)
    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
        width=1024,
        height=1024,
        num_inference_steps=4,
        guidance_scale=0.0,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return _write_poster_file(
        buffer.getvalue(),
        ".png",
        "image/png",
        "huggingface",
        business_id,
        post_id,
        logo_url=logo_url,
        visual_context=visual_context,
    )


def _generate_gemini_poster(
    prompt: str,
    business_id: str,
    post_id: str,
    logo_url: str | None,
    visual_context: VisualAssetContext | None,
) -> PosterImage:
    payload = {
        "model": settings.gemini_image_model,
        "input": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
        "response_format": {
            "type": "image",
            "mime_type": "image/png",
            "aspect_ratio": "1:1",
        },
    }

    response = _post_gemini(payload)
    image_data = _extract_image_data(response)
    image_bytes = base64.b64decode(image_data)
    return _write_poster_file(
        image_bytes,
        ".png",
        "image/png",
        "gemini",
        business_id,
        post_id,
        logo_url=logo_url,
        visual_context=visual_context,
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

    with urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_image_data(response: dict) -> str:
    output_image = response.get("output_image") or response.get("outputImage")
    if isinstance(output_image, dict) and isinstance(output_image.get("data"), str):
        return output_image["data"]

    for step in response.get("steps", []):
        model_output = step.get("model_output") or step.get("modelOutput") or step
        for content in model_output.get("content", []):
            if content.get("type") == "image" and isinstance(content.get("data"), str):
                return content["data"]
            image = content.get("image")
            if isinstance(image, dict) and isinstance(image.get("data"), str):
                return image["data"]

    raise ValueError("Gemini response did not include image data")


def _generate_fallback_poster(
    generated_post: GeneratedPostResponse,
    business_id: str,
    error_message: str | None = None,
) -> PosterImage:
    hashtags = " ".join(generated_post.hashtags[:5])
    caption = generated_post.caption[:180]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="#f7f8f5"/>
  <rect x="64" y="64" width="952" height="952" rx="28" fill="#ffffff" stroke="#1b7b68" stroke-width="12"/>
  <text x="110" y="160" font-family="Arial, sans-serif" font-size="42" fill="#d9542b" font-weight="700">{html.escape(generated_post.content_type)}</text>
  <text x="110" y="275" font-family="Arial, sans-serif" font-size="82" fill="#11231d" font-weight="800">{html.escape(generated_post.product_name[:22])}</text>
  <foreignObject x="110" y="340" width="860" height="300">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, sans-serif; font-size: 42px; line-height: 1.25; color: #283b34;">{html.escape(caption)}</div>
  </foreignObject>
  <foreignObject x="110" y="730" width="860" height="130">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial, sans-serif; font-size: 34px; line-height: 1.3; color: #1b7b68; font-weight: 700;">{html.escape(hashtags)}</div>
  </foreignObject>
  <rect x="110" y="900" width="330" height="74" rx="8" fill="#1b7b68"/>
  <text x="150" y="949" font-family="Arial, sans-serif" font-size="34" fill="#ffffff" font-weight="700">Order Today</text>
</svg>"""
    return _write_poster_file(
        svg.encode("utf-8"),
        ".svg",
        "image/svg+xml",
        "fallback",
        business_id,
        generated_post.post_id,
        error_message,
    )


def _generate_layout_poster(
    generated_post: GeneratedPostResponse,
    business_id: str,
    visual_context: VisualAssetContext,
    template: PosterTemplate,
) -> PosterImage:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ImportError("Pillow is required for layout poster rendering. Run pip install -r requirements.txt.") from exc

    business = visual_context.business
    if not business:
        raise ValueError("Business profile is required for layout poster rendering")

    selected_template = _choose_template(template, generated_post.content_type)
    palette = _layout_palette(business, selected_template)
    width = 1080
    height = 1080

    image = Image.new("RGBA", (width, height), palette["background"])
    draw = ImageDraw.Draw(image)
    _draw_template_background(draw, width, height, palette, selected_template)

    margin = 70
    logo_reserved_height = _draw_logo_block(image, business.brand_kit.logo_url, margin, margin)
    eyebrow_y = margin + logo_reserved_height + 38
    eyebrow = generated_post.content_type.upper()[:34]
    draw.text(
        (margin, eyebrow_y),
        eyebrow,
        font=_font(36, bold=True),
        fill=palette["accent"],
    )

    headline = _headline_for_post(generated_post)
    headline_y = eyebrow_y + 52
    _draw_wrapped_text(
        draw,
        headline,
        (margin, headline_y),
        max_width=560,
        font=_font(78, bold=True),
        fill=palette["ink"],
        line_spacing=8,
        max_lines=3,
    )

    caption_y = headline_y + 250
    _draw_wrapped_text(
        draw,
        generated_post.caption,
        (margin, caption_y),
        max_width=560,
        font=_font(34),
        fill=palette["muted"],
        line_spacing=8,
        max_lines=4,
    )

    product_box = (640, 218, 1000, 660)
    product_drawn = _draw_product_image(image, visual_context.product_image_url, product_box)
    if not product_drawn:
        _draw_product_placeholder(draw, product_box, generated_post.product_name, palette)

    hashtags = " ".join(generated_post.hashtags[:4])
    _draw_wrapped_text(
        draw,
        hashtags,
        (margin, 802),
        max_width=620,
        font=_font(30, bold=True),
        fill=palette["primary"],
        line_spacing=6,
        max_lines=2,
    )

    cta = _cta_for_business(business)
    _draw_cta(draw, cta, (margin, 910), palette)
    _draw_footer(draw, business, width, height, palette)

    output = io.BytesIO()
    image.convert("RGB").save(output, format="PNG", optimize=True)
    return _write_poster_file(
        output.getvalue(),
        ".png",
        "image/png",
        "layout",
        business_id,
        generated_post.post_id,
    )


def _write_poster_file(
    data: bytes,
    extension: str,
    mime_type: str,
    provider: str,
    business_id: str,
    post_id: str,
    error_message: str | None = None,
    logo_url: str | None = None,
    visual_context: VisualAssetContext | None = None,
) -> PosterImage:
    if visual_context and visual_context.product_image_url:
        try:
            data, extension, mime_type = _overlay_product_image(
                data,
                mime_type,
                visual_context.product_image_url,
            )
        except Exception as exc:
            product_error = f"Product image overlay skipped: {_safe_error_message(exc)}"
            error_message = f"{error_message}; {product_error}" if error_message else product_error

    if logo_url:
        try:
            data, extension, mime_type = _overlay_logo(data, mime_type, logo_url)
        except Exception as exc:
            logo_error = f"Logo overlay skipped: {_safe_error_message(exc)}"
            error_message = f"{error_message}; {logo_error}" if error_message else logo_error

    storage_path = f"businesses/{business_id}/posters/{post_id}/poster_{uuid4().hex[:12]}{extension}"
    try:
        stored_asset = upload_bytes_to_storage(data, mime_type, storage_path)
        return PosterImage(
            image_url=stored_asset.image_url,
            storage_path=stored_asset.storage_path,
            mime_type=mime_type,
            provider=provider,
            error_message=error_message,
        )
    except Exception as exc:
        if error_message:
            error_message = f"{error_message}; Firebase Storage fallback: {exc}"
        else:
            error_message = f"Firebase Storage fallback: {exc}"

    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"poster_{uuid4().hex[:12]}{extension}"
    path = POSTER_DIR / filename
    path.write_bytes(data)

    storage_path = f"generated/posters/{filename}"
    public_url = f"{settings.backend_public_url.rstrip('/')}/static/posters/{filename}"
    return PosterImage(
        image_url=public_url,
        storage_path=storage_path,
        mime_type=mime_type,
        provider=provider,
        error_message=error_message,
    )


def _choose_template(template: PosterTemplate, content_type: str) -> str:
    if template != "auto":
        return template

    content = content_type.lower()
    if any(word in content for word in ["offer", "sale", "discount", "promotion"]):
        return "offer"
    if any(word in content for word in ["festival", "season", "holiday"]):
        return "festival"
    if any(word in content for word in ["educational", "tip", "how"]):
        return "educational"
    return "product_spotlight"


def _layout_palette(business: BusinessProfileResponse, template: str) -> dict[str, tuple[int, int, int, int]]:
    primary = _hex_to_rgba(business.brand_kit.primary_color, (27, 123, 104, 255))
    secondary = _hex_to_rgba(business.brand_kit.secondary_color, (217, 84, 43, 255))
    accent = _hex_to_rgba(business.brand_kit.accent_color, (242, 201, 76, 255))
    background = {
        "product_spotlight": (248, 250, 246, 255),
        "educational": (245, 248, 250, 255),
        "offer": (255, 248, 242, 255),
        "festival": (255, 250, 235, 255),
    }.get(template, (248, 250, 246, 255))
    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "background": background,
        "surface": (255, 255, 255, 244),
        "ink": (15, 31, 26, 255),
        "muted": (56, 74, 68, 255),
        "line": (224, 231, 225, 255),
    }


def _draw_template_background(draw, width: int, height: int, palette: dict, template: str) -> None:
    draw.rectangle((0, 0, width, height), fill=palette["background"])
    draw.rounded_rectangle((46, 46, width - 46, height - 46), radius=34, fill=palette["surface"])

    if template == "offer":
        draw.rectangle((0, height - 260, width, height), fill=palette["secondary"])
        draw.rectangle((0, height - 276, width, height - 260), fill=palette["accent"])
    elif template == "festival":
        draw.ellipse((760, -160, 1180, 260), fill=(*palette["accent"][:3], 80))
        draw.ellipse((-180, 720, 260, 1160), fill=(*palette["secondary"][:3], 56))
    elif template == "educational":
        draw.rectangle((0, 0, width, 122), fill=(*palette["primary"][:3], 235))
        draw.rectangle((0, 122, width, 136), fill=palette["accent"])
    else:
        draw.rectangle((0, 0, width, 32), fill=palette["primary"])
        draw.rectangle((0, height - 32, width, height), fill=palette["primary"])


def _draw_logo_block(image, logo_url: str, x: int, y: int) -> int:
    if not logo_url:
        return 0

    try:
        logo = _open_remote_image(logo_url)
        logo.thumbnail((220, 96))
        backing = Image.new("RGBA", (logo.width + 32, logo.height + 24), (255, 255, 255, 220))
        image.alpha_composite(backing, (x, y))
        image.alpha_composite(logo, (x + 16, y + 12))
        return backing.height
    except Exception:
        return 0


def _draw_product_image(image, image_url: str, box: tuple[int, int, int, int]) -> bool:
    if not image_url:
        return False

    try:
        from PIL import Image, ImageDraw
        product = _open_remote_image(image_url)
    except Exception:
        return False

    x1, y1, x2, y2 = box
    box_width = x2 - x1
    box_height = y2 - y1
    product.thumbnail((box_width - 48, box_height - 48), Image.Resampling.LANCZOS)

    backing = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 236))
    mask = Image.new("L", (box_width, box_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, box_width, box_height), radius=34, fill=255)
    backing.putalpha(mask)
    image.alpha_composite(backing, (x1, y1))

    px = x1 + (box_width - product.width) // 2
    py = y1 + (box_height - product.height) // 2
    image.alpha_composite(product, (px, py))
    return True


def _draw_product_placeholder(draw, box: tuple[int, int, int, int], product_name: str, palette: dict) -> None:
    draw.rounded_rectangle(box, radius=34, fill=(255, 255, 255, 236), outline=palette["line"], width=3)
    _draw_wrapped_text(
        draw,
        product_name,
        (box[0] + 34, box[1] + 150),
        max_width=box[2] - box[0] - 68,
        font=_font(42, bold=True),
        fill=palette["primary"],
        line_spacing=8,
        max_lines=3,
    )


def _draw_cta(draw, cta: str, position: tuple[int, int], palette: dict) -> None:
    x, y = position
    font = _font(34, bold=True)
    bbox = draw.textbbox((0, 0), cta, font=font)
    width = bbox[2] - bbox[0] + 58
    height = 78
    draw.rounded_rectangle((x, y, x + width, y + height), radius=14, fill=palette["primary"])
    draw.text((x + 29, y + 21), cta, font=font, fill=(255, 255, 255, 255))


def _draw_footer(draw, business: BusinessProfileResponse, width: int, height: int, palette: dict) -> None:
    footer_parts = [part for part in [business.website_url, business.phone_number] if part]
    if not footer_parts:
        footer_parts = [business.business_name]
    footer = "  |  ".join(footer_parts)[:70]
    draw.text((70, height - 78), footer, font=_font(26), fill=palette["muted"])


def _headline_for_post(generated_post: GeneratedPostResponse) -> str:
    if generated_post.content_type.lower().startswith("offer"):
        return f"Try {generated_post.product_name} Today"
    return generated_post.product_name


def _cta_for_business(business: BusinessProfileResponse) -> str:
    if business.website_url:
        return "Order Today"
    if business.phone_number:
        return "Message to Order"
    return "Learn More"


def _draw_wrapped_text(
    draw,
    text: str,
    position: tuple[int, int],
    max_width: int,
    font,
    fill,
    line_spacing: int,
    max_lines: int,
) -> None:
    x, y = position
    lines = _wrap_text(draw, text, font, max_width, max_lines)
    line_height = _line_height(font) + line_spacing
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, font=font, fill=fill)


def _wrap_text(draw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    words = text.replace("\n", " ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = f"{lines[-1].rstrip('., ')}..."
    return lines


def _line_height(font) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1]


def _font(size: int, bold: bool = False):
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise ImportError("Pillow is required for layout poster rendering. Run pip install -r requirements.txt.") from exc

    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _hex_to_rgba(value: str, fallback: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        return fallback
    try:
        return (
            int(raw[0:2], 16),
            int(raw[2:4], 16),
            int(raw[4:6], 16),
            255,
        )
    except ValueError:
        return fallback


def _build_poster_prompt(
    generated_post: GeneratedPostResponse,
    visual_context: VisualAssetContext | None = None,
) -> str:
    base_prompt = generated_post.poster_prompt or generated_post.caption
    brand_prompt = _build_visual_context_prompt(visual_context)
    return (
        f"{base_prompt}\n\n"
        "Create a polished square 1:1 social media poster for Instagram. "
        "Use premium small-business advertising style, clear product focus, "
        "readable composition, no misleading medical claims, and leave space "
        f"for a headline about {generated_post.product_name}. "
        "Do not include garbled text. "
        "Do not invent a different logo, package, ingredient, or product shape. "
        f"{brand_prompt}"
    )


def _build_visual_context_prompt(visual_context: VisualAssetContext | None) -> str:
    if not visual_context:
        return ""

    parts: list[str] = []
    business = visual_context.business
    product = visual_context.product

    if business:
        colors = ", ".join(
            color
            for color in [
                business.brand_kit.primary_color,
                business.brand_kit.secondary_color,
                business.brand_kit.accent_color,
            ]
            if color
        )
        parts.append(
            "Brand identity: "
            f"name={business.business_name}; industry={business.industry}; "
            f"tone={business.brand_tone}; website={business.website_url}; "
            f"colors={colors}; heading font={business.brand_kit.heading_font_family}; "
            f"body font={business.brand_kit.font_family}; "
            f"visual style={', '.join(business.brand_kit.visual_style[:5])}; "
            f"brand keywords={', '.join(business.brand_kit.brand_keywords[:8])}."
        )
        if business.brand_kit.logo_url:
            parts.append("Final poster will include the uploaded brand logo at the top; leave clean space for it.")
        if business.brand_kit.avatar_url:
            parts.append("Use the brand avatar as identity reference if a profile mark is needed.")

    if product:
        parts.append(
            "Product truth: "
            f"name={product.name}; category={product.category}; description={product.description}; "
            f"benefits={', '.join(product.benefits[:5])}; ingredients={', '.join(product.ingredients[:8])}; "
            f"image notes={product.image_notes}; uploaded product image count={len(product.image_urls)}."
        )
        if product.image_urls:
            parts.append("Final poster will include the uploaded product image; design around it.")

    if visual_context.reference_images:
        reference_descriptions = []
        for reference in visual_context.reference_images[:8]:
            reference_descriptions.append(
                " / ".join(
                    part
                    for part in [
                        reference.name,
                        reference.reference_type,
                        ", ".join(reference.labels[:6]),
                        reference.notes,
                    ]
                    if part
                )
            )
        parts.append(f"Reference visual memory: {'; '.join(reference_descriptions)}.")

    return " ".join(parts)


def _open_remote_image(image_url: str):
    try:
        from PIL import Image
    except ImportError as exc:
        raise ImportError("Pillow is required for poster compositing. Run pip install -r requirements.txt.") from exc

    request = Request(image_url, headers={"User-Agent": "ai-marketing-partner/1.0"})
    with urlopen(request, timeout=20) as response:
        image_bytes = response.read()

    return Image.open(io.BytesIO(image_bytes)).convert("RGBA")


def _overlay_logo(data: bytes, mime_type: str, logo_url: str) -> tuple[bytes, str, str]:
    if mime_type not in {"image/png", "image/jpeg", "image/jpg"}:
        return data, ".svg" if mime_type == "image/svg+xml" else ".png", mime_type

    try:
        from PIL import Image
    except ImportError as exc:
        raise ImportError("Pillow is required for logo overlay. Run pip install -r requirements.txt.") from exc

    with Image.open(io.BytesIO(data)) as base_image:
        base = base_image.convert("RGBA")

    logo = _open_remote_image(logo_url)

    max_logo_width = max(120, int(base.width * 0.22))
    max_logo_height = max(80, int(base.height * 0.12))
    logo.thumbnail((max_logo_width, max_logo_height), Image.Resampling.LANCZOS)

    margin = max(32, int(base.width * 0.035))
    backing_padding = max(16, int(base.width * 0.014))
    backing = Image.new(
        "RGBA",
        (logo.width + backing_padding * 2, logo.height + backing_padding * 2),
        (255, 255, 255, 220),
    )
    base.alpha_composite(backing, (margin, margin))
    base.alpha_composite(logo, (margin + backing_padding, margin + backing_padding))

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue(), ".png", "image/png"


def _overlay_product_image(
    data: bytes,
    mime_type: str,
    product_image_url: str,
) -> tuple[bytes, str, str]:
    if mime_type not in {"image/png", "image/jpeg", "image/jpg"}:
        return data, ".svg" if mime_type == "image/svg+xml" else ".png", mime_type

    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ImportError("Pillow is required for product image overlay. Run pip install -r requirements.txt.") from exc

    with Image.open(io.BytesIO(data)) as base_image:
        base = base_image.convert("RGBA")

    product = _open_remote_image(product_image_url)
    max_product_width = max(260, int(base.width * 0.34))
    max_product_height = max(260, int(base.height * 0.34))
    product.thumbnail((max_product_width, max_product_height), Image.Resampling.LANCZOS)

    margin = max(36, int(base.width * 0.04))
    padding = max(18, int(base.width * 0.018))
    box_width = product.width + padding * 2
    box_height = product.height + padding * 2
    x = base.width - box_width - margin
    y = base.height - box_height - margin

    backing = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 232))
    mask = Image.new("L", (box_width, box_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, box_width, box_height), radius=28, fill=255)
    backing.putalpha(mask)
    base.alpha_composite(backing, (x, y))
    base.alpha_composite(product, (x + padding, y + padding))

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue(), ".png", "image/png"


def _safe_error_message(exc: Exception) -> str:
    if isinstance(exc, HTTPError):
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        if body:
            return f"HTTP {exc.code}: {body[:500]}"
        return f"HTTP {exc.code}: {exc.reason}"

    return str(exc)[:500]
