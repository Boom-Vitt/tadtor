<div align="center">

<img src="assets/banner.png" alt="tadtor — Thai-first video editing plugin for Claude Code and Codex" width="100%">

**Edit videos by chatting in Thai: Thai subtitles, silence cutting, and vertical shorts for Claude Code & Codex.**

[![License: MIT](https://img.shields.io/badge/License-MIT-E4572E?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/Boom-Vitt/tadtor/test.yml?branch=main&style=flat-square&label=tests)](https://github.com/Boom-Vitt/tadtor/actions)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square&logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![Codex](https://img.shields.io/badge/Codex-plugin-000000?style=flat-square&logo=openai&logoColor=white)](https://developers.openai.com/codex)

[ไทย](README.md) · **English**

</div>

---

*tadtor* (ตัดต่อ) means "to edit" in Thai. Most AI video tooling assumes English, and Thai breaks it: Thai has no spaces between words, so subtitles get cut mid-word, and vowel/tone marks get counted toward line width. This plugin packages the Thai-specific know-how as agent skills on top of plain `ffmpeg` + Whisper. Everything runs locally.

## Skills

| Skill | What it does |
|---|---|
| `thai-subtitles` | Transcribe Thai speech → SRT → word-aware line breaking (`pythainlp`) → proofread → burn in with a Thai font |
| `cut-silence` | Remove silences automatically, plus Thai filler words (เอ่อ/อ่า/อืม) and retakes from word timestamps |
| `thai-shorts` | Find highlights in a long video → cut to 9:16 → big captions → Thai titles & hashtags; YouTube chapters |

## Install

```bash
# Claude Code
claude plugin marketplace add Boom-Vitt/tadtor
claude plugin install tadtor@tadtor

# Codex
codex plugin marketplace add Boom-Vitt/tadtor
codex plugin add tadtor@tadtor
```

Other agents: copy `skills/*` into that agent's skills folder.

**Requirements:** `ffmpeg` built with libass (`brew install ffmpeg-full`), Python 3.9+, a Whisper CLI (`mlx-whisper` or `whisper-ctranslate2`), and `pythainlp` (recommended).

## Contributing

PRs welcome. Run `python3 tests/test_scripts.py` and `claude plugin validate .` before opening one.

## License

[MIT](LICENSE)
