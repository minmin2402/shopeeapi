<?php
declare(strict_types=1);

/**
 * Quickstart PHP 8.1+ (FFI) — ShopeeAPI MinSign Native Universal SDK v2.0.0
 *
 * Requirements:
 *   - PHP 8.1+ (64-bit / x64) with FFI enabled:
 *       php -d extension=ffi -d ffi.enable=true examples/quickstart_php.php
 *   - Obtain your X-API-Key at: https://vip-sign.minmintool.site
 */

require_once __DIR__ . '/../wrappers/php/MinSignSdk.php';

use MinSign\MinSignClient;

$apiKey = getenv('MINSIGN_API_KEY') ?: 'YOUR_X_API_KEY_HERE';
if ($apiKey === 'YOUR_X_API_KEY_HERE') {
    echo "[!] Set MINSIGN_API_KEY or replace YOUR_X_API_KEY_HERE with your key from https://vip-sign.minmintool.site\n";
    echo "    Example (PowerShell): \$env:MINSIGN_API_KEY=\"shopee-...\"; php -d extension=ffi -d ffi.enable=true examples/quickstart_php.php\n";
    exit(0);
}

$sdk = new MinSignClient(
    apiKey: $apiKey,
    signerUrl: 'https://vip-sign.minmintool.site',
    vaultFilePath: './minsign_data/devices_vault.json',
    defaultCountry: 'VN',
);

// 1. Check SDK version & X-API-Key quota
$version = $sdk->version();
echo "1. SDK Version   : " . ($version['version'] ?? 'unknown') . " (" . ($version['name'] ?? '') . ")\n";

$keyInfo = $sdk->checkApiKey();
echo "2. API Key Status: " . json_encode($keyInfo, JSON_UNESCAPED_UNICODE) . "\n";

// 2. [v2.0.0] Resolve any Shopee product/shop/video/live URL into canonical IDs
$sampleUrl = 'https://shopee.vn/product/1023922469/25294038727';
$resolved = $sdk->resolveShopeeUrl([
    'url'            => $sampleUrl,
    'country'        => 'VN',
    'followRedirect' => true,
]);
echo sprintf(
    "\n3. Resolved URL  : type=%s | shopId=%s | itemId=%s | canonical=%s\n",
    (string) ($resolved['urlType'] ?? ''),
    (string) ($resolved['shopId'] ?? ''),
    (string) ($resolved['itemId'] ?? ''),
    (string) ($resolved['canonicalProductUrl'] ?? '')
);

// 3. Fetch complete product detail (no Shopee cookie required)
$detail = $sdk->getProductDetail([
    'productUrl' => $sampleUrl,
    'country'    => 'VN',
]);
$product = $detail['product'] ?? [];
echo "\n4. Product Detail:\n";
echo "   - Name        : " . ($product['name'] ?? 'N/A') . "\n";
echo "   - Price (VND) : " . number_format((int) ($product['priceVnd'] ?? 0)) . "\n";
echo "   - Sold        : " . ($product['historicalSold'] ?? 0) . "\n";
echo "   - Rating      : " . ($product['ratingStar'] ?? 0) . "\n";

// 4. [v2.0.0] Fetch buyer ratings & autocomplete search suggestions
$ratings = $sdk->getProductRatings([
    'productUrl' => $sampleUrl,
    'limit'      => 5,
    'offset'     => 0,
    'country'    => 'VN',
]);
echo "\n5. Product Ratings fetched: " . count($ratings['ratings'] ?? []) . " items\n";

$suggestions = $sdk->getSearchSuggestions([
    'keyword' => 'iphone 16',
    'limit'   => 5,
    'country' => 'VN',
]);
echo "6. Search Suggestions     : " . json_encode($suggestions['suggestions'] ?? [], JSON_UNESCAPED_UNICODE) . "\n";

// 5. [v2.0.0] Concurrent batch product detail fetch
$batch = $sdk->batchGetProductDetails([
    'productUrls' => [$sampleUrl],
    'concurrency' => 4,
    'country'     => 'VN',
]);
echo sprintf(
    "7. Batch Product Fetch    : total=%d | succeeded=%d | failed=%d | elapsedMs=%d\n",
    (int) ($batch['total'] ?? 0),
    (int) ($batch['succeeded'] ?? 0),
    (int) ($batch['failed'] ?? 0),
    (int) ($batch['elapsedMs'] ?? 0)
);

// 6. [v2.0.0] Optional: Chrome 131 Web Signer & Affiliate Offers (requires Shopee account cookie)
// $webSig = $sdk->signWeb([
//     'url'     => 'https://affiliate.shopee.vn/api/v3/offer/product/list',
//     'method'  => 'GET',
//     'country' => 'VN',
//     'cookie'  => 'SPC_EC=...; SPC_F=...;',
// ]);
// $offers = $sdk->getAffiliateOfferList([
//     'keyword'   => 'tai nghe bluetooth',
//     'pageLimit' => 10,
//     'country'   => 'VN',
//     'cookie'    => 'SPC_EC=...; SPC_F=...;',
// ]);
