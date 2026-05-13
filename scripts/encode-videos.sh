#!/usr/bin/env bash
# Re-encode background-video loops to ~1.5 Mbps H.264, no audio.
# Run after scripts/mirror.py to compress freshly-downloaded videos.
# Requires ffmpeg.
set -euo pipefail

VIDEO_DIR="$(cd "$(dirname "$0")/.." && pwd)/src/assets/vendor/video"
cd "$VIDEO_DIR"

mkdir -p _new
for f in *.mp4; do
  echo "encoding $f..."
  ffmpeg -y -i "$f" \
    -c:v libx264 -preset slow -b:v 1500k -maxrate 2000k -bufsize 4M \
    -pix_fmt yuv420p -movflags +faststart -an \
    "_new/$f" 2>&1 | tail -1
  orig=$(wc -c < "$f")
  new=$(wc -c < "_new/$f")
  echo "  $((orig/1024/1024))MB -> $((new/1024/1024))MB"
done

mv _new/*.mp4 .
rmdir _new
echo "Done. Total size:"
du -sh .
