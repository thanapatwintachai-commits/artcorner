"""_validators.py - ตัวแปลงชนิดข้อมูล (int, float, str, bool) และตัวตรวจสอบข้อมูลนำเข้า

ทุกฟังก์ชันที่นี่ "ไม่โยน error ใส่ผู้ใช้" ยกเว้น fail() ที่ตั้งใจให้ส่งข้อความภาษาไทยกลับไปแสดง
"""
import re

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^0\d{9}$")
ROLES = ("admin", "staff", "customer")  # tuple: ลำดับและค่าคงที่ ห้ามแก้ไข
RENT_FEE = 100   # ค่าพื้นที่ขายของศิลปิน (บาทต่อเดือน)
RENT_DAYS = 30   # อายุสิทธิ์ต่อการจ่าย 1 ครั้ง (วัน)
RENT_KINDS = ("new", "renew")  # สมัครใหม่ / ต่ออายุ
SLIP_MAX = 850000  # ขนาดข้อความรูปสลิปสูงสุด (ตัวอักษร)
TRACK_RE = re.compile(r"^[A-Za-z0-9-]{6,30}$")
COMM_DEFAULT = 10  # ค่าคอมมิชชันตั้งต้น (% ของราคาผลงาน ไม่รวมค่าส่ง)
COMM_MAX = 50      # ตั้งได้สูงสุด (%)


class ValidationError(Exception):
    """ข้อผิดพลาดที่ตั้งใจให้ผู้ใช้เห็น (เป็นข้อความภาษาไทยที่เข้าใจได้)"""


def fail(message):
    """หยุดการทำงานและส่งข้อความนี้กลับไปบอกผู้ใช้"""
    raise ValidationError(message)


def to_str(value):
    """แปลงเป็น str และตัดช่องว่างหัวท้าย (None -> ข้อความว่าง)"""
    if value is None:
        return ""
    return str(value).strip()


def is_int(value):
    """True ถ้าเป็นจำนวนเต็มจริงๆ (bool ไม่นับ เพราะ True == 1 ใน Python)"""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and value.is_integer()


def is_number(value):
    """True ถ้าเป็นตัวเลข int หรือ float (bool ไม่นับ)"""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_int(value, default=None):
    """แปลงเป็น int ถ้าแปลงไม่ได้คืน default (ใช้กับข้อมูลที่ผู้ใช้พิมพ์เข้ามา)"""
    if isinstance(value, bool):
        return default
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    if not number.is_integer():
        return default
    return int(number)


def to_float(value, default=None):
    """แปลงเป็น float ถ้าแปลงไม่ได้คืน default"""
    if isinstance(value, bool):
        return default
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return number


def to_bool(value, default=False):
    """แปลงข้อความ/ตัวเลขเป็น bool เช่น 'true', 'yes', '1', 'ใช่' -> True"""
    if isinstance(value, bool):
        return value
    text = to_str(value).lower()
    if text in ("true", "yes", "y", "1", "ใช่"):
        return True
    elif text in ("false", "no", "n", "0", "ไม่"):
        return False
    return default


def valid_email(email):
    """รูปแบบอีเมลถูกต้องหรือไม่"""
    return isinstance(email, str) and EMAIL_RE.match(email) is not None


def valid_phone(phone):
    """เบอร์โทรไทย 10 หลัก ขึ้นต้นด้วย 0"""
    return isinstance(phone, str) and PHONE_RE.match(phone) is not None


def valid_name(name):
    """ชื่อยาว 2-60 ตัวอักษร"""
    return isinstance(name, str) and 2 <= len(name.strip()) and len(name) <= 60


def valid_password(password):
    """รหัสผ่านยาว 6-100 ตัวอักษร"""
    return isinstance(password, str) and 6 <= len(password) <= 100


def valid_role(role):
    """บทบาทต้องเป็น admin / staff / customer เท่านั้น"""
    return role in ROLES


def valid_slip(data):
    """สลิปต้องเป็นรูปภาพ (data URL) และขนาดไม่ใหญ่เกินกำหนด"""
    if not isinstance(data, str):
        return False
    return data.startswith("data:image/") and 100 < len(data) <= SLIP_MAX


def valid_rent_kind(kind):
    """ชนิดใบสมัครต้องเป็น new หรือ renew เท่านั้น"""
    return kind in RENT_KINDS


def rent_active(artist, now_ms):
    """ค่าพื้นที่ขายยังไม่หมดอายุหรือไม่ (ศิลปินเก่าที่ไม่มีวันหมดอายุนับว่ายังใช้ได้)"""
    if not artist:
        return False
    until = artist.get("until")
    if until is None:
        return True
    return is_number(until) and until >= now_ms


def valid_rate(rate):
    """อัตราค่าคอมมิชชันต้องเป็นจำนวนเต็ม 0 ถึง COMM_MAX เปอร์เซ็นต์"""
    return is_int(rate) and 0 <= rate <= COMM_MAX


def calc_commission(base, rate):
    """ค่าคอมมิชชัน (บาท) = base * rate / 100 ปัดเศษครึ่งขึ้น (ต้องตรงกับสูตรฝั่งหน้าเว็บ)"""
    return int(base * rate / 100 + 0.5)


def valid_tracking(text):
    """เลขพัสดุ: ตัวอักษรอังกฤษ/ตัวเลข/ขีด 6-30 ตัว (ตัดช่องว่างหัวท้ายก่อนตรวจ)"""
    return isinstance(text, str) and TRACK_RE.match(text.strip()) is not None
