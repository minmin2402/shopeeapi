//go:build windows

// Package minsignclient provides a zero-CGO Windows wrapper for the MinSign Native Universal SDK v2.0.0
// (`minsign_sdk.dll`) using `syscall.NewLazyDLL`.
//
// Every C-string pointer returned by `minsign_sdk.dll` is copied into Go memory and deterministically
// freed via `MinSign_Free(ptr)` inside a `defer` block.
package minsignclient

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
	"unsafe"
)

const (
	// DefaultSignerURL is the official MinSign Cloud Signer endpoint.
	DefaultSignerURL = "https://vip-sign.minmintool.site"
	// DefaultVaultFilePath is the default local path for persisting bound device fingerprints.
	DefaultVaultFilePath = "./minsign_data/devices_vault.json"
)

// Config configures a MinSign Native SDK client instance.
type Config struct {
	APIKey         string `json:"apiKey"`
	DLLPath        string `json:"-"`
	SignerURL      string `json:"signerUrl,omitempty"`
	VaultFilePath  string `json:"vaultFilePath,omitempty"`
	VaultSecret    string `json:"vaultSecret,omitempty"`
	DefaultCountry string `json:"defaultCountry,omitempty"`
	TimeoutMs      int    `json:"timeoutMs,omitempty"`
}

// SDKError represents an error returned by the MinSign Native SDK (`ok: false`).
type SDKError struct {
	Code    int
	Message string
	Raw     string
}

func (e *SDKError) Error() string {
	if e.Message != "" {
		return fmt.Sprintf("MinSign SDK Error (code %d): %s", e.Code, e.Message)
	}
	return fmt.Sprintf("MinSign SDK Error (code %d): %s", e.Code, e.Raw)
}

type sdkEnvelope struct {
	OK    bool            `json:"ok"`
	Code  int             `json:"code"`
	Data  json.RawMessage `json:"data"`
	Error string          `json:"error"`
}

var (
	kernel32DLL       = syscall.NewLazyDLL("kernel32.dll")
	procLstrlenA      = kernel32DLL.NewProc("lstrlenA")
	procRtlMoveMemory = kernel32DLL.NewProc("RtlMoveMemory")
)

// Client wraps minsign_sdk.dll via Windows LazyDLL without requiring CGO or gcc.
type Client struct {
	dllPath                      string
	dll                          *syscall.LazyDLL
	procVersion                  *syscall.LazyProc
	procInit                     *syscall.LazyProc
	procCheckApiKey              *syscall.LazyProc
	procListDevices              *syscall.LazyProc
	procGetRiskTok               *syscall.LazyProc
	procSignWeb                  *syscall.LazyProc
	procResolveShopeeUrl         *syscall.LazyProc
	procBatchGetProductDetails   *syscall.LazyProc
	procGetProductRatings        *syscall.LazyProc
	procGetFlashSaleItems        *syscall.LazyProc
	procGetRecommendProducts     *syscall.LazyProc
	procGetSearchSuggestions     *syscall.LazyProc
	procGetAccountProfile        *syscall.LazyProc
	procGetCartSummary           *syscall.LazyProc
	procClaimShopVoucher         *syscall.LazyProc
	procGetAffiliateOfferList    *syscall.LazyProc
	procGetAffiliateCommReport   *syscall.LazyProc
	procGetLiveBagItems          *syscall.LazyProc
	procInvoke                   *syscall.LazyProc
	procFree                     *syscall.LazyProc
	initInfo                     map[string]any
}

// NewClient loads minsign_sdk.dll, validates required C-ABI exports, and calls MinSign_Init.
func NewClient(cfg Config) (*Client, error) {
	apiKey := strings.TrimSpace(cfg.APIKey)
	if apiKey == "" {
		return nil, errors.New("minsignclient: APIKey is required")
	}
	if strings.TrimSpace(cfg.SignerURL) == "" {
		cfg.SignerURL = DefaultSignerURL
	}
	if strings.TrimSpace(cfg.VaultFilePath) == "" {
		cfg.VaultFilePath = DefaultVaultFilePath
	}
	if strings.TrimSpace(cfg.DefaultCountry) == "" {
		cfg.DefaultCountry = "VN"
	}
	if cfg.TimeoutMs <= 0 {
		cfg.TimeoutMs = 25000
	}
	cfg.APIKey = apiKey

	resolvedPath, err := ResolveDLLPath(cfg.DLLPath)
	if err != nil {
		return nil, err
	}

	dll := syscall.NewLazyDLL(resolvedPath)
	if err := dll.Load(); err != nil {
		return nil, fmt.Errorf("minsignclient: failed to load %s: %w", resolvedPath, err)
	}

	c := &Client{
		dllPath:                    resolvedPath,
		dll:                        dll,
		procVersion:                dll.NewProc("MinSign_Version"),
		procInit:                   dll.NewProc("MinSign_Init"),
		procCheckApiKey:            dll.NewProc("MinSign_CheckApiKey"),
		procListDevices:            dll.NewProc("MinSign_ListLocalDevices"),
		procGetRiskTok:             dll.NewProc("MinSign_GetRiskToken"),
		procSignWeb:                dll.NewProc("MinSign_SignWeb"),
		procResolveShopeeUrl:       dll.NewProc("MinSign_ResolveShopeeUrl"),
		procBatchGetProductDetails: dll.NewProc("MinSign_BatchGetProductDetails"),
		procGetProductRatings:      dll.NewProc("MinSign_GetProductRatings"),
		procGetFlashSaleItems:      dll.NewProc("MinSign_GetFlashSaleItems"),
		procGetRecommendProducts:   dll.NewProc("MinSign_GetRecommendProducts"),
		procGetSearchSuggestions:   dll.NewProc("MinSign_GetSearchSuggestions"),
		procGetAccountProfile:      dll.NewProc("MinSign_GetAccountProfile"),
		procGetCartSummary:         dll.NewProc("MinSign_GetCartSummary"),
		procClaimShopVoucher:       dll.NewProc("MinSign_ClaimShopVoucher"),
		procGetAffiliateOfferList:  dll.NewProc("MinSign_GetAffiliateOfferList"),
		procGetAffiliateCommReport: dll.NewProc("MinSign_GetAffiliateCommissionReport"),
		procGetLiveBagItems:        dll.NewProc("MinSign_GetLiveBagItems"),
		procInvoke:                 dll.NewProc("MinSign_Invoke"),
		procFree:                   dll.NewProc("MinSign_Free"),
	}

	// Verify essential C-ABI exports upfront so callers fail fast on mismatched DLLs.
	for _, proc := range []*syscall.LazyProc{
		c.procVersion,
		c.procInit,
		c.procCheckApiKey,
		c.procListDevices,
		c.procGetRiskTok,
		c.procInvoke,
		c.procFree,
	} {
		if err := proc.Find(); err != nil {
			return nil, fmt.Errorf("minsignclient: missing symbol %s in %s: %w", proc.Name, resolvedPath, err)
		}
	}

	cfgBytes, err := json.Marshal(cfg)
	if err != nil {
		return nil, fmt.Errorf("minsignclient: marshal init config: %w", err)
	}

	initInfo, err := c.callOneString(c.procInit, string(cfgBytes), true)
	if err != nil {
		return nil, err
	}
	c.initInfo = initInfo
	return c, nil
}

// ResolveDLLPath locates minsign_sdk.dll across common working directory and repository layouts.
func ResolveDLLPath(customPath string) (string, error) {
	if p := strings.TrimSpace(customPath); p != "" {
		abs, err := filepath.Abs(p)
		if err == nil {
			if st, statErr := os.Stat(abs); statErr == nil && !st.IsDir() {
				return abs, nil
			}
		}
		return "", fmt.Errorf("minsignclient: minsign_sdk.dll not found at custom path: %s", customPath)
	}

	const dllName = "minsign_sdk.dll"
	var candidates []string

	if cwd, err := os.Getwd(); err == nil {
		candidates = append(candidates,
			filepath.Join(cwd, dllName),
			filepath.Join(cwd, "bin", "win-x64", dllName),
			filepath.Join(cwd, "..", "bin", "win-x64", dllName),
			filepath.Join(cwd, "..", "..", "bin", "win-x64", dllName),
		)
	}
	if exePath, err := os.Executable(); err == nil {
		exeDir := filepath.Dir(exePath)
		candidates = append(candidates,
			filepath.Join(exeDir, dllName),
			filepath.Join(exeDir, "bin", "win-x64", dllName),
			filepath.Join(exeDir, "..", "..", "bin", "win-x64", dllName),
		)
	}
	if _, thisFile, _, ok := runtime.Caller(0); ok {
		wrapperDir := filepath.Dir(thisFile)
		candidates = append(candidates,
			filepath.Join(wrapperDir, dllName),
			filepath.Join(wrapperDir, "..", "..", "bin", "win-x64", dllName),
			filepath.Join(wrapperDir, "..", "..", "dist", "win-x64", dllName),
			filepath.Join(wrapperDir, "..", "bin", dllName),
		)
	}

	for _, cand := range candidates {
		abs, err := filepath.Abs(cand)
		if err != nil {
			continue
		}
		if st, err := os.Stat(abs); err == nil && !st.IsDir() {
			return abs, nil
		}
	}

	return "", fmt.Errorf("minsignclient: could not find %s (place it in ./bin/win-x64/ or set Config.DLLPath)", dllName)
}

// InitInfo returns the metadata returned by MinSign_Init.
func (c *Client) InitInfo() map[string]any {
	return c.initInfo
}

// DLLPath returns the resolved path of the loaded minsign_sdk.dll.
func (c *Client) DLLPath() string {
	return c.dllPath
}

// Invoke calls the universal C-ABI dispatcher `MinSign_Invoke(action, reqJson)`.
// It unwraps the `data` object and returns `*SDKError` when `ok` is false.
func (c *Client) Invoke(action string, payload any) (map[string]any, error) {
	act := strings.TrimSpace(action)
	if act == "" {
		return nil, errors.New("minsignclient: action cannot be empty")
	}
	reqJSON, err := marshalPayload(payload)
	if err != nil {
		return nil, err
	}
	return c.callTwoStrings(c.procInvoke, act, reqJSON, true)
}

// InvokeRaw calls `MinSign_Invoke(action, reqJson)` and returns the full JSON envelope
// (`ok`, `code`, `data`, `error`) without turning `ok: false` into a Go error.
func (c *Client) InvokeRaw(action string, payload any) (map[string]any, error) {
	act := strings.TrimSpace(action)
	if act == "" {
		return nil, errors.New("minsignclient: action cannot be empty")
	}
	reqJSON, err := marshalPayload(payload)
	if err != nil {
		return nil, err
	}
	return c.callTwoStrings(c.procInvoke, act, reqJSON, false)
}

// ============================================================================
// GROUP 1: CORE, AUTH, DEVICE VAULT & DUAL SIGNING (9 Methods)
// ============================================================================

// Version returns the native SDK version, supported regions, and TLS engine details (`MinSign_Version`).
func (c *Client) Version() (map[string]any, error) {
	return c.callVoid(c.procVersion, true)
}

// CheckApiKey validates the configured X-API-Key and returns quota/tier info (`MinSign_CheckApiKey`).
func (c *Client) CheckApiKey() (map[string]any, error) {
	return c.callVoid(c.procCheckApiKey, true)
}

// BindAccountDevice binds and persists a real Android device fingerprint for an account.
func (c *Client) BindAccountDevice(req any) (map[string]any, error) {
	return c.Invoke("bind_account_device", req)
}

// ListLocalDevices lists all bound device fingerprints in the local vault (`MinSign_ListLocalDevices`).
func (c *Client) ListLocalDevices() (map[string]any, error) {
	return c.callVoid(c.procListDevices, true)
}

// RemoveLocalDevice removes a bound device fingerprint from the local vault.
func (c *Client) RemoveLocalDevice(accountKey string) (map[string]any, error) {
	return c.Invoke("remove_local_device", map[string]any{"accountKey": accountKey})
}

// SignRaw generates raw Shopee security signature headers (App Mobile or Web mode via `clientType`).
func (c *Client) SignRaw(req any) (map[string]any, error) {
	return c.Invoke("sign_raw", req)
}

// SignWeb [v2.0.0] generates Chrome 131 Web security signature headers + patched cookies (`MinSign_SignWeb`).
func (c *Client) SignWeb(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procSignWeb, "sign_web", req)
}

// GetRiskToken fetches a fresh anti-fraud risk token / x-sap-ri (`MinSign_GetRiskToken`).
func (c *Client) GetRiskToken(req any) (map[string]any, error) {
	reqJSON, err := marshalPayload(req)
	if err != nil {
		return nil, err
	}
	return c.callOneString(c.procGetRiskTok, reqJSON, true)
}

// ExecuteSignedRequest executes an arbitrary signed Shopee API request (App or Web mode).
func (c *Client) ExecuteSignedRequest(req any) (map[string]any, error) {
	return c.Invoke("execute_signed_request", req)
}

// ============================================================================
// GROUP 2: COMMERCE, PRODUCT, SHOP, SEARCH & DISCOVERY (16 Methods)
// ============================================================================

// ResolveShopeeUrl [v2.0.0] parses or resolves any Shopee URL (product, shop, video, live, shortlink).
func (c *Client) ResolveShopeeUrl(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procResolveShopeeUrl, "resolve_shopee_url", req)
}

// GetProductDetail fetches complete Shopee product metadata, pricing, stock, and variants.
func (c *Client) GetProductDetail(req any) (map[string]any, error) {
	return c.Invoke("get_product_detail", req)
}

// BatchGetProductDetails [v2.0.0] fetches multiple products concurrently with proxy/cookie rotation.
func (c *Client) BatchGetProductDetails(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procBatchGetProductDetails, "batch_get_product_details", req)
}

// GetProductRatings [v2.0.0] fetches normalized buyer reviews, star counts, and media URLs.
func (c *Client) GetProductRatings(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetProductRatings, "get_product_ratings", req)
}

// GetShopOverview fetches a shop's public profile and performance metrics.
func (c *Client) GetShopOverview(req any) (map[string]any, error) {
	return c.Invoke("get_shop_overview", req)
}

// GetShopProducts lists products belonging to a shop.
func (c *Client) GetShopProducts(req any) (map[string]any, error) {
	return c.Invoke("get_shop_products", req)
}

// GetShopNewestProducts fetches newest products listed by a shop (supports `sinceItemId`).
func (c *Client) GetShopNewestProducts(req any) (map[string]any, error) {
	return c.Invoke("get_shop_newest_products", req)
}

// GetShopCategories lists custom categories configured on a shop.
func (c *Client) GetShopCategories(req any) (map[string]any, error) {
	return c.Invoke("get_shop_categories", req)
}

// GetShopVouchers lists active vouchers offered by a shop.
func (c *Client) GetShopVouchers(req any) (map[string]any, error) {
	return c.Invoke("get_shop_vouchers", req)
}

// SearchProducts searches Shopee products by keyword across any supported region.
func (c *Client) SearchProducts(req any) (map[string]any, error) {
	return c.Invoke("search_products", req)
}

// SearchProductsByImage performs visual AI product search from an image file, URL, or base64 payload.
func (c *Client) SearchProductsByImage(req any) (map[string]any, error) {
	return c.Invoke("search_products_by_image", req)
}

// GetImageBoundingBox detects product object bounding boxes inside an image.
func (c *Client) GetImageBoundingBox(req any) (map[string]any, error) {
	return c.Invoke("get_image_bounding_box", req)
}

// GetCategoryTree returns the Shopee category hierarchy for a region.
func (c *Client) GetCategoryTree(req any) (map[string]any, error) {
	return c.Invoke("get_category_tree", req)
}

// GetFlashSaleItems [v2.0.0] retrieves active Flash Sale sessions and discounted item listings.
func (c *Client) GetFlashSaleItems(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetFlashSaleItems, "get_flash_sale_items", req)
}

// GetRecommendProducts [v2.0.0] fetches similar or daily-discover recommended products.
func (c *Client) GetRecommendProducts(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetRecommendProducts, "get_recommend_products", req)
}

// GetSearchSuggestions [v2.0.0] fetches real-time autocomplete keyword suggestions.
func (c *Client) GetSearchSuggestions(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetSearchSuggestions, "get_search_suggestions", req)
}

// ============================================================================
// GROUP 3: ACCOUNT, CART & VOUCHER WALLET (3 Methods)
// ============================================================================

// GetAccountProfile [v2.0.0] checks cookie liveness and fetches account profile information.
func (c *Client) GetAccountProfile(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetAccountProfile, "get_account_profile", req)
}

// GetCartSummary [v2.0.0] fetches shopping cart items grouped by shop with subtotal.
func (c *Client) GetCartSummary(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetCartSummary, "get_cart_summary", req)
}

// ClaimShopVoucher [v2.0.0] saves/claims a shop voucher into the account wallet.
func (c *Client) ClaimShopVoucher(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procClaimShopVoucher, "claim_shop_voucher", req)
}

// ============================================================================
// GROUP 4: VIDEO UPLOAD, AFFILIATE & MP4 STUDIO (8 Methods)
// ============================================================================

// UploadShopeeVideo uploads a video directly to Shopee Video with optional affiliate product tags.
func (c *Client) UploadShopeeVideo(req any) (map[string]any, error) {
	return c.Invoke("upload_shopee_video", req)
}

// PrecheckVideoUpload verifies upload eligibility and prepares a Shopee Video upload session.
func (c *Client) PrecheckVideoUpload(req any) (map[string]any, error) {
	return c.Invoke("precheck_video_upload", req)
}

// GetAffiliateProducts queries affiliate-eligible products for tagging or promotion.
func (c *Client) GetAffiliateProducts(req any) (map[string]any, error) {
	return c.Invoke("get_affiliate_products", req)
}

// ConvertAffiliateLink converts a Shopee URL into a tracked affiliate shortlink.
func (c *Client) ConvertAffiliateLink(req any) (map[string]any, error) {
	return c.Invoke("convert_affiliate_link", req)
}

// BatchConvertAffiliateLinks batch-converts multiple Shopee URLs into tracked affiliate shortlinks.
func (c *Client) BatchConvertAffiliateLinks(req any) (map[string]any, error) {
	return c.Invoke("batch_convert_affiliate_links", req)
}

// MutateMp4Fingerprint mutates MP4 metadata locally to produce a unique MD5 hash.
func (c *Client) MutateMp4Fingerprint(req any) (map[string]any, error) {
	return c.Invoke("mutate_mp4_fingerprint", req)
}

// GetAffiliateOfferList [v2.0.0] queries Affiliate portal product offers with commission rates.
func (c *Client) GetAffiliateOfferList(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetAffiliateOfferList, "get_affiliate_offer_list", req)
}

// GetAffiliateCommissionReport [v2.0.0] queries Affiliate commission and conversion reports.
func (c *Client) GetAffiliateCommissionReport(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetAffiliateCommReport, "get_affiliate_commission_report", req)
}

// ============================================================================
// GROUP 5: SHOPEE VIDEO VIEWER & CHANNEL DISCOVERY (5 Methods)
// ============================================================================

// BuffVideoView sends a single signed Shopee Video view event.
func (c *Client) BuffVideoView(req any) (map[string]any, error) {
	return c.Invoke("buff_video_view", req)
}

// BuffVideoBatch runs a multi-worker batch of Shopee Video view events.
func (c *Client) BuffVideoBatch(req any) (map[string]any, error) {
	return c.Invoke("buff_video_batch", req)
}

// GetVideoDetail fetches Shopee Video post details, stream URLs, and tagged products.
func (c *Client) GetVideoDetail(req any) (map[string]any, error) {
	return c.Invoke("get_video_detail", req)
}

// GetShopVideos fetches the Shopee Video timeline of a shop or creator.
func (c *Client) GetShopVideos(req any) (map[string]any, error) {
	return c.Invoke("get_shop_videos", req)
}

// GetChannelAndHashtagVideos discovers Shopee Videos by channel or hashtag.
func (c *Client) GetChannelAndHashtagVideos(req any) (map[string]any, error) {
	return c.Invoke("get_channel_and_hashtag_videos", req)
}

// ============================================================================
// GROUP 6: SHOPEE LIVE VIEWER & LIVE BAG COMMERCE (4 Methods)
// ============================================================================

// GetLiveSessionDetail fetches Shopee Live session metadata, viewer count, and stream info.
func (c *Client) GetLiveSessionDetail(req any) (map[string]any, error) {
	return c.Invoke("get_live_session_detail", req)
}

// BuffLiveView joins and maintains a single signed Shopee Live viewer session.
func (c *Client) BuffLiveView(req any) (map[string]any, error) {
	return c.Invoke("buff_live_view", req)
}

// BuffLiveBatch runs a concurrent batch of Shopee Live viewer sessions.
func (c *Client) BuffLiveBatch(req any) (map[string]any, error) {
	return c.Invoke("buff_live_batch", req)
}

// GetLiveBagItems [v2.0.0] extracts products pinned in a Shopee Live shopping bag.
func (c *Client) GetLiveBagItems(req any) (map[string]any, error) {
	return c.callDirectOrInvoke(c.procGetLiveBagItems, "get_live_bag_items", req)
}

// ============================================================================
// INTERNAL MEMORY-SAFE SYSCALL / C-ABI HELPERS (NO CGO, GO VET CLEAN)
// ============================================================================

func (c *Client) callDirectOrInvoke(proc *syscall.LazyProc, action string, req any) (map[string]any, error) {
	if proc != nil && proc.Find() == nil {
		reqJSON, err := marshalPayload(req)
		if err != nil {
			return nil, err
		}
		return c.callOneString(proc, reqJSON, true)
	}
	return c.Invoke(action, req)
}

func (c *Client) callVoid(proc *syscall.LazyProc, unwrapData bool) (map[string]any, error) {
	ptr, _, _ := proc.Call()
	return c.consumePtr(ptr, unwrapData)
}

func (c *Client) callOneString(proc *syscall.LazyProc, arg1 string, unwrapData bool) (map[string]any, error) {
	b1, err := syscall.BytePtrFromString(arg1)
	if err != nil {
		return nil, fmt.Errorf("minsignclient: invalid C string argument: %w", err)
	}
	ptr, _, _ := proc.Call(uintptr(unsafe.Pointer(b1)))
	runtime.KeepAlive(b1)
	return c.consumePtr(ptr, unwrapData)
}

func (c *Client) callTwoStrings(proc *syscall.LazyProc, arg1, arg2 string, unwrapData bool) (map[string]any, error) {
	b1, err := syscall.BytePtrFromString(arg1)
	if err != nil {
		return nil, fmt.Errorf("minsignclient: invalid C string action: %w", err)
	}
	b2, err := syscall.BytePtrFromString(arg2)
	if err != nil {
		return nil, fmt.Errorf("minsignclient: invalid C string payload: %w", err)
	}
	ptr, _, _ := proc.Call(uintptr(unsafe.Pointer(b1)), uintptr(unsafe.Pointer(b2)))
	runtime.KeepAlive(b1)
	runtime.KeepAlive(b2)
	return c.consumePtr(ptr, unwrapData)
}

// consumePtr reads a null-terminated UTF-8 C-string via kernel32 lstrlenA + RtlMoveMemory
// and ALWAYS frees the native allocation via MinSign_Free(ptr) in a defer block.
func (c *Client) consumePtr(ptr uintptr, unwrapData bool) (map[string]any, error) {
	if ptr == 0 {
		return nil, errors.New("minsignclient: minsign_sdk.dll returned a NULL pointer")
	}
	defer func() {
		_, _, _ = c.procFree.Call(ptr)
	}()

	rawBytes := readCString(ptr)

	if !unwrapData {
		var rawMap map[string]any
		if err := json.Unmarshal(rawBytes, &rawMap); err != nil {
			return nil, fmt.Errorf("minsignclient: decode raw JSON envelope: %w", err)
		}
		return rawMap, nil
	}

	var env sdkEnvelope
	if err := json.Unmarshal(rawBytes, &env); err != nil {
		return nil, fmt.Errorf("minsignclient: decode JSON response: %w", err)
	}

	if !env.OK {
		return nil, &SDKError{
			Code:    env.Code,
			Message: env.Error,
			Raw:     string(rawBytes),
		}
	}

	if len(env.Data) == 0 || string(env.Data) == "null" {
		return map[string]any{}, nil
	}

	var dataMap map[string]any
	if err := json.Unmarshal(env.Data, &dataMap); err == nil {
		return dataMap, nil
	}

	var generic any
	if err := json.Unmarshal(env.Data, &generic); err != nil {
		return nil, fmt.Errorf("minsignclient: decode data payload: %w", err)
	}
	return map[string]any{"value": generic}, nil
}

// readCString copies a null-terminated C string from a native uintptr into a Go byte slice
// without casting uintptr back to unsafe.Pointer (100% go vet unsafeptr compliant).
func readCString(ptr uintptr) []byte {
	n, _, _ := procLstrlenA.Call(ptr)
	if n == 0 {
		return nil
	}
	buf := make([]byte, int(n))
	_, _, _ = procRtlMoveMemory.Call(uintptr(unsafe.Pointer(&buf[0])), ptr, n)
	return buf
}

func marshalPayload(payload any) (string, error) {
	if payload == nil {
		return "{}", nil
	}
	switch v := payload.(type) {
	case string:
		if strings.TrimSpace(v) == "" {
			return "{}", nil
		}
		return v, nil
	case []byte:
		if len(strings.TrimSpace(string(v))) == 0 {
			return "{}", nil
		}
		return string(v), nil
	default:
		b, err := json.Marshal(v)
		if err != nil {
			return "", fmt.Errorf("minsignclient: marshal request payload: %w", err)
		}
		if len(b) == 0 || string(b) == "null" {
			return "{}", nil
		}
		return string(b), nil
	}
}
