#!/usr/bin/env python3
"""Cut silent parts (or any ranges) out of a video with ffmpeg.

  python3 cut_silence.py in.mp4 -o out.mp4                 # auto: remove silences
  python3 cut_silence.py in.mp4 --dry-run                  # print keep ranges as JSON
  python3 cut_silence.py in.mp4 -o out.mp4 --keep "0-12.5,14.2-30"   # explicit ranges

Needs ffmpeg + ffprobe on PATH. Re-encodes (frame-accurate cuts).
"""
import argparse
import json
import re
import subprocess
import sys


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def has_video(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=index", "-of", "csv=p=0", path], capture_output=True, text=True)
    return bool(out.stdout.strip())


def detect_silences(path, noise_db, min_silence):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          "silencedetect=noise=%sdB:d=%s" % (noise_db, min_silence), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def keep_ranges(silences, total, pad=0.15, min_keep=0.2):
    """Invert silences into ranges to keep; `pad` seconds of breath stay on each side."""
    keep, cur = [], 0.0
    for s, e in silences:
        e = total if e is None else e
        if s - cur > 0:
            keep.append((max(0.0, cur - pad), min(total, s + pad)))
        cur = e
    if total - cur > 0:
        keep.append((max(0.0, cur - pad), total))
    merged = []
    for a, b in keep:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return [(round(a, 3), round(b, 3)) for a, b in merged if b - a >= min_keep]


def parse_keep(s):
    return [tuple(float(x) for x in part.split("-")) for part in s.split(",") if part.strip()]


def render(src, dst, ranges, video=True):
    parts, labels = [], ""
    for i, (a, b) in enumerate(ranges):
        if video:
            parts.append("[0:v]trim=%s:%s,setpts=PTS-STARTPTS[v%d]" % (a, b, i))
            labels += "[v%d]" % i
        parts.append("[0:a]atrim=%s:%s,asetpts=PTS-STARTPTS[a%d]" % (a, b, i))
        labels += "[a%d]" % i
    parts.append("%sconcat=n=%d:v=%d:a=1%s" % (labels, len(ranges), int(video), "[v][a]" if video else "[a]"))
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", src, "-filter_complex", ";".join(parts)]
    cmd += (["-map", "[v]"] if video else []) + ["-map", "[a]", dst]
    subprocess.run(cmd, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.add_argument("--noise", type=float, default=-35, help="silence threshold in dB (default -35; noisy room: -30)")
    p.add_argument("--min-silence", type=float, default=0.6, help="seconds of silence before cutting (default 0.6)")
    p.add_argument("--pad", type=float, default=0.15, help="seconds kept around speech (default 0.15)")
    p.add_argument("--keep", help='explicit ranges "a-b,c-d" in seconds; skips detection')
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    total = duration(a.input)
    ranges = parse_keep(a.keep) if a.keep else keep_ranges(detect_silences(a.input, a.noise, a.min_silence), total, a.pad)
    kept = sum(b - x for x, b in ranges)
    info = {"duration": round(total, 3), "kept": round(kept, 3), "removed": round(total - kept, 3), "keep": ranges}
    if a.dry_run or not a.output:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    if not ranges:
        sys.exit("nothing to keep, try a lower --noise (e.g. -45)")
    render(a.input, a.output, ranges, has_video(a.input))
    print(json.dumps({k: v for k, v in info.items() if k != "keep"}))


if __name__ == "__main__":
    main()
