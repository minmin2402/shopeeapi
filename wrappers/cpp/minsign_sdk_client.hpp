#pragma once
/**
 * Official Header-Only C++17 Wrapper cho MinSign Native Universal SDK (minsign_sdk.dll)
 * Không cần file .lib — tự động nạp động qua LoadLibraryA / dlopen và quản lý bộ nhớ RAII.
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
        fnInit_   = reinterpret_cast<Fn1>(GetProcAddress(handle_, "MinSign_Init"));
        fnCheck_  = reinterpret_cast<Fn0>(GetProcAddress(handle_, "MinSign_CheckApiKey"));
        fnList_   = reinterpret_cast<Fn0>(GetProcAddress(handle_, "MinSign_ListLocalDevices"));
        fnInvoke_ = reinterpret_cast<Fn2>(GetProcAddress(handle_, "MinSign_Invoke"));
        fnFree_   = reinterpret_cast<FnFree>(GetProcAddress(handle_, "MinSign_Free"));
#else
        handle_ = dlopen(dllPath.c_str(), RTLD_LAZY);
        if (!handle_) throw std::runtime_error("Cannot load " + dllPath);
        fnInit_   = reinterpret_cast<Fn1>(dlsym(handle_, "MinSign_Init"));
        fnCheck_  = reinterpret_cast<Fn0>(dlsym(handle_, "MinSign_CheckApiKey"));
        fnList_   = reinterpret_cast<Fn0>(dlsym(handle_, "MinSign_ListLocalDevices"));
        fnInvoke_ = reinterpret_cast<Fn2>(dlsym(handle_, "MinSign_Invoke"));
        fnFree_   = reinterpret_cast<FnFree>(dlsym(handle_, "MinSign_Free"));
#endif
        if (!fnInit_ || !fnInvoke_ || !fnFree_) {
            throw std::runtime_error("Missing required C-ABI symbols in minsign_sdk.dll");
        }
        initResponse_ = consume(fnInit_(configJson.c_str()));
    }

    ~Client() {
        if (handle_) {
#ifdef _WIN32
            FreeLibrary(handle_);
#else
            dlclose(handle_);
#endif
        }
    }

    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;

    std::string checkApiKey() const { return consume(fnCheck_()); }
    std::string listLocalDevices() const { return consume(fnList_()); }

    std::string invoke(const std::string& action, const std::string& reqJson = "{}") const {
        return consume(fnInvoke_(action.c_str(), reqJson.c_str()));
    }

    std::string getProductDetail(const std::string& reqJson) const { return invoke("get_product_detail", reqJson); }
    std::string getShopOverview(const std::string& reqJson) const { return invoke("get_shop_overview", reqJson); }
    std::string getShopProducts(const std::string& reqJson) const { return invoke("get_shop_products", reqJson); }
    std::string getShopVouchers(const std::string& reqJson) const { return invoke("get_shop_vouchers", reqJson); }
    std::string searchProducts(const std::string& reqJson) const { return invoke("search_products", reqJson); }
    std::string uploadShopeeVideo(const std::string& reqJson) const { return invoke("upload_shopee_video", reqJson); }
    std::string precheckVideoUpload(const std::string& reqJson) const { return invoke("precheck_video_upload", reqJson); }
    std::string mutateMp4Fingerprint(const std::string& reqJson) const { return invoke("mutate_mp4_fingerprint", reqJson); }
    std::string buffVideoView(const std::string& reqJson) const { return invoke("buff_video_view", reqJson); }
    std::string buffVideoBatch(const std::string& reqJson) const { return invoke("buff_video_batch", reqJson); }
    std::string executeSignedRequest(const std::string& reqJson) const { return invoke("execute_signed_request", reqJson); }

    const std::string& initResponse() const { return initResponse_; }

private:
    using Fn0    = char* (*)();
    using Fn1    = char* (*)(const char*);
    using Fn2    = char* (*)(const char*, const char*);
    using FnFree = void (*)(char*);

#ifdef _WIN32
    HMODULE handle_ = nullptr;
#else
    void* handle_ = nullptr;
#endif
    Fn1 fnInit_     = nullptr;
    Fn0 fnCheck_    = nullptr;
    Fn0 fnList_     = nullptr;
    Fn2 fnInvoke_   = nullptr;
    FnFree fnFree_  = nullptr;
    std::string initResponse_;

    std::string consume(char* ptr) const {
        if (!ptr) throw std::runtime_error("minsign_sdk.dll returned null pointer");
        std::string out(ptr);
        fnFree_(ptr);
        return out;
    }
};

} // namespace minsign
