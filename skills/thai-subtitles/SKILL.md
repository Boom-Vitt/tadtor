---
name: thai-subtitles
description: Generate, clean up, and burn Thai subtitles (ซับไทย / คำบรรยายภาษาไทย) for a video or audio file — transcribe Thai speech with Whisper, fix Thai line breaks (Thai has no spaces between words), and hard-sub with a Thai font via ffmpeg. Use when the user asks for ซับไทย, ทำซับ, ถอดเสียง, แกะเทป, subtitles, captions, SRT, or burning captions onto a clip in Thai.
---

# ซับไทย (Thai subtitles)

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา

## ขั้นตอน

### 1. เช็กเครื่องมือ

```bash
ffmpeg -version | head -1
ffmpeg -hide_banner -filters | grep -E " (subtitles|ass) "   # ต้องมี ถึงจะฝังซับได้
python3 -c "import pythainlp" 2>/dev/null || pip install pythainlp   # ตัดคำไทย
```

ถ้า ffmpeg ไม่มี filter `subtitles` (ไม่ได้ build กับ libass) บน macOS ให้แนะนำ `brew install ffmpeg-full` แทนการติดตั้งเองแบบเงียบๆ

### 2. ถอดเสียง → SRT

ดึงเสียงออกมาก่อน (เร็วกว่า และ Whisper ต้องการ 16 kHz mono):

```bash
ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 audio.wav
```

เลือกตัวที่มีในเครื่อง ตามลำดับนี้:

| เครื่องมือ | คำสั่ง |
|---|---|
| `mlx-whisper` (Apple Silicon, เร็วสุดบน Mac) | `mlx_whisper audio.wav --model mlx-community/whisper-large-v3-turbo --language th --output-format srt --word-timestamps True` |
| `whisper-ctranslate2` / faster-whisper (NVIDIA/CPU) | `whisper-ctranslate2 audio.wav --model large-v3 --language th --output_format srt --word_timestamps True` |
| `openai-whisper` | `whisper audio.wav --model large-v3 --language th --output_format srt` |

- **ต้องใส่ `--language th` เสมอ** ไม่งั้นช่วงที่พูดทับศัพท์อังกฤษเยอะจะถูกตีเป็นภาษาอังกฤษ
- งานที่เน้นความแม่นภาษาไทย แนะนำโมเดล fine-tune ภาษาไทย เช่น `biodatlab/whisper-th-large-v3-combined` (ใช้ผ่าน transformers)
- ถ้าผู้ใช้ให้รายชื่อเฉพาะ (ชื่อคน/แบรนด์/ศัพท์เทคนิค) ส่งเป็น `--initial_prompt "..."` ช่วยให้สะกดถูก

### 3. จัดบรรทัดซับไทย

Whisper ตัดบรรทัดตามความยาว ทำให้คำไทยขาดกลางคำ ใช้สคริปต์นี้ (อยู่ในโฟลเดอร์เดียวกับไฟล์นี้):

```bash
python3 scripts/thai_srt.py audio.srt -o th.srt --max-chars 30 --strip-fillers
```

- `--max-chars` นับเฉพาะตัวที่กินที่ (สระบน/ล่าง วรรณยุกต์ไม่นับ): แนวนอน 16:9 ≈ 30–38, แนวตั้ง 9:16 ≈ 16–20
- `--strip-fillers` ลบ เอ่อ/อ่า/อืม ออกจากซับ (ไม่ตัดวิดีโอ ถ้าจะตัดเสียงด้วยใช้ skill `cut-silence`)

### 4. ตรวจทานคำผิด (สำคัญ)

อ่าน `th.srt` แล้วแก้เองก่อนฝัง อย่าแก้ timestamp:
- คำพ้องเสียงที่ Whisper ชอบผิด: คะ/ค่ะ, นะคะ/นะค่ะ, ทำไม/ทำไหม, อนุญาต/อนุญาติ, ศัพท์อังกฤษที่ถอดเป็นไทย (เช่น "เอไอ" → "AI" ถ้าผู้ใช้ต้องการ)
- ตัวเลข: ใช้เลขอารบิกเป็นค่าเริ่มต้น
- ไม่ต้องใส่ ฯลฯ หรือจุดท้ายประโยค ซับไทยไม่นิยมใส่ `.`
- ถ้าแก้ข้อความจนยาวขึ้น ให้รัน `thai_srt.py` ซ้ำ

### 5. ฝังซับ (hard-sub)

ฟอนต์ไทยฟรี (OFL จาก Google Fonts): **Kanit**, **Prompt**, **Sarabun**, **Noto Sans Thai** ถ้าเครื่องไม่มี ให้โหลดใส่ `./fonts/` แล้วชี้ `fontsdir`

```bash
ffmpeg -i input.mp4 -vf "subtitles=th.srt:fontsdir=./fonts:force_style='FontName=Kanit,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=40'" -c:a copy output.mp4
```

- ซับไทยมีสระบน/วรรณยุกต์สูง ให้ `MarginV` อย่างน้อย 30 ไม่งั้นบรรทัดบนจะโดนตัด
- คลิปแนวตั้ง: `FontSize=14–16`, `MarginV=120–200` (หลบ UI ของ TikTok/Reels)
- ถ้าผู้ใช้ต้องการซับแยกไฟล์ (soft-sub) ใส่ใน mp4: `ffmpeg -i input.mp4 -i th.srt -c copy -c:s mov_text -metadata:s:s:0 language=tha output.mp4`

### 6. ส่งงาน

บอกผู้ใช้: ไฟล์ที่ได้, ความยาว, จุดที่ไม่แน่ใจการถอดเสียง (ระบุเวลา) ให้เขาตรวจเอง
