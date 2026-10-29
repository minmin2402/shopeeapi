"use strict";
/**
 * Official Node.js / Electron Wrapper cho MinSign Native Universal SDK (minsign_sdk.dll)
 * Sử dụng `koffi` để gọi C-ABI bất đồng bộ (Worker Thread) không bao giờ gây đơ UI Electron!
 * Cài đặt: npm install koffi
 */
const fs = require("fs");
const path = require("path");

class MinSignClient {
  constructor(options = {}) {
    const {
      apiKey,
      dllPath = null,
      signerUrl = "https://vip-sign.minmintool.site",
      vaultFilePath = "./minsign_data/devices_vault.json",
      vaultSecret = "",
      defaultCountry = "VN",
      timeoutMs = 25000,
    } = options;

    if (!apiKey || !String(apiKey).trim()) {
      throw new Error("Bắt buộc truyền mã X-API-Key (apiKey) khi khởi tạo MinSignClient.");
    }

    const koffi = require("koffi");
    this._koffi = koffi;
    const resolvedDll = MinSignClient._resolveDll(dllPath);
    const lib = koffi.load(resolvedDll);

    // Dùng void* cho kết quả trả về để giải phóng chuẩn xác qua MinSign_Free(ptr)
    this._fnVersion = lib.func("void* MinSign_Version()");
    this._fnInit = lib.func("void* MinSign_Init(const char* configJson)");
    this._fnCheckKey = lib.func("void* MinSign_CheckApiKey()");
    this._fnListDevices = lib.func("void* MinSign_ListLocalDevices()");
    this._fnInvoke = lib.func("void* MinSign_Invoke(const char* action, const char* reqJson)");
    this._fnFree = lib.func("void MinSign_Free(void* ptr)");

    const initPtr = this._fnInit(
      JSON.stringify({
        apiKey: String(apiKey).trim(),
        signerUrl,
        vaultFilePath,
        vaultSecret,
        defaultCountry,
        timeoutMs,
      })
    );
    this.initInfo = this._consumePtr(initPtr);
  }

  static _resolveDll(customPath) {
    if (customPath && fs.existsSync(customPath)) return path.resolve(customPath);
    const libName = process.platform === "win32" ? "minsign_sdk.dll" : "libminsign_sdk.so";
    const candidates = [
      path.resolve(process.cwd(), libName),
      path.resolve(process.cwd(), "bin/win-x64", libName),
      path.resolve(__dirname, libName),
      path.resolve(__dirname, "../../bin/win-x64", libName),
      path.resolve(__dirname, "../../dist/win-x64", libName),
      path.resolve(__dirname, "../bin", libName),
    ];
    for (const c of candidates) {
      if (fs.existsSync(c)) return c;
    }
    throw new Error(`Không tìm thấy ${libName}. Hãy đặt ${libName} cạnh file hoặc truyền dllPath.`);
  }

  _consumePtr(ptr) {
    if (!ptr) throw new Error("minsign_sdk.dll trả về con trỏ NULL.");
    try {
      const jsonStr = this._koffi.decode(ptr, "char", -1);
      const parsed = JSON.parse(jsonStr);
      if (!parsed.ok) {
        throw new Error(parsed.error || JSON.stringify(parsed));
      }
      return parsed.data;
    } finally {
      this._fnFree(ptr);
    }
  }

  invoke(action, payload = {}) {
    const jsonReq = typeof payload === "string" ? payload : JSON.stringify(payload || {});
    return new Promise((resolve, reject) => {
      this._fnInvoke.async(String(action), jsonReq, (err, ptr) => {
        if (err) return reject(err);
        try {
          resolve(this._consumePtr(ptr));
        } catch (ex) {
          reject(ex);
        }
      });
    });
  }

  version() { return this._consumePtr(this._fnVersion()); }
  checkApiKey() { return this.invoke("check_api_key", {}); }
  bindAccountDevice(req) { return this.invoke("bind_account_device", req); }
  listLocalDevices() { return Promise.resolve(this._consumePtr(this._fnListDevices())); }
  removeLocalDevice(accountKey) { return this.invoke("remove_local_device", { accountKey }); }
  signRaw(req) { return this.invoke("sign_raw", req); }

  // Sản phẩm, Shop, Voucher, Tìm kiếm & Affiliate Theo Dõi Shop
  getProductDetail(req) { return this.invoke("get_product_detail", req); }
  getShopOverview(req) { return this.invoke("get_shop_overview", req); }
  getShopProducts(req) { return this.invoke("get_shop_products", req); }
  getShopNewestProducts(req) { return this.invoke("get_shop_newest_products", req); }
  getShopVideos(req) { return this.invoke("get_shop_videos", req); }
  getShopCategories(req) { return this.invoke("get_shop_categories", req); }
  getShopVouchers(req) { return this.invoke("get_shop_vouchers", req); }
  searchProducts(req) { return this.invoke("search_products", req); }
  getCategoryTree(req = {}) { return this.invoke("get_category_tree", req); }

  // Đăng Video Shopee & Affiliate
  uploadShopeeVideo(req) { return this.invoke("upload_shopee_video", req); }
  precheckVideoUpload(req) { return this.invoke("precheck_video_upload", req); }
  getAffiliateProducts(req) { return this.invoke("get_affiliate_products", req); }
  mutateMp4Fingerprint(req) { return this.invoke("mutate_mp4_fingerprint", req); }

  // Buff View Shopee Video & Kênh Video
  buffVideoView(req) { return this.invoke("buff_video_view", req); }
  buffVideoBatch(req) { return this.invoke("buff_video_batch", req); }
  getVideoDetail(req) { return this.invoke("get_video_detail", req); }
  getChannelAndHashtagVideos(req) { return this.invoke("get_channel_and_hashtag_videos", req); }

  // Giỏ hàng & Cổng Ký Vạn Năng
  addToCart(req) { return this.invoke("add_to_cart", req); }
  executeSignedRequest(req) { return this.invoke("execute_signed_request", req); }
}

module.exports = { MinSignClient };
