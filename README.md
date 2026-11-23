🌐 **Languages:** [English](README.md) · [Tiếng Việt](README.vi.md) · [Bahasa Indonesia](README.id.md) · [ภาษาไทย](README.th.md) · [简体中文](README.zh.md)

# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.5.0)

[![Version](https://img.shields.io/badge/Release-v1.5.0%20(31%20APIs)-8B5CF6?style=for-the-badge)](https://github.com/minmin2402/shopeeapi/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**A cross-language native core library (`minsign_sdk.dll` — Standard C-ABI)** that empowers developers to integrate full Shopee & Shopee Affiliate automation into any stack (`C# .NET`, `Python`, `Node.js / Electron`, `C/C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`) with **just 1 single DLL**:

---

## Key Capabilities & Highlights (v1.5.0)

- **[NEW v1.5.0 — Shopee Affiliate Link Converter & Batch Shortener (`ConvertAffiliateLink` & `BatchConvertAffiliateLinks`)]:**
  - Directly convert **standard Shopee product URLs**, **existing `aff_id` links**, **`universal-link`s**, or **`s.shopee.*` / `shp.ee` short links** into official tracked Affiliate short links (`https://s.shopee.vn/...`, `https://s.shopee.co.th/...`, `https://s.shopee.co.id/...`) belonging to your Affiliate Cookie via `affiliate.shopee.*/api/v3/gql?q=batchCustomLink`.
  - Supports up to 5 tracking sub-IDs (**`subId1..subId5`**), **automatic region detection from URL**, **batch conversion** (auto-chunked 20–50 links per call), and **auto MinSign + RiskToken retry** on `90309999`.
- **[NEW v1.4.0 — Multi-Threaded Shopee Live View & WebSocket Heartbeat (`GetLiveSessionDetail`, `BuffLiveView` & `BuffLiveBatch`)]:**
  - Automatically resolves Shopee Live URLs (`live.shopee.*/...`, `shp.ee/...`), signs Aegis (`X-Livestreaming-Auth`) + MinSign for `POST /api/v1/session/{id}/joinv2` & `play_url_list`.
  - Built-in **WebSocket RFC 6455 over Proxy + Android uTLS (`wss://live-ws.<dom>/im/v1/comet`)** sending Wire Protobuf `HB_REQ` (auto-handling `CONF_REQ`/`PUSH_REQ`), pulling CDN FLV/HLS streams, reporting `SZTracker` `reportPB` (`StreamStart` 10002 / `StreamFirstFrame` 10003 / `StreamHeartbeat` 10007), optional `/like`, and clean `/exit`.
- **[NEW v1.3.0 — Visual Product Search & AI Object Bounding Box (`SearchProductsByImage` & `GetImageBoundingBox`)]:**
  - **Pure-HTTP Image Search (`search_products_by_image`)** — Supports 5 image sources (`.jpg/.png/.webp/.gif/.bmp` auto-encoded in RAM, `imageBase64` from clipboard, external TikTok/1688/Taobao URLs, Shopee CDN image URLs, or Shopee product links) with `SimilarProducts` and `CheaperOptions` modes — zero browser or emulator required.
  - **AI Object Detection (`get_image_bounding_box`)** — Returns object coordinates `left,top,width,height` inside a scene photo (`0` cookies, `0` signing credits).
- **[NEW v1.2.0 — Layer-2 Android Device Risk Token (`af-ac-enc-sz-token`)]:**
  - **`MinSign_GetRiskToken` / `get_risk_token`** — Mints and caches full `af-ac-enc-sz-token`, `riskToken`, `dfp`, `longToken`, `shpSecData`, `miniToken` bound 1:1 to each account's persistent Android hardware profile in `devices_vault.json`, plus `attachRiskHeaders: true` in `SignRaw` & `ExecuteSignedRequest` for sensitive Checkout / Order / Voucher flows.
- **[NEW v1.1.0 — Built for Affiliate & Shop Automation]:**
  - **Real-Time Newest Shop Products (`GetShopNewestProducts`)** — Monitor newly listed items from any shop (`rcmd_items?sort_type=2` + `affiliate/offer` commission data + Zero-Cookie Index) with `sinceItemId`, `sinceTimestamp`, and `withinHours` filters.
  - **Watermark-Free Shop Video Scraper (`GetShopVideos`)** — Resolves `shopUrl` / `shopId` / `username` to Shopee Video `userId`, paginates across `maxPages`, and returns clean `.mp4` download URLs (`mp4Url`) + attached cart products (`attachedProducts[]`).
- **Product Details, Shop Profiles, Vouchers, SEO Search & Category Trees across 8 Shopee Regions** (`VN`, `TW`, `PH`, `MY`, `TH`, `ID`, `SG`, `BR`) — supports both full slug URLs and short `/product/{shop_id}/{item_id}` URLs!
- **Pure-API 4-Step Shopee Video Upload (`UploadShopeeVideo`)** — Attaches up to **6 Affiliate cart products**, supports Normal & Duet modes, and includes an instant `<10ms` `.mp4` binary fingerprint mutator (`MD5`/`SHA-256`) without FFmpeg.
- **Multi-Threaded Shopee Video View Booster (`BuffVideoView` & `BuffVideoBatch`)** — High-speed Go worker pool inside the DLL with proxy rotation and full MP4 byte-range + `c-api-bit` telemetry simulation.
- **Persistent Sticky Android Device Vault (`devices_vault.json`)** — Binds each Shopee account (`SPC_U` / `accountId`) to a dedicated Android 14 hardware profile locally (optional `AES-256-GCM` encryption) to prevent device-hopping checkpoints.
- **Native `uTLS` Network Stack (Android OkHttp4 / Chrome 131)** + full proxy format support (`http://user:pass@ip:port`, `socks5://...`, `ip:port:user:pass`, `ip:port`).

---

## Get Your `X-API-Key`

The SDK connects to **MinSign Shopee Cloud** for real-time dynamic signature generation:

1. Visit **[https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)** (supports English, Vietnamese & Thai).
2. Sign up or log in with Google.
3. Activate a **Pay-As-You-Go** wallet or monthly plan (**Basic / Pro / VIP**) and copy your **`X-API-Key`** from **API Keys**.
4. Pass `X-API-Key` into `MinSignClient` and start building immediately.

> **Full API Reference:** See [**`DOCS_MINSIGN_NATIVE_SDK.md`**](./DOCS_MINSIGN_NATIVE_SDK.md).

---

## Repository Structure

```text
shopeeapi/
├── bin/
│   └── win-x64/
│       └── minsign_sdk.dll            # Native Windows x64 Core Library (C-ABI)
├── include/
│   └── minsign_sdk.h                  # Standard C / C++ Header
├── wrappers/
│   ├── python/minsign_sdk.py          # Python 3.8+ Wrapper (pure ctypes, 0 dependencies)
│   ├── csharp/MinSignSdk.cs           # C# Wrapper (.NET Framework 4.7.2+ / .NET 6/7/8/9 x64)
│   ├── nodejs/minsign_sdk.js          # Node.js / Electron Async Wrapper (koffi Worker Thread)
│   └── cpp/minsign_sdk_client.hpp     # C++17 Header-only RAII Wrapper
├── examples/
│   ├── quickstart_python.py           # Ready-to-run Python quickstart
│   ├── image_search_shopee.py         # Visual Search & AI Crop example
│   ├── buff_view_shopee_video.py      # Single & batch Video View Booster example
│   ├── buff_view_shopee_live.py       # Shopee Live View Booster example
│   ├── quickstart_nodejs.js           # Node.js quickstart
│   ├── QuickstartCSharp.cs            # C# / WinForms / WPF example
│   └── quickstart_cpp.cpp             # C++17 example
├── README.md                          # English (Primary)
├── README.vi.md                       # Tiếng Việt
├── README.id.md                       # Bahasa Indonesia
├── README.th.md                       # ภาษาไทย
└── README.zh.md                       # 简体中文
```

---

## 60-Second Quickstart

### 1. Python (Zero external `pip` dependencies!)

```bash
git clone https://github.com/minmin2402/shopeeapi.git
cd shopeeapi
python examples/quickstart_python.py
```

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(
    api_key="YOUR_X_API_KEY_HERE",  # Get at https://vip-sign.minmintool.site
    default_country="ID",           # Supports VN, ID, TH, MY, PH, SG, TW, BR
)

# 1. Fetch full product details (title, price, stock, variants, HD images, shop info)
detail = sdk.get_product_detail(
    product_url="https://shopee.co.th/product/1834601441/57811171288",
    proxy="http://user:pass@ip:port",
    country="TH",
)
print("Product:", detail["product"]["name"])
print("Price:", detail["product"]["price"], "| Stock:", detail["product"]["stock"])

# 2. Convert & shorten Shopee Affiliate links (v1.5.0)
aff = sdk.convert_affiliate_link(
    url="https://shopee.vn/product/104187240/19894959672",
    sub_ids=["camp_01", "tiktok"],
    cookie="SPC_U=...; SPC_ST=...;",
    proxy="http://user:pass@ip:port",
    country="VN",
)
print("Short Link:", aff.get("shortLink"))

# 3. Monitor newest products from any shop in real time
newest = sdk.get_shop_newest_products(username="lovito.vn", limit=20, country="VN")
print("Latest Item ID:", newest["latestItemId"], "| Count:", newest["count"])
```

### 2. C# (.NET 6/8 / .NET Framework 4.7.2+ — `x64`)

```csharp
using System;
using System.Text.Json;
using MinSign;

using var sdk = new MinSignClient(
    apiKey: "YOUR_X_API_KEY_HERE",
    signerUrl: "https://vip-sign.minmintool.site",
    vaultFilePath: "./minsign_data/devices_vault.json",
    defaultCountry: "ID"
);

JsonElement res = sdk.GetProductDetail(new {
    productUrl = "https://shopee.co.id/product/2955704/26112249802",
    proxy = "http://user:pass@ip:port",
    country = "ID"
});
Console.WriteLine(res.GetRawText());
```

### 3. Node.js / Electron (`npm install koffi`)

```javascript
const { MinSignClient } = require("./wrappers/nodejs/minsign_sdk");

(async () => {
  const sdk = new MinSignClient({ apiKey: "YOUR_X_API_KEY_HERE", defaultCountry: "VN" });
  const detail = await sdk.getProductDetail({
    productUrl: "https://shopee.vn/product/104187240/19894959672",
    proxy: "http://user:pass@ip:port",
  });
  console.log(detail.product.name, detail.product.price);
})();
```

---

## Complete API Reference (`minsign_sdk.dll` v1.5.0 — 31 Built-in Functions)

| Category | Action (`MinSign_Invoke`) | Description | Cookie Required? |
|---|---|---|---|
| **1. System & Device Vault** | `MinSign_Init` | Initialize SDK with `apiKey`, `signerUrl`, `vaultFilePath`, `vaultSecret` | No |
| | `check_api_key` | Check subscription plan, wallet balance, quota & RPM limit | No |
| | `bind_account_device` | Bind & persist an Android 14 hardware profile to `devices_vault.json` | Optional |
| | `list_local_devices` | List all locally stored `Account <-> Android Device` bindings | No |
| | `remove_local_device` | Unbind a device profile from an account | No |
| | `sign_raw` | Generate raw security signature headers (`x-sap-ri`, dynamic headers) | Optional |
| | **`get_risk_token`** | **[v1.2]** Mint & cache Layer-2 Risk Tokens (`af-ac-enc-sz-token`, `dfp`, `shpSecData`) | Optional |
| **2. Products, Shops & Visual Search** | `get_product_detail` | Full product details (name, price, stock, ratings, variants, HD images, shop info) | Optional |
| | `get_shop_overview` | Shop profile from URL, `shopId`, or `username` (includes Video `userId`, 8 regions) | No |
| | `get_shop_products` | Paginated shop product list (`limit`, `offset`) | No |
| | **`get_shop_newest_products`** | **[v1.1]** Real-time newest shop items (`sinceItemId`, `withinHours`, affiliate tags) | Optional |
| | `get_shop_categories` | Internal shop categories | No |
| | `get_shop_vouchers` | Active shop vouchers | No |
| | `search_products` | Keyword product search (`relevancy`, `sales`, `ctime`, `price`) | Optional |
| | **`search_products_by_image`** | **[v1.3]** Pure-HTTP image search (`SimilarProducts` / `CheaperOptions`) | **Yes (`SPC_ST`)** |
| | **`get_image_bounding_box`** | **[v1.3]** AI object bounding box detection (`left,top,width,height` — `0` credits) | No |
| | `get_category_tree` | Full Shopee category tree by region | No |
| **3. Video Upload & Affiliate** | `upload_shopee_video` | 4-step pure-API Shopee Video upload + up to 6 Affiliate cart products + Duet | **Yes** |
| | `precheck_video_upload` | Verify cookie health & video upload permission | **Yes** |
| | `get_affiliate_products` | Fetch recommended Affiliate products for video cart | **Yes** |
| | **`convert_affiliate_link`** | **[v1.5]** Convert & shorten any Shopee link to your Affiliate short link (`subId1..5`) | **Yes** |
| | **`batch_convert_affiliate_links`** | **[v1.5]** Batch convert/shorten multiple Shopee links in parallel chunks | **Yes** |
| | `mutate_mp4_fingerprint` | Mutate `.mp4` binary `MD5` & `SHA-256` in `<10ms` without FFmpeg | No |
| **4. Video View Booster & Scraper** | `buff_video_view` | Dispatch 1 valid 4-step Shopee Video view over proxy | Optional |
| | `buff_video_batch` | Multi-threaded Go worker pool rotating `proxies[]` & `cookies[]` | Optional |
| | `get_video_detail` | Video stats (views, likes, comments, watermark-free `mp4Url`) | Optional |
| | **`get_shop_videos`** | **[v1.1]** Scrape all shop videos with watermark-free `mp4Url` & `attachedProducts[]` | Recommended |
| | `get_channel_and_hashtag_videos` | Fetch videos by channel `userId` or hashtag | Optional |
| **5. Shopee Live View Booster** | **`get_live_session_detail`** | **[v1.4]** Resolve Live URL / `sessionId`, `roomId`, `viewerCount`, `usersig`, `playUrls` | Optional |
| | **`buff_live_view`** | **[v1.4]** Dispatch 1 Live view (`joinv2` → FLV/HLS → WS `HB_REQ` → `reportPB` → `exit`) | Optional |
| | **`buff_live_batch`** | **[v1.4]** Multi-threaded Live viewer pool rotating `proxies[]` & `cookies[]` | Optional |
| **6. Universal Gateway** | `execute_signed_request` | Universal gateway: sign & execute any Shopee GET/POST API via `uTLS` + Proxy | Optional |

---

## Supported Shopee Regions

| Code | Region | Domain | Currency |
|---|---|---|---|
| `VN` | Vietnam | `shopee.vn` | VND (`₫`) |
| `ID` | Indonesia | `shopee.co.id` | IDR (`Rp`) |
| `TH` | Thailand | `shopee.co.th` | THB (`฿`) |
| `MY` | Malaysia | `shopee.com.my` | MYR (`RM`) |
| `PH` | Philippines | `shopee.ph` | PHP (`₱`) |
| `SG` | Singapore | `shopee.sg` | SGD (`S$`) |
| `TW` | Taiwan | `shopee.tw` | TWD (`NT$`) |
| `BR` | Brazil | `shopee.com.br` | BRL (`R$`) |

---

## Terms of Service
See [`TERMS_OF_SERVICE.md`](./TERMS_OF_SERVICE.md). Provided AS-IS for protocol research, sandbox testing, and authorized internal automation.
