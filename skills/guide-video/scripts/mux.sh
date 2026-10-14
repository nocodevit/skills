#!/bin/sh
# usage: ./mux.sh <video.mp4> <output.mp4> [music file] [music volume, default 0.25]
# Mixes out/sfx.wav (from sfx.py) with optional background music under the video.
set -e
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")
if [ -n "$3" ]; then
  F=$(python3 -c "print(max(0,$D-1.5))")
  ffmpeg -v error -y -i "$1" -i out/sfx.wav -i "$3" -filter_complex \
    "[2:a]atrim=0:$D,afade=t=out:st=$F:d=1.5,volume=${4:-0.25}[m];[1:a]aformat=channel_layouts=stereo[s];[m][s]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$D" -movflags +faststart "$2"
else
  ffmpeg -v error -y -i "$1" -i out/sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t "$D" -movflags +faststart "$2"
fi
echo "$2"
