# Quickstart by Language — All 7 Official Wrappers (`v2.1.0`)

`minsign_sdk.dll` (`v2.1.0`) exposes a standard **Windows x64 C-ABI** (`54 Action APIs`, `58 C-ABI exports`). Because there are zero external runtime dependencies inside the DLL, you can embed the exact same high-performance engine into **Python, Node.js/TypeScript, C#, C++, PHP 8+ FFI, Go, or Java JNA** in minutes.

---

## Architecture & Memory-Safety Rules (Applies to Every Language)

1. **64-bit (`x64`) Process Required:** `bin/win-x64/minsign_sdk.dll` is compiled for `windows/amd64`. Ensure your Python, Node.js, .NET (`PlatformTarget=x64`), PHP, Go (`GOARCH=amd64`), Java JVM, or C++ target is **64-bit**. Loading a 64-bit DLL into a 32-bit process triggers `BadImageFormatException` / `OSError: [WinError 193]`.
2. **Always Free Returned Pointers (`MinSign_Free`):** Every C-ABI function returns a heap-allocated UTF-8 JSON `char*` owned by Go/C. Copy the UTF-8 bytes into a native string and **always invoke `MinSign_Free(ptr)`** in a `try / finally`, `defer`, or RAII destructor. All 7 official wrappers handle this automatically.
3. **Initialize Once (`MinSign_Init`):** Call `MinSign_Init` once at startup with your `X-API-Key` from [https://vip-sign.minmintool.site](https://vip-sign.minmintool.site). Afterward, all 54 APIs are thread-safe and share the same local `devices_vault.json` and connection pools.
4. **Universal Dispatcher (`MinSign_Invoke`):** Every wrapper exposes both strongly named methods (e.g., `resolve_shopee_url`, `get_affiliate_offer_list`) and a generic `invoke(action, payload)` method for forward compatibility.

---

## 1. Python 3.8+ (Pure `ctypes` — Zero `pip` Dependencies)

- **Wrapper:** [`wrappers/python/minsign_sdk.py`](../wrappers/python/minsign_sdk.py)
- **Examples:** [`examples/quickstart_python.py`](../examples/quickstart_python.py), [`examples/batch_product_scraper.py`](../examples/batch_product_scraper.py), [`examples/affiliate_hunter.py`](../examples/affiliate_hunter.py), [`examples/live_bag_scraper.py`](../examples/live_bag_scraper.py)

### Setup
```bash
git clone https://github.com/minmin2402/shopeeapi.git
cd shopeeapi
python --version   # Verify 64-bit Python 3.8+
python examples/quickstart_python.py
```

### Runnable Example
```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(
    api_key="YOUR_X_API_KEY",
    dll_path="./bin/win-x64/minsign_sdk.dll",
    vault_file_path="./minsign_data/devices_vault.json",
    default_country="VN",
)

print("SDK Version:", sdk.version())

# 1. Parse any Shopee URL offline or with redirect following
parsed = sdk.resolve_shopee_url(url="https://shopee.co.th/product/1834601441/57811171288")
print("Parsed:", parsed["country"], parsed["shopId"], parsed["itemId"])

# 2. Batch scrape product details concurrently inside the DLL
batch = sdk.batch_get_product_details(
    product_urls=[
        "https://shopee.co.id/product/2955704/26112249802",
        "https://shopee.co.th/product/1834601441/57811171288",
    ],
    proxies=["http://user:pass@ip:port"],
    concurrency=5,
)
print(f"Batch: {batch['succeeded']}/{batch['total']} in {batch['elapsedMs']}ms")

# 3. Sign a Web Chrome 131 request directly
web_sig = sdk.sign_web(
    url="https://affiliate.shopee.vn/api/v3/offer/product/list?list_type=0&sort_type=1&page_offset=0&page_limit=10",
    country="VN",
    cookie="SPC_U=...; SPC_ST=...;",
)
print("Web Headers:", list(web_sig["headers"].keys()))
```

---

## 2. Node.js / TypeScript / Electron (`koffi` Async Worker)

- **Wrapper:** [`wrappers/nodejs/minsign_sdk.js`](../wrappers/nodejs/minsign_sdk.js)
- **TypeScript Types:** [`wrappers/nodejs/minsign_sdk.d.ts`](../wrappers/nodejs/minsign_sdk.d.ts)
- **Example:** [`examples/quickstart_nodejs.js`](../examples/quickstart_nodejs.js)

### Setup
```bash
npm install koffi
node examples/quickstart_nodejs.js
```

### Runnable Example (TypeScript / CommonJS)
```typescript
import { MinSignClient } from "./wrappers/nodejs/minsign_sdk";

async function main() {
  const sdk = new MinSignClient({
    apiKey: "YOUR_X_API_KEY",
    dllPath: "./bin/win-x64/minsign_sdk.dll",
    vaultFilePath: "./minsign_data/devices_vault.json",
    defaultCountry: "VN",
  });

  // Non-blocking async calls — safe for Electron renderer & Express/NestJS servers
  const suggestions = await sdk.getSearchSuggestions({
    keyword: "mechanical keyboard",
    limit: 10,
    country: "VN",
  });
  console.log("Suggestions:", suggestions.suggestions);

  const profile = await sdk.getAccountProfile({
    cookie: "SPC_U=...; SPC_ST=...;",
    country: "VN",
  });
  console.log("Account alive:", profile.alive, "| Username:", profile.username);
}

main().catch(console.error);
```

---

## 3. C# (.NET 6/7/8/9 & .NET Framework 4.7.2+ — `x64`)

- **Wrapper:** [`wrappers/csharp/MinSignSdk.cs`](../wrappers/csharp/MinSignSdk.cs)
- **Example:** [`examples/QuickstartCSharp.cs`](../examples/QuickstartCSharp.cs)

### Setup
1. Set your `.csproj` platform target to `x64`:
   ```xml
   <PropertyGroup>
     <PlatformTarget>x64</PlatformTarget>
   </PropertyGroup>
   ```
2. Copy `bin/win-x64/minsign_sdk.dll` next to your compiled `.exe` (or set `CopyToOutputDirectory=PreserveNewest`).
3. Include `wrappers/csharp/MinSignSdk.cs` in your project.

### Runnable Example
```csharp
using System;
using System.Text.Json;
using MinSign;

class Program
{
    static void Main()
    {
        using var sdk = new MinSignClient(
            apiKey: "YOUR_X_API_KEY",
            signerUrl: "https://vip-sign.minmintool.site",
            vaultFilePath: "./minsign_data/devices_vault.json",
            defaultCountry: "ID"
        );

        JsonElement flashSale = sdk.GetFlashSaleItems(new
        {
            country = "ID",
            limit = 20,
            offset = 0,
            proxy = "http://user:pass@ip:port"
        });
        Console.WriteLine(flashSale.GetRawText());

        JsonElement liveBag = sdk.GetLiveBagItems(new
        {
            liveUrl = "https://live.shopee.co.id/share?session=123456789",
            limit = 20,
            country = "ID"
        });
        Console.WriteLine(liveBag.GetRawText());
    }
}
```

---

## 4. C++17 (Header-Only RAII Wrapper)

- **Wrapper:** [`wrappers/cpp/minsign_sdk_client.hpp`](../wrappers/cpp/minsign_sdk_client.hpp)
- **C Header:** [`include/minsign_sdk.h`](../include/minsign_sdk.h)
- **Example:** [`examples/quickstart_cpp.cpp`](../examples/quickstart_cpp.cpp)

### Setup (MSVC x64 Developer Command Prompt)
```bat
cl /std:c++17 /EHsc /I wrappers\cpp examples\quickstart_cpp.cpp /Fe:quickstart_cpp.exe
quickstart_cpp.exe
```

### Runnable Example
```cpp
#include <iostream>
#include "minsign_sdk_client.hpp"

int main() {
    minsign::Client sdk(R"({
        "apiKey": "YOUR_X_API_KEY",
        "signerUrl": "https://vip-sign.minmintool.site",
        "vaultFilePath": "./minsign_data/devices_vault.json",
        "defaultCountry": "VN"
    })", "bin\\win-x64\\minsign_sdk.dll");

    // RAII wrapper automatically calls MinSign_Free on every returned char*
    std::string resolved = sdk.resolveShopeeUrl(R"({
        "url": "https://shopee.co.th/product/1834601441/57811171288"
    })");
    std::cout << resolved << std::endl;

    std::string ratings = sdk.getProductRatings(R"({
        "shopId": "1834601441",
        "itemId": "57811171288",
        "country": "TH",
        "limit": 10
    })");
    std::cout << ratings << std::endl;
    return 0;
}
```

---

## 5. PHP 8.1+ (Built-in `ext-ffi` — Zero Composer Packages)

- **Wrapper:** [`wrappers/php/MinSignSdk.php`](../wrappers/php/MinSignSdk.php)
- **Example:** [`examples/quickstart_php.php`](../examples/quickstart_php.php)

### Setup
1. Use 64-bit PHP 8.1+ on Windows.
2. Enable FFI in `php.ini`:
   ```ini
   extension=ffi
   ffi.enable=true
   ```
3. Run:
   ```bash
   php examples/quickstart_php.php
   ```

### Runnable Example
```php
<?php
declare(strict_types=1);

require_once __DIR__ . '/wrappers/php/MinSignSdk.php';

use MinSign\MinSignClient;

$sdk = new MinSignClient(
    apiKey: 'YOUR_X_API_KEY',
    dllPath: __DIR__ . '/bin/win-x64/minsign_sdk.dll',
    defaultCountry: 'VN'
);

// Memory-safe: MinSignClient frees every C pointer in try/finally via MinSign_Free
$resolved = $sdk->resolveShopeeUrl([
    'url' => 'https://shopee.vn/product/104187240/19894959672',
]);
print_r($resolved);

$offers = $sdk->getAffiliateOfferList([
    'keyword' => 'sunscreen',
    'sortType' => 1,
    'pageLimit' => 10,
    'cookie' => 'SPC_U=...; SPC_ST=...;',
    'country' => 'VN',
]);
print_r($offers);
```

---

## 6. Go (Zero CGO — Native Windows `syscall.NewLazyDLL`)

- **Wrapper:** [`wrappers/go/minsign.go`](../wrappers/go/minsign.go) (`package minsignclient`)
- **Example:** [`examples/quickstart_go.go`](../examples/quickstart_go.go)

### Setup
No `gcc` or `CGO_ENABLED=1` is required to consume the DLL from Go! The wrapper uses `syscall.NewLazyDLL` and safely frees every pointer via `defer client.free(ptr)`.

```bash
go run examples/quickstart_go.go
```

### Runnable Example
```go
package main

import (
	"fmt"
	"log"

	minsignclient "github.com/minmin2402/shopeeapi/wrappers/go"
)

func main() {
	sdk, err := minsignclient.NewClient(minsignclient.Config{
		APIKey:         "YOUR_X_API_KEY",
		DLLPath:        "./bin/win-x64/minsign_sdk.dll",
		VaultFilePath:  "./minsign_data/devices_vault.json",
		DefaultCountry: "TH",
	})
	if err != nil {
		log.Fatal(err)
	}

	resolved, err := sdk.ResolveShopeeUrl(map[string]any{
		"url": "https://shopee.co.th/product/1834601441/57811171288",
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Resolved: %+v\n", resolved)

	recs, err := sdk.GetRecommendProducts(map[string]any{
		"bundle":  "daily_discover_main",
		"country": "TH",
		"limit":   10,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Recommendations: %+v\n", recs)
}
```

---

## 7. Java 11+ (JNA — Zero JNI Compilation)

- **Wrapper:** [`wrappers/java/MinSignSdk.java`](../wrappers/java/MinSignSdk.java)
- **Example:** [`examples/QuickstartJava.java`](../examples/QuickstartJava.java)

### Setup
Add `net.java.dev.jna:jna:5.14.0` (Maven/Gradle) or place `jna-5.14.0.jar` on your classpath, using a 64-bit JDK:

```xml
<!-- Maven pom.xml -->
<dependency>
  <groupId>net.java.dev.jna</groupId>
  <artifactId>jna</artifactId>
  <version>5.14.0</version>
</dependency>
```

```bash
javac -cp jna-5.14.0.jar -d out wrappers/java/MinSignSdk.java examples/QuickstartJava.java
java -cp "out;jna-5.14.0.jar" QuickstartJava
```

### Runnable Example
```java
import com.minsign.sdk.MinSignSdk;

public class Quickstart {
    public static void main(String[] args) {
        try (MinSignSdk sdk = new MinSignSdk(
                "YOUR_X_API_KEY",
                null, // auto-detect ./bin/win-x64/minsign_sdk.dll
                MinSignSdk.DEFAULT_SIGNER_URL,
                MinSignSdk.DEFAULT_VAULT_FILE_PATH,
                "",
                "SG",
                25000
        )) {
            // MinSignSdk automatically invokes MinSign_Free(ptr) inside try/finally
            String resolved = sdk.resolveShopeeUrl(
                "{\"shopId\":\"2955704\",\"itemId\":\"26112249802\",\"country\":\"ID\"}"
            );
            System.out.println("Resolved: " + resolved);

            String hints = sdk.getSearchSuggestions(
                "{\"keyword\":\"air fryer\",\"limit\":10,\"country\":\"SG\"}"
            );
            System.out.println("Suggestions: " + hints);
        }
    }
}
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `WinError 193` / `BadImageFormatException` | 32-bit interpreter loading 64-bit DLL | Switch to 64-bit (`x64`) Python, .NET, PHP, JVM, or Go (`GOARCH=amd64`). |
| `X-API-Key` rejected / `401` | Invalid or expired key | Check balance & active plan at [https://vip-sign.minmintool.site](https://vip-sign.minmintool.site) via `check_api_key`. |
| `90309999` on Affiliate or Checkout APIs | Missing proxy, stale cookie, or Layer-2 risk check | Use residential/4G proxy matching the region, verify cookie with `get_account_profile`, and enable `attachRiskHeaders: true`. |
| Slow throughput on batch scraping | Too few proxies for concurrency | Match `concurrency` to your `proxies[]` pool size (up to `16` for `batch_get_product_details`). |
