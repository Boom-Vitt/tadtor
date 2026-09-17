#!/usr/bin/env python3
"""Re-wrap an SRT file for Thai: break lines at word boundaries, cap line length,
split cues that are too long. Thai has no spaces between words, so plain
width-based wrapping cuts words in half.

Usage: python3 thai_srt.py in.srt -o out.srt [--max-chars 30] [--max-lines 2]

Uses pythainlp for word segmentation when installed (pip install pythainlp),
otherwise falls back to breaking between Thai character clusters.
"""
import argparse
import re
import sys
import unicodedata

LEADING_VOWELS = "เแโใไ"  # written before the consonant, never end a line on them
FILLERS = ("เอ่อ", "อ่า", "อืม", "เอิ่ม", "อ้า")


def width(s):
    """Visible length: Thai vowel/tone marks (Mn) sit above/below and take no width."""
    return sum(1 for c in s if unicodedata.category(c) != "Mn")


def tokens(text):
    try:
        from pythainlp.tokenize import word_tokenize
        return [t for t in word_tokenize(text, engine="newmm") if t]
    except ImportError:
        # ponytail: no dictionary, break at spaces only; install pythainlp for real word breaks
        return re.findall(r"\S+\s*", text)


def clusters(text):
    """Split into chars, never separating a mark from its consonant or a leading vowel from what follows."""
    out = []
    for c in text:
        if out and (unicodedata.category(c) == "Mn" or out[-1][-1] in LEADING_VOWELS):
            out[-1] += c
        else:
            out.append(c)
    return out


def wrap(text, max_chars):
    lines, cur = [], ""
    toks = [t for tok in tokens(text) for t in (clusters(tok) if width(tok) > max_chars else [tok])]
    for tok in toks:
        if cur and width(cur + tok) > max_chars:
            lines.append(cur.strip())
            cur = tok.lstrip()
        else:
            cur += tok
    if cur.strip():
        lines.append(cur.strip())
    return lines


def ts_to_s(ts):
    h, m, rest = ts.strip().replace(".", ",").split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def s_to_ts(x):
    ms = int(round(x * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def parse(srt):
    cues = []
    for block in re.split(r"\n\s*\n", srt.replace("\r\n", "\n").strip()):
        rows = block.strip().split("\n")
        i = next((k for k, r in enumerate(rows) if "-->" in r), None)
        if i is None:
            continue
        a, b = rows[i].split("-->")
        cues.append((ts_to_s(a), ts_to_s(b), "\n".join(rows[i + 1:]).strip()))
    return cues


def rewrap(cues, max_chars=30, max_lines=2, strip_fillers=False):
    out = []
    for start, end, text in cues:
        text = text.replace("\n", " ")
        if strip_fillers:
            for f in FILLERS:
                text = text.replace(f, "")
            text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        lines = wrap(text, max_chars)
        chunks = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)]
        total = sum(width("".join(c)) for c in chunks) or 1
        t = start
        for c in chunks:  # split timing proportional to visible text length
            dur = (end - start) * width("".join(c)) / total
            out.append((t, t + dur, "\n".join(c)))
            t += dur
    return out


def word_times(start, end, text):
    """[(token, start)] with time spread by visible width; whitespace tokens take no time.
    ponytail: proportional timing, not forced alignment; fine for short cues."""
    toks = tokens(text)
    total = sum(width(t.strip()) for t in toks) or 1
    t, out = start, []
    for tok in toks:
        out.append((tok, round(t, 3)))
        t += (end - start) * width(tok.strip()) / total
    return out


def chunk_words(cues, n):
    """CapCut-style short subtitles: every cue becomes cues of n words (1, 2 or 3)."""
    out = []
    for start, end, text in cues:
        words, i = [], -1
        for tok, t in word_times(start, end, text.replace("\n", " ")):
            if tok.strip():
                words.append([tok, t])
                i += 1
            elif words:
                words[i][0] += tok  # keep the space after a word
        for k in range(0, len(words), n):
            group = words[k:k + n]
            stop = words[k + n][1] if k + n < len(words) else end
            out.append((group[0][1], stop, "".join(w for w, _ in group).strip()))
    return out


def dump(cues):
    return "\n".join("%d\n%s --> %s\n%s\n" % (i, s_to_ts(a), s_to_ts(b), t)
                     for i, (a, b, t) in enumerate(cues, 1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("-o", "--output", help="default: stdout")
    p.add_argument("--max-chars", type=int, default=30, help="visible chars per line (default 30, use ~18 for 9:16)")
    p.add_argument("--max-lines", type=int, default=2)
    p.add_argument("--strip-fillers", action="store_true", help="remove เอ่อ/อ่า/อืม")
    p.add_argument("--words", type=int, choices=(1, 2, 3), help="CapCut-style: 1, 2 or 3 words per subtitle")
    a = p.parse_args()
    with open(a.input, encoding="utf-8-sig") as f:
        cues = rewrap(parse(f.read()), a.max_chars, a.max_lines, a.strip_fillers)
    result = dump(chunk_words(cues, a.words) if a.words else cues)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
