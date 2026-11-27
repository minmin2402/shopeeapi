using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

namespace MinSign
{
    /// <summary>
    /// Official C# / .NET Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll).
    /// Compatible with .NET Framework 4.7.2+, .NET Core 3.1+, and .NET 6/7/8/9 (x64).
    /// Automatically frees every C-ABI heap allocation via <c>MinSign_Free</c> to prevent memory leaks.
    /// Exposes all 44 production APIs across 8 Shopee regions with App Mobile and Web Chrome signing modes.
    /// </summary>
    public sealed class MinSignClient : IDisposable
    {
        private const string DllName = "minsign_sdk.dll";

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern bool SetDllDirectoryW(string lpPathName);

        static MinSignClient()
        {
            string[] candidates =
            {
                Path.Combine(AppContext.BaseDirectory, "bin", "win-x64"),
                Path.Combine(Directory.GetCurrentDirectory(), "bin", "win-x64"),
                Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "bin", "win-x64"))
            };
            foreach (var dir in candidates)
            {
                if (File.Exists(Path.Combine(dir, DllName)))
                {
                    SetDllDirectoryW(dir);
                    break;
                }
            }
        }

        // Core C-ABI exports
        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Version();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Init(IntPtr configJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_CheckApiKey();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ListLocalDevices();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetRiskToken(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Invoke(IntPtr actionUtf8, IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void MinSign_Free(IntPtr ptr);

        // v2.0.0 C-ABI exports (13 new production APIs)
        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_SignWeb(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ResolveShopeeUrl(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_BatchGetProductDetails(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetProductRatings(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetFlashSaleItems(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetRecommendProducts(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetSearchSuggestions(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAccountProfile(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetCartSummary(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ClaimShopVoucher(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliateOfferList(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliateCommissionReport(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetLiveBagItems(IntPtr reqJsonUtf8);

        // v2.1.0 C-ABI exports (10 MCN, Partnership Accept/Reply & Affiliate Center APIs)
        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliateUserProfile(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetMcnPartnershipStatus(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ReplyMcnInvitation(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetMcnKolPartnerships(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_SendMcnPartnershipInvitation(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ManageMcnPartnership(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetMcnAnalytics(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliatePaymentTax(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliateClickReport(IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_GetAffiliateBilling(IntPtr reqJsonUtf8);

        private bool _disposed;

        /// <summary>
        /// Initializes the native MinSign SDK client with your X-API-Key and vault configuration.
        /// </summary>
        public MinSignClient(
            string apiKey,
            string signerUrl = "https://vip-sign.minmintool.site",
            string vaultFilePath = "./minsign_data/devices_vault.json",
            string vaultSecret = "",
            string defaultCountry = "VN",
            int timeoutMs = 25000)
        {
            if (string.IsNullOrWhiteSpace(apiKey))
                throw new ArgumentException("X-API-Key (apiKey) is required.", nameof(apiKey));

            var initRes = CallJsonExport(MinSign_Init, new
            {
                apiKey = apiKey.Trim(),
                signerUrl,
                vaultFilePath,
                vaultSecret,
                defaultCountry,
                timeoutMs
            });

            EnsureOk(initRes);
        }

        // =====================================================================
        // Group 1: Key Management, Local Device Vault & Core Signing (App + Web)
        // =====================================================================

        /// <summary>Returns SDK version and build metadata.</summary>
        public JsonElement Version() => CallPtr(MinSign_Version);

        /// <summary>Checks X-API-Key validity, plan tier, and remaining quota.</summary>
        public JsonElement CheckApiKey() => CallPtr(MinSign_CheckApiKey);

        /// <summary>Lists all virtual device profiles saved in the local vault.</summary>
        public JsonElement ListLocalDevices() => CallPtr(MinSign_ListLocalDevices);

        /// <summary>Binds a persistent virtual device fingerprint to an account.</summary>
        public JsonElement BindAccountDevice(object request) => Invoke("bind_account_device", request);

        /// <summary>Removes a bound virtual device profile from the local vault.</summary>
        public JsonElement RemoveLocalDevice(string accountKey) => Invoke("remove_local_device", new { accountKey });

        /// <summary>
        /// Generates Shopee security headers for a raw URL and body.
        /// Set <c>clientType = "web"</c> to route through the Web Chrome 131 signer, or omit / <c>"app"</c> for mobile app signing.
        /// </summary>
        public JsonElement SignRaw(object request) => Invoke("sign_raw", request);

        /// <summary>
        /// Generates Shopee Web Chrome 131 security headers and patched cookies via <c>MinSign_SignWeb</c>.
        /// Accepts: <c>{ url, body, country, cookie, accountId, deviceId, proxy, fetchLive }</c>.
        /// </summary>
        public JsonElement SignWeb(object request) => CallJsonExport(MinSign_SignWeb, request);

        /// <summary>Fetches or refreshes Shopee anti-fraud risk tokens.</summary>
        public JsonElement GetRiskToken(object request = null) => CallJsonExport(MinSign_GetRiskToken, request);

        // =====================================================================
        // Group 2: Products, Shops, Vouchers, Search, Recommendations & URL Tools
        // =====================================================================

        /// <summary>
        /// Parses any Shopee URL (product, shop, video, live, shortlink) or constructs a canonical product URL from <c>shopId</c> + <c>itemId</c>.
        /// Accepts: <c>{ url, shopId, itemId, country, proxy, followRedirect }</c>.
        /// </summary>
        public JsonElement ResolveShopeeUrl(object request) => CallJsonExport(MinSign_ResolveShopeeUrl, request);

        /// <summary>Fetches detailed product metadata, pricing, stock, and variations.</summary>
        public JsonElement GetProductDetail(object request) => Invoke("get_product_detail", request);

        /// <summary>
        /// Fetches multiple product details concurrently using the native Go worker pool with proxy/cookie rotation.
        /// Accepts: <c>{ items, productUrls, country, cookie, cookies, proxy, proxies, concurrency }</c>.
        /// </summary>
        public JsonElement BatchGetProductDetails(object request) => CallJsonExport(MinSign_BatchGetProductDetails, request);

        /// <summary>
        /// Fetches product customer reviews, star counts, and review media URLs.
        /// Accepts: <c>{ productUrl, shopId, itemId, limit, offset, filter, type, country, cookie, proxy }</c>.
        /// </summary>
        public JsonElement GetProductRatings(object request) => CallJsonExport(MinSign_GetProductRatings, request);

        /// <summary>
        /// Fetches active Shopee Flash Sale sessions and discounted items.
        /// Accepts: <c>{ promotionId, limit, offset, country, cookie, proxy }</c>.
        /// </summary>
        public JsonElement GetFlashSaleItems(object request = null) => CallJsonExport(MinSign_GetFlashSaleItems, request);

        /// <summary>
        /// Fetches Shopee recommendation feeds (daily discover or similar products for an item).
        /// Accepts: <c>{ bundle, shopId, itemId, limit, offset, country, cookie, proxy }</c>.
        /// </summary>
        public JsonElement GetRecommendProducts(object request = null) => CallJsonExport(MinSign_GetRecommendProducts, request);

        /// <summary>
        /// Fetches live autocomplete search keyword suggestions.
        /// Accepts: <c>{ keyword, limit, country, cookie, proxy }</c>.
        /// </summary>
        public JsonElement GetSearchSuggestions(object request) => CallJsonExport(MinSign_GetSearchSuggestions, request);

        /// <summary>Fetches shop profile metadata, rating, and follower counts.</summary>
        public JsonElement GetShopOverview(object request) => Invoke("get_shop_overview", request);

        /// <summary>Lists products in a shop with pagination.</summary>
        public JsonElement GetShopProducts(object request) => Invoke("get_shop_products", request);

        /// <summary>Fetches newly listed products of a shop with optional cursor filtering.</summary>
        public JsonElement GetShopNewestProducts(object request) => Invoke("get_shop_newest_products", request);

        /// <summary>Lists Shopee Videos posted by a shop or creator profile.</summary>
        public JsonElement GetShopVideos(object request) => Invoke("get_shop_videos", request);

        /// <summary>Fetches in-shop category collections.</summary>
        public JsonElement GetShopCategories(object request) => Invoke("get_shop_categories", request);

        /// <summary>Lists active discount vouchers offered by a shop.</summary>
        public JsonElement GetShopVouchers(object request) => Invoke("get_shop_vouchers", request);

        /// <summary>Searches products by keyword.</summary>
        public JsonElement SearchProducts(object request) => Invoke("search_products", request);

        /// <summary>Searches visually similar products by image path, base64, URL, or item ID.</summary>
        public JsonElement SearchProductsByImage(object request) => Invoke("search_products_by_image", request);

        /// <summary>Detects object bounding boxes in an image for visual search.</summary>
        public JsonElement GetImageBoundingBox(object request) => Invoke("get_image_bounding_box", request);

        /// <summary>Fetches the marketplace category hierarchy tree for a Shopee region.</summary>
        public JsonElement GetCategoryTree(object request = null) => Invoke("get_category_tree", request ?? new { });

        // =====================================================================
        // Group 3: Account, Cart & Voucher Actions
        // =====================================================================

        /// <summary>
        /// Checks cookie liveness and retrieves basic Shopee account profile information.
        /// Accepts: <c>{ cookie, country, proxy, accountId, deviceId }</c>.
        /// </summary>
        public JsonElement GetAccountProfile(object request) => CallJsonExport(MinSign_GetAccountProfile, request);

        /// <summary>
        /// Retrieves the authenticated account's shopping cart groups, item count, and subtotal.
        /// Accepts: <c>{ cookie, country, proxy, accountId, deviceId }</c>.
        /// </summary>
        public JsonElement GetCartSummary(object request) => CallJsonExport(MinSign_GetCartSummary, request);

        /// <summary>
        /// Claims/saves a shop voucher into the account's voucher wallet with risk headers attached.
        /// Accepts: <c>{ voucherCode, promotionId, signature, shopId, cookie, country, proxy, accountId, deviceId }</c>.
        /// </summary>
        public JsonElement ClaimShopVoucher(object request) => CallJsonExport(MinSign_ClaimShopVoucher, request);

        // =====================================================================
        // Group 4: Shopee Video Studio & Affiliate Marketing
        // =====================================================================

        /// <summary>Uploads and publishes a Shopee Video with optional product tags and MP4 mutation.</summary>
        public JsonElement UploadShopeeVideo(object request) => Invoke("upload_shopee_video", request);

        /// <summary>Verifies whether an account can publish Shopee Videos.</summary>
        public JsonElement PrecheckVideoUpload(object request) => Invoke("precheck_video_upload", request);

        /// <summary>Searches affiliate-eligible products for video tagging.</summary>
        public JsonElement GetAffiliateProducts(object request) => Invoke("get_affiliate_products", request);

        /// <summary>
        /// Queries Shopee Affiliate product offers with commission rates and monthly sales via Web Signer.
        /// Accepts: <c>{ keyword, shopId, listType, sortType, pageOffset, pageLimit, cookie, country, proxy }</c>.
        /// </summary>
        public JsonElement GetAffiliateOfferList(object request) => CallJsonExport(MinSign_GetAffiliateOfferList, request);

        /// <summary>
        /// Queries Shopee Affiliate conversion and commission report records via Web Signer.
        /// Accepts: <c>{ startTime, endTime, pageOffset, pageLimit, cookie, country, proxy }</c>.
        /// </summary>
        public JsonElement GetAffiliateCommissionReport(object request) => CallJsonExport(MinSign_GetAffiliateCommissionReport, request);

        /// <summary>Converts a single Shopee URL into a tracked affiliate short link.</summary>
        public JsonElement ConvertAffiliateLink(object request) => Invoke("convert_affiliate_link", request);

        /// <summary>Batch-converts multiple Shopee URLs into tracked affiliate short links.</summary>
        public JsonElement BatchConvertAffiliateLinks(object request) => Invoke("batch_convert_affiliate_links", request);

        /// <summary>Mutates MP4 metadata/fingerprint locally without re-encoding.</summary>
        public JsonElement MutateMp4Fingerprint(object request) => Invoke("mutate_mp4_fingerprint", request);

        // =====================================================================
        // Group 5: Shopee Video Discovery & View Booster
        // =====================================================================

        /// <summary>Executes a single Shopee Video view telemetry session.</summary>
        public JsonElement BuffVideoView(object request) => Invoke("buff_video_view", request);

        /// <summary>Runs concurrent Shopee Video view sessions with proxy/cookie rotation.</summary>
        public JsonElement BuffVideoBatch(object request) => Invoke("buff_video_batch", request);

        /// <summary>Fetches Shopee Video metadata, metrics, and direct media URL.</summary>
        public JsonElement GetVideoDetail(object request) => Invoke("get_video_detail", request);

        /// <summary>Fetches videos from a creator channel or hashtag feed.</summary>
        public JsonElement GetChannelAndHashtagVideos(object request) => Invoke("get_channel_and_hashtag_videos", request);

        // =====================================================================
        // Group 6: Shopee Live Commerce & Viewer Pipeline
        // =====================================================================

        /// <summary>Fetches Shopee Live session metadata, viewer metrics, and stream URLs.</summary>
        public JsonElement GetLiveSessionDetail(object request) => Invoke("get_live_session_detail", request);

        /// <summary>
        /// Scrapes pinned shopping-bag items from a Shopee Live session with prices, stock, and affiliate details.
        /// Accepts: <c>{ liveUrl, sessionId, offset, limit, country, cookie, proxy }</c>.
        /// </summary>
        public JsonElement GetLiveBagItems(object request) => CallJsonExport(MinSign_GetLiveBagItems, request);

        /// <summary>Runs a single Shopee Live viewer session.</summary>
        public JsonElement BuffLiveView(object request) => Invoke("buff_live_view", request);

        /// <summary>Runs concurrent Shopee Live viewer sessions with proxy/cookie rotation.</summary>
        public JsonElement BuffLiveBatch(object request) => Invoke("buff_live_batch", request);

        // =====================================================================
        // Group 8: Shopee MCN, Accept/Reply Invitations & Affiliate Center (v2.1.0)
        // =====================================================================

        /// <summary>Fetches Affiliate profile, affiliateId, and MCN/KYC flags (/api/v3/user/profile).</summary>
        public JsonElement GetAffiliateUserProfile(object request) => CallJsonExport(MinSign_GetAffiliateUserProfile, request);

        /// <summary>Scans ongoing MCN partnership and pending MCN invitations (with REST fallback).</summary>
        public JsonElement GetMcnPartnershipStatus(object request) => CallJsonExport(MinSign_GetMcnPartnershipStatus, request);

        /// <summary>Accepts or rejects an MCN partnership invitation/request.</summary>
        public JsonElement ReplyMcnInvitation(object request) => CallJsonExport(MinSign_ReplyMcnInvitation, request);

        /// <summary>Lists KOL/Affiliate partnerships from the MCN Portal.</summary>
        public JsonElement GetMcnKolPartnerships(object request) => CallJsonExport(MinSign_GetMcnKolPartnerships, request);

        /// <summary>Sends an MCN partnership invitation to a KOL/Affiliate.</summary>
        public JsonElement SendMcnPartnershipInvitation(object request) => CallJsonExport(MinSign_SendMcnPartnershipInvitation, request);

        /// <summary>Performs MCN Portal partnership actions (reply|accept|reject|change_fee|extend|cancel|history).</summary>
        public JsonElement ManageMcnPartnership(object request) => CallJsonExport(MinSign_ManageMcnPartnership, request);

        /// <summary>Queries MCN Portal analytics, affiliate metrics, campaigns, or basic info.</summary>
        public JsonElement GetMcnAnalytics(object request) => CallJsonExport(MinSign_GetMcnAnalytics, request);

        /// <summary>Fetches Affiliate payment bank &amp; tax TIN/CCCD verification settings.</summary>
        public JsonElement GetAffiliatePaymentTax(object request) => CallJsonExport(MinSign_GetAffiliatePaymentTax, request);

        /// <summary>Fetches Shopee Affiliate click analytics (/api/v1/click_report/list).</summary>
        public JsonElement GetAffiliateClickReport(object request) => CallJsonExport(MinSign_GetAffiliateClickReport, request);

        /// <summary>Fetches Affiliate payout billing list and details including MCN fee deductions.</summary>
        public JsonElement GetAffiliateBilling(object request) => CallJsonExport(MinSign_GetAffiliateBilling, request);

        // =====================================================================
        // Group 7: Universal Signed HTTP Gateway (App + Web)
        // =====================================================================

        /// <summary>
        /// Signs and executes any arbitrary Shopee HTTP request.
        /// Supports <c>clientType = "app"</c> (default) or <c>clientType = "web"</c>.
        /// </summary>
        public JsonElement ExecuteSignedRequest(object request) => Invoke("execute_signed_request", request);

        /// <summary>Universal action dispatcher invoking <c>MinSign_Invoke</c>.</summary>
        public JsonElement Invoke(string action, object payload)
        {
            string jsonStr = payload is string s ? s : JsonSerializer.Serialize(payload ?? new { });
            return CallPtr(() =>
            {
                IntPtr pAct = ToUtf8Ptr(action);
                IntPtr pReq = ToUtf8Ptr(jsonStr);
                try { return MinSign_Invoke(pAct, pReq); }
                finally
                {
                    Marshal.FreeHGlobal(pAct);
                    Marshal.FreeHGlobal(pReq);
                }
            });
        }

        private static JsonElement CallJsonExport(Func<IntPtr, IntPtr> exportFn, object request)
        {
            string jsonStr = request is string s ? s : JsonSerializer.Serialize(request ?? new { });
            return CallPtr(() =>
            {
                IntPtr pReq = ToUtf8Ptr(jsonStr);
                try { return exportFn(pReq); }
                finally { Marshal.FreeHGlobal(pReq); }
            });
        }

        private static JsonElement CallPtr(Func<IntPtr> fn)
        {
            IntPtr ptr = fn();
            if (ptr == IntPtr.Zero)
                throw new InvalidOperationException("minsign_sdk.dll returned a null pointer.");
            try
            {
                string utf8 = FromUtf8Ptr(ptr);
                using var doc = JsonDocument.Parse(utf8);
                return doc.RootElement.Clone();
            }
            finally
            {
                MinSign_Free(ptr);
            }
        }

        private static void EnsureOk(JsonElement root)
        {
            if (root.TryGetProperty("ok", out var okProp) && !okProp.GetBoolean())
            {
                string err = root.TryGetProperty("error", out var eProp) ? eProp.GetString() : root.GetRawText();
                throw new Exception($"MinSign SDK Error: {err}");
            }
        }

        private static IntPtr ToUtf8Ptr(string s)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(s ?? "");
            IntPtr mem = Marshal.AllocHGlobal(bytes.Length + 1);
            Marshal.Copy(bytes, 0, mem, bytes.Length);
            Marshal.WriteByte(mem, bytes.Length, 0);
            return mem;
        }

        private static string FromUtf8Ptr(IntPtr ptr)
        {
            int len = 0;
            while (Marshal.ReadByte(ptr, len) != 0) len++;
            byte[] buf = new byte[len];
            Marshal.Copy(ptr, buf, 0, len);
            return Encoding.UTF8.GetString(buf);
        }

        public void Dispose()
        {
            if (!_disposed) _disposed = true;
        }
    }
}
