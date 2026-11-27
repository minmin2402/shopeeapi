"""
Official Python Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll / libminsign_sdk.so).

Zero external dependencies (uses Python's standard library ctypes).
Automatically frees every C-ABI heap pointer via MinSign_Free(ptr) to guarantee zero memory leaks.
Supports all 44 production APIs across 8 Shopee regions (VN, ID, TH, MY, PH, SG, TW, BR)
with dual App Mobile + Web Chrome signing modes.
"""
from __future__ import annotations

import ctypes
import json
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

CookieInput = Union[str, Dict[str, Any], List[Any]]


class MinSignError(RuntimeError):
    """Raised when minsign_sdk.dll returns an error response or null pointer."""


class MinSignClient:
    """Thread-safe Python client wrapping MinSign Native Universal SDK v2.0.0."""

    _V2_EXPORT_SYMBOLS = (
        "MinSign_SignWeb",
        "MinSign_ResolveShopeeUrl",
        "MinSign_BatchGetProductDetails",
        "MinSign_GetProductRatings",
        "MinSign_GetFlashSaleItems",
        "MinSign_GetRecommendProducts",
        "MinSign_GetSearchSuggestions",
        "MinSign_GetAccountProfile",
        "MinSign_GetCartSummary",
        "MinSign_ClaimShopVoucher",
        "MinSign_GetAffiliateOfferList",
        "MinSign_GetAffiliateCommissionReport",
        "MinSign_GetLiveBagItems",
        "MinSign_GetAffiliateUserProfile",
        "MinSign_GetMcnPartnershipStatus",
        "MinSign_ReplyMcnInvitation",
        "MinSign_GetMcnKolPartnerships",
        "MinSign_SendMcnPartnershipInvitation",
        "MinSign_ManageMcnPartnership",
        "MinSign_GetMcnAnalytics",
        "MinSign_GetAffiliatePaymentTax",
        "MinSign_GetAffiliateClickReport",
        "MinSign_GetAffiliateBilling",
    )

    def __init__(
        self,
        api_key: str,
        dll_path: Optional[str] = None,
        signer_url: str = "https://vip-sign.minmintool.site",
        vault_file_path: str = "./minsign_data/devices_vault.json",
        vault_secret: str = "",
        default_country: str = "VN",
        timeout_ms: int = 25000,
    ) -> None:
        """Initialize the native SDK library and configure the signer + local device vault."""
        if not api_key or not api_key.strip():
            raise ValueError("api_key (X-API-Key) is required.")

        resolved_dll = self._resolve_dll_path(dll_path)
        self._lib = ctypes.CDLL(str(resolved_dll))

        # Core C-ABI signatures (use c_void_p for return values so exact pointers are passed to MinSign_Free)
        self._lib.MinSign_Version.argtypes = []
        self._lib.MinSign_Version.restype = ctypes.c_void_p

        self._lib.MinSign_Init.argtypes = [ctypes.c_char_p]
        self._lib.MinSign_Init.restype = ctypes.c_void_p

        self._lib.MinSign_CheckApiKey.argtypes = []
        self._lib.MinSign_CheckApiKey.restype = ctypes.c_void_p

        self._lib.MinSign_ListLocalDevices.argtypes = []
        self._lib.MinSign_ListLocalDevices.restype = ctypes.c_void_p

        self._lib.MinSign_GetRiskToken.argtypes = [ctypes.c_char_p]
        self._lib.MinSign_GetRiskToken.restype = ctypes.c_void_p

        self._lib.MinSign_Invoke.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.MinSign_Invoke.restype = ctypes.c_void_p

        self._lib.MinSign_Free.argtypes = [ctypes.c_void_p]
        self._lib.MinSign_Free.restype = None

        # Bind all 13 v2.0.0 C-ABI exports (gracefully optional if loaded against an older DLL)
        self._exports: Dict[str, Any] = {}
        for symbol in self._V2_EXPORT_SYMBOLS:
            fn = getattr(self._lib, symbol, None)
            if fn is not None:
                fn.argtypes = [ctypes.c_char_p]
                fn.restype = ctypes.c_void_p
                self._exports[symbol] = fn

        self.init_info = self._consume_ptr(
            self._lib.MinSign_Init(
                json.dumps(
                    {
                        "apiKey": api_key.strip(),
                        "signerUrl": signer_url,
                        "vaultFilePath": vault_file_path,
                        "vaultSecret": vault_secret,
                        "defaultCountry": default_country,
                        "timeoutMs": timeout_ms,
                    }
                ).encode("utf-8")
            )
        )

    @staticmethod
    def _resolve_dll_path(custom_path: Optional[str]) -> Path:
        if custom_path:
            p = Path(custom_path).resolve()
            if p.exists():
                return p
            raise FileNotFoundError(f"Native SDK library not found at: {p}")

        lib_name = "minsign_sdk.dll" if platform.system() == "Windows" else "libminsign_sdk.so"
        here = Path(__file__).resolve().parent
        candidates = [
            Path.cwd() / lib_name,
            Path.cwd() / "bin" / "win-x64" / lib_name,
            here / lib_name,
            here.parent.parent / "bin" / "win-x64" / lib_name,
            here.parent.parent / "dist" / "win-x64" / lib_name,
            here.parent / "bin" / lib_name,
        ]
        for cand in candidates:
            if cand.exists():
                return cand
        raise FileNotFoundError(
            f"Could not locate {lib_name}. Place it next to your script or pass dll_path=..."
        )

    @staticmethod
    def _normalize_payload(payload: Optional[Dict[str, Any]]) -> bytes:
        req = dict(payload or {})
        if isinstance(req.get("cookie"), (dict, list)):
            req["cookie"] = json.dumps(req["cookie"], ensure_ascii=False)
        if isinstance(req.get("cookies"), list):
            req["cookies"] = [
                json.dumps(c, ensure_ascii=False) if isinstance(c, (dict, list)) else str(c)
                for c in req["cookies"]
            ]
        return json.dumps(req, ensure_ascii=False).encode("utf-8")

    def _consume_ptr(self, ptr: Optional[int], raise_on_error: bool = True) -> Dict[str, Any]:
        if not ptr:
            raise MinSignError("minsign_sdk.dll returned a NULL pointer.")
        try:
            raw_bytes = ctypes.string_at(ptr)
            parsed: Dict[str, Any] = json.loads(raw_bytes.decode("utf-8"))
        finally:
            self._lib.MinSign_Free(ctypes.c_void_p(ptr))

        if raise_on_error and not parsed.get("ok", False):
            raise MinSignError(parsed.get("error") or json.dumps(parsed, ensure_ascii=False))
        return parsed

    def _call_export(
        self,
        symbol: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        raise_on_error: bool = True,
    ) -> Dict[str, Any]:
        body = self._normalize_payload(payload)
        fn = self._exports.get(symbol)
        if fn is not None:
            return self._consume_ptr(fn(body), raise_on_error=raise_on_error)
        ptr = self._lib.MinSign_Invoke(action.encode("utf-8"), body)
        return self._consume_ptr(ptr, raise_on_error=raise_on_error)

    def invoke(
        self,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        raise_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Invoke any SDK action by its snake_case action name via MinSign_Invoke."""
        body = self._normalize_payload(payload)
        ptr = self._lib.MinSign_Invoke(action.encode("utf-8"), body)
        return self._consume_ptr(ptr, raise_on_error=raise_on_error)

    # =========================================================================
    # Group 1: Key Management, Local Device Vault & Core Signing (App + Web)
    # =========================================================================

    def version(self) -> Dict[str, Any]:
        """Return SDK version and build metadata."""
        return self._consume_ptr(self._lib.MinSign_Version())["data"]

    def check_api_key(self) -> Dict[str, Any]:
        """Check API key validity, plan tier, and remaining quota."""
        return self._consume_ptr(self._lib.MinSign_CheckApiKey())["data"]

    def bind_account_device(
        self,
        cookie: CookieInput = "",
        account_id: str = "",
        country: str = "VN",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Bind a persistent virtual device fingerprint to a Shopee account in the local vault."""
        return self.invoke(
            "bind_account_device",
            {"cookie": cookie, "accountId": account_id, "country": country, "deviceId": device_id},
        )["data"]

    def list_local_devices(self) -> Dict[str, Any]:
        """List all device profiles stored in the local encrypted vault."""
        return self._consume_ptr(self._lib.MinSign_ListLocalDevices())["data"]

    def remove_local_device(self, account_key: str) -> Dict[str, Any]:
        """Remove a stored device binding from the local vault."""
        return self.invoke("remove_local_device", {"accountKey": account_key})["data"]

    def sign_raw(
        self,
        url: str,
        body: str = "",
        country: str = "",
        cookie: CookieInput = "",
        account_id: str = "",
        device_id: str = "",
        brand: str = "",
        fetch_live: bool = False,
        include_risk_tokens: bool = False,
        attach_risk_headers: bool = False,
        force_refresh_risk: bool = False,
        sec_token: str = "",
        client_type: str = "app",
    ) -> Dict[str, Any]:
        """Generate Shopee security signature headers for a raw URL/body (supports client_type='app' or 'web')."""
        return self.invoke(
            "sign_raw",
            {
                "url": url,
                "body": body,
                "country": country,
                "cookie": cookie,
                "accountId": account_id,
                "deviceId": device_id,
                "brand": brand,
                "fetchLive": fetch_live,
                "includeRiskTokens": include_risk_tokens,
                "attachRiskHeaders": attach_risk_headers,
                "forceRefreshRisk": force_refresh_risk,
                "secToken": sec_token,
                "clientType": client_type,
            },
        )["data"]

    def sign_web(
        self,
        url: str,
        body: str = "",
        country: str = "",
        cookie: CookieInput = "",
        account_id: str = "",
        device_id: str = "",
        proxy: str = "",
        fetch_live: bool = False,
    ) -> Dict[str, Any]:
        """Generate Shopee Web Chrome 131 security headers and patched cookies via MinSign_SignWeb."""
        return self._call_export(
            "MinSign_SignWeb",
            "sign_web",
            {
                "url": url,
                "body": body,
                "country": country,
                "cookie": cookie,
                "accountId": account_id,
                "deviceId": device_id,
                "proxy": proxy,
                "fetchLive": fetch_live,
            },
        )["data"]

    def get_risk_token(
        self,
        country: str = "VN",
        cookie: CookieInput = "",
        account_id: str = "",
        device_id: str = "",
        brand: str = "",
        force_refresh: bool = False,
        sec_token: str = "",
    ) -> Dict[str, Any]:
        """Fetch or refresh Shopee anti-fraud risk tokens (af-ac-enc-dat / sz-token)."""
        payload = self._normalize_payload(
            {
                "country": country,
                "cookie": cookie,
                "accountId": account_id,
                "deviceId": device_id,
                "brand": brand,
                "forceRefresh": force_refresh,
                "secToken": sec_token,
            }
        )
        return self._consume_ptr(self._lib.MinSign_GetRiskToken(payload))["data"]

    # =========================================================================
    # Group 2: Products, Shops, Vouchers, Search, Recommendations & URL Tools
    # =========================================================================

    def resolve_shopee_url(
        self,
        url: str = "",
        shop_id: str = "",
        item_id: str = "",
        country: str = "",
        proxy: str = "",
        follow_redirect: bool = False,
    ) -> Dict[str, Any]:
        """Parse any Shopee URL (product, shop, video, live, shortlink) or build a canonical URL from shop_id/item_id."""
        return self._call_export(
            "MinSign_ResolveShopeeUrl",
            "resolve_shopee_url",
            {
                "url": url,
                "shopId": str(shop_id or ""),
                "itemId": str(item_id or ""),
                "country": country,
                "proxy": proxy,
                "followRedirect": follow_redirect,
            },
        )["data"]

    def get_product_detail(
        self,
        product_url: str = "",
        shop_id: str = "",
        item_id: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
        account_id: str = "",
        include_shop: bool = True,
    ) -> Dict[str, Any]:
        """Fetch full product details, pricing, stock, variations/models, and optional shop summary."""
        return self.invoke(
            "get_product_detail",
            {
                "productUrl": product_url,
                "shopId": str(shop_id or ""),
                "itemId": str(item_id or ""),
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
                "includeShop": include_shop,
            },
        )["data"]

    def batch_get_product_details(
        self,
        items: Optional[List[Dict[str, Any]]] = None,
        product_urls: Optional[List[str]] = None,
        country: str = "",
        cookie: CookieInput = "",
        cookies: Optional[List[CookieInput]] = None,
        proxy: str = "",
        proxies: Optional[List[str]] = None,
        concurrency: int = 5,
    ) -> Dict[str, Any]:
        """Fetch multiple product details concurrently using a native Go worker pool with proxy/cookie rotation."""
        return self._call_export(
            "MinSign_BatchGetProductDetails",
            "batch_get_product_details",
            {
                "items": items or [],
                "productUrls": product_urls or [],
                "country": country,
                "cookie": cookie,
                "cookies": cookies or [],
                "proxy": proxy,
                "proxies": proxies or [],
                "concurrency": concurrency,
            },
        )["data"]

    def get_product_ratings(
        self,
        product_url: str = "",
        shop_id: str = "",
        item_id: str = "",
        limit: int = 20,
        offset: int = 0,
        filter: int = 0,
        type: int = 0,
        country: str = "",
        cookie: CookieInput = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch product customer reviews, star rating summary, and review media URLs."""
        return self._call_export(
            "MinSign_GetProductRatings",
            "get_product_ratings",
            {
                "productUrl": product_url,
                "shopId": str(shop_id or ""),
                "itemId": str(item_id or ""),
                "limit": limit,
                "offset": offset,
                "filter": filter,
                "type": type,
                "country": country,
                "cookie": cookie,
                "proxy": proxy,
            },
        )["data"]

    def get_flash_sale_items(
        self,
        promotion_id: int = 0,
        limit: int = 20,
        offset: int = 0,
        country: str = "",
        cookie: CookieInput = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch active Shopee Flash Sale sessions and discounted flash-sale items."""
        return self._call_export(
            "MinSign_GetFlashSaleItems",
            "get_flash_sale_items",
            {
                "promotionId": promotion_id,
                "limit": limit,
                "offset": offset,
                "country": country,
                "cookie": cookie,
                "proxy": proxy,
            },
        )["data"]

    def get_recommend_products(
        self,
        bundle: str = "",
        shop_id: str = "",
        item_id: str = "",
        limit: int = 20,
        offset: int = 0,
        country: str = "",
        cookie: CookieInput = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch Shopee recommendation feeds (daily discover or item-detail similar products)."""
        return self._call_export(
            "MinSign_GetRecommendProducts",
            "get_recommend_products",
            {
                "bundle": bundle,
                "shopId": str(shop_id or ""),
                "itemId": str(item_id or ""),
                "limit": limit,
                "offset": offset,
                "country": country,
                "cookie": cookie,
                "proxy": proxy,
            },
        )["data"]

    def get_search_suggestions(
        self,
        keyword: str = "",
        limit: int = 10,
        country: str = "",
        cookie: CookieInput = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch live Shopee autocomplete keyword suggestions for a search query."""
        return self._call_export(
            "MinSign_GetSearchSuggestions",
            "get_search_suggestions",
            {
                "keyword": keyword,
                "limit": limit,
                "country": country,
                "cookie": cookie,
                "proxy": proxy,
            },
        )["data"]

    def get_shop_overview(
        self,
        shop_url: str = "",
        shop_id: str = "",
        username: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
    ) -> Dict[str, Any]:
        """Fetch shop profile metadata, follower counts, rating, and seller status."""
        return self.invoke(
            "get_shop_overview",
            {
                "shopUrl": shop_url,
                "shopId": str(shop_id or ""),
                "username": username,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    def get_shop_products(
        self,
        shop_id: str = "",
        shop_url: str = "",
        limit: int = 30,
        offset: int = 0,
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
    ) -> Dict[str, Any]:
        """List products in a shop with pagination."""
        return self.invoke(
            "get_shop_products",
            {
                "shopId": str(shop_id or ""),
                "shopUrl": shop_url,
                "limit": limit,
                "offset": offset,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    def get_shop_newest_products(
        self,
        shop_url: str = "",
        shop_id: str = "",
        username: str = "",
        limit: int = 30,
        offset: int = 0,
        since_item_id: str = "",
        since_timestamp: int = 0,
        within_hours: int = 0,
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
        account_id: str = "",
    ) -> Dict[str, Any]:
        """Fetch newly listed products of a shop with optional incremental cursor filtering."""
        return self.invoke(
            "get_shop_newest_products",
            {
                "shopUrl": shop_url,
                "shopId": str(shop_id or ""),
                "username": username,
                "limit": limit,
                "offset": offset,
                "sinceItemId": str(since_item_id or ""),
                "sinceTimestamp": since_timestamp,
                "withinHours": within_hours,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
            },
        )["data"]

    def get_shop_categories(
        self,
        shop_id: str = "",
        shop_url: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
    ) -> Dict[str, Any]:
        """Fetch in-shop custom category collections."""
        return self.invoke(
            "get_shop_categories",
            {
                "shopId": str(shop_id or ""),
                "shopUrl": shop_url,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    def get_shop_vouchers(
        self,
        shop_id: str = "",
        shop_url: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
    ) -> Dict[str, Any]:
        """List active discount vouchers offered by a shop."""
        return self.invoke(
            "get_shop_vouchers",
            {
                "shopId": str(shop_id or ""),
                "shopUrl": shop_url,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    def search_products(
        self,
        keyword: str,
        country: str = "VN",
        sort_by: str = "relevancy",
        page: int = 0,
        limit: int = 20,
        proxy: str = "",
        cookie: CookieInput = "",
    ) -> Dict[str, Any]:
        """Search Shopee products by keyword with sort and pagination options."""
        return self.invoke(
            "search_products",
            {
                "keyword": keyword,
                "country": country,
                "sortBy": sort_by,
                "page": page,
                "limit": limit,
                "proxy": proxy,
                "cookie": cookie,
            },
        )["data"]

    def search_products_by_image(
        self,
        cookie: CookieInput,
        image_path: str = "",
        image_base64: str = "",
        image_url: str = "",
        image_id: str = "",
        product_url: str = "",
        shop_id: str = "",
        item_id: str = "",
        country: str = "VN",
        result_type: str = "SimilarProducts",
        offset: int = 0,
        limit: int = 20,
        bounding_box: str = "",
        auto_detect_box: bool = False,
        force_upload: bool = False,
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Search visually similar products on Shopee from a local image, base64, URL, or existing item."""
        return self.invoke(
            "search_products_by_image",
            {
                "cookie": cookie,
                "imagePath": image_path,
                "imageBase64": image_base64,
                "imageUrl": image_url,
                "imageId": image_id,
                "productUrl": product_url,
                "shopId": str(shop_id or ""),
                "itemId": str(item_id or ""),
                "country": country,
                "resultType": result_type,
                "offset": offset,
                "limit": limit,
                "boundingBox": bounding_box,
                "autoDetectBox": auto_detect_box,
                "forceUpload": force_upload,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def get_image_bounding_box(
        self,
        image_path: str = "",
        image_base64: str = "",
        image_url: str = "",
        country: str = "VN",
        image_source: str = "local",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Detect object bounding boxes in an image for Shopee visual search."""
        return self.invoke(
            "get_image_bounding_box",
            {
                "imagePath": image_path,
                "imageBase64": image_base64,
                "imageUrl": image_url,
                "country": country,
                "imageSource": image_source,
                "proxy": proxy,
            },
        )["data"]

    def get_category_tree(self, country: str = "VN", proxy: str = "") -> Dict[str, Any]:
        """Fetch the marketplace category hierarchy tree for a Shopee region."""
        return self.invoke("get_category_tree", {"country": country, "proxy": proxy})["data"]

    # =========================================================================
    # Group 3: Account, Cart & Voucher Actions
    # =========================================================================

    def get_account_profile(
        self,
        cookie: CookieInput = "",
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Check cookie health and retrieve basic Shopee account profile information."""
        return self._call_export(
            "MinSign_GetAccountProfile",
            "get_account_profile",
            {
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def get_cart_summary(
        self,
        cookie: CookieInput = "",
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Retrieve the authenticated account's shopping cart groups, item count, and subtotal."""
        return self._call_export(
            "MinSign_GetCartSummary",
            "get_cart_summary",
            {
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def claim_shop_voucher(
        self,
        voucher_code: str = "",
        promotion_id: int = 0,
        signature: str = "",
        shop_id: str = "",
        cookie: CookieInput = "",
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Save/claim a shop voucher into the account's voucher wallet with risk headers attached."""
        return self._call_export(
            "MinSign_ClaimShopVoucher",
            "claim_shop_voucher",
            {
                "voucherCode": voucher_code,
                "promotionId": promotion_id,
                "signature": signature,
                "shopId": str(shop_id or ""),
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    # =========================================================================
    # Group 4: Shopee Video Studio & Affiliate Marketing
    # =========================================================================

    def upload_shopee_video(
        self,
        video_path: str,
        cookie: CookieInput,
        caption: str = "",
        hashtags: Optional[List[str]] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        product_links: Optional[List[str]] = None,
        cover_path: str = "",
        post_mode: str = "normal",
        proxy: str = "",
        country: str = "VN",
        account_id: str = "",
        mutate_mp4: bool = True,
    ) -> Dict[str, Any]:
        """Upload and publish a Shopee Video with optional product tags and MP4 fingerprint mutation."""
        return self.invoke(
            "upload_shopee_video",
            {
                "videoPath": video_path,
                "coverPath": cover_path,
                "caption": caption,
                "hashtags": hashtags or [],
                "products": products or [],
                "productLinks": product_links or [],
                "postMode": post_mode,
                "mutateMp4": mutate_mp4,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
            },
        )["data"]

    def precheck_video_upload(
        self,
        cookie: CookieInput,
        proxy: str = "",
        country: str = "VN",
        account_id: str = "",
    ) -> Dict[str, Any]:
        """Verify whether an account is eligible to publish Shopee Videos."""
        return self.invoke(
            "precheck_video_upload",
            {"cookie": cookie, "proxy": proxy, "country": country, "accountId": account_id},
        )["data"]

    def get_affiliate_products(
        self,
        cookie: CookieInput,
        keyword: str = "",
        page_offset: int = 0,
        page_limit: int = 20,
        proxy: str = "",
        country: str = "VN",
    ) -> Dict[str, Any]:
        """Search affiliate-eligible products for video tagging."""
        return self.invoke(
            "get_affiliate_products",
            {
                "cookie": cookie,
                "keyword": keyword,
                "pageOffset": page_offset,
                "pageLimit": page_limit,
                "proxy": proxy,
                "country": country,
            },
        )["data"]

    def get_affiliate_offer_list(
        self,
        keyword: str = "",
        shop_id: str = "",
        list_type: int = 0,
        sort_type: int = 1,
        page_offset: int = 0,
        page_limit: int = 20,
        cookie: CookieInput = "",
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Query Shopee Affiliate product offers with commission rates and monthly sales via Web Signer."""
        return self._call_export(
            "MinSign_GetAffiliateOfferList",
            "get_affiliate_offer_list",
            {
                "keyword": keyword,
                "shopId": str(shop_id or ""),
                "listType": list_type,
                "sortType": sort_type,
                "pageOffset": page_offset,
                "pageLimit": page_limit,
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def get_affiliate_commission_report(
        self,
        start_time: int = 0,
        end_time: int = 0,
        page_offset: int = 0,
        page_limit: int = 20,
        cookie: CookieInput = "",
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Query Shopee Affiliate conversion and commission report records via Web Signer."""
        return self._call_export(
            "MinSign_GetAffiliateCommissionReport",
            "get_affiliate_commission_report",
            {
                "startTime": start_time,
                "endTime": end_time,
                "pageOffset": page_offset,
                "pageLimit": page_limit,
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def convert_affiliate_link(
        self,
        url: str,
        cookie: CookieInput,
        sub_id1: str = "",
        sub_id2: str = "",
        sub_id3: str = "",
        sub_id4: str = "",
        sub_id5: str = "",
        sub_ids: Optional[List[str]] = None,
        country: str = "",
        proxy: str = "",
        clean_product_url: bool = False,
        resolve_short_links: bool = True,
        sign_request: bool = True,
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Convert a single Shopee product/shop URL into a tracked affiliate short link."""
        return self.invoke(
            "convert_affiliate_link",
            {
                "url": url,
                "cookie": cookie,
                "subId1": sub_id1,
                "subId2": sub_id2,
                "subId3": sub_id3,
                "subId4": sub_id4,
                "subId5": sub_id5,
                "subIds": sub_ids or [],
                "country": country,
                "proxy": proxy,
                "cleanProductUrl": clean_product_url,
                "resolveShortLinks": resolve_short_links,
                "signRequest": sign_request,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def batch_convert_affiliate_links(
        self,
        cookie: CookieInput,
        urls: Optional[List[str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        sub_id1: str = "",
        sub_id2: str = "",
        sub_id3: str = "",
        sub_id4: str = "",
        sub_id5: str = "",
        sub_ids: Optional[List[str]] = None,
        country: str = "",
        proxy: str = "",
        clean_product_url: bool = False,
        resolve_short_links: bool = True,
        sign_request: bool = True,
        batch_size: int = 20,
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Batch-convert multiple Shopee URLs into tracked affiliate short links."""
        return self.invoke(
            "batch_convert_affiliate_links",
            {
                "cookie": cookie,
                "urls": urls or [],
                "items": items or [],
                "subId1": sub_id1,
                "subId2": sub_id2,
                "subId3": sub_id3,
                "subId4": sub_id4,
                "subId5": sub_id5,
                "subIds": sub_ids or [],
                "country": country,
                "proxy": proxy,
                "cleanProductUrl": clean_product_url,
                "resolveShortLinks": resolve_short_links,
                "signRequest": sign_request,
                "batchSize": batch_size,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def mutate_mp4_fingerprint(
        self,
        input_path: str,
        output_path: str = "",
        in_place: bool = False,
    ) -> Dict[str, Any]:
        """Mutate MP4 container metadata/fingerprint locally without re-encoding."""
        return self.invoke(
            "mutate_mp4_fingerprint",
            {"inputPath": input_path, "outputPath": output_path, "inPlace": in_place},
        )["data"]

    # =========================================================================
    # Group 5: Shopee Video Discovery & View Booster
    # =========================================================================

    def buff_video_view(
        self,
        video_url: str = "",
        post_id: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        watch_seconds: int = 18,
        country: str = "VN",
        account_id: str = "",
        device_id: str = "",
        simulate_wait: bool = False,
    ) -> Dict[str, Any]:
        """Execute a single Shopee Video view telemetry session."""
        return self.invoke(
            "buff_video_view",
            {
                "videoUrl": video_url,
                "postId": post_id,
                "proxy": proxy,
                "cookie": cookie,
                "watchSeconds": watch_seconds,
                "country": country,
                "accountId": account_id,
                "deviceId": device_id,
                "simulateWait": simulate_wait,
            },
        )["data"]

    def buff_video_batch(
        self,
        video_url: str = "",
        target_views: int = 10,
        concurrency: int = 5,
        proxies: Optional[List[str]] = None,
        cookies: Optional[List[CookieInput]] = None,
        watch_seconds: int = 18,
        country: str = "VN",
        post_id: str = "",
    ) -> Dict[str, Any]:
        """Run concurrent Shopee Video view sessions with proxy/cookie rotation."""
        return self.invoke(
            "buff_video_batch",
            {
                "videoUrl": video_url,
                "postId": post_id,
                "targetViews": target_views,
                "concurrency": concurrency,
                "proxies": proxies or [],
                "cookies": cookies or [],
                "watchSeconds": watch_seconds,
                "country": country,
            },
        )["data"]

    def get_video_detail(
        self,
        video_url: str = "",
        post_id: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "VN",
    ) -> Dict[str, Any]:
        """Fetch Shopee Video metadata, metrics, tagged items, and direct media URL."""
        return self.invoke(
            "get_video_detail",
            {
                "videoUrl": video_url,
                "postId": post_id,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    def get_shop_videos(
        self,
        shop_url: str = "",
        shop_id: str = "",
        username: str = "",
        user_id: str = "",
        limit: int = 20,
        page_token: str = "",
        max_pages: int = 1,
        include_product_videos: bool = True,
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
        account_id: str = "",
    ) -> Dict[str, Any]:
        """Fetch videos published by a shop or creator profile."""
        return self.invoke(
            "get_shop_videos",
            {
                "shopUrl": shop_url,
                "shopId": str(shop_id or ""),
                "username": username,
                "userId": str(user_id or ""),
                "limit": limit,
                "pageToken": page_token,
                "maxPages": max_pages,
                "includeProductVideos": include_product_videos,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
            },
        )["data"]

    def get_channel_and_hashtag_videos(
        self,
        mode: str = "channel",
        request_user_id: str = "",
        hashtag_id: str = "",
        limit: int = 20,
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "VN",
    ) -> Dict[str, Any]:
        """Fetch videos from a creator channel or hashtag feed."""
        return self.invoke(
            "get_channel_and_hashtag_videos",
            {
                "mode": mode,
                "requestUserId": request_user_id,
                "hashtagId": hashtag_id,
                "limit": limit,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
            },
        )["data"]

    # =========================================================================
    # Group 6: Shopee Live Commerce & Viewer Pipeline
    # =========================================================================

    def get_live_session_detail(
        self,
        live_url: str = "",
        session_id: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "VN",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Fetch Shopee Live session metadata, viewer stats, stream URLs, and host info."""
        return self.invoke(
            "get_live_session_detail",
            {
                "liveUrl": live_url,
                "sessionId": str(session_id or ""),
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def get_live_bag_items(
        self,
        live_url: str = "",
        session_id: str = "",
        offset: int = 0,
        limit: int = 20,
        country: str = "",
        cookie: CookieInput = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Scrape pinned/shopping-bag products from a Shopee Live session with prices, stock, and affiliate info."""
        return self._call_export(
            "MinSign_GetLiveBagItems",
            "get_live_bag_items",
            {
                "liveUrl": live_url,
                "sessionId": str(session_id or ""),
                "offset": offset,
                "limit": limit,
                "country": country,
                "cookie": cookie,
                "proxy": proxy,
            },
        )["data"]

    def buff_live_view(
        self,
        live_url: str = "",
        session_id: str = "",
        proxy: str = "",
        cookie: CookieInput = "",
        watch_seconds: int = 18,
        simulate_wait: bool = False,
        connect_ws: bool = True,
        pull_stream: bool = True,
        report_heartbeat: bool = True,
        send_exit: bool = True,
        send_like: bool = False,
        like_count: int = 0,
        bypass_stream_proxy: bool = False,
        stream_lite_mode: bool = False,
        country: str = "VN",
        account_id: str = "",
        device_id: str = "",
        from_source: str = "share",
    ) -> Dict[str, Any]:
        """Run a single Shopee Live viewer session (join, stream pull, WebSocket, heartbeat, optional likes)."""
        return self.invoke(
            "buff_live_view",
            {
                "liveUrl": live_url,
                "sessionId": str(session_id or ""),
                "proxy": proxy,
                "cookie": cookie,
                "watchSeconds": watch_seconds,
                "simulateWait": simulate_wait,
                "connectWs": connect_ws,
                "pullStream": pull_stream,
                "reportHeartbeat": report_heartbeat,
                "sendExit": send_exit,
                "sendLike": send_like,
                "likeCount": like_count,
                "bypassStreamProxy": bypass_stream_proxy,
                "streamLiteMode": stream_lite_mode,
                "country": country,
                "accountId": account_id,
                "deviceId": device_id,
                "fromSource": from_source,
            },
        )["data"]

    def buff_live_batch(
        self,
        live_url: str = "",
        session_id: str = "",
        target_views: int = 10,
        concurrency: int = 5,
        proxies: Optional[List[str]] = None,
        cookies: Optional[List[CookieInput]] = None,
        watch_seconds: int = 18,
        simulate_wait: bool = False,
        connect_ws: bool = True,
        pull_stream: bool = True,
        report_heartbeat: bool = True,
        send_exit: bool = True,
        send_like: bool = False,
        like_count: int = 0,
        bypass_stream_proxy: bool = False,
        stream_lite_mode: bool = False,
        stagger_ms: int = 0,
        country: str = "VN",
        from_source: str = "share",
    ) -> Dict[str, Any]:
        """Run concurrent Shopee Live viewer sessions with proxy/cookie rotation."""
        return self.invoke(
            "buff_live_batch",
            {
                "liveUrl": live_url,
                "sessionId": str(session_id or ""),
                "targetViews": target_views,
                "concurrency": concurrency,
                "proxies": proxies or [],
                "cookies": cookies or [],
                "watchSeconds": watch_seconds,
                "simulateWait": simulate_wait,
                "connectWs": connect_ws,
                "pullStream": pull_stream,
                "reportHeartbeat": report_heartbeat,
                "sendExit": send_exit,
                "sendLike": send_like,
                "likeCount": like_count,
                "bypassStreamProxy": bypass_stream_proxy,
                "streamLiteMode": stream_lite_mode,
                "staggerMs": stagger_ms,
                "country": country,
                "fromSource": from_source,
            },
        )["data"]

    # =========================================================================
    # Group 8: Shopee MCN, Accept/Reply Invitations & Affiliate Center (v2.1.0)
    # =========================================================================

    def get_affiliate_user_profile(
        self,
        cookie: CookieInput,
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
        allow_mobile_fallback: bool = True,
    ) -> Dict[str, Any]:
        """Fetch Shopee Affiliate user profile, affiliateId, and KYC/MCN flags (/api/v3/user/profile)."""
        return self._call_export(
            "MinSign_GetAffiliateUserProfile",
            "get_affiliate_user_profile",
            {
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
                "allowMobileFallback": allow_mobile_fallback,
            },
        )["data"]

    def get_mcn_partnership_status(
        self,
        cookie: CookieInput,
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
        page_num: int = 1,
        page_size: int = 20,
        fast_fallback: bool = True,
        fast_only: bool = False,
        include_entry_point: bool = False,
    ) -> Dict[str, Any]:
        """Scan an Affiliate account's ongoing MCN partnership and pending MCN invitations."""
        return self._call_export(
            "MinSign_GetMcnPartnershipStatus",
            "get_mcn_partnership_status",
            {
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
                "pageNum": page_num,
                "pageSize": page_size,
                "fastFallback": fast_fallback,
                "fastOnly": fast_only,
                "includeEntryPoint": include_entry_point,
            },
        )["data"]

    def reply_mcn_invitation(
        self,
        cookie: CookieInput,
        decision: str = "accept",
        mcn_id: str = "",
        request_id: str = "",
        request_type: str = "InvitationRequest",
        is_accept: Optional[bool] = None,
        verify_after: bool = True,
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Accept or reject an MCN partnership invitation/request (auto-resolves pending invitation if IDs omitted)."""
        payload: Dict[str, Any] = {
            "cookie": cookie,
            "decision": decision,
            "mcnId": mcn_id,
            "requestId": request_id,
            "requestType": request_type,
            "verifyAfter": verify_after,
            "country": country,
            "proxy": proxy,
            "accountId": account_id,
            "deviceId": device_id,
        }
        if is_accept is not None:
            payload["isAccept"] = is_accept
        return self._call_export("MinSign_ReplyMcnInvitation", "reply_mcn_invitation", payload)["data"]

    def get_mcn_kol_partnerships(
        self,
        cookie: CookieInput,
        mcn_id: str = "",
        affiliate_id: str = "",
        affiliate_name: str = "",
        tab_status_filter: str = "",
        page_num: int = 1,
        page_size: int = 20,
        include_meta: bool = False,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """List KOL/Affiliate partnerships from the MCN Portal (mcn.affiliate.shopee.*)."""
        return self._call_export(
            "MinSign_GetMcnKolPartnerships",
            "get_mcn_kol_partnerships",
            {
                "cookie": cookie,
                "mcnId": mcn_id,
                "affiliateId": affiliate_id,
                "affiliateName": affiliate_name,
                "tabStatusFilter": tab_status_filter,
                "pageNum": page_num,
                "pageSize": page_size,
                "includeMeta": include_meta,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def send_mcn_partnership_invitation(
        self,
        cookie: CookieInput,
        mcn_id: str,
        mcn_fee_rate_percent: int,
        affiliate_id: str = "",
        username: str = "",
        end_date_timestamp: int = 0,
        duration_days: int = 0,
        validate_first: bool = True,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Send an MCN partnership invitation from MCN Portal to an Affiliate/KOL."""
        return self._call_export(
            "MinSign_SendMcnPartnershipInvitation",
            "send_mcn_partnership_invitation",
            {
                "cookie": cookie,
                "mcnId": mcn_id,
                "affiliateId": affiliate_id,
                "username": username,
                "mcnFeeRatePercent": mcn_fee_rate_percent,
                "endDateTimestamp": end_date_timestamp,
                "durationDays": duration_days,
                "validateFirst": validate_first,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def manage_mcn_partnership(
        self,
        cookie: CookieInput,
        action: str,
        mcn_id: str,
        affiliate_id: str,
        partnership_id: str = "",
        request_id: str = "",
        request_type: str = "",
        is_accept: Optional[bool] = None,
        new_mcn_fee_rate_percent: int = 0,
        new_end_date_timestamp: int = 0,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Manage MCN-side KOL partnerships (reply|accept|reject|change_fee|extend|cancel|history)."""
        payload: Dict[str, Any] = {
            "cookie": cookie,
            "action": action,
            "mcnId": mcn_id,
            "affiliateId": affiliate_id,
            "partnershipId": partnership_id,
            "requestId": request_id,
            "requestType": request_type,
            "newMcnFeeRatePercent": new_mcn_fee_rate_percent,
            "newEndDateTimestamp": new_end_date_timestamp,
            "country": country,
            "proxy": proxy,
        }
        if is_accept is not None:
            payload["isAccept"] = is_accept
        return self._call_export("MinSign_ManageMcnPartnership", "manage_mcn_partnership", payload)["data"]

    def get_mcn_analytics(
        self,
        cookie: CookieInput,
        mode: str = "core",
        start_time: int = 0,
        end_time: int = 0,
        affiliate_id: str = "",
        campaign_id: str = "",
        page_num: int = 1,
        page_size: int = 20,
        variables: Optional[Dict[str, Any]] = None,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Query MCN Portal metrics, affiliate analytics, campaigns, campaign detail, or basic info."""
        return self._call_export(
            "MinSign_GetMcnAnalytics",
            "get_mcn_analytics",
            {
                "cookie": cookie,
                "mode": mode,
                "startTime": start_time,
                "endTime": end_time,
                "affiliateId": affiliate_id,
                "campaignId": campaign_id,
                "pageNum": page_num,
                "pageSize": page_size,
                "variables": variables or {},
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def get_affiliate_payment_tax(
        self,
        cookie: CookieInput,
        country: str = "",
        proxy: str = "",
        account_id: str = "",
        device_id: str = "",
    ) -> Dict[str, Any]:
        """Fetch normalized bank payment, tax TIN/CCCD, and EWT/VAT settings (/api/v3/payment_setting/display)."""
        return self._call_export(
            "MinSign_GetAffiliatePaymentTax",
            "get_affiliate_payment_tax",
            {
                "cookie": cookie,
                "country": country,
                "proxy": proxy,
                "accountId": account_id,
                "deviceId": device_id,
            },
        )["data"]

    def get_affiliate_click_report(
        self,
        cookie: CookieInput,
        start_time: int = 0,
        end_time: int = 0,
        page_num: int = 1,
        page_offset: int = 0,
        page_limit: int = 20,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch Shopee Affiliate click analytics (/api/v1/click_report/list)."""
        return self._call_export(
            "MinSign_GetAffiliateClickReport",
            "get_affiliate_click_report",
            {
                "cookie": cookie,
                "startTime": start_time,
                "endTime": end_time,
                "pageNum": page_num,
                "pageOffset": page_offset,
                "pageLimit": page_limit,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    def get_affiliate_billing(
        self,
        cookie: CookieInput,
        days: int = 365,
        start_time: int = 0,
        end_time: int = 0,
        validation_id: str = "",
        include_details: bool = False,
        country: str = "",
        proxy: str = "",
    ) -> Dict[str, Any]:
        """Fetch Affiliate payout billing list and per-bill details including MCN fee deductions."""
        return self._call_export(
            "MinSign_GetAffiliateBilling",
            "get_affiliate_billing",
            {
                "cookie": cookie,
                "days": days,
                "startTime": start_time,
                "endTime": end_time,
                "validationId": validation_id,
                "includeDetails": include_details,
                "country": country,
                "proxy": proxy,
            },
        )["data"]

    # =========================================================================
    # Group 7: Universal Signed HTTP Gateway (App + Web)
    # =========================================================================

    def execute_signed_request(
        self,
        url: str,
        method: str = "GET",
        body: Any = None,
        proxy: str = "",
        cookie: CookieInput = "",
        country: str = "",
        account_id: str = "",
        device_id: str = "",
        brand: str = "",
        include_risk_tokens: bool = False,
        attach_risk_headers: bool = False,
        force_refresh_risk: bool = False,
        sec_token: str = "",
        custom_headers: Optional[Dict[str, str]] = None,
        client_type: str = "app",
    ) -> Dict[str, Any]:
        """Sign and execute any arbitrary Shopee HTTP request (supports client_type='app' or 'web')."""
        return self.invoke(
            "execute_signed_request",
            {
                "url": url,
                "method": method,
                "body": body,
                "proxy": proxy,
                "cookie": cookie,
                "country": country,
                "accountId": account_id,
                "deviceId": device_id,
                "brand": brand,
                "includeRiskTokens": include_risk_tokens,
                "attachRiskHeaders": attach_risk_headers,
                "forceRefreshRisk": force_refresh_risk,
                "secToken": sec_token,
                "customHeaders": custom_headers or {},
                "clientType": client_type,
            },
        )["data"]
