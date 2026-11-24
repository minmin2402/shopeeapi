# Changelog

All notable changes to **ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll`)** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

---

## [2.0.0] — 2026-11-25

### Major Release — 44 Production APIs, 7 Language Wrappers & Dual App + Web Security Signing

#### Added — Dual Signing Engine (Web Chrome 131 Signer)
- **`sign_web` (`MinSign_SignWeb`)**: Dedicated Chrome 131 Web Signer calling `/api/v1/web/sign` on MinSign Cloud, returning Chrome 131 Web security headers and `patchedCookie` for Shopee Web & Affiliate portals.
- **`clientType` selector (`"app"` | `"web"`)**: Added `clientType` support to both `sign_raw` (`MinSign_SignRaw`) and `execute_signed_request` (`MinSign_ExecuteSignedRequest`) so developers can switch seamlessly between Android App UniDBG signing and Chrome 131 Web signing.

#### Added — Commerce, Discovery & Batch Intelligence (6 New APIs)
- **`resolve_shopee_url` (`MinSign_ResolveShopeeUrl`)**: Universal Shopee URL parser & builder supporting product URLs (`/product/{shop}/{item}`, `-i.{shop}.{item}`), shop URLs, Shopee Video (`share-video`, `post_id`), Shopee Live (`session`), shortlink redirection (`shp.ee`, `s.shopee.*` with `followRedirect: true`), and canonical URL generation across all 8 regions.
- **`batch_get_product_details` (`MinSign_BatchGetProductDetails`)**: Bounded Go goroutine worker pool (default concurrency `5`, max `16`) rotating `proxies[]` and `cookies[]` to fetch multiple products concurrently while preserving input order.
- **`get_product_ratings` (`MinSign_GetProductRatings`)**: Signed buyer rating & review scraper (`api/v2/item/get_ratings`) with auto URL parsing, pagination, star filters, star summary counts, and attached image/video URLs.
- **`get_flash_sale_items` (`MinSign_GetFlashSaleItems`)**: Auto-discovers active Flash Sale sessions (`get_all_sessions`) and fetches discounted flash-sale items (`flash_sale_batch_get_items` / `get_all_itemids`).
- **`get_recommend_products` (`MinSign_GetRecommendProducts`)**: Queries `api/v4/recommend/recommend` for `item_detail_similar_items` (when `itemId` is supplied) or `daily_discover_main` feeds.
- **`get_search_suggestions` (`MinSign_GetSearchSuggestions`)**: Queries `api/v4/search/search_suggestion` / `search_hint` for real-time keyword autocomplete suggestions.

#### Added — Account, Cart, Affiliate Analytics & Live Commerce (6 New APIs)
- **`get_account_profile` (`MinSign_GetAccountProfile`)**: Cookie health check & account identity endpoint (`api/v4/account/basic/get_account_info`) returning `alive`, `userId`, `shopId`, `username`, `emailVerified`, `phoneVerified`, `isSeller`, and `portrait`.
- **`get_cart_summary` (`MinSign_GetCartSummary`)**: Retrieves normalized shopping cart shop groups, total item count, and subtotal via `api/v4/cart/get` (with automatic `api/v4/cart/mini` fallback).
- **`claim_shop_voucher` (`MinSign_ClaimShopVoucher`)**: Claims/saves shop vouchers via `POST api/v2/voucher_wallet/save_voucher` with Layer-2 Risk Headers (`attachRiskHeaders: true`) enabled automatically.
- **`get_affiliate_offer_list` (`MinSign_GetAffiliateOfferList`)**: Uses `sign_web` + `Affiliate-Program-Type: 1` against `https://affiliate.<domain>/api/v3/offer/product/list` to discover high-commission products (`commissionRate`, `sellerCommissionRate`, monthly `sales`, `price`, `imageUrl`, `productLink`).
- **`get_affiliate_commission_report` (`MinSign_GetAffiliateCommissionReport`)**: Uses `sign_web` against `https://affiliate.<domain>/api/v3/report/list` to query conversion & commission payout records by Unix timestamp range.
- **`get_live_bag_items` (`MinSign_GetLiveBagItems`)**: Resolves Live URL / `sessionId` and queries `https://live.<domain>/api/v1/session/{sessionId}/more_items` to extract pinned Live shopping bag products, discounts, stock, and affiliate metadata.

#### Added — 3 New Official Language Wrappers & TypeScript Definitions (7 Languages Total)
- **PHP 8.1+ FFI Wrapper**: [`wrappers/php/MinSignSdk.php`](./wrappers/php/MinSignSdk.php) + [`examples/quickstart_php.php`](./examples/quickstart_php.php)
- **Go Zero-CGO Wrapper**: [`wrappers/go/minsign.go`](./wrappers/go/minsign.go) (`syscall.NewLazyDLL`) + [`examples/quickstart_go.go`](./examples/quickstart_go.go)
- **Java JNA Wrapper**: [`wrappers/java/MinSignSdk.java`](./wrappers/java/MinSignSdk.java) + [`examples/QuickstartJava.java`](./examples/QuickstartJava.java)
- **TypeScript Definitions**: [`wrappers/nodejs/minsign_sdk.d.ts`](./wrappers/nodejs/minsign_sdk.d.ts) covering all 44 APIs.

#### Added — Examples & Global Documentation
- Added [`examples/batch_product_scraper.py`](./examples/batch_product_scraper.py), [`examples/affiliate_hunter.py`](./examples/affiliate_hunter.py), and [`examples/live_bag_scraper.py`](./examples/live_bag_scraper.py).
- Added [`docs/API_REFERENCE.md`](./docs/API_REFERENCE.md), [`docs/QUICKSTART_BY_LANGUAGE.md`](./docs/QUICKSTART_BY_LANGUAGE.md), and [`docs/USE_CASES_AND_PLAYBOOKS.md`](./docs/USE_CASES_AND_PLAYBOOKS.md).
- Upgraded multilingual READMEs (`README.md`, `README.vi.md`, `README.id.md`, `README.th.md`, `README.zh.md`) to v2.0.0.

#### Changed
- Updated all 4 existing wrappers (`Python`, `Node.js`, `C#`, `C++17`) to expose all 44 Action APIs (48 total C-ABI exports) and `clientType` support.
- Bumped `MinSign_Version()` to `"2.0.0"`.

---

## [1.5.0] — 2026-11-23

### Added — Shopee Affiliate Link Converter & Batch Shortener (31 Action APIs)
- **`convert_affiliate_link` (`MinSign_ConvertAffiliateLink`)**: Converts standard Shopee product URLs, competitor `aff_id` URLs, `universal-link`s, or `s.shopee.*` / `shp.ee` shortlinks into official tracked Affiliate short links via `affiliate.shopee.*/api/v3/gql?q=batchCustomLink`, supporting `subId1..subId5`, automatic region detection, and automatic MinSign + RiskToken retry on `90309999`.
- **`batch_convert_affiliate_links` (`MinSign_BatchConvertAffiliateLinks`)**: Batch converts multiple URLs in auto-chunked GraphQL calls (20–50 links per request) with per-item tracking `subIds`.

---

## [1.4.0] — 2026-11-20

### Added — Multi-Threaded Shopee Live View & WebSocket Heartbeat Engine (29 Action APIs)
- **`get_live_session_detail` (`MinSign_GetLiveSessionDetail`)**: Resolves Live URLs (`live.shopee.*`, `shp.ee`) or `sessionId`, signs Aegis (`X-Livestreaming-Auth`) + MinSign for `joinv2` & `play_url_list`, returning `roomId`, `viewerCount`, `memberCnt`, `usersig`, and CDN `playUrls`.
- **`buff_live_view` (`MinSign_BuffLiveView`)**: Executes a full single-viewer Live session (`joinv2` → FLV/HLS stream pull → RFC 6455 WebSocket `wss://live-ws.<dom>/im/v1/comet` Wire Protobuf `HB_REQ` → `SZTracker` `reportPB` `10002`/`10003`/`10007` → optional `/like` → clean `/exit`).
- **`buff_live_batch` (`MinSign_BuffLiveBatch`)**: Multi-threaded Go worker pool rotating `proxies[]` and `cookies[]` with configurable `staggerMs` and stream-lite options.
- Added [`examples/buff_view_shopee_live.py`](./examples/buff_view_shopee_live.py).

---

## [1.3.0] — 2026-11-06

### Added — Pure-HTTP Visual Product Search & AI Bounding Box (26 Action APIs)
- **`search_products_by_image` (`MinSign_SearchProductsByImage`)**: Visual search supporting 5 image input modes (local file path, Base64 clipboard, external TikTok/1688/Taobao URL, Shopee CDN image hash, or Shopee product URL) with `SimilarProducts` and `CheaperOptions` result types.
- **`get_image_bounding_box` (`MinSign_GetImageBoundingBox`)**: Zero-cookie, zero-credit AI object detection returning `left,top,width,height` bounding boxes for multi-object photos.
- Added [`examples/image_search_shopee.py`](./examples/image_search_shopee.py) and [`DOCS_TIM_SAN_PHAM_BANG_ANH.md`](./DOCS_TIM_SAN_PHAM_BANG_ANH.md).

---

## [1.2.0] — 2026-11-01

### Added — Layer-2 Android Device Risk Token Engine (24 Action APIs)
- **`get_risk_token` (`MinSign_GetRiskToken`)**: Mints and caches full Layer-2 Android Device Risk Tokens (`af-ac-enc-sz-token`, `riskToken`, `dfp`, `longToken`, `shpSecData`, `miniToken`) bound 1:1 to each account's persistent hardware profile in `devices_vault.json`.
- Added `attachRiskHeaders`, `includeRiskTokens`, and `forceRefreshRisk` flags to `sign_raw` and `execute_signed_request` for sensitive checkout, cart, and voucher endpoints.

---

## [1.1.0] — 2026-10-31

### Added — Real-Time Affiliate Shop Monitoring & Watermark-Free Video Scraper (23 Action APIs)
- **`get_shop_newest_products` (`MinSign_GetShopNewestProducts`)**: Real-time newest product monitor (`rcmd_items?sort_type=2` + Affiliate offer enrichment + Zero-Cookie fallback) with `sinceItemId`, `sinceTimestamp`, and `withinHours` filters.
- **`get_shop_videos` (`MinSign_GetShopVideos`)**: Resolves `shopUrl`/`shopId`/`username` to Shopee Video channel `userId`, paginates across `maxPages`, and returns watermark-free CDN `mp4Url` + `attachedProducts[]`.

---

## [1.0.0] — 2026-10-29

### Initial Public Release (21 Action APIs, 4 Language Wrappers, 8 Shopee Regions)
- Native Windows x64 C-ABI DLL (`minsign_sdk.dll`) powered by Go `uTLS` (Android OkHttp4) and MinSign Cloud Signer (`https://vip-sign.minmintool.site`).
- Local persistent sticky Android 14 device vault (`devices_vault.json`) with optional `AES-256-GCM` encryption.
- Core Commerce & Shop APIs (`get_product_detail`, `get_shop_overview`, `get_shop_products`, `get_shop_categories`, `get_shop_vouchers`, `search_products`, `get_category_tree`) across `VN`, `ID`, `TH`, `MY`, `PH`, `SG`, `TW`, `BR`.
- Pure-API 4-step Shopee Video uploader (`upload_shopee_video`, `precheck_video_upload`, `get_affiliate_products`), `<10ms` `.mp4` binary fingerprint mutator (`mutate_mp4_fingerprint`), and multi-threaded video view booster (`buff_video_view`, `buff_video_batch`, `get_video_detail`, `get_channel_and_hashtag_videos`).
- Universal signed gateway (`execute_signed_request`) and system/vault APIs (`check_api_key`, `bind_account_device`, `list_local_devices`, `remove_local_device`, `sign_raw`).
- Initial wrappers for **Python**, **Node.js**, **C#**, and **C++17**.
