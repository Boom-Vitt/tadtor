---
name: thai-shorts
description: Turn a long Thai video (podcast, live, lecture, vlog) into vertical 9:16 short clips for TikTok, Reels, and YouTube Shorts — find the best moments from the Thai transcript, cut, reframe, add big Thai captions, and write Thai titles/hashtags; also YouTube chapters (สารบัญ) in Thai. Use when the user says ทำคลิปสั้น, ตัดไฮไลต์, ทำ TikTok/Reels/Shorts, แนวตั้ง, 9:16, หาช่วงเด็ด, or ทำ chapter.
---

# คลิปสั้นแนวตั้ง จากวิดีโอยาว

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา

## 1. ถอดเสียงทั้งคลิป

ทำตาม skill `thai-subtitles` ขั้นที่ 1–2 (ได้ `audio.srt`) ไม่ต้องฝังซับ

## 2. หาช่วงเด็ด

อ่าน transcript ทั้งหมด แล้วเสนอ 3–5 ช่วง ความยาว 20–60 วินาที เรียงจากดีที่สุด แต่ละช่วงต้อง:
- **3 วินาทีแรกดึงคน**: เริ่มที่ประโยคที่เป็นคำถาม ข้อเท็จจริงที่น่าตกใจ หรือความเห็นแรงๆ ไม่เริ่มที่ "สวัสดีครับ" หรือ "เอ่อ"
- จบในตัว ฟังรู้เรื่องโดยไม่ต้องดูคลิปเต็ม
- เริ่ม/จบตรงขอบประโยค (ใช้ timestamp จาก SRT)

แสดงเป็นตาราง: `#`, `เริ่ม–จบ`, `ความยาว`, `hook (ประโยคแรก)`, `ทำไมถึงน่าจะปัง` ให้ผู้ใช้เลือกก่อน render

## 3. ตัด + แปลงเป็น 9:16

```bash
# ครอปกลางเฟรม (คนพูดอยู่กลางจอ)
ffmpeg -ss START -to END -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a aac -b:a 160k clip1.mp4

# ภาพทั้งเฟรม + พื้นหลังเบลอ (มีสไลด์/หลายคนในเฟรม)
ffmpeg -ss START -to END -i input.mp4 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -c:a aac -b:a 160k clip1.mp4
```

ถ้าคนพูดไม่ได้อยู่กลาง ให้ดึงเฟรมมาดู (`ffmpeg -ss START -i input.mp4 -frames:v 1 frame.jpg`) แล้วเลื่อน crop x: `crop=ih*9/16:ih:X:0`

## 4. ซับตัวใหญ่แบบคลิปสั้น

ถอดเสียงคลิปที่ตัดแล้วใหม่ (timestamp เริ่มที่ 0) แล้ว:

```bash
python3 ../thai-subtitles/scripts/thai_srt.py clip1.srt -o clip1.th.srt --max-chars 16 --max-lines 2 --strip-fillers
ffmpeg -i clip1.mp4 -vf "subtitles=clip1.th.srt:force_style='FontName=Kanit,Bold=1,FontSize=16,Outline=3,Alignment=2,MarginV=160'" -c:a copy clip1.final.mp4
```

(path สคริปต์อ้างจากโฟลเดอร์ของไฟล์นี้)

## 5. แคปชันโพสต์

ต่อคลิปละ: ชื่อคลิปภาษาไทย 3 แบบ (≤ 60 ตัวอักษร), แคปชัน 1–2 บรรทัด, แฮชแท็ก 5 อัน (ผสมไทย/อังกฤษ) ห้ามแต่งข้อมูลที่ไม่ได้พูดในคลิป

## YouTube chapters (สารบัญ)

ถ้าผู้ใช้ขอ chapter: อ่าน transcript แบ่งตามหัวข้อ ให้รูปแบบที่ YouTube รับ (บรรทัดแรกต้องเป็น `00:00`, อย่างน้อย 3 ช่วง, แต่ละช่วง ≥ 10 วินาที):

```
00:00 เกริ่นนำ
02:15 ...
```
