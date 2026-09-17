<div align="center">

<img src="assets/banner.png" alt="tadtor ตัดต่อ — ปลั๊กอินตัดต่อวิดีโอภาษาไทย สำหรับ Claude Code และ Codex" width="100%">

<br>

**สั่งตัดต่อวิดีโอเป็นภาษาไทย ให้ AI ทำซับไทย ตัดช่วงเงียบ และทำคลิปสั้นให้จบในแชตเดียว**

[![License: MIT](https://img.shields.io/badge/License-MIT-E4572E?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/Boom-Vitt/tadtor/test.yml?branch=main&style=flat-square&label=tests)](https://github.com/Boom-Vitt/tadtor/actions)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square&logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![Codex](https://img.shields.io/badge/Codex-plugin-000000?style=flat-square&logo=openai&logoColor=white)](https://developers.openai.com/codex)
[![ffmpeg](https://img.shields.io/badge/powered_by-ffmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![GitHub stars](https://img.shields.io/github/stars/Boom-Vitt/tadtor?style=flat-square&color=yellow)](https://github.com/Boom-Vitt/tadtor/stargazers)

**ไทย** · [English](README.en.md)

[ติดตั้ง](#-ติดตั้ง) · [ความสามารถ](#-ความสามารถ) · [ตัวอย่างคำสั่ง](#-ตัวอย่างคำสั่ง) · [ร่วมพัฒนา](#-ร่วมพัฒนา)

</div>

---

## 🤔 ทำไมต้อง tadtor

AI ตัดต่อทั่วไปถูกออกแบบมาสำหรับภาษาอังกฤษ พอเจอภาษาไทยก็มีปัญหาเดิมๆ:

- **ซับไทยขาดกลางคำ** เพราะภาษาไทยไม่เว้นวรรคระหว่างคำ
- **นับความยาวบรรทัดผิด** เพราะนับสระบน/ล่างและวรรณยุกต์เป็นตัวอักษรด้วย
- **ถอดเสียงไม่ได้ `--language th`** เลยกลายเป็นภาษาอังกฤษเมื่อพูดทับศัพท์เยอะ
- **ตัด "เอ่อ อ่า อืม" ไม่ได้** เพราะไม่รู้จักคำเติมภาษาไทย

tadtor รวมความรู้ตรงนี้ไว้เป็น skills ที่ Claude Code และ Codex ใช้ได้ทันที ข้างในเป็นแค่ `ffmpeg` + Whisper + สคริปต์ Python สั้นๆ ไม่ต้องสมัครบริการ ไม่ต้องอัปโหลดวิดีโอขึ้นคลาวด์

### ก่อน / หลัง

<table>
<tr><th>❌ ตัดบรรทัดตามความยาวอย่างเดียว</th><th>✅ ผ่าน <code>thai_srt.py</code></th></tr>
<tr><td>

```
เอ่อ สวัสดีครับทุกคน วันนี้
เราจะมาสอนตัดต่อวิดีโอภา
ษาไทยด้วยปัญญาประดิษฐ์แบ
บง่ายๆ กันนะครับ
```

</td><td>

```
สวัสดีครับทุกคน วันนี้เราจะ
มาสอนตัดต่อวิดีโอภาษาไทย

ด้วยปัญญาประดิษฐ์แบบง่ายๆ
กันนะครับ
```

</td></tr>
</table>

## ✨ ความสามารถ

| Skill | ทำอะไร | ลองพิมพ์ |
|---|---|---|
| 🎞️ **`thai-subtitles`** | ถอดเสียงไทย → SRT → จัดบรรทัดตามคำ → ตรวจคำผิด → ฝังซับด้วยฟอนต์ไทย | *"ทำซับไทยให้ vlog.mp4 ฟอนต์ Kanit"* |
| ✂️ **`cut-silence`** | ตัดช่วงเงียบอัตโนมัติ, ตัดคำว่า เอ่อ/อ่า/อืม และประโยคที่พูดซ้ำ | *"ตัดช่วงเงียบกับคำว่าเอ่อออกจาก podcast.mp4"* |
| 📱 **`thai-shorts`** | หาช่วงเด็ดจากคลิปยาว → ตัดเป็น 9:16 → ซับตัวใหญ่ → เขียนแคปชัน/แฮชแท็กไทย, ทำ YouTube chapters | *"หา 3 ช่วงเด็ดจาก live.mp4 ทำเป็น TikTok"* |

> [!TIP]
> skills ทำงานต่อกันได้ เช่น *"ตัดช่วงเงียบ แล้วทำซับไทยฝังลงไป แล้วตัดเป็นคลิปสั้น 2 คลิป"*

## 📦 ติดตั้ง

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude plugin marketplace add Boom-Vitt/tadtor
claude plugin install tadtor@tadtor
```

หรือพิมพ์ในแชต Claude Code: `/plugin marketplace add Boom-Vitt/tadtor` แล้ว `/plugin install tadtor@tadtor`

</details>

<details open>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add Boom-Vitt/tadtor
codex plugin add tadtor@tadtor
```

</details>

<details>
<summary><b>เครื่องมืออื่น (Cursor, Gemini CLI ฯลฯ) หรือใช้แค่ skills</b></summary>

คัดลอกโฟลเดอร์ใน [`skills/`](skills) ไปไว้ที่โฟลเดอร์ skills ของเครื่องมือนั้น เช่น `~/.claude/skills/`, `~/.codex/skills/` หรือ `.agents/skills/` ในโปรเจกต์

```bash
git clone https://github.com/Boom-Vitt/tadtor
cp -r tadtor/skills/* ~/.claude/skills/
```

</details>

### สิ่งที่ต้องมีในเครื่อง

| โปรแกรม | จำเป็น | ติดตั้ง (macOS) |
|---|---|---|
| `ffmpeg` (มี libass สำหรับฝังซับ) | ✅ | `brew install ffmpeg-full` |
| Python 3.9+ | ✅ | มีอยู่แล้วบน macOS |
| Whisper ตัวใดตัวหนึ่ง | สำหรับถอดเสียง | `pip install mlx-whisper` (Apple Silicon) หรือ `pip install whisper-ctranslate2` |
| `pythainlp` | แนะนำมาก | `pip install pythainlp` |
| ฟอนต์ไทย เช่น Kanit, Prompt, Sarabun | สำหรับฝังซับ | [Google Fonts](https://fonts.google.com/?subset=thai) |

> [!NOTE]
> ไม่ต้องติดตั้งเองทั้งหมดก็ได้ AI จะเช็กและบอกว่าขาดอะไรตอนเริ่มใช้งาน

## 💬 ตัวอย่างคำสั่ง

```text
ทำซับไทยให้ interview.mp4 แก้ชื่อ "คุณสมชาย" กับ "Claude" ให้สะกดถูก แล้วฝังซับสีขาวขอบดำ
```

```text
ตัดช่วงเงียบใน tutorial.mov ให้กระชับ แต่อย่าตัดท้ายคำ ขอดูก่อนว่าจะตัดกี่วินาที
```

```text
podcast-ep12.mp4 ยาว 1 ชั่วโมง หาช่วงที่น่าจะไวรัล 5 ช่วง ทำเป็น Reels พร้อมแคปชัน
```

```text
ทำ YouTube chapters ภาษาไทยให้ lecture.mp4
```

## 🧰 ใช้สคริปต์เองโดยไม่ผ่าน AI

```bash
# จัดบรรทัดซับไทย (30 ตัวต่อบรรทัด, สูงสุด 2 บรรทัด, ลบ เอ่อ/อ่า/อืม)
python3 skills/thai-subtitles/scripts/thai_srt.py in.srt -o out.srt --max-chars 30 --strip-fillers

# ดูว่าจะตัดช่วงเงียบตรงไหน แล้วค่อย render
python3 skills/cut-silence/scripts/cut_silence.py in.mp4 --dry-run
python3 skills/cut-silence/scripts/cut_silence.py in.mp4 -o out.mp4 --noise -35 --pad 0.15
```

## 🗂️ โครงสร้าง

```
tadtor/
├── .claude-plugin/        # manifest สำหรับ Claude Code
├── .codex-plugin/         # manifest สำหรับ Codex
├── .agents/plugins/       # marketplace สำหรับ Codex
├── skills/
│   ├── thai-subtitles/    # SKILL.md + scripts/thai_srt.py
│   ├── cut-silence/       # SKILL.md + scripts/cut_silence.py
│   └── thai-shorts/       # SKILL.md
└── tests/test_scripts.py  # python3 tests/test_scripts.py
```

## 🗺️ แผนต่อไป

- [ ] ซับคาราโอเกะ (ไฮไลต์ทีละคำ) สำหรับคลิปสั้น
- [ ] แปลซับ ไทย ⇄ อังกฤษ
- [ ] ตรวจจับใบหน้าเพื่อ crop 9:16 อัตโนมัติ
- [ ] export timeline ไป DaVinci Resolve / Premiere (EDL/FCPXML)

มีไอเดีย? [เปิด issue](https://github.com/Boom-Vitt/tadtor/issues) ได้เลย

## 🤝 ร่วมพัฒนา

ยินดีรับ PR ทุกขนาด ตั้งแต่แก้คำผิดใน SKILL.md ไปจนถึงเพิ่ม skill ใหม่

1. Fork แล้วสร้าง branch
2. แก้ไข แล้วรัน `python3 tests/test_scripts.py`
3. ถ้าแก้ manifest ให้รัน `claude plugin validate .`
4. เปิด PR อธิบายว่าแก้อะไร (ภาษาไทยหรืออังกฤษก็ได้)

skill ที่ดีควร: สั้น, บอกคำสั่งที่รันได้จริง, บอกว่าเมื่อไหร่ต้องถามผู้ใช้ก่อน, และไม่เขียนทับไฟล์ต้นฉบับ

## ⭐ Star History

<a href="https://star-history.com/#Boom-Vitt/tadtor&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Boom-Vitt/tadtor&type=Date&theme=dark">
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Boom-Vitt/tadtor&type=Date">
  </picture>
</a>

## 👥 ผู้ร่วมพัฒนา

<a href="https://github.com/Boom-Vitt/tadtor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Boom-Vitt/tadtor" alt="contributors">
</a>

## 📄 License

[MIT](LICENSE) ใช้ แก้ แจก ได้ฟรี รวมถึงงานเชิงพาณิชย์

<div align="center">
<sub>ทำด้วย ❤️ เพื่อคนทำคอนเทนต์ไทย · ถ้ามีประโยชน์ ฝากกด ⭐ ด้วยนะครับ</sub>
</div>
