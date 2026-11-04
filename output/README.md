# output/

## ลิงก์ผลงาน

- Dashboard (เปิดในเครื่อง): `output/dashboard.html` · ดาวน์โหลดแล้วเปิดด้วยเบราว์เซอร์
- Dashboard บน claude.ai: https://claude.ai/artifact/WmQ8WDvSFsgnc6oRuC7TDM (เป็น private จนกว่าเจ้าของจะกดแชร์)

## ไฟล์ข้อมูล (`output/data/`)

| ไฟล์ | เนื้อหา |
|---|---|
| `universe.csv` | หุ้น Top 50 สหรัฐฯ ตาม market cap (TradingView, 2026-11-04) |
| `events.csv` | ปฏิทินงบ + มาโคร 4 พ.ย. 2026 – 4 ม.ค. 2027 พร้อมที่มาทุกแถว |
| `spillover.csv` | สถิติรายคู่ บริษัทที่ประกาศงบ → peer (8 ไตรมาส) |
| `spillover_reporters.csv` | บริษัทที่ใช้วิเคราะห์ 50 ตัว: ประกาศงบแล้วในเดือนที่ผ่านมา (reported) หรือกำลังจะประกาศ (upcoming) พร้อมการขยับของหุ้นตัวเองในรอบล่าสุด |
| `spillover_events.csv` | excess return รายไตรมาสรายหุ้น พร้อมลิงก์ 8-K บน EDGAR |

สร้างใหม่ได้ด้วย `scripts/build_universe.py` → `build_events.py` → `spillover.py` → `build_dashboard.py`
ข้อมูลดิบที่ดึงมา (ราคารายวัน, JSON จาก EDGAR) อยู่ใน `work/` ซึ่งไม่ขึ้น git
