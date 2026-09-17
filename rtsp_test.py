"""
Day 4 checkpoint script.

Confirms the RTSP stream coming out of MediaMTX is actually playable —
i.e. proves the full chain (webcam -> ffmpeg -> MediaMTX -> OpenCV) works
before we add any YOLO/detection logic on top of it.

Run this AFTER:
  1. MediaMTX is running:      ./mediamtx
  2. ffmpeg is pushing your webcam into it as rtsp://localhost:8554/mystream

Usage:
    python3 rtsp_test.py

Press 'q' in the video window to quit.
"""

import sys

import cv2

RTSP_URL = "rtsp://localhost:8554/mystream"


def main() -> None:
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print(f"[ERROR] Could not open stream at {RTSP_URL}")
        print("Check that:")
        print("  - MediaMTX is running (./mediamtx)")
        print("  - ffmpeg is actively pushing to this URL")
        sys.exit(1)

    print(f"[OK] Connected to {RTSP_URL}. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame not received, retrying...")
            continue

        cv2.imshow("RTSP Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
