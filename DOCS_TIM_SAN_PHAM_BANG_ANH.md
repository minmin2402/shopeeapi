# CẨM NANG TÍCH HỢP TÌM KIẾM SẢN PHẨM BẰNG HÌNH ẢNH SHOPEE (`minsign_sdk.dll` v1.3.0+)

Tài liệu chuyên sâu hướng dẫn sử dụng bộ đôi hàm **`search_products_by_image`** (`MinSign_SearchProductsByImage`) và **`get_image_bounding_box`** (`MinSign_GetImageBoundingBox`) trong **MinSign Native Universal SDK (`v1.3.0+`)**.

---

## 1. Tổng Quan Cơ Chế & Chi Phí Lượt Ký

Khác với phương pháp điều khiển trình duyệt hay giả lập Android tốn RAM và dễ dính Captcha, `minsign_sdk.dll` thực thi **100% Pure HTTP** theo đúng luồng nội bộ của ứng dụng Shopee:

1. **Tự động chuẩn hóa định dạng ảnh trong RAM (`0` lượt ký):**
   - Mọi ảnh đầu vào dù ở định dạng `.webp` (tải từ 1688, Taobao, TikTok, Chrome), `.png` (dán từ Clipboard `Ctrl+V`), `.gif`, `.bmp` hay `.jpg` đều được SDK tự động giải mã và nén chuẩn `JPEG` ngay trên RAM để không bao giờ bị lỗi `ERROR_PARAMS (10002)`.
2. **Upload ảnh lên CDN Shopee (`0` lượt ký):**
   - Với file ảnh local, Base64 hoặc link ảnh ngoài sàn, SDK đẩy ảnh lên `sv.<domain>/api/v2/biz/file/image` bằng Cookie tài khoản và nhận về mã `imageId` (VD: `vn-11134114-81ztc-...`).
   - **Tối ưu Fast-Path (`0ms` upload):** Nếu bạn truyền `imageUrl` đã là link CDN Shopee (`susercontent.com/file/...`) hoặc truyền lại `imageId` khi lật sang Trang 2, Trang 3 (`offset: 20, 40...`), SDK bỏ qua hoàn toàn bước upload và trả kết quả chỉ trong `~700ms`!
3. **AI Nhận diện vùng vật thể (`get_image_bounding_box` — `0` Cookie, `0` lượt ký):**
   - Khi ảnh chụp có nhiều món đồ (ví dụ người mẫu mặc cả áo, quần, giày, túi xách), hàm `get_image_bounding_box` (hoặc cờ `autoDetectBox: true`) gọi AI của Shopee để lấy toạ độ `left,top,width,height` của từng món đồ.
4. **Truy vấn kết quả Image Search (`1` lượt ký / trang `20` sản phẩm):**
   - Trả về danh sách sản phẩm đã chuẩn hóa sạch đẹp (`itemId`, `shopId`, `name`, `priceVnd`, `displayPriceVnd`, `discountText`, `sold`, `historicalSold`, `ratingStar`, `shopLocation`, `imageUrl`, `productUrl`).

---

## 2. Lưu Ý Quan Trọng Về Cookie Khi Gọi Image Search

- API `get_image_bounding_box` (nhận diện toạ độ khung vật thể AI): **KHÔNG cần Cookie** và **tốn `0` lượt ký**.
- API `search_products_by_image` (tìm sản phẩm bằng ảnh): Máy chủ Shopee **bắt buộc phải có Cookie tài khoản Shopee còn sống (chứa `SPC_ST=...`)**.
  - Nếu thiếu `SPC_ST`, SDK sẽ chặn ngay lập tức ở tầng kiểm tra đầu vào (0ms) để **bảo vệ không làm hao bất kỳ lượt ký nào** của bạn, kèm thông báo tiếng Việt rõ ràng.
  - Bạn chỉ cần dùng 1 hoặc vài Cookie tài khoản Buyer phụ thông thường (kèm Proxy dân cư tương ứng nếu quét số lượng lớn) là có thể tra cứu liên tục rất bền bỉ.

---

## 3. Năm Nguồn Ảnh Đầu Vào Linh Hoạt

Khi gọi `search_products_by_image`, bạn chỉ cần truyền **1 trong 5 trường nguồn ảnh** dưới đây:

| STT | Trường Đầu Vào | Khi Nào Nên Dùng? | Ví Dụ Giá Trị |
|---|---|---|---|
| **1** | `imagePath` (`image_path`) | Người dùng bấm nút **Chọn File Ảnh** trên máy tính (`.jpg`, `.png`, `.webp`, `.bmp`, `.gif`) | `"D:/1688/mau_tui_xach.webp"` |
| **2** | `imageBase64` (`image_base64`) | Người dùng chụp màn hình (`Win+Shift+S`) rồi bấm **`Ctrl+V`** dán thẳng vào ô tìm kiếm trên Tool | `"data:image/png;base64,iVBORw0KGgo..."` |
| **3** | `imageUrl` (`image_url`) | Dán link ảnh bất kỳ từ **TikTok Shop / Douyin / 1688 / Taobao / Facebook**, hoặc link ảnh CDN Shopee | `"https://p16-sign-sg.tiktokcdn.com/..."` |
| **4** | `productUrl` (`product_url`) | Dán link 1 sản phẩm Shopee để tìm toàn bộ các Shop khác đang bán mẫu y hệt nhưng **giá rẻ hơn** | `"https://shopee.vn/...-i.1023922469.25294038727"` |
| **5** | `imageId` (`image_id`) | Khi lật sang **Trang 2, Trang 3...** (`offset = 20, 40...`), truyền lại `res.imageId` từ Trang 1 để không phải upload lại ảnh | `"vn-11134114-81ztc-mv06c0iux5he52"` |

---

## 4. Chọn Chế Độ Sắp Xếp Kết Quả (`resultType`)

- **`"SimilarProducts"` *(Mặc định)*:** Ưu tiên độ giống nhau cao nhất về thị giác, kiểu dáng, màu sắc và hoa văn.
- **`"CheaperOptions"`:** Ưu tiên lọc các gian hàng đang bán mẫu sản phẩm tương tự với **mức giá thấp hơn** — cực kỳ hữu ích cho:
  - Công cụ **Săn nguồn hàng / Dropship / Nhập sỉ**.
  - Công cụ **So sánh giá đối thủ** cho nhà bán hàng.
  - Công cụ **Affiliate** tìm đúng sản phẩm đang hot trên TikTok ở Shop có giá tốt nhất trên Shopee để gắn giỏ Video / Livestream dễ chốt đơn nhất!

---

## 5. Kịch Bản Nâng Cao: Làm Giao Diện Kéo Khung Chọn Đồ Vật Như App Shopee

Nếu muốn làm tính năng cho người dùng bấm chọn từng món đồ trên bức ảnh (giống hệt tính năng ống kính Camera trên App Shopee):

1. **Bước 1 (`0` lượt ký, `0` Cookie):** Ngay khi người dùng chọn hoặc dán ảnh vào Tool, gọi `get_image_bounding_box`:
   ```javascript
   const boxInfo = await sdk.getImageBoundingBox({
     imagePath: "D:/outfit_full.jpg",
     country: "VN"
   });
   // boxInfo.candidateBoxes = [
   //   { left: 112, top: 42, width: 350, height: 737, score: 0.68, boxStr: "112,42,350,737" },
   //   { left: 180, top: 690, width: 210, height: 195, score: 0.54, boxStr: "180,690,210,195" }
   // ]
   ```
2. **Bước 2:** Vẽ các khung chữ nhật `candidateBoxes` đè lên ảnh preview trên UI (hoặc cho phép người dùng tự kéo chuột chọn vùng `x,y,w,h` bất kỳ theo pixel gốc của ảnh).
3. **Bước 3 (`1` lượt ký):** Khi người dùng bấm vào 1 khung (hoặc kéo khung mới), truyền chuỗi `"left,top,width,height"` vào tham số `boundingBox` của `searchProductsByImage`:
   ```javascript
   const res = await sdk.searchProductsByImage({
     cookie: userCookie,
     imagePath: "D:/outfit_full.jpg", // Lần sau chỉ cần truyền imageId: res.imageId!
     boundingBox: "180,690,210,195",  // Tìm riêng đôi giày ở góc dưới ảnh!
     resultType: "SimilarProducts",
     limit: 20
   });
   ```

---

## 6. Chạy Ngay File Ví Dụ Mẫu

Trong thư mục `examples/` đã có sẵn kịch bản mẫu chạy ngay bằng Python chuẩn (không cần cài thêm bất kỳ thư viện ngoài nào):

```bash
python examples/image_search_shopee.py
```
