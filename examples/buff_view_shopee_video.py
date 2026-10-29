#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 MinSign Native Universal SDK (minsign_sdk.dll v1.1.0)
 Ví Dụ Thực Tế: Đẩy View Shopee Video Đơn Luồng & Đa Luồng Xoay Proxy
 GitHub: https://github.com/minmin2402/shopeeapi
 Lấy X-API-Key tại: https://vip-sign.minmintool.site/dashboard
================================================================================
 Chạy ngay (không cần pip install bất kỳ thư viện ngoài nào):
   python examples/buff_view_shopee_video.py
"""
import os
import sys
from pathlib import Path

# Thêm thư mục gốc repo vào sys.path để import wrapper
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient, MinSignError


# ==============================================================================
# CẤU HÌNH CÁC THAM SỐ ĐẦU VÀO (XEM BẢNG GIẢI THÍCH TRONG README.md)
# ==============================================================================
# 1. api_key: Lấy tại mục [Quản Lý API Key] trên https://vip-sign.minmintool.site/dashboard
API_KEY = os.environ.get("MINSIGN_API_KEY", "YOUR_X_API_KEY_HERE")

# 2. video_url: Mở video trên App Shopee -> Bấm [Chia sẻ] -> [Sao chép liên kết]
#    Hỗ trợ cả link rút gọn (https://vn.shp.ee/...) lẫn link đầy đủ (https://sv.shopee.vn/share-video/...)
VIDEO_URL = "https://sv.shopee.vn/share-video/c4PVehg9CgChmFCrAwAAAA%3D%3D"

# 3. proxies: Danh sách Proxy xoay IPv4 Dân cư / 4G (mua tại TMProxy, WWProxy, Tinsoft, ZingProxy...)
#    Hỗ trợ mọi định dạng: "ip:port:user:pass", "ip:port", "http://user:pass@ip:port", "socks5://..."
#    Để mảng rỗng [] nếu muốn test thử 1-2 lượt trực tiếp bằng mạng máy tính hiện tại.
PROXY_LIST = [
    # "103.145.22.11:8080:user1:pass1",
    # "103.145.22.12:8080:user2:pass2",
    # "http://user3:pass3@103.145.22.13:8080",
]

# 4. cookies: Danh sách Cookie Shopee (Tuỳ chọn — ĐỂ RỖNG [] SDK sẽ chạy chế độ Guest tự sinh máy Android mới!)
COOKIE_LIST = [
    # "SPC_U=15759087777; SPC_ST=...;",
]


def main() -> None:
    if API_KEY == "YOUR_X_API_KEY_HERE":
        print("[!] Vui lòng thay YOUR_X_API_KEY_HERE bằng mã X-API-Key lấy trên https://vip-sign.minmintool.site/dashboard")
        return

    # Khởi tạo SDK (tự nạp bin/win-x64/minsign_sdk.dll)
    sdk = MinSignClient(
        api_key=API_KEY,
        signer_url="https://vip-sign.minmintool.site",
        vault_file_path="./minsign_data/devices_vault.json",
        default_country="VN",
    )

    # Bước A: Kiểm tra thông tin & lượt xem hiện tại của Video trước khi đẩy
    print(f"[*] Đang lấy thông tin video: {VIDEO_URL}")
    before = sdk.get_video_detail(
        video_url=VIDEO_URL,
        proxy=PROXY_LIST[0] if PROXY_LIST else "",
        country="VN",
    )
    print(
        f"    -> Tác giả: {before.get('authorName')} | PostID: {before.get('postId')} | "
        f"View hiện tại: {before.get('views')} | Tim: {before.get('likes')}"
    )

    # Bước B (Cách 1): Đẩy thử 1 lượt xem đơn lẻ (dễ theo dõi chi tiết từng bước)
    print("\n[*] Cách 1: Đẩy thử 1 lượt xem đơn lẻ bằng buff_video_view(...)...")
    single = sdk.buff_video_view(
        video_url=VIDEO_URL,
        proxy=PROXY_LIST[0] if PROXY_LIST else "",
        cookie=COOKIE_LIST[0] if COOKIE_LIST else "",
        watch_seconds=18,  # Báo cáo đã xem 18 giây
        country="VN",
    )
    print(
        f"    -> Thành công: {single.get('success')} | CDN MP4 HTTP: {single.get('vodStreamStatus')} | "
        f"Tracker UBT HTTP: {single.get('ubtHttpStatus')} | Thời gian: {single.get('totalLatencyMs')}ms"
    )

    # Bước C (Cách 2): Đẩy hàng loạt đa luồng ngay trong nhân DLL bằng buff_video_batch(...)
    print("\n[*] Cách 2: Đẩy Batch đa luồng xoay Proxy bằng buff_video_batch(...)...")
    batch = sdk.buff_video_batch(
        video_url=VIDEO_URL,
        target_views=5,      # Tổng số view muốn đẩy (tăng lên 50, 200, 1000 khi có dàn Proxy xoay)
        concurrency=3,       # Số luồng chạy song song bên trong DLL (tối đa 200)
        proxies=PROXY_LIST,  # Tự động xoay vòng danh sách Proxy
        cookies=COOKIE_LIST, # Để [] = Chế độ Guest vãng lai không cần nuôi nick
        watch_seconds=20,
        country="VN",
    )
    print(
        f"    -> Hoàn tất Batch: Thành công {batch.get('successViews')}/{batch.get('targetViews')} view "
        f"(Lỗi: {batch.get('failedViews')}) trong {batch.get('elapsedMs')}ms"
    )
    print("    -> Lưu ý: Bộ đếm View công khai trên Shopee sẽ nhảy số sau khoảng 30 giây - 2 phút.")


if __name__ == "__main__":
    try:
        main()
    except MinSignError as exc:
        print(f"[Lỗi SDK]: {exc}")
