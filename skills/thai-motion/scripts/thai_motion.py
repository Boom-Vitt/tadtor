#!/usr/bin/env python3
"""Build a HyperFrames project that puts Thai motion graphics on top of a video:
kinetic title card, lower third, karaoke captions (word-by-word highlight),
punch-in zooms with a slow push-in for depth, progress bar, and an end CTA.

  python3 thai_motion.py cut.mp4 --srt th.srt -o motion/ \
      --title "ตัดต่อด้วย AI" --title-sub "EP.1" --name "บูม" --role "Content Creator" \
      --zoom 4.5,11.8 --cta "กดติดตามด้วยนะ"
  cd motion && npx hyperframes check && npx hyperframes render --quality high --output final.mp4

Add --vertical for a 1080x1920 (TikTok/Reels/Shorts) canvas.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "thai-subtitles", "scripts"))
import thai_srt  # noqa: E402

TITLE_DUR = 2.8


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def caption_words(cues):
    """Per cue: [(word, start)] with times spread by visible width (whitespace gets no time).
    ponytail: proportional timing, not true word alignment; good enough for karaoke on short cues."""
    out = []
    for a, b, text in cues:
        toks = thai_srt.tokens(text)
        total = sum(thai_srt.width(t.strip()) for t in toks) or 1
        t, words = a, []
        for tok in toks:
            words.append((tok, round(t, 3)))
            t += (b - a) * thai_srt.width(tok.strip()) / total
        out.append((a, b, words))
    return out


def spans(words):
    return "".join(html.escape(w) if not w.strip() else '<span class="w">%s</span>' % html.escape(w)
                   for w in words)


def build(a):
    dur = round(duration(a.video), 3)
    w, h = (1080, 1920) if a.vertical else (1920, 1080)
    # one "line" per cue so the original spaces survive; the browser wraps between word spans
    per_cue = a.max_chars or (32 if a.vertical else 28)
    with open(a.srt, encoding="utf-8-sig") as f:
        cues = thai_srt.rewrap(thai_srt.parse(f.read()), max_chars=per_cue, max_lines=1)
    caps = caption_words(cues)
    ext = os.path.splitext(a.video)[1]

    os.makedirs(os.path.join(a.out, "assets", "fonts"), exist_ok=True)
    shutil.copy(a.video, os.path.join(a.out, "assets", "footage" + ext))
    for f in ("Kanit-Regular.ttf", "Kanit-Bold.ttf", "OFL.txt"):
        shutil.copy(os.path.join(HERE, "..", "assets", "fonts", f), os.path.join(a.out, "assets", "fonts", f))

    title_on = bool(a.title)
    body = []
    if title_on:
        words = thai_srt.tokens(a.title)
        body.append('<section id="title-card" class="clip" data-start="0" data-duration="%s" data-track-index="2">'
                    '<div class="title-inner"><h1 id="title">%s</h1><div id="title-line"></div>%s</div></section>'
                    % (TITLE_DUR, spans(words),
                       '<p id="title-sub">%s</p>' % html.escape(a.title_sub) if a.title_sub else ""))
    lt_at = a.lower_third_at if a.lower_third_at is not None else (TITLE_DUR + 0.4 if title_on else 0.5)
    if a.name:
        body.append('<section id="lt" class="clip" data-start="%s" data-duration="4" data-track-index="3">'
                    '<div id="lt-bar"></div><div id="lt-text"><div id="lt-name">%s</div><div id="lt-role">%s</div></div></section>'
                    % (lt_at, html.escape(a.name), html.escape(a.role or "")))
    for i, (ca, cb, words) in enumerate(caps):
        body.append('<div id="cap-%d" class="cap clip" data-start="%s" data-duration="%s" data-track-index="4"><p>%s</p></div>'
                    % (i, round(ca, 3), round(cb - ca, 3), spans([t for t, _ in words])))
    cta_at = round(max(0.0, dur - 3.0), 3)
    if a.cta:
        body.append('<section id="cta" class="clip" data-start="%s" data-duration="%s" data-track-index="5">'
                    '<div id="cta-pill">%s</div></section>' % (cta_at, round(dur - cta_at, 3), html.escape(a.cta)))

    data = {
        "dur": dur, "title": title_on, "titleDur": TITLE_DUR, "lt": lt_at if a.name else None,
        "cta": cta_at if a.cta else None, "zoom": a.zoom, "accent": a.accent,
        "caps": [{"start": ca, "words": [t for tok, t in words if tok.strip()]} for ca, _, words in caps],
    }
    cap_bottom = 380 if a.vertical else 90
    page = TEMPLATE % {
        "w": w, "h": h, "dur": dur, "ext": ext, "accent": a.accent, "body": "\n    ".join(body),
        "data": json.dumps(data, ensure_ascii=False),
        "title_size": 96 if a.vertical else 120,
        "cap_size": 76 if a.vertical else 62, "cap_bottom": cap_bottom,
        "cap_width": 900 if a.vertical else 1500, "lt_bottom": 1500 if a.vertical else 200,
    }
    with open(os.path.join(a.out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    return dur, len(caps)


TEMPLATE = """<!doctype html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=%(w)s, height=%(h)s" />
  <title>tadtor motion</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face { font-family: "Kanit"; src: url("assets/fonts/Kanit-Regular.ttf") format("truetype"); font-weight: 400; }
    @font-face { font-family: "Kanit"; src: url("assets/fonts/Kanit-Bold.ttf") format("truetype"); font-weight: 700; }
    body { margin: 0; background: #000; font-family: "Kanit", sans-serif; }
    #root { position: relative; width: %(w)spx; height: %(h)spx; overflow: hidden; background: #000; }
    #cam, #push { position: absolute; inset: 0; width: 100%%; height: 100%%; transform-origin: 50%% 42%%; }
    #footage { position: absolute; inset: 0; width: 100%%; height: 100%%; object-fit: cover; }
    #shade { position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.6), rgba(0,0,0,0) 38%%); }
    #title-card { position: absolute; inset: 0; display: grid; place-items: center; background: rgba(10,10,14,.55); }
    .title-inner { width: 100%%; display: flex; flex-direction: column; align-items: center; }
    #title { margin: 0; color: #fff; font-weight: 700; font-size: %(title_size)spx; line-height: 1.3; text-align: center; max-width: 90%%; }
    #title .w { display: inline-block; }
    #title-line { width: 220px; height: 10px; margin-top: 18px; border-radius: 5px; background: %(accent)s; transform-origin: 0 50%%; }
    #title-sub { margin: 20px 0 0; color: rgba(255,255,255,.85); font-size: 44px; letter-spacing: .04em; }
    #lt { position: absolute; left: 90px; bottom: %(lt_bottom)spx; width: 900px; height: 160px; }
    #lt-bar { position: absolute; left: 0; top: 0; width: 14px; height: 160px; background: %(accent)s; transform-origin: 50%% 100%%; }
    #lt-text { position: absolute; left: 40px; top: 10px; width: 840px; overflow: hidden; }
    #lt-name { color: #fff; font-weight: 700; font-size: 64px; line-height: 1.25; text-shadow: 0 4px 18px rgba(0,0,0,.5); }
    #lt-role { color: %(accent)s; font-size: 38px; line-height: 1.3; text-shadow: 0 4px 18px rgba(0,0,0,.5); }
    .cap { position: absolute; left: 0; right: 0; bottom: %(cap_bottom)spx; display: flex; justify-content: center; }
    .cap p { margin: 0; max-width: %(cap_width)spx; text-align: center; color: #fff; font-weight: 700; font-size: %(cap_size)spx;
             line-height: 1.45; paint-order: stroke fill; -webkit-text-stroke: 10px rgba(0,0,0,.85); }
    .cap .w { display: inline-block; }
    #progress { position: absolute; left: 0; bottom: 0; width: 100%%; height: 8px; background: %(accent)s; transform-origin: 0 50%%; }
    #cta { position: absolute; inset: 0; display: flex; justify-content: center; align-items: flex-start; padding-top: 90px; }
    #cta-pill { padding: 18px 44px; border-radius: 999px; background: %(accent)s; color: #111; font-weight: 700; font-size: 48px;
                box-shadow: 0 10px 40px rgba(0,0,0,.35); }
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-width="%(w)s" data-height="%(h)s" data-duration="%(dur)s">
    <div id="cam"><div id="push">
      <video id="footage" src="assets/footage%(ext)s" data-start="0" data-duration="%(dur)s" data-track-index="0" muted playsinline></video>
    </div></div>
    <audio id="footage-audio" src="assets/footage%(ext)s" data-start="0" data-duration="%(dur)s" data-track-index="10" data-volume="1"></audio>
    <div id="shade"></div>
    %(body)s
    <div id="progress"></div>
  </div>
  <script>
    const D = %(data)s;
    const tl = gsap.timeline({ paused: true });
    // depth: slow push-in for the whole clip, punch-in zooms on a separate wrapper
    tl.fromTo("#push", { scale: 1 }, { scale: 1.06, duration: D.dur, ease: "none" }, 0);
    tl.fromTo("#progress", { scaleX: 0 }, { scaleX: 1, duration: D.dur, ease: "none" }, 0);
    D.zoom.forEach((z) => {
      tl.fromTo("#cam", { scale: 1 }, { scale: 1.18, duration: 0.35, ease: "power3.out", immediateRender: false }, z);
      tl.to("#cam", { scale: 1, duration: 0.6, ease: "power2.inOut" }, z + 2.2);
    });
    if (D.title) {
      tl.fromTo("#title .w", { yPercent: 120, autoAlpha: 0, rotation: 4 },
        { yPercent: 0, autoAlpha: 1, rotation: 0, duration: 0.7, stagger: 0.08, ease: "back.out(1.6)" }, 0.15);
      tl.fromTo("#title-line", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power3.out" }, 0.6);
      if (document.querySelector("#title-sub"))
        tl.fromTo("#title-sub", { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5, ease: "power2.out" }, 0.8);
      tl.to(".title-inner", { scale: 1.08, autoAlpha: 0, duration: 0.4, ease: "power2.in" }, D.titleDur - 0.45);
      tl.to("#title-card", { backgroundColor: "rgba(10,10,14,0)", duration: 0.4 }, D.titleDur - 0.45);
    }
    if (D.lt !== null) {
      tl.fromTo("#lt-bar", { scaleY: 0 }, { scaleY: 1, duration: 0.35, ease: "power3.out" }, D.lt);
      tl.fromTo("#lt-name", { xPercent: -105 }, { xPercent: 0, duration: 0.55, ease: "power3.out" }, D.lt + 0.15);
      tl.fromTo("#lt-role", { xPercent: -105 }, { xPercent: 0, duration: 0.55, ease: "power3.out" }, D.lt + 0.28);
      tl.to("#lt-text", { autoAlpha: 0, x: -30, duration: 0.35, ease: "power2.in" }, D.lt + 3.5);
      tl.to("#lt-bar", { scaleY: 0, duration: 0.3, ease: "power2.in" }, D.lt + 3.6);
    }
    D.caps.forEach((c, i) => {
      const words = document.querySelectorAll("#cap-" + i + " .w");
      tl.fromTo("#cap-" + i + " p", { scale: 0.86, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.2, ease: "back.out(2)" }, c.start);
      words.forEach((el, k) => {
        const t = c.words[k];
        tl.set(el, { color: D.accent }, t);
        tl.fromTo(el, { scale: 1 }, { scale: 1.12, duration: 0.09, yoyo: true, repeat: 1, ease: "power1.out", immediateRender: false }, t);
        if (k + 1 < words.length) tl.set(el, { color: "#ffffff" }, c.words[k + 1]);
      });
    });
    if (D.cta !== null) {
      tl.fromTo("#cta-pill", { y: -80, autoAlpha: 0, scale: 0.7 }, { y: 0, autoAlpha: 1, scale: 1, duration: 0.6, ease: "back.out(2)" }, D.cta);
      tl.to("#cta-pill", { scale: 1.07, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }, D.cta + 0.8);
    }
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--srt", required=True, help="Thai SRT, timestamps must match the video")
    p.add_argument("-o", "--out", required=True, help="project directory to create")
    p.add_argument("--title")
    p.add_argument("--title-sub")
    p.add_argument("--name", help="lower third name")
    p.add_argument("--role", help="lower third role")
    p.add_argument("--lower-third-at", type=float)
    p.add_argument("--zoom", default="", help="punch-in times in seconds, e.g. 4.5,11.8")
    p.add_argument("--cta", help="end call-to-action pill, e.g. กดติดตามด้วยนะ")
    p.add_argument("--accent", default="#FFD23F")
    p.add_argument("--vertical", action="store_true", help="1080x1920 canvas")
    p.add_argument("--max-chars", type=int, help="visible chars per caption (default 28, vertical 32 over 2 lines)")
    a = p.parse_args()
    a.zoom = [float(x) for x in a.zoom.split(",") if x.strip()]
    dur, n = build(a)
    print(json.dumps({"project": a.out, "duration": dur, "captions": n}, ensure_ascii=False))


if __name__ == "__main__":
    main()
