"""
Day 5 - Detection + MJPEG streaming server.

Pulls the RTSP stream (served by MediaMTX), runs YOLOv8 object detection
on each frame, and exposes:

  GET  /video     -> MJPEG stream of annotated frames (for <img src="/video">)
  WS   /ws/stats  -> live JSON object-count stats, pushed twice a second

Run with:
    uvicorn video_server:app --reload --host 0.0.0.0 --port 8000

Then open:
    http://localhost:8000/static/index.html
"""

import asyncio

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO

RTSP_URL = "rtsp://localhost:8554/mystream"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# yolov8n = "nano" variant: smallest and fastest of the YOLOv8 family,
# which matters here since we're running inference on every live frame.
# Ultralytics auto-downloads these weights on first run if not present.
model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(RTSP_URL)


def gen_frames():
    """
    Generator that continuously reads frames from the RTSP stream, runs
    YOLOv8 detection, draws bounding boxes, and yields them as JPEG bytes
    in the multipart MJPEG format browsers know how to render directly
    in an <img> tag.
    """
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        results = model(frame, verbose=False)
        annotated = results[0].plot()  # draws bounding boxes + class labels on the frame

        ok, buffer = cv2.imencode(".jpg", annotated)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.get("/video")
def video_feed():
    """Serves the annotated MJPEG stream for a browser <img> tag to consume."""
    return StreamingResponse(
        gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.websocket("/ws/stats")
async def stats_ws(websocket: WebSocket):
    """
    Pushes a small JSON payload with the current detected-object count
    every 0.5s, so the frontend can show a live stats box alongside the
    video without needing to decode frames itself.
    """
    await websocket.accept()

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                results = model(frame, verbose=False)
                count = len(results[0].boxes)
                await websocket.send_json({"object_count": count})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass


@app.on_event("shutdown")
def shutdown_event():
    """Release the video capture cleanly when the server stops."""
    cap.release()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
