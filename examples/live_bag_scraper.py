"""
Shopee Live Bag Scraper & Account Health Check — MinSign Native Universal SDK v2.0.0 (Python)

Demonstrates:
  1. get_account_profile     — Verify cookie liveness and inspect account metadata (optional if no cookie).
  2. get_live_session_detail — Fetch Shopee Live session info, viewer stats, host, and stream URLs.
  3. get_live_bag_items      — Scrape pinned shopping-bag items (prices, discounts, stock, affiliate tags).

Usage:
  set MINSIGN_API_KEY=your_api_key_here
  set SHOPEE_LIVE_URL=https://live.shopee.vn/share?from=live&session=123456789
  python examples/live_bag_scraper.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient


def main() -> None:
    api_key = os.environ.get("MINSIGN_API_KEY", "").strip()
    live_url = os.environ.get("SHOPEE_LIVE_URL", "").strip()
    session_id = os.environ.get("SHOPEE_LIVE_SESSION_ID", "").strip()
    cookie = os.environ.get("SHOPEE_COOKIE", "").strip()
    country = os.environ.get("SHOPEE_COUNTRY", "VN").strip() or "VN"
    proxy = os.environ.get("SHOPEE_PROXY", "").strip()

    if not api_key:
        print("[!] Set MINSIGN_API_KEY first (obtain a key at https://vip-sign.minmintool.site).")
        return

    sdk = MinSignClient(
        api_key=api_key,
        signer_url=os.environ.get("MINSIGN_SIGNER_URL", "https://vip-sign.minmintool.site"),
        default_country=country,
    )

    # Step 1: Optional cookie health check via get_account_profile
    if cookie:
        print("=== 1. Checking Account Cookie Health ===")
        profile = sdk.get_account_profile(cookie=cookie, country=country, proxy=proxy)
        print(
            f"  alive={profile.get('alive')} username={profile.get('username')} "
            f"userId={profile.get('userId')} shopId={profile.get('shopId')} "
            f"isSeller={profile.get('isSeller')}"
        )
    else:
        print("=== 1. Account Check Skipped (SHOPEE_COOKIE not set; continuing anonymously) ===")

    if not live_url and not session_id:
        print("\n[!] Set SHOPEE_LIVE_URL or SHOPEE_LIVE_SESSION_ID to inspect a live room.")
        print("    Example: set SHOPEE_LIVE_SESSION_ID=123456789 && python examples/live_bag_scraper.py")
        return

    # Step 2: Fetch Shopee Live session metadata
    print("\n=== 2. Fetching Live Session Detail ===")
    session = sdk.get_live_session_detail(
        live_url=live_url,
        session_id=session_id,
        cookie=cookie,
        country=country,
        proxy=proxy,
    )
    resolved_session_id = str(session.get("sessionId") or session_id)
    print(
        f"  sessionId={resolved_session_id} | title={session.get('title')} | "
        f"viewers={session.get('viewerCount') or session.get('viewers')} | "
        f"host={session.get('username') or session.get('hostName')}"
    )

    # Step 3: Scrape pinned shopping-bag items from the live session
    print("\n=== 3. Scraping Live Shopping Bag Items ===")
    bag = sdk.get_live_bag_items(
        live_url=live_url,
        session_id=resolved_session_id,
        offset=0,
        limit=20,
        country=country,
        cookie=cookie,
        proxy=proxy,
    )
    items = bag.get("items") or []
    print(f"  Retrieved {len(items)} pinned bag items (total={bag.get('total') or len(items)})")
    for idx, item in enumerate(items, start=1):
        print(
            f"  [{idx}] {item.get('name', 'N/A')[:55]} | "
            f"itemId={item.get('itemId')} shopId={item.get('shopId')} | "
            f"price={item.get('price')} | discount={item.get('discount')} | stock={item.get('stock')}"
        )


if __name__ == "__main__":
    main()
