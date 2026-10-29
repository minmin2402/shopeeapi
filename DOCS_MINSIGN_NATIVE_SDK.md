# Tài Liệu Tích Hợp Bộ Thư Viện Gốc Đa Ngôn Ngữ — MinSign Native Universal SDK (`minsign_sdk.dll` v1.1.0)

**Phiên bản:** `1.1.0` (Windows x64 Native Shared Library — C-ABI Standard · **23 Hàm Dựng Sẵn**)  
**Máy chủ Ký Bảo Mật Mặc Định:** `https://vip-sign.minmintool.site` (Yêu cầu mã `X-API-Key`)  
**Hỗ trợ 8 Thị trường Shopee:** `VN`, `TW`, `PH`, `MY`, `TH`, `ID`, `SG`, `BR`  
**Ngôn ngữ tương thích 100%:** `C# (.NET Framework / .NET 6-9)`, `Python`, `Node.js / Electron`, `C / C++`, `Delphi`, `AutoIt`, `PHP FFI`, `Rust`, `Java JNA`, `Go`...

---

## 1. Kiến Trúc & Sức Mạnh Của `minsign_sdk.dll`

Thay vì phải tự viết lại hàng nghìn dòng logic giả lập TLS vân tay Android, giải mã AES-128-CBC VOD Token, tự vá Cookie `SPC_F` hay quản lý thiết bị cho từng tài khoản ở mỗi ngôn ngữ khác nhau, toàn bộ động cơ lõi đã được biên dịch thẳng ra **mã máy Native (`minsign_sdk.dll`)**:

1. **Chuẩn giao tiếp C-ABI Quốc tế (`const char*` UTF-8 JSON)**: Mọi ngôn ngữ lập trình trên Windows đều nạp được trực tiếp qua `DllImport` (C#), `ctypes` (Python), `koffi` (Node.js), `LoadLibrary` (C++/Delphi/AutoIt) mà không cần cài Runtime phụ thuộc.
2. **Bắt buộc xác thực `X-API-Key` với Server Ký (`https://vip-sign.minmintool.site`)**: Tự động xin chữ ký bảo mật (`x-sap-ri`, `x-sap-sec`, `af-ac-enc-dat`...) và kiểm tra hạn mức gói / số dư ví.
3. **Tự động Lưu & Tái Sử Dụng Thiết Bị Cố Định Theo Từng Acc Ngay Trên Máy Client (`devices_vault.json`)**:
   - Lần đầu tiên một tài khoản Shopee (`Cookie` chứa `SPC_U` hoặc `accountId`) được gọi, SDK tự động đồng bộ 1 hồ sơ phần cứng Android 14 cố định từ máy chủ ký và **lưu xuống file `devices_vault.json` ngay trên máy đang chạy tool**.
   - Ở mọi lần gọi tiếp theo (kể cả tắt phần mềm mở lại), SDK tự động nạp lại đúng 100% chiếc điện thoại đó (`deviceId`, `recommendedSpcF`, `recommendedUserAgent`, `model`, `androidId`, `carrier`) cho đúng tài khoản Shopee đó — chống hoàn toàn lỗi đổi thiết bị liên tục gây checkpoint tài khoản!
   - Hỗ trợ cả **JSON rõ ràng (mặc định)** để dễ kiểm tra và **Mã hóa khóa cứng AES-256-GCM** (khi truyền `vaultSecret`).
4. **Tầng Mạng Native `uTLS` (Giả lập JA3/JA4 Android OkHttp4 & Chrome 131) + Proxy Riêng Của Coder**:
   - Mọi request lấy sản phẩm, đăng video hay đẩy view đều đi **trực tiếp từ máy Client qua Proxy riêng của Coder** (`HTTP` / `HTTPS` / `SOCKS5`) lên Shopee, không đi vòng qua IP của Server Ký.
5. **Đa luồng Goroutine Worker Pool Tốc Độ Cao**: Có sẵn hàm đẩy view hàng loạt (`BuffVideoBatch`) chạy hàng chục đến hàng trăm luồng song song ngay bên trong nhân DLL với mức tiêu thụ RAM cực thấp.

---

## 2. Cấu Trúc Thư Mục Bộ SDK Giải Nén

```text
MinSign_Native_SDK_v1.0_win_x64/
├── bin/
│   └── win-x64/
│       └── minsign_sdk.dll            # Thư viện nhân Native Windows 64-bit
├── include/
│   └── minsign_sdk.h                  # Header C/C++ chuẩn xuất tự động
├── wrappers/
│   ├── csharp/
│   │   └── MinSignSdk.cs              # Wrapper C# (.NET Framework 4.8+ / .NET 6/8/9)
│   ├── python/
│   │   └── minsign_sdk.py             # Wrapper Python 3.8+ (dùng ctypes chuẩn, 0 thư viện ngoài)
│   ├── nodejs/
│   │   └── minsign_sdk.js             # Wrapper Node.js / Electron (Async Worker Thread qua koffi)
│   └── cpp/
│       └── minsign_sdk_client.hpp     # Wrapper C++17 Header-only (RAII tự giải phóng RAM)
└── DOCS_MINSIGN_NATIVE_SDK.md         # Tài liệu hướng dẫn tích hợp chi tiết này
```

---

## 3. Quy Tắc Định Dạng `Proxy`, `Cookie` & Kho Thiết Bị `devices_vault.json`

### 3.1. Định dạng `proxy` hỗ trợ tự động (Truyền chuỗi rỗng `""` nếu dùng mạng trực tiếp)
Bộ SDK tự động nhận diện và chuẩn hóa mọi định dạng Proxy phổ biến của dân MMO/Coder:
- `http://user:pass@103.145.22.11:8080` hoặc `http://103.145.22.11:8080`
- `socks5://user:pass@103.145.22.11:1080` hoặc `socks5://103.145.22.11:1080`
- Định dạng viết tắt 4 phần: `103.145.22.11:8080:user:pass` (SDK tự chuyển thành `http://user:pass@103.145.22.11:8080`)
- Định dạng viết tắt 2 phần: `103.145.22.11:8080` (SDK tự chuyển thành `http://103.145.22.11:8080`)

### 3.2. Định dạng `cookie` Shopee
- Truyền nguyên chuỗi Cookie tiêu chuẩn (ví dụ: `"SPC_U=15759087777; SPC_ST=...; csrftoken=...;"`).
- SDK sẽ tự động:
  1. Bóc `SPC_U` để định danh tài khoản (`VN:spcu_15759087777`) và lấy đúng máy Android cố định từ `devices_vault.json`.
  2. Tự động vá/đồng bộ `SPC_F`, `csrftoken`, `shopee_app_version` khớp với hồ sơ thiết bị đã gắn cho nick.
  3. Trả kèm `refreshedCookie` nếu Shopee cấp lại `Set-Cookie` mới.

### 3.3. Cơ chế Kho Thiết Bị Cục Bộ (`devices_vault.json`)
Khi gọi `MinSign_Init`:
- Nếu `vaultSecret = ""` (mặc định): File `./minsign_data/devices_vault.json` lưu dạng JSON thuần để coder dễ mở xem danh sách ánh xạ `Tài khoản <-> Điện thoại Android`.
- Nếu `vaultSecret = "mat-khau-rieng-cua-ban"`: Toàn bộ nội dung file trên ổ cứng được mã hóa **AES-256-GCM** chống sao chép trái phép.
- Với các tác vụ **không truyền Cookie / không truyền `accountId`** (ví dụ: Buff View vãng lai), SDK tự động chuyển sang chế độ **Guest Ephemeral** (mỗi lượt xem sinh 1 thiết bị ngẫu nhiên mới, không làm rác file `devices_vault.json`).

---

## 4. Danh Mục Toàn Bộ Các Hàm Có Sẵn Trong `minsign_sdk.dll`

Tất cả các hàm đều có thể gọi trực tiếp qua hàm C-ABI riêng hoặc gọi thống nhất qua `MinSign_Invoke(action, payloadJson)`:

| Nhóm | Tên Hàm C-ABI | Tên `action` (`MinSign_Invoke`) | Chức năng chính |
|---|---|---|---|
| **1. Hệ Thống & Thiết Bị Acc** | `MinSign_Init(cfgJson)` | — | Khởi tạo SDK với `apiKey` (bắt buộc), `signerUrl`, `vaultFilePath`, `vaultSecret`, `defaultCountry`. |
| | `MinSign_CheckApiKey()` | `check_api_key` | Kiểm tra hạn mức Quota trong ngày, gói thuê, tốc độ RPM và số dư ví của `X-API-Key`. |
| | `MinSign_BindAccountDevice(json)` | `bind_account_device` | Gắn trước & đồng bộ cố định 1 máy Android cho 1 `cookie` / `accountId` và lưu vào `devices_vault.json`. |
| | `MinSign_ListLocalDevices()` | `list_local_devices` | Lấy danh sách toàn bộ cặp `Acc <-> Thiết bị` đang lưu trên máy Client. |
| | `MinSign_RemoveLocalDevice(json)` | `remove_local_device` | Xóa 1 hồ sơ thiết bị khỏi `devices_vault.json` theo `accountKey` (khi muốn đổi máy mới cho nick). |
| | `MinSign_SignRaw(json)` | `sign_raw` | Chỉ xin bộ Header chữ ký bảo mật từ Server Ký (tự động giữ cố định máy theo Acc). |
| **2. Sản Phẩm & Gian Hàng (8 Quốc Gia)** | `MinSign_GetProductDetail(json)` | `get_product_detail` | Lấy chi tiết sản phẩm đầy đủ (tên, giá, tồn kho, đã bán, biến thể `models`, bộ ảnh HD, video, thông tin Shop). Hỗ trợ truyền link rút gọn, link SP hoặc `shopId` + `itemId`. |
| | `MinSign_GetShopOverview(json)` | `get_shop_overview` | Lấy hồ sơ gian hàng từ `shopUrl`, `shopId` hoặc `username` (tự động giải `shopId -> username` cho cả VN, TW, PH, MY, TH, ID, SG, BR). |
| | `MinSign_GetShopProducts(json)` | `get_shop_products` | Lấy danh sách sản phẩm trong gian hàng có phân trang (`limit`, `offset`) + fallback tìm kiếm nội bộ shop. |
| | `MinSign_GetShopNewestProducts(json)` | `get_shop_newest_products` | **[MỚI v1.1 — Chuyên Dụng Affiliate]** Lấy danh sách **sản phẩm MỚI NHẤT vừa lên kệ của Shop theo thời gian thực** (kết hợp 3 tầng: `rcmd_items?sort_type=2` + `affiliate/offer/product/list` kèm hoa hồng + Zero-Cookie Index). Hỗ trợ lọc `sinceItemId`, `sinceTimestamp`, `withinHours` để làm Bot canh hàng mới tự động! |
| | `MinSign_GetShopCategories(json)` | `get_shop_categories` | Lấy danh sách danh mục con của gian hàng (`get_categories`). |
| | `MinSign_GetShopVouchers(json)` | `get_shop_vouchers` | Quét toàn bộ mã giảm giá / Voucher đang mở của gian hàng (`get_shop_vouchers_by_shopid`). |
| | `MinSign_SearchProducts(json)` | `search_products` | Tìm kiếm sản phẩm theo từ khóa (`keyword`, `sortBy`: `relevancy`/`sales`/`ctime`/`price`, `page`, `limit`). |
| | `MinSign_GetCategoryTree(json)` | `get_category_tree` | Lấy toàn bộ cây danh mục ngành hàng chính thức của Shopee theo quốc gia. |
| **3. Đăng Video Shopee & Affiliate** | `MinSign_UploadShopeeVideo(json)` | `upload_shopee_video` | **Pipeline 4 bước Pure API đăng Shopee Video hoàn chỉnh**: Tự đổi vân tay MP4 tạm $\rightarrow$ `vod/preupload` $\rightarrow$ giải mã AES-128-CBC VOD Token & đẩy file MP4 lên CDN (`WCS-Android-SDK`) $\rightarrow$ `vod/reportupload` $\rightarrow$ ký `biz/post/precheck` & `biz/post/create` (hỗ trợ gắn tối đa **6 link/sản phẩm Affiliate** vào giỏ hàng vàng + chế độ `normal` hoặc `duet`). |
| | `MinSign_PrecheckVideoUpload(json)` | `precheck_video_upload` | Kiểm tra nhanh Cookie tài khoản còn sống và có quyền đăng Shopee Video hay không. |
| | `MinSign_GetAffiliateProducts(json)` | `get_affiliate_products` | Truy vấn danh sách sản phẩm gợi ý gắn giỏ hàng Affiliate (`affiliate.shopee.*/api/v3/offer/product/list`). |
| | `MinSign_MutateMp4Fingerprint(json)` | `mutate_mp4_fingerprint` | Biến đổi nhị phân file `.mp4` (`mvhd`/`tkhd`/`mdhd` timestamps + chèn atom `free` ngẫu nhiên) giúp đổi mới 100% mã băm `MD5` & `SHA-256` trong `< 10ms` mà không cần render lại bằng FFmpeg. |
| **4. Buff View & Kênh Shopee Video** | `MinSign_BuffVideoView(json)` | `buff_video_view` | Thực thi chuẩn **4 bước đẩy 1 lượt xem Shopee Video hợp lệ**: Giải link `shp.ee` $\rightarrow$ Ký & mở `timeline/single` lấy `view_token` $\rightarrow$ Đọc luồng byte MP4 thật (`Range: bytes=0-65535`) qua Proxy $\rightarrow$ Ký & bắn gói sự kiện `video_impression` + `video_play` + `video_play_time` lên `c-api-bit`. |
| | `MinSign_BuffVideoBatch(json)` | `buff_video_batch` | Khởi chạy **Goroutine Worker Pool đa luồng ngay trong DLL** để đẩy `targetViews` lượt xem song song với danh sách `proxies[]` và `cookies[]` xoay vòng tự động. |
| | `MinSign_GetVideoDetail(json)` | `get_video_detail` | Lấy thông tin chi tiết 1 bài đăng Shopee Video (lượt xem hiện tại, tim, bình luận, tác giả, `mp4Url`, `viewToken`). |
| | `MinSign_GetShopVideos(json)` | `get_shop_videos` | **[MỚI v1.1 — Chuyên Dụng Affiliate]** Lấy **danh sách toàn bộ Video của Shop** (`shopUrl` / `shopId` / `username` $\rightarrow$ tự động giải mã sang kênh Shopee Video `userId` + quét `/api/v2/timeline/me` hỗ trợ lật nhiều trang `maxPages`). Trả sẵn link `.mp4` CDN gốc không watermark (`mp4Url`), lượt xem/tim/comment và danh sách SP gắn giỏ vàng (`attachedProducts[]`)! |
| | `MinSign_GetChannelAndHashtagVideos(json)` | `get_channel_and_hashtag_videos` | Quét danh sách toàn bộ video của 1 Kênh người dùng (`mode: "channel"`) hoặc theo Hashtag (`mode: "hashtag"`). |
| **5. Giỏ Hàng & Mở Rộng** | `MinSign_AddToCart(json)` | `add_to_cart` | Tự động ký POST và thêm sản phẩm / phân loại (`modelId`) vào giỏ hàng tài khoản Shopee. |
| | `MinSign_ExecuteSignedRequest(json)` | `execute_signed_request` | **Hàm vạn năng**: Cho phép coder truyền bất kỳ URL API Shopee GET/POST nào — SDK tự gắn máy cố định của Acc, tự xin chữ ký Server và tự bắn qua Proxy bằng `uTLS` Android! |

---

## 4.1. Đặc Tả Chi Tiết 2 API Affiliate Chuyên Biệt Mới Nhất (`v1.1.0`)

### A. API Lấy Sản Phẩm Mới Nhất Của Shop Theo Thời Gian Thực (`get_shop_newest_products`)
Phục vụ các hệ thống **Affiliate / Reup Video / Bot Canh Hàng Mới Lên Kệ** muốn phát hiện ngay lập tức sản phẩm vừa được Shop đăng bán để tạo link Affiliate hoặc gắn giỏ hàng Shopee Video đầu tiên:

- **Input JSON (`MinSign_GetShopNewestProducts`)**:
  ```json
  {
    "shopUrl": "https://shopee.vn/lovito.vn",
    "shopId": "",
    "username": "",
    "limit": 30,
    "offset": 0,
    "sinceItemId": "28419201122",
    "sinceTimestamp": 0,
    "withinHours": 24,
    "cookie": "SPC_U=...; SPC_ST=...;",
    "proxy": "http://user:pass@ip:port",
    "country": "VN"
  }
  ```
  - **Mẹo chạy Bot thời gian thực**: Lưu lại trường `latestItemId` của lần quét trước và truyền vào `sinceItemId` ở lần quét sau — SDK sẽ chỉ trả về đúng các sản phẩm **mới hơn** vừa lên kệ (`hasNewItems: true/false`)!
  - **Về Cookie**: Truyền kèm `cookie` của bất kỳ nick phụ Shopee nào còn sống + `proxy` sẽ mở khóa 100% tab **Mới Nhất (`sort_type=2`)** trực tiếp trên App Shopee và lấy kèm tỷ lệ hoa hồng Affiliate (`commissionRateRaw`). Nếu gọi không Cookie tại `VN`, SDK tự động chuyển sang tầng Public Shop Index sắp xếp theo `itemId` giảm dần.

### B. API Lấy Danh Sách Video Của Shop (`get_shop_videos`)
Chỉ cần truyền `shopUrl`, `shopId` hoặc `username` của Shop — SDK sẽ **tự động ánh xạ sang `userId` (`request_user_id`) của kênh Shopee Video thuộc Shop đó**, ký bộ Header Shopee Video RN (`business_id=6`) và quét danh sách bài đăng:

- **Input JSON (`MinSign_GetShopVideos`)**:
  ```json
  {
    "shopUrl": "https://shopee.vn/lovito.vn",
    "limit": 20,
    "pageToken": "",
    "maxPages": 3,
    "includeProductVideos": true,
    "cookie": "SPC_U=...; SPC_ST=...;",
    "proxy": "http://user:pass@ip:port",
    "country": "VN"
  }
  ```
- **Dữ liệu bóc tách sẵn cho từng Video trong `data.videos[]`**:
  - `postId`, `videoId`, `shareUrl`, `caption`, `createTime`, `createdTimeIso`, `durationMs`
  - `mp4Url`: Link tải trực tiếp file `.mp4` gốc từ CDN Shopee (**không dính logo/watermark**)
  - `coverUrl`: Ảnh bìa HD của video
  - `views`, `likes`, `comments`, `shares`
  - `attachedProducts[]`: Danh sách sản phẩm đang gắn trong giỏ hàng vàng của video đó (`shopId`, `itemId`, `name`, `productUrl`) để hệ thống Affiliate sao chép gắn giỏ ngay lập tức!
  - *(Lưu ý: Endpoint `/api/v2/timeline/me` của Shopee Video yêu cầu truyền `cookie` tài khoản Shopee bất kỳ đang đăng nhập để xem toàn bộ danh sách video kênh).*

---

## 4.2. Chuyên Đề Tích Hợp Buff View Shopee Video Bằng SDK (Tham Số & Nguồn Lấy Chi Tiết)

Khi gọi `buff_video_view` hoặc `buff_video_batch`, nhân `minsign_sdk.dll` tự động xử lý trọn gói 4 bước chuẩn nội bộ của Shopee Video:
1. Tự động giải nén link rút gọn `https://vn.shp.ee/...` (nếu có) sang mã `post_id` gốc.
2. Xin chữ ký & mở `GET sv.<domain>/api/v2/timeline/single` qua Proxy để trích xuất `view_token`, `videoId`, `mp4Url`, `durationMs` (**1 lượt ký**).
3. Đọc luồng byte thật của file video MP4 trên CDN (`Range: bytes=0-65535` $\rightarrow$ `HTTP 206`, **0 lượt ký**).
4. Đóng gói mảng 3 sự kiện `video_impression` + `video_play` + `video_play_time` kèm `view_token` & `seg_duration`, xin chữ ký POST và bắn lên `c-api-bit.shopeemobile.com/v4/tr/<region>` qua cùng Proxy (**1 lượt ký**).

### A. Bảng Tra Cứu Toàn Bộ Tham Số Đầu Vào & Cách Lấy

| Tên Tham Số JSON (`MinSign_Invoke` / C# / Node) | Tên Tham Số Python (`minsign_sdk.py`) | Kiểu & Mặc Định | Giải Thích & Nguồn Lấy Thực Tế |
|---|---|---|---|
| `apiKey` | `api_key` *(khởi tạo `MinSignClient`)* | `string` *(Bắt buộc)* | Mã `X-API-Key` lấy tại mục **Quản Lý API Key** trên `https://vip-sign.minmintool.site/dashboard`. |
| `videoUrl` | `video_url` | `string` *(Bắt buộc nếu không có `postId`)* | Link bài đăng Shopee Video: Mở App Shopee $\rightarrow$ bấm nút **Chia sẻ (Share)** trên video $\rightarrow$ chọn **Sao chép liên kết**. Nhận cả link rút gọn (`https://vn.shp.ee/...`), link đầy đủ (`https://sv.shopee.vn/share-video/...`) hoặc trường `shareUrl` trả về từ hàm `get_shop_videos`. |
| `postId` | `post_id` | `string` (`""`) | Mã định danh bài đăng Base64 (VD: `"c4PVehg9CgChmFCrAwAAAA=="`). Nếu đã truyền `videoUrl` thì để trống `""`. Nếu lấy từ danh sách `get_shop_videos`, truyền thẳng `postId` giúp tiết kiệm 1 request giải nén link rút gọn. |
| `targetViews` | `target_views` | `int` (`10`) | *(Chỉ dùng cho `buff_video_batch`)* Tổng số lượt xem mục tiêu cần đẩy. |
| `concurrency` | `concurrency` | `int` (`5`, max `200`) | *(Chỉ dùng cho `buff_video_batch`)* Số luồng Goroutine chạy đồng thời bên trong DLL. Nên đặt $\le$ số lượng Proxy xoay trong mảng `proxies`. |
| `proxy` / `proxies` | `proxy` / `proxies` | `string` / `string[]` | Proxy xoay IPv4 Dân cư hoặc 4G (mua tại TMProxy, WWProxy, Tinsoft, ZingProxy, LunaProxy...) để mỗi lượt xem mang 1 IP thật khác nhau. Test lẻ 1–2 lượt trên máy có thể truyền `""` / `[]`. Hỗ trợ mọi định dạng: `"ip:port:user:pass"`, `"ip:port"`, `"http://user:pass@ip:port"`, `"socks5://user:pass@ip:port"`. |
| `cookie` / `cookies` | `cookie` / `cookies` | `string` / `string[]` | **Không bắt buộc!** Để trống `""` / `[]` SDK sẽ chạy chế độ **Guest Vãng Lai** (mỗi view tự cấp 1 máy Android 14 + `SPC_F` mới tinh, không cần nuôi nick Shopee). Nếu truyền Cookie nick phụ (`"SPC_U=...; SPC_ST=...;"`), lượt xem tính là người dùng đã đăng nhập và giữ cố định thiết bị theo nick trong `devices_vault.json`. |
| `watchSeconds` | `watch_seconds` | `int` (`18`) | Số giây xem video báo cáo trong sự kiện `video_play_time` (`seg_duration`). Khuyên để `15` – `25` giây. |
| `simulateWait` | *(truyền qua `invoke`)* | `bool` (`false`) | *(Chỉ dùng cho `buff_video_view`)* Nếu `true`, luồng nghỉ chờ ~3 giây trước khi bắn sự kiện kết thúc lượt xem. |
| `country` | `country` | `string` (`"VN"`) | Mã quốc gia (`"VN"`, `"TW"`, `"PH"`, `"MY"`, `"TH"`, `"ID"`, `"SG"`, `"BR"`). Tự động nhận diện nếu truyền `videoUrl` đầy đủ. |

### B. Cấu Trúc Kết Quả Trả Về (`data`)
- **Kết quả của `buff_video_view` (1 lượt xem đơn lẻ):**
  - `success` (`bool`): `true` khi `c-api-bit` xác nhận `HTTP 200`.
  - `postId`, `videoId`, `authorName`, `caption`, `currentViews`, `likes`.
  - `vodStreamStatus` (`int`, chuẩn là `206`), `vodBytesRead` (`65536`), `ubtHttpStatus` (`200`), `totalLatencyMs`.
- **Kết quả của `buff_video_batch` (Đa luồng hàng loạt):**
  - `targetViews`, `concurrency`, `successViews`, `failedViews`, `reportedViews`, `lastError`, `elapsedMs`.
  - *(Lưu ý: Bộ đếm View công khai của Shopee có độ trễ cache khoảng **30 giây – 2 phút** sau khi đẩy thành công).*

---

## 5. Ví Dụ Tích Hợp Thực Tế Cho Từng Ngôn Ngữ

### 5.1. Tích hợp với C# (.NET Framework / .NET 6 / .NET 8 / WinForms / WPF)

Copy file `bin/win-x64/minsign_sdk.dll` vào thư mục chạy `.exe` (chọn cấu hình build `x64`) và thêm file `wrappers/csharp/MinSignSdk.cs` vào Project:

```csharp
using System;
using System.Text.Json;
using MinSign;

class Program
{
    static void Main()
    {
        // 1. Khởi tạo SDK (Bắt buộc truyền X-API-Key lấy tại https://vip-sign.minmintool.site)
        using var sdk = new MinSignClient(
            apiKey: "YOUR_X_API_KEY_HERE",
            signerUrl: "https://vip-sign.minmintool.site",
            vaultFilePath: "./minsign_data/devices_vault.json",
            vaultSecret: "", // Điền mật khẩu nếu muốn mã hóa AES-256 file devices_vault.json
            defaultCountry: "VN"
        );

        // 2. Kiểm tra thông tin gói & hạn mức API Key
        JsonElement keyInfo = sdk.CheckApiKey();
        Console.WriteLine("Trạng thái API Key: " + keyInfo.GetRawText());

        string proxy = ""; // Ví dụ: "http://user:pass@103.145.22.11:8080" hoặc "103.145.22.11:8080:user:pass"
        string cookie = ""; // Có thể để trống "" khi lấy thông tin Sản phẩm / Gian hàng / Voucher!

        // 3. Lấy chi tiết sản phẩm & thông tin gian hàng (hỗ trợ cả VN, TW, PH, MY, TH, ID, SG, BR — không cần Cookie)
        JsonElement product = sdk.GetProductDetail(new
        {
            productUrl = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
            proxy,
            cookie,
            country = "VN"
        });
        Console.WriteLine("Dữ liệu SP: " + product.GetProperty("data").GetProperty("product").GetProperty("name").GetString());

        // 4. Đăng Shopee Video tự động gắn Giỏ hàng Affiliate + tự lách trùng MD5/SHA256 (cần Cookie nick đăng video)
        string videoCookie = "SPC_U=15759087777; SPC_ST=...; csrftoken=...;";
        JsonElement uploadRes = sdk.UploadShopeeVideo(new
        {
            videoPath = @"D:\Videos\review_vot_pickleball.mp4",
            caption = "Vợt Pickleball Perseus 4 bề mặt carbon cực ngon #shopeevideo #xuhuong",
            productLinks = new[] { "https://shopee.vn/product/1023922469/25294038727" },
            mutateMp4 = true,
            proxy,
            cookie = videoCookie,
            country = "VN"
        });
        Console.WriteLine("Kết quả đăng Video: " + uploadRes.GetRawText());

        // 5. Đẩy View Shopee Video:
        // - Đẩy lẻ 1 view (BuffVideoView): truyền cookie = videoCookie (chuỗi đơn, hoặc "" nếu chạy Guest)
        // - Đẩy đa luồng (BuffVideoBatch): truyền cookies = new[] { ... } (mảng Cookie xoay vòng, hoặc Array.Empty<string>() nếu chạy Guest)
        JsonElement singleView = sdk.BuffVideoView(new
        {
            videoUrl = "https://vn.shp.ee/xxxxxx",
            proxy = "103.145.22.11:8080:user:pass",
            cookie = videoCookie, // Truyền Cookie nick Shopee (hoặc "" nếu đẩy Guest vãng lai)
            watchSeconds = 18,
            country = "VN"
        });

        JsonElement batchView = sdk.BuffVideoBatch(new
        {
            videoUrl = "https://vn.shp.ee/xxxxxx",
            targetViews = 50,
            concurrency = 10,
            proxies = new[] { "103.145.22.11:8080:user:pass", "103.145.22.12:8080:user:pass" },
            cookies = new[] { videoCookie }, // Mảng Cookie các nick Shopee (hoặc Array.Empty<string>() nếu đẩy Guest)
            watchSeconds = 18,
            country = "VN"
        });
        Console.WriteLine("Kết quả Buff View Batch: " + batchView.GetRawText());
    }
}
```

---

### 5.2. Tích hợp với Python (`ctypes` chuẩn — Không cần cài thêm thư viện)

Đặt `minsign_sdk.dll` cùng thư mục với `minsign_sdk.py`:

```python
from minsign_sdk import MinSignClient

# 1. Khởi tạo SDK (kết nối vip-sign.minmintool.site + tự lưu máy cố định cho từng Acc)
sdk = MinSignClient(
    api_key="YOUR_X_API_KEY_HERE",
    dll_path="./minsign_sdk.dll",
    vault_file_path="./minsign_data/devices_vault.json",
    default_country="VN",
)

print("Phiên bản SDK:", sdk.version())
print("Thông tin Key:", sdk.check_api_key())

# 2. Lấy thông tin Shop & Voucher đa quốc gia (ví dụ Shopee Đài Loan TW)
tw_shop = sdk.get_shop_overview(shop_id="116309859", country="TW")
print("Shop TW:", tw_shop["shop"]["shopName"], "| Username:", tw_shop["shop"]["username"])

tw_vouchers = sdk.get_shop_vouchers(shop_id="116309859", country="TW")
print("Số mã giảm giá đang mở:", tw_vouchers["count"])

# 3. Gắn trước thiết bị cố định cho Cookie tài khoản Shopee
cookie_acc = "SPC_U=15759087777; SPC_ST=...; csrftoken=...;"
bound = sdk.bind_account_device(cookie=cookie_acc, country="VN")
print("Thiết bị cố định của Acc:", bound["device"]["deviceId"], bound["device"]["marketingName"])

# 4. Đẩy 1 lượt xem lẻ (buff_video_view -> truyền tham số cookie="...")
view_res = sdk.buff_video_view(
    video_url="https://sv.shopee.vn/share-video/c4PVehg9CgChmFCrAwAAAA%3D%3D",
    proxy="http://user:pass@103.145.22.11:8080",  # Để "" nếu test trực tiếp
    cookie=cookie_acc,                            # Truyền Cookie nick Shopee (hoặc để "" nếu chạy Guest vãng lai)
    watch_seconds=18,
    country="VN",
)
print("Đẩy view thành công:", view_res["success"], "| UBT HTTP:", view_res["ubtHttpStatus"])

# 4b. Đẩy hàng loạt đa luồng (buff_video_batch -> truyền mảng cookies=[...])
batch_res = sdk.buff_video_batch(
    video_url="https://sv.shopee.vn/share-video/c4PVehg9CgChmFCrAwAAAA%3D%3D",
    target_views=50,
    concurrency=10,
    proxies=["103.145.22.11:8080:user:pass"],
    cookies=[cookie_acc],  # Danh sách Cookie các nick tự xoay vòng (hoặc để [] nếu chạy Guest vãng lai)
    watch_seconds=18,
    country="VN",
)
print("Batch hoàn tất:", batch_res["successViews"], "/", batch_res["targetViews"])

# 5. Đổi mới MD5/SHA256 file MP4 trong 5ms (chống quét trùng video hàng loạt)
mut = sdk.mutate_mp4_fingerprint("video_goc.mp4", "video_up_nick1.mp4")
print("SHA256 mới:", mut["newSha256"])
```

---

### 5.3. Tích hợp với Node.js / Electron (`npm install koffi` — Chạy Bất Đồng Bộ Không Đơ UI)

```javascript
const { MinSignClient } = require("./wrappers/nodejs/minsign_sdk");

async function main() {
  const sdk = new MinSignClient({
    apiKey: "YOUR_X_API_KEY_HERE",
    dllPath: "./bin/win-x64/minsign_sdk.dll",
    vaultFilePath: "./minsign_data/devices_vault.json",
    defaultCountry: "VN",
  });

  // Kiểm tra hạn mức Key (Async Worker Thread — không bao giờ làm đơ Main Thread Electron)
  const keyStatus = await sdk.checkApiKey();
  console.log("Hạn mức Key:", keyStatus);

  // Quét thông tin gian hàng Apple Flagship Store VN
  const shop = await sdk.getShopOverview({ username: "apple_flagship_store", country: "VN" });
  console.log("Gian hàng:", shop.shop.shopName, "| Người theo dõi:", shop.shop.followerCount);

  // Chạy Buff View đa luồng ngay trong nhân DLL (truyền cookies: [...] hoặc buffVideoView truyền cookie: "...")
  const batch = await sdk.buffVideoBatch({
    postId: "c4PVehg9CgChmFCrAwAAAA==",
    targetViews: 20,
    concurrency: 5,
    proxies: ["http://user:pass@103.145.22.11:8080"],
    cookies: ["SPC_U=15759087777; SPC_ST=...;"], // Mảng Cookie các nick (hoặc để [] nếu chạy Guest)
    watchSeconds: 18,
    country: "VN",
  });
  console.log("Hoàn tất Batch:", batch.successViews, "/", batch.targetViews);
}

main().catch(console.error);
```

---

### 5.4. Tích hợp với C / C++ Hoặc Bất Kỳ Ngôn Ngữ Nào Khác (AutoIt, Delphi, PHP FFI, Rust)

Mọi ngôn ngữ chỉ cần gọi đúng **3 hàm C-ABI cốt lõi** trong `minsign_sdk.dll`:
1. `char* MinSign_Init(const char* configJsonUtf8)`
2. `char* MinSign_Invoke(const char* actionUtf8, const char* payloadJsonUtf8)`
3. `void MinSign_Free(void* ptr)` *(Luôn gọi hàm này sau khi đọc xong chuỗi JSON trả về để giải phóng vùng nhớ C)*

Ví dụ với **C++17** (dùng sẵn `wrappers/cpp/minsign_sdk_client.hpp`):

```cpp
#include <iostream>
#include "minsign_sdk_client.hpp"

int main() {
    minsign::Client sdk(R"({
        "apiKey": "YOUR_X_API_KEY_HERE",
        "signerUrl": "https://vip-sign.minmintool.site",
        "vaultFilePath": "./minsign_data/devices_vault.json",
        "defaultCountry": "VN"
    })", "bin\\win-x64\\minsign_sdk.dll");

    std::string shopJson = sdk.getShopOverview(R"({
        "username": "apple_flagship_store",
        "country": "VN"
    })");
    std::cout << "Shop JSON: " << shopJson << std::endl;
    return 0;
}
```

---

## 6. Cấu Trúc Chuẩn Của Chuỗi JSON Phản Hồi Từ Mọi Hàm Trong DLL

Mọi hàm C-ABI của `minsign_sdk.dll` đều trả về chuỗi JSON UTF-8 đồng nhất để coder dễ parse và bắt lỗi:

- **Khi thành công (`ok: true`)**:
  ```json
  {
    "ok": true,
    "code": 0,
    "data": { ... }
  }
  ```
- **Khi có lỗi đầu vào, hết hạn mức Key hoặc lỗi kết nối Proxy (`ok: false`)**:
  ```json
  {
    "ok": false,
    "code": -1,
    "error": "Mô tả nguyên nhân lỗi rõ ràng bằng Tiếng Việt"
  }
  ```

---

*Bản quyền thuộc Hệ thống Ký Bảo Mật & API Shopee — **MinSign Cloud (`https://vip-sign.minmintool.site`)**.*
