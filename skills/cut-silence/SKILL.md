---
name: cut-silence
description: Remove silences, dead air, and Thai filler words (เอ่อ อ่า อืม) from talking-head videos, podcasts, and screen recordings with ffmpeg — a jump-cut / rough-cut pass. Use when the user says ตัดช่วงเงียบ, ตัดคำว่าเอ่อ, ตัดต่อคร่าวๆ, jump cut, remove silence, tighten the pacing, or wants a shorter edit of a recording.
---

# ตัดช่วงเงียบ / คำฟุ่มเฟือย

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา ไม่เขียนทับไฟล์ต้นฉบับเด็ดขาด

## A. ตัดช่วงเงียบอัตโนมัติ

ดูผลก่อนเสมอ (ไม่ render):

```bash
python3 scripts/cut_silence.py input.mp4 --dry-run
```

ได้ JSON: `duration`, `kept`, `removed`, `keep` (ช่วงวินาทีที่เก็บไว้) สรุปให้ผู้ใช้ว่าจะตัดออกกี่วินาที แล้วค่อย render:

```bash
python3 scripts/cut_silence.py input.mp4 -o cut.mp4
```

ปรับค่า:
| อาการ | แก้ |
|---|---|
| ตัดโดนท้ายคำ/หายใจขาด | `--pad 0.25` |
| ห้องมีเสียงรบกวน ตัดไม่ค่อยได้ | `--noise -30` |
| ตัดถี่เกินไป จังหวะรัว | `--min-silence 1.0` |
| เสียงเบา โดนตัดเป็นเงียบ | `--noise -45` |

## B. ตัดคำฟุ่มเฟือย (เอ่อ อ่า อืม) และประโยคที่พูดผิดซ้ำ

1. ถอดเสียงแบบมี word timestamps (ดู skill `thai-subtitles` ขั้นที่ 2 ใช้ `--output-format json` / `--output_format json`)
2. อ่าน JSON หา:
   - คำเติม: `เอ่อ`, `อ่า`, `อืม`, `เอิ่ม`, และ `แบบ`/`คือ` **เฉพาะ**ตอนที่ใช้เป็นคำเติม ไม่ใช่ในประโยค
   - การพูดซ้ำ/พูดใหม่ (retake) เช่น พูดประโยคเดิมสองครั้ง ให้เก็บครั้งหลัง
3. สร้างช่วงที่จะ **เก็บ** เป็นวินาที แล้วเสนอรายการที่จะตัด (เวลา + ข้อความ) ให้ผู้ใช้ยืนยันก่อน
4. Render:

```bash
python3 scripts/cut_silence.py input.mp4 -o clean.mp4 --keep "0-12.4,13.1-45.8,47.0-90"
```

ถ้าต้องทำซับต่อ ให้ถอดเสียงใหม่จาก `clean.mp4` (timestamp เดิมใช้ไม่ได้แล้ว)

## หมายเหตุ

- สคริปต์ re-encode ทั้งไฟล์ (ตัดแม่นระดับเฟรม) คลิปยาวมากจะใช้เวลา แจ้งผู้ใช้ก่อน
- ถ้าคลิปมีช่วงเพลงประกอบ/B-roll ที่ไม่มีเสียงพูด ให้เตือนว่าช่วงนั้นอาจถูกตัด และใช้ `--keep` แทน
