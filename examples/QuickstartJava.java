import com.minsign.sdk.MinSignSdk;

/**
 * Quickstart Java (JNA) — ShopeeAPI MinSign Native Universal SDK v2.0.0
 *
 * Requirements:
 *   - JDK 11+ (64-bit / x64)
 *   - JNA JAR (e.g. jna-5.14.0.jar from Maven Central: net.java.dev.jna:jna)
 *   - Obtain your X-API-Key at: https://vip-sign.minmintool.site
 *
 * Compile & Run from the repository root:
 *   javac -cp jna-5.14.0.jar -d out wrappers/java/MinSignSdk.java examples/QuickstartJava.java
 *   set MINSIGN_API_KEY=shopee-...
 *   java  -cp out;jna-5.14.0.jar QuickstartJava
 */
public final class QuickstartJava {

    public static void main(String[] args) {
        String apiKey = System.getenv("MINSIGN_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            System.out.println("[!] Set MINSIGN_API_KEY with your key from https://vip-sign.minmintool.site");
            System.out.println("    Example (PowerShell): $env:MINSIGN_API_KEY=\"shopee-...\"; java -cp out;jna-5.14.0.jar QuickstartJava");
            return;
        }

        try (MinSignSdk sdk = new MinSignSdk(
                apiKey,
                null, // auto-detect ./bin/win-x64/minsign_sdk.dll
                MinSignSdk.DEFAULT_SIGNER_URL,
                MinSignSdk.DEFAULT_VAULT_FILE_PATH,
                "",
                "VN",
                25000
        )) {
            // 1. Check SDK version & X-API-Key quota
            System.out.println("1. SDK Version   : " + sdk.version());
            System.out.println("2. API Key Status: " + sdk.checkApiKey());

            // 2. [v2.0.0] Resolve any Shopee product/shop/video/live URL into canonical IDs
            String sampleUrl = "https://shopee.vn/product/1023922469/25294038727";
            String resolvedJson = sdk.resolveShopeeUrl(
                    "{\"url\":\"" + sampleUrl + "\",\"country\":\"VN\",\"followRedirect\":true}"
            );
            System.out.println("\n3. Resolved URL  : " + resolvedJson);

            // 3. Fetch complete product detail (no Shopee cookie required)
            String detailJson = sdk.getProductDetail(
                    "{\"productUrl\":\"" + sampleUrl + "\",\"country\":\"VN\"}"
            );
            System.out.println("\n4. Product Detail OK? " + MinSignSdk.isOk(detailJson));
            System.out.println("   Payload preview: " + truncate(detailJson, 300));

            // 4. [v2.0.0] Fetch buyer ratings & autocomplete search suggestions
            String ratingsJson = sdk.getProductRatings(
                    "{\"productUrl\":\"" + sampleUrl + "\",\"limit\":5,\"offset\":0,\"country\":\"VN\"}"
            );
            System.out.println("\n5. Product Ratings OK? " + MinSignSdk.isOk(ratingsJson));

            String suggestionsJson = sdk.getSearchSuggestions(
                    "{\"keyword\":\"iphone 16\",\"limit\":5,\"country\":\"VN\"}"
            );
            System.out.println("6. Search Suggestions : " + suggestionsJson);

            // 5. [v2.0.0] Concurrent batch product detail fetch
            String batchJson = sdk.batchGetProductDetails(
                    "{\"productUrls\":[\"" + sampleUrl + "\"],\"concurrency\":4,\"country\":\"VN\"}"
            );
            System.out.println("7. Batch Product Fetch: " + truncate(batchJson, 300));

            // 6. [v2.0.0] Optional: Chrome 131 Web Signer & Affiliate Offers (requires Shopee account cookie)
            // String webSig = sdk.signWeb("{\"url\":\"https://affiliate.shopee.vn/api/v3/offer/product/list\",\"method\":\"GET\",\"country\":\"VN\",\"cookie\":\"SPC_EC=...; SPC_F=...;\"}");
            // String offers = sdk.getAffiliateOfferList("{\"keyword\":\"tai nghe bluetooth\",\"pageLimit\":10,\"country\":\"VN\",\"cookie\":\"SPC_EC=...; SPC_F=...;\"}");
        }
    }

    private static String truncate(String s, int maxLen) {
        if (s == null || s.length() <= maxLen) {
            return s;
        }
        return s.substring(0, maxLen) + "...";
    }
}
