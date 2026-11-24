"""
Affiliate Offer Hunter & Commission Tracker — MinSign Native Universal SDK v2.0.0 (Python)

Demonstrates:
  1. get_affiliate_offer_list        — Discover high-commission affiliate offers via Web Chrome Signer.
  2. batch_convert_affiliate_links   — Convert discovered product URLs into tracked affiliate short links.
  3. get_affiliate_commission_report — Query affiliate conversion & commission earnings over a date range.

Usage:
  set MINSIGN_API_KEY=your_api_key_here
  set SHOPEE_COOKIE=SPC_EC=...; SPC_U=...; csrftoken=...
  python examples/affiliate_hunter.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from wrappers.python.minsign_sdk import MinSignClient


def main() -> None:
    api_key = os.environ.get("MINSIGN_API_KEY", "").strip()
    cookie = os.environ.get("SHOPEE_COOKIE", "").strip()
    country = os.environ.get("SHOPEE_COUNTRY", "VN").strip() or "VN"
    keyword = os.environ.get("AFFILIATE_KEYWORD", "tai nghe bluetooth").strip()
    proxy = os.environ.get("SHOPEE_PROXY", "").strip()

    if not api_key or not cookie:
        print("[!] Both MINSIGN_API_KEY and SHOPEE_COOKIE environment variables are required.")
        print("    Obtain X-API-Key at https://vip-sign.minmintool.site")
        print("    Example:")
        print("      set MINSIGN_API_KEY=shopee-xxxx")
        print("      set SHOPEE_COOKIE=SPC_EC=...; SPC_U=...; csrftoken=...")
        print("      python examples/affiliate_hunter.py")
        return

    sdk = MinSignClient(
        api_key=api_key,
        signer_url=os.environ.get("MINSIGN_SIGNER_URL", "https://vip-sign.minmintool.site"),
        default_country=country,
    )

    # Step 1: Discover high-commission affiliate product offers
    print(f"=== 1. Hunting Affiliate Offers for keyword='{keyword}' ({country}) ===")
    offers_res = sdk.get_affiliate_offer_list(
        keyword=keyword,
        list_type=0,
        sort_type=1,
        page_offset=0,
        page_limit=10,
        cookie=cookie,
        country=country,
        proxy=proxy,
    )
    offers = offers_res.get("offers") or offers_res.get("items") or []
    print(f"  Found {len(offers)} affiliate offers")

    candidate_urls = []
    for idx, offer in enumerate(offers[:5], start=1):
        name = offer.get("name", "N/A")
        comm = offer.get("commissionRate") or offer.get("sellerCommissionRate")
        sales = offer.get("sales")
        link = offer.get("productLink") or ""
        print(f"  [{idx}] {name[:60]} | comm={comm} | monthlySales={sales}")
        if link:
            candidate_urls.append(link)

    # Step 2: Batch-convert discovered product URLs into tracked affiliate short links
    if candidate_urls:
        print(f"\n=== 2. Batch Converting {len(candidate_urls)} Affiliate Links ===")
        converted = sdk.batch_convert_affiliate_links(
            cookie=cookie,
            urls=candidate_urls,
            sub_id1="minsign_hunter",
            sub_id2=country.lower(),
            country=country,
            proxy=proxy,
            batch_size=10,
        )
        for row in converted.get("results") or converted.get("items") or []:
            print(f"  -> {row.get('shortLink') or row.get('affiliateUrl') or row}")
    else:
        print("\n[i] No productLink fields returned in offers; skipping batch link conversion.")

    # Step 3: Pull last 7 days of affiliate commission & conversion report
    end_ts = int(time.time())
    start_ts = end_ts - 7 * 24 * 3600
    print(f"\n=== 3. Fetching 7-Day Commission Report ({start_ts} -> {end_ts}) ===")
    report = sdk.get_affiliate_commission_report(
        start_time=start_ts,
        end_time=end_ts,
        page_offset=0,
        page_limit=10,
        cookie=cookie,
        country=country,
        proxy=proxy,
    )
    records = report.get("records") or report.get("items") or report.get("list") or []
    print(f"  Retrieved {len(records)} conversion records")
    for rec in records[:5]:
        print("  *", rec)


if __name__ == "__main__":
    main()
