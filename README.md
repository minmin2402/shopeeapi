# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.3.0)

[![Version](https://img.shields.io/badge/Release-v1.3.0%20(26%20APIs)-8B5CF6?style=for-the-badge)](https://github.com/minmin2402/shopeeapi/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**Bộ thư viện nhân gốc đa ngôn ngữ (`minsign_sdk.dll` — Chuẩn C-ABI quốc tế)** giúp lập trình viên tích hợp toàn bộ nghiệp vụ Shopee & Shopee Affiliate tốc độ cao vào bất kỳ phần mềm nào (`C# .NET`, `Python`, `Node.js / Electron`, `C/C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`...) chỉ với **1 file DLL duy nhất**:

- **[MỚI v1.3.0 — Tìm Kiếm Sản Phẩm Bằng Hình Ảnh & AI Crop Vật Thể (`SearchProductsByImage` & `GetImageBoundingBox`)]:**
  - **API Tìm Sản Phẩm Tương Tự / Giá Rẻ Hơn Bằng Hình Ảnh Thuần HTTP (`search_products_by_image`)** — Hỗ trợ 5 nguồn ảnh linh hoạt (file `.jpg/.png/.webp/.gif/.bmp` tự động chuyển JPEG trong RAM, chuỗi `imageBase64` dán từ Clipboard `Ctrl+V`, link ảnh ngoài TikTok/1688/Taobao/Web, link ảnh CDN Shopee 0ms upload, hoặc link sản phẩm Shopee), chọn chế độ `SimilarProducts` hoặc `CheaperOptions`, không cần mở trình duyệt hay giả lập!
  - **API Nhận Diện Vùng Vật Thể AI (`get_image_bounding_box`)** — Trả về danh sách toạ độ `left,top,width,height` của các món đồ trong ảnh chụp toàn cảnh (`0` Cookie, `0` lượt ký).
- **[MỚI v1.2.0 — Layer-2 Android Device Risk Token (`af-ac-enc-sz-token`)]:**
  - **API Lấy Bộ Risk Token Thiết Bị (`MinSign_GetRiskToken` / `get_risk_token`)** — Sinh và lưu cache trọn bộ `af-ac-enc-sz-token`, `riskToken`, `dfp`, `longToken`, `shpSecData`, `miniToken` khớp 100% với hồ sơ máy Android cố định của từng tài khoản trong `devices_vault.json`, đồng thời hỗ trợ tham số `attachRiskHeaders: true` ngay trong `SignRaw` và `ExecuteSignedRequest` cho các luồng Checkout / Đặt hàng / Lưu Voucher nhạy cảm!
- **[MỚI v1.1.0 — Chuyên Dụng Cho Hệ Thống Affiliate]:**
  - **API Lấy Sản Phẩm Mới Nhất Của Shop Theo Thời Gian Thực (`GetShopNewestProducts`)** — Canh hàng vừa lên kệ của bất kỳ Shop nào (`rcmd_items?sort_type=2` + `affiliate/offer` kèm hoa hồng + Zero-Cookie Index), tích hợp sẵn bộ lọc `sinceItemId`, `sinceTimestamp`, `withinHours` để chạy Bot săn SP mới tự động!
  - **API Lấy Danh Sách Video Của Shop (`GetShopVideos`)** — Tự động giải mã `shopUrl` / `shopId` / `username` sang kênh Shopee Video `userId`, lật nhiều trang liên tiếp (`maxPages`), trả sẵn link tải `.mp4` gốc **không watermark** (`mp4Url`) và danh sách sản phẩm gắn giỏ vàng (`attachedProducts[]`)!
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
│   ├── image_search_shopee.py         # Ví dụ chuyên sâu: Tìm SP bằng Hình ảnh (Tương tự / Giá rẻ hơn) & AI Crop
│   ├── buff_view_shopee_video.py      # Ví dụ chuyên sâu: Buff View đơn luồng & đa luồng xoay Proxy
│   ├── quickstart_nodejs.js           # Code mẫu chạy ngay bằng Node.js
│   ├── QuickstartCSharp.cs            # Code mẫu tích hợp C# / WinForms / WPF
│   └── quickstart_cpp.cpp             # Code mẫu tích hợp C++17
├── DOCS_TIM_SAN_PHAM_BANG_ANH.md      # Cẩm nang riêng: Tích hợp Tìm kiếm bằng Hình ảnh & AI Crop Vật Thể
├── DOCS_MINSIGN_NATIVE_SDK.md         # Tài liệu kỹ thuật chi tiết toàn bộ 26 hàm SDK
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

# 2. [MỚI v1.1.0 - AFFILIATE] Canh sản phẩm MỚI NHẤT vừa lên kệ của Shop theo thời gian thực
newest = sdk.get_shop_newest_products(
    username="lovito.vn",
    limit=20,
    since_item_id="",  # Truyền latestItemId lần quét trước để chỉ nhận SP mới vừa đăng!
    cookie="",         # Khuyên truyền Cookie nick phụ + Proxy để mở full tab Mới Nhất (sort_type=2) & hoa hồng
    proxy="",
    country="VN",
)
print("SP mới nhất:", newest["latestItemId"], "| Số SP mới:", newest["count"])

# 3. [MỚI v1.1.0 - AFFILIATE] Quét danh sách Video của Shop (link MP4 gốc không logo + SP gắn giỏ vàng)
shop_videos = sdk.get_shop_videos(
    username="lovito.vn",
    limit=20,
    max_pages=2,
    cookie="SPC_U=...; SPC_ST=...;",  # Cần Cookie Shopee còn sống để đọc full timeline kênh Video
    proxy="",
    country="VN",
)
for v in shop_videos["videos"]:
    print("Video:", v["postId"], "| MP4 không logo:", v["mp4Url"], "| SP gắn giỏ:", len(v["attachedProducts"]))

# 4. Đẩy View Shopee Video đa luồng (buff_video_batch nhận cookies=[...], còn buff_video_view nhận cookie="...")
batch = sdk.buff_video_batch(
    video_url="https://sv.shopee.vn/share-video/c4PVehg9CgChmFCrAwAAAA%3D%3D",
    target_views=20,
    concurrency=5,
    proxies=["103.145.22.11:8080:user:pass"],        # Để [] nếu test mạng trực tiếp
    cookies=["SPC_U=15759087777; SPC_ST=...;"],      # Danh sách Cookie xoay vòng (hoặc để [] nếu chạy Guest vãng lai)
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

## Bảng Tổng Hợp 26 Hàm Tích Hợp Sẵn Trong `minsign_sdk.dll` (`v1.3.0`)

| Nhóm Chức Năng | Tên `action` (`MinSign_Invoke`) | Mô Tả Ngắn | Cần Cookie? |
|---|---|---|---|
| **1. Hệ Thống & Thiết Bị Acc** | `MinSign_Init` | Khởi tạo SDK với `apiKey`, `signerUrl`, `vaultFilePath`, `vaultSecret` | Không |
| | `check_api_key` | Kiểm tra gói thuê, số dư ví, hạn mức Quota & tốc độ RPM của `X-API-Key` | Không |
| | `bind_account_device` | Cấp phát & khóa cố định 1 thiết bị Android cho `cookie` / `accountId` vào `devices_vault.json` | Tuỳ chọn |
| | `list_local_devices` | Xem danh sách toàn bộ cặp `Tài khoản <-> Điện thoại Android` đang lưu trên máy Client | Không |
| | `remove_local_device` | Xóa thiết bị đã lưu của 1 tài khoản để cấp máy mới | Không |
| | `sign_raw` | Chỉ lấy bộ Header chữ ký bảo mật (`x-sap-ri`, `af-ac-enc-dat`, chữ ký động...) | Tuỳ chọn |
| | **`get_risk_token`** | **[v1.2]** Sinh & lưu cache bộ Layer-2 Risk Token (`af-ac-enc-sz-token`, `dfp`, `shpSecData`) theo thiết bị | Tuỳ chọn |
| **2. Sản Phẩm, Gian Hàng & Tìm Bằng Ảnh** | `get_product_detail` | Lấy trọn bộ chi tiết SP: tên, giá, tồn kho, đã bán, sao, `models` phân loại, ảnh HD, thông tin Shop | **Không cần** (hoặc kèm Cookie) |
| | `get_shop_overview` | Lấy thông tin gian hàng từ link shop, `shopId` hoặc `username` (kèm `userId` kênh Video, hỗ trợ 8 nước) | **Không cần** |
| | `get_shop_products` | Lấy danh sách sản phẩm trong gian hàng có phân trang (`limit`, `offset`) | **Không cần** |
| | **`get_shop_newest_products`** | **[v1.1 — Affiliate]** Lấy SP mới nhất vừa lên kệ của Shop theo thời gian thực (`sinceItemId`, `sinceTimestamp`, `withinHours`, kèm `affiliateProductTag` & hoa hồng) | **Không cần** (khuyên kèm Cookie để mở full `sort_type=2`) |
| | `get_shop_categories` | Lấy danh mục con nội bộ của gian hàng | **Không cần** |
| | `get_shop_vouchers` | Quét danh sách mã giảm giá / Voucher đang mở của gian hàng | **Không cần** |
| | `search_products` | Tìm kiếm sản phẩm theo từ khóa (`relevancy`, `sales`, `ctime`, `price`) | Tuỳ chọn |
| | **`search_products_by_image`** | **[MỚI v1.3]** Tìm kiếm sản phẩm tương tự (`SimilarProducts`) hoặc giá rẻ hơn (`CheaperOptions`) bằng file ảnh / Base64 / URL ảnh TikTok-1688-Shopee / Link SP | **Bắt buộc (`SPC_ST`)** |
| | **`get_image_bounding_box`** | **[MỚI v1.3]** AI nhận diện toạ độ khung vật thể sản phẩm trong ảnh (`left,top,width,height` — `0` lượt ký) | **Không cần** |
| | `get_category_tree` | Lấy toàn bộ cây danh mục ngành hàng Shopee theo quốc gia | **Không cần** |
| **3. Đăng Video & Affiliate** | `upload_shopee_video` | Pipeline 4 bước đăng Shopee Video thuần API + gắn tối đa 6 link SP giỏ hàng vàng + Duet | **Bắt buộc** |
| | `precheck_video_upload` | Kiểm tra nhanh Cookie còn sống và có quyền đăng Shopee Video không | **Bắt buộc** |
| | `get_affiliate_products` | Lấy danh sách sản phẩm gợi ý gắn giỏ hàng Affiliate | **Bắt buộc** |
| | `mutate_mp4_fingerprint` | Biến đổi nhị phân `.mp4` làm mới `MD5` & `SHA-256` trong `< 10ms` chống quét trùng video | Không |
| **4. Buff View & Kênh Video Shop** | `buff_video_view` | Đẩy 1 lượt xem Shopee Video hợp lệ chuẩn 4 bước qua Proxy | Không (hoặc kèm Cookie) |
| | `buff_video_batch` | Chạy Worker Pool đa luồng trong DLL đẩy hàng loạt lượt xem xoay vòng `proxies[]` & `cookies[]` | Không (hoặc kèm Cookie) |
| | `get_video_detail` | Lấy thống kê chi tiết 1 video Shopee (lượt xem, tim, bình luận, `mp4Url`) | Tuỳ chọn |
| | **`get_shop_videos`** | **[MỚI v1.1 — Affiliate]** Quét toàn bộ danh sách Video của Shop (tự động giải mã `Shop -> userId`, hỗ trợ lật nhiều trang `maxPages`, trả `mp4Url` gốc không logo & `attachedProducts[]`) | Khuyên truyền Cookie nick phụ |
| | `get_channel_and_hashtag_videos` | Quét danh sách video theo Kênh người dùng hoặc theo Hashtag | Tuỳ chọn |
| **5. Cổng Ký Mở Rộng** | `execute_signed_request` | Cổng vạn năng: truyền bất kỳ URL API Shopee GET/POST nào, SDK tự ký & bắn qua `uTLS` + Proxy | Tuỳ chọn |

---

## Hướng Dẫn Chi Tiết Cách Buff View Shopee Video Bằng SDK (Tham Số & Nguồn Lấy)

SDK tích hợp sẵn trọn vẹn quy trình 4 bước chuẩn của Shopee Video bên trong nhân `minsign_sdk.dll` (*Giải link rút gọn `shp.ee` $\rightarrow$ Ký mở `timeline/single` lấy `view_token` $\rightarrow$ Đọc luồng byte MP4 `Range: 0-65535` trên CDN $\rightarrow$ Ký bắn gói 3 sự kiện `video_impression` + `video_play` + `video_play_time` lên `c-api-bit`*).

> **Chi phí lượt ký:** Đúng **2 lượt ký / 1 View hoàn chỉnh** (bước đọc CDN MP4 tốn 0 lượt ký). Bộ đếm View hiển thị trên App Shopee cập nhật sau khoảng **30 giây – 2 phút**.

### 1. Chọn Hàm Phù Hợp Với Tool Của Bạn
- **`buff_video_batch` (`BuffVideoBatch` / `buffVideoBatch`)**: Khuyên dùng! Tự chạy **Goroutine Worker Pool đa luồng ngay trong DLL** (tối đa `200` luồng), tự chia việc và xoay vòng mảng `proxies[]` + `cookies[]`.
- **`buff_video_view` (`BuffVideoView` / `buffVideoView`)**: Đẩy **1 lượt xem đơn lẻ** (dùng khi bạn muốn tự viết vòng lặp quản lý luồng riêng để cập nhật từng dòng trạng thái lên bảng giao diện WinForms / WPF / Electron).
- **`get_video_detail` (`GetVideoDetail` / `getVideoDetail`)**: Kiểm tra số `views`, `likes`, `comments`, `authorName` hiện tại của video trước và sau khi chạy.

### 2. Bảng Giải Thích Chi Tiết Các Tham Số Truyền Vào & Lấy Ở Đâu?

| Tham Số (JSON / C# / JS) | Tên Tham Số Python | Bắt Buộc? | Ý Nghĩa & Cách Lấy Thực Tế |
|---|---|---|---|
| **`apiKey`** | `api_key` *(lúc tạo `MinSignClient`)* | **Bắt buộc** | Mã xác thực máy chủ ký. Đăng nhập **[vip-sign.minmintool.site/dashboard](https://vip-sign.minmintool.site/dashboard)** $\rightarrow$ mục **Quản Lý API Key** $\rightarrow$ bấm **Sao Chép Key**. |
| **`videoUrl`** | `video_url` | **Bắt buộc** *(nếu trống `postId`)* | Link video cần đẩy view. Mở video trên **App Shopee** $\rightarrow$ bấm nút **Chia sẻ (Share)** $\rightarrow$ **Sao chép liên kết**. Nhận mọi dạng link: rút gọn `https://vn.shp.ee/...`, link đầy đủ `https://sv.shopee.vn/share-video/...`, hoặc lấy từ trường `shareUrl` của hàm `get_shop_videos`. |
| **`postId`** | `post_id` | Tuỳ chọn (`""`) | Mã ID gốc của bài đăng video (VD: `"c4PVehg9CgChmFCrAwAAAA=="`). Nếu đã truyền `videoUrl` thì **để trống `""`** (SDK tự tách). Nếu quét từ `get_shop_videos`, truyền thẳng `postId` sẽ bỏ qua bước giải nén link rút gọn (nhanh hơn ~150ms). |
| **`targetViews`** | `target_views` | Chỉ ở `buff_video_batch` | Tổng số lượt xem cần đẩy trong đợt gọi này (mặc định `10`, ví dụ truyền `100`, `500`, `1000`). |
| **`concurrency`** | `concurrency` | Chỉ ở `buff_video_batch` | Số luồng chạy song song cùng lúc bên trong DLL (mặc định `5`, tối đa `200`). **Mẹo:** Đặt nhỏ hơn hoặc bằng tổng số Proxy xoay đang có. |
| **`proxy`** / **`proxies`** | `proxy` *(chuỗi)* / `proxies` *(mảng)* | **Rất quan trọng khi chạy SLL** | Shopee chống spam nhiều view từ cùng 1 địa chỉ IP. Nếu test 1–2 view trên máy cá nhân có thể để trống `""` / `[]`. Khi chạy số lượng lớn, mua Proxy xoay IPv4 Dân cư / 4G (TMProxy, WWProxy, Tinsoft, ZingProxy, LunaProxy...) và truyền vào. **SDK tự nhận mọi định dạng:** `"ip:port:user:pass"`, `"ip:port"`, `"http://user:pass@ip:port"`, `"socks5://user:pass@ip:port"`. |
| **`cookie`** / **`cookies`** | `cookie` *(chuỗi)* / `cookies` *(mảng)* | **Không bắt buộc** (`""` / `[]`) | **Để trống `""` / `[]` (Khuyên dùng mặc định):** SDK chạy chế độ *Guest Vãng Lai* — mỗi lượt xem tự sinh mới 1 điện thoại Android 14 + mã `SPC_F` riêng biệt, không cần nuôi nick Shopee! Nếu có sẵn dàn Cookie nick phụ (`"SPC_U=...; SPC_ST=...;"`), truyền vào sẽ tính là view người dùng đã đăng nhập và tự khóa thiết bị cố định vào `devices_vault.json`. |
| **`watchSeconds`** | `watch_seconds` | Tuỳ chọn (`18`) | Số giây xem video báo cáo lên Shopee (`seg_duration`). Khuyên đặt từ `15` đến `25` giây để đạt độ giữ chân (Retention) tự nhiên. |
| **`simulateWait`** | *(qua `invoke`)* | Tuỳ chọn (`false`) | Chỉ có ở `buff_video_view`: đặt `true` nếu muốn luồng nghỉ thực tế ~3 giây giữa bước mở video và bước báo cáo xem xong. |
| **`country`** | `country` | Tuỳ chọn (`"VN"`) | Mã vùng Shopee (`"VN"`, `"TW"`, `"PH"`, `"MY"`, `"TH"`, `"ID"`, `"SG"`, `"BR"`). Nếu truyền `videoUrl` đầy đủ SDK tự động nhận diện vùng. |

### 3. Ví Dụ Đầy Đủ Cách Gọi Buff View Ở Các Ngôn Ngữ

#### Python (`examples/buff_view_shopee_video.py`)
```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY_HERE", default_country="VN")

# Danh sách Proxy xoay (để [] nếu test thử 1-2 lượt bằng mạng hiện tại)
proxies = [
    "103.145.22.11:8080:user1:pass1",
    "103.145.22.12:8080:user2:pass2",
]

# Danh sách Cookie các nick Shopee (tuỳ chọn — để [] nếu muốn chạy Guest vãng lai không cần nick)
cookies = [
    "SPC_U=15759087777; SPC_ST=...; csrftoken=...;",
    "SPC_U=26841029333; SPC_ST=...; csrftoken=...;",
]

# Cách A: Đẩy Batch 100 View đa luồng -> truyền tham số mảng cookies=[...]
batch_res = sdk.buff_video_batch(
    video_url="https://vn.shp.ee/xxxxxx",  # Hoặc link https://sv.shopee.vn/share-video/...
    target_views=100,
    concurrency=10,
    proxies=proxies,
    cookies=cookies,   # Tự xoay vòng Cookie + giữ thiết bị cố định từng nick (hoặc để [] nếu đẩy Guest)
    watch_seconds=20,
    country="VN",
)
print(f"Thành công: {batch_res['successViews']}/{batch_res['targetViews']} | Thời gian: {batch_res['elapsedMs']}ms")

# Cách B: Đẩy lẻ 1 View -> truyền tham số chuỗi đơn cookie="..."
single_res = sdk.buff_video_view(
    video_url="https://vn.shp.ee/xxxxxx",
    proxy=proxies[0],
    cookie=cookies[0],  # Truyền 1 chuỗi Cookie nick Shopee (hoặc để "" nếu đẩy Guest)
    watch_seconds=18,
    country="VN",
)
print("1 View OK:", single_res["success"], "| UBT HTTP:", single_res["ubtHttpStatus"])
```

#### C# (.NET / WinForms / WPF)
```csharp
using System;
using MinSign;

using var sdk = new MinSignClient(apiKey: "YOUR_X_API_KEY_HERE", defaultCountry: "VN");

// 1. Đẩy Batch đa luồng -> truyền mảng cookies = new[] { ... }
var batch = sdk.BuffVideoBatch(new
{
    videoUrl = "https://vn.shp.ee/xxxxxx",
    targetViews = 100,
    concurrency = 10,
    proxies = new[]
    {
        "103.145.22.11:8080:user1:pass1",
        "103.145.22.12:8080:user2:pass2"
    },
    cookies = new[]
    {
        "SPC_U=15759087777; SPC_ST=...;", // Hoặc truyền Array.Empty<string>() nếu chạy Guest không cần nick
    },
    watchSeconds = 20,
    country = "VN"
});

// 2. Đẩy lẻ 1 View -> truyền chuỗi đơn cookie = "..."
var single = sdk.BuffVideoView(new
{
    videoUrl = "https://vn.shp.ee/xxxxxx",
    proxy = "103.145.22.11:8080:user1:pass1",
    cookie = "SPC_U=15759087777; SPC_ST=...;", // Hoặc "" nếu chạy Guest
    watchSeconds = 18,
    country = "VN"
});

var data = batch.GetProperty("data");
Console.WriteLine($"Đã đẩy thành công: {data.GetProperty("successViews")}/{data.GetProperty("targetViews")} views!");
```

#### Node.js / Electron (`npm install koffi`)
```javascript
const { MinSignClient } = require("./wrappers/nodejs/minsign_sdk");

(async () => {
  const sdk = new MinSignClient({ apiKey: "YOUR_X_API_KEY_HERE", defaultCountry: "VN" });

  // 1. Đẩy Batch đa luồng trên Worker Thread -> truyền mảng cookies: [...]
  const batch = await sdk.buffVideoBatch({
    videoUrl: "https://vn.shp.ee/xxxxxx",
    targetViews: 100,
    concurrency: 10,
    proxies: ["103.145.22.11:8080:user1:pass1", "103.145.22.12:8080:user2:pass2"],
    cookies: ["SPC_U=15759087777; SPC_ST=...;"], // Để [] nếu đẩy Guest vãng lai
    watchSeconds: 20,
    country: "VN",
  });
  console.log("Kết quả Batch:", batch.successViews, "/", batch.targetViews);

  // 2. Đẩy lẻ 1 View -> truyền chuỗi đơn cookie: "..."
  const single = await sdk.buffVideoView({
    videoUrl: "https://vn.shp.ee/xxxxxx",
    proxy: "103.145.22.11:8080:user1:pass1",
    cookie: "SPC_U=15759087777; SPC_ST=...;", // Để "" nếu đẩy Guest vãng lai
    watchSeconds: 18,
    country: "VN",
  });
  console.log("1 View OK:", single.success);
})();
```

### 4. Cấu Trúc Dữ Liệu JSON Trả Về Của Hàm Buff View
- **`buff_video_view` (`data`)**:
  ```json
  {
    "success": true,
    "country": "VN",
    "postId": "c4PVehg9CgChmFCrAwAAAA==",
    "videoId": "vn-11110105-6ke17-m1...",
    "authorName": "ten_kenh_video",
    "currentViews": 1250,
    "vodStreamStatus": 206,
    "vodBytesRead": 65536,
    "ubtHttpStatus": 200,
    "totalLatencyMs": 840
  }
  ```
- **`buff_video_batch` (`data`)**:
  ```json
  {
    "country": "VN",
    "postId": "c4PVehg9CgChmFCrAwAAAA==",
    "targetViews": 100,
    "concurrency": 10,
    "successViews": 98,
    "failedViews": 2,
    "reportedViews": 1348,
    "lastError": "",
    "elapsedMs": 9420
  }
  ```

---

## Hướng Dẫn Chi Tiết Cách Tìm Sản Phẩm Bằng Hình Ảnh & AI Crop Vật Thể (`v1.3.0+`)

Từ bản **`v1.3.0`**, `minsign_sdk.dll` tích hợp trực tiếp luồng **Tìm kiếm sản phẩm bằng hình ảnh thuần HTTP (`search_products_by_image`)** và **AI nhận diện vùng vật thể (`get_image_bounding_box`)** chuẩn App Shopee — hoàn toàn **không cần trình duyệt, không cần giả lập Android, không dính Captcha**.

> **Chi phí lượt ký cực tiết kiệm:**
> - Bước **Upload ảnh lên CDN Shopee** (`sv.shopee.vn/api/v2/biz/file/image`): **`0` lượt ký** (tự động chuyển mọi định dạng `.webp` từ 1688/TikTok, `.png` chụp màn hình `Ctrl+V`, `.gif`, `.bmp` sang `JPEG` chuẩn ngay trong RAM).
> - Bước **AI Nhận diện khung vật thể** (`get_image_bounding_box`): **`0` lượt ký** & **không cần Cookie**.
> - Bước **Truy vấn kết quả Image Search**: Chỉ tốn đúng **`1` lượt ký / trang (`20` sản phẩm)**.

### 1. Bảng Giải Thích Chi Tiết Các Tham Số Của `search_products_by_image`

Bạn chỉ cần truyền **`cookie`** kèm **1 trong 5 nguồn ảnh đầu vào** (`imagePath`, `imageBase64`, `imageUrl`, `productUrl`, hoặc `imageId`):

| Tham Số (JSON / JS / C#) | Tên Tham Số Python | Bắt Buộc? | Ý Nghĩa & Cách Truyền Thực Tế |
|---|---|---|---|
| **`cookie`** | `cookie` | **Bắt buộc** | Chuỗi Cookie tài khoản Shopee còn sống (**bắt buộc có `SPC_ST=...`**; hỗ trợ cả định dạng chuỗi header `"SPC_ST=...; SPC_U=...;"` hoặc mảng JSON cookie xuất từ trình duyệt). |
| **`imagePath`** | `image_path` | Chọn 1 trong 5 nguồn ảnh | Đường dẫn file ảnh trên máy tính (VD: `"D:/anh_mau_1688.webp"`, `"C:/test.png"`, `"D:/sp.jpg"`). SDK tự động giải mã `WebP/PNG/GIF/BMP` sang `JPEG` chuẩn trên RAM trước khi đẩy lên Shopee. |
| **`imageBase64`** | `image_base64` | Chọn 1 trong 5 nguồn ảnh | Chuỗi ảnh mã hóa Base64 (nhận cả chuỗi thuần lẫn `data:image/png;base64,iVBOR...` khi người dùng bấm `Ctrl+V` dán ảnh chụp màn hình trực tiếp vào phần mềm!). |
| **`imageUrl`** | `image_url` | Chọn 1 trong 5 nguồn ảnh | - **Link ảnh ngoài** (*TikTok, 1688, Taobao, Facebook, Web bất kỳ*): SDK tự tải ảnh về RAM $\rightarrow$ đẩy lên CDN Shopee (`0` lượt ký) $\rightarrow$ tìm kiếm.<br>- **Link ảnh CDN Shopee** (`https://down-vn.img.susercontent.com/file/...`): SDK tự bóc mã ảnh tìm thẳng trong **`~700ms` (`0` bước upload)**! |
| **`productUrl`** | `product_url` | Chọn 1 trong 5 nguồn ảnh | Link sản phẩm Shopee bất kỳ (hoặc truyền cặp `shopId` + `itemId`). SDK tự lấy ảnh bìa sản phẩm đó để quét toàn bộ các Shop khác đang bán mẫu hàng giống hệt hoặc giá rẻ hơn! |
| **`imageId`** | `image_id` | Chọn 1 trong 5 nguồn ảnh | Mã hash ảnh trên CDN Shopee (VD: `"vn-11134114-81ztc-..."`). Dùng để phân trang trang 2, trang 3 (`offset: 20, 40...`) mà **không cần upload lại ảnh**! |
| **`resultType`** | `result_type` | Tuỳ chọn (`"SimilarProducts"`) | - `"SimilarProducts"`: Tìm sản phẩm giống nhất về kiểu dáng/mẫu mã.<br>- `"CheaperOptions"`: Tìm các Shop bán mẫu tương tự nhưng **ưu tiên giá rẻ hơn** (cực mạnh để so giá nguồn hàng / Affiliate). |
| **`autoDetectBox`** | `auto_detect_box` | Tuỳ chọn (`false`) | Đặt `true` nếu ảnh chụp toàn cảnh có nhiều món đồ (VD: ảnh outfit cả áo + quần + túi). AI Shopee sẽ tự cắt đúng khung vật thể có điểm tin cậy cao nhất trước khi tìm! |
| **`boundingBox`** | `bounding_box` | Tuỳ chọn (`""`) | Chuỗi toạ độ cắt vùng ảnh `"left,top,width,height"` (VD: `"112,42,350,737"` lấy từ hàm `get_image_bounding_box` khi làm tính năng cho khách tự kéo khung chọn món đồ trên UI). |
| **`offset` / `limit`** | `offset` / `limit` | Tuỳ chọn (`0` / `20`) | Phân trang kết quả: Trang 1 truyền `offset=0, limit=20`; Trang 2 truyền lại `imageId` của Trang 1 kèm `offset=20, limit=20`. |
| **`proxy`** | `proxy` | Khuyên dùng | Proxy gắn theo tài khoản Cookie (`"ip:port:user:pass"`, `"http://user:pass@ip:port"`, `"socks5://..."`). Để `""` nếu dùng mạng trực tiếp. |
| **`country`** | `country` | Tuỳ chọn (`"VN"`) | Mã quốc gia Shopee (`"VN"`, `"TH"`, `"ID"`, `"MY"`, `"SG"`, `"PH"`, `"BR"`). |

---

### 2. Code Mẫu Tích Hợp Tìm Bằng Hình Ảnh Ở 4 Ngôn Ngữ

#### A. Python (`examples/image_search_shopee.py`)
```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY_HERE", default_country="VN")
COOKIE_SHOPEE = "SPC_U=...; SPC_ST=...;"

# Cách 1: Tìm sản phẩm tương tự từ file ảnh trên máy (.jpg / .png / .webp đều chạy mượt!)
res = sdk.search_products_by_image(
    cookie=COOKIE_SHOPEE,
    image_path=r"D:\NguonHang1688\ao_khoac_mau.webp",
    result_type="SimilarProducts",   # Đổi thành "CheaperOptions" nếu muốn tìm Shop bán rẻ hơn!
    auto_detect_box=True,            # Tự động nhờ AI cắt vùng sản phẩm chính trong ảnh
    limit=20,
    proxy="",                        # Hoặc "103.145.22.11:8080:user:pass"
    country="VN",
)
print(f"Mã ảnh CDN: {res['imageId']} | Khung AI: {res.get('boundingBox')} | Trả về: {res['itemsCount']} SP")
for sp in res["items"][:5]:
    print(f"#{sp['rank']} [{sp['priceVnd']:,}đ | Đã bán: {sp['historicalSold']}] {sp['name']} -> {sp['productUrl']}")

# Cách 2: Lật sang Trang 2 siêu tốc (truyền lại image_id vừa nhận được -> tốn 0ms upload!)
if res["hasMore"]:
    page2 = sdk.search_products_by_image(
        cookie=COOKIE_SHOPEE,
        image_id=res["imageId"],
        bounding_box=res.get("boundingBox", ""),
        result_type="SimilarProducts",
        offset=res["nextOffset"],    # 20
        limit=20,
    )
    print("Trang 2 trả thêm:", page2["itemsCount"], "sản phẩm!")

# Cách 3 (Tuỳ chọn - 0 Cookie, 0 Lượt Ký): Chỉ lấy danh sách khung vật thể AI để vẽ ô chọn trên giao diện
boxes = sdk.get_image_bounding_box(image_path=r"D:\NguonHang1688\anh_outfit.jpg", country="VN")
print("Khung gợi ý tốt nhất:", boxes["bestBox"], "| Tất cả khung:", boxes["candidateBoxes"])
```

#### B. Node.js / Electron (`npm install koffi` — Chạy Worker Thread Mượt Mà)
```javascript
const { MinSignClient } = require("./wrappers/nodejs/minsign_sdk");

(async () => {
  const sdk = new MinSignClient({ apiKey: "YOUR_X_API_KEY_HERE", defaultCountry: "VN" });
  const cookie = "SPC_U=...; SPC_ST=...;";

  // Hỗ trợ truyền imagePath, imageBase64 (dán Ctrl+V), imageUrl (link ảnh TikTok/1688/Shopee), hoặc productUrl!
  const result = await sdk.searchProductsByImage({
    cookie,
    imageUrl: "https://down-vn.img.susercontent.com/file/vn-11134114-7ras8-mccff7oz208s9a",
    resultType: "CheaperOptions", // "SimilarProducts" | "CheaperOptions"
    autoDetectBox: false,
    offset: 0,
    limit: 20,
    proxy: "",
    country: "VN",
  });

  console.log(`Tìm thấy ${result.itemsCount} sản phẩm (${result.totalLatencyMs}ms):`);
  for (const item of result.items.slice(0, 5)) {
    console.log(`#${item.rank} - ${item.priceVnd.toLocaleString()}đ - ${item.name} (${item.productUrl})`);
  }
})();
```

#### C. C# (.NET / WinForms / WPF)
```csharp
using System;
using MinSign;

using var sdk = new MinSignClient(apiKey: "YOUR_X_API_KEY_HERE", defaultCountry: "VN");

// Tìm các Shop bán rẻ hơn từ file ảnh hoặc chuỗi Base64 chụp màn hình
var res = sdk.SearchProductsByImage(new
{
    cookie = "SPC_U=...; SPC_ST=...;",
    imagePath = @"D:\Images\mau_giay.webp",
    resultType = "CheaperOptions",
    autoDetectBox = true,
    offset = 0,
    limit = 20,
    proxy = "",
    country = "VN"
});

var data = res.GetProperty("data");
Console.WriteLine($"ImageID: {data.GetProperty("imageId").GetString()} | Số SP: {data.GetProperty("itemsCount").GetInt32()}");
foreach (var item in data.GetProperty("items").EnumerateArray())
{
    Console.WriteLine($"#{item.GetProperty("rank")} | {item.GetProperty("priceVnd")}đ | {item.GetProperty("name")}");
}
```

#### D. C++17 (`wrappers/cpp/minsign_sdk_client.hpp`)
```cpp
#include "wrappers/cpp/minsign_sdk_client.hpp"
#include <iostream>

int main() {
    minsign::Client sdk(R"({"apiKey":"YOUR_X_API_KEY_HERE","defaultCountry":"VN"})");
    std::string jsonRes = sdk.searchProductsByImage(R"({
        "cookie": "SPC_U=...; SPC_ST=...;",
        "imagePath": "D:\\Images\\sample.jpg",
        "resultType": "SimilarProducts",
        "limit": 20
    })");
    std::cout << jsonRes << std::endl;
    return 0;
}
```

### 3. Cấu Trúc JSON Trả Về Của `search_products_by_image`
```json
{
  "country": "VN",
  "domain": "shopee.vn",
  "httpStatus": 200,
  "error": 0,
  "sourceMode": "sv_file_upload",
  "imageId": "vn-11134114-81ztc-mv06c0iux5he52",
  "uploadedImageUrl": "https://down-vn.img.susercontent.com/file/vn-11134114-81ztc-mv06c0iux5he52",
  "boundingBox": "277,299,145,255",
  "resultType": "SimilarProducts",
  "offset": 0,
  "limit": 20,
  "nextOffset": 20,
  "hasMore": true,
  "totalCount": 20,
  "itemsCount": 20,
  "items": [
    {
      "rank": 1,
      "itemId": "25294038727",
      "shopId": "1023922469",
      "name": "Vợt pickleball Perseus 4 bề mặt carbon (NFC)",
      "priceVnd": 362600,
      "displayPriceVnd": 362600,
      "discountText": "-28%",
      "sold": 450,
      "historicalSold": 4000,
      "soldText": "Đã bán 4k+",
      "ratingStar": 4.9,
      "shopLocation": "Hà Nội",
      "isOfficialShop": false,
      "isPreferred": true,
      "imageUrl": "https://down-vn.img.susercontent.com/file/vn-11134207-...",
      "productUrl": "https://shopee.vn/product/1023922469/25294038727"
    }
  ],
  "signCostMs": 86,
  "totalLatencyMs": 1881
}
```

---

## Liên Hệ & Hỗ Trợ Kỹ Thuật

- **Website Đăng Ký & Lấy `X-API-Key` Tự Động:** [https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)
- **Cẩm Nang Riêng Tìm Kiếm Bằng Hình Ảnh:** [`DOCS_TIM_SAN_PHAM_BANG_ANH.md`](./DOCS_TIM_SAN_PHAM_BANG_ANH.md)
- **Tài Liệu Chi Tiết Đầy Đủ 26 Hàm SDK:** [`DOCS_MINSIGN_NATIVE_SDK.md`](./DOCS_MINSIGN_NATIVE_SDK.md)
