---
name: capcut
description: Edit in CapCut Web (capcut.com/editor) by controlling the browser — upload footage, import Thai subtitles as 1, 2 or 3 words at a time (CapCut-style short captions), apply caption styles, Thai fonts, and caption animations to all clips, then export. Use when the user mentions CapCut, แคปคัท, ซับทีละคำ, ซับ 1 คำ / 2 คำ / 3 คำ, สไตล์ซับ CapCut, or wants the edit to stay editable in CapCut. Needs a browser-control tool (Claude in Chrome, Playwright MCP, or similar).
---

# CapCut Web ผ่าน browser control

ตอบผู้ใช้เป็นภาษาไทย ถ้าผู้ใช้ไม่ได้พิมพ์ภาษาอื่นมา

**หลักการประหยัด token:** งานที่ทำในเครื่องได้ (ตัดช่วงเงียบ, ถอดเสียง, แบ่งซับ 1-2-3 คำ) ให้ทำในเครื่องก่อน แล้วค่อยใช้ CapCut แค่ **อัปโหลด → ใส่สไตล์/แอนิเมชัน → export** อย่าใช้ Auto captions ของ CapCut (ต้องจ่ายเงิน และภาษาไทยแย่กว่า) ใช้ JS helper ด้านล่างหาตำแหน่งปุ่ม แทนการจับภาพหน้าจอแล้วเดา

## กฎความปลอดภัย

- **ห้ามล็อกอินแทนผู้ใช้** ห้ามพิมพ์อีเมล/รหัสผ่าน ถ้าหน้า "Welcome to CapCut" ขึ้นมา ให้ผู้ใช้ล็อกอินเองแล้วบอกให้ทำต่อ
- โหมด guest (ไม่ล็อกอิน) แก้ไขได้ทุกอย่าง แต่ **Export ต้องล็อกอิน** และโปรเจกต์ไม่ถูกเก็บถาวร แจ้งผู้ใช้ก่อนเริ่มงาน
- ไอคอนเพชร 💎 = ฟีเจอร์เสียเงิน ห้ามกด เว้นแต่ผู้ใช้สั่ง
- อัปโหลดไฟล์ขึ้น CapCut = ส่งไฟล์ขึ้น cloud ของ ByteDance ถามก่อนถ้าคลิปเป็นงานลับ/ข้อมูลส่วนตัว
- ห้ามกด Share / โพสต์ลง TikTok เองโดยไม่ได้รับคำสั่ง

## 1. เตรียมไฟล์ในเครื่อง

```bash
# (ถ้าต้องการ) ตัดช่วงเงียบ → ดู skill cut-silence
# ถอดเสียง + ตรวจคำผิด → ดู skill thai-subtitles ขั้น 2–4 ได้ th.srt
python3 ../thai-subtitles/scripts/thai_srt.py th.srt --words 2 -o capcut-2w.srt   # 1, 2 หรือ 3 คำต่อซับ
```

`--words 1` เด้งทีละคำ (เร็ว ต้องการสมาธิสูง เหมาะ hook 3 วิแรก), `2` สมดุลที่สุดสำหรับภาษาไทย, `3` อ่านง่ายสำหรับคลิปยาว ตัดคำด้วย pythainlp จึงไม่ขาดกลางคำ

## 2. เปิด editor และอัปโหลด

1. ไปที่ `https://www.capcut.com/editor` (โปรเจกต์ใหม่) หรือ `https://www.capcut.com/my-edit` (โปรเจกต์เดิม ต้องล็อกอิน)
2. ถ้ามี dialog "Welcome to CapCut" แต่ผู้ใช้ยอมใช้โหมด guest: กดปุ่ม ✕ มุมขวาบนของ dialog
3. ปิด tooltip แนะนำ (ปุ่ม `OK` / `Next` / ✕) ที่ทับหน้าจอ
4. **อย่ากดปุ่ม Upload** (จะเปิด file picker ของระบบที่ควบคุมไม่ได้) ให้ส่งไฟล์เข้า `<input type=file>` โดยตรง:

| ต้องการ | input (เลือกจาก `accept`) | อยู่ที่ |
|---|---|---|
| วิดีโอลง timeline ทันที | `accept` เริ่มด้วย `video/mp4,video/mov` (single) | canvas กลาง "Click to upload" (มีเฉพาะโปรเจกต์ว่าง) |
| วิดีโอ/รูป/เสียงเข้าคลัง | `accept` เริ่มด้วย `image/*,...video/*` (multiple) | แผง Media |
| ไฟล์ซับ | `accept=".srt,.ass,.lrc"` | แผง Captions (ต้องเปิดแผงก่อน input ถึงจะมี) |

ใช้ `find` หา ref ของ input แล้วใช้ tool อัปโหลดไฟล์ (Claude in Chrome: `file_upload`, ≤ 10 MB ต่อครั้ง; ไฟล์ใหญ่กว่านั้นให้ผู้ใช้ลากเอง)

## 3. นำเข้าซับ

1. แถบซ้าย → `Captions` → ปุ่ม 4 อัน: Auto captions 💎 / Manual captions / **Upload caption file** / Auto lyrics
2. อัปโหลด `capcut-2w.srt` เข้า input `.srt,.ass,.lrc` → ซับขึ้นเป็น track สีส้มบน timeline และรายการซับในแผงซ้าย (แก้ข้อความทีละอันได้ในรายการ)
3. คลิกซับใดก็ได้ใน preview หรือรายการ เพื่อเปิดแถบขวา: `Presets`, `Basic`, `Text to speech`, `AI avatars`, `Animation`, `Motion tracking`

## 4. สไตล์ซับ

| แผงขวา | มีอะไร | Apply to all |
|---|---|---|
| `Presets` → `Styles` | กริดสไตล์ตัวอักษร (ขาว/ขอบดำ, พื้นเหลือง, นีออน ฯลฯ) | ใช้กับทุกซับอัตโนมัติ |
| `Presets` → `Templates` | ซับสำเร็จรูปมีแอนิเมชัน | ยังไม่ได้ทดสอบ ตรวจด้วยการเลื่อนไปซับอื่น |
| `Basic` | ข้อความ, ฟอนต์, ขนาด, B/I/U, จัดวาง, Fill/Stroke/Background/Shadow, Glow | checkbox ล่างสุด ติ๊กอยู่แล้ว |
| `Animation` → `In` / `Out` / `Loop` / `Captions` | แท็บ Captions = คอมโบซับ เช่น `Pop-Up Combo`, `Caption Flow`, `Highlight Slide`, `Drop Bounce`, `Wave Pop-In`, `Bracket Typing` | checkbox ล่างสุด **ไม่ได้ติ๊ก ต้องติ๊กเอง** |

**ฟอนต์ไทยใน CapCut** (dropdown `Default` ใน Basic, พิมพ์ค้นหาไม่ได้ ต้องเลื่อนหา): `ใบจามจุรี-Bd` (แนะนำสำหรับซับ), `ใบจามจุรี`, `สระบุญ-Rg`, `อนุพันธ์`, `ฟ้าหวัง-Bd`, `นิรมิต`, `ครุบ`, `KoHo-Md`

**ขนาด:** ช่องตัวเลขขวาของ dropdown ฟอนต์ (ค่าเริ่มต้น 6) triple-click แล้วพิมพ์เลข + Enter แนวนอนใช้ 10–14, แนวตั้ง 14–18

**สูตรซับ CapCut ยอดนิยม:**
1. ป้ายเหลือง (ทดสอบแล้ว): Presets → Styles แถว 3 ช่อง 1 → Basic ฟอนต์ `ใบจามจุรี-Bd` ขนาด 12
2. เด้งทีละคำ (ทดสอบแล้วกับ `--words 2`): SRT `--words 1` + Animation → Captions → `Pop-Up Combo` + ติ๊ก Apply to all
3. Karaoke (ยังไม่ได้ทดสอบ): SRT `--words 3` + Animation → Captions → `Highlight Slide`

## 5. เครื่องมืออื่นใน CapCut (แถบซ้าย)

`Media` · `Templates` · `Elements` (สติกเกอร์/สต็อก) · `Audio` (เพลง/เสียงประกอบ) · `Text` · `Captions` · `Transcript` (ตัดต่อจากข้อความ, ยังไม่ได้ทดสอบ) · `Effects` · `Transitions` · `Filters` · `Brand kit` · `Plugins`

เลือกคลิปวิดีโอบน timeline แถบขวาจะเป็น `Basic` · `Background` · `Smart tools` · `Audio` · `Animation` · `Speed` เครื่องมือบน timeline: split, delete, crop, flip และปุ่ม `Ratio` มุมซ้ายบนของ canvas เปลี่ยนเป็น 9:16

ถ้าต้องใช้ฟีเจอร์ที่ไม่มีในตารางนี้: เปิดแผงนั้นแล้วอ่านชื่อด้วย `listText()` ก่อน ค่อยจับภาพหน้าจอเมื่อจำเป็นจริงๆ

## 6. Export

ปุ่ม `Export` มุมขวาบน → ถ้าไม่ได้ล็อกอินจะขึ้น "Welcome to CapCut" → **หยุด** ให้ผู้ใช้ล็อกอินเอง (ความคืบหน้าในโหมด guest ยังอยู่ในแท็บเดิม) หลังล็อกอินให้ทำตามหน้าต่าง Export (ขั้นนี้ยังไม่ได้ทดสอบ อ่านตัวเลือกด้วย `listText()`) ตั้ง 1080p และถามผู้ใช้ก่อนดาวน์โหลดไฟล์

## JS helpers (รันผ่าน javascript tool)

CapCut ใช้ CSS class แบบสุ่ม (`file-input-DTohfp`) ห้ามจำ class ให้หาจากข้อความ/`accept` แทน พิกัดใน DOM เป็น CSS px ต้องคูณ `k = ความกว้างภาพหน้าจอ / innerWidth` ก่อนคลิก

```js
// 1) รายการ file input
[...document.querySelectorAll('input[type=file]')].map((i, n) => n + ': ' + i.accept.slice(0, 40))

// 2) หาพิกัดคลิกจากข้อความที่เห็นบนจอ (SHOT_W = ความกว้างภาพหน้าจอ เช่น 1568)
const at = (t, SHOT_W) => { const k = SHOT_W / innerWidth;
  const e = [...document.querySelectorAll('div,span,label,button')].find(e => e.children.length === 0 && e.offsetParent && e.innerText?.trim() === t);
  if (!e) return null; e.scrollIntoView({ block: 'center' }); const r = e.getBoundingClientRect();
  return [Math.round((r.left + r.width / 2) * k), Math.round((r.top + r.height / 2) * k)]; };
at('Pop-Up Combo', 1568)   // ชื่อแอนิเมชันอยู่ใต้ thumbnail: คลิกสูงขึ้นไป ~40px

// 3) ข้อความทั้งหมดในแผงขวา (x > 1260 CSS px) — ใช้แทน screenshot
const listText = (x0 = 1260) => [...new Set([...document.querySelectorAll('div,span,label')]
  .filter(e => e.children.length === 0 && e.offsetParent && e.getBoundingClientRect().left > x0 && e.innerText?.trim().length < 30)
  .map(e => e.innerText.trim()))];

// 4) เลือกฟอนต์ (เปิด dropdown ฟอนต์ก่อน) แล้วคลิกพิกัดที่ได้
const font = (name, SHOT_W) => { const n = [...document.querySelectorAll('.font-item-name, .font-item-text')].find(e => e.innerText.trim() === name);
  const o = n.closest('.font-item'); o.scrollIntoView({ block: 'center' }); const r = o.getBoundingClientRect(), k = SHOT_W / innerWidth;
  return [Math.round((r.left + r.width / 2) * k), Math.round((r.top + r.height / 2) * k)]; };
```

> UI ของ CapCut เปลี่ยนบ่อย ถ้าชื่อปุ่มในไฟล์นี้หาไม่เจอ ให้ใช้ `listText()` ดูของจริง แล้วแจ้งผู้ใช้ว่า skill ควรอัปเดต (ตรวจสอบล่าสุด: 17 ก.ย. 2026)
