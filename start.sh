#!/bin/bash
# start.sh
#
# A deployed container only runs ONE main process. Locally, you ran
# MediaMTX, ffmpeg, and uvicorn as three separate terminal commands —
# this script does the same three things, but from inside one container,
# so the whole pipeline comes up together whenever the container starts.
set -e

# 1. Start MediaMTX (the RTSP server) in the background.
#    "&" means "run this and immediately move to the next line"
#    instead of waiting for it to finish (it never finishes on its own).
./mediamtx &

# Give MediaMTX a moment to finish booting before anything tries to push
# a stream to it.
sleep 2

# 2. Loop the sample video into MediaMTX as the RTSP source, in the background.
#    This replaces the physical webcam — a deployed server has no camera,
#    so this looping file IS the "camera feed" as far as the rest of the
#    pipeline is concerned.
ffmpeg -re -stream_loop -1 -i playlist.mp4 -c:v libx264 -f rtsp rtsp://localhost:8554/mystream &

# Give ffmpeg a moment to start actually pushing frames before the app
# tries to pull them.
sleep 2

# 3. Run the FastAPI server in the FOREGROUND (no "&" here).
#    "exec" replaces this script process with uvicorn directly, and being
#    in the foreground is what keeps the container alive — if nothing is
#    running in the foreground, the container thinks it's done and exits.
#    ${PORT:-8000} means "use the PORT the hosting platform assigns, or
#    fall back to 8000 if none is set" — Render/Railway pick their own
#    port at deploy time, so we can't hardcode 8000 here.
exec uvicorn video_server:app --host 0.0.0.0 --port ${PORT:-8000}
