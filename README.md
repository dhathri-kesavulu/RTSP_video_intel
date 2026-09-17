# RTSP Video Intelligence Module

## What it does
A real RTSP video pipeline — not a webcam-over-HTTP hack — with basic
ONVIF-style device discovery, live object detection using YOLOv8, and
real-time detection stats pushed over WebSocket.

## Why I built it
Built as a self-directed project to get hands-on with RTSP/ONVIF/computer
vision, whose UAV/UGV
command-and-control platform uses this exact stack. Paired with a
companion project, Multi-Vehicle GCS Core, this module is framed as a
sensor plugin that could feed into that GCS.

## Tech Stack
- **Video server:** MediaMTX (lightweight RTSP server)
- **Processing:** Python, OpenCV, Ultralytics YOLOv8 (nano, pretrained)
- **Discovery:** onvif-zeep (ONVIF-style device discovery)
- **Streaming to browser:** MJPEG over HTTP + WebSocket for detection stats

## Architecture
```
[Webcam] --> [MediaMTX RTSP Server] --RTSP--> [Python: OpenCV + YOLOv8]
                                                        |
                                          [FastAPI: /video (MJPEG) + /ws/stats]
                                                        |
                                              [Browser Dashboard]
```

## What's simulated vs real
- **Video source:** real RTSP stream, pushed from an actual USB webcam via ffmpeg — not a canned video file.
- **Object detection:** real YOLOv8 inference running on live frames, not mocked.
- **ONVIF discovery:** scaffolded and functional against a real ONVIF-compliant camera, but not tested end-to-end here since only a plain USB webcam was available — documented as a known limitation rather than hidden.

## How to run
1. Start MediaMTX:
   ```bash
   ./mediamtx
   ```
2. Push a video source into it with ffmpeg, e.g.:
   ```bash
   ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -f rtsp rtsp://localhost:8554/mystream
   ```
3. (Optional sanity check) confirm the stream plays:
   ```bash
   python3 rtsp_test.py
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the detection + streaming server:
   ```bash
   uvicorn video_server:app --reload --host 0.0.0.0 --port 8000
   ```
6. Open `http://localhost:8000/static/index.html` in a browser.

## Demo
[link to video- yet to be shot and uploaded]

## Next steps
- Full ONVIF device negotiation against a real IP camera
- Persist detection stats/history instead of only streaming live
- Swap YOLOv8n for a larger model if accuracy needs outweigh the speed cost
