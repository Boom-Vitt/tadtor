"""Run: python3 tests/test_scripts.py  (the ffmpeg test is skipped when ffmpeg is missing)"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "skills/thai-subtitles/scripts"), os.path.join(ROOT, "skills/cut-silence/scripts")]
import cut_silence  # noqa: E402
import thai_srt  # noqa: E402

SRT = """1
00:00:01,000 --> 00:00:05,000
เอ่อ สวัสดีครับทุกคน วันนี้เราจะมาสอนตัดต่อวิดีโอภาษาไทยด้วยปัญญาประดิษฐ์แบบง่ายๆ กันนะครับ
"""


def test_thai_srt():
    assert thai_srt.width("สวัสดี") == 4  # ั and ี are combining marks
    cues = thai_srt.rewrap(thai_srt.parse(SRT), max_chars=20, max_lines=2, strip_fillers=True)
    assert len(cues) >= 2, cues
    assert cues[0][0] == 1.0 and abs(cues[-1][1] - 5.0) < 1e-6
    for a, b, text in cues:
        assert a < b
        assert "เอ่อ" not in text
        lines = text.split("\n")
        assert len(lines) <= 2
        for line in lines:
            assert thai_srt.width(line) <= 20 or " " not in line, line
            assert unicodedata_ok(line), line
    joined = "".join(t.replace("\n", "") for _, _, t in cues).replace(" ", "")
    assert joined == SRT.split("\n")[2].replace("เอ่อ", "").replace(" ", "")  # no text lost
    back = thai_srt.parse(thai_srt.dump(cues))
    assert [c[2] for c in back] == [c[2] for c in cues]


def unicodedata_ok(line):
    import unicodedata
    return unicodedata.category(line[0]) != "Mn" and line[-1] not in thai_srt.LEADING_VOWELS


def test_keep_ranges():
    r = cut_silence.keep_ranges([(0, 1), (3, 5), (8, None)], total=10, pad=0.1)
    assert r == [(0.9, 3.1), (4.9, 8.1)], r
    assert cut_silence.keep_ranges([], total=4) == [(0.0, 4)]
    assert cut_silence.parse_keep("0-1.5, 2-3") == [(0.0, 1.5), (2.0, 3.0)]


def test_cut_real_video():
    if not shutil.which("ffmpeg"):
        print("skip ffmpeg test")
        return
    d = tempfile.mkdtemp()
    src, dst = os.path.join(d, "in.mp4"), os.path.join(d, "out.mp4")
    # 1s tone, 2s silence, 1s tone
    audio = "aevalsrc='if(between(t,1,3),0,0.5*sin(440*2*PI*t))':d=4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=160x90:d=4",
                    "-f", "lavfi", "-i", audio, "-shortest", src], check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "skills/cut-silence/scripts/cut_silence.py"),
                    src, "-o", dst, "--pad", "0.1"], check=True, capture_output=True)
    got = cut_silence.duration(dst)
    assert 2.0 < got < 2.6, got


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
