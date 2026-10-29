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

  // [MỚI v1.1.0 - AFFILIATE] Lấy danh sách SP mới nhất của Shop theo thời gian thực
  const newest = await sdk.getShopNewestProducts({
    shopId: "1023922469",
    limit: 10,
    sinceItemId: "", // Truyền latestItemId lần quét trước để canh SP mới vừa lên kệ
    country: "VN",
  });
  console.log("4. SP mới nhất của Shop -> count:", newest.count, "| latestItemId:", newest.latestItemId);

  // [MỚI v1.1.0 - AFFILIATE] Lấy danh sách Video của Shop (tự động giải mã Shop -> Creator userId)
  const vids = await sdk.getShopVideos({
    username: "lovito.vn",
    limit: 20,
    maxPages: 1,
    cookie: "", // Truyền Cookie Shopee còn sống để tải full danh sách video + mp4Url gốc không logo
    country: "VN",
  });
  console.log("5. Kênh Shopee Video Shop -> userId:", vids.userId, "| videos:", vids.count);
}

main().catch(console.error);
