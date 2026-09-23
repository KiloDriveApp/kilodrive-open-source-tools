"""Create the synthetic screenshot used by the StoreFrame example."""

from pathlib import Path

from PIL import Image, ImageDraw


target = Path(__file__).parent / "fixtures/example-screen.png"
target.parent.mkdir(parents=True, exist_ok=True)
image = Image.new("RGB", (540, 1080), "#F7FAF7")
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, 540, 110), fill="#123B45")
draw.text((30, 38), "Example App", fill="white")
draw.rounded_rectangle((35, 165, 505, 410), radius=28, fill="#D8FFE1", outline="#7DBB8B", width=3)
draw.text((65, 210), "Your useful content", fill="#082D35")
draw.text((65, 270), "Synthetic example screenshot", fill="#35565C")
draw.rounded_rectangle((35, 460, 505, 560), radius=24, fill="#1689D9")
draw.text((160, 500), "Primary action", fill="white")
draw.rounded_rectangle((35, 610, 250, 870), radius=28, fill="#E9F7EE")
draw.rounded_rectangle((290, 610, 505, 870), radius=28, fill="#E9F7EE")
image.save(target, format="PNG", optimize=True)
print(target)
