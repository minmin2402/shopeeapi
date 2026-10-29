/**
 * Quickstart C++17 — ShopeeAPI Native Universal SDK (minsign_sdk.dll)
 * Compile (MSVC x64): cl /EHsc /std:c++17 examples\quickstart_cpp.cpp
 * Đăng ký & lấy mã X-API-Key tại: https://vip-sign.minmintool.site
 */
#include <iostream>
#include "../wrappers/cpp/minsign_sdk_client.hpp"

int main() {
    try {
        minsign::Client sdk(R"({
            "apiKey": "YOUR_X_API_KEY_HERE",
            "signerUrl": "https://vip-sign.minmintool.site",
            "vaultFilePath": "./minsign_data/devices_vault.json",
            "defaultCountry": "VN"
        })", "bin\\win-x64\\minsign_sdk.dll");

        std::cout << "Key Status: " << sdk.checkApiKey() << "\n\n";

        std::string productJson = sdk.getProductDetail(R"({
            "productUrl": "https://shopee.vn/V%E1%BB%A3t-pickleball-Perseus-4-b%E1%BB%81-m%E1%BA%B7t-carbon-(NFC)-i.1023922469.25294038727",
            "country": "VN"
        })");
        std::cout << "Product Detail JSON:\n" << productJson << std::endl;
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
