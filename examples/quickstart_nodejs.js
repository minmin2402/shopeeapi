/**
 * Quickstart Node.js / Electron — ShopeeAPI Native Universal SDK (minsign_sdk.dll)
 * Cài đặt 1 lần: npm install koffi
 * Đăng ký & lấy mã X-API-Key tại: https://vip-sign.minmintool.site
 */
"use strict";

const { MinSignClient } = require("../wrappers/nodejs/minsign_sdk");

async function main() {
  const apiKey = process.env.MINSIGN_API_KEY || "YOUR_X_API_KEY_HERE";
  if (apiKey === "YOUR_X_API_KEY_HERE") {
    console.log("[!] Hãy thay 'YOUR_X_API_KEY_HERE' bằng mã X-API-Key lấy tại https://vip-sign.minmintool.site");
    return;
  }

  const sdk = new MinSignClient({
    apiKey,
    signerUrl: "https://vip-sign.minmintool.site",
    vaultFilePath: "./minsign_data/devices_vault.json",
    defaultCountry: "VN",
  });

  console.log("1. Phiên bản SDK:", sdk.version());
  console.log("2. Thông tin hạn mức X-API-Key:", await sdk.checkApiKey());

  const detail = await sdk.getProductDetail({
    productUrl: "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
    country: "VN",
  });

  console.log("3. Tên sản phẩm:", detail.product?.name);
  console.log("   Giá bán (VNĐ):", detail.product?.priceVnd);
  console.log("   Số phân loại :", (detail.product?.models || []).length);
}

main().catch(console.error);
