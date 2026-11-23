🌐 **Bahasa:** [English](README.md) · [Tiếng Việt](README.vi.md) · [Bahasa Indonesia](README.id.md) · [ภาษาไทย](README.th.md) · [简体中文](README.zh.md)

# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.5.0)

[![Version](https://img.shields.io/badge/Release-v1.5.0%20(31%20APIs)-8B5CF6?style=for-the-badge)](https://github.com/minmin2402/shopeeapi/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**Library inti native lintas bahasa (`minsign_sdk.dll` — Standar C-ABI)** yang memudahkan developer mengintegrasikan seluruh otomasi Shopee & Shopee Affiliate ke dalam aplikasi apa saja (`C# .NET`, `Python`, `Node.js / Electron`, `C/C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`) hanya dengan **1 file DLL**:

---

## Fitur Utama & Kemampuan SDK (v1.5.0)

- **[BARU v1.5.0 — Konverter & Pemendek Link Shopee Affiliate (`ConvertAffiliateLink` & `BatchConvertAffiliateLinks`)]:**
  - Mengubah **link produk Shopee biasa**, **link yang sudah punya `aff_id`**, **`universal-link`**, atau **link pendek `s.shopee.*` / `shp.ee`** langsung menjadi link Affiliate resmi milik Cookie Affiliate Anda (`https://s.shopee.co.id/...`, `https://s.shopee.vn/...`).
  - Mendukung hingga 5 sub-ID tracking (**`subId1..subId5`**), **deteksi negara otomatis**, **konversi massal (batch)**, dan **retry otomatis dengan MinSign + RiskToken**.
- **[BARU v1.4.0 — Shopee Live View Booster & WebSocket Heartbeat (`GetLiveSessionDetail`, `BuffLiveView`, `BuffLiveBatch`)]:**
  - Mendukung **WebSocket RFC 6455 via Proxy + Android uTLS (`wss://live-ws.<dom>/im/v1/comet`)** untuk mengirim Protobuf `HB_REQ`, menarik stream FLV/HLS, melaporkan `SZTracker` (`reportPB`), serta worker pool multi-thread.
- **[BARU v1.3.0 — Pencarian Produk via Gambar & AI Object Crop (`SearchProductsByImage`, `GetImageBoundingBox`)]:**
  - Cari produk serupa atau lebih murah (`SimilarProducts` / `CheaperOptions`) murni lewat HTTP tanpa browser/emulator, mendukung 5 sumber gambar (file lokal, Base64 clipboard, URL eksternal, CDN Shopee, link produk).
- **[BARU v1.2.0 — Layer-2 Android Device Risk Token (`af-ac-enc-sz-token`)]:**
  - Membuat & menyimpan cache `af-ac-enc-sz-token`, `riskToken`, `dfp`, `shpSecData` yang terikat 1:1 dengan profil perangkat Android di `devices_vault.json`.
- **[BARU v1.1.0 — Scraper Affiliate Real-Time]:**
  - **`GetShopNewestProducts`:** Memantau produk terbaru yang baru diupload toko mana pun (`sinceItemId`, `withinHours`, lengkap dengan tag komisi Affiliate).
  - **`GetShopVideos`:** Mengambil daftar video toko beserta link download `.mp4` **tanpa watermark** (`mp4Url`) dan daftar produk di keranjang kuning (`attachedProducts[]`).
- **Ambil Detail Produk, Profil Toko, Voucher, Pencarian SEO & Pohon Kategori di 8 Negara Shopee** (`ID`, `VN`, `TH`, `MY`, `PH`, `SG`, `TW`, `BR`) — mendukung URL lengkap maupun format singkat `https://shopee.co.id/product/{shop_id}/{item_id}`!
- **Upload Shopee Video Murni API 4 Langkah (`UploadShopeeVideo`)** — Pasang hingga **6 produk keranjang Affiliate**, mode Normal & Duet, serta mutator hash `.mp4` (`MD5`/`SHA-256`) dalam `<10ms` tanpa FFmpeg.
- **Sticky Device Vault (`devices_vault.json` terenkripsi `AES-256-GCM`)** & **Network Stack `uTLS` Native** dengan dukungan penuh proxy (`http://user:pass@ip:port`, `socks5://...`, `ip:port:user:pass`).

---

## Cara Mendapatkan `X-API-Key`

1. Buka portal resmi: **[https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)**
2. Daftar atau login cepat dengan Google.
3. Aktifkan saldo **Pay-As-You-Go** atau paket bulanan (**Basic / Pro / VIP**), lalu salin **`X-API-Key`** Anda.

---

## Contoh Cepat (Python — Tanpa `pip install`)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(
    api_key="YOUR_X_API_KEY_HERE",
    default_country="ID",
)

# Ambil detail produk lengkap langsung dari shop_id & item_id
detail = sdk.get_product_detail(
    product_url="https://shopee.co.id/product/2955704/26112249802",
    proxy="http://user:pass@ip:port",
    country="ID",
)
print("Nama Produk:", detail["product"]["name"])
print("Harga:", detail["product"]["price"], "| Stok:", detail["product"]["stock"])
```

---

## Daftar Lengkap 31 Fungsi API (`minsign_sdk.dll` v1.5.0)

Lihat tabel lengkap 31 fungsi di [`README.md`](./README.md#complete-api-reference-minsign_sdkdll-v150--31-built-in-functions) atau dokumentasi teknis di [`DOCS_MINSIGN_NATIVE_SDK.md`](./DOCS_MINSIGN_NATIVE_SDK.md).
