"""
Batch Product Scraper Example — MinSign Native Universal SDK v2.0.0 (Python)

Demonstrates:
  1. resolve_shopee_url        — Normalize URLs and extract shopId / itemId / region across Shopee markets.
  2. batch_get_product_details — Scrape multiple products concurrently via the native Go worker pool.
  3. get_product_ratings       — Pull customer reviews, star counts, and review media for an item.

Usage:
  set MINSIGN_API_KEY=your_api_key_here
  python examples/batch_product_scraper.py
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
    if not api_key:
        print("[!] Set MINSIGN_API_KEY first (obtain a key at https://vip-sign.minmintool.site).")
        print("    Example: set MINSIGN_API_KEY=shopee-xxxx && python examples/batch_product_scraper.py")
        return

    cookie = os.environ.get("SHOPEE_COOKIE", "").strip()
    proxy = os.environ.get("SHOPEE_PROXY", "").strip()

    sdk = MinSignClient(
        api_key=api_key,
        signer_url=os.environ.get("MINSIGN_SIGNER_URL", "https://vip-sign.minmintool.site"),
        default_country="VN",
    )

    print("SDK Version:", sdk.version())

    # Step 1: Parse and normalize mixed-format Shopee URLs across regions
    sample_urls = [
        "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
        "https://shopee.co.th/product/1834601441/57811171288",
        "https://shopee.co.id/product/2955704/26112249802",
    ]

    print("\n=== 1. Resolving Shopee URLs ===")
    resolved_items = []
    for raw_url in sample_urls:
        info = sdk.resolve_shopee_url(url=raw_url, proxy=proxy, follow_redirect=False)
        print(
            f"  [{info.get('country')}] type={info.get('urlType')} "
            f"shopId={info.get('shopId')} itemId={info.get('itemId')} "
            f"-> {info.get('canonicalProductUrl')}"
        )
        resolved_items.append(info)

    # Step 2: Concurrently fetch product details in the native Go worker pool
    print("\n=== 2. Batch Fetching Product Details (concurrency=3) ===")
    batch = sdk.batch_get_product_details(
        product_urls=[r.get("canonicalProductUrl") or u for r, u in zip(resolved_items, sample_urls)],
        country="VN",
        cookie=cookie,
        proxy=proxy,
        concurrency=3,
    )
    print(
        f"  Completed: total={batch.get('total')} succeeded={batch.get('succeeded')} "
        f"failed={batch.get('failed')} elapsedMs={batch.get('elapsedMs')}"
    )
    for idx, entry in enumerate(batch.get("results") or [], start=1):
        if entry.get("ok") is False or entry.get("error"):
            print(f"  [{idx}] ERROR: {entry.get('error')}")
            continue
        product = (entry.get("data") or entry).get("product") or entry.get("product") or {}
        print(
            f"  [{idx}] {product.get('name', 'N/A')} | "
            f"price={product.get('priceVnd') or product.get('price')} | "
            f"sold={product.get('historicalSold')} | rating={product.get('ratingStar')}"
        )

    # Step 3: Fetch top customer ratings & reviews for the first product
    first = resolved_items[0]
    print(f"\n=== 3. Fetching Ratings for shopId={first.get('shopId')} itemId={first.get('itemId')} ===")
    ratings = sdk.get_product_ratings(
        shop_id=first.get("shopId", ""),
        item_id=first.get("itemId", ""),
        country=first.get("country", "VN"),
        limit=5,
        offset=0,
        filter=0,
        type=0,
        cookie=cookie,
        proxy=proxy,
    )
    review_list = ratings.get("ratings") or ratings.get("items") or []
    print(f"  Retrieved {len(review_list)} reviews | summary={ratings.get('summary') or ratings.get('ratingSummary')}")
    for rev in review_list[:5]:
        author = rev.get("authorUsername") or rev.get("author_username") or "anonymous"
        stars = rev.get("ratingStar") or rev.get("rating_star")
        comment = (rev.get("comment") or "").replace("\n", " ").strip()[:100]
        print(f"  - [{stars}*] {author}: {comment or '(no comment)'}")


if __name__ == "__main__":
    main()
