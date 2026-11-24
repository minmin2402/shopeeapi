"""
Quickstart Python — MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll)

Requirements: Python 3.8+ (64-bit) on Windows. Zero third-party packages required!
Register & obtain your X-API-Key at: https://vip-sign.minmintool.site
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add repository root to sys.path so the official wrapper can be imported directly
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient


def main() -> None:
    api_key = os.environ.get("MINSIGN_API_KEY", "YOUR_X_API_KEY_HERE")
    if api_key == "YOUR_X_API_KEY_HERE":
        print("[!] Replace 'YOUR_X_API_KEY_HERE' with your X-API-Key from https://vip-sign.minmintool.site")
        print("    Or set the environment variable: set MINSIGN_API_KEY=shopee-...")
        return

    sdk = MinSignClient(
        api_key=api_key,
        signer_url="https://vip-sign.minmintool.site",
        vault_file_path="./minsign_data/devices_vault.json",
        default_country="VN",
    )

    print("1. SDK Version:", sdk.version())
    print("2. API Key Quota:", sdk.check_api_key())

    # [v2.0.0] Resolve any Shopee URL across all 8 regions (offline local parser, zero cookie required)
    sample_url = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727"
    resolved = sdk.resolve_shopee_url(url=sample_url)
    print(f"\n3. Resolved URL -> country={resolved.get('country')} shopId={resolved.get('shopId')} itemId={resolved.get('itemId')}")

    # Fetch live Shopee product details (no cookie required)
    detail = sdk.get_product_detail(product_url=sample_url, country="VN")
    product = detail.get("product") or {}
    print("\n4. Product Detail:")
    print("   - Name       :", product.get("name"))
    print("   - Price      :", f"{product.get('priceVnd', 0):,} VND")
    print("   - Sold       :", product.get("historicalSold"))
    print("   - Rating     :", product.get("ratingStar"))
    print("   - Variations :", len(product.get("models") or []))

    # Fetch Taiwan (TW) shop overview without cookies
    tw_shop = sdk.get_shop_overview(shop_id="116309859", country="TW")
    print("\n5. Taiwan (TW) Shop Overview:", tw_shop.get("shop", {}).get("shopName"))

    # Fetch newest products of a shop with incremental cursor support
    newest = sdk.get_shop_newest_products(shop_id="1023922469", limit=10, country="VN")
    print(f"\n6. Shop Newest Products (count={newest.get('count')} | latestItemId={newest.get('latestItemId')}):")
    for it in (newest.get("items") or [])[:3]:
        print("   *", it.get("itemId"), "|", it.get("name"), "|", f"{it.get('priceVnd', 0):,} VND")

    # Fetch shop videos (pass an active cookie to unlock the full Shopee Video timeline)
    shop_vids = sdk.get_shop_videos(username="lovito.vn", limit=20, cookie="", country="VN")
    print(f"\n7. Shop Video Channel (lovito.vn) -> creator userId={shop_vids.get('userId')} | videos={shop_vids.get('count')}")


if __name__ == "__main__":
    main()
