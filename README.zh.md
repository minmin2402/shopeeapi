🌐 **语言:** [English](README.md) · [Tiếng Việt](README.vi.md) · [Bahasa Indonesia](README.id.md) · [ภาษาไทย](README.th.md) · [简体中文](README.zh.md)

# ShopeeAPI — MinSign Native Universal SDK (`minsign_sdk.dll` v1.5.0)

[![Version](https://img.shields.io/badge/Release-v1.5.0%20(31%20APIs)-8B5CF6?style=for-the-badge)](https://github.com/minmin2402/shopeeapi/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64%20(C--ABI%20DLL)-2563EB?style=for-the-badge)](#)
[![Shopee Regions](https://img.shields.io/badge/Regions-VN%20%7C%20TW%20%7C%20PH%20%7C%20MY%20%7C%20TH%20%7C%20ID%20%7C%20SG%20%7C%20BR-EE4D2D?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Wrappers-C%23%20%7C%20Python%20%7C%20Node.js%20%7C%20C%2B%2B%20%7C%20PHP%20%7C%20Delphi-10B981?style=for-the-badge)](#)
[![Cloud Signer](https://img.shields.io/badge/Get%20X--API--Key-vip--sign.minmintool.site-F59E0B?style=for-the-badge)](https://vip-sign.minmintool.site)

**跨语言原生核心库（`minsign_sdk.dll` — 标准 C-ABI 接口）**，仅需 **1 个 DLL 文件**即可将完整的 Shopee 与 Shopee Affiliate 自动化能力快速集成到任何开发语言（`C# .NET`、`Python`、`Node.js / Electron`、`C/C++`、`Delphi`、`AutoIt`、`PHP FFI`、`Rust`、`Java JNA`）：

---

## 核心功能全景 (v1.5.0 — 共 31 个 API)

- **[v1.5.0 新增 — Shopee 联盟链接转换与批量短链 (`ConvertAffiliateLink` & `BatchConvertAffiliateLinks`)]:**
  - 支持将普通商品链接、已有 `aff_id` 链接、`universal-link` 或 `s.shopee.*` / `shp.ee` 短链直接转换为您账号下的官方联盟短链，支持最多 5 个追踪参数 `subId1..subId5`、自动识别站点与批量分块处理。
- **[v1.4.0 新增 — Shopee 直播间多线程人气与 WebSocket 心跳 (`GetLiveSessionDetail`, `BuffLiveView`, `BuffLiveBatch`)]:**
  - 内置 Proxy + Android uTLS WebSocket RFC 6455 心跳协议（`HB_REQ` Protobuf）、拉取 FLV/HLS 流及 `SZTracker` 埋点上报。
- **[v1.3.0 新增 — 纯 HTTP 以图搜款与 AI 物体框识别 (`SearchProductsByImage`, `GetImageBoundingBox`)]:**
  - 无需浏览器或模拟器，支持本地图片、剪贴板 Base64、TikTok/1688/淘宝图链或 Shopee CDN 图链搜同款/找低价。
- **[v1.2.0 新增 — Layer-2 安卓设备风控令牌 (`af-ac-enc-sz-token`)]:**
  - 自动生成并缓存绑定固定安卓硬件档案的 `af-ac-enc-sz-token`、`dfp`、`shpSecData`。
- **[v1.1.0 新增 — 联盟选品与无水印视频采集]:**
  - **`GetShopNewestProducts`：** 实时监控任意店铺最新上架商品（支持 `sinceItemId`、`withinHours` 及佣金信息）。
  - **`GetShopVideos`：** 批量获取店铺短视频，返回**无水印 `.mp4` 原链**与挂车商品列表。
- **支持 8 大 Shopee 站点数据采集**（`TW`, `VN`, `ID`, `TH`, `MY`, `PH`, `SG`, `BR`）— 商品详情、SKU 规格、店铺档案、优惠券、搜索与类目树（支持 `/product/{shop_id}/{item_id}` 短链）。
- **纯 API 四步发布 Shopee 短视频 (`UploadShopeeVideo`)** — 支持挂最多 6 个联盟商品、`<10ms` 修改 `.mp4` 二进制 `MD5/SHA-256` 指纹防查重。
- **本地固定设备库 (`devices_vault.json`, `AES-256-GCM`)** + **原生 `uTLS` 指纹网络栈**（支持各类 HTTP/SOCKS5 代理）。

---

## 获取 `X-API-Key`

1. 访问官网控制台：**[https://vip-sign.minmintool.site](https://vip-sign.minmintool.site)**
2. 注册或使用 Google 一键登录。
3. 开通按量计费（Pay-As-You-Go）或包月套餐，复制您的 **`X-API-Key`** 即可使用。

---

## Python 60 秒快速上手（无需安装额外依赖）

```python
from wrappers.python.minsign_sdk import MinSignClient

sdk = MinSignClient(api_key="YOUR_X_API_KEY_HERE", default_country="TW")

detail = sdk.get_product_detail(
    product_url="https://shopee.tw/product/116309859/26774240701",
    proxy="http://user:pass@ip:port",
    country="TW",
)
print("商品名称:", detail["product"]["name"])
print("价格:", detail["product"]["price"], "| 库存:", detail["product"]["stock"])
```

完整 31 个 API 列表请查阅 [`README.md`](./README.md#complete-api-reference-minsign_sdkdll-v150--31-built-in-functions)。
