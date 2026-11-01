#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 MinSign Native Universal SDK (minsign_sdk.dll v1.3.0)
 Ví Dụ Thực Tế: Tìm Sản Phẩm Bằng Hình Ảnh (Tương Tự / Giá Rẻ Hơn) & AI Crop
 GitHub: https://github.com/minmin2402/shopeeapi
 Lấy X-API-Key tại: https://vip-sign.minmintool.site/dashboard
================================================================================
 Chạy ngay (không cần pip install bất kỳ thư viện ngoài nào):
   python examples/image_search_shopee.py
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient, MinSignError

# ==============================================================================
# CẤU HÌNH ĐẦU VÀO
# ==============================================================================
# 1. Mã X-API-Key lấy trên https://vip-sign.minmintool.site/dashboard
API_KEY = os.environ.get("MINSIGN_API_KEY", "YOUR_X_API_KEY_HERE")

# 2. Cookie tài khoản Shopee còn sống (BẮT BUỘC có SPC_ST=... để gọi Image Search)
SHOPEE_COOKIE = os.environ.get("SHOPEE_COOKIE", "SPC_U=...; SPC_ST=...;")

# 3. Proxy riêng (Tuỳ chọn: "ip:port:user:pass" hoặc "http://user:pass@ip:port")
PROXY_URL = ""

# 4. Link ảnh mẫu để test ngay (có thể thay bằng đường dẫn file .jpg/.png/.webp trên máy!)
SAMPLE_IMAGE_URL = "https://down-vn.img.susercontent.com/file/vn-11134114-7ras8-mccff7oz208s9a"


def main() -> None:
    if API_KEY == "YOUR_X_API_KEY_HERE":
        print("[!] Vui lòng điền mã X-API-Key (biến MINSIGN_API_KEY hoặc sửa trong file).")
        return

    sdk = MinSignClient(
        api_key=API_KEY,
        signer_url="https://vip-sign.minmintool.site",
        vault_file_path="./minsign_data/devices_vault.json",
        default_country="VN",
    )
    print("[*] Phiên bản SDK:", sdk.version().get("version"))

    # --------------------------------------------------------------------------
    # BƯỚC 1: Test AI Nhận diện khung vật thể (0 tốn Cookie, 0 tốn lượt ký!)
    # --------------------------------------------------------------------------
    print("\n[1] Đang gọi AI nhận diện vùng vật thể (get_image_bounding_box - 0 lượt ký)...")
    boxes = sdk.get_image_bounding_box(
        image_url=SAMPLE_IMAGE_URL,
        country="VN",
        proxy=PROXY_URL,
    )
    print(
        f"    -> Phát hiện {boxes.get('count')} vùng vật thể | "
        f"Khung tốt nhất: {boxes.get('bestBox')} (score={boxes.get('bestScore'):.2f})"
    )

    if "SPC_ST=..." in SHOPEE_COOKIE:
        print("\n[!] Để chạy tiếp Bước 2 & 3 (Tìm SP bằng ảnh), hãy thay SHOPEE_COOKIE bằng Cookie thật có SPC_ST.")
        return

    # --------------------------------------------------------------------------
    # BƯỚC 2: Tìm danh sách sản phẩm TƯƠNG TỰ (SimilarProducts)
    # Hỗ trợ truyền: image_path="D:/anh.webp" | image_base64="..." | image_url="..." | product_url="..."
    # --------------------------------------------------------------------------
    print("\n[2] Đang tìm sản phẩm tương tự (SimilarProducts)...")
    similar = sdk.search_products_by_image(
        cookie=SHOPEE_COOKIE,
        image_url=SAMPLE_IMAGE_URL,
        force_upload=True,          # Đặt True nếu muốn test trọn vẹn luồng Upload ảnh mới lên Shopee
        auto_detect_box=True,       # Tự động dùng khung AI cắt vật thể chính
        result_type="SimilarProducts",
        offset=0,
        limit=20,
        proxy=PROXY_URL,
        country="VN",
    )
    print(
        f"    -> HTTP {similar.get('httpStatus')} | ImageID: {similar.get('imageId')} | "
        f"Tìm thấy: {similar.get('itemsCount')} SP ({similar.get('totalLatencyMs')}ms)"
    )
    for item in similar.get("items", [])[:5]:
        print(
            f"       #{item['rank']:02d} | {item['priceVnd']:>10,}đ | "
            f"Đã bán: {item['historicalSold']:>5} | {item['name'][:55]} -> {item['productUrl']}"
        )

    # --------------------------------------------------------------------------
    # BƯỚC 3: Tìm nơi bán GIÁ RẺ HƠN (CheaperOptions) dùng lại imageId vừa upload (0ms upload!)
    # --------------------------------------------------------------------------
    print("\n[3] Đang lọc các Shop bán GIÁ RẺ HƠN (CheaperOptions)...")
    cheaper = sdk.search_products_by_image(
        cookie=SHOPEE_COOKIE,
        image_id=similar["imageId"],
        result_type="CheaperOptions",
        offset=0,
        limit=20,
        proxy=PROXY_URL,
        country="VN",
    )
    print(f"    -> Phản hồi siêu tốc trong {cheaper.get('totalLatencyMs')}ms:")
    for item in cheaper.get("items", [])[:5]:
        print(
            f"       #{item['rank']:02d} | {item['priceVnd']:>10,}đ | "
            f"Đã bán: {item['historicalSold']:>5} | {item['name'][:55]}"
        )


if __name__ == "__main__":
    try:
        main()
    except MinSignError as exc:
        print(f"[Lỗi SDK]: {exc}")
