package com.minsign.sdk;

import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Pointer;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Official Java JNA Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll / libminsign_sdk.so).
 *
 * <p>Dependencies:
 * <ul>
 *   <li>JDK 11+ (64-bit / x64)</li>
 *   <li>JNA ({@code net.java.dev.jna:jna:5.14.0} or newer) — zero third-party JSON dependencies required.</li>
 * </ul>
 *
 * <p>Memory safety guarantee: Every {@link Pointer} returned by the native C-ABI is read as UTF-8
 * and deterministically released via {@code MinSign_Free(ptr)} inside a {@code try / finally} block.
 */
public final class MinSignSdk implements AutoCloseable {

    public static final String DEFAULT_SIGNER_URL = "https://vip-sign.minmintool.site";
    public static final String DEFAULT_VAULT_FILE_PATH = "./minsign_data/devices_vault.json";

    /**
     * JNA C-ABI binding interface for {@code minsign_sdk.dll}.
     * String inputs are passed as null-terminated UTF-8 {@code byte[]} arrays to guarantee
     * locale-independent UTF-8 marshaling across all Windows/Linux JVMs.
     */
    public interface NativeLibrary extends Library {
        Pointer MinSign_Version();

        Pointer MinSign_Init(byte[] configJsonUtf8);

        Pointer MinSign_CheckApiKey();

        Pointer MinSign_ListLocalDevices();

        Pointer MinSign_GetRiskToken(byte[] reqJsonUtf8);

        Pointer MinSign_SignWeb(byte[] reqJsonUtf8);

        Pointer MinSign_ResolveShopeeUrl(byte[] reqJsonUtf8);

        Pointer MinSign_BatchGetProductDetails(byte[] reqJsonUtf8);

        Pointer MinSign_GetProductRatings(byte[] reqJsonUtf8);

        Pointer MinSign_GetFlashSaleItems(byte[] reqJsonUtf8);

        Pointer MinSign_GetRecommendProducts(byte[] reqJsonUtf8);

        Pointer MinSign_GetSearchSuggestions(byte[] reqJsonUtf8);

        Pointer MinSign_GetAccountProfile(byte[] reqJsonUtf8);

        Pointer MinSign_GetCartSummary(byte[] reqJsonUtf8);

        Pointer MinSign_ClaimShopVoucher(byte[] reqJsonUtf8);

        Pointer MinSign_GetAffiliateOfferList(byte[] reqJsonUtf8);

        Pointer MinSign_GetAffiliateCommissionReport(byte[] reqJsonUtf8);

        Pointer MinSign_GetLiveBagItems(byte[] reqJsonUtf8);

        Pointer MinSign_Invoke(byte[] actionUtf8, byte[] reqJsonUtf8);

        void MinSign_Free(Pointer ptr);
    }

    /**
     * Runtime exception raised on native load failures, NULL C-ABI pointers, or SDK initialization errors.
     */
    public static final class MinSignException extends RuntimeException {
        private static final long serialVersionUID = 1L;

        public MinSignException(String message) {
            super(message);
        }

        public MinSignException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    private final NativeLibrary nativeLib;
    private final String dllPath;
    private final String initInfoJson;
    private volatile boolean closed;

    /**
     * Create and initialize a MinSignSdk client using default signer URL, vault path, and VN region.
     *
     * @param apiKey X-API-Key obtained from https://vip-sign.minmintool.site
     */
    public MinSignSdk(String apiKey) {
        this(apiKey, null, DEFAULT_SIGNER_URL, DEFAULT_VAULT_FILE_PATH, "", "VN", 25000);
    }

    /**
     * Create and initialize a MinSignSdk client with full configuration.
     *
     * @param apiKey         X-API-Key obtained from https://vip-sign.minmintool.site
     * @param dllPath        Optional explicit path to minsign_sdk.dll / libminsign_sdk.so (null to auto-detect)
     * @param signerUrl      Cloud signer base URL
     * @param vaultFilePath  Local device vault JSON path
     * @param vaultSecret    Optional encryption passphrase for the local device vault
     * @param defaultCountry Default Shopee region (VN, ID, TH, MY, PH, SG, TW, BR)
     * @param timeoutMs      HTTP request timeout in milliseconds
     */
    public MinSignSdk(
            String apiKey,
            String dllPath,
            String signerUrl,
            String vaultFilePath,
            String vaultSecret,
            String defaultCountry,
            int timeoutMs
    ) {
        if (apiKey == null || apiKey.trim().isEmpty()) {
            throw new IllegalArgumentException("A non-empty X-API-Key (apiKey) is required.");
        }

        String effectiveSigner = (signerUrl == null || signerUrl.trim().isEmpty()) ? DEFAULT_SIGNER_URL : signerUrl.trim();
        String effectiveVault = (vaultFilePath == null || vaultFilePath.trim().isEmpty()) ? DEFAULT_VAULT_FILE_PATH : vaultFilePath.trim();
        String effectiveSecret = vaultSecret == null ? "" : vaultSecret;
        String effectiveCountry = (defaultCountry == null || defaultCountry.trim().isEmpty()) ? "VN" : defaultCountry.trim();
        int effectiveTimeout = timeoutMs > 0 ? timeoutMs : 25000;

        this.dllPath = resolveDllPath(dllPath);
        try {
            this.nativeLib = Native.load(this.dllPath, NativeLibrary.class);
        } catch (UnsatisfiedLinkError e) {
            throw new MinSignException(
                    "Failed to load MinSign native library at \"" + this.dllPath + "\". Ensure 64-bit JVM matches x64 DLL.",
                    e
            );
        }

        String configJson = "{"
                + "\"apiKey\":\"" + escapeJson(apiKey.trim()) + "\","
                + "\"signerUrl\":\"" + escapeJson(effectiveSigner) + "\","
                + "\"vaultFilePath\":\"" + escapeJson(effectiveVault) + "\","
                + "\"vaultSecret\":\"" + escapeJson(effectiveSecret) + "\","
                + "\"defaultCountry\":\"" + escapeJson(effectiveCountry) + "\","
                + "\"timeoutMs\":" + effectiveTimeout
                + "}";

        String initRes = consumePointer(this.nativeLib.MinSign_Init(toUtf8CString(configJson)));
        assertOk(initRes);
        this.initInfoJson = initRes;
    }

    /**
     * Resolve the native shared library path automatically across common working directory layouts.
     *
     * @param customPath Optional explicit path; pass null/blank for auto-discovery
     * @return Absolute path to {@code minsign_sdk.dll} or {@code libminsign_sdk.so}
     */
    public static String resolveDllPath(String customPath) {
        if (customPath != null && !customPath.trim().isEmpty()) {
            Path p = Paths.get(customPath.trim()).toAbsolutePath().normalize();
            if (Files.isRegularFile(p)) {
                return p.toString();
            }
            throw new MinSignException("MinSign native library not found at custom path: " + p);
        }

        boolean isWin = System.getProperty("os.name", "").toLowerCase(Locale.ROOT).contains("win");
        String libName = isWin ? "minsign_sdk.dll" : "libminsign_sdk.so";
        Path cwd = Paths.get("").toAbsolutePath().normalize();

        List<Path> candidates = new ArrayList<>();
        candidates.add(cwd.resolve(libName));
        candidates.add(cwd.resolve("bin").resolve("win-x64").resolve(libName));
        candidates.add(cwd.resolve("..").resolve("bin").resolve("win-x64").resolve(libName));
        candidates.add(cwd.resolve("..").resolve("..").resolve("bin").resolve("win-x64").resolve(libName));
        candidates.add(cwd.resolve("dist").resolve("win-x64").resolve(libName));

        for (Path cand : candidates) {
            Path normalized = cand.normalize();
            if (Files.isRegularFile(normalized)) {
                return normalized.toString();
            }
        }

        throw new MinSignException(
                "Could not locate " + libName + ". Place it in ./bin/win-x64/ or pass dllPath explicitly."
        );
    }

    /**
     * Return the raw JSON envelope returned by {@code MinSign_Init}.
     */
    public String getInitInfo() {
        return this.initInfoJson;
    }

    /**
     * Return the resolved path of the loaded native shared library.
     */
    public String getDllPath() {
        return this.dllPath;
    }

    /**
     * Check whether a raw SDK JSON envelope indicates success ({@code "ok":true}).
     */
    public static boolean isOk(String jsonResponse) {
        if (jsonResponse == null) {
            return false;
        }
        String compact = jsonResponse.replaceAll("\\s+", "");
        return compact.contains("\"ok\":true");
    }

    /**
     * Assert that a raw SDK JSON envelope returned {@code "ok":true}; otherwise throw {@link MinSignException}.
     */
    public static void assertOk(String jsonResponse) {
        if (!isOk(jsonResponse)) {
            throw new MinSignException("MinSign SDK Error: " + jsonResponse);
        }
    }

    /**
     * Universal dynamic dispatcher calling {@code MinSign_Invoke(action, jsonPayload)}.
     *
     * @param action      SDK action name (e.g., {@code "get_product_detail"}, {@code "sign_web"})
     * @param jsonPayload Request JSON string (null or blank defaults to {@code "{}"})
     * @return Raw UTF-8 JSON envelope ({@code {"ok":true,"code":0,"data":...}})
     */
    public String invoke(String action, String jsonPayload) {
        ensureOpen();
        if (action == null || action.trim().isEmpty()) {
            throw new IllegalArgumentException("SDK action cannot be null or empty.");
        }
        String payload = (jsonPayload == null || jsonPayload.trim().isEmpty()) ? "{}" : jsonPayload;
        Pointer ptr = this.nativeLib.MinSign_Invoke(toUtf8CString(action.trim()), toUtf8CString(payload));
        return consumePointer(ptr);
    }

    // =========================================================================
    // GROUP 1: CORE, AUTH, DEVICE VAULT & DUAL SIGNING (9 Methods)
    // =========================================================================

    /** Get native SDK version, supported regions, and TLS engine info ({@code MinSign_Version}). */
    public String version() {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_Version());
    }

    /** Validate the configured X-API-Key and inspect quota/tier ({@code MinSign_CheckApiKey}). */
    public String checkApiKey() {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_CheckApiKey());
    }

    /** Bind and persist a real Android device fingerprint to an account in the local vault. */
    public String bindAccountDevice(String jsonPayload) {
        return invoke("bind_account_device", jsonPayload);
    }

    /** List all device fingerprints stored in the local vault ({@code MinSign_ListLocalDevices}). */
    public String listLocalDevices() {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_ListLocalDevices());
    }

    /** Remove a bound device entry from the local vault by account key / ID. */
    public String removeLocalDevice(String accountKey) {
        String key = accountKey == null ? "" : accountKey;
        return invoke("remove_local_device", "{\"accountKey\":\"" + escapeJson(key) + "\"}");
    }

    /** Generate raw Shopee security signature headers (App Mobile or Web mode via {@code clientType}). */
    public String signRaw(String jsonPayload) {
        return invoke("sign_raw", jsonPayload);
    }

    /** [v2.0.0] Generate Chrome 131 Web security signature headers + patched cookies ({@code MinSign_SignWeb}). */
    public String signWeb(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_SignWeb(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** Fetch a fresh anti-fraud risk token / x-sap-ri ({@code MinSign_GetRiskToken}). */
    public String getRiskToken() {
        return getRiskToken("{}");
    }

    /** Fetch a fresh anti-fraud risk token / x-sap-ri ({@code MinSign_GetRiskToken}). */
    public String getRiskToken(String jsonPayload) {
        ensureOpen();
        String payload = (jsonPayload == null || jsonPayload.trim().isEmpty()) ? "{}" : jsonPayload;
        return consumePointer(this.nativeLib.MinSign_GetRiskToken(toUtf8CString(payload)));
    }

    /** Universal signed HTTP gateway supporting arbitrary Shopee endpoints (App or Web mode). */
    public String executeSignedRequest(String jsonPayload) {
        return invoke("execute_signed_request", jsonPayload);
    }

    // =========================================================================
    // GROUP 2: COMMERCE, PRODUCT, SHOP, SEARCH & DISCOVERY (16 Methods)
    // =========================================================================

    /** [v2.0.0] Parse or resolve any Shopee URL (product, shop, video, live, shortlink) into canonical IDs. */
    public String resolveShopeeUrl(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_ResolveShopeeUrl(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** Fetch complete product detail (title, price, stock, variants/models, ratings, images). */
    public String getProductDetail(String jsonPayload) {
        return invoke("get_product_detail", jsonPayload);
    }

    /** [v2.0.0] Fetch multiple product details concurrently with proxy/cookie rotation. */
    public String batchGetProductDetails(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_BatchGetProductDetails(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Fetch normalized product buyer reviews, star summary, and media URLs. */
    public String getProductRatings(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetProductRatings(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** Fetch shop profile overview (followers, rating, verification, item count). */
    public String getShopOverview(String jsonPayload) {
        return invoke("get_shop_overview", jsonPayload);
    }

    /** List products in a shop with sorting and pagination. */
    public String getShopProducts(String jsonPayload) {
        return invoke("get_shop_products", jsonPayload);
    }

    /** Fetch newest products published by a shop (supports {@code sinceItemId} polling). */
    public String getShopNewestProducts(String jsonPayload) {
        return invoke("get_shop_newest_products", jsonPayload);
    }

    /** Fetch custom category list of a shop. */
    public String getShopCategories(String jsonPayload) {
        return invoke("get_shop_categories", jsonPayload);
    }

    /** List active vouchers offered by a shop. */
    public String getShopVouchers(String jsonPayload) {
        return invoke("get_shop_vouchers", jsonPayload);
    }

    /** Search Shopee products by keyword across any supported region. */
    public String searchProducts(String jsonPayload) {
        return invoke("search_products", jsonPayload);
    }

    /** Search visually similar Shopee products using an image path, URL, or base64 payload. */
    public String searchProductsByImage(String jsonPayload) {
        return invoke("search_products_by_image", jsonPayload);
    }

    /** Detect object bounding boxes in an image for targeted visual search. */
    public String getImageBoundingBox(String jsonPayload) {
        return invoke("get_image_bounding_box", jsonPayload);
    }

    /** Retrieve the full Shopee category tree for the default region. */
    public String getCategoryTree() {
        return getCategoryTree("{}");
    }

    /** Retrieve the full Shopee category tree for a region. */
    public String getCategoryTree(String jsonPayload) {
        return invoke("get_category_tree", jsonPayload);
    }

    /** [v2.0.0] Retrieve active Flash Sale sessions and discounted items (default region). */
    public String getFlashSaleItems() {
        return getFlashSaleItems("{}");
    }

    /** [v2.0.0] Retrieve active Flash Sale sessions and discounted item listings. */
    public String getFlashSaleItems(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetFlashSaleItems(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Retrieve recommended / daily discover products (default region). */
    public String getRecommendProducts() {
        return getRecommendProducts("{}");
    }

    /** [v2.0.0] Retrieve recommended / similar products (item detail or daily discover). */
    public String getRecommendProducts(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetRecommendProducts(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Retrieve real-time autocomplete keyword suggestions from Shopee Search. */
    public String getSearchSuggestions(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetSearchSuggestions(toUtf8CString(normalizeJson(jsonPayload))));
    }

    // =========================================================================
    // GROUP 3: ACCOUNT, CART & VOUCHER WALLET (3 Methods)
    // =========================================================================

    /** [v2.0.0] Verify account cookie liveness and fetch account profile metadata. */
    public String getAccountProfile(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetAccountProfile(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Fetch shopping cart summary grouped by shop with item count and subtotal. */
    public String getCartSummary(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetCartSummary(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Save/claim a shop voucher into the account voucher wallet (with risk headers). */
    public String claimShopVoucher(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_ClaimShopVoucher(toUtf8CString(normalizeJson(jsonPayload))));
    }

    // =========================================================================
    // GROUP 4: VIDEO UPLOAD, AFFILIATE & MP4 STUDIO (8 Methods)
    // =========================================================================

    /** Upload a video directly to Shopee Video with optional affiliate product tags. */
    public String uploadShopeeVideo(String jsonPayload) {
        return invoke("upload_shopee_video", jsonPayload);
    }

    /** Precheck an account's eligibility and upload session before uploading a Shopee Video. */
    public String precheckVideoUpload(String jsonPayload) {
        return invoke("precheck_video_upload", jsonPayload);
    }

    /** Query affiliate-eligible products to attach to Shopee Video / Affiliate campaigns. */
    public String getAffiliateProducts(String jsonPayload) {
        return invoke("get_affiliate_products", jsonPayload);
    }

    /** Convert a Shopee product/shop URL into a tracked affiliate shortlink. */
    public String convertAffiliateLink(String jsonPayload) {
        return invoke("convert_affiliate_link", jsonPayload);
    }

    /** Batch-convert multiple Shopee URLs into tracked affiliate shortlinks. */
    public String batchConvertAffiliateLinks(String jsonPayload) {
        return invoke("batch_convert_affiliate_links", jsonPayload);
    }

    /** Mutate MP4 container metadata/fingerprint locally to generate a unique MD5 hash. */
    public String mutateMp4Fingerprint(String jsonPayload) {
        return invoke("mutate_mp4_fingerprint", jsonPayload);
    }

    /** [v2.0.0] Browse Shopee Affiliate portal offer listings with commission rates via Web Signer. */
    public String getAffiliateOfferList(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetAffiliateOfferList(toUtf8CString(normalizeJson(jsonPayload))));
    }

    /** [v2.0.0] Query Shopee Affiliate commission and conversion report records via Web Signer. */
    public String getAffiliateCommissionReport(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetAffiliateCommissionReport(toUtf8CString(normalizeJson(jsonPayload))));
    }

    // =========================================================================
    // GROUP 5: SHOPEE VIDEO VIEWER & CHANNEL DISCOVERY (5 Methods)
    // =========================================================================

    /** Send a single signed Shopee Video view event. */
    public String buffVideoView(String jsonPayload) {
        return invoke("buff_video_view", jsonPayload);
    }

    /** Run a multi-worker batch of Shopee Video view events. */
    public String buffVideoBatch(String jsonPayload) {
        return invoke("buff_video_batch", jsonPayload);
    }

    /** Fetch Shopee Video post metadata, playback URLs, and attached product tags. */
    public String getVideoDetail(String jsonPayload) {
        return invoke("get_video_detail", jsonPayload);
    }

    /** Fetch the Shopee Video timeline of a specific shop or creator. */
    public String getShopVideos(String jsonPayload) {
        return invoke("get_shop_videos", jsonPayload);
    }

    /** Discover Shopee Videos by creator channel or hashtag. */
    public String getChannelAndHashtagVideos(String jsonPayload) {
        return invoke("get_channel_and_hashtag_videos", jsonPayload);
    }

    // =========================================================================
    // GROUP 6: SHOPEE LIVE VIEWER & LIVE BAG COMMERCE (4 Methods)
    // =========================================================================

    /** Fetch live session details (host info, viewer count, stream URLs, status). */
    public String getLiveSessionDetail(String jsonPayload) {
        return invoke("get_live_session_detail", jsonPayload);
    }

    /** Join and maintain a single signed Shopee Live viewer session. */
    public String buffLiveView(String jsonPayload) {
        return invoke("buff_live_view", jsonPayload);
    }

    /** Run a concurrent batch of Shopee Live viewer sessions. */
    public String buffLiveBatch(String jsonPayload) {
        return invoke("buff_live_batch", jsonPayload);
    }

    /** [v2.0.0] Extract products pinned in a Shopee Live orange shopping bag. */
    public String getLiveBagItems(String jsonPayload) {
        ensureOpen();
        return consumePointer(this.nativeLib.MinSign_GetLiveBagItems(toUtf8CString(normalizeJson(jsonPayload))));
    }

    @Override
    public void close() {
        this.closed = true;
    }

    // =========================================================================
    // INTERNAL MEMORY-SAFE JNA / UTF-8 HELPERS
    // =========================================================================

    private static String normalizeJson(String jsonPayload) {
        return (jsonPayload == null || jsonPayload.trim().isEmpty()) ? "{}" : jsonPayload;
    }

    private void ensureOpen() {
        if (this.closed) {
            throw new IllegalStateException("MinSignSdk client has been closed.");
        }
    }

    private String consumePointer(Pointer ptr) {
        if (ptr == null) {
            throw new MinSignException("MinSign native library returned a NULL pointer.");
        }
        try {
            return ptr.getString(0, "UTF-8");
        } finally {
            this.nativeLib.MinSign_Free(ptr);
        }
    }

    private static byte[] toUtf8CString(String s) {
        byte[] utf8 = (s == null ? "" : s).getBytes(StandardCharsets.UTF_8);
        byte[] nullTerminated = new byte[utf8.length + 1];
        System.arraycopy(utf8, 0, nullTerminated, 0, utf8.length);
        nullTerminated[utf8.length] = 0;
        return nullTerminated;
    }

    private static String escapeJson(String s) {
        StringBuilder sb = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            switch (ch) {
                case '"':
                    sb.append("\\\"");
                    break;
                case '\\':
                    sb.append("\\\\");
                    break;
                case '\b':
                    sb.append("\\b");
                    break;
                case '\f':
                    sb.append("\\f");
                    break;
                case '\n':
                    sb.append("\\n");
                    break;
                case '\r':
                    sb.append("\\r");
                    break;
                case '\t':
                    sb.append("\\t");
                    break;
                default:
                    if (ch < 0x20) {
                        sb.append(String.format("\\u%04x", (int) ch));
                    } else {
                        sb.append(ch);
                    }
                    break;
            }
        }
        return sb.toString();
    }
}
