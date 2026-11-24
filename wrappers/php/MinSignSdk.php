<?php
declare(strict_types=1);

namespace MinSign;

use FFI;
use FFI\CData;
use InvalidArgumentException;
use JsonException;
use RuntimeException;

/**
 * Official PHP 8.1+ FFI Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll / libminsign_sdk.so).
 *
 * Requirements:
 * - PHP 8.1+ (64-bit) with the built-in FFI extension enabled (`extension=ffi`, `ffi.enable=true`).
 * - No external Composer packages required.
 * - Every heap-allocated C-string returned by the native library is deterministically released
 *   via `MinSign_Free(ptr)` inside a `try / finally` block to guarantee zero memory leaks.
 */
final class MinSignClient
{
    private const DEFAULT_SIGNER_URL = 'https://vip-sign.minmintool.site';
    private const DEFAULT_VAULT_PATH = './minsign_data/devices_vault.json';

    private const CDEF = <<<'C'
        char* MinSign_Version(void);
        char* MinSign_Init(const char* configJson);
        char* MinSign_CheckApiKey(void);
        char* MinSign_ListLocalDevices(void);
        char* MinSign_GetRiskToken(const char* reqJson);
        char* MinSign_SignWeb(const char* reqJson);
        char* MinSign_ResolveShopeeUrl(const char* reqJson);
        char* MinSign_BatchGetProductDetails(const char* reqJson);
        char* MinSign_GetProductRatings(const char* reqJson);
        char* MinSign_GetFlashSaleItems(const char* reqJson);
        char* MinSign_GetRecommendProducts(const char* reqJson);
        char* MinSign_GetSearchSuggestions(const char* reqJson);
        char* MinSign_GetAccountProfile(const char* reqJson);
        char* MinSign_GetCartSummary(const char* reqJson);
        char* MinSign_ClaimShopVoucher(const char* reqJson);
        char* MinSign_GetAffiliateOfferList(const char* reqJson);
        char* MinSign_GetAffiliateCommissionReport(const char* reqJson);
        char* MinSign_GetLiveBagItems(const char* reqJson);
        char* MinSign_Invoke(const char* action, const char* reqJson);
        void  MinSign_Free(char* ptr);
    C;

    private FFI $ffi;
    private string $dllPath;

    /** @var array<string, mixed> */
    private array $initInfo;

    /**
     * Initialize the MinSign Native SDK client via PHP FFI.
     *
     * @param string      $apiKey         X-API-Key obtained from https://vip-sign.minmintool.site
     * @param string|null $dllPath        Optional explicit path to minsign_sdk.dll / libminsign_sdk.so
     * @param string      $signerUrl      Cloud signer base URL
     * @param string      $vaultFilePath  Local device vault JSON path
     * @param string      $vaultSecret    Optional encryption passphrase for the local device vault
     * @param string      $defaultCountry Default Shopee region (VN, ID, TH, MY, PH, SG, TW, BR)
     * @param int         $timeoutMs      HTTP request timeout in milliseconds
     *
     * @throws InvalidArgumentException If apiKey is empty
     * @throws RuntimeException         If FFI is unavailable, DLL cannot be loaded, or MinSign_Init fails
     */
    public function __construct(
        string $apiKey,
        ?string $dllPath = null,
        string $signerUrl = self::DEFAULT_SIGNER_URL,
        string $vaultFilePath = self::DEFAULT_VAULT_PATH,
        string $vaultSecret = '',
        string $defaultCountry = 'VN',
        int $timeoutMs = 25000,
    ) {
        if (!extension_loaded('ffi')) {
            throw new RuntimeException(
                'PHP FFI extension is not loaded. Enable extension=ffi and ffi.enable=true in php.ini.'
            );
        }

        if (PHP_INT_SIZE < 8) {
            throw new RuntimeException(
                'MinSign Native SDK requires 64-bit PHP (x64) to load minsign_sdk.dll.'
            );
        }

        $trimmedKey = trim($apiKey);
        if ($trimmedKey === '') {
            throw new InvalidArgumentException(
                'A non-empty X-API-Key ($apiKey) is required to initialize MinSignClient.'
            );
        }

        $this->dllPath = self::resolveDllPath($dllPath);
        self::pinWindowsNativeDll($this->dllPath);
        try {
            $this->ffi = FFI::cdef(self::CDEF, $this->dllPath);
        } catch (\Throwable $e) {
            throw new RuntimeException(
                sprintf('Failed to load MinSign native library at "%s": %s', $this->dllPath, $e->getMessage()),
                0,
                $e
            );
        }

        $configPayload = self::encodeJson([
            'apiKey'         => $trimmedKey,
            'signerUrl'      => $signerUrl,
            'vaultFilePath'  => $vaultFilePath,
            'vaultSecret'    => $vaultSecret,
            'defaultCountry' => $defaultCountry,
            'timeoutMs'      => $timeoutMs,
        ]);

        $this->initInfo = $this->consumePtr($this->ffi->MinSign_Init($configPayload), true);
    }

    /**
     * Resolve the native shared library path automatically across common repository layouts.
     *
     * @throws RuntimeException If the shared library cannot be found
     */
    public static function resolveDllPath(?string $customPath = null): string
    {
        if ($customPath !== null && trim($customPath) !== '') {
            $real = realpath($customPath);
            if ($real !== false && is_file($real)) {
                return $real;
            }
            if (is_file($customPath)) {
                return $customPath;
            }
            throw new RuntimeException(sprintf('MinSign native library not found at custom path: %s', $customPath));
        }

        $libName = PHP_OS_FAMILY === 'Windows' ? 'minsign_sdk.dll' : 'libminsign_sdk.so';
        $cwd = getcwd() ?: '.';
        $dir = __DIR__;

        $candidates = [
            $cwd . DIRECTORY_SEPARATOR . $libName,
            $cwd . DIRECTORY_SEPARATOR . 'bin' . DIRECTORY_SEPARATOR . 'win-x64' . DIRECTORY_SEPARATOR . $libName,
            $dir . DIRECTORY_SEPARATOR . $libName,
            $dir . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'bin' . DIRECTORY_SEPARATOR . 'win-x64' . DIRECTORY_SEPARATOR . $libName,
            $dir . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'dist' . DIRECTORY_SEPARATOR . 'win-x64' . DIRECTORY_SEPARATOR . $libName,
            $dir . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'bin' . DIRECTORY_SEPARATOR . $libName,
        ];

        foreach ($candidates as $candidate) {
            $real = realpath($candidate);
            if ($real !== false && is_file($real)) {
                return $real;
            }
        }

        throw new RuntimeException(
            sprintf(
                'Could not locate %s. Place it in ./bin/win-x64/ or pass $dllPath explicitly to MinSignClient.',
                $libName
            )
        );
    }

    /**
     * Return initialization metadata returned by MinSign_Init.
     *
     * @return array<string, mixed>
     */
    public function getInitInfo(): array
    {
        return $this->initInfo;
    }

    /**
     * Return the resolved path of the loaded native shared library.
     */
    public function getDllPath(): string
    {
        return $this->dllPath;
    }

    /**
     * Universal dynamic dispatcher calling `MinSign_Invoke(action, reqJson)`.
     * Returns the unwrapped `data` array and throws RuntimeException when `ok === false`.
     *
     * @param string               $action  SDK action name (e.g. "get_product_detail", "sign_web")
     * @param array<string, mixed> $payload Request parameters
     *
     * @return array<string, mixed>
     * @throws RuntimeException On native call failure, invalid JSON, or SDK error response
     */
    public function invoke(string $action, array $payload = []): array
    {
        $act = trim($action);
        if ($act === '') {
            throw new InvalidArgumentException('SDK action name cannot be empty.');
        }

        $jsonReq = self::encodeJson(self::normalizePayload($payload));
        $ptr = $this->ffi->MinSign_Invoke($act, $jsonReq);
        return $this->consumePtr($ptr, true);
    }

    /**
     * Universal dynamic dispatcher returning the full SDK JSON envelope (`ok`, `code`, `data`, `error`)
     * without throwing on `ok === false`.
     *
     * @param string                      $action  SDK action name
     * @param array<string, mixed>|string $payload Request array or raw JSON string
     *
     * @return array<string, mixed>
     * @throws RuntimeException On NULL pointer or malformed JSON from the DLL
     */
    public function invokeRaw(string $action, array|string $payload = []): array
    {
        $act = trim($action);
        if ($act === '') {
            throw new InvalidArgumentException('SDK action name cannot be empty.');
        }

        $jsonReq = is_string($payload)
            ? ($payload !== '' ? $payload : '{}')
            : self::encodeJson(self::normalizePayload($payload));

        $ptr = $this->ffi->MinSign_Invoke($act, $jsonReq);
        return $this->consumePtr($ptr, false);
    }

    // =========================================================================
    // GROUP 1: CORE, AUTH, DEVICE VAULT & DUAL SIGNING (9 Methods)
    // =========================================================================

    /**
     * Get native SDK version, supported regions, and TLS engine info (`MinSign_Version`).
     *
     * @return array<string, mixed>
     */
    public function version(): array
    {
        return $this->consumePtr($this->ffi->MinSign_Version(), true);
    }

    /**
     * Validate the configured X-API-Key and inspect quota/tier (`MinSign_CheckApiKey`).
     *
     * @return array<string, mixed>
     */
    public function checkApiKey(): array
    {
        return $this->consumePtr($this->ffi->MinSign_CheckApiKey(), true);
    }

    /**
     * Bind and persist a real Android device fingerprint to an account in the local vault.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function bindAccountDevice(array $request): array
    {
        return $this->invoke('bind_account_device', $request);
    }

    /**
     * List all device fingerprints stored in the local vault (`MinSign_ListLocalDevices`).
     *
     * @return array<string, mixed>
     */
    public function listLocalDevices(): array
    {
        return $this->consumePtr($this->ffi->MinSign_ListLocalDevices(), true);
    }

    /**
     * Remove a bound device entry from the local vault by account key / ID.
     *
     * @return array<string, mixed>
     */
    public function removeLocalDevice(string $accountKey): array
    {
        return $this->invoke('remove_local_device', ['accountKey' => $accountKey]);
    }

    /**
     * Generate raw Shopee security signature headers (App Mobile or Web mode via `clientType`).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function signRaw(array $request): array
    {
        return $this->invoke('sign_raw', $request);
    }

    /**
     * [v2.0.0] Generate Chrome 131 Web security signature headers + patched cookies (`MinSign_SignWeb` / `sign_web`).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function signWeb(array $request): array
    {
        return $this->callDirectJson('MinSign_SignWeb', $request);
    }

    /**
     * Fetch a fresh anti-fraud risk token / x-sap-ri (`MinSign_GetRiskToken`).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getRiskToken(array $request = []): array
    {
        $jsonReq = self::encodeJson(self::normalizePayload($request));
        return $this->consumePtr($this->ffi->MinSign_GetRiskToken($jsonReq), true);
    }

    /**
     * Universal signed HTTP gateway supporting arbitrary Shopee endpoints (App or Web mode).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function executeSignedRequest(array $request): array
    {
        return $this->invoke('execute_signed_request', $request);
    }

    // =========================================================================
    // GROUP 2: COMMERCE, PRODUCT, SHOP, SEARCH & DISCOVERY (16 Methods)
    // =========================================================================

    /**
     * [v2.0.0] Parse or resolve any Shopee URL (product, shop, video, live, shortlink) into canonical IDs.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function resolveShopeeUrl(array $request): array
    {
        return $this->callDirectJson('MinSign_ResolveShopeeUrl', $request);
    }

    /**
     * Fetch complete product detail (title, price, stock, variants/models, ratings, images).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getProductDetail(array $request): array
    {
        return $this->invoke('get_product_detail', $request);
    }

    /**
     * [v2.0.0] Fetch multiple product details concurrently with proxy/cookie rotation.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function batchGetProductDetails(array $request): array
    {
        return $this->callDirectJson('MinSign_BatchGetProductDetails', $request);
    }

    /**
     * [v2.0.0] Fetch normalized product buyer reviews, star summary, and review media URLs.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getProductRatings(array $request): array
    {
        return $this->callDirectJson('MinSign_GetProductRatings', $request);
    }

    /**
     * Fetch shop profile overview (followers, rating, verification, item count).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopOverview(array $request): array
    {
        return $this->invoke('get_shop_overview', $request);
    }

    /**
     * List products in a shop with sorting and pagination.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopProducts(array $request): array
    {
        return $this->invoke('get_shop_products', $request);
    }

    /**
     * Fetch newest products published by a shop (supports `sinceItemId` incremental polling).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopNewestProducts(array $request): array
    {
        return $this->invoke('get_shop_newest_products', $request);
    }

    /**
     * Fetch custom category list of a shop.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopCategories(array $request): array
    {
        return $this->invoke('get_shop_categories', $request);
    }

    /**
     * List active vouchers offered by a shop.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopVouchers(array $request): array
    {
        return $this->invoke('get_shop_vouchers', $request);
    }

    /**
     * Search Shopee products by keyword across any supported region.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function searchProducts(array $request): array
    {
        return $this->invoke('search_products', $request);
    }

    /**
     * Search visually similar Shopee products using an image file path, URL, or base64 payload.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function searchProductsByImage(array $request): array
    {
        return $this->invoke('search_products_by_image', $request);
    }

    /**
     * Detect object bounding boxes in an image for targeted visual search.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getImageBoundingBox(array $request): array
    {
        return $this->invoke('get_image_bounding_box', $request);
    }

    /**
     * Retrieve the full Shopee category tree for a region.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getCategoryTree(array $request = []): array
    {
        return $this->invoke('get_category_tree', $request);
    }

    /**
     * [v2.0.0] Retrieve active Flash Sale sessions and discounted item listings.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getFlashSaleItems(array $request = []): array
    {
        return $this->callDirectJson('MinSign_GetFlashSaleItems', $request);
    }

    /**
     * [v2.0.0] Retrieve recommended / similar products (item detail or daily discover).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getRecommendProducts(array $request = []): array
    {
        return $this->callDirectJson('MinSign_GetRecommendProducts', $request);
    }

    /**
     * [v2.0.0] Retrieve real-time autocomplete keyword suggestions from Shopee Search.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getSearchSuggestions(array $request): array
    {
        return $this->callDirectJson('MinSign_GetSearchSuggestions', $request);
    }

    // =========================================================================
    // GROUP 3: ACCOUNT, CART & VOUCHER WALLET (3 Methods)
    // =========================================================================

    /**
     * [v2.0.0] Verify account cookie liveness and fetch account profile metadata.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getAccountProfile(array $request): array
    {
        return $this->callDirectJson('MinSign_GetAccountProfile', $request);
    }

    /**
     * [v2.0.0] Fetch shopping cart summary grouped by shop with item count and subtotal.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getCartSummary(array $request): array
    {
        return $this->callDirectJson('MinSign_GetCartSummary', $request);
    }

    /**
     * [v2.0.0] Save/claim a shop voucher into the account voucher wallet (with risk headers).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function claimShopVoucher(array $request): array
    {
        return $this->callDirectJson('MinSign_ClaimShopVoucher', $request);
    }

    // =========================================================================
    // GROUP 4: VIDEO UPLOAD, AFFILIATE & MP4 STUDIO (8 Methods)
    // =========================================================================

    /**
     * Upload a video directly to Shopee Video with optional affiliate product tags.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function uploadShopeeVideo(array $request): array
    {
        return $this->invoke('upload_shopee_video', $request);
    }

    /**
     * Precheck an account's eligibility and upload session before uploading a Shopee Video.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function precheckVideoUpload(array $request): array
    {
        return $this->invoke('precheck_video_upload', $request);
    }

    /**
     * Query affiliate-eligible products to attach to Shopee Video / Affiliate campaigns.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getAffiliateProducts(array $request): array
    {
        return $this->invoke('get_affiliate_products', $request);
    }

    /**
     * Convert a Shopee product/shop URL into a tracked affiliate shortlink.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function convertAffiliateLink(array $request): array
    {
        return $this->invoke('convert_affiliate_link', $request);
    }

    /**
     * Batch-convert multiple Shopee URLs into tracked affiliate shortlinks.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function batchConvertAffiliateLinks(array $request): array
    {
        return $this->invoke('batch_convert_affiliate_links', $request);
    }

    /**
     * Mutate MP4 container metadata/fingerprint locally to generate a unique MD5 hash.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function mutateMp4Fingerprint(array $request): array
    {
        return $this->invoke('mutate_mp4_fingerprint', $request);
    }

    /**
     * [v2.0.0] Browse Shopee Affiliate portal offer listings with commission rates via Web Signer.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getAffiliateOfferList(array $request): array
    {
        return $this->callDirectJson('MinSign_GetAffiliateOfferList', $request);
    }

    /**
     * [v2.0.0] Query Shopee Affiliate commission and conversion report records via Web Signer.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getAffiliateCommissionReport(array $request): array
    {
        return $this->callDirectJson('MinSign_GetAffiliateCommissionReport', $request);
    }

    // =========================================================================
    // GROUP 5: SHOPEE VIDEO VIEWER & CHANNEL DISCOVERY (5 Methods)
    // =========================================================================

    /**
     * Send a single signed Shopee Video view event.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function buffVideoView(array $request): array
    {
        return $this->invoke('buff_video_view', $request);
    }

    /**
     * Run a multi-worker batch of Shopee Video view events.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function buffVideoBatch(array $request): array
    {
        return $this->invoke('buff_video_batch', $request);
    }

    /**
     * Fetch Shopee Video post metadata, playback URLs, and attached product tags.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getVideoDetail(array $request): array
    {
        return $this->invoke('get_video_detail', $request);
    }

    /**
     * Fetch the Shopee Video timeline of a specific shop or creator.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getShopVideos(array $request): array
    {
        return $this->invoke('get_shop_videos', $request);
    }

    /**
     * Discover Shopee Videos by creator channel or hashtag.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getChannelAndHashtagVideos(array $request): array
    {
        return $this->invoke('get_channel_and_hashtag_videos', $request);
    }

    // =========================================================================
    // GROUP 6: SHOPEE LIVE VIEWER & LIVE BAG COMMERCE (4 Methods)
    // =========================================================================

    /**
     * Fetch live session details (host info, viewer count, stream URLs, status).
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getLiveSessionDetail(array $request): array
    {
        return $this->invoke('get_live_session_detail', $request);
    }

    /**
     * Join and maintain a single signed Shopee Live viewer session.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function buffLiveView(array $request): array
    {
        return $this->invoke('buff_live_view', $request);
    }

    /**
     * Run a concurrent batch of Shopee Live viewer sessions.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function buffLiveBatch(array $request): array
    {
        return $this->invoke('buff_live_batch', $request);
    }

    /**
     * [v2.0.0] Extract products pinned in a Shopee Live orange shopping bag.
     *
     * @param array<string, mixed> $request
     * @return array<string, mixed>
     */
    public function getLiveBagItems(array $request): array
    {
        return $this->callDirectJson('MinSign_GetLiveBagItems', $request);
    }

    // =========================================================================
    // INTERNAL MEMORY-SAFE C-ABI HELPERS
    // =========================================================================

    /**
     * Invoke a direct single-JSON-argument C-ABI symbol (e.g. `MinSign_SignWeb`) and free its returned pointer.
     *
     * @param array<string, mixed> $payload
     * @return array<string, mixed>
     */
    private function callDirectJson(string $symbol, array $payload): array
    {
        $jsonReq = self::encodeJson(self::normalizePayload($payload));
        $ptr = $this->ffi->{$symbol}($jsonReq);
        return $this->consumePtr($ptr, true);
    }

    /**
     * Read UTF-8 JSON from a native C-string pointer and ALWAYS release it via `MinSign_Free`.
     *
     * @return array<string, mixed>
     * @throws RuntimeException
     */
    private function consumePtr(?CData $ptr, bool $unwrapData): array
    {
        if ($ptr === null || FFI::isNull($ptr)) {
            throw new RuntimeException('MinSign native library returned a NULL pointer.');
        }

        try {
            $rawJson = FFI::string($ptr);
        } finally {
            $this->ffi->MinSign_Free($ptr);
        }

        try {
            $decoded = json_decode($rawJson, true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $e) {
            throw new RuntimeException(
                sprintf('Failed to decode JSON response from MinSign SDK: %s', $e->getMessage()),
                0,
                $e
            );
        }

        if (!is_array($decoded)) {
            throw new RuntimeException('Unexpected non-object JSON payload returned by MinSign SDK.');
        }

        if (!$unwrapData) {
            return $decoded;
        }

        $ok = (bool) ($decoded['ok'] ?? false);
        if (!$ok) {
            $code = (int) ($decoded['code'] ?? -1);
            $errorMsg = isset($decoded['error']) && is_string($decoded['error']) && $decoded['error'] !== ''
                ? $decoded['error']
                : $rawJson;
            throw new RuntimeException(sprintf('MinSign SDK Error (code %d): %s', $code, $errorMsg), $code);
        }

        $data = $decoded['data'] ?? [];
        if (is_array($data)) {
            return $data;
        }

        return ['value' => $data];
    }

    /**
     * Normalize nested cookie fields (arrays -> JSON string) before encoding to JSON.
     *
     * @param array<string, mixed> $payload
     * @return array<string, mixed>
     */
    private static function normalizePayload(array $payload): array
    {
        if (isset($payload['cookie']) && is_array($payload['cookie'])) {
            $payload['cookie'] = self::encodeJson($payload['cookie']);
        }
        if (isset($payload['cookies']) && is_array($payload['cookies'])) {
            $normalized = [];
            foreach ($payload['cookies'] as $entry) {
                $normalized[] = is_array($entry) ? self::encodeJson($entry) : (string) $entry;
            }
            $payload['cookies'] = $normalized;
        }
        return $payload;
    }

    /**
     * Pin Go c-shared DLL in the host process on Windows so PHP's FFI shutdown does not
     * unload the Go runtime prematurely via FreeLibrary.
     */
    private static function pinWindowsNativeDll(string $dllPath): void
    {
        if (PHP_OS_FAMILY !== 'Windows') {
            return;
        }
        static $pinned = [];
        if (isset($pinned[$dllPath])) {
            return;
        }
        try {
            $k32 = FFI::cdef('void* LoadLibraryA(const char* lpLibFileName);', 'kernel32.dll');
            $k32->LoadLibraryA($dllPath);
            $pinned[$dllPath] = true;
        } catch (\Throwable) {
            // Non-fatal fallback: continue with standard FFI loading.
        }
    }

    /**
     * Encode an array into a UTF-8 JSON object string (ensuring empty arrays serialize as `{}`).
     *
     * @param array<mixed> $data
     * @throws RuntimeException
     */
    private static function encodeJson(array $data): string
    {
        if ($data === []) {
            return '{}';
        }
        try {
            return json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        } catch (JsonException $e) {
            throw new RuntimeException(
                sprintf('Failed to encode request payload to JSON: %s', $e->getMessage()),
                0,
                $e
            );
        }
    }
}

if (!class_exists(__NAMESPACE__ . '\\MinSignSdk', false)) {
    class_alias(MinSignClient::class, __NAMESPACE__ . '\\MinSignSdk');
}
