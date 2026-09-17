---
name: thai-motion
description: Add Thai motion graphics to a video with HyperFrames (HTML → MP4) — kinetic Thai title cards, lower thirds (ชื่อ/ตำแหน่ง), TikTok-style karaoke captions that highlight word by word or show 1/2/3 words at a time (ซับทีละคำ), punch-in zooms and slow push-in for depth, progress bar, and end CTA, rendered with a real Thai font (Kanit). Use when the user asks for โมชั่นกราฟิก, motion graphics, ซับเด้ง/ซับคาราโอเกะ, ไตเติ้ล, lower third, ซูมเข้า, ใส่ลูกเล่น, animated captions, HyperFrames, or wants captions burned without libass.
---

# โมชั่นกราฟิกภาษาไทย (HyperFrames)

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา

HyperFrames เรนเดอร์วิดีโอจาก HTML ด้วย headless Chrome ข้อดีกับภาษาไทย: สระ/วรรณยุกต์วางถูกตำแหน่ง ตัดบรรทัดตามคำได้ และไม่ต้องใช้ ffmpeg ที่มี libass

## 0. เช็กเครื่องมือ

```bash
node -v                                  # ต้อง 22+
npx hyperframes doctor --json | head -40 # ต้องมี FFmpeg, Chrome
python3 -c "import pythainlp" 2>/dev/null || pip install pythainlp
```

## 1. เตรียม input

- วิดีโอที่ตัดเสร็จแล้ว (ตัดช่วงเงียบก่อนด้วย skill `cut-silence` ถ้าต้องการ)
- SRT ภาษาไทยที่ **timestamp ตรงกับวิดีโอนี้** และตรวจคำผิดแล้ว (skill `thai-subtitles` ขั้น 2–4)
- ถามผู้ใช้ (หรือเดาจากบริบทแล้วบอก): หัวเรื่อง, ชื่อ/ตำแหน่งสำหรับ lower third, ข้อความ CTA ตอนจบ, แนวนอนหรือแนวตั้ง

## 2. หาจังหวะซูม (punch-in)

อ่าน SRT แล้วเลือก 1 จุดต่อ 8–15 วินาที ที่เป็นประโยคสำคัญ/มุก/ตัวเลข ใส่เวลาเริ่มของ cue นั้น ห้ามซูมถี่จนเวียนหัว

## 3. สร้างโปรเจกต์

```bash
python3 scripts/thai_motion.py cut.mp4 --srt th.srt -o motion \
  --title "หัวเรื่องคลิป" --title-sub "EP.12 · ชื่อช่อง" \
  --name "ชื่อคนพูด" --role "ตำแหน่ง" \
  --zoom 7.2,21.5 --cta "กดติดตามด้วยนะ" --accent "#FFD23F"
# แนวตั้ง TikTok/Reels/Shorts: เพิ่ม --vertical
# ซับแบบ CapCut ขึ้นทีละ 1, 2 หรือ 3 คำ ตัวใหญ่กลางจอ: เพิ่ม --words 1 (หรือ 2, 3)
```

ทุก option ไม่บังคับ ยกเว้น `--srt` และ `-o` ไม่ใส่ `--title` ก็ไม่มีไตเติ้ล ฯลฯ

| ส่วน | ทำอะไร |
|---|---|
| Title card | คำไทยเด้งขึ้นทีละคำ + เส้น accent (2.8 วินาทีแรก) |
| Lower third | แถบสี + ชื่อ/ตำแหน่งสไลด์เข้า 4 วินาที |
| Karaoke captions | ซับขึ้นทีละ cue, คำที่กำลังพูดเปลี่ยนสี + เด้ง (เวลาต่อคำประมาณจากความยาวคำ) |
| Depth | push-in ช้าๆ ทั้งคลิป + punch-in ตามเวลาใน `--zoom` |
| Progress bar / CTA | แถบความคืบหน้าล่างจอ + ปุ่ม CTA 3 วินาทีสุดท้าย |

ห้ามใช้อีโมจิในข้อความ (headless Chrome ไม่มีฟอนต์อีโมจิ จะออกมาเป็นกรอบว่าง)

## 4. ตรวจ → ดูภาพ → render

```bash
cd motion
npx hyperframes check                        # ต้อง "Check passed" (ครั้งแรกอาจ timeout ให้รันซ้ำ)
npx hyperframes snapshot --at 1.3,4.2,10,20  # เปิดดู snapshots/contact-sheet.jpg ด้วยตาทุกครั้ง
npx hyperframes render --quality draft --output draft.mp4
```

ดู contact sheet ว่า: ตัวอักษรไทยไม่ถูกตัดหัว/ท้าย, ซับไม่ทับ lower third, ไตเติ้ลไม่ขึ้นบรรทัดใหม่แค่คำเดียว แก้ได้ที่ `index.html` โดยตรง แล้ว check ใหม่

ให้ผู้ใช้ดู draft ก่อน ถ้าโอเคค่อย `npx hyperframes render --quality high --output final.mp4` แล้วเช็ก `ffprobe final.mp4`

ถ้าผู้ใช้อยากปรับเองแบบลากวาง: `npx hyperframes preview --background` แล้วส่ง URL ให้

## 5. ปรับแต่งเพิ่ม

`index.html` เป็น HyperFrames composition ธรรมดา (GSAP timeline เดียวที่ `window.__timelines["main"]`) แก้สี ฟอนต์ ตำแหน่ง หรือเพิ่มฉากได้เลย ถ้าต้องการลูกเล่นที่ซับซ้อนกว่านี้ (B-roll, transition, เสียงประกอบ, ducking) ให้ติดตั้ง skills ทางการของ HyperFrames:

```bash
npx skills add heygen-com/hyperframes
```

กฎที่ห้ามพลาดเมื่อแก้ `index.html`:
- ห้ามใส่ `transform` ใน CSS ของ element ที่ GSAP tween (ให้ใช้ `fromTo`)
- ห้ามใช้ `Math.random`, `Date.now`, `repeat: -1`, `<br>` ในข้อความ
- `<audio>` ต้องมี `id` เสมอ ไม่งั้นเสียงหาย
- ฟอนต์ไทยต้องประกาศ `@font-face` ชี้ไฟล์ใน `assets/fonts/` (เครื่อง render ไม่มีฟอนต์ไทยในระบบ)
