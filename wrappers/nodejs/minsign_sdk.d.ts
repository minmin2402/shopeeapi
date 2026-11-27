/**
 * Official TypeScript Definitions for MinSign Native Universal SDK v2.0.0 (minsign_sdk.dll).
 * Covers all 44 production APIs across 8 Shopee regions (VN, ID, TH, MY, PH, SG, TW, BR).
 */

export type ShopeeCountry = "VN" | "ID" | "TH" | "MY" | "PH" | "SG" | "TW" | "BR" | (string & {});
export type SignClientType = "app" | "web";
export type CookieInput = string | Record<string, unknown> | Array<Record<string, unknown>>;
export type JsonObject = Record<string, any>;

export interface MinSignClientOptions {
  /** Required X-API-Key obtained from https://vip-sign.minmintool.site */
  apiKey: string;
  /** Optional explicit path to minsign_sdk.dll or libminsign_sdk.so */
  dllPath?: string | null;
  /** Cloud signer endpoint (default: "https://vip-sign.minmintool.site") */
  signerUrl?: string;
  /** Local encrypted device vault JSON path */
  vaultFilePath?: string;
  /** Optional vault encryption passphrase */
  vaultSecret?: string;
  /** Default Shopee country code (default: "VN") */
  defaultCountry?: ShopeeCountry;
  /** HTTP timeout in milliseconds (default: 25000) */
  timeoutMs?: number;
}

export interface VersionInfo {
  version: string;
  sdk?: string;
  [key: string]: any;
}

export interface BindAccountDeviceRequest {
  cookie?: CookieInput;
  accountId?: string;
  country?: ShopeeCountry;
  deviceId?: string;
}

export interface SignRawRequest {
  url: string;
  body?: string;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  accountId?: string;
  deviceId?: string;
  brand?: string;
  fetchLive?: boolean;
  includeRiskTokens?: boolean;
  attachRiskHeaders?: boolean;
  forceRefreshRisk?: boolean;
  secToken?: string;
  /** Signing mode: "app" (mobile UniDBG, default) or "web" (Chrome 131 Web Signer) */
  clientType?: SignClientType;
}

export interface SignWebRequest {
  url: string;
  body?: string;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  accountId?: string;
  deviceId?: string;
  proxy?: string;
  fetchLive?: boolean;
}

export interface GetRiskTokenRequest {
  country?: ShopeeCountry;
  cookie?: CookieInput;
  accountId?: string;
  deviceId?: string;
  brand?: string;
  forceRefresh?: boolean;
  secToken?: string;
}

export interface ResolveShopeeUrlRequest {
  url?: string;
  shopId?: string | number;
  itemId?: string | number;
  country?: ShopeeCountry;
  proxy?: string;
  followRedirect?: boolean;
}

export interface ResolveShopeeUrlResponse {
  urlType: string;
  country: string;
  domain: string;
  shopId: string;
  itemId: string;
  postId: string;
  sessionId: string;
  username: string;
  canonicalProductUrl: string;
  resolvedUrl: string;
  [key: string]: any;
}

export interface GetProductDetailRequest {
  productUrl?: string;
  shopId?: string | number;
  itemId?: string | number;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
  accountId?: string;
  includeShop?: boolean;
}

export interface BatchProductItemTarget {
  shopId?: string | number;
  itemId?: string | number;
  productUrl?: string;
}

export interface BatchGetProductDetailsRequest {
  items?: BatchProductItemTarget[];
  productUrls?: string[];
  country?: ShopeeCountry;
  cookie?: CookieInput;
  cookies?: CookieInput[];
  proxy?: string;
  proxies?: string[];
  /** Bounded worker concurrency (default: 5, max: 16) */
  concurrency?: number;
}

export interface BatchGetProductDetailsResponse {
  total: number;
  succeeded: number;
  failed: number;
  elapsedMs: number;
  results: JsonObject[];
  [key: string]: any;
}

export interface GetProductRatingsRequest {
  productUrl?: string;
  shopId?: string | number;
  itemId?: string | number;
  limit?: number;
  offset?: number;
  filter?: number;
  type?: number;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  proxy?: string;
}

export interface GetFlashSaleItemsRequest {
  promotionId?: number;
  limit?: number;
  offset?: number;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  proxy?: string;
}

export interface GetRecommendProductsRequest {
  bundle?: string;
  shopId?: string | number;
  itemId?: string | number;
  limit?: number;
  offset?: number;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  proxy?: string;
}

export interface GetSearchSuggestionsRequest {
  keyword: string;
  limit?: number;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  proxy?: string;
}

export interface GetShopOverviewRequest {
  shopUrl?: string;
  shopId?: string | number;
  username?: string;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface GetShopProductsRequest {
  shopId?: string | number;
  shopUrl?: string;
  limit?: number;
  offset?: number;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface GetShopNewestProductsRequest {
  shopUrl?: string;
  shopId?: string | number;
  username?: string;
  limit?: number;
  offset?: number;
  sinceItemId?: string | number;
  sinceTimestamp?: number;
  withinHours?: number;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
  accountId?: string;
}

export interface GetShopCategoriesRequest {
  shopId?: string | number;
  shopUrl?: string;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface GetShopVouchersRequest {
  shopId?: string | number;
  shopUrl?: string;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface SearchProductsRequest {
  keyword: string;
  country?: ShopeeCountry;
  sortBy?: string;
  page?: number;
  limit?: number;
  proxy?: string;
  cookie?: CookieInput;
}

export interface SearchProductsByImageRequest {
  cookie: CookieInput;
  imagePath?: string;
  imageBase64?: string;
  imageUrl?: string;
  imageId?: string;
  productUrl?: string;
  shopId?: string | number;
  itemId?: string | number;
  country?: ShopeeCountry;
  resultType?: string;
  offset?: number;
  limit?: number;
  boundingBox?: string;
  autoDetectBox?: boolean;
  forceUpload?: boolean;
  proxy?: string;
  accountId?: string;
  deviceId?: string;
}

export interface GetImageBoundingBoxRequest {
  imagePath?: string;
  imageBase64?: string;
  imageUrl?: string;
  country?: ShopeeCountry;
  imageSource?: string;
  proxy?: string;
}

export interface GetCategoryTreeRequest {
  country?: ShopeeCountry;
  proxy?: string;
}

export interface GetAccountProfileRequest {
  cookie: CookieInput;
  country?: ShopeeCountry;
  proxy?: string;
  accountId?: string;
  deviceId?: string;
}

export interface GetAccountProfileResponse {
  alive: boolean;
  userId: string | number;
  shopId: string | number;
  username: string;
  emailVerified: boolean;
  phoneVerified: boolean;
  isSeller: boolean;
  portrait: string;
  raw?: JsonObject;
  [key: string]: any;
}

export interface GetCartSummaryRequest {
  cookie: CookieInput;
  country?: ShopeeCountry;
  proxy?: string;
  accountId?: string;
  deviceId?: string;
}

export interface ClaimShopVoucherRequest {
  voucherCode?: string;
  promotionId?: number;
  signature?: string;
  shopId?: string | number;
  cookie: CookieInput;
  country?: ShopeeCountry;
  proxy?: string;
  accountId?: string;
  deviceId?: string;
}

export interface UploadShopeeVideoRequest {
  videoPath: string;
  cookie: CookieInput;
  caption?: string;
  hashtags?: string[];
  products?: JsonObject[];
  productLinks?: string[];
  coverPath?: string;
  postMode?: string;
  proxy?: string;
  country?: ShopeeCountry;
  accountId?: string;
  mutateMp4?: boolean;
}

export interface PrecheckVideoUploadRequest {
  cookie: CookieInput;
  proxy?: string;
  country?: ShopeeCountry;
  accountId?: string;
}

export interface GetAffiliateProductsRequest {
  cookie: CookieInput;
  keyword?: string;
  pageOffset?: number;
  pageLimit?: number;
  proxy?: string;
  country?: ShopeeCountry;
}

export interface GetAffiliateOfferListRequest {
  keyword?: string;
  shopId?: string | number;
  listType?: number;
  sortType?: number;
  pageOffset?: number;
  pageLimit?: number;
  cookie: CookieInput;
  country?: ShopeeCountry;
  proxy?: string;
}

export interface GetAffiliateCommissionReportRequest {
  startTime?: number;
  endTime?: number;
  pageOffset?: number;
  pageLimit?: number;
  cookie: CookieInput;
  country?: ShopeeCountry;
  proxy?: string;
}

export interface ConvertAffiliateLinkRequest {
  url: string;
  cookie: CookieInput;
  subId1?: string;
  subId2?: string;
  subId3?: string;
  subId4?: string;
  subId5?: string;
  subIds?: string[];
  country?: ShopeeCountry;
  proxy?: string;
  cleanProductUrl?: boolean;
  resolveShortLinks?: boolean;
  signRequest?: boolean;
  accountId?: string;
  deviceId?: string;
}

export interface BatchConvertAffiliateLinksRequest {
  cookie: CookieInput;
  urls?: string[];
  items?: JsonObject[];
  subId1?: string;
  subId2?: string;
  subId3?: string;
  subId4?: string;
  subId5?: string;
  subIds?: string[];
  country?: ShopeeCountry;
  proxy?: string;
  cleanProductUrl?: boolean;
  resolveShortLinks?: boolean;
  signRequest?: boolean;
  batchSize?: number;
  accountId?: string;
  deviceId?: string;
}

export interface MutateMp4FingerprintRequest {
  inputPath: string;
  outputPath?: string;
  inPlace?: boolean;
}

export interface BuffVideoViewRequest {
  videoUrl?: string;
  postId?: string;
  proxy?: string;
  cookie?: CookieInput;
  watchSeconds?: number;
  country?: ShopeeCountry;
  accountId?: string;
  deviceId?: string;
  simulateWait?: boolean;
}

export interface BuffVideoBatchRequest {
  videoUrl?: string;
  postId?: string;
  targetViews?: number;
  concurrency?: number;
  proxies?: string[];
  cookies?: CookieInput[];
  watchSeconds?: number;
  country?: ShopeeCountry;
}

export interface GetVideoDetailRequest {
  videoUrl?: string;
  postId?: string;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface GetShopVideosRequest {
  shopUrl?: string;
  shopId?: string | number;
  username?: string;
  userId?: string | number;
  limit?: number;
  pageToken?: string;
  maxPages?: number;
  includeProductVideos?: boolean;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
  accountId?: string;
}

export interface GetChannelAndHashtagVideosRequest {
  mode?: string;
  requestUserId?: string;
  hashtagId?: string;
  limit?: number;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
}

export interface GetLiveSessionDetailRequest {
  liveUrl?: string;
  sessionId?: string | number;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
  accountId?: string;
  deviceId?: string;
}

export interface GetLiveBagItemsRequest {
  liveUrl?: string;
  sessionId?: string | number;
  offset?: number;
  limit?: number;
  country?: ShopeeCountry;
  cookie?: CookieInput;
  proxy?: string;
}

export interface BuffLiveViewRequest {
  liveUrl?: string;
  sessionId?: string | number;
  proxy?: string;
  cookie?: CookieInput;
  watchSeconds?: number;
  simulateWait?: boolean;
  connectWs?: boolean;
  pullStream?: boolean;
  reportHeartbeat?: boolean;
  sendExit?: boolean;
  sendLike?: boolean;
  likeCount?: number;
  bypassStreamProxy?: boolean;
  streamLiteMode?: boolean;
  country?: ShopeeCountry;
  accountId?: string;
  deviceId?: string;
  fromSource?: string;
}

export interface BuffLiveBatchRequest {
  liveUrl?: string;
  sessionId?: string | number;
  targetViews?: number;
  concurrency?: number;
  proxies?: string[];
  cookies?: CookieInput[];
  watchSeconds?: number;
  simulateWait?: boolean;
  connectWs?: boolean;
  pullStream?: boolean;
  reportHeartbeat?: boolean;
  sendExit?: boolean;
  sendLike?: boolean;
  likeCount?: number;
  bypassStreamProxy?: boolean;
  streamLiteMode?: boolean;
  staggerMs?: number;
  country?: ShopeeCountry;
  fromSource?: string;
}

export interface ExecuteSignedRequestInput {
  url: string;
  method?: string;
  body?: unknown;
  proxy?: string;
  cookie?: CookieInput;
  country?: ShopeeCountry;
  accountId?: string;
  deviceId?: string;
  brand?: string;
  includeRiskTokens?: boolean;
  attachRiskHeaders?: boolean;
  forceRefreshRisk?: boolean;
  secToken?: string;
  customHeaders?: Record<string, string>;
  /** Signing mode: "app" (default) or "web" (Chrome 131 Web Signer) */
  clientType?: SignClientType;
}

export type MinSignAction =
  | "check_api_key"
  | "bind_account_device"
  | "list_local_devices"
  | "remove_local_device"
  | "sign_raw"
  | "sign_web"
  | "get_risk_token"
  | "resolve_shopee_url"
  | "get_product_detail"
  | "batch_get_product_details"
  | "get_product_ratings"
  | "get_flash_sale_items"
  | "get_recommend_products"
  | "get_search_suggestions"
  | "get_shop_overview"
  | "get_shop_products"
  | "get_shop_newest_products"
  | "get_shop_categories"
  | "get_shop_vouchers"
  | "search_products"
  | "search_products_by_image"
  | "get_image_bounding_box"
  | "get_category_tree"
  | "get_account_profile"
  | "get_cart_summary"
  | "claim_shop_voucher"
  | "upload_shopee_video"
  | "precheck_video_upload"
  | "get_affiliate_products"
  | "get_affiliate_offer_list"
  | "get_affiliate_commission_report"
  | "convert_affiliate_link"
  | "batch_convert_affiliate_links"
  | "mutate_mp4_fingerprint"
  | "buff_video_view"
  | "buff_video_batch"
  | "get_video_detail"
  | "get_shop_videos"
  | "get_channel_and_hashtag_videos"
  | "get_live_session_detail"
  | "get_live_bag_items"
  | "buff_live_view"
  | "buff_live_batch"
  | "get_affiliate_user_profile"
  | "get_mcn_partnership_status"
  | "reply_mcn_invitation"
  | "get_mcn_kol_partnerships"
  | "send_mcn_partnership_invitation"
  | "manage_mcn_partnership"
  | "get_mcn_analytics"
  | "get_affiliate_payment_tax"
  | "get_affiliate_click_report"
  | "get_affiliate_billing"
  | "execute_signed_request"
  | (string & {});

export declare class MinSignClient {
  readonly initInfo: JsonObject;

  constructor(options: MinSignClientOptions);

  /** Universal async action dispatcher calling MinSign_Invoke on a worker thread. */
  invoke<T = JsonObject>(action: MinSignAction, payload?: JsonObject | string): Promise<T>;

  // Group 1: Key Management, Local Device Vault & Core Signing (App + Web)
  version(): VersionInfo;
  checkApiKey(): Promise<JsonObject>;
  bindAccountDevice(req: BindAccountDeviceRequest): Promise<JsonObject>;
  listLocalDevices(): Promise<JsonObject>;
  removeLocalDevice(accountKey: string): Promise<JsonObject>;
  signRaw(req: SignRawRequest): Promise<JsonObject>;
  signWeb(req: SignWebRequest): Promise<JsonObject>;
  getRiskToken(req?: GetRiskTokenRequest): Promise<JsonObject>;

  // Group 2: Products, Shops, Vouchers, Search, Recommendations & URL Tools
  resolveShopeeUrl(req: ResolveShopeeUrlRequest): Promise<ResolveShopeeUrlResponse>;
  getProductDetail(req: GetProductDetailRequest): Promise<JsonObject>;
  batchGetProductDetails(req: BatchGetProductDetailsRequest): Promise<BatchGetProductDetailsResponse>;
  getProductRatings(req: GetProductRatingsRequest): Promise<JsonObject>;
  getFlashSaleItems(req?: GetFlashSaleItemsRequest): Promise<JsonObject>;
  getRecommendProducts(req?: GetRecommendProductsRequest): Promise<JsonObject>;
  getSearchSuggestions(req: GetSearchSuggestionsRequest): Promise<JsonObject>;
  getShopOverview(req: GetShopOverviewRequest): Promise<JsonObject>;
  getShopProducts(req: GetShopProductsRequest): Promise<JsonObject>;
  getShopNewestProducts(req: GetShopNewestProductsRequest): Promise<JsonObject>;
  getShopVideos(req: GetShopVideosRequest): Promise<JsonObject>;
  getShopCategories(req: GetShopCategoriesRequest): Promise<JsonObject>;
  getShopVouchers(req: GetShopVouchersRequest): Promise<JsonObject>;
  searchProducts(req: SearchProductsRequest): Promise<JsonObject>;
  searchProductsByImage(req: SearchProductsByImageRequest): Promise<JsonObject>;
  getImageBoundingBox(req: GetImageBoundingBoxRequest): Promise<JsonObject>;
  getCategoryTree(req?: GetCategoryTreeRequest): Promise<JsonObject>;

  // Group 3: Account, Cart & Voucher Actions
  getAccountProfile(req: GetAccountProfileRequest): Promise<GetAccountProfileResponse>;
  getCartSummary(req: GetCartSummaryRequest): Promise<JsonObject>;
  claimShopVoucher(req: ClaimShopVoucherRequest): Promise<JsonObject>;

  // Group 4: Shopee Video Studio & Affiliate Marketing
  uploadShopeeVideo(req: UploadShopeeVideoRequest): Promise<JsonObject>;
  precheckVideoUpload(req: PrecheckVideoUploadRequest): Promise<JsonObject>;
  getAffiliateProducts(req: GetAffiliateProductsRequest): Promise<JsonObject>;
  getAffiliateOfferList(req: GetAffiliateOfferListRequest): Promise<JsonObject>;
  getAffiliateCommissionReport(req: GetAffiliateCommissionReportRequest): Promise<JsonObject>;
  convertAffiliateLink(req: ConvertAffiliateLinkRequest): Promise<JsonObject>;
  batchConvertAffiliateLinks(req: BatchConvertAffiliateLinksRequest): Promise<JsonObject>;
  mutateMp4Fingerprint(req: MutateMp4FingerprintRequest): Promise<JsonObject>;

  // Group 5: Shopee Video Discovery & View Booster
  buffVideoView(req: BuffVideoViewRequest): Promise<JsonObject>;
  buffVideoBatch(req: BuffVideoBatchRequest): Promise<JsonObject>;
  getVideoDetail(req: GetVideoDetailRequest): Promise<JsonObject>;
  getChannelAndHashtagVideos(req: GetChannelAndHashtagVideosRequest): Promise<JsonObject>;

  // Group 6: Shopee Live Commerce & Viewer Pipeline
  getLiveSessionDetail(req: GetLiveSessionDetailRequest): Promise<JsonObject>;
  getLiveBagItems(req: GetLiveBagItemsRequest): Promise<JsonObject>;
  buffLiveView(req: BuffLiveViewRequest): Promise<JsonObject>;
  buffLiveBatch(req: BuffLiveBatchRequest): Promise<JsonObject>;

  // Group 8: Shopee MCN, Accept/Reply Invitations & Affiliate Center (v2.1.0)
  getAffiliateUserProfile(req: JsonObject): Promise<JsonObject>;
  getMcnPartnershipStatus(req: JsonObject): Promise<JsonObject>;
  replyMcnInvitation(req: JsonObject): Promise<JsonObject>;
  getMcnKolPartnerships(req: JsonObject): Promise<JsonObject>;
  sendMcnPartnershipInvitation(req: JsonObject): Promise<JsonObject>;
  manageMcnPartnership(req: JsonObject): Promise<JsonObject>;
  getMcnAnalytics(req: JsonObject): Promise<JsonObject>;
  getAffiliatePaymentTax(req: JsonObject): Promise<JsonObject>;
  getAffiliateClickReport(req: JsonObject): Promise<JsonObject>;
  getAffiliateBilling(req: JsonObject): Promise<JsonObject>;

  // Group 7: Universal Signed HTTP Gateway (App + Web)
  executeSignedRequest(req: ExecuteSignedRequestInput): Promise<JsonObject>;
}
