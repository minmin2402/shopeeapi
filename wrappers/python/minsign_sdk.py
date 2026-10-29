"""
Official Python Wrapper cho MinSign Native Universal SDK (minsign_sdk.dll / libminsign_sdk.so)
Không cần cài thêm bất kỳ thư viện ngoài nào (sử dụng ctypes chuẩn của Python).
Tự động giải phóng con trỏ C-ABI qua MinSign_Free(ptr) an toàn tuyệt đối.
"""
from __future__ import annotations

import ctypes
import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional


class MinSignError(RuntimeError):
    pass


class MinSignClient:
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
        if not api_key or not api_key.strip():
            raise ValueError("Bắt buộc truyền mã X-API-Key (api_key).")

        resolved_dll = self._resolve_dll_path(dll_path)
        self._lib = ctypes.CDLL(str(resolved_dll))

        # Khai báo chữ ký hàm C-ABI (dùng c_void_p để giữ nguyên địa chỉ vùng nhớ truyền vào MinSign_Free)
        self._lib.MinSign_Version.argtypes = []
        self._lib.MinSign_Version.restype = ctypes.c_void_p

        self._lib.MinSign_Init.argtypes = [ctypes.c_char_p]
        self._lib.MinSign_Init.restype = ctypes.c_void_p

        self._lib.MinSign_CheckApiKey.argtypes = []
        self._lib.MinSign_CheckApiKey.restype = ctypes.c_void_p

        self._lib.MinSign_ListLocalDevices.argtypes = []
        self._lib.MinSign_ListLocalDevices.restype = ctypes.c_void_p

        self._lib.MinSign_Invoke.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.MinSign_Invoke.restype = ctypes.c_void_p

        self._lib.MinSign_Free.argtypes = [ctypes.c_void_p]
        self._lib.MinSign_Free.restype = None

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
            raise FileNotFoundError(f"Không tìm thấy thư viện Native SDK tại: {p}")

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
            f"Không tìm thấy {lib_name}. Hãy đặt {lib_name} cùng thư mục hoặc truyền dll_path=..."
        )

    def _consume_ptr(self, ptr: Optional[int], raise_on_error: bool = True) -> Dict[str, Any]:
        if not ptr:
            raise MinSignError("minsign_sdk.dll trả về con trỏ NULL.")
        try:
            raw_bytes = ctypes.string_at(ptr)
            parsed: Dict[str, Any] = json.loads(raw_bytes.decode("utf-8"))
        finally:
            self._lib.MinSign_Free(ctypes.c_void_p(ptr))

        if raise_on_error and not parsed.get("ok", False):
            raise MinSignError(parsed.get("error") or json.dumps(parsed, ensure_ascii=False))
        return parsed

    def invoke(self, action: str, payload: Optional[Dict[str, Any]] = None, raise_on_error: bool = True) -> Dict[str, Any]:
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        ptr = self._lib.MinSign_Invoke(action.encode("utf-8"), body)
        return self._consume_ptr(ptr, raise_on_error=raise_on_error)

    # --- Nhóm 1: Quản trị Key & Thiết bị cố định theo Acc ---
    def version(self) -> Dict[str, Any]:
        return self._consume_ptr(self._lib.MinSign_Version())["data"]

    def check_api_key(self) -> Dict[str, Any]:
        return self._consume_ptr(self._lib.MinSign_CheckApiKey())["data"]

    def bind_account_device(self, cookie: str = "", account_id: str = "", country: str = "VN", device_id: str = "") -> Dict[str, Any]:
        return self.invoke("bind_account_device", {"cookie": cookie, "accountId": account_id, "country": country, "deviceId": device_id})["data"]

    def list_local_devices(self) -> Dict[str, Any]:
        return self._consume_ptr(self._lib.MinSign_ListLocalDevices())["data"]

    def remove_local_device(self, account_key: str) -> Dict[str, Any]:
        return self.invoke("remove_local_device", {"accountKey": account_key})["data"]

    def sign_raw(self, url: str, body: str = "", country: str = "", cookie: str = "", account_id: str = "", device_id: str = "", fetch_live: bool = False) -> Dict[str, Any]:
        return self.invoke(
            "sign_raw",
            {"url": url, "body": body, "country": country, "cookie": cookie, "accountId": account_id, "deviceId": device_id, "fetchLive": fetch_live},
        )["data"]

    # --- Nhóm 2: Chi tiết Sản Phẩm, Gian Hàng, Voucher, Tìm kiếm ---
    def get_product_detail(self, product_url: str = "", shop_id: str = "", item_id: str = "", proxy: str = "", cookie: str = "", country: str = "", account_id: str = "", include_shop: bool = True) -> Dict[str, Any]:
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

    def get_shop_overview(self, shop_url: str = "", shop_id: str = "", username: str = "", proxy: str = "", cookie: str = "", country: str = "") -> Dict[str, Any]:
        return self.invoke("get_shop_overview", {"shopUrl": shop_url, "shopId": str(shop_id or ""), "username": username, "proxy": proxy, "cookie": cookie, "country": country})["data"]

    def get_shop_products(self, shop_id: str = "", shop_url: str = "", limit: int = 30, offset: int = 0, proxy: str = "", cookie: str = "", country: str = "") -> Dict[str, Any]:
        return self.invoke("get_shop_products", {"shopId": str(shop_id or ""), "shopUrl": shop_url, "limit": limit, "offset": offset, "proxy": proxy, "cookie": cookie, "country": country})["data"]

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
        cookie: str = "",
        country: str = "",
        account_id: str = "",
    ) -> Dict[str, Any]:
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

    def get_shop_categories(self, shop_id: str = "", shop_url: str = "", proxy: str = "", cookie: str = "", country: str = "") -> Dict[str, Any]:
        return self.invoke("get_shop_categories", {"shopId": str(shop_id or ""), "shopUrl": shop_url, "proxy": proxy, "cookie": cookie, "country": country})["data"]

    def get_shop_vouchers(self, shop_id: str = "", shop_url: str = "", proxy: str = "", cookie: str = "", country: str = "") -> Dict[str, Any]:
        return self.invoke("get_shop_vouchers", {"shopId": str(shop_id or ""), "shopUrl": shop_url, "proxy": proxy, "cookie": cookie, "country": country})["data"]

    def search_products(self, keyword: str, country: str = "VN", sort_by: str = "relevancy", page: int = 0, limit: int = 20, proxy: str = "", cookie: str = "") -> Dict[str, Any]:
        return self.invoke("search_products", {"keyword": keyword, "country": country, "sortBy": sort_by, "page": page, "limit": limit, "proxy": proxy, "cookie": cookie})["data"]

    def get_category_tree(self, country: str = "VN", proxy: str = "") -> Dict[str, Any]:
        return self.invoke("get_category_tree", {"country": country, "proxy": proxy})["data"]

    # --- Nhóm 3: Đăng Video Shopee & Affiliate ---
    def upload_shopee_video(
        self,
        video_path: str,
        cookie: str,
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

    def precheck_video_upload(self, cookie: str, proxy: str = "", country: str = "VN", account_id: str = "") -> Dict[str, Any]:
        return self.invoke("precheck_video_upload", {"cookie": cookie, "proxy": proxy, "country": country, "accountId": account_id})["data"]

    def get_affiliate_products(self, cookie: str, keyword: str = "", page_offset: int = 0, page_limit: int = 20, proxy: str = "", country: str = "VN") -> Dict[str, Any]:
        return self.invoke("get_affiliate_products", {"cookie": cookie, "keyword": keyword, "pageOffset": page_offset, "pageLimit": page_limit, "proxy": proxy, "country": country})["data"]

    def mutate_mp4_fingerprint(self, input_path: str, output_path: str = "", in_place: bool = False) -> Dict[str, Any]:
        return self.invoke("mutate_mp4_fingerprint", {"inputPath": input_path, "outputPath": output_path, "inPlace": in_place})["data"]

    # --- Nhóm 4: Buff View Shopee Video & Kênh Video ---
    def buff_video_view(self, video_url: str = "", post_id: str = "", proxy: str = "", cookie: str = "", watch_seconds: int = 18, country: str = "VN") -> Dict[str, Any]:
        return self.invoke("buff_video_view", {"videoUrl": video_url, "postId": post_id, "proxy": proxy, "cookie": cookie, "watchSeconds": watch_seconds, "country": country})["data"]

    def buff_video_batch(self, video_url: str, target_views: int = 10, concurrency: int = 5, proxies: Optional[List[str]] = None, cookies: Optional[List[str]] = None, watch_seconds: int = 18, country: str = "VN") -> Dict[str, Any]:
        return self.invoke(
            "buff_video_batch",
            {"videoUrl": video_url, "targetViews": target_views, "concurrency": concurrency, "proxies": proxies or [], "cookies": cookies or [], "watchSeconds": watch_seconds, "country": country},
        )["data"]

    def get_video_detail(self, video_url: str = "", post_id: str = "", proxy: str = "", cookie: str = "", country: str = "VN") -> Dict[str, Any]:
        return self.invoke("get_video_detail", {"videoUrl": video_url, "postId": post_id, "proxy": proxy, "cookie": cookie, "country": country})["data"]

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
        cookie: str = "",
        country: str = "",
        account_id: str = "",
    ) -> Dict[str, Any]:
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

    def get_channel_and_hashtag_videos(self, mode: str = "channel", request_user_id: str = "", hashtag_id: str = "", limit: int = 20, proxy: str = "", cookie: str = "", country: str = "VN") -> Dict[str, Any]:
        return self.invoke("get_channel_and_hashtag_videos", {"mode": mode, "requestUserId": request_user_id, "hashtagId": hashtag_id, "limit": limit, "proxy": proxy, "cookie": cookie, "country": country})["data"]

    # --- Nhóm 5: Giỏ hàng & Gọi Ký Mở Rộng ---
    def add_to_cart(self, shop_id: int, item_id: int, cookie: str, model_id: int = 0, quantity: int = 1, proxy: str = "", country: str = "VN") -> Dict[str, Any]:
        return self.invoke("add_to_cart", {"shopId": shop_id, "itemId": item_id, "modelId": model_id, "quantity": quantity, "cookie": cookie, "proxy": proxy, "country": country})["data"]

    def execute_signed_request(self, url: str, method: str = "GET", body: Any = None, proxy: str = "", cookie: str = "", country: str = "", custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self.invoke("execute_signed_request", {"url": url, "method": method, "body": body, "proxy": proxy, "cookie": cookie, "country": country, "customHeaders": custom_headers or {}})["data"]
