from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .common import load_json, safe_relative_path, sha256


def _color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected a six-digit RGB color, received {value!r}")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    start, end = _color(top), _color(bottom)
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(round(start[i] + (end[i] - start[i]) * ratio) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image


def _font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path and Path(path).is_file():
        return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _fit_text(draw: ImageDraw.ImageDraw, title: str, font_path: str | None,
              max_width: int, starting_size: int) -> ImageFont.ImageFont:
    for size in range(starting_size, 15, -2):
        font = _font(font_path, size)
        if draw.textbbox((0, 0), title, font=font)[2] <= max_width:
            return font
    return _font(font_path, 16)


def generate(config_path: Path) -> list[Path]:
    config_path = config_path.resolve()
    config = load_json(config_path)
    root = config_path.parent
    width, height = (int(v) for v in config["canvas"])
    output = safe_relative_path(root, config.get("output", "output"))
    output.mkdir(parents=True, exist_ok=True)
    frame = config.get("frame", {})
    frame_width = int(frame.get("width", width * 0.72))
    frame_height = int(frame.get("height", height * 0.70))
    frame_x = (width - frame_width) // 2
    frame_y = int(frame.get("top", height * 0.25))
    border = int(frame.get("border", max(12, width * 0.018)))
    radius = int(frame.get("radius", max(24, width * 0.05)))
    results: list[Path] = []
    manifest: list[dict[str, Any]] = []

    for index, slide in enumerate(config["slides"], start=1):
        source = safe_relative_path(root, slide["source"])
        if not source.is_file():
            raise FileNotFoundError(source)
        canvas = _gradient((width, height), config["colors"]["top"], config["colors"]["bottom"])
        draw = ImageDraw.Draw(canvas)
        brand = str(config.get("brand", ""))
        brand_font = _font(config.get("font"), int(width * 0.032))
        draw.text((int(width * 0.06), int(height * 0.025)), brand, fill=_color(config["colors"]["text"]), font=brand_font)
        title = str(slide["title"])
        title_font = _fit_text(draw, title, config.get("font"), int(width * 0.86), int(width * 0.055))
        box = draw.textbbox((0, 0), title, font=title_font)
        draw.text(((width - (box[2] - box[0])) // 2, int(height * 0.105)), title,
                  fill=_color(config["colors"]["text"]), font=title_font)

        draw.rounded_rectangle((frame_x, frame_y, frame_x + frame_width, frame_y + frame_height),
                               radius=radius, fill=_color(frame.get("color", "#111820")))
        screen_box = (frame_x + border, frame_y + border,
                      frame_x + frame_width - border, frame_y + frame_height - border)
        with Image.open(source) as source_image:
            screen = ImageOps.fit(source_image.convert("RGB"),
                                  (screen_box[2] - screen_box[0], screen_box[3] - screen_box[1]),
                                  method=Image.Resampling.LANCZOS,
                                  centering=(0.5, float(slide.get("vertical_focus", 0.5))))
        mask = Image.new("L", screen.size)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, screen.width, screen.height), radius=max(4, radius - border), fill=255)
        canvas.paste(screen, screen_box[:2], mask)

        slug = str(slide.get("slug", f"slide-{index:02d}"))
        target = output / f"{index:02d}-{slug}.png"
        canvas.save(target, format="PNG", optimize=True)
        results.append(target)
        manifest.append({"file": target.name, "title": title, "altText": slide.get("altText", ""),
                         "width": width, "height": height, "mode": "RGB"})

    for item, target in zip(manifest, results, strict=True):
        item["sha256"] = sha256(target)
        item["bytes"] = target.stat().st_size
    (output / "manifest.json").write_text(json.dumps({"assets": manifest}, indent=2) + "\n", encoding="utf-8")
    return results
