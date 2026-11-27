# MinSign Native Universal SDK — Complete 54-API Reference (`v2.1.0`)

**Library:** `bin/win-x64/minsign_sdk.dll` (`v2.1.0` · **54 Action APIs** · **58 C-ABI Exports**)  
**Cloud Signer:** `https://vip-sign.minmintool.site` (requires `X-API-Key`)  
**Supported Regions:** `VN` (`shopee.vn`), `ID` (`shopee.co.id`), `TH` (`shopee.co.th`), `MY` (`shopee.com.my`), `PH` (`shopee.ph`), `SG` (`shopee.sg`), `TW` (`shopee.tw`), `BR` (`shopee.com.br`)

---

## Global Conventions

### 1. Response Envelope
Every C-ABI export returns a heap-allocated UTF-8 JSON C-string (`char*`). **Callers must always free the pointer via `MinSign_Free(ptr)`** (all official wrappers handle this automatically).

```json
// Success
{
  "ok": true,
  "code": 0,
  "data": { ... }
}

// Error
{
  "ok": false,
  "code": -1,
  "error": "Descriptive error message"
}
```

### 2. Core Lifecycle Exports (4 Non-Action C-ABI Functions)

| C-ABI Signature | Purpose |
|---|---|
| `char* MinSign_Version(void)` | Returns `{"ok":true,"code":0,"data":{"version":"2.1.0",...}}`. |
| `char* MinSign_Init(const char* configJson)` | Initializes the singleton SDK client. Must be called once before invoking APIs. |
| `char* MinSign_Invoke(const char* action, const char* reqJson)` | Universal dispatcher accepting any of the 54 snake_case `action` names below. |
| `void MinSign_Free(char* ptr)` | Frees any `char*` pointer returned by the DLL. Never pass to standard `free()`. |

**`MinSign_Init` Request JSON:**
```json
{
  "apiKey": "YOUR_X_API_KEY",
  "signerUrl": "https://vip-sign.minmintool.site",
  "vaultFilePath": "./minsign_data/devices_vault.json",
  "vaultSecret": "",
  "defaultCountry": "VN",
  "timeoutMs": 25000
}
```

### 3. Proxy & Cookie Normalization
- **`proxy` / `proxies[]`**: Empty string `""` connects directly. Automatically normalizes:
  - `http://user:pass@ip:port`, `http://ip:port`
  - `socks5://user:pass@ip:port`, `socks5://ip:port`
  - `ip:port:user:pass` → `http://user:pass@ip:port`
  - `ip:port` → `http://ip:port`
- **`cookie` / `cookies[]`**: Standard header string (`"SPC_U=...; SPC_ST=...; csrftoken=...;"`). When provided, the SDK extracts `SPC_U`, loads/creates a sticky Android 14 hardware profile in `devices_vault.json`, patches `SPC_F` / `csrftoken`, and preserves device continuity. When omitted, guest/ephemeral profiles are used without polluting the vault.

---

## Table of Contents (54 Action APIs)

1. [System, Device Vault & Dual Signing (7 APIs)](#1-system-device-vault--dual-signing-7-apis)
2. [Products, Shops, Ratings & Discovery (16 APIs)](#2-products-shops-ratings--discovery-16-apis)
3. [Account, Cart & Vouchers (3 APIs)](#3-account-cart--vouchers-3-apis)
4. [Shopee Affiliate & Monetization (5 APIs)](#4-shopee-affiliate--monetization-5-apis)
5. [Shopee Video Studio, Scraper & View Booster (8 APIs)](#5-shopee-video-studio-scraper--view-booster-8-apis)
6. [Shopee Live Commerce & Viewer Engine (4 APIs)](#6-shopee-live-commerce--viewer-engine-4-apis)
7. [Universal Signed HTTP Gateway (1 API)](#7-universal-signed-http-gateway-1-api)
8. [Shopee MCN, Invitation Accept (`acp`) & Affiliate Center (10 APIs — *NEW in v2.1*)](#8-shopee-mcn-invitation-accept-acp--affiliate-center-10-apis--new-in-v21)

---

## 1. System, Device Vault & Dual Signing (7 APIs)

### 1.1 `check_api_key` (`MinSign_CheckApiKey`)
Validates your `X-API-Key` against MinSign Cloud and returns quota, plan, RPM limits, and wallet balance.
- **Request:** `{}` (or `void` via `MinSign_CheckApiKey()`)
- **Response `data`:**
```json
{
  "plan": "PRO",
  "walletBalance": 150000,
  "dailyUsed": 420,
  "dailyLimit": 50000,
  "rpmLimit": 300
}
```

### 1.2 `bind_account_device` (`MinSign_BindAccountDevice`)
Binds and persists a dedicated Android 14 hardware profile for an account in `devices_vault.json`.
- **Request:**
```json
{
  "cookie": "SPC_U=15759087777; SPC_ST=...;",
  "accountId": "",
  "country": "VN",
  "deviceId": ""
}
```
- **Response `data`:** `{ "accountKey": "VN:spcu_15759087777", "device": { "deviceId": "...", "marketingName": "...", "recommendedSpcF": "...", "recommendedUserAgent": "..." } }`

### 1.3 `list_local_devices` (`MinSign_ListLocalDevices`)
Lists all `accountKey <-> Android Device` bindings stored in the local vault file.
- **Request:** `{}` (or `void` via `MinSign_ListLocalDevices()`)
- **Response `data`:** `{ "count": 2, "devices": [ ... ] }`

### 1.4 `remove_local_device` (`MinSign_RemoveLocalDevice`)
Deletes a stored device binding from `devices_vault.json` so the next request mints a fresh hardware profile.
- **Request:** `{ "accountKey": "VN:spcu_15759087777" }`
- **Response `data`:** `{ "removed": true, "accountKey": "VN:spcu_15759087777" }`

### 1.5 `sign_raw` (`MinSign_SignRaw`) — *Updated in v2.0*
Requests dynamic Shopee security signature headers from MinSign Cloud. Supports **both** App Mobile (`clientType: "app"`, default) and Web Chrome 131 (`clientType: "web"`) modes, plus optional Layer-2 Risk Headers.
- **Request:**
```json
{
  "url": "https://mall.shopee.vn/api/v4/pdp/get_pc?shop_id=104187240&item_id=19894959672",
  "body": "",
  "clientType": "app",
  "country": "VN",
  "cookie": "",
  "accountId": "",
  "deviceId": "",
  "brand": "",
  "fetchLive": false,
  "includeRiskTokens": false,
  "attachRiskHeaders": false,
  "forceRefreshRisk": false,
  "secToken": ""
}
```
- **Response `data`:** `{ "headers": { "x-sap-ri": "...", "x-sap-sec": "...", "af-ac-enc-dat": "..." }, "patchedCookie": "...", "clientType": "app", "riskTokens": { ... } }`

### 1.6 `sign_web` (`MinSign_SignWeb`) — *NEW in v2.0*
Dedicated Chrome 131 Web Signer calling `/api/v1/web/sign` on MinSign Cloud. Required for Shopee Web & Affiliate Portal APIs (`affiliate.shopee.*`, web checkout/offer endpoints).
- **Request:**
```json
{
  "url": "https://affiliate.shopee.vn/api/v3/offer/product/list?list_type=0&sort_type=1&page_offset=0&page_limit=20",
  "body": "",
  "country": "VN",
  "cookie": "SPC_U=...; SPC_ST=...; csrftoken=...;",
  "accountId": "",
  "deviceId": "",
  "proxy": "",
  "fetchLive": false
}
```
- **Response `data`:**
```json
{
  "clientType": "web",
  "url": "https://affiliate.shopee.vn/api/v3/offer/product/list?...",
  "headers": {
    "x-sap-ri": "...",
    "x-sap-sec": "...",
    "af-ac-enc-dat": "...",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... Chrome/131.0.0.0 ..."
  },
  "patchedCookie": "SPC_F=...; SPC_U=...; SPC_ST=...; csrftoken=...;",
  "signCostMs": 32
}
```

### 1.7 `get_risk_token` (`MinSign_GetRiskToken`) — *v1.2*
Mints and caches Layer-2 Android Device Risk Tokens bound 1:1 to the account's sticky hardware profile.
- **Request:**
```json
{
  "country": "VN",
  "cookie": "SPC_U=...; SPC_ST=...;",
  "accountId": "",
  "deviceId": "",
  "brand": "",
  "forceRefresh": false,
  "secToken": ""
}
```
- **Response `data`:** `{ "afAcEncSzToken": "...", "riskToken": "...", "dfp": "...", "longToken": "...", "shpSecData": "...", "miniToken": "...", "headers": { "af-ac-enc-sz-token": "..." } }`

---

## 2. Products, Shops, Ratings & Discovery (16 APIs)

### 2.1 `resolve_shopee_url` (`MinSign_ResolveShopeeUrl`) — *NEW in v2.0*
Offline + optional redirect-following Shopee URL parser & canonical builder across all 8 regions. Recognizes product URLs (`/product/{shop}/{item}` and `-i.{shop}.{item}`), shop URLs, Shopee Video (`share-video`, `post_id`), Shopee Live (`session`), and shortlinks (`shp.ee`, `s.shopee.*`).
- **Request:**
```json
{
  "url": "https://shopee.co.th/product/1834601441/57811171288",
  "shopId": "",
  "itemId": "",
  "country": "",
  "proxy": "",
  "followRedirect": false
}
```
- **Notes:**
  - Provide either `url` OR `shopId` + `itemId` + `country` to construct a canonical product URL.
  - Set `followRedirect: true` when passing shortlinks (`https://s.shopee.vn/...`, `https://shp.ee/...`) so the SDK follows HTTP redirects via `uTLS` (+ optional `proxy`).
- **Response `data`:**
```json
{
  "urlType": "product",
  "country": "TH",
  "domain": "shopee.co.th",
  "shopId": "1834601441",
  "itemId": "57811171288",
  "postId": "",
  "sessionId": "",
  "username": "",
  "canonicalProductUrl": "https://shopee.co.th/product/1834601441/57811171288",
  "resolvedUrl": "https://shopee.co.th/product/1834601441/57811171288"
}
```
- `urlType` values: `"product"`, `"shop"`, `"video"`, `"live"`, `"shortlink"`, `"unknown"`.

### 2.2 `get_product_detail` (`MinSign_GetProductDetail`)
Fetches full product details (title, pricing, stock, historical sold, rating, tier variations, `models[]`, HD images, videos, and optional shop summary).
- **Request:**
```json
{
  "productUrl": "https://shopee.co.id/product/2955704/26112249802",
  "shopId": "",
  "itemId": "",
  "country": "ID",
  "cookie": "",
  "proxy": "http://user:pass@ip:port",
  "accountId": "",
  "includeShop": true
}
```
- **Response `data`:** `{ "country": "ID", "product": { "shopId": "...", "itemId": "...", "name": "...", "price": 125000, "priceMin": 125000, "priceMax": 150000, "stock": 420, "sold": 1200, "historicalSold": 8500, "ratingStar": 4.9, "images": [...], "models": [...] }, "shop": { ... } }`

### 2.3 `batch_get_product_details` (`MinSign_BatchGetProductDetails`) — *NEW in v2.0*
Fetches multiple products in parallel inside the DLL using a bounded Go goroutine worker pool (default concurrency `5`, maximum `16`) with automatic round-robin `proxies[]` and `cookies[]` rotation. Output `results[]` strictly preserves input order.
- **Request:**
```json
{
  "items": [
    { "shopId": "2955704", "itemId": "26112249802" },
    { "productUrl": "https://shopee.co.th/product/1834601441/57811171288" }
  ],
  "productUrls": [
    "https://shopee.vn/product/104187240/19894959672"
  ],
  "country": "VN",
  "cookie": "",
  "cookies": [],
  "proxy": "",
  "proxies": [
    "http://user:pass@proxy1:8080",
    "http://user:pass@proxy2:8080"
  ],
  "concurrency": 5
}
```
- **Response `data`:**
```json
{
  "total": 3,
  "succeeded": 3,
  "failed": 0,
  "elapsedMs": 1420,
  "results": [
    {
      "index": 0,
      "ok": true,
      "shopId": "2955704",
      "itemId": "26112249802",
      "productUrl": "https://shopee.co.id/product/2955704/26112249802",
      "data": { "product": { ... }, "shop": { ... } },
      "error": ""
    }
  ]
}
```

### 2.4 `get_product_ratings` (`MinSign_GetProductRatings`) — *NEW in v2.0*
Fetches paginated buyer reviews, star breakdown counts, comments, variation tags, and attached review images/videos via signed `api/v2/item/get_ratings`.
- **Request:**
```json
{
  "productUrl": "https://shopee.vn/product/104187240/19894959672",
  "shopId": "",
  "itemId": "",
  "limit": 20,
  "offset": 0,
  "filter": 0,
  "type": 0,
  "country": "VN",
  "cookie": "",
  "proxy": ""
}
```
- **Filter Reference:** `filter`: `0` = all, `1` = with comment, `3` = with media (photos/videos). `type`: `0` = all stars, `1..5` = specific star count.
- **Response `data`:**
```json
{
  "country": "VN",
  "shopId": "104187240",
  "itemId": "19894959672",
  "offset": 0,
  "limit": 20,
  "total": 1245,
  "summary": {
    "ratingTotal": 1245,
    "rcountWithContext": 612,
    "rcountWithImage": 298,
    "rcountWithMedia": 310,
    "starCounts": [12, 8, 25, 110, 1090]
  },
  "ratings": [
    {
      "cmtid": "19283746501",
      "authorUsername": "buyer***1",
      "ratingStar": 5,
      "comment": "Fast shipping, authentic quality!",
      "ctime": 1732400000,
      "images": ["https://down-vn.img.susercontent.com/file/..."],
      "videos": []
    }
  ],
  "raw": { ... }
}
```

### 2.5 `get_flash_sale_items` (`MinSign_GetFlashSaleItems`) — *NEW in v2.0*
Fetches active Flash Sale sessions (`api/v4/flash_sale/get_all_sessions` when `promotionId` is `0`) and loads discounted flash-sale items (`flash_sale_batch_get_items` / `get_all_itemids`).
- **Request:**
```json
{
  "promotionId": 0,
  "limit": 20,
  "offset": 0,
  "country": "ID",
  "cookie": "",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "ID",
  "promotionId": 248192011223,
  "sessions": [
    { "promotionId": 248192011223, "startTime": 1732410000, "endTime": 1732424400, "name": "12:00" }
  ],
  "total": 200,
  "count": 20,
  "items": [
    {
      "itemId": "26112249802",
      "shopId": "2955704",
      "name": "...",
      "price": 89000,
      "priceBeforeDiscount": 199000,
      "discount": "55%",
      "stock": 42,
      "flashSaleStock": 100,
      "imageUrl": "https://down-id.img.susercontent.com/file/...",
      "productUrl": "https://shopee.co.id/product/2955704/26112249802"
    }
  ],
  "raw": { ... }
}
```

### 2.6 `get_recommend_products` (`MinSign_GetRecommendProducts`) — *NEW in v2.0*
Fetches personalized or item-contextual Shopee recommendation feeds via `api/v4/recommend/recommend`. Defaults `bundle` to `"item_detail_similar_items"` when `itemId` is present, or `"daily_discover_main"` otherwise.
- **Request:**
```json
{
  "bundle": "item_detail_similar_items",
  "shopId": "104187240",
  "itemId": "19894959672",
  "limit": 20,
  "offset": 0,
  "country": "VN",
  "cookie": "",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "bundle": "item_detail_similar_items",
  "offset": 0,
  "limit": 20,
  "count": 20,
  "items": [
    {
      "itemId": "...",
      "shopId": "...",
      "name": "...",
      "price": 199000,
      "historicalSold": 3200,
      "ratingStar": 4.9,
      "imageUrl": "...",
      "productUrl": "https://shopee.vn/product/..."
    }
  ],
  "raw": { ... }
}
```

### 2.7 `get_search_suggestions` (`MinSign_GetSearchSuggestions`) — *NEW in v2.0*
Fetches live autocomplete search hints and trending query completions via `api/v4/search/search_suggestion` / `search_hint`.
- **Request:**
```json
{
  "keyword": "iphone 16",
  "limit": 10,
  "country": "VN",
  "cookie": "",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "keyword": "iphone 16",
  "count": 10,
  "suggestions": [
    "iphone 16 pro max",
    "iphone 16 case",
    "iphone 16 screen protector"
  ],
  "raw": { ... }
}
```

### 2.8 `search_products` (`MinSign_SearchProducts`)
Searches Shopee products by keyword with sort options (`relevancy`, `sales`, `ctime`, `price`).
- **Request:** `{ "keyword": "mechanical keyboard", "country": "VN", "sortBy": "sales", "page": 0, "limit": 20, "proxy": "", "cookie": "" }`
- **Response `data`:** `{ "country": "VN", "keyword": "...", "totalCount": 1200, "items": [ ... ] }`

### 2.9 `search_products_by_image` (`MinSign_SearchProductsByImage`) — *v1.3*
Pure-HTTP visual search (`SimilarProducts` or `CheaperOptions`). Requires a live cookie with `SPC_ST`. Accepts 1 of 5 image sources: `imagePath`, `imageBase64`, `imageUrl`, `imageId`, or `productUrl` (`shopId`+`itemId`).
- **Request:**
```json
{
  "cookie": "SPC_U=...; SPC_ST=...;",
  "imagePath": "D:/sample.jpg",
  "imageBase64": "",
  "imageUrl": "",
  "imageId": "",
  "productUrl": "",
  "shopId": "",
  "itemId": "",
  "country": "VN",
  "resultType": "CheaperOptions",
  "offset": 0,
  "limit": 20,
  "boundingBox": "",
  "autoDetectBox": false,
  "forceUpload": false,
  "proxy": "",
  "accountId": "",
  "deviceId": ""
}
```
- **Response `data`:** `{ "imageId": "...", "uploadedImageUrl": "...", "resultType": "CheaperOptions", "itemsCount": 20, "hasMore": true, "nextOffset": 20, "items": [ { "rank": 1, "shopId": "...", "itemId": "...", "name": "...", "priceVnd": 299000, "historicalSold": 1500, "productUrl": "..." } ] }`

### 2.10 `get_image_bounding_box` (`MinSign_GetImageBoundingBox`) — *v1.3*
Detects object bounding boxes in multi-item images (`0` cookies, `0` signing credits).
- **Request:** `{ "imagePath": "D:/scene.jpg", "imageBase64": "", "imageUrl": "", "country": "VN", "imageSource": "local", "proxy": "" }`
- **Response `data`:** `{ "bestBox": "112,42,350,737", "boxes": [ { "left": 112, "top": 42, "width": 350, "height": 737, "label": "..." } ] }`

### 2.11 `get_shop_overview` (`MinSign_GetShopOverview`)
Retrieves shop profile metadata (name, followers, rating, official/mall flags, Shopee Video `userId`) across all 8 regions.
- **Request:** `{ "shopUrl": "", "shopId": "", "username": "lovito.vn", "country": "VN", "proxy": "", "cookie": "" }`
- **Response `data`:** `{ "shop": { "shopId": "...", "userId": "...", "username": "lovito.vn", "shopName": "...", "followerCount": 520000, "ratingStar": 4.9, "isOfficialShop": true } }`

### 2.12 `get_shop_products` (`MinSign_GetShopProducts`)
Lists paginated products belonging to a shop.
- **Request:** `{ "shopId": "104187240", "shopUrl": "", "limit": 30, "offset": 0, "country": "VN", "proxy": "", "cookie": "" }`
- **Response `data`:** `{ "count": 30, "items": [ ... ] }`

### 2.13 `get_shop_newest_products` (`MinSign_GetShopNewestProducts`) — *v1.1*
Monitors newly listed shop products in real time with incremental cursor filters (`sinceItemId`, `sinceTimestamp`, `withinHours`).
- **Request:** `{ "shopUrl": "https://shopee.vn/lovito.vn", "shopId": "", "username": "", "limit": 30, "offset": 0, "sinceItemId": "", "sinceTimestamp": 0, "withinHours": 24, "country": "VN", "cookie": "", "proxy": "", "accountId": "" }`
- **Response `data`:** `{ "latestItemId": "...", "hasNewItems": true, "count": 12, "items": [ ... ] }`

### 2.14 `get_shop_categories` (`MinSign_GetShopCategories`)
Lists a shop's custom storefront categories.
- **Request:** `{ "shopId": "104187240", "shopUrl": "", "country": "VN", "proxy": "", "cookie": "" }`
- **Response `data`:** `{ "categories": [ { "shopCategoryId": 12345, "displayName": "Best Sellers", "total": 45 } ] }`

### 2.15 `get_shop_vouchers` (`MinSign_GetShopVouchers`)
Scrapes all currently active vouchers offered by a shop.
- **Request:** `{ "shopId": "104187240", "shopUrl": "", "country": "VN", "proxy": "", "cookie": "" }`
- **Response `data`:** `{ "count": 5, "vouchers": [ { "voucherCode": "...", "promotionId": 99887766, "signature": "...", "discountValue": 20000, "minSpend": 150000 } ] }`

### 2.16 `get_category_tree` (`MinSign_GetCategoryTree`)
Fetches the official Shopee category hierarchy for a region.
- **Request:** `{ "country": "VN", "proxy": "" }`
- **Response `data`:** `{ "country": "VN", "categories": [ ... ] }`

---

## 3. Account, Cart & Vouchers (3 APIs)

### 3.1 `get_account_profile` (`MinSign_GetAccountProfile`) — *NEW in v2.0*
Checks cookie liveness and returns profile metadata via `api/v4/account/basic/get_account_info`.
- **Request:**
```json
{
  "cookie": "SPC_U=...; SPC_ST=...; csrftoken=...;",
  "country": "VN",
  "proxy": "",
  "accountId": "",
  "deviceId": ""
}
```
- **Response `data`:**
```json
{
  "alive": true,
  "userId": "15759087777",
  "shopId": "15759087778",
  "username": "min_affiliate_vn",
  "emailVerified": true,
  "phoneVerified": true,
  "isSeller": true,
  "portrait": "https://down-vn.img.susercontent.com/file/...",
  "raw": { ... }
}
```

### 3.2 `get_cart_summary` (`MinSign_GetCartSummary`) — *NEW in v2.0*
Reads the authenticated account's shopping cart via `api/v4/cart/get` (automatic fallback to `api/v4/cart/mini`).
- **Request:**
```json
{
  "cookie": "SPC_U=...; SPC_ST=...; csrftoken=...;",
  "country": "VN",
  "proxy": "",
  "accountId": "",
  "deviceId": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "itemCount": 3,
  "subtotal": 485000,
  "shopGroups": [
    {
      "shopId": "104187240",
      "shopName": "Official Store",
      "items": [
        { "itemId": "19894959672", "modelId": "123456", "name": "...", "quantity": 1, "price": 199000 }
      ]
    }
  ],
  "raw": { ... }
}
```

### 3.3 `claim_shop_voucher` (`MinSign_ClaimShopVoucher`) — *NEW in v2.0*
Claims/saves a shop voucher into the user's voucher wallet via `POST api/v2/voucher_wallet/save_voucher` with Layer-2 Risk Headers (`attachRiskHeaders: true`) enabled automatically.
- **Request:**
```json
{
  "voucherCode": "SHOP20K",
  "promotionId": 9988776655,
  "signature": "a1b2c3d4e5...",
  "shopId": "104187240",
  "cookie": "SPC_U=...; SPC_ST=...; csrftoken=...;",
  "country": "VN",
  "proxy": "",
  "accountId": "",
  "deviceId": ""
}
```
- **Response `data`:**
```json
{
  "claimed": true,
  "promotionId": 9988776655,
  "voucherCode": "SHOP20K",
  "error": 0,
  "errorMsg": "",
  "raw": { ... }
}
```

---

## 4. Shopee Affiliate & Monetization (5 APIs)

### 4.1 `get_affiliate_offer_list` (`MinSign_GetAffiliateOfferList`) — *NEW in v2.0*
Queries the Shopee Affiliate Portal (`https://affiliate.<domain>/api/v3/offer/product/list`) signed with **Web Chrome 131 Signer (`sign_web`)** and `Affiliate-Program-Type: 1`. Ideal for hunting high-commission products.
- **Request:**
```json
{
  "keyword": "serum",
  "shopId": "",
  "listType": 0,
  "sortType": 1,
  "pageOffset": 0,
  "pageLimit": 20,
  "cookie": "SPC_U=...; SPC_ST=...; SPC_EC=...; csrftoken=...;",
  "country": "VN",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "pageOffset": 0,
  "pageLimit": 20,
  "totalCount": 500,
  "hasMore": true,
  "items": [
    {
      "itemId": "19894959672",
      "shopId": "104187240",
      "name": "Vitamin C Brightening Serum 30ml",
      "price": 249000,
      "sales": 3420,
      "commissionRate": 0.125,
      "sellerCommissionRate": 0.08,
      "imageUrl": "https://down-vn.img.susercontent.com/file/...",
      "productLink": "https://shopee.vn/product/104187240/19894959672"
    }
  ],
  "raw": { ... }
}
```

### 4.2 `get_affiliate_commission_report` (`MinSign_GetAffiliateCommissionReport`) — *NEW in v2.0*
Queries `https://affiliate.<domain>/api/v3/report/list` using **Web Chrome 131 Signer (`sign_web`)** to fetch Affiliate conversion and commission records within a Unix timestamp window.
- **Request:**
```json
{
  "startTime": 1730419200,
  "endTime": 1732492800,
  "pageOffset": 0,
  "pageLimit": 20,
  "cookie": "SPC_U=...; SPC_ST=...; SPC_EC=...; csrftoken=...;",
  "country": "VN",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "pageOffset": 0,
  "pageLimit": 20,
  "totalCount": 84,
  "records": [
    {
      "conversionId": "...",
      "orderId": "...",
      "itemId": "19894959672",
      "shopId": "104187240",
      "itemName": "...",
      "orderAmount": 249000,
      "commission": 31125,
      "status": "COMPLETED",
      "purchaseTime": 1732300000
    }
  ],
  "raw": { ... }
}
```

### 4.3 `get_affiliate_products` (`MinSign_GetAffiliateProducts`)
Fetches recommended Affiliate catalog items for attaching to Shopee Video shopping carts.
- **Request:** `{ "cookie": "...", "keyword": "", "pageOffset": 0, "pageLimit": 20, "proxy": "", "country": "VN" }`
- **Response `data`:** `{ "items": [ ... ] }`

### 4.4 `convert_affiliate_link` (`MinSign_ConvertAffiliateLink`) — *v1.5*
Converts any standard product URL, competitor `aff_id` link, `universal-link`, or shortlink into your own tracked `s.shopee.*` Affiliate short link via `affiliate.shopee.*/api/v3/gql?q=batchCustomLink`.
- **Request:**
```json
{
  "url": "https://shopee.vn/product/104187240/19894959672",
  "cookie": "SPC_U=...; SPC_EC=...; csrftoken=...;",
  "subId1": "tiktok_bio",
  "subId2": "camp_nov",
  "subId3": "",
  "subId4": "",
  "subId5": "",
  "subIds": [],
  "country": "",
  "proxy": "",
  "cleanProductUrl": true,
  "resolveShortLinks": true,
  "signRequest": true,
  "accountId": "",
  "deviceId": ""
}
```
- **Response `data`:** `{ "inputUrl": "...", "shortLink": "https://s.shopee.vn/...", "longLink": "https://shopee.vn/universal-link/...", "country": "VN" }`

### 4.5 `batch_convert_affiliate_links` (`MinSign_BatchConvertAffiliateLinks`) — *v1.5*
Batch converts and shortens multiple URLs in auto-chunked GraphQL calls (`batchSize` 20–50) with optional per-item `subId1..5`.
- **Request:**
```json
{
  "cookie": "SPC_U=...; SPC_EC=...; csrftoken=...;",
  "urls": ["https://shopee.vn/product/104187240/19894959672"],
  "items": [
    { "url": "https://shopee.co.th/product/1834601441/57811171288", "subId1": "th_bot" }
  ],
  "subIds": ["default_campaign"],
  "batchSize": 20,
  "cleanProductUrl": true,
  "resolveShortLinks": true,
  "signRequest": true,
  "country": "",
  "proxy": ""
}
```
- **Response `data`:** `{ "total": 2, "succeeded": 2, "results": [ { "inputUrl": "...", "shortLink": "https://s.shopee.vn/...", "longLink": "...", "ok": true } ] }`

---

## 5. Shopee Video Studio, Scraper & View Booster (8 APIs)

### 5.1 `upload_shopee_video` (`MinSign_UploadShopeeVideo`)
Complete 4-step pure-API Shopee Video upload pipeline (`mutate_mp4` → `vod/preupload` → AES-128-CBC VOD token decode & CDN upload → `vod/reportupload` → `biz/post/precheck` & `biz/post/create`) supporting up to 6 Affiliate cart products and `normal`/`duet` modes.
- **Request:**
```json
{
  "videoPath": "D:/videos/review.mp4",
  "coverPath": "",
  "caption": "Must-have wireless earbuds #shopeevideo",
  "hashtags": ["shopeevideo", "gadgets"],
  "products": [],
  "productLinks": ["https://shopee.vn/product/104187240/19894959672"],
  "postMode": "normal",
  "mutateMp4": true,
  "cookie": "SPC_U=...; SPC_ST=...;",
  "proxy": "",
  "country": "VN",
  "accountId": ""
}
```
- **Response `data`:** `{ "postId": "...", "videoId": "...", "shareUrl": "https://sv.shopee.vn/share-video/..." }`

### 5.2 `precheck_video_upload` (`MinSign_PrecheckVideoUpload`)
Verifies whether the account cookie is active and permitted to publish Shopee Videos.
- **Request:** `{ "cookie": "...", "proxy": "", "country": "VN", "accountId": "" }`
- **Response `data`:** `{ "canUpload": true, "userId": "..." }`

### 5.3 `mutate_mp4_fingerprint` (`MinSign_MutateMp4Fingerprint`)
Mutates `.mp4` atom metadata (`mvhd`/`tkhd`/`mdhd` timestamps + random `free` atom) to generate a brand-new `MD5` and `SHA-256` hash in `<10ms` without FFmpeg.
- **Request:** `{ "inputPath": "D:/orig.mp4", "outputPath": "D:/unique.mp4", "inPlace": false }`
- **Response `data`:** `{ "outputPath": "D:/unique.mp4", "oldSha256": "...", "newSha256": "...", "elapsedMs": 4 }`

### 5.4 `buff_video_view` (`MinSign_BuffVideoView`)
Executes 1 full 4-step Shopee Video view over proxy (`shp.ee` resolve → `timeline/single` → MP4 byte-range `0-65535` → `c-api-bit` telemetry).
- **Request:** `{ "videoUrl": "https://vn.shp.ee/...", "postId": "", "proxy": "", "cookie": "", "watchSeconds": 18, "country": "VN", "accountId": "", "deviceId": "", "simulateWait": false }`
- **Response `data`:** `{ "success": true, "postId": "...", "vodStreamStatus": 206, "vodBytesRead": 65536, "ubtHttpStatus": 200, "totalLatencyMs": 1150 }`

### 5.5 `buff_video_batch` (`MinSign_BuffVideoBatch`)
Launches an internal Go Goroutine worker pool dispatching `targetViews` views concurrently with `proxies[]` and `cookies[]` rotation.
- **Request:** `{ "videoUrl": "...", "postId": "", "targetViews": 50, "concurrency": 10, "proxies": [...], "cookies": [], "watchSeconds": 18, "country": "VN" }`
- **Response `data`:** `{ "targetViews": 50, "successViews": 50, "failedViews": 0, "elapsedMs": 8200 }`

### 5.6 `get_video_detail` (`MinSign_GetVideoDetail`)
Fetches metadata, engagement counters, and watermark-free `mp4Url` for a single Shopee Video post.
- **Request:** `{ "videoUrl": "", "postId": "c4PVehg9CgChmFCrAwAAAA==", "proxy": "", "cookie": "", "country": "VN" }`
- **Response `data`:** `{ "postId": "...", "videoId": "...", "views": 12400, "likes": 430, "comments": 19, "mp4Url": "https://..." }`

### 5.7 `get_shop_videos` (`MinSign_GetShopVideos`) — *v1.1*
Resolves a shop to its Shopee Video channel and scrapes paginated videos including watermark-free `mp4Url` and `attachedProducts[]`.
- **Request:** `{ "shopUrl": "https://shopee.vn/lovito.vn", "shopId": "", "username": "", "userId": "", "limit": 20, "pageToken": "", "maxPages": 3, "includeProductVideos": true, "cookie": "...", "proxy": "", "country": "VN", "accountId": "" }`
- **Response `data`:** `{ "userId": "...", "nextPageToken": "...", "videos": [ { "postId": "...", "mp4Url": "...", "coverUrl": "...", "views": 5000, "attachedProducts": [ { "shopId": "...", "itemId": "...", "productUrl": "..." } ] } ] }`

### 5.8 `get_channel_and_hashtag_videos` (`MinSign_GetChannelAndHashtagVideos`)
Scrapes videos by channel `requestUserId` (`mode: "channel"`) or by `hashtagId` (`mode: "hashtag"`).
- **Request:** `{ "mode": "channel", "requestUserId": "12345678", "hashtagId": "", "limit": 20, "proxy": "", "cookie": "", "country": "VN" }`
- **Response `data`:** `{ "videos": [ ... ] }`

---

## 6. Shopee Live Commerce & Viewer Engine (4 APIs)

### 6.1 `get_live_session_detail` (`MinSign_GetLiveSessionDetail`) — *v1.4*
Resolves Live URLs (`live.shopee.*`, `shp.ee`) or `sessionId` and returns live room telemetry, viewer counts, and CDN FLV/HLS stream URLs.
- **Request:** `{ "liveUrl": "https://live.shopee.vn/share?session=123456789", "sessionId": "", "proxy": "", "cookie": "", "country": "VN", "accountId": "", "deviceId": "" }`
- **Response `data`:** `{ "sessionId": "123456789", "roomId": "...", "title": "...", "viewerCount": 342, "memberCnt": 1200, "usersig": "...", "playUrls": [ ... ] }`

### 6.2 `get_live_bag_items` (`MinSign_GetLiveBagItems`) — *NEW in v2.0*
Resolves `liveUrl` or `sessionId` and queries `https://live.<domain>/api/v1/session/{sessionId}/more_items` to scrape products pinned in the Live shopping bag (orange basket), including Live-exclusive prices, discounts, stock, and affiliate metadata.
- **Request:**
```json
{
  "liveUrl": "https://live.shopee.vn/share?session=123456789",
  "sessionId": "",
  "offset": 0,
  "limit": 20,
  "country": "VN",
  "cookie": "",
  "proxy": ""
}
```
- **Response `data`:**
```json
{
  "country": "VN",
  "sessionId": "123456789",
  "offset": 0,
  "limit": 20,
  "totalCount": 34,
  "hasMore": true,
  "items": [
    {
      "itemId": "19894959672",
      "shopId": "104187240",
      "name": "Flash Live Deal — Wireless Earbuds",
      "price": 179000,
      "priceBeforeDiscount": 350000,
      "discount": "49%",
      "stock": 85,
      "isPinned": true,
      "imageUrl": "https://down-vn.img.susercontent.com/file/...",
      "productUrl": "https://shopee.vn/product/104187240/19894959672"
    }
  ],
  "raw": { ... }
}
```

### 6.3 `buff_live_view` (`MinSign_BuffLiveView`) — *v1.4*
Executes 1 full Shopee Live viewer session (`joinv2` → CDN FLV/HLS stream pull → RFC 6455 WebSocket `HB_REQ` → `SZTracker` `reportPB` → optional `/like` → `/exit`).
- **Request:** `{ "liveUrl": "...", "sessionId": "", "proxy": "", "cookie": "", "watchSeconds": 18, "simulateWait": false, "connectWs": true, "pullStream": true, "reportHeartbeat": true, "sendExit": true, "sendLike": false, "likeCount": 0, "bypassStreamProxy": false, "streamLiteMode": false, "country": "VN", "accountId": "", "deviceId": "", "fromSource": "share" }`
- **Response `data`:** `{ "success": true, "sessionId": "...", "wsConnected": true, "streamBytesRead": 65536, "totalLatencyMs": 2100 }`

### 6.4 `buff_live_batch` (`MinSign_BuffLiveBatch`) — *v1.4*
Multi-threaded Shopee Live viewer pool rotating `proxies[]` and `cookies[]` with optional `staggerMs` ramp-up.
- **Request:** `{ "liveUrl": "...", "sessionId": "", "targetViews": 30, "concurrency": 10, "proxies": [...], "cookies": [], "watchSeconds": 18, "staggerMs": 200, "country": "VN" }`
- **Response `data`:** `{ "targetViews": 30, "successViews": 30, "failedViews": 0, "elapsedMs": 14500 }`

---

## 7. Universal Signed HTTP Gateway (1 API)

### 7.1 `execute_signed_request` (`MinSign_ExecuteSignedRequest`) — *Updated in v2.0*
Universal signed HTTP client for calling **any** Shopee GET or POST API through `uTLS` + Proxy using either **App Mobile UniDBG (`clientType: "app"`)** or **Web Chrome 131 (`clientType: "web"`)** signing and optional Layer-2 Risk Headers.
- **Request:**
```json
{
  "url": "https://mall.shopee.vn/api/v4/cart/get",
  "method": "POST",
  "body": {},
  "clientType": "app",
  "country": "VN",
  "cookie": "SPC_U=...; SPC_ST=...;",
  "proxy": "http://user:pass@ip:port",
  "accountId": "",
  "deviceId": "",
  "brand": "",
  "includeRiskTokens": false,
  "attachRiskHeaders": true,
  "forceRefreshRisk": false,
  "secToken": "",
  "customHeaders": {
    "X-Custom-Header": "value"
  }
}
```
- **Response `data`:**
```json
{
  "httpStatus": 200,
  "clientType": "app",
  "body": { ... },
  "rawBody": "...",
  "refreshedCookie": "...",
  "signCostMs": 35,
  "totalLatencyMs": 420
}
```

---

## 8. Shopee MCN, Invitation Accept (`acp`) & Affiliate Center (10 APIs — *NEW in v2.1*)

### 8.1 `get_affiliate_user_profile` (`MinSign_GetAffiliateUserProfile`)
Queries `GET https://affiliate.<domain>/api/v3/user/profile` (Web Signer + automatic Mobile fallback) to retrieve `affiliateId`, `region`, `shopeeUserName`, `paymentSettingStatus`, `paymentSettingTaxStatus`, and `isAllowMcnSetAds`.
- **Request:** `{ "cookie": "...", "country": "VN", "proxy": "", "allowMobileFallback": true }`
- **Response `data`:** `{ "affiliateId": "...", "region": "VN", "shopeeUserName": "...", "paymentSettingStatus": 2, "paymentSettingTaxStatus": 2, "isAllowMcnSetAds": false, "raw": { ... } }`

### 8.2 `get_mcn_partnership_status` (`MinSign_GetMcnPartnershipStatus`)
Scans an Affiliate account's ongoing MCN partnership (`mcnOngoingPartnershipDetailAndPendingRequest`) and pending MCN invitations (`mcnPendingPartnershipInvitationList`) via `POST https://affiliate.<domain>/api/v3/gql`, with optional automatic REST fallback (`user/profile` + `report/list` `linked_mcn_id`).
- **Request:** `{ "cookie": "...", "country": "VN", "proxy": "", "pageNum": 1, "pageSize": 20, "fastFallback": true, "fastOnly": false, "includeEntryPoint": false }`
- **Response `data`:** `{ "source": "gql", "mcnStatus": "linked|invited|none", "mcnId": "...", "mcnName": "...", "partnershipId": "...", "mcnFeeRatePercent": 10, "displayLeftDays": 180, "invitations": [ ... ], "raw": { ... } }`

### 8.3 `reply_mcn_invitation` (`MinSign_ReplyMcnInvitation`) — Accept / Reject MCN Invite (`acp_mcn_invitation`)
Accepts (`decision: "accept"`) or rejects (`decision: "reject"`) a pending MCN invitation/request via `mutation mcnKOLReplyToMCNRequest` (`https://affiliate.<domain>/api/v3/gql?q=mcnKOLReplyToMCNRequest`). Auto-resolves `mcnId` and `requestId` if omitted, and verifies post-reply partnership state when `verifyAfter: true`.
- **Request:** `{ "cookie": "...", "decision": "accept", "mcnId": "", "requestId": "", "requestType": "InvitationRequest", "verifyAfter": true, "country": "VN", "proxy": "" }`
- **Response `data`:** `{ "isSuccess": true, "decision": "accept", "mcnId": "...", "requestId": "...", "partnership": { ... }, "raw": { ... } }`

### 8.4 `get_mcn_kol_partnerships` (`MinSign_GetMcnKolPartnerships`)
Lists and filters managed KOL/Affiliate contracts from the MCN Portal (`POST https://mcn.affiliate.<domain>/api/v3/gql?q=getMCNAndKOLPartnershipList`), optionally fetching `mcnBasicInfo`, permissions, and system configs (`includeMeta: true`).
- **Request:** `{ "cookie": "...", "mcnId": "", "affiliateId": "", "affiliateName": "", "tabStatusFilter": "", "pageNum": 1, "pageSize": 20, "includeMeta": false, "country": "VN", "proxy": "" }`
- **Response `data`:** `{ "count": 20, "partnerships": [ ... ], "pagination": { ... }, "summaryFilterResult": { ... }, "raw": { ... } }`

### 8.5 `send_mcn_partnership_invitation` (`MinSign_SendMcnPartnershipInvitation`)
Validates an Affiliate username/ID (`checkUsernameWhenMCNSendPartnershipInvitation` / `checkAffiliateIdWhenMCNSendPartnershipInvitation`) and sends a partnership invitation (`MCNSendPartnershipInvitationMutation`) from the MCN Portal.
- **Request:** `{ "cookie": "...", "mcnId": "888111", "affiliateId": "", "username": "kol_name", "mcnFeeRatePercent": 10, "durationDays": 180, "endDateTimestamp": 0, "validateFirst": true, "country": "VN", "proxy": "" }`
- **Response `data`:** `{ "isSuccess": true, "mcnId": "888111", "affiliateId": "...", "endDateTimestamp": 1790000000, "raw": { ... } }`

### 8.6 `manage_mcn_partnership` (`MinSign_ManageMcnPartnership`)
Executes MCN-side contract lifecycle mutations and request history queries on `mcn.affiliate.<domain>/api/v3/gql`:
- `action: "reply" | "accept" | "reject"` → `MCNReplyToKOLRequestMutation`
- `action: "change_fee"` → `MCNRequestChangeFeeRateMutation` (`newMcnFeeRatePercent`)
- `action: "extend"` → `MCNRequestPartnershipExtensionMutation` (`newEndDateTimestamp`)
- `action: "cancel"` → `MCNCancelPartnershipMutation`
- `action: "history"` → `getPartnershipRequestHistoryGroupByContractId`
- **Request:** `{ "cookie": "...", "action": "cancel", "mcnId": "888111", "affiliateId": "123456", "partnershipId": "999222", "country": "VN", "proxy": "" }`

### 8.7 `get_mcn_analytics` (`MinSign_GetMcnAnalytics`)
Queries MCN Portal analytics and campaigns on `mcn.affiliate.<domain>/api/v3/gql` (`mode`: `"core"` | `"affiliates"` | `"campaigns"` | `"campaign_detail"` | `"info"`).
- **Request:** `{ "cookie": "...", "mode": "core", "startTime": 1730419200, "endTime": 1733011200, "campaignId": "", "pageNum": 1, "pageSize": 20, "country": "VN", "proxy": "" }`

### 8.8 `get_affiliate_payment_tax` (`MinSign_GetAffiliatePaymentTax`)
Queries `GET https://affiliate.<domain>/api/v3/payment_setting/display` and normalizes bank status, tax/TIN/CCCD KYC status (`valid` | `pending` | `rejected` | `empty`), and EWT/VAT rates.
- **Request:** `{ "cookie": "...", "country": "VN", "proxy": "" }`
- **Response `data`:** `{ "paymentStatus": "valid", "taxStatus": "valid", "bankName": "...", "bankAccountNo": "...", "taxCodeTin": "...", "cccdId": "...", "ewtRate": "10%", "raw": { ... } }`

### 8.9 `get_affiliate_click_report` (`MinSign_GetAffiliateClickReport`)
Queries `GET https://affiliate.<domain>/api/v1/click_report/list` within a Unix timestamp window to extract click counts and records.
- **Request:** `{ "cookie": "...", "startTime": 1730419200, "endTime": 1733011200, "pageNum": 1, "pageLimit": 20, "country": "VN", "proxy": "" }`

### 8.10 `get_affiliate_billing` (`MinSign_GetAffiliateBilling`)
Queries `GET https://affiliate.<domain>/api/v3/payment/billing_list` (with `settlement_cycle=4` for `VN`) and optionally `billing_detail` (`validationId` or `includeDetails: true`), returning normalized gross payouts, tax withheld, MCN deductions, and net payouts.
- **Request:** `{ "cookie": "...", "days": 365, "validationId": "", "includeDetails": false, "country": "VN", "proxy": "" }`
