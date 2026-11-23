🌐 **ภาษา:** [English](README.md) · [Tiếng Việt](README.vi.md) · [Bahasa Indonesia](README.id.md) · [ภาษาไทย](README.th.md) · [简体中文](README.zh.md)

# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.5.0)

[![Version](https://img.shields.io/badge/Release-v1.5.0%20(31%20APIs)-8B5CF6?style=for-the-badge)](https://github.com/minmin2402/shopeeapi/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**ไลบรารี Native หลายภาษา (`minsign_sdk.dll` — มาตรฐาน C-ABI)** สำหรับเชื่อมต่อระบบอัตโนมัติ Shopee และ Shopee Affiliate เข้ากับทุกภาษาโปรแกรม (`C# .NET`, `Python`, `Node.js / Electron`, `C/C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`) ด้วยไฟล์ **DLL เพียงไฟล์เดียว**:

---

## ความสามารถหลักทั้งหมด (v1.5.0 — 31 APIs)

- **[ใหม่ v1.5.0 — แปลงและย่อลิงก์ Shopee Affiliate (`ConvertAffiliateLink` & `BatchConvertAffiliateLinks`)]:**
  - แปลงลิงก์สินค้า Shopee ปกติ, ลิงก์ติด `aff_id`, `universal-link` หรือลิงก์ย่อ `s.shopee.*` / `shp.ee` ให้เป็นลิงก์ย่อ Affiliate ของคุณ (`https://s.shopee.co.th/...`) รองรับ `subId1..subId5` และแปลงเป็นชุด (Batch) อัตโนมัติ
- **[ใหม่ v1.4.0 — เพิ่มยอดชม Shopee Live แบบ Multi-Thread & WebSocket (`GetLiveSessionDetail`, `BuffLiveView`, `BuffLiveBatch`)]:**
  - จำลองการเชื่อมต่อ WebSocket RFC 6455 ผ่าน Proxy + Android uTLS ส่ง Protobuf `HB_REQ`, ดึงสตรีม FLV/HLS และรายงาน `SZTracker` (`reportPB`)
- **[ใหม่ v1.3.0 — ค้นหาสินค้าด้วยรูปภาพ & AI ตรวจจับวัตถุ (`SearchProductsByImage`, `GetImageBoundingBox`)]:**
  - ค้นหาสินค้าที่เหมือนกันหรือราคาถูกกว่า (`SimilarProducts` / `CheaperOptions`) ผ่าน HTTP โดยตรงไม่ต้องเปิดเบราว์เซอร์
- **[ใหม่ v1.2.0 — Layer-2 Android Device Risk Token (`af-ac-enc-sz-token`)]:**
  - สร้างและแคช Risk Token ผูกกับโปรไฟล์อุปกรณ์ Android ถาวรใน `devices_vault.json`
- **[ใหม่ v1.1.0 — เครื่องมือสำหรับสาย Affiliate]:**
  - **`GetShopNewestProducts`:** ดักจับสินค้าใหม่ล่าสุดของร้านค้าแบบเรียลไทม์พร้อมค่าคอมมิชชัน
  - **`GetShopVideos`:** ดึงวิดีโอของร้านค้าพร้อมลิงก์ดาวน์โหลด `.mp4` **ไม่มีลายน้ำ** และสินค้าที่ปักตะกร้า
- **ดึงข้อมูลสินค้า โปรไฟล์ร้านค้า โค้ดส่วนลด ค้นหาสินค้า และหมวดหมู่ครบ 8 ประเทศ** (`TH`, `VN`, `ID`, `MY`, `PH`, `SG`, `TW`, `BR`) — รองรับทั้งลิงก์เต็มและลิงก์สั้น `https://shopee.co.th/product/{shop_id}/{item_id}`
- **อัปโหลด Shopee Video ผ่าน API 4 ขั้นตอน (`UploadShopeeVideo`)** — ปักตะกร้า Affiliate สูงสุด 6 ชิ้น พร้อมเปลี่ยนค่า Hash `MD5/SHA-256` ของไฟล์ `.mp4` ใน `<10ms`
- **ระบบจำลองอุปกรณ์ถาวร `devices_vault.json` (`AES-256-GCM`)** + **Native `uTLS`** รองรับ Proxy ทุกรูปแบบ

---

## วิธีขอรับ `X-API-Key`

1. เข้าเว็บไซต์: **[https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)** (รองรับภาษาไทย / อังกฤษ / เวียดนาม)
2. สมัครสมาชิกหรือเข้าสู่ระบบด้วย Google
3. เติมเครดิต **Pay-As-You-Go** หรือเลือกแพ็กเกจรายเดือน แล้วคัดลอก **`X-API-Key`** ไปใช้งานได้ทันที

---

## ตัวอย่างใช้งานด่วน (Python)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY_HERE", default_country="TH")

detail = sdk.get_product_detail(
    product_url="https://shopee.co.th/product/1834601441/57811171288",
    proxy="http://user:pass@ip:port",
    country="TH",
)
print("ชื่อสินค้า:", detail["product"]["name"])
print("ราคา:", detail["product"]["price"], "| คลัง:", detail["product"]["stock"])
```

ดูรายการฟังก์ชันทั้ง 31 ตัวได้ที่ [`README.md`](./README.md#complete-api-reference-minsign_sdkdll-v150--31-built-in-functions)
