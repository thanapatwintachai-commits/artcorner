# ArtCorner – ตลาดงานศิลป์นักศึกษา (Python backend)

หน้าเว็บ (HTML/CSS/JS) + ฝั่งเซิร์ฟเวอร์ **Python (Standard Library ล้วน)** ที่รันได้ทั้งในเครื่องและบน Vercel

## โครงสร้างไฟล์
| ไฟล์ | หน้าที่ |
|---|---|
| `api/app.py` | จุดเข้าของ Vercel Function (`POST /api/app`) |
| `api/_logic.py` | รับคำขอ แยกตาม action: register, login, state, passwd, adminUser, sync |
| `api/_rules.py` | กติกาสิทธิ์: ใครเห็นอะไร / เขียนอะไรได้ + ตรวจข้อมูลฝั่งเซิร์ฟเวอร์ (คำนวณยอดซ้ำ ฯลฯ) |
| `api/_auth.py` | แฮชรหัสผ่าน (scrypt+salt), โทเคนล็อกอิน (HMAC-SHA256) |
| `api/_validators.py` | แปลงชนิด int/float/str/bool และตรวจอีเมล เบอร์ ชื่อ รหัสผ่าน |
| `api/_storage.py` | ที่เก็บข้อมูล: ไฟล์ JSON (ในเครื่อง) / Upstash Redis (Vercel) / หน่วยความจำ (ทดสอบ) |
| `server.py` | รันเว็บในเครื่อง |
| `cli.py` | เมนูผู้ดูแลบนหน้าจอ (while วนจนกดออก) + ส่งออก CSV + สำรองไฟล์ |
| `index.html style.css app.js qr.js` | หน้าเว็บ |

## รันในเครื่อง
```
python server.py          # เปิด http://localhost:8000  (เปลี่ยนพอร์ต: python server.py 8001)
python cli.py             # เมนูผู้ดูแล
```
ข้อมูลเก็บที่ `data/artcorner.json` (ปิดแล้วเปิดใหม่ข้อมูลยังอยู่) รหัสลับโทเคนที่ `data/secret.txt`
ตั้งอีเมลแอดมินได้ด้วย `set ADMIN_EMAIL=you@gmail.com` (Windows) ก่อนรัน ถ้าไม่ตั้ง คนแรกที่สมัครจะเป็นแอดมิน

## ขึ้น Vercel
1. Push ทั้งโฟลเดอร์ (ยกเว้น `data/`) ขึ้น GitHub แล้ว Import ที่ Vercel
2. Storage → Create Database → Upstash for Redis → Connect to Project
3. Settings → Environment Variables เพิ่ม `AUTH_SECRET` (สุ่มยาว ≥ 32 ตัว) และ `ADMIN_EMAIL`
4. Redeploy แล้วสมัครด้วยอีเมล `ADMIN_EMAIL` จะได้เป็นแอดมิน
> Vercel เขียนไฟล์ถาวรไม่ได้ จึงใช้ Upstash แทนไฟล์ JSON บนเซิร์ฟเวอร์ (โค้ดเลือกให้เองจากตัวแปรสภาพแวดล้อม)

## จุดที่ใช้อธิบายอาจารย์
- **ตรวจฝั่งเซิร์ฟเวอร์ทุกครั้ง** (`_rules.py`): ลูกค้าแก้ราคา/สถานะ/สิทธิ์ตัวเองไม่ได้ ยอดสั่งซื้อคำนวณซ้ำ ซื้อของที่ขายแล้วไม่ได้
- **ไม่มี Traceback ถึงผู้ใช้**: `handle()` ใน `_logic.py` ดักทุก exception แล้วตอบข้อความไทย
- **ข้อมูลผิดไม่ทำให้ระบบพัง**: ข้อมูลที่ไม่ใช่ JSON, ฟิลด์ผิดชนิด, ไฟล์ข้อมูลเสีย ถูกจัดการหมด
- **log**: ทุกการแก้ไขสำคัญเขียนลง `logs` (แอดมินดูได้) เก็บล่าสุด 500 รายการ
