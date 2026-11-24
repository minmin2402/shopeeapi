/**
 * Quickstart Node.js / Electron — MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll)
 * Install once: npm install koffi
 * Register & obtain your X-API-Key at: https://vip-sign.minmintool.site
 */
"use strict";

const { MinSignClient } = require("../wrappers/nodejs/minsign_sdk");

async function main() {
  const apiKey = process.env.MINSIGN_API_KEY || "YOUR_X_API_KEY_HERE";
  if (apiKey === "YOUR_X_API_KEY_HERE") {
    console.log("[!] Replace 'YOUR_X_API_KEY_HERE' with your X-API-Key from https://vip-sign.minmintool.site");
    return;
  }

  const sdk = new MinSignClient({
    apiKey,
    signerUrl: "https://vip-sign.minmintool.site",
    vaultFilePath: "./minsign_data/devices_vault.json",
    defaultCountry: "VN",
  });

  console.log("1. SDK Version:", sdk.version());
  console.log("2. API Key Quota:", await sdk.checkApiKey());

  // [v2.0.0] Resolve any Shopee URL across all 8 regions
  const sampleUrl = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727";
  const resolved = await sdk.resolveShopeeUrl({ url: sampleUrl });
  console.log("3. Resolved URL:", resolved.country, resolved.shopId, resolved.itemId);

  // Fetch product detail (no cookie required)
  const detail = await sdk.getProductDetail({
    productUrl: sampleUrl,
    country: "VN",
  });
  console.log("4. Product Name:", detail.product?.name);
  console.log("   Price (VND) :", detail.product?.priceVnd);
  console.log("   Variations  :", (detail.product?.models || []).length);

  // Fetch newest products of a shop
  const newest = await sdk.getShopNewestProducts({
    shopId: "1023922469",
    limit: 10,
    sinceItemId: "", // Pass previous latestItemId to monitor newly listed items
    country: "VN",
  });
  console.log("5. Shop Newest Products -> count:", newest.count, "| latestItemId:", newest.latestItemId);

  // Fetch shop videos (automatically resolves shop username -> creator userId)
  const vids = await sdk.getShopVideos({
    username: "lovito.vn",
    limit: 20,
    maxPages: 1,
    cookie: "", // Pass an active Shopee cookie to fetch full video timeline + watermark-free MP4 URLs
    country: "VN",
  });
  console.log("6. Shop Video Channel -> userId:", vids.userId, "| videos:", vids.count);
}

main().catch(console.error);
