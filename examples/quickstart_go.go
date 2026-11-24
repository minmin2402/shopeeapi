//go:build windows

// Quickstart Go (Windows LazyDLL, zero CGO!) — ShopeeAPI MinSign Native Universal SDK v2.0.0
//
// How to run from the repository root (no gcc / CGO required):
//   go mod init github.com/minmin2402/shopeeapi
//   $env:MINSIGN_API_KEY = "shopee-..."
//   go run ./examples/quickstart_go.go
//
// Obtain your X-API-Key at: https://vip-sign.minmintool.site
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	minsignclient "github.com/minmin2402/shopeeapi/wrappers/go"
)

func main() {
	apiKey := os.Getenv("MINSIGN_API_KEY")
	if apiKey == "" {
		fmt.Println("[!] Set MINSIGN_API_KEY with your key from https://vip-sign.minmintool.site")
		fmt.Println("    Example (PowerShell): $env:MINSIGN_API_KEY=\"shopee-...\"; go run ./examples/quickstart_go.go")
		return
	}

	sdk, err := minsignclient.NewClient(minsignclient.Config{
		APIKey:         apiKey,
		SignerURL:      minsignclient.DefaultSignerURL,
		VaultFilePath:  minsignclient.DefaultVaultFilePath,
		DefaultCountry: "VN",
		TimeoutMs:      25000,
	})
	if err != nil {
		log.Fatalf("Failed to initialize MinSign SDK: %v", err)
	}

	// 1. Check SDK version & X-API-Key quota
	ver, err := sdk.Version()
	if err != nil {
		log.Fatalf("Version failed: %v", err)
	}
	fmt.Printf("1. SDK Version   : %v (%v)\n", ver["version"], ver["name"])

	keyInfo, err := sdk.CheckApiKey()
	if err != nil {
		log.Fatalf("CheckApiKey failed: %v", err)
	}
	keyJSON, _ := json.Marshal(keyInfo)
	fmt.Printf("2. API Key Status: %s\n", string(keyJSON))

	// 2. [v2.0.0] Resolve any Shopee URL into canonical IDs
	sampleURL := "https://shopee.vn/product/1023922469/25294038727"
	resolved, err := sdk.ResolveShopeeUrl(map[string]any{
		"url":            sampleURL,
		"country":        "VN",
		"followRedirect": true,
	})
	if err != nil {
		log.Fatalf("ResolveShopeeUrl failed: %v", err)
	}
	fmt.Printf("\n3. Resolved URL  : type=%v | shopId=%v | itemId=%v | canonical=%v\n",
		resolved["urlType"], resolved["shopId"], resolved["itemId"], resolved["canonicalProductUrl"])

	// 3. Fetch complete product detail (no Shopee cookie required)
	detail, err := sdk.GetProductDetail(map[string]any{
		"productUrl": sampleURL,
		"country":    "VN",
	})
	if err != nil {
		log.Fatalf("GetProductDetail failed: %v", err)
	}
	if prod, ok := detail["product"].(map[string]any); ok {
		fmt.Println("\n4. Product Detail:")
		fmt.Printf("   - Name        : %v\n", prod["name"])
		fmt.Printf("   - Price (VND) : %.0f\n", prod["priceVnd"])
		fmt.Printf("   - Sold        : %v\n", prod["historicalSold"])
		fmt.Printf("   - Rating      : %v\n", prod["ratingStar"])
	}

	// 4. [v2.0.0] Fetch buyer ratings & autocomplete search suggestions
	ratings, err := sdk.GetProductRatings(map[string]any{
		"productUrl": sampleURL,
		"limit":      5,
		"offset":     0,
		"country":    "VN",
	})
	if err != nil {
		log.Fatalf("GetProductRatings failed: %v", err)
	}
	if list, ok := ratings["ratings"].([]any); ok {
		fmt.Printf("\n5. Product Ratings fetched: %d items\n", len(list))
	}

	suggestions, err := sdk.GetSearchSuggestions(map[string]any{
		"keyword": "iphone 16",
		"limit":   5,
		"country": "VN",
	})
	if err != nil {
		log.Fatalf("GetSearchSuggestions failed: %v", err)
	}
	sugJSON, _ := json.Marshal(suggestions["suggestions"])
	fmt.Printf("6. Search Suggestions     : %s\n", string(sugJSON))

	// 5. [v2.0.0] Concurrent batch product detail fetch
	batch, err := sdk.BatchGetProductDetails(map[string]any{
		"productUrls": []string{sampleURL},
		"concurrency": 4,
		"country":     "VN",
	})
	if err != nil {
		log.Fatalf("BatchGetProductDetails failed: %v", err)
	}
	fmt.Printf("7. Batch Product Fetch    : total=%v | succeeded=%v | failed=%v | elapsedMs=%v\n",
		batch["total"], batch["succeeded"], batch["failed"], batch["elapsedMs"])

	// 6. [v2.0.0] Optional: Chrome 131 Web Signer & Affiliate Offers (requires Shopee account cookie)
	// _, _ = sdk.SignWeb(map[string]any{
	//     "url":     "https://affiliate.shopee.vn/api/v3/offer/product/list",
	//     "method":  "GET",
	//     "country": "VN",
	//     "cookie":  "SPC_EC=...; SPC_F=...;",
	// })
	// _, _ = sdk.GetAffiliateOfferList(map[string]any{
	//     "keyword":   "tai nghe bluetooth",
	//     "pageLimit": 10,
	//     "country":   "VN",
	//     "cookie":    "SPC_EC=...; SPC_F=...;",
	// })
}
