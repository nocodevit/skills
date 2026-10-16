#!/bin/sh
# usage: ./mux.sh <video.mp4> <music file> <output.mp4>
# Adds the music track and out/sfx.wav to a rendered video. Run from the project folder.
set -e
D=$(python3 -c "import json;print(json.load(open('out/cues.json'))['duration'])")
F=$(python3 -c "print($D-1.7)")
ffmpeg -v error -y -i "$1" -i "$2" -i out/sfx.wav -filter_complex \
  "[1:a]atrim=0:$D,afade=t=out:st=$F:d=1.7,volume=0.9[m];[2:a]aformat=channel_layouts=stereo,volume=1.0[s];[m][s]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -t "$D" -movflags +faststart "$3"
echo "$3"
