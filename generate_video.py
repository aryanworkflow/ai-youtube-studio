
import json
import os
import random
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("output")
WORK = OUT / "work"
WORK.mkdir(parents=True, exist_ok=True)

FORMAT = os.getenv("VIDEO_FORMAT", "shorts")
SHORT = FORMAT == "shorts"

W, H = (720, 1280) if SHORT else (1280, 720)
FPS = 24

SCENES = [
    {
        "title": "DID YOU KNOW?",
        "caption": "Your brain keeps learning.",
        "narration": (
            "Did you know your brain keeps learning? "
            "Every new experience gives your brain something to process."
        ),
        "symbol": "brain",
    },
    {
        "title": "SMALL STEPS",
        "caption": "Practice builds habits.",
        "narration": (
            "Small steps can make a difference. "
            "Practising a skill regularly can help you improve over time."
        ),
        "symbol": "star",
    },
    {
        "title": "REST MATTERS",
        "caption": "Give your mind time to rest.",
        "narration": (
            "Rest matters too. Sleep helps your brain process "
            "information and supports learning and memory."
        ),
        "symbol": "moon",
    },
    {
        "title": "KEEP GOING",
        "caption": "Progress takes consistency.",
        "narration": (
            "Keep going, one step at a time. "
            "Choose one useful thing to practise today. "
            "Follow for more simple explainers."
        ),
        "symbol": "sun",
    },
]

BG = (255, 249, 231)
INK = (65, 54, 47)
COLORS = [
    (238, 119, 99),
    (92, 165, 130),
    (108, 151, 220),
    (242, 190, 79),
]

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(args):
    subprocess.run(args, check=True)


def font(path, size):
    return ImageFont.truetype(path, size)


def centered_text(draw, text, y, fnt, fill):
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=0)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=fnt, fill=fill)


def wrap_words(draw, text, fnt, max_width):
    words = text.split()
    lines, current = [], ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines


def crayon_symbol(draw, kind, cx, cy, color, rng):
    # Repeated imperfect strokes create a hand-drawn texture.
    radius = min(W, H) // 7

    for _ in range(260):
        angle = rng.random() * 6.283185
        r = radius * (rng.random() ** 0.5)
        x = cx + int(r * __import__("math").cos(angle))
        y = cy + int(r * __import__("math").sin(angle))
        dx = rng.randint(-10, 10)
        dy = rng.randint(-8, 8)
        draw.line(
            (x, y, x + dx, y + dy),
            fill=(*color, 170),
            width=rng.choice([1, 2, 3, 4]),
        )

    # Rough outline around the illustration.
    for _ in range(3):
        offset = rng.randint(-5, 5)
        draw.ellipse(
            (
                cx - radius + offset,
                cy - radius + offset,
                cx + radius + offset,
                cy + radius + offset,
            ),
            outline=color,
            width=3,
        )

    if kind == "sun":
        for angle in range(0, 360, 45):
            import math
            a = math.radians(angle)
            x1 = cx + int((radius + 12) * math.cos(a))
            y1 = cy + int((radius + 12) * math.sin(a))
            x2 = cx + int((radius + 42) * math.cos(a))
            y2 = cy + int((radius + 42) * math.sin(a))
            draw.line((x1, y1, x2, y2), fill=color, width=6)

    elif kind == "moon":
        draw.ellipse(
            (cx - radius // 2, cy - radius,
             cx + radius + radius // 2, cy + radius),
            fill=color,
        )
        draw.ellipse(
            (cx, cy - radius - 12,
             cx + radius + 30, cy + radius - 12),
            fill=BG,
        )

    elif kind == "star":
        import math
        points = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = radius if i % 2 == 0 else radius * 0.48
            points.append(
                (cx + int(r * math.cos(a)),
                 cy + int(r * math.sin(a)))
            )
        draw.polygon(points, fill=color, outline=INK)

    else:
        # Simple brain-like lobes, drawn as overlapping circles.
        lobes = [
            (-35, -20, 40), (5, -28, 42), (-48, 20, 34),
            (0, 18, 38), (40, 4, 34)
        ]
        for ox, oy, r in lobes:
            draw.ellipse(
                (cx + ox - r, cy + oy - r,
                 cx + ox + r, cy + oy + r),
                outline=INK, width=5
            )


def make_scene(scene, index):
    rng = random.Random(500 + index)
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)

    # Paper-like speckles.
    for _ in range(W * H // 1200):
        x, y = rng.randrange(W), rng.randrange(H)
        shade = rng.choice([(243, 235, 216), (250, 245, 228)])
        draw.point((x, y), fill=shade)

    margin = int(W * 0.09)
    accent = COLORS[index % len(COLORS)]

    # Loose, hand-drawn page borders.
    for j in range(3):
        jitter = rng.randint(-5, 5)
        draw.rounded_rectangle(
            (margin + jitter, 25 + j * 5,
             W - margin + jitter, H - 25 - j * 5),
            radius=30,
            outline=accent,
            width=2,
        )

    title_font = font(FONT_BOLD, 42 if SHORT else 38)
    caption_font = font(FONT_BOLD, 34 if SHORT else 30)
    small_font = font(FONT_REG, 20)

    centered_text(draw, scene["title"], int(H * 0.12),
                  title_font, INK)

    crayon_symbol(
        draw,
        scene["symbol"],
        W // 2,
        int(H * 0.39),
        accent,
        rng,
    )

    lines = wrap_words(
        draw, scene["caption"], caption_font, W - 2 * margin - 20
    )
    y = int(H * 0.61)
    for line in lines[:3]:
        centered_text(draw, line, y, caption_font, INK)
        y += caption_font.size + 12

    centered_text(
        draw, f"SCENE {index + 1} / {len(SCENES)}",
        H - 85, small_font, INK
    )

    path = WORK / f"scene_{index:02d}.png"
    image.save(path)
    return path


def main():
    if not Path("/usr/bin/espeak-ng").exists():
        raise RuntimeError("eSpeak NG is missing. Check the workflow setup.")

    segments = []

    for i, scene in enumerate(SCENES):
        print(f"Creating scene {i + 1}/{len(SCENES)}")

        image_path = make_scene(scene, i)
        audio_path = WORK / f"voice_{i:02d}.wav"
        segment_path = WORK / f"segment_{i:02d}.mp4"

        run([
            "espeak-ng", "-v", "en-us", "-s", "145",
            "-w", str(audio_path), scene["narration"]
        ])

        # Slow zoom gives the illustration gentle movement.
        vf = (
            f"scale={W}:{H},"
            f"zoompan=z='min(zoom+0.0005,1.04)':"
            f"d=1:s={W}x{H}:fps={FPS},"
            "format=yuv420p"
        )

        run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", str(FPS),
            "-i", str(image_path),
            "-i", str(audio_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast",
            "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-movflags", "+faststart",
            str(segment_path),
        ])

        segments.append(segment_path)

    concat_path = WORK / "concat.txt"
    with concat_path.open("w", encoding="utf-8") as f:
        for segment in segments:
            f.write(f"file '{segment.resolve()}'\n")

    video_path = OUT / "preview.mp4"
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_path),
        "-c", "copy", "-movflags", "+faststart",
        str(video_path),
    ])

    metadata = {
        "title": "Small Habits, Big Results",
        "description": (
            "An illustrated educational explainer about learning, "
            "practice, rest and consistency."
        ),
        "format": FORMAT,
        "review_required": True,
        "narration": "eSpeak NG offline synthetic English voice",
        "scenes": len(SCENES),
    }

    (OUT / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(f"SUCCESS: video created at {video_path}")


if __name__ == "__main__":
    main()
