using System;
using System.Text.Json;
using MinSign;

namespace ShopeeApiDemo
{
    /// <summary>
    /// Quickstart C# (.NET 6/8/9 hoặc .NET Framework 4.7.2+ — Build Platform: x64)
    /// Đăng ký & lấy mã X-API-Key tại: https://vip-sign.minmintool.site
    /// </summary>
    internal static class QuickstartCSharp
    {
        public static void Main()
        {
            string apiKey = Environment.GetEnvironmentVariable("MINSIGN_API_KEY") ?? "YOUR_X_API_KEY_HERE";
            if (apiKey == "YOUR_X_API_KEY_HERE")
            {
                Console.WriteLine("[!] Hãy điền mã X-API-Key lấy tại https://vip-sign.minmintool.site");
                return;
            }

            using var sdk = new MinSignClient(
                apiKey: apiKey,
                signerUrl: "https://vip-sign.minmintool.site",
                vaultFilePath: "./minsign_data/devices_vault.json",
                defaultCountry: "VN"
            );

            Console.WriteLine("1. Phiên bản SDK: " + sdk.Version().GetRawText());
            Console.WriteLine("2. Hạn mức X-API-Key: " + sdk.CheckApiKey().GetRawText());

            JsonElement detail = sdk.GetProductDetail(new
            {
                productUrl = "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
                proxy = "",
                country = "VN"
            });

            var prod = detail.GetProperty("data").GetProperty("product");
            Console.WriteLine("3. Tên SP: " + prod.GetProperty("name").GetString());
            Console.WriteLine("   Giá VNĐ: " + prod.GetProperty("priceVnd").GetInt64());

            // [MỚI v1.1.0 - AFFILIATE] Lấy sản phẩm mới nhất của Shop theo thời gian thực (hỗ trợ lọc sinceItemId)
            JsonElement newest = sdk.GetShopNewestProducts(new
            {
                shopId = "1023922469",
                limit = 10,
                sinceItemId = "", // Truyền latestItemId lần quét trước để chỉ nhận SP vừa đăng mới!
                cookie = "",      // Khuyên truyền Cookie Shopee phụ + Proxy để mở full tab Mới Nhất realtime
                proxy = "",
                country = "VN"
            });
            Console.WriteLine("4. SP mới nhất của Shop: " + newest.GetProperty("data").GetProperty("latestItemId").GetString());

            // [MỚI v1.1.0 - AFFILIATE] Lấy danh sách Video của Shop (kèm link .mp4 gốc không watermark & SP gắn giỏ)
            JsonElement shopVideos = sdk.GetShopVideos(new
            {
                username = "lovito.vn",
                limit = 20,
                maxPages = 1,
                cookie = "", // Truyền Cookie Shopee để lấy toàn bộ timeline Shopee Video của Shop
                proxy = "",
                country = "VN"
            });
            Console.WriteLine("5. Creator UserId kênh Video Shop: " + shopVideos.GetProperty("data").GetProperty("userId").GetString());
        }
    }
}
