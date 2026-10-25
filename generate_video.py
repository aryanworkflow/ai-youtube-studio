
import json
import os
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("output")
OUT.mkdir(exist_ok=True)

is_short = os.getenv("VIDEO_FORMAT", "shorts") == "shorts"

scenes = [
    ("DID YOU KNOW?", "Your brain is always learning."),
    ("SMALL STEPS", "Repeated practice builds stronger habits."),
    ("SLEEP MATTERS", "Rest helps your brain process memories."),
    ("KEEP GOING", "Progress comes from consistent effort."),
]

width, height = (720, 1280) if is_short else (1280, 720)
duration = 4
fps = 24

def make_svg(title, caption, index):
    title = escape(title)
    caption = escape(caption)
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}">
    <rect width="100%" height="100%" fill="#fff8e8"/>
    <path d="M50 80 Q{width//2} 40 {width-50} 90
      M70 {height-120} Q{width//2} {height-80} {width-60} {height-140}"
      fill="none" stroke="#e5a44a" stroke-width="7"
      stroke-linecap="round" opacity=".7"/>
    <circle cx="{width//2}" cy="{height//2-100}"
      r="100" fill="#ffcf70" stroke="#9a653d" stroke-width="5"/>
    <text x="50%" y="{height//2+160}" text-anchor="middle"
      font-size="{54 if is_short else 48}" font-family="DejaVu Sans"
      font-weight="bold" fill="#333333">{title}</text>
    <text x="50%" y="{height//2+240}" text-anchor="middle"
      font-size="30" font-family="DejaVu Sans" fill="#444444">
      {caption}</text>
    <text x="50%" y="{height-60}" text-anchor="middle"
      font-size="22" font-family="DejaVu Sans" fill="#777777">
      SCENE {index+1}</text>
    </svg>"""

concat = OUT / "scenes.txt"
with concat.open("w", encoding="utf-8") as f:
    for i, (title, caption) in enumerate(scenes):
        svg = make_svg(title, caption, i)
        svg_path = OUT / f"scene_{i}.svg"
        png_path = OUT / f"scene_{i}.png"
        svg_path.write_text(svg, encoding="utf-8")

        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(svg_path), str(png_path)
        ], check=True)

        f.write(f"file '{png_path.resolve()}'\n")
        f.write(f"duration {duration}\n")

    f.write(f"file '{(OUT / f'scene_{len(scenes)-1}.png').resolve()}'\n")

video = OUT / "preview.mp4"
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", str(concat),
    "-vf", f"scale={width}:{height},format=yuv420p",
    "-r", str(fps), "-c:v", "libx264",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    str(video)
], check=True)

(OUT / "metadata.json").write_text(json.dumps({
    "title": "Small Habits, Big Results",
    "description": "A short illustrated educational video.",
    "format": "shorts" if is_short else "explainer",
    "review_required": True
}, indent=2), encoding="utf-8")

print(f"Video created: {video}")
