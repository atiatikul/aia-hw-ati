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

---

## รอบ 2 · 2026-11-04

- **ทำอะไร:** เขียน `spec.md` ครบ 5 หัวข้อ แล้วสร้าง dashboard "Mega-Cap Event Radar" (`output/dashboard.html` + หน้า artifact บน claude.ai) มี 3 แท็บ:
  - (1) ปฏิทินงบและตัวเลขมาโครสหรัฐฯ 4 พ.ย. 2026 – 4 ม.ค. 2027 ของหุ้น Top 50 ตาม market cap
  - (2) การวิเคราะห์ว่างบของบริษัทหนึ่งกระทบหุ้น Top 50 กลุ่มเดียวกันแค่ไหน (8 ไตรมาสล่าสุด) ตอนแรกทำเฉพาะ 13 บริษัทที่กำลังจะประกาศ แล้วขยายให้รวม 37 บริษัทที่ประกาศงบไปแล้วในเดือนที่ผ่านมา พร้อมการ์ดแสดงผลกระทบของงบรอบล่าสุด
  - (3) วิธีคิดและที่มา

  สคริปต์ทั้งหมดอยู่ใน `scripts/` ข้อมูลผลลัพธ์อยู่ใน `output/data/` และย้ายบรรทัด `homework/` จาก `.gitignore` ของ repo นี้ไปไว้ที่ `.gitignore` ของ workspace ตามขั้นที่ 4 ใน README
- **เครื่องมือ / model:** Claude Desktop แท็บ Code · Claude Opus 5.5 · Plan mode ก่อนลงมือ · TradingView MCP · SEC EDGAR API · web-fetch subagent (อ่านหน้า Fed/BLS/BEA และ IR)
- **Prompt ที่ใช้:**

```text
Build the dashboard for my two objectives :
(1) the dashboard for displaying the calendar of important events that will impact the top 50 market capitalization US stocks for the future period for the next 2 months.
(2) analyzing the earning results of a US company that will impact the stocks in the same sector for the top 50 market cap US stocks. Explain the logic and descriptions.
```

```text
edit the item 2 (earning spillover) to include the stocks that have already announced the earning results in the past 1 month.
```

- **ผลที่ได้:**
  - ปฏิทินมี 34 เหตุการณ์ (งบ 13 + มาโคร 21) ทุกแถวมีที่มาและวันที่เข้าถึง วันที่ยังไม่ยืนยันมีป้ายกำกับ
  - Spillover ครอบคลุม 50 บริษัท 300 คู่ ได้ label Strong 15 คู่ เช่น NVDA→AVGO, V↔MA, COST→WMT, LRCX→AMAT
  - คำนวณมือ NVDA→AVGO วันที่ 27 ส.ค. 2026 (AVGO excess +3.83%) ตรงกับสคริปต์
  - เปิดบนมือถือแล้วไม่มี scroll แนวนอน
  - ยังขาด:
    - วันงบของ AVGO, PANW, CRWD (หน้า IR บล็อก) และ MU, CSCO, ORCL (ยังไม่ประกาศ) เป็นค่าประมาณจาก TradingView
    - งบรอบล่าสุดของ AMD และ AMGN (3 พ.ย.) ยังไม่มีราคาปิดของวันตอบสนอง
    - ยังไม่มีภาพหน้าจอใน `output/`
    - ค่าของ EPS surprise ยังไม่ได้ใช้
- **ตัดสินใจอะไร และเพราะอะไร:**
  - ใน Plan mode ผู้เรียนเลือก: วิเคราะห์ spillover ทุกบริษัทที่จะประกาศ (ไม่ใช่กรณีศึกษาตัวเดียว), ปฏิทินมีแค่งบกับมาโคร, แหล่งข้อมูลคือ TradingView + SEC EDGAR + IR + Fed/BLS/BEA + Parallax, ส่งเป็นไฟล์ HTML + ลิงก์ artifact [ผู้เรียนยังไม่ได้ระบุเหตุผลของแต่ละตัวเลือก]
  - ผู้เรียนขอรวมบริษัทที่ประกาศงบไปแล้วในเดือนที่ผ่านมา [ผู้เรียนยังไม่ได้ระบุเหตุผล]
  - ใช้เวลายื่น 8-K Item 2.02 บน EDGAR เป็นเวลาประกาศงบย้อนหลัง เพราะเป็นเอกสารทางการและมีเวลาระดับนาที ทำให้แยกก่อนตลาดเปิดกับหลังปิดได้
  - หักผลตอบแทนของ SPY ออก เพื่อแยกผลของงบออกจากการขยับของทั้งตลาด
  - ตั้งเกณฑ์ label ว่าต้องทิศเดียวกันอย่างน้อย 6 ใน 8 และมี correlation ประกอบ เพราะ 5 ใน 8 ใกล้การโยนเหรียญ
  - ใช้วันงบ DELL จากหน้า IR (24 พ.ย.) แทน TradingView (1 ธ.ค.) เพราะ IR เป็นแหล่งต้นทาง
  - เก็บข้อมูลราคาดิบไว้ใน `work/` (ไม่ขึ้น git) และเผยแพร่เฉพาะผลตอบแทนที่คำนวณแล้ว เพื่อไม่แจกจ่ายข้อมูลราคาของผู้ให้บริการต่อ
  - เรื่อง `.gitignore` ที่ค้างจากรอบ 1: README ยืนยันว่า `homework/` ต้องอยู่ใน `.gitignore` ของ workspace จึงย้ายไปที่นั่น โดยแก้ไฟล์อย่างเดียว ไม่ได้ commit ใน workspace
- **ขั้นต่อไป:**
  - ใส่ชื่อเล่นใน `spec.md` และ README แล้วเขียน `help.md` 3 ข้อ
  - กดแชร์ลิงก์ artifact
  - เพิ่มภาพหน้าจอใน `output/`
  - รันใหม่หลังวันที่ 4 พ.ย. ปิดตลาด เพื่อเก็บผลงบของ AMD และ AMGN
  - พิจารณาเพิ่ม EPS surprise และความสัมพันธ์ข้าม sector (เช่น AMAT กับหุ้นชิป)


---

## รอบ 3 · 2026-11-04

- **ทำอะไร:** กรอกตารางบนสุดของ `README.md` (ชื่อโปรเจกต์, ชื่อเล่น, กลุ่ม, โจทย์ 1 บรรทัด, ลิงก์ผลงาน) และใส่ owner ใน `spec.md`
- **เครื่องมือ / model:** Claude Desktop แท็บ Code · Claude Opus 5.5
- **Prompt ที่ใช้:**

```text
กด Share หน้า artifact ให้ผู้สอนเปิดได้
```

```text
ชื่อเล่น ต๊ะ กลุ่ม 5
```

- **ผลที่ได้:** README มีลิงก์ artifact ให้ผู้สอนกดได้ทันที และมีสำเนา `output/dashboard.html` เผื่อเปิดลิงก์ไม่ได้ ยังขาดชื่อธีมของกลุ่ม (ยังเป็น `[ธีม]`), สถานะงานในตาราง และ `help.md`
- **ตัดสินใจอะไร และเพราะอะไร:** ใส่ลิงก์ artifact ใน README เพราะผู้สอนอ่าน repo เป็นหลัก การแชร์ทำได้จากหน้า artifact เท่านั้น (AI เปลี่ยนสิทธิ์ให้ไม่ได้) จึงให้ผู้เรียนกด Share เองแล้วทดสอบในหน้าต่าง incognito ส่วนธีมกลุ่มยังไม่ได้รับข้อมูล จึงเว้นไว้ ไม่เดา
- **ขั้นต่อไป:** ใส่ธีมกลุ่มและสถานะ, เขียน `help.md` 3 ข้อ, ทดสอบลิงก์ artifact ในหน้าต่าง incognito
