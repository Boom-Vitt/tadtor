---
name: edit-video
description: End-to-end Thai video edit from raw footage to a finished MP4 — cut silences and filler words, transcribe Thai, proofread subtitles, add motion graphics (title, lower third, karaoke captions, zooms) with HyperFrames, and export horizontal and/or vertical versions. Use when the user hands over raw footage and says ตัดต่อให้หน่อย, ตัดต่อคลิปนี้, ทำคลิปให้พร้อมโพสต์, edit this video, or anything that needs more than one editing step.
---

# ตัดต่อคลิปเต็มขั้นตอน

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา skill นี้เรียงงานของ skill อื่นในปลั๊กอินเดียวกัน (`cut-silence`, `thai-subtitles`, `thai-motion`, `thai-shorts`) อ่าน SKILL.md ของแต่ละตัวเมื่อถึงขั้นนั้น

## กฎ

- ไม่เขียนทับไฟล์ต้นฉบับ ทำงานในโฟลเดอร์ `<ชื่อคลิป>-edit/`
- หยุดถามผู้ใช้แค่ 2 จุด: **ยืนยันรายการตัด** (ขั้น 2) และ **ดู draft** (ขั้น 6) ที่เหลือทำเลย
- ใช้ path สคริปต์เทียบกับโฟลเดอร์ `skills/` ของปลั๊กอินนี้

## ขั้นตอน

1. **ดูไฟล์**: `ffprobe` ความยาว, ขนาด, fps, มีเสียงไหม ถ้าไม่มีเสียงพูด ข้ามขั้น 2–4
2. **ตัดช่วงเงียบ**: `cut-silence/scripts/cut_silence.py raw.mp4 --dry-run` สรุปว่าจะตัดกี่วินาที ให้ผู้ใช้ยืนยัน แล้ว render เป็น `cut.mp4`
3. **ถอดเสียงจาก `cut.mp4`** (ไม่ใช่ไฟล์ดิบ timestamp จะไม่ตรง) ตาม `thai-subtitles` ขั้น 2
4. **ตรวจทานซับ** ตาม `thai-subtitles` ขั้น 4 เขียนเป็น `th.srt`
5. **โมชั่นกราฟิก**: `thai-motion` ขั้น 2–4 ได้ `motion/` แล้ว render draft
6. **ส่ง draft**: บอกความยาวก่อน/หลัง, จุดซูม, คำที่ไม่แน่ใจ ถามว่าต้องแก้อะไร
7. **Export**: render high quality, ถ้าผู้ใช้ต้องการคลิปสั้นด้วย ใช้ `thai-shorts` (หรือรัน `thai_motion.py --vertical` กับช่วงที่ตัดมา)
8. **สรุปงาน**: ไฟล์ที่ได้ + ขนาด + ความยาว, และแคปชัน/แฮชแท็กถ้าจะโพสต์

## ตัวอย่างผลจริง (ทดสอบแล้ว)

ฟุตเทจ 26.0 วิ → ตัดช่วงเงียบเหลือ 18.8 วิ → whisper large-v3-turbo ถอดเสียง 2.4 วิ → แก้คำผิด 6 จุด → HyperFrames check ผ่าน → render 1080p ใช้เวลา 28 วิ บน Mac mini M4
