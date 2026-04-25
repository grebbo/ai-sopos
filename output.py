import os
import re
from datetime import datetime


OUTPUT_DIR = "output"


def _sanitize_filename(title: str) -> str:
    clean = re.sub(r"[^\w\s-]", "", title).strip()
    return re.sub(r"\s+", "_", clean).lower()[:50]


def save_story(title: str, story: str, theme: str, filename: str | None = None) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if filename is None:
        slug = _sanitize_filename(title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_{timestamp}.txt" if slug else f"fiaba_{theme}_{timestamp}.txt"

    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{'=' * len(title)}\n\n{story}")

    return filepath
