"""Run: python3 tests/test_scripts.py  (the ffmpeg test is skipped when ffmpeg is missing)"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "skills/thai-subtitles/scripts"), os.path.join(ROOT, "skills/cut-silence/scripts"),
                os.path.join(ROOT, "skills/thai-motion/scripts")]
import cut_silence  # noqa: E402
import thai_motion  # noqa: E402
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

    # motion project from the cut clip; rendering needs Chrome so CI only checks the generated HTML
    srt = os.path.join(d, "th.srt")
    with open(srt, "w", encoding="utf-8") as f:
        f.write("1\n00:00:00,000 --> 00:00:02,000\nสวัสดีค่ะ ทุกคน<b>\n")
    out = os.path.join(d, "motion")
    subprocess.run([sys.executable, os.path.join(ROOT, "skills/thai-motion/scripts/thai_motion.py"), dst, "--srt", srt,
                    "-o", out, "--title", "ทดสอบ", "--name", "บูม", "--zoom", "0.5", "--cta", "กดติดตาม", "--vertical"],
                   check=True, capture_output=True)
    with open(os.path.join(out, "index.html"), encoding="utf-8") as f:
        page = f.read()
    for needle in ('data-composition-id="main"', 'data-width="1080"', 'id="footage-audio"', 'id="cap-0"',
                   'id="lt"', 'id="cta"', '&lt;b&gt;', 'window.__timelines["main"] = tl'):
        assert needle in page, needle
    assert "<b>" not in page.split("<body>")[1]  # SRT text is escaped
    assert os.path.getsize(os.path.join(out, "assets/fonts/Kanit-Bold.ttf")) > 100000


def test_chunk_words():
    cues = [(0.0, 4.0, "สวัสดีค่ะ ทุกคน วันนี้เราจะมาลองตัดต่อ")]
    for n in (1, 2, 3):
        out = thai_srt.chunk_words(cues, n)
        assert out[0][0] == 0.0 and out[-1][1] == 4.0, out
        assert all(a < b for a, b, _ in out) and all(out[i][1] == out[i + 1][0] for i in range(len(out) - 1))
        assert "".join(t for _, _, t in out).replace(" ", "") == cues[0][2].replace(" ", "")  # no text lost
    assert len(thai_srt.chunk_words(cues, 1)) > len(thai_srt.chunk_words(cues, 3))


def test_caption_words():
    (a, b, words), = thai_motion.caption_words([(1.0, 3.0, "กิน ข้าว")])
    times = [t for w, t in words if w.strip()]
    assert times[0] == 1.0 and times == sorted(times) and times[-1] < 3.0, words
    assert "".join(w for w, _ in words) == "กิน ข้าว"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
