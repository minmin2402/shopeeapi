#pragma once
/**
 * Official Header-Only C++17 Wrapper for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll / libminsign_sdk.so).
 * No import library (.lib) required — dynamically loads symbols via LoadLibraryA / dlopen with RAII lifetime
 * management and exception-safe MinSign_Free cleanup for every returned C-ABI pointer.
 *
 * Exposes all 44 production APIs across 8 Shopee regions with App Mobile + Web Chrome signing modes.
 */
#include <stdexcept>
#include <string>

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace minsign {

class Client {
public:
    explicit Client(const std::string& configJson, const std::string& dllPath = "minsign_sdk.dll") {
#ifdef _WIN32
        handle_ = LoadLibraryA(dllPath.c_str());
        if (!handle_) handle_ = LoadLibraryA("bin\\win-x64\\minsign_sdk.dll");
        if (!handle_) handle_ = LoadLibraryA("..\\..\\bin\\win-x64\\minsign_sdk.dll");
        if (!handle_) throw std::runtime_error("Cannot load " + dllPath);
#else
        handle_ = dlopen(dllPath.c_str(), RTLD_LAZY);
        if (!handle_) throw std::runtime_error("Cannot load " + dllPath);
#endif

        // Core C-ABI symbols
        fnVersion_ = loadSymbol<Fn0>("MinSign_Version");
        fnInit_    = loadSymbol<Fn1>("MinSign_Init");
        fnCheck_   = loadSymbol<Fn0>("MinSign_CheckApiKey");
        fnList_    = loadSymbol<Fn0>("MinSign_ListLocalDevices");
        fnRisk_    = loadSymbol<Fn1>("MinSign_GetRiskToken");
        fnInvoke_  = loadSymbol<Fn2>("MinSign_Invoke");
        fnFree_    = loadSymbol<FnFree>("MinSign_Free");

        // v2.0.0 C-ABI symbols (13 new production APIs)
        fnSignWeb_                      = loadSymbol<Fn1>("MinSign_SignWeb");
        fnResolveShopeeUrl_             = loadSymbol<Fn1>("MinSign_ResolveShopeeUrl");
        fnBatchGetProductDetails_       = loadSymbol<Fn1>("MinSign_BatchGetProductDetails");
        fnGetProductRatings_            = loadSymbol<Fn1>("MinSign_GetProductRatings");
        fnGetFlashSaleItems_            = loadSymbol<Fn1>("MinSign_GetFlashSaleItems");
        fnGetRecommendProducts_         = loadSymbol<Fn1>("MinSign_GetRecommendProducts");
        fnGetSearchSuggestions_         = loadSymbol<Fn1>("MinSign_GetSearchSuggestions");
        fnGetAccountProfile_            = loadSymbol<Fn1>("MinSign_GetAccountProfile");
        fnGetCartSummary_               = loadSymbol<Fn1>("MinSign_GetCartSummary");
        fnClaimShopVoucher_             = loadSymbol<Fn1>("MinSign_ClaimShopVoucher");
        fnGetAffiliateOfferList_        = loadSymbol<Fn1>("MinSign_GetAffiliateOfferList");
        fnGetAffiliateCommissionReport_ = loadSymbol<Fn1>("MinSign_GetAffiliateCommissionReport");
        fnGetLiveBagItems_              = loadSymbol<Fn1>("MinSign_GetLiveBagItems");

        if (!fnInit_ || !fnInvoke_ || !fnFree_) {
            closeLibrary();
            throw std::runtime_error("Missing required C-ABI symbols in minsign_sdk.dll");
        }
        initResponse_ = consume(fnInit_(configJson.c_str()));
    }

    ~Client() {
        closeLibrary();
    }

    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;

    // Universal dispatcher
    std::string invoke(const std::string& action, const std::string& reqJson = "{}") const {
        return consume(fnInvoke_(action.c_str(), reqJson.c_str()));
    }

    // Group 1: Key Management, Local Device Vault & Core Signing (App + Web)
    std::string version() const {
        if (fnVersion_) return consume(fnVersion_());
        return invoke("version", "{}");
    }
    std::string checkApiKey() const {
        if (fnCheck_) return consume(fnCheck_());
        return invoke("check_api_key", "{}");
    }
    std::string bindAccountDevice(const std::string& reqJson) const { return invoke("bind_account_device", reqJson); }
    std::string listLocalDevices() const {
        if (fnList_) return consume(fnList_());
        return invoke("list_local_devices", "{}");
    }
    std::string removeLocalDevice(const std::string& reqJson) const { return invoke("remove_local_device", reqJson); }
    std::string signRaw(const std::string& reqJson) const { return invoke("sign_raw", reqJson); }
    std::string signWeb(const std::string& reqJson) const { return callExport(fnSignWeb_, "sign_web", reqJson); }
    std::string getRiskToken(const std::string& reqJson = "{}") const { return callExport(fnRisk_, "get_risk_token", reqJson); }

    // Group 2: Products, Shops, Vouchers, Search, Recommendations & URL Tools
    std::string resolveShopeeUrl(const std::string& reqJson) const { return callExport(fnResolveShopeeUrl_, "resolve_shopee_url", reqJson); }
    std::string getProductDetail(const std::string& reqJson) const { return invoke("get_product_detail", reqJson); }
    std::string batchGetProductDetails(const std::string& reqJson) const { return callExport(fnBatchGetProductDetails_, "batch_get_product_details", reqJson); }
    std::string getProductRatings(const std::string& reqJson) const { return callExport(fnGetProductRatings_, "get_product_ratings", reqJson); }
    std::string getFlashSaleItems(const std::string& reqJson = "{}") const { return callExport(fnGetFlashSaleItems_, "get_flash_sale_items", reqJson); }
    std::string getRecommendProducts(const std::string& reqJson = "{}") const { return callExport(fnGetRecommendProducts_, "get_recommend_products", reqJson); }
    std::string getSearchSuggestions(const std::string& reqJson) const { return callExport(fnGetSearchSuggestions_, "get_search_suggestions", reqJson); }
    std::string getShopOverview(const std::string& reqJson) const { return invoke("get_shop_overview", reqJson); }
    std::string getShopProducts(const std::string& reqJson) const { return invoke("get_shop_products", reqJson); }
    std::string getShopNewestProducts(const std::string& reqJson) const { return invoke("get_shop_newest_products", reqJson); }
    std::string getShopCategories(const std::string& reqJson) const { return invoke("get_shop_categories", reqJson); }
    std::string getShopVouchers(const std::string& reqJson) const { return invoke("get_shop_vouchers", reqJson); }
    std::string searchProducts(const std::string& reqJson) const { return invoke("search_products", reqJson); }
    std::string searchProductsByImage(const std::string& reqJson) const { return invoke("search_products_by_image", reqJson); }
    std::string getImageBoundingBox(const std::string& reqJson) const { return invoke("get_image_bounding_box", reqJson); }
    std::string getCategoryTree(const std::string& reqJson = "{}") const { return invoke("get_category_tree", reqJson); }

    // Group 3: Account, Cart & Voucher Actions
    std::string getAccountProfile(const std::string& reqJson) const { return callExport(fnGetAccountProfile_, "get_account_profile", reqJson); }
    std::string getCartSummary(const std::string& reqJson) const { return callExport(fnGetCartSummary_, "get_cart_summary", reqJson); }
    std::string claimShopVoucher(const std::string& reqJson) const { return callExport(fnClaimShopVoucher_, "claim_shop_voucher", reqJson); }

    // Group 4: Shopee Video Studio & Affiliate Marketing
    std::string uploadShopeeVideo(const std::string& reqJson) const { return invoke("upload_shopee_video", reqJson); }
    std::string precheckVideoUpload(const std::string& reqJson) const { return invoke("precheck_video_upload", reqJson); }
    std::string getAffiliateProducts(const std::string& reqJson) const { return invoke("get_affiliate_products", reqJson); }
    std::string getAffiliateOfferList(const std::string& reqJson) const { return callExport(fnGetAffiliateOfferList_, "get_affiliate_offer_list", reqJson); }
    std::string getAffiliateCommissionReport(const std::string& reqJson) const { return callExport(fnGetAffiliateCommissionReport_, "get_affiliate_commission_report", reqJson); }
    std::string convertAffiliateLink(const std::string& reqJson) const { return invoke("convert_affiliate_link", reqJson); }
    std::string batchConvertAffiliateLinks(const std::string& reqJson) const { return invoke("batch_convert_affiliate_links", reqJson); }
    std::string mutateMp4Fingerprint(const std::string& reqJson) const { return invoke("mutate_mp4_fingerprint", reqJson); }

    // Group 5: Shopee Video Discovery & View Booster
    std::string buffVideoView(const std::string& reqJson) const { return invoke("buff_video_view", reqJson); }
    std::string buffVideoBatch(const std::string& reqJson) const { return invoke("buff_video_batch", reqJson); }
    std::string getVideoDetail(const std::string& reqJson) const { return invoke("get_video_detail", reqJson); }
    std::string getShopVideos(const std::string& reqJson) const { return invoke("get_shop_videos", reqJson); }
    std::string getChannelAndHashtagVideos(const std::string& reqJson) const { return invoke("get_channel_and_hashtag_videos", reqJson); }

    // Group 6: Shopee Live Commerce & Viewer Pipeline
    std::string getLiveSessionDetail(const std::string& reqJson) const { return invoke("get_live_session_detail", reqJson); }
    std::string getLiveBagItems(const std::string& reqJson) const { return callExport(fnGetLiveBagItems_, "get_live_bag_items", reqJson); }
    std::string buffLiveView(const std::string& reqJson) const { return invoke("buff_live_view", reqJson); }
    std::string buffLiveBatch(const std::string& reqJson) const { return invoke("buff_live_batch", reqJson); }

    // Group 7: Universal Signed HTTP Gateway (App + Web via clientType)
    std::string executeSignedRequest(const std::string& reqJson) const { return invoke("execute_signed_request", reqJson); }

    const std::string& initResponse() const { return initResponse_; }

private:
    using Fn0    = char* (*)();
    using Fn1    = char* (*)(const char*);
    using Fn2    = char* (*)(const char*, const char*);
    using FnFree = void (*)(char*);

    struct NativePtrGuard {
        char* ptr;
        FnFree freeFn;
        ~NativePtrGuard() {
            if (ptr && freeFn) {
                freeFn(ptr);
            }
        }
    };

#ifdef _WIN32
    HMODULE handle_ = nullptr;
#else
    void* handle_ = nullptr;
#endif

    // Core function pointers
    Fn0 fnVersion_  = nullptr;
    Fn1 fnInit_     = nullptr;
    Fn0 fnCheck_    = nullptr;
    Fn0 fnList_     = nullptr;
    Fn1 fnRisk_     = nullptr;
    Fn2 fnInvoke_   = nullptr;
    FnFree fnFree_  = nullptr;

    // v2.0.0 function pointers
    Fn1 fnSignWeb_                      = nullptr;
    Fn1 fnResolveShopeeUrl_             = nullptr;
    Fn1 fnBatchGetProductDetails_       = nullptr;
    Fn1 fnGetProductRatings_            = nullptr;
    Fn1 fnGetFlashSaleItems_            = nullptr;
    Fn1 fnGetRecommendProducts_         = nullptr;
    Fn1 fnGetSearchSuggestions_         = nullptr;
    Fn1 fnGetAccountProfile_            = nullptr;
    Fn1 fnGetCartSummary_               = nullptr;
    Fn1 fnClaimShopVoucher_             = nullptr;
    Fn1 fnGetAffiliateOfferList_        = nullptr;
    Fn1 fnGetAffiliateCommissionReport_ = nullptr;
    Fn1 fnGetLiveBagItems_              = nullptr;

    std::string initResponse_;

    template <typename Fn>
    Fn loadSymbol(const char* name) const {
#ifdef _WIN32
        return reinterpret_cast<Fn>(GetProcAddress(handle_, name));
#else
        return reinterpret_cast<Fn>(dlsym(handle_, name));
#endif
    }

    void closeLibrary() noexcept {
        if (!handle_) return;
#ifdef _WIN32
        FreeLibrary(handle_);
#else
        dlclose(handle_);
#endif
        handle_ = nullptr;
    }

    std::string callExport(Fn1 fn, const char* action, const std::string& reqJson) const {
        if (fn) {
            return consume(fn(reqJson.c_str()));
        }
        return invoke(action, reqJson);
    }

    std::string consume(char* ptr) const {
        if (!ptr) throw std::runtime_error("minsign_sdk.dll returned null pointer");
        NativePtrGuard guard{ptr, fnFree_};
        return std::string(ptr);
    }
};

} // namespace minsign
