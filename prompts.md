# บันทึกขั้นตอน (process log)

> เพิ่ม 1 entry ทุกครั้งก่อน commit ต่อท้ายไฟล์ ห้ามลบของเก่า
> ผู้สอนอ่านไฟล์นี้เพื่อดูวิธีคิดของคุณ ไม่ใช่แค่ผลงานสุดท้าย
> ถ้าใช้ AI ช่วยทำงาน AI จะเขียน entry ให้ตาม AGENTS.md ถ้า commit เอง ให้เขียนเองตามแบบด้านล่าง

---

## รอบ 1 · 2026-10-31

- **ทำอะไร:** clone repo `aia-hw-ati` จาก GitHub, เพิ่ม `homework/` ใน `.gitignore`, ย้าย repo เข้า `AI Investor Alpha/homework/aia-hw-ati` ตามที่ AGENTS.md ระบุ แล้วเปิดเซสชันที่โฟลเดอร์ใหม่
- **เครื่องมือ / model:** Claude Code (Claude Desktop แท็บ Code) · Sonnet 5.5
- **Prompt ที่ใช้:**

```text
clone https://github.com/atiatikul/aia-hw-ati.git
และเพิ่ม homework/ ใน .gitignore
ย้ายครับ
```

- **ผลที่ได้:** ได้ repo ในตำแหน่งที่ถูกต้องและ git ใช้งานได้ ยังขาด: โฟลเดอร์เก่าบน Desktop (`aia-hw-ati`) เหลือเป็นโฟลเดอร์เปล่า ต้องลบเอง และบรรทัด `homework/` ใน `.gitignore` ของ repo นี้อาจไม่จำเป็น เพราะ repo อยู่ใต้ `homework/` เอง
- **ตัดสินใจอะไร และเพราะอะไร:** ย้ายเข้า `homework/` เพราะ AGENTS.md ระบุว่า repo นี้อยู่ที่ `AI Investor Alpha/homework/` เพื่อให้โหลดกติกาของ workspace ด้วย ส่วนการเพิ่ม `homework/` ใน `.gitignore` เป็นคำสั่งของผู้เรียน ยังไม่ทราบว่าตั้งใจให้อยู่ใน repo นี้หรือใน workspace [ยังไม่ยืนยัน]
- **ขั้นต่อไป:** ยืนยันว่า `homework/` ควรอยู่ใน `.gitignore` ของที่ไหน, ลบโฟลเดอร์เปล่าบน Desktop, แล้วเริ่มอ่าน `spec.md` เพื่อทำการบ้าน
