#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 MinSign Native Universal SDK (minsign_sdk.dll v1.4.0)
 Ví Dụ Thực Tế: Đẩy View & Mắt Shopee Live Đa Luồng Xoay Proxy
 GitHub: https://github.com/minmin2402/shopeeapi
 Lấy X-API-Key tại: https://vip-sign.minmintool.site/dashboard
================================================================================
 Chạy ngay (không cần pip install bất kỳ thư viện ngoài nào):
   python examples/buff_view_shopee_live.py
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient


API_KEY = os.environ.get("MINSIGN_API_KEY", "YOUR_X_API_KEY_HERE")

# Hỗ trợ link chia sẻ Shopee Live đầy đủ, link rút gọn shp.ee / s.shopee.*, hoặc sessionId số trực tiếp
LIVE_URL = "https://live.shopee.vn/share?from=live&session=12345678"

PROXY_LIST = [
    # "103.145.22.11:8080:user1:pass1",
    # "http://user2:pass2@103.145.22.12:8080",
]

COOKIE_LIST = [
    # Để rỗng [] để SDK tự tạo hồ sơ Guest Android độc lập cho mỗi lượt xem
]


def main() -> None:
    if API_KEY == "YOUR_X_API_KEY_HERE":
        print("[!] Vui lòng thay YOUR_X_API_KEY_HERE bằng X-API-Key tại https://vip-sign.minmintool.site/dashboard")
        return

    sdk = MinSignClient(
        api_key=API_KEY,
        signer_url="https://vip-sign.minmintool.site",
        vault_file_path="./minsign_data/devices_vault.json",
        default_country="VN",
    )

    print(f"[*] Lấy thông tin phòng Live: {LIVE_URL}")
    detail = sdk.get_live_session_detail(
        live_url=LIVE_URL,
        proxy=PROXY_LIST[0] if PROXY_LIST else "",
        country="VN",
    )
    print(
        f"    -> Session={detail.get('sessionId')} | Room={detail.get('roomId')} | "
        f"Title={detail.get('title')} | Viewers={detail.get('viewerCount')} | MemberCnt={detail.get('memberCnt')}"
    )

    print("\n[*] Đẩy 1 lượt xem Live đơn lẻ (joinv2 -> FLV/HLS -> WebSocket HB -> SZTracker reportPB -> exit)...")
    single = sdk.buff_live_view(
        live_url=LIVE_URL,
        proxy=PROXY_LIST[0] if PROXY_LIST else "",
        cookie=COOKIE_LIST[0] if COOKIE_LIST else "",
        watch_seconds=15,
        simulate_wait=True,   # True: giữ WS /im/v1/comet đủ thời lượng để kéo mắt CCU
        connect_ws=True,
        pull_stream=True,
        report_heartbeat=True,
        send_exit=True,
        country="VN",
    )
    print("    -> Kết quả đơn lẻ:", single)

    print("\n[*] Đẩy hàng loạt đa luồng bằng buff_live_batch(...)...")
    batch = sdk.buff_live_batch(
        live_url=LIVE_URL,
        target_views=10,
        concurrency=5,
        proxies=PROXY_LIST,
        cookies=COOKIE_LIST,
        watch_seconds=15,
        simulate_wait=False,
        bypass_stream_proxy=True,  # Split-Tunnel tiết kiệm băng thông Proxy
        country="VN",
    )
    print("    -> Kết quả Batch:", batch)


if __name__ == "__main__":
    main()
