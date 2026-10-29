"""
Quickstart Python — ShopeeAPI Native Universal SDK (minsign_sdk.dll)
Yêu cầu: Python 3.8+ (64-bit) trên Windows. Không cần cài thêm bất kỳ thư viện ngoài nào!
Đăng ký & lấy mã X-API-Key tại: https://vip-sign.minmintool.site
"""
import os
import sys
from pathlib import Path

# Tự động thêm thư mục gốc repo vào sys.path để import wrapper dễ dàng
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient


def main() -> None:
    api_key = os.environ.get("MINSIGN_API_KEY", "YOUR_X_API_KEY_HERE")
    if api_key == "YOUR_X_API_KEY_HERE":
        print("[!] Hãy thay 'YOUR_X_API_KEY_HERE' bằng mã X-API-Key lấy tại https://vip-sign.minmintool.site")
        print("    Hoặc đặt biến môi trường: set MINSIGN_API_KEY=shopee-...")
        return

    sdk = MinSignClient(
        api_key=api_key,
        signer_url="https://vip-sign.minmintool.site",
        vault_file_path="./minsign_data/devices_vault.json",
        default_country="VN",
    )

    print("1. Phiên bản SDK:", sdk.version())
    print("2. Thông tin hạn mức X-API-Key:", sdk.check_api_key())

    # Lấy chi tiết sản phẩm Shopee thật (KHÔNG cần truyền Cookie!)
    sample_url = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727"
    detail = sdk.get_product_detail(product_url=sample_url, country="VN")
    product = detail.get("product") or {}
    print("\n3. Chi tiết sản phẩm trích xuất trực tiếp:")
    print("   - Tên SP      :", product.get("name"))
    print("   - Giá bán     :", f"{product.get('priceVnd', 0):,} VNĐ")
    print("   - Đã bán      :", product.get("historicalSold"))
    print("   - Đánh giá    :", product.get("ratingStar"))
    print("   - Số phân loại:", len(product.get("models") or []))

    # Lấy hồ sơ gian hàng Shopee Đài Loan (TW) không cần Cookie
    tw_shop = sdk.get_shop_overview(shop_id="116309859", country="TW")
    print("\n4. Hồ sơ Shop Đài Loan (TW):", tw_shop.get("shop", {}).get("shopName"))

    # [MỚI v1.1.0 - AFFILIATE] Lấy sản phẩm mới nhất vừa lên kệ của Shop theo thời gian thực
    newest = sdk.get_shop_newest_products(shop_id="1023922469", limit=10, country="VN")
    print(f"\n5. SP mới nhất của Shop ({newest.get('count')} SP | latestItemId={newest.get('latestItemId')}):")
    for it in (newest.get("items") or [])[:3]:
        print("   *", it.get("itemId"), "|", it.get("name"), "|", f"{it.get('priceVnd', 0):,} VNĐ")

    # [MỚI v1.1.0 - AFFILIATE] Lấy danh sách Video của Shop (truyền kèm Cookie nick phụ để mở khóa full timeline SV)
    shop_vids = sdk.get_shop_videos(username="lovito.vn", limit=20, cookie="", country="VN")
    print(f"\n6. Kênh Video của Shop lovito.vn -> Creator userId={shop_vids.get('userId')} | Video quét được={shop_vids.get('count')}")


if __name__ == "__main__":
    main()
