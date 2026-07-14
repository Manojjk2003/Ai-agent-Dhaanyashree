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
from app.schemas.generated_post import GeneratedPostResponse


GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
POSTER_DIR = BACKEND_DIR.parent / "generated" / "posters"


@dataclass(frozen=True)
class PosterImage:
    image_url: str
    storage_path: str
    mime_type: str
    provider: str
    error_message: str | None = None


def generate_poster_image(generated_post: GeneratedPostResponse) -> PosterImage:
    prompt = _build_poster_prompt(generated_post)
    image_provider = settings.image_provider.lower()
    fallback_reason = None

    if image_provider == "huggingface" and settings.hf_token:
        try:
            return _generate_huggingface_poster(prompt)
        except Exception as exc:
            fallback_reason = _safe_error_message(exc)

    if image_provider == "gemini" and settings.gemini_api_key:
        try:
            return _generate_gemini_poster(prompt)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            fallback_reason = _safe_error_message(exc)

    if image_provider == "huggingface" and not settings.hf_token:
        fallback_reason = "HF_TOKEN is not configured on the backend"
    elif image_provider == "gemini" and not settings.gemini_api_key:
        fallback_reason = "GEMINI_API_KEY is not configured on the backend"
    elif image_provider not in {"fallback", "gemini", "huggingface"}:
        fallback_reason = f"Unsupported IMAGE_PROVIDER value: {settings.image_provider}"

    return _generate_fallback_poster(generated_post, fallback_reason)


def _generate_huggingface_poster(prompt: str) -> PosterImage:
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
    )


def _generate_gemini_poster(prompt: str) -> PosterImage:
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
    return _write_poster_file(image_bytes, ".png", "image/png", "gemini")


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
        error_message,
    )


def _write_poster_file(
    data: bytes,
    extension: str,
    mime_type: str,
    provider: str,
    error_message: str | None = None,
) -> PosterImage:
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


def _build_poster_prompt(generated_post: GeneratedPostResponse) -> str:
    base_prompt = generated_post.poster_prompt or generated_post.caption
    return (
        f"{base_prompt}\n\n"
        "Create a polished square 1:1 social media poster for Instagram. "
        "Use premium small-business advertising style, clear product focus, "
        "readable composition, no misleading medical claims, and leave space "
        f"for a headline about {generated_post.product_name}. "
        "Do not include garbled text."
    )


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
