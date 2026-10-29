# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.0.0)

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**Bộ thư viện nhân gốc đa ngôn ngữ (`minsign_sdk.dll` — Chuẩn C-ABI quốc tế)** giúp lập trình viên tích hợp toàn bộ nghiệp vụ Shopee tốc độ cao vào bất kỳ phần mềm nào (`C# .NET`, `Python`, `Node.js / Electron`, `C/C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`...) chỉ với **1 file DLL duy nhất**:

- **Lấy Chi Tiết Sản Phẩm, Gian Hàng, Mã Giảm Giá (Voucher), Tìm Kiếm SEO & Cây Danh Mục (8 Quốc gia Shopee)** — Hoạt động mượt mà ngay cả khi **không truyền Cookie**!
- **Đăng Shopee Video Thuần API (Pure-API Upload Pipeline 4 Bước)** — Tự động gắn tối đa **6 sản phẩm giỏ hàng Affiliate**, hỗ trợ cả chế độ thường & Duet, kèm hàm đổi mới vân tay nhị phân `.mp4` (`MD5`/`SHA-256`) trong `< 10ms` không cần FFmpeg.
- **Đẩy Lượt Xem Shopee Video Đa Luồng (`BuffVideoView` & `BuffVideoBatch`)** — Tích hợp sẵn Goroutine Worker Pool tốc độ cao ngay trong nhân DLL, tự động xoay vòng danh sách Proxy & giả lập trọn vẹn luồng đọc byte MP4 + sự kiện `c-api-bit`.
- **Tự Động Lưu & Tái Sử Dụng Thiết Bị Android Cố Định Theo Từng Tài Khoản (`devices_vault.json`)** — Mỗi tài khoản Shopee (`SPC_U` / `accountId`) được gắn cố định 1 hồ sơ phần cứng Android 14 ngay trên máy chạy tool (hỗ trợ khóa mã hóa `AES-256-GCM`), chống đổi máy liên tục gây checkpoint nick.
- **Tầng Mạng Native `uTLS` (Android OkHttp4 / Chrome 131 Fingerprint) + Hỗ Trợ Mọi Định Dạng Proxy Riêng** (`http://user:pass@ip:port`, `socks5://...`, `ip:port:user:pass`, `ip:port`).

---

## Lấy Mã `X-API-Key` Để Sử Dụng SDK

Bộ SDK kết nối trực tiếp tới hệ thống ký bảo mật đám mây **MinSign Shopee Cloud** để cấp phát chữ ký động thời gian thực:

1. Truy cập cổng dịch vụ chính thức: **[https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)**
2. Đăng ký tài khoản (hoặc Đăng nhập nhanh bằng Google).
3. Kích hoạt gói **Pay-As-You-Go (150đ / lượt ký)** hoặc gói tháng (**Basic / Pro / VIP**) và sao chép mã **`X-API-Key`** tại mục **Quản Lý API Key**.
4. Truyền `X-API-Key` vào hàm khởi tạo `MinSignClient` là dùng được ngay lập tức!

> **Tài liệu đặc tả đầy đủ từng hàm:** Xem chi tiết tại file [**`DOCS_MINSIGN_NATIVE_SDK.md`**](./DOCS_MINSIGN_NATIVE_SDK.md).

---

## Cấu Trúc Repository

```text
shopeeapi/
├── bin/
│   └── win-x64/
│       └── minsign_sdk.dll            # Thư viện nhân Native Windows 64-bit (C-ABI)
├── include/
│   └── minsign_sdk.h                  # Header C / C++ chuẩn
├── wrappers/
│   ├── python/
│   │   └── minsign_sdk.py             # Python 3.8+ Wrapper (dùng ctypes chuẩn, 0 thư viện ngoài)
│   ├── csharp/
│   │   └── MinSignSdk.cs              # C# Wrapper (.NET Framework 4.7.2+ / .NET 6/7/8/9 x64)
│   ├── nodejs/
│   │   └── minsign_sdk.js             # Node.js / Electron Async Wrapper (qua koffi Worker Thread)
│   └── cpp/
│       └── minsign_sdk_client.hpp     # C++17 Header-only Wrapper (RAII tự giải phóng vùng nhớ)
├── examples/
│   ├── quickstart_python.py           # Code mẫu chạy ngay bằng Python
│   ├── quickstart_nodejs.js           # Code mẫu chạy ngay bằng Node.js
│   ├── QuickstartCSharp.cs            # Code mẫu tích hợp C# / WinForms / WPF
│   └── quickstart_cpp.cpp             # Code mẫu tích hợp C++17
├── DOCS_MINSIGN_NATIVE_SDK.md         # Tài liệu kỹ thuật chi tiết toàn bộ 21 hàm SDK
└── README.md
```

---

## Bắt Đầu Nhanh Trong 60 Giây (Quickstart)

### 1. Python (Không cần `pip install` bất kỳ thư viện nào!)

```bash
git clone https://github.com/minmin2402/shopeeapi.git
cd shopeeapi
python examples/quickstart_python.py
```

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(
    api_key="YOUR_X_API_KEY_HERE",  # Lấy tại https://vip-sign.minmintool.site
    default_country="VN",
)

# 1. Lấy chi tiết sản phẩm Shopee (giá, tồn kho, đã bán, 26 phân loại models, bộ ảnh HD — KHÔNG cần Cookie!)
detail = sdk.get_product_detail(
    product_url="https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727"
)
print("Tên SP:", detail["product"]["name"])
print("Giá bán:", detail["product"]["priceVnd"], "VNĐ | Đã bán:", detail["product"]["historicalSold"])
print("Số phân loại (models):", len(detail["product"]["models"]))

# 2. Quét thông tin gian hàng đa quốc gia (VN, TW, PH, MY, TH, ID, SG, BR)
shop_tw = sdk.get_shop_overview(shop_id="116309859", country="TW")
print("Shop Đài Loan:", shop_tw["shop"]["shopName"])

# 3. Đẩy View Shopee Video đa luồng qua danh sách Proxy riêng
batch = sdk.buff_video_batch(
    video_url="https://sv.shopee.vn/share-video/c4PVehg9CgChmFCrAwAAAA%3D%3D",
    target_views=20,
    concurrency=5,
    proxies=["103.145.22.11:8080:user:pass"],  # Để [] nếu test mạng trực tiếp
    watch_seconds=18,
    country="VN",
)
print("Kết quả Buff View:", batch["successViews"], "/", batch["targetViews"])
```

---

### 2. C# (.NET Framework 4.7.2+ / .NET 6 / .NET 8 — WinForms / WPF / Console)

Thêm file `wrappers/csharp/MinSignSdk.cs` vào Project (chọn nền tảng build **`x64`**) và đặt `bin/win-x64/minsign_sdk.dll` cạnh file `.exe`:

```csharp
using System;
using System.Text.Json;
using MinSign;

class Program
{
    static void Main()
    {
        using var sdk = new MinSignClient(
            apiKey: "YOUR_X_API_KEY_HERE",
            signerUrl: "https://vip-sign.minmintool.site",
            vaultFilePath: "./minsign_data/devices_vault.json",
            defaultCountry: "VN"
        );

        // Lấy chi tiết sản phẩm không cần Cookie
        JsonElement res = sdk.GetProductDetail(new
        {
            productUrl = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
            proxy = "", // Hỗ trợ http://user:pass@ip:port, socks5://..., ip:port:user:pass
            country = "VN"
        });
        Console.WriteLine("Tên sản phẩm: " + res.GetProperty("data").GetProperty("product").GetProperty("name").GetString());

        // Đăng Shopee Video gắn giỏ hàng Affiliate + tự đổi MD5/SHA256 chống quét trùng
        JsonElement up = sdk.UploadShopeeVideo(new
        {
            videoPath = @"D:\Videos\review.mp4",
            caption = "Review vợt carbon siêu nảy #shopeevideo #xuhuong",
            productLinks = new[] { "https://shopee.vn/product/1023922469/25294038727" },
            mutateMp4 = true,
            proxy = "103.145.22.11:8080:user:pass",
            cookie = "SPC_U=...; SPC_ST=...;",
            country = "VN"
        });
        Console.WriteLine(up.GetRawText());
    }
}
```

---

### 3. Node.js / Electron (`npm install koffi` — Chạy Async Worker Thread Không Đơ Giao Diện)

```javascript
const { MinSignClient } = require("./wrappers/nodejs/minsign_sdk");

(async () => {
  const sdk = new MinSignClient({
    apiKey: "YOUR_X_API_KEY_HERE",
    defaultCountry: "VN",
  });

  const detail = await sdk.getProductDetail({
    productUrl: "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
  });
  console.log("Sản phẩm:", detail.product.name, "| Giá:", detail.product.priceVnd);
})();
```

---

## Bảng Tổng Hợp 21 Hàm Tích Hợp Sẵn Trong `minsign_sdk.dll`

| Nhóm Chức Năng | Tên `action` (`MinSign_Invoke`) | Mô Tả Ngắn | Cần Cookie? |
|---|---|---|---|
| **1. Hệ Thống & Thiết Bị Acc** | `MinSign_Init` | Khởi tạo SDK với `apiKey`, `signerUrl`, `vaultFilePath`, `vaultSecret` | Không |
| | `check_api_key` | Kiểm tra gói thuê, số dư ví, hạn mức Quota & tốc độ RPM của `X-API-Key` | Không |
| | `bind_account_device` | Cấp phát & khóa cố định 1 thiết bị Android cho `cookie` / `accountId` vào `devices_vault.json` | Tuỳ chọn |
| | `list_local_devices` | Xem danh sách toàn bộ cặp `Tài khoản <-> Điện thoại Android` đang lưu trên máy Client | Không |
| | `remove_local_device` | Xóa thiết bị đã lưu của 1 tài khoản để cấp máy mới | Không |
| | `sign_raw` | Chỉ lấy bộ Header chữ ký bảo mật (`x-sap-ri`, `af-ac-enc-dat`, chữ ký động...) | Tuỳ chọn |
| **2. Sản Phẩm & Gian Hàng (8 Nước)** | `get_product_detail` | Lấy trọn bộ chi tiết SP: tên, giá, tồn kho, đã bán, sao, `models` phân loại, ảnh HD, thông tin Shop | **Không cần** (hoặc kèm Cookie) |
| | `get_shop_overview` | Lấy thông tin gian hàng từ link shop, `shopId` hoặc `username` (hỗ trợ cả VN, TW, PH, MY, TH, ID, SG, BR) | **Không cần** |
| | `get_shop_products` | Lấy danh sách sản phẩm trong gian hàng có phân trang (`limit`, `offset`) | **Không cần** |
| | `get_shop_categories` | Lấy danh mục con nội bộ của gian hàng | **Không cần** |
| | `get_shop_vouchers` | Quét danh sách mã giảm giá / Voucher đang mở của gian hàng | **Không cần** |
| | `search_products` | Tìm kiếm sản phẩm theo từ khóa (`relevancy`, `sales`, `ctime`, `price`) | Tuỳ chọn |
| | `get_category_tree` | Lấy toàn bộ cây danh mục ngành hàng Shopee theo quốc gia | **Không cần** |
| **3. Đăng Video & Affiliate** | `upload_shopee_video` | Pipeline 4 bước đăng Shopee Video thuần API + gắn tối đa 6 link SP giỏ hàng vàng + Duet | **Bắt buộc** |
| | `precheck_video_upload` | Kiểm tra nhanh Cookie còn sống và có quyền đăng Shopee Video không | **Bắt buộc** |
| | `get_affiliate_products` | Lấy danh sách sản phẩm gợi ý gắn giỏ hàng Affiliate | **Bắt buộc** |
| | `mutate_mp4_fingerprint` | Biến đổi nhị phân `.mp4` làm mới `MD5` & `SHA-256` trong `< 10ms` chống quét trùng video | Không |
| **4. Buff View & Kênh Video** | `buff_video_view` | Đẩy 1 lượt xem Shopee Video hợp lệ chuẩn 4 bước qua Proxy | Không (hoặc kèm Cookie) |
| | `buff_video_batch` | Chạy Worker Pool đa luồng trong DLL đẩy hàng loạt lượt xem xoay vòng `proxies[]` & `cookies[]` | Không (hoặc kèm Cookie) |
| | `get_video_detail` | Lấy thống kê chi tiết 1 video Shopee (lượt xem, tim, bình luận, `mp4Url`) | Tuỳ chọn |
| | `get_channel_and_hashtag_videos` | Quét danh sách video theo Kênh người dùng hoặc theo Hashtag | Tuỳ chọn |
| **5. Giỏ Hàng & Mở Rộng** | `add_to_cart` | Tự động ký POST thêm sản phẩm / phân loại (`modelId`) vào giỏ hàng | **Bắt buộc** |
| | `execute_signed_request` | Cổng vạn năng: truyền bất kỳ URL API Shopee GET/POST nào, SDK tự ký & bắn qua `uTLS` + Proxy | Tuỳ chọn |

---

## Liên Hệ & Hỗ Trợ Kỹ Thuật

- **Website Đăng Ký & Lấy `X-API-Key` Tự Động:** [https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)
- **Tài Liệu Chi Tiết Đầy Đủ:** [`DOCS_MINSIGN_NATIVE_SDK.md`](./DOCS_MINSIGN_NATIVE_SDK.md)
