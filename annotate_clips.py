"""
annotate_clips.py

Runs YOLOv8 detection on each sample clip ONCE and saves the annotated
result (bounding boxes baked into the video) as a plain .mp4 file.

Why this exists: the simulation/deployed version of the dashboard doesn't
need to run live inference for every visitor — that doesn't scale to a
big LinkedIn audience clicking around. Instead, we do the expensive part
(YOLOv8 inference) a single time, right now, and the deployed app just
serves the already-annotated video files afterward — which is cheap no
matter how many people watch.

Usage:
    1. Put your raw clips in samples/, named clip1.mp4, clip2.mp4, etc.
    2. Run: python3 annotate_clips.py
    3. Annotated output lands in static/clips/clip1_detected.mp4, etc.
       ready to be served directly to the browser.
"""

import os
from pathlib import Path

from ultralytics import YOLO

SAMPLES_DIR = Path("samples")
OUTPUT_DIR = Path("static/clips")

# yolov8n = nano variant — fastest, which matters here since we're about
# to run it on several full video files in one go.
MODEL = YOLO("yolov8n.pt")


def annotate_all_clips():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    clip_paths = sorted(SAMPLES_DIR.glob("clip*.mp4"))
    if not clip_paths:
        print(f"[ERROR] No files matching clip*.mp4 found in {SAMPLES_DIR}/")
        return

    for clip_path in clip_paths:
        print(f"[..] Running YOLOv8 on {clip_path.name}")

        # Ultralytics can run detection directly on a video file and save
        # an annotated copy — no need to hand-roll the frame loop here,
        # since this only needs to happen once, not on every visitor request.
        results = MODEL.predict(
            source=str(clip_path),
            save=True,
            project=str(OUTPUT_DIR.parent),  # "static"
            name="clips_raw",
            exist_ok=True,
        )

        # Ultralytics names its own output file after the source clip;
        # rename it to a predictable "<name>_detected.mp4" so the frontend
        # can reference it directly.
        raw_output = OUTPUT_DIR.parent / "clips_raw" / clip_path.name
        final_output = OUTPUT_DIR / f"{clip_path.stem}_detected.mp4"

        if raw_output.exists():
            raw_output.rename(final_output)
            print(f"[OK] Saved {final_output}")
        else:
            print(f"[WARN] Expected output not found at {raw_output} — check Ultralytics' printed save path above.")

    # Clean up the now-empty intermediate folder Ultralytics created.
    intermediate = OUTPUT_DIR.parent / "clips_raw"
    if intermediate.exists() and not any(intermediate.iterdir()):
        intermediate.rmdir()

    print(f"\n[DONE] Annotated clips are in {OUTPUT_DIR}/")


if __name__ == "__main__":
    annotate_all_clips()
