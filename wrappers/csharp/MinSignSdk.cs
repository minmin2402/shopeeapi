using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

namespace MinSign
{
    /// <summary>
    /// Official C# / .NET Wrapper cho MinSign Native Universal SDK (minsign_sdk.dll).
    /// Tương thích .NET Framework 4.7.2+, .NET Core 3.1+, .NET 6/7/8/9 (x64).
    /// Tự động giải phóng bộ nhớ C-ABI (MinSign_Free) chống rò rỉ RAM 100%.
    /// </summary>
    public sealed class MinSignClient : IDisposable
    {
        private const string DllName = "minsign_sdk.dll";

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern bool SetDllDirectoryW(string lpPathName);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Version();

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

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Init(IntPtr configJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_CheckApiKey();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_ListLocalDevices();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr MinSign_Invoke(IntPtr actionUtf8, IntPtr reqJsonUtf8);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        private static extern void MinSign_Free(IntPtr ptr);

        private bool _disposed;

        public MinSignClient(
            string apiKey,
            string signerUrl = "https://vip-sign.minmintool.site",
            string vaultFilePath = "./minsign_data/devices_vault.json",
            string vaultSecret = "",
            string defaultCountry = "VN",
            int timeoutMs = 25000)
        {
            if (string.IsNullOrWhiteSpace(apiKey))
                throw new ArgumentException("Bắt buộc truyền mã X-API-Key (apiKey).", nameof(apiKey));

            var initRes = CallPtr(() =>
            {
                IntPtr pCfg = ToUtf8Ptr(JsonSerializer.Serialize(new
                {
                    apiKey,
                    signerUrl,
                    vaultFilePath,
                    vaultSecret,
                    defaultCountry,
                    timeoutMs
                }));
                try { return MinSign_Init(pCfg); }
                finally { Marshal.FreeHGlobal(pCfg); }
            });

            EnsureOk(initRes);
        }

        public JsonElement Version() => CallPtr(MinSign_Version);
        public JsonElement CheckApiKey() => CallPtr(MinSign_CheckApiKey);
        public JsonElement ListLocalDevices() => CallPtr(MinSign_ListLocalDevices);

        public JsonElement BindAccountDevice(object request) => Invoke("bind_account_device", request);
        public JsonElement RemoveLocalDevice(string accountKey) => Invoke("remove_local_device", new { accountKey });
        public JsonElement SignRaw(object request) => Invoke("sign_raw", request);

        // Nhóm Sản Phẩm, Shop, Voucher, Tìm Kiếm
        public JsonElement GetProductDetail(object request) => Invoke("get_product_detail", request);
        public JsonElement GetShopOverview(object request) => Invoke("get_shop_overview", request);
        public JsonElement GetShopProducts(object request) => Invoke("get_shop_products", request);
        public JsonElement GetShopCategories(object request) => Invoke("get_shop_categories", request);
        public JsonElement GetShopVouchers(object request) => Invoke("get_shop_vouchers", request);
        public JsonElement SearchProducts(object request) => Invoke("search_products", request);
        public JsonElement GetCategoryTree(object request = null) => Invoke("get_category_tree", request ?? new { });

        // Nhóm Đăng Video Shopee & Affiliate
        public JsonElement UploadShopeeVideo(object request) => Invoke("upload_shopee_video", request);
        public JsonElement PrecheckVideoUpload(object request) => Invoke("precheck_video_upload", request);
        public JsonElement GetAffiliateProducts(object request) => Invoke("get_affiliate_products", request);
        public JsonElement MutateMp4Fingerprint(object request) => Invoke("mutate_mp4_fingerprint", request);

        // Nhóm Buff View Shopee Video & Kênh Video
        public JsonElement BuffVideoView(object request) => Invoke("buff_video_view", request);
        public JsonElement BuffVideoBatch(object request) => Invoke("buff_video_batch", request);
        public JsonElement GetVideoDetail(object request) => Invoke("get_video_detail", request);
        public JsonElement GetChannelAndHashtagVideos(object request) => Invoke("get_channel_and_hashtag_videos", request);

        // Nhóm Giỏ Hàng & Gọi Ký Mở Rộng
        public JsonElement AddToCart(object request) => Invoke("add_to_cart", request);
        public JsonElement ExecuteSignedRequest(object request) => Invoke("execute_signed_request", request);

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

        private static JsonElement CallPtr(Func<IntPtr> fn)
        {
            IntPtr ptr = fn();
            if (ptr == IntPtr.Zero)
                throw new InvalidOperationException("minsign_sdk.dll trả về con trỏ rỗng.");
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
