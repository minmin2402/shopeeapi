"use strict";
/**
 * Official Node.js / Electron / TypeScript Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll).
 * Uses `koffi` async worker-thread calls so native calls never block the Node.js event loop or Electron UI.
 * Install once: npm install koffi
 *
 * Exposes all 44 production APIs across 8 Shopee regions with App Mobile + Web Chrome signing modes.
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
      throw new Error("apiKey (X-API-Key) is required to initialize MinSignClient.");
    }

    const koffi = require("koffi");
    this._koffi = koffi;
    const resolvedDll = MinSignClient._resolveDll(dllPath);
    const lib = koffi.load(resolvedDll);

    // Core C-ABI bindings (return void* so the exact native address is freed via MinSign_Free)
    this._fnVersion = lib.func("void* MinSign_Version()");
    this._fnInit = lib.func("void* MinSign_Init(const char* configJson)");
    this._fnCheckKey = lib.func("void* MinSign_CheckApiKey()");
    this._fnListDevices = lib.func("void* MinSign_ListLocalDevices()");
    this._fnGetRiskToken = lib.func("void* MinSign_GetRiskToken(const char* reqJson)");
    this._fnInvoke = lib.func("void* MinSign_Invoke(const char* action, const char* reqJson)");
    this._fnFree = lib.func("void MinSign_Free(void* ptr)");

    // v2.0.0 C-ABI bindings (13 new production APIs)
    this._fnSignWeb = MinSignClient._bindOptional(lib, "void* MinSign_SignWeb(const char* reqJson)");
    this._fnResolveShopeeUrl = MinSignClient._bindOptional(lib, "void* MinSign_ResolveShopeeUrl(const char* reqJson)");
    this._fnBatchGetProductDetails = MinSignClient._bindOptional(lib, "void* MinSign_BatchGetProductDetails(const char* reqJson)");
    this._fnGetProductRatings = MinSignClient._bindOptional(lib, "void* MinSign_GetProductRatings(const char* reqJson)");
    this._fnGetFlashSaleItems = MinSignClient._bindOptional(lib, "void* MinSign_GetFlashSaleItems(const char* reqJson)");
    this._fnGetRecommendProducts = MinSignClient._bindOptional(lib, "void* MinSign_GetRecommendProducts(const char* reqJson)");
    this._fnGetSearchSuggestions = MinSignClient._bindOptional(lib, "void* MinSign_GetSearchSuggestions(const char* reqJson)");
    this._fnGetAccountProfile = MinSignClient._bindOptional(lib, "void* MinSign_GetAccountProfile(const char* reqJson)");
    this._fnGetCartSummary = MinSignClient._bindOptional(lib, "void* MinSign_GetCartSummary(const char* reqJson)");
    this._fnClaimShopVoucher = MinSignClient._bindOptional(lib, "void* MinSign_ClaimShopVoucher(const char* reqJson)");
    this._fnGetAffiliateOfferList = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliateOfferList(const char* reqJson)");
    this._fnGetAffiliateCommissionReport = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliateCommissionReport(const char* reqJson)");
    this._fnGetLiveBagItems = MinSignClient._bindOptional(lib, "void* MinSign_GetLiveBagItems(const char* reqJson)");

    // v2.1.0 C-ABI bindings (10 MCN, Partnership Accept/Reply & Affiliate Center APIs)
    this._fnGetAffiliateUserProfile = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliateUserProfile(const char* reqJson)");
    this._fnGetMcnPartnershipStatus = MinSignClient._bindOptional(lib, "void* MinSign_GetMcnPartnershipStatus(const char* reqJson)");
    this._fnReplyMcnInvitation = MinSignClient._bindOptional(lib, "void* MinSign_ReplyMcnInvitation(const char* reqJson)");
    this._fnGetMcnKolPartnerships = MinSignClient._bindOptional(lib, "void* MinSign_GetMcnKolPartnerships(const char* reqJson)");
    this._fnSendMcnPartnershipInvitation = MinSignClient._bindOptional(lib, "void* MinSign_SendMcnPartnershipInvitation(const char* reqJson)");
    this._fnManageMcnPartnership = MinSignClient._bindOptional(lib, "void* MinSign_ManageMcnPartnership(const char* reqJson)");
    this._fnGetMcnAnalytics = MinSignClient._bindOptional(lib, "void* MinSign_GetMcnAnalytics(const char* reqJson)");
    this._fnGetAffiliatePaymentTax = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliatePaymentTax(const char* reqJson)");
    this._fnGetAffiliateClickReport = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliateClickReport(const char* reqJson)");
    this._fnGetAffiliateBilling = MinSignClient._bindOptional(lib, "void* MinSign_GetAffiliateBilling(const char* reqJson)");

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

  static _bindOptional(lib, signature) {
    try {
      return lib.func(signature);
    } catch (_err) {
      return null;
    }
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
    throw new Error(`Could not locate ${libName}. Place it next to your script or pass dllPath.`);
  }

  static _serializePayload(payload) {
    if (typeof payload === "string") return payload;
    if (!payload || typeof payload !== "object") return "{}";
    const req = { ...payload };
    if (req.cookie && typeof req.cookie === "object") {
      req.cookie = JSON.stringify(req.cookie);
    }
    if (Array.isArray(req.cookies)) {
      req.cookies = req.cookies.map((c) => (c && typeof c === "object" ? JSON.stringify(c) : String(c)));
    }
    return JSON.stringify(req);
  }

  _consumePtr(ptr) {
    if (!ptr) throw new Error("minsign_sdk.dll returned a NULL pointer.");
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

  _callExportAsync(fn, action, payload = {}) {
    if (!fn) {
      return this.invoke(action, payload);
    }
    const jsonReq = MinSignClient._serializePayload(payload);
    return new Promise((resolve, reject) => {
      fn.async(jsonReq, (err, ptr) => {
        if (err) return reject(err);
        try {
          resolve(this._consumePtr(ptr));
        } catch (ex) {
          reject(ex);
        }
      });
    });
  }

  invoke(action, payload = {}) {
    const jsonReq = MinSignClient._serializePayload(payload);
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

  // Group 1: Key Management, Local Device Vault & Core Signing (App + Web)
  version() { return this._consumePtr(this._fnVersion()); }
  checkApiKey() { return this.invoke("check_api_key", {}); }
  bindAccountDevice(req) { return this.invoke("bind_account_device", req); }
  listLocalDevices() { return Promise.resolve(this._consumePtr(this._fnListDevices())); }
  removeLocalDevice(accountKey) { return this.invoke("remove_local_device", { accountKey }); }
  signRaw(req) { return this.invoke("sign_raw", req); }
  signWeb(req) { return this._callExportAsync(this._fnSignWeb, "sign_web", req); }
  getRiskToken(req = {}) { return this._callExportAsync(this._fnGetRiskToken, "get_risk_token", req); }

  // Group 2: Products, Shops, Vouchers, Search, Recommendations & URL Tools
  resolveShopeeUrl(req) { return this._callExportAsync(this._fnResolveShopeeUrl, "resolve_shopee_url", req); }
  getProductDetail(req) { return this.invoke("get_product_detail", req); }
  batchGetProductDetails(req) { return this._callExportAsync(this._fnBatchGetProductDetails, "batch_get_product_details", req); }
  getProductRatings(req) { return this._callExportAsync(this._fnGetProductRatings, "get_product_ratings", req); }
  getFlashSaleItems(req = {}) { return this._callExportAsync(this._fnGetFlashSaleItems, "get_flash_sale_items", req); }
  getRecommendProducts(req = {}) { return this._callExportAsync(this._fnGetRecommendProducts, "get_recommend_products", req); }
  getSearchSuggestions(req) { return this._callExportAsync(this._fnGetSearchSuggestions, "get_search_suggestions", req); }
  getShopOverview(req) { return this.invoke("get_shop_overview", req); }
  getShopProducts(req) { return this.invoke("get_shop_products", req); }
  getShopNewestProducts(req) { return this.invoke("get_shop_newest_products", req); }
  getShopVideos(req) { return this.invoke("get_shop_videos", req); }
  getShopCategories(req) { return this.invoke("get_shop_categories", req); }
  getShopVouchers(req) { return this.invoke("get_shop_vouchers", req); }
  searchProducts(req) { return this.invoke("search_products", req); }
  searchProductsByImage(req) { return this.invoke("search_products_by_image", req); }
  getImageBoundingBox(req) { return this.invoke("get_image_bounding_box", req); }
  getCategoryTree(req = {}) { return this.invoke("get_category_tree", req); }

  // Group 3: Account, Cart & Voucher Actions
  getAccountProfile(req) { return this._callExportAsync(this._fnGetAccountProfile, "get_account_profile", req); }
  getCartSummary(req) { return this._callExportAsync(this._fnGetCartSummary, "get_cart_summary", req); }
  claimShopVoucher(req) { return this._callExportAsync(this._fnClaimShopVoucher, "claim_shop_voucher", req); }

  // Group 4: Shopee Video Studio & Affiliate Marketing
  uploadShopeeVideo(req) { return this.invoke("upload_shopee_video", req); }
  precheckVideoUpload(req) { return this.invoke("precheck_video_upload", req); }
  getAffiliateProducts(req) { return this.invoke("get_affiliate_products", req); }
  getAffiliateOfferList(req) { return this._callExportAsync(this._fnGetAffiliateOfferList, "get_affiliate_offer_list", req); }
  getAffiliateCommissionReport(req) { return this._callExportAsync(this._fnGetAffiliateCommissionReport, "get_affiliate_commission_report", req); }
  convertAffiliateLink(req) { return this.invoke("convert_affiliate_link", req); }
  batchConvertAffiliateLinks(req) { return this.invoke("batch_convert_affiliate_links", req); }
  mutateMp4Fingerprint(req) { return this.invoke("mutate_mp4_fingerprint", req); }

  // Group 5: Shopee Video Discovery & View Booster
  buffVideoView(req) { return this.invoke("buff_video_view", req); }
  buffVideoBatch(req) { return this.invoke("buff_video_batch", req); }
  getVideoDetail(req) { return this.invoke("get_video_detail", req); }
  getChannelAndHashtagVideos(req) { return this.invoke("get_channel_and_hashtag_videos", req); }

  // Group 6: Shopee Live Commerce & Viewer Pipeline
  getLiveSessionDetail(req) { return this.invoke("get_live_session_detail", req); }
  getLiveBagItems(req) { return this._callExportAsync(this._fnGetLiveBagItems, "get_live_bag_items", req); }
  buffLiveView(req) { return this.invoke("buff_live_view", req); }
  buffLiveBatch(req) { return this.invoke("buff_live_batch", req); }

  // Group 8: Shopee MCN, Accept/Reply Invitations & Affiliate Center (v2.1.0)
  getAffiliateUserProfile(req) { return this._callExportAsync(this._fnGetAffiliateUserProfile, "get_affiliate_user_profile", req); }
  getMcnPartnershipStatus(req) { return this._callExportAsync(this._fnGetMcnPartnershipStatus, "get_mcn_partnership_status", req); }
  replyMcnInvitation(req) { return this._callExportAsync(this._fnReplyMcnInvitation, "reply_mcn_invitation", req); }
  getMcnKolPartnerships(req) { return this._callExportAsync(this._fnGetMcnKolPartnerships, "get_mcn_kol_partnerships", req); }
  sendMcnPartnershipInvitation(req) { return this._callExportAsync(this._fnSendMcnPartnershipInvitation, "send_mcn_partnership_invitation", req); }
  manageMcnPartnership(req) { return this._callExportAsync(this._fnManageMcnPartnership, "manage_mcn_partnership", req); }
  getMcnAnalytics(req) { return this._callExportAsync(this._fnGetMcnAnalytics, "get_mcn_analytics", req); }
  getAffiliatePaymentTax(req) { return this._callExportAsync(this._fnGetAffiliatePaymentTax, "get_affiliate_payment_tax", req); }
  getAffiliateClickReport(req) { return this._callExportAsync(this._fnGetAffiliateClickReport, "get_affiliate_click_report", req); }
  getAffiliateBilling(req) { return this._callExportAsync(this._fnGetAffiliateBilling, "get_affiliate_billing", req); }

  // Group 7: Universal Signed HTTP Gateway (App + Web)
  executeSignedRequest(req) { return this.invoke("execute_signed_request", req); }
}

module.exports = { MinSignClient };
