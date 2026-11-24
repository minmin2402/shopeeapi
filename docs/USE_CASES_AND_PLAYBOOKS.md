# Production Use Cases & Automation Playbooks (`v2.0.0`)

Five end-to-end production blueprints showing how to chain `minsign_sdk.dll` v2.0.0 APIs into resilient, high-throughput Shopee systems. All examples below use the zero-dependency Python wrapper ([`wrappers/python/minsign_sdk.py`](../wrappers/python/minsign_sdk.py)), and every action maps 1:1 to Node.js/TypeScript, C#, C++, PHP FFI, Go, and Java JNA.

---

## Playbook 1: Multi-Region Batch Product & Price Monitor

**Goal:** Normalize mixed Shopee URLs (shortlinks, full slugs, cross-border VN/ID/TH/MY links), fetch live prices/stock concurrently inside the DLL's Go worker pool, and pull buyer ratings for top-performing SKUs.

**APIs Chained:** `resolve_shopee_url` → `batch_get_product_details` → `get_product_ratings`  
**Runnable Sample:** [`examples/batch_product_scraper.py`](../examples/batch_product_scraper.py)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY", default_country="VN")

raw_urls = [
    "https://shopee.co.id/product/2955704/26112249802",
    "https://shopee.co.th/product/1834601441/57811171288",
    "https://s.shopee.vn/exampleShortLink",
]
proxies = [
    "http://user:pass@proxy-1:8080",
    "http://user:pass@proxy-2:8080",
]

# Step 1: Normalize mixed URLs & expand shortlinks across all 8 regions
normalized_items = []
for u in raw_urls:
    info = sdk.resolve_shopee_url(url=u, proxy=proxies[0], follow_redirect=True)
    if info.get("urlType") == "product":
        normalized_items.append({
            "productUrl": info["canonicalProductUrl"],
            "shopId": info["shopId"],
            "itemId": info["itemId"],
        })

# Step 2: Fetch all products concurrently inside the native Go worker pool
batch = sdk.batch_get_product_details(
    items=normalized_items,
    proxies=proxies,
    concurrency=5,
)

print(f"Scraped {batch['succeeded']}/{batch['total']} items in {batch['elapsedMs']}ms")

# Step 3: Pull recent 5-star photo reviews for in-stock items
for row in batch["results"]:
    if not row.get("ok"):
        continue
    prod = row["data"]["product"]
    print(f"[{prod['shopId']}.{prod['itemId']}] {prod['name']} | Price: {prod['price']} | Stock: {prod['stock']}")

    if prod.get("stock", 0) > 0:
        reviews = sdk.get_product_ratings(
            product_url=row["productUrl"],
            limit=5,
            filter=3,  # 3 = reviews with photos/videos
            type=5,    # 5 = 5-star reviews
            proxy=proxies[0],
        )
        print(f"  -> Media Reviews: {reviews['summary'].get('rcountWithMedia', 0)}")
```

**Production Tips:**
- Cache `resolve_shopee_url` outputs for shortlinks so subsequent price checks skip the HTTP redirect hop.
- Keep `concurrency` ≤ `len(proxies)` (max `16`) to avoid IP rate-limiting on Shopee PDPs.

---

## Playbook 2: High-Commission Affiliate Bot & Revenue Tracker

**Goal:** Verify your Affiliate cookie health, discover high-commission products via the v2.0 Web Chrome 131 Signer, filter by minimum monthly sales + commission rate, batch-convert them into tracked `s.shopee.*` short links with campaign `subIds`, and pull daily conversion payouts.

**APIs Chained:** `get_account_profile` → `get_affiliate_offer_list` → `batch_convert_affiliate_links` → `get_affiliate_commission_report`  
**Runnable Sample:** [`examples/affiliate_hunter.py`](../examples/affiliate_hunter.py)

```python
import time
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY", default_country="VN")
COOKIE = "SPC_U=...; SPC_ST=...; SPC_EC=...; csrftoken=...;"
PROXY = "http://user:pass@vn-res-proxy:8080"

# Step 1: Verify cookie liveness before running the pipeline
profile = sdk.get_account_profile(cookie=COOKIE, proxy=PROXY, country="VN")
if not profile.get("alive"):
    raise RuntimeError("Affiliate cookie expired — refresh SPC_ST/SPC_EC.")
print(f"Active Affiliate Account: {profile['username']} (UID: {profile['userId']})")

# Step 2: Hunt high-commission offers via Web Chrome 131 Signer (sign_web)
offers = sdk.get_affiliate_offer_list(
    keyword="serum vitamin c",
    list_type=0,
    sort_type=1,
    page_offset=0,
    page_limit=30,
    cookie=COOKIE,
    proxy=PROXY,
    country="VN",
)

# Filter for winning products (>= 8% commission and >= 200 monthly sales)
winners = [
    item for item in offers.get("items", [])
    if float(item.get("commissionRate", 0)) >= 0.08 and int(item.get("sales", 0)) >= 200
]
print(f"Found {len(winners)} winning Affiliate products")

# Step 3: Batch convert all winners into tracked s.shopee.vn links in 1 GraphQL call
convert_items = [
    {
        "url": item["productLink"],
        "subId1": "auto_bot",
        "subId2": f"shop_{item['shopId']}",
    }
    for item in winners[:20]
]
converted = sdk.batch_convert_affiliate_links(
    cookie=COOKIE,
    items=convert_items,
    clean_product_url=True,
    batch_size=20,
    proxy=PROXY,
    country="VN",
)

for row in converted.get("results", []):
    print(f"  {row['inputUrl']}  ==>  {row['shortLink']}")

# Step 4: Pull last 7 days commission report
now = int(time.time())
report = sdk.get_affiliate_commission_report(
    start_time=now - 7 * 86400,
    end_time=now,
    page_offset=0,
    page_limit=20,
    cookie=COOKIE,
    proxy=PROXY,
    country="VN",
)
print(f"7-Day Conversions: {report.get('totalCount', 0)}")
```

---

## Playbook 3: Shopee Live Bag & Viewer Pipeline

**Goal:** Inspect a live broadcast, scrape every product pinned in the Live orange shopping bag (including Live-exclusive flash discounts), convert the top deals into your Affiliate short links, and optionally launch a multi-threaded viewer pool to boost live visibility.

**APIs Chained:** `get_live_session_detail` → `get_live_bag_items` → `batch_convert_affiliate_links` → `buff_live_batch`  
**Runnable Sample:** [`examples/live_bag_scraper.py`](../examples/live_bag_scraper.py)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY", default_country="VN")
LIVE_URL = "https://live.shopee.vn/share?session=123456789"
PROXIES = ["http://user:pass@proxy-1:8080", "http://user:pass@proxy-2:8080"]

# Step 1: Resolve Live session metadata (roomId, viewerCount, CDN streams)
session = sdk.get_live_session_detail(live_url=LIVE_URL, proxy=PROXIES[0], country="VN")
session_id = session["sessionId"]
print(f"Live Session {session_id} | Viewers: {session.get('viewerCount')} | Room: {session.get('roomId')}")

# Step 2: Paginate through all pinned Live shopping bag items
all_bag_items = []
offset = 0
while True:
    page = sdk.get_live_bag_items(
        session_id=session_id,
        offset=offset,
        limit=20,
        proxy=PROXIES[0],
        country="VN",
    )
    items = page.get("items", [])
    all_bag_items.extend(items)
    if not page.get("hasMore") or not items:
        break
    offset += 20

print(f"Extracted {len(all_bag_items)} Live Bag deals:")
for item in all_bag_items[:5]:
    print(f"  [Pinned={item.get('isPinned')}] {item['name']} | Live Price: {item['price']} ({item.get('discount', '')})")

# Step 3 (Optional): Dispatch multi-threaded WebSocket + Protobuf live viewers
live_result = sdk.buff_live_batch(
    session_id=session_id,
    target_views=20,
    concurrency=5,
    proxies=PROXIES,
    watch_seconds=20,
    stagger_ms=300,
    country="VN",
)
print(f"Live Viewer Batch: {live_result['successViews']}/{live_result['targetViews']} succeeded")
```

---

## Playbook 4: Visual Sourcing & Cheaper Product Finder

**Goal:** Take a multi-object product photo from TikTok/1688/WhatsApp, automatically detect the main object bounding box with zero signing cost, search Shopee for `CheaperOptions`, and inspect the top 5 suppliers' detailed stock & ratings in parallel.

**APIs Chained:** `get_image_bounding_box` → `search_products_by_image` → `batch_get_product_details`  
**Runnable Sample:** [`examples/image_search_shopee.py`](../examples/image_search_shopee.py)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY", default_country="VN")
COOKIE = "SPC_U=...; SPC_ST=...;"
PROXY = "http://user:pass@proxy-1:8080"
IMAGE_PATH = "D:/sourcing/tiktok_trending_bag.jpg"

# Step 1: Detect the primary product bounding box (0 cookies, 0 signing credits)
boxes = sdk.get_image_bounding_box(image_path=IMAGE_PATH, country="VN")
best_box = boxes.get("bestBox", "")
print("Detected bounding box:", best_box)

# Step 2: Pure-HTTP visual search for cheaper suppliers on Shopee
visual = sdk.search_products_by_image(
    cookie=COOKIE,
    image_path=IMAGE_PATH,
    bounding_box=best_box,
    result_type="CheaperOptions",
    limit=15,
    proxy=PROXY,
    country="VN",
)

top_urls = [item["productUrl"] for item in visual.get("items", [])[:5]]
print(f"Found {visual['itemsCount']} matches. Deep-scanning top {len(top_urls)} suppliers...")

# Step 3: Batch fetch full variants & stock for the cheapest 5 matches
details = sdk.batch_get_product_details(
    product_urls=top_urls,
    proxies=[PROXY],
    concurrency=5,
    country="VN",
)
for row in details["results"]:
    if row.get("ok"):
        p = row["data"]["product"]
        print(f"  {p['price']} | Sold: {p['historicalSold']} | Rating: {p['ratingStar']} | {row['productUrl']}")
```

---

## Playbook 5: Pure-API Shopee Video Auto-Uploader & View Booster

**Goal:** Monitor a target shop for newly listed products (`get_shop_newest_products`) and watermark-free videos (`get_shop_videos`), mutate `.mp4` binary fingerprints (`MD5`/`SHA-256`) in `<10ms` without FFmpeg, precheck the uploader account, publish a new Shopee Video with attached Affiliate cart items, and kick-start initial views.

**APIs Chained:** `precheck_video_upload` → `get_shop_videos` → `mutate_mp4_fingerprint` → `upload_shopee_video` → `buff_video_batch`  
**Runnable Sample:** [`examples/buff_view_shopee_video.py`](../examples/buff_view_shopee_video.py)

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY", default_country="VN")
COOKIE = "SPC_U=...; SPC_ST=...; csrftoken=...;"
PROXY = "http://user:pass@vn-res-proxy:8080"

# Step 1: Confirm the uploader cookie is healthy and has Video publishing rights
check = sdk.precheck_video_upload(cookie=COOKIE, proxy=PROXY, country="VN")
if not check.get("canUpload"):
    raise RuntimeError("Account cannot upload Shopee Video right now.")

# Step 2: Mutate local MP4 binary hash (<10ms, no re-encoding)
mutated = sdk.mutate_mp4_fingerprint(
    input_path="D:/videos/raw_review.mp4",
    output_path="D:/videos/unique_review_acc1.mp4",
)
print("New SHA-256:", mutated["newSha256"])

# Step 3: Upload via 4-step pure-API pipeline with Affiliate cart products
uploaded = sdk.upload_shopee_video(
    video_path=mutated["outputPath"],
    caption="Honest unboxing & durability test #shopeevideo #gadgets",
    hashtags=["shopeevideo", "gadgets"],
    product_links=[
        "https://shopee.vn/product/104187240/19894959672",
    ],
    post_mode="normal",
    mutate_mp4=False,  # Already mutated in Step 2
    cookie=COOKIE,
    proxy=PROXY,
    country="VN",
)
print("Published Post ID:", uploaded["postId"], "| Share URL:", uploaded["shareUrl"])

# Step 4: Dispatch initial views via internal multi-threaded Go worker pool
views = sdk.buff_video_batch(
    post_id=uploaded["postId"],
    target_views=30,
    concurrency=5,
    proxies=[PROXY],
    watch_seconds=18,
    country="VN",
)
print(f"Initial Views Dispatched: {views['successViews']}/{views['targetViews']}")
```
