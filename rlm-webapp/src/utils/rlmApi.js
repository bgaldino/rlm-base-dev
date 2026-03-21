// ─────────────────────────────────────────────────────────────────────────────
// Revenue Cloud Business API helpers
// Covers ALL developer-portal API surface areas:
//   • Product Catalog Management (PCM)  /connect/pcm/...
//   • Product Discovery (CPQ)           /connect/cpq/...
//   • Product Configurator              /connect/cpq/configurator/...
//   • Salesforce Pricing (Core)         /connect/core-pricing/...
//   • Instant Pricing                   /industries/cpq/quotes/actions/get-instant-price
//   • Transaction Management            /commerce/quotes|sales-orders/actions/place
//   • Sales Transaction (new)           /connect/rev/sales-transaction/...
//   • Read Sales Transaction            /connect/revenue/transaction-management/...
//   • Asset Lifecycle                   /actions/standard/initiate{Amendment|Renewal|Cancellation}
//   • Revenue Management (Amend/Renew)  /connect/revenue-management/assets/...
//   • Eligible Promotions               /revenue/transaction-management/.../get-eligible-promotions
//   • Advanced Approvals                /connect/advanced-approvals/...
//   • Ramp Deals                        /connect/revenue-management/sales-transaction-contexts/...
//   • SOQL helpers                      /query/
// ─────────────────────────────────────────────────────────────────────────────

import { config } from '../config';

const { apiVersion } = config;

// ══════════════════════════════════════════════════════════════════════════════
// Core fetch primitives
// ══════════════════════════════════════════════════════════════════════════════

async function sfFetch(auth, path, { method = 'POST', body, params } = {}) {
  let url = `${auth.instanceUrl}/services/data/${apiVersion}${path}`;
  if (params) {
    const qs = new URLSearchParams(params);
    url += `?${qs}`;
  }

  const opts = {
    method,
    headers: {
      Authorization: `Bearer ${auth.accessToken}`,
      'Content-Type': 'application/json',
    },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const resp = await fetch(url, opts);

  if (resp.status === 401)
    throw Object.assign(new Error('Session expired. Please log in again.'), { code: 'UNAUTHORIZED' });

  if (!resp.ok) {
    let msg = `Salesforce error ${resp.status}`;
    try {
      const err = await resp.json();
      if (Array.isArray(err)) msg = err[0]?.message ?? err[0]?.errorCode ?? msg;
      else msg = err?.message ?? err?.errorCode ?? msg;
    } catch (_) {}
    throw new Error(msg);
  }

  return resp.status === 204 ? null : resp.json();
}

const post = (auth, path, body = {}) => sfFetch(auth, path, { method: 'POST', body });
const get  = (auth, path, params)    => sfFetch(auth, path, { method: 'GET', params });
const patch = (auth, path, body)     => sfFetch(auth, path, { method: 'PATCH', body });

/** SOQL query helper — returns records array (paginated if allPages=true). */
async function query(auth, soql, allPages = false) {
  const path = `/query/?q=${encodeURIComponent(soql)}`;
  let data = await get(auth, path);
  let records = [...(data.records ?? [])];
  if (allPages) {
    while (data.nextRecordsUrl) {
      const resp = await fetch(`${auth.instanceUrl}${data.nextRecordsUrl}`, {
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      });
      data = await resp.json();
      records = records.concat(data.records ?? []);
    }
  }
  return records;
}

async function queryRaw(auth, soql) {
  return get(auth, `/query/?q=${encodeURIComponent(soql)}`);
}

// ══════════════════════════════════════════════════════════════════════════════
// Product Catalog Management (PCM) — /connect/pcm/...
// The "admin" catalog API. Use for search, deep metadata, multilingual support.
// ══════════════════════════════════════════════════════════════════════════════

/**
 * List product catalogs via PCM.
 * Supports filter / pagination.  Returns { catalogs, totalCount }.
 */
export async function pcmListCatalogs(auth, { name, pageSize = 50, offset = 0 } = {}) {
  const body = { pageSize, offset };
  if (name) body.filter = { criteria: [{ property: 'name', operator: 'contains', value: name }] };
  try {
    const data = await post(auth, '/connect/pcm/catalogs', body);
    return { catalogs: data?.catalogs ?? data?.records ?? [], totalCount: data?.totalCount ?? 0 };
  } catch (e) {
    if (e.message?.includes('NOT_FOUND') || e.message?.includes('404')) return { catalogs: [], totalCount: 0 };
    throw e;
  }
}

/**
 * Get a single PCM catalog by ID.
 * Optionally pass `language` for localised labels.
 */
export async function pcmGetCatalog(auth, catalogId, { language } = {}) {
  const params = language ? { language } : undefined;
  return get(auth, `/connect/pcm/catalogs/${catalogId}`, params);
}

/**
 * List categories for a PCM catalog (top-level or all).
 */
export async function pcmListCategories(auth, catalogId, { language } = {}) {
  const params = language ? { language } : undefined;
  return get(auth, `/connect/pcm/catalogs/${catalogId}/categories`, params);
}

/**
 * Get a single PCM category by ID.
 */
export async function pcmGetCategory(auth, categoryId, { language } = {}) {
  const params = language ? { language } : undefined;
  return get(auth, `/connect/pcm/categories/${categoryId}`, params);
}

/**
 * Search / list products via PCM.
 * Returns { products, totalCount }.
 */
export async function pcmListProducts(auth, {
  catalogIds,
  searchTerm,
  productClassificationId,
  pageSize = 48,
  offset = 0,
  language,
} = {}) {
  const body = { pageSize, offset };
  if (catalogIds?.length) body.catalogIds = catalogIds;
  if (searchTerm) body.filter = { criteria: [{ property: 'name', operator: 'contains', value: searchTerm }] };
  if (productClassificationId) body.productClassificationId = productClassificationId;
  try {
    const data = await post(auth, '/connect/pcm/products', body);
    return { products: data?.products ?? data?.records ?? [], totalCount: data?.totalCount ?? 0 };
  } catch (e) {
    if (e.message?.includes('NOT_FOUND')) return { products: [], totalCount: 0 };
    throw e;
  }
}

/**
 * Get full PCM product details (attributes, specifications, selling models).
 */
export async function pcmGetProduct(auth, productId, { language, catalogSystems } = {}) {
  const params = {};
  if (language) params.language = language;
  if (catalogSystems) params.catalogSystems = catalogSystems;
  return get(auth, `/connect/pcm/products/${productId}`, Object.keys(params).length ? params : undefined);
}

/**
 * Bulk fetch PCM products by IDs.
 * POST /connect/pcm/products/bulk
 */
export async function pcmBulkGetProducts(auth, productIds) {
  return post(auth, '/connect/pcm/products/bulk', { productIds });
}

// ══════════════════════════════════════════════════════════════════════════════
// Product Discovery (CPQ) — /connect/cpq/...
// The "storefront" API for buyer-facing catalog browsing + pricing.
// ══════════════════════════════════════════════════════════════════════════════

/**
 * List active product catalogs (CPQ/Discovery).
 * Response shape: { result: [...], total: N, correlationId, limit, offSet }
 */
export async function listCatalogs(auth, { limit = 50, offset = 0 } = {}) {
  try {
    const data = await post(auth, '/connect/cpq/catalogs', {
      correlationId: `portal-${Date.now()}`,
      limit,
      offset,
      orderBy: ['name:asc'],
    });
    // API returns items in "result" array and count in "total"
    const items = data?.result ?? data?.catalogs ?? data?.records ?? [];
    console.debug('[RLM] listCatalogs →', items.length, 'catalogs', data);
    return items;
  } catch (e) {
    console.error('[RLM] listCatalogs failed:', e.message);
    if (e.message?.includes('NOT_FOUND') || e.message?.includes('404')) return [];
    throw e;
  }
}

/** Get details for a single catalog. Response shape: CPQ Base Details */
export async function getCatalog(auth, catalogId) {
  try {
    const data = await post(auth, `/connect/cpq/catalogs/${catalogId}`, {
      correlationId: `portal-${Date.now()}`,
    });
    return data?.result?.[0] ?? data?.result ?? data;
  } catch (e) {
    console.error('[RLM] getCatalog failed:', e.message);
    return null;
  }
}

/**
 * List categories for a CPQ catalog.
 * Response shape: { result: [...], total: N }
 * Each category: { id, name, catalogId, childCategories, sortOrder, isNavigational, description }
 */
export async function listCategories(auth, catalogId, { parentCategoryId, usePromotions } = {}) {
  const body = {
    catalogId,
    correlationId: `portal-${Date.now()}`,
  };
  if (parentCategoryId) body.parentCategoryId = parentCategoryId;
  if (usePromotions)    body.usePromotions    = true;
  try {
    const data = await post(auth, '/connect/cpq/categories', body);
    const items = data?.result ?? data?.categories ?? data?.records ?? [];
    console.debug('[RLM] listCategories →', items.length, 'categories for catalog', catalogId);
    return items;
  } catch (e) {
    console.error('[RLM] listCategories failed:', e.message);
    return [];
  }
}

/**
 * Get details for a single category (CPQ endpoint).
 * Response shape: CPQ Base Details
 */
export async function getCategoryDetails(auth, categoryId) {
  try {
    const data = await post(auth, `/connect/cpq/categories/${categoryId}`, {
      correlationId: `portal-${Date.now()}`,
    });
    return data?.result?.[0] ?? data?.result ?? data;
  } catch (e) {
    console.error('[RLM] getCategoryDetails failed:', e.message);
    return null;
  }
}

/**
 * List products for a catalog/category with optional pricing and qualification.
 *
 * Response shape (CPQ Base List):
 *   { result: [...products], cursor: 'MTAw...', total: N, contextId, correlationId }
 *
 * Each product in result:
 *   { id, name, productCode, productType, nodeType, configureDuringSale,
 *     description, isActive, isAssetizable, prices[], productSellingModelOptions[],
 *     categories[], catalogs[], childProducts[], attributeCategories[],
 *     additionalFields: { ProductCode, CanRamp, DecompositionScope } }
 *
 * Returns { products, nextPageToken, totalCount } for backward-compat with the page.
 */
export async function listProducts(auth, {
  catalogId,
  categoryId,
  priceBookId,
  currencyCode = 'USD',
  limit = 48,
  cursor,
  searchTerm,
  contextDefinition,
  contextMapping,
  accountId,
  enablePricing = false,
  enableQualification = false,
  qualificationProcedure,
  pricingProcedure,
  includeCatalogDetails = false,
  relatedObjectFilters,
} = {}) {
  const body = {
    limit,
    correlationId: `portal-${Date.now()}`,
    // Always request useful additional fields
    additionalFields: {
      Product2: { fields: ['ProductCode', 'CanRamp', 'DecompositionScope', 'Family'] },
    },
  };
  if (catalogId)            body.catalogId            = catalogId;
  if (categoryId)           body.categoryId           = categoryId;
  if (priceBookId)          body.priceBookId          = priceBookId;
  if (currencyCode)         body.currencyCode         = currencyCode;
  if (cursor)               body.cursor               = cursor;
  if (contextDefinition)    body.contextDefinition    = contextDefinition;
  if (contextMapping)       body.contextMapping       = contextMapping;
  if (enablePricing)        body.enablePricing        = true;
  if (pricingProcedure)     body.pricingProcedure     = pricingProcedure;
  if (enableQualification)  body.enableQualification  = true;
  if (qualificationProcedure) body.qualificationProcedure = qualificationProcedure;
  if (includeCatalogDetails)  body.includeCatalogDetails  = true;
  if (accountId)            body.userContext          = { accountId };
  if (relatedObjectFilters) body.relatedObjectFilters = relatedObjectFilters;
  if (searchTerm) body.filter = {
    criteria: [{ property: 'name', operator: 'contains', value: searchTerm }],
  };

  try {
    const data = await post(auth, '/connect/cpq/products', body);
    // API returns items in "result", pagination cursor in "cursor", count in "total"
    const products = data?.result ?? data?.products ?? data?.records ?? [];
    console.debug('[RLM] listProducts →', products.length, 'products, total:', data?.total, data);
    return {
      products,
      nextPageToken: data?.cursor ?? data?.nextPageToken ?? null,
      totalCount:    data?.total  ?? data?.totalCount   ?? null,
    };
  } catch (e) {
    console.error('[RLM] listProducts failed:', e.message, e);
    if (e.message?.includes('NOT_FOUND')) return { products: [], nextPageToken: null, totalCount: 0 };
    throw e;
  }
}

/**
 * Get full product details (selling models, attributes, price).
 * POST /connect/cpq/products/{productId}
 * Response shape: CPQ Base Details — { result: { ...productFields }, apiStatus, correlationId }
 */
export async function getProductDetails(auth, productId, {
  catalogId,
  priceBookId,
  productSellingModelId,
  accountId,
  currencyCode,
} = {}) {
  const body = { correlationId: `portal-${Date.now()}` };
  if (catalogId)             body.catalogId             = catalogId;
  if (priceBookId)           body.priceBookId           = priceBookId;
  if (productSellingModelId) body.productSellingModelId = productSellingModelId;
  if (currencyCode)          body.currencyCode          = currencyCode;
  if (accountId)             body.userContext           = { accountId };
  try {
    const data = await post(auth, `/connect/cpq/products/${productId}`, body);
    // Product Details returns a single object in result, not an array
    return data?.result ?? data;
  } catch (e) {
    console.error('[RLM] getProductDetails failed:', e.message);
    return null;
  }
}

/**
 * Global Search — find products across the catalog by search term.
 * POST /connect/cpq/products/search
 * Returns { products, nextPageToken, totalCount }
 */
export async function globalSearch(auth, {
  searchTerm,
  catalogId,
  categoryId,
  limit = 48,
  cursor,
  accountId,
  facets,
} = {}) {
  const body = {
    correlationId: `portal-${Date.now()}`,
    limit,
  };
  if (searchTerm) body.searchTerm = searchTerm;
  if (catalogId)  body.catalogId  = catalogId;
  if (categoryId) body.categoryId = categoryId;
  if (cursor)     body.cursor     = cursor;
  if (accountId)  body.userContext = { accountId };
  if (facets)     body.facets     = facets;
  try {
    const data = await post(auth, '/connect/cpq/products/search', body);
    return {
      products:      data?.result ?? data?.products ?? [],
      nextPageToken: data?.cursor ?? data?.nextPageToken ?? null,
      totalCount:    data?.total  ?? data?.totalCount   ?? null,
      facets:        data?.facets ?? [],
    };
  } catch (e) {
    console.error('[RLM] globalSearch failed:', e.message);
    return { products: [], nextPageToken: null, totalCount: 0, facets: [] };
  }
}

/**
 * Bulk fetch CPQ product details by IDs.
 * POST /connect/cpq/products/bulk
 * Returns array of product detail objects.
 */
export async function bulkGetProducts(auth, productIds, { catalogId, priceBookId } = {}) {
  const body = {
    productIds,
    correlationId: `portal-${Date.now()}`,
  };
  if (catalogId)   body.catalogId   = catalogId;
  if (priceBookId) body.priceBookId = priceBookId;
  try {
    const data = await post(auth, '/connect/cpq/products/bulk', body);
    return data?.result ?? data?.products ?? data ?? [];
  } catch (e) {
    console.error('[RLM] bulkGetProducts failed:', e.message);
    return [];
  }
}

/**
 * Qualify products for display — runs a qualification procedure to filter
 * which products a given account/context is eligible to see.
 * Returns { products: [{ productId, isQualified, ... }] }
 */
export async function qualifyProducts(auth, {
  productIds,
  accountId,
  contextDefinition,
  qualificationProcedure,
} = {}) {
  const body = {};
  if (productIds)            body.productIds           = productIds;
  if (accountId)             body.userContext          = { accountId };
  if (contextDefinition)     body.contextDefinition    = contextDefinition;
  if (qualificationProcedure) body.qualificationProcedure = qualificationProcedure;
  try {
    return await post(auth, '/connect/cpq/qualification', body);
  } catch (_) {
    return { products: [] };
  }
}

/**
 * Global product search (full-text) across catalogs.
 * POST /connect/cpq/products/search
 */
export async function searchProducts(auth, { searchTerm, catalogId, limit = 20 } = {}) {
  const body = { searchTerm, limit };
  if (catalogId) body.catalogId = catalogId;
  try {
    const data = await post(auth, '/connect/cpq/products/search', body);
    return data?.products ?? data?.records ?? [];
  } catch (_) {
    return [];
  }
}

/**
 * Guided Selection — surface products based on contextual answers.
 * POST /connect/cpq/products/guided-selection
 */
export async function guidedSelection(auth, {
  catalogId,
  answers = [],
  priceBookId,
  accountId,
} = {}) {
  const body = { answers };
  if (catalogId)   body.catalogId   = catalogId;
  if (priceBookId) body.priceBookId = priceBookId;
  if (accountId)   body.userContext = { accountId };
  return post(auth, '/connect/cpq/products/guided-selection', body);
}

// ══════════════════════════════════════════════════════════════════════════════
// Headless Product Configurator — /connect/cpq/configurator/...
//
// Requires:
//   • Org permission:  OrgPermissions.headlessConfigurator
//   • User permission: CpqSettings.UserPermissions.headlessConfiguratorUser
//
// All endpoints POST to /services/data/vXX.0/connect/cpq/configurator/<action>
// and return HTTP 201. Every response has:
//   { success: boolean, contextId?: string, errors?: [{ message, errorCode }] }
//
// Lifecycle:
//   1. headlessConfigLoad(transactionId)  — hydrate context from existing Quote
//      OR headlessConfigSet(contextMappingId, transaction)  — seed from JSON
//   2. headlessConfigGet(contextId)       — read current state
//   3. headlessConfigAddNodes / headlessConfigUpdateNodes / headlessConfigDeleteNodes
//      headlessConfigSetQuantity          — mutate in-memory context
//   4. headlessConfigSave(contextId)      — persist context back to the Quote
// ══════════════════════════════════════════════════════════════════════════════

const DEFAULT_CONFIG_OPTIONS = {
  executePricing: false,
  qualifyAllProductsInTransaction: false,
};

/**
 * Load a Headless Configurator context from an existing transaction (Quote).
 * The Quote must already have at least one QuoteLineItem on it.
 * Returns { success, contextId, errors }
 */
export async function headlessConfigLoad(auth, {
  transactionId,
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/load', {
    transactionId,
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/**
 * Get the current state of a Headless Configurator context.
 * Returns {
 *   success, contextId,
 *   transaction: {
 *     SalesTransaction: [{
 *       SalesTransactionItem: [{ id, Quantity, Product, businessObjectType, ... }]
 *     }]
 *   }
 * }
 */
export async function headlessConfigGet(auth, { contextId } = {}) {
  return post(auth, '/connect/cpq/configurator/get', { contextId });
}

/**
 * Initialise a context via a Context Mapping (alternative to Load for custom seeds).
 * transaction must be a JSON string or object describing the SalesTransaction seed,
 * e.g. { Quote: [{ businessObjectType: "Quote", id: quoteId }] }.
 * Returns { success, contextId, errors }
 */
export async function headlessConfigSet(auth, {
  contextMappingId,
  transaction,
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/set', {
    contextMappingId,
    transaction: typeof transaction === 'string' ? transaction : JSON.stringify(transaction),
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/**
 * Fetch the contextMappingId for the QuoteEntitiesMapping mapping inside the
 * RLM_SalesTransactionContext context definition.
 *
 * Uses the Connect API (two-step, mirrors rlm_context_service.py):
 *   1. GET /connect/context-definitions/RLM_SalesTransactionContext
 *      → { contextDefinitionId }
 *   2. GET /connect/context-definitions/{contextDefinitionId}/context-mappings
 *      → { contextMappings: [{ contextMappingId, developerName }] }
 *
 * Result is module-level cached after the first successful lookup so subsequent
 * calls within the same session skip the network round-trips.
 *
 * Returns the contextMappingId string, or null if the record cannot be found.
 */
const CONTEXT_DEFINITION_DEV_NAME = 'RLM_SalesTransactionContext';
const CONTEXT_MAPPING_DEV_NAME    = 'QuoteEntitiesMapping';
// undefined = not yet fetched; null = fetched but not found; string = found
let _quoteEntitiesMappingId = undefined;

export async function fetchQuoteEntitiesMappingId(auth) {
  if (_quoteEntitiesMappingId !== undefined) return _quoteEntitiesMappingId;
  try {
    // Step 1 — resolve the context definition ID by developer name
    const defResult = await get(auth, `/connect/context-definitions/${CONTEXT_DEFINITION_DEV_NAME}`);
    const defId = defResult?.contextDefinitionId;
    if (!defId) return null;

    // Step 2 — list context mappings for that definition and find QuoteEntitiesMapping
    const mappingsResult = await get(auth, `/connect/context-definitions/${defId}/context-mappings`);
    const mappings = mappingsResult?.contextMappings ?? mappingsResult?.contextMappingList ?? [];
    const match = mappings.find(m => m.developerName === CONTEXT_MAPPING_DEV_NAME);
    _quoteEntitiesMappingId = match?.contextMappingId ?? null;
  } catch (e) {
    console.warn('[rlmApi] fetchQuoteEntitiesMappingId failed:', e.message);
    _quoteEntitiesMappingId = null;
  }
  return _quoteEntitiesMappingId;
}

/**
 * Save the Headless Configurator context back to the Quote/transaction.
 * Returns { success, errors }
 */
export async function headlessConfigSave(auth, { contextId } = {}) {
  return post(auth, '/connect/cpq/configurator/save', { contextId });
}

/**
 * Add new nodes (line items / relationships) to the context.
 * addedNodes: [{
 *   path: [transactionId, ...parentIds, nodeRefId],
 *   addedObject: {
 *     id: "ref_synthetic123",          // synthetic reference ID
 *     businessObjectType: "QuoteLineItem" | "QuoteLineRelationship",
 *     Quantity: 1,
 *     Product: productId,              // for QuoteLineItem
 *     MainItem: quoteLineId,           // for QuoteLineRelationship
 *     AssociatedItem: "ref_synthetic123",
 *     ProductRelationshipType: prtId,
 *     ProductRelatedComponent: prcId,
 *   }
 * }]
 * Returns { success, errors }
 */
export async function headlessConfigAddNodes(auth, {
  contextId,
  addedNodes = [],
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/add-nodes', {
    contextId,
    addedNodes,
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/**
 * Update attributes on existing nodes in the context.
 * updatedNodes: [{
 *   path: [transactionId, ...parentIds, nodeId],
 *   updatedAttributes: { Quantity: 2, StartDate: "2025-01-01", ... }
 * }]
 * Returns { success, errors }
 */
export async function headlessConfigUpdateNodes(auth, {
  contextId,
  updatedNodes = [],
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/update-nodes', {
    contextId,
    updatedNodes,
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/**
 * Delete nodes from the context.
 * deletedNodes: [{ path: [transactionId, ...parentIds, nodeId] }]
 * Returns { success, errors }
 */
export async function headlessConfigDeleteNodes(auth, {
  contextId,
  deletedNodes = [],
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/delete-nodes', {
    contextId,
    deletedNodes,
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/**
 * Set the quantity of a specific transaction line via the configurator.
 * transactionLinePath: [transactionId, quoteLineItemId]
 * Returns { success, errors }
 */
export async function headlessConfigSetQuantity(auth, {
  contextId,
  transactionLinePath = [],
  quantity,
  configuratorOptions = {},
} = {}) {
  return post(auth, '/connect/cpq/configurator/set-product-quantity', {
    contextId,
    transactionLinePath,
    quantity,
    configuratorOptions: { ...DEFAULT_CONFIG_OPTIONS, ...configuratorOptions },
  });
}

/** List saved configurations. */
export async function listSavedConfigurations(auth, { params } = {}) {
  return get(auth, '/connect/cpq/configurator/saved-configuration', params);
}

/** Get a saved configuration by ID. */
export async function getSavedConfiguration(auth, savedConfigId) {
  return get(auth, `/connect/cpq/configurator/saved-configuration/${savedConfigId}`);
}

// ══════════════════════════════════════════════════════════════════════════════
// Salesforce Pricing (Core) — /connect/core-pricing/...
// Low-level pricing execution engine; also powers the Configurator's pricing.
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Execute the core pricing engine.
 * contextDefinitionId + contextMappingId identify the pricing procedure.
 * jsonDataString is the serialised SalesTransaction/Cart context data.
 *
 * Use getInstantPricing (below) for simpler quote-level pricing without
 * having to construct the full context JSON manually.
 */
export async function corePricing(auth, {
  contextDefinitionId,
  contextMappingId,
  jsonDataString,
  pricingProcedureId,
  configurationOverrides,
} = {}) {
  const body = {};
  if (contextDefinitionId)    body.contextDefinitionId    = contextDefinitionId;
  if (contextMappingId)       body.contextMappingId       = contextMappingId;
  if (jsonDataString)         body.jsonDataString         = jsonDataString;
  if (pricingProcedureId)     body.pricingProcedureId     = pricingProcedureId;
  if (configurationOverrides) body.configurationOverrides = configurationOverrides;
  return post(auth, '/connect/core-pricing/pricing', body);
}

/**
 * Execute pricing from context (price-context endpoint).
 * Executes the pricing procedure on an already-created context.
 */
export async function executePriceContext(auth, contextId) {
  return post(auth, `/connect/core-pricing/price-contexts/${contextId}`, {});
}

/**
 * Get the pricing waterfall for a product execution.
 * Useful for debugging price calculation steps.
 */
export async function getPricingWaterfall(auth, productName, executionId, { tagsToFilter } = {}) {
  const params = tagsToFilter ? { tagsToFilter } : undefined;
  return get(auth, `/connect/core-pricing/waterfall/${encodeURIComponent(productName)}/${executionId}`, params);
}

/** Get the active pricing recipe (procedure configuration). */
export async function getPricingRecipe(auth) {
  return get(auth, '/connect/core-pricing/recipe');
}

/** Get pricing recipe field mapping. */
export async function getPricingRecipeMapping(auth) {
  return get(auth, '/connect/core-pricing/recipe/mapping');
}

/** Sync pricing data (triggers a pricing data refresh). */
export async function syncPricingData(auth) {
  return get(auth, '/connect/core-pricing/sync/syncData');
}

// ══════════════════════════════════════════════════════════════════════════════
// Instant Pricing — /industries/cpq/quotes/actions/get-instant-price
// The recommended API for live pricing in the storefront experience.
// Accepts quote + line item records in the Commerce graph format.
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Get instant pricing for a set of quote line items.
 *
 * lineItems: [{
 *   productId, pricebookEntryId, quantity,
 *   unitPrice,     // optional override
 *   startDate, endDate,
 *   periodBoundary,   // 'Anniversary' | 'Calendar'
 *   billingFrequency, // 'Annual' | 'Monthly' etc.
 *   subscriptionTerm,
 * }]
 *
 * quoteContext: { name, pricebookId, currencyCode, opportunityId, accountId }
 *
 * Returns the Salesforce composite graph response — look for records[*].outputValues
 * for the calculated prices.
 */
export async function getInstantPricing(auth, {
  lineItems = [],
  quoteContext = {},
  contextId = '',
  correlationId,
} = {}) {
  const corrId = correlationId ?? `portal-${Date.now()}`;

  const records = [
    {
      referenceId: 'refQuote',
      record: {
        attributes: { type: 'Quote', method: quoteContext.quoteId ? 'PUT' : 'POST' },
        ...(quoteContext.quoteId    && { Id: quoteContext.quoteId }),
        Name:          quoteContext.name        ?? 'Portal Pricing Request',
        Pricebook2Id:  quoteContext.pricebookId ?? undefined,
        CurrencyIsoCode: quoteContext.currencyCode ?? 'USD',
        ...(quoteContext.opportunityId && { OpportunityId: quoteContext.opportunityId }),
      },
    },
  ];

  lineItems.forEach((li, idx) => {
    records.push({
      referenceId: `refQLI${idx + 1}`,
      record: {
        attributes: { type: 'QuoteLineItem', method: 'POST' },
        QuoteId:           '@{refQuote.id}',
        Product2Id:        li.productId,
        Quantity:          li.quantity       ?? 1,
        ...(li.pricebookEntryId && { PricebookEntryId: li.pricebookEntryId }),
        ...(li.unitPrice    != null && { UnitPrice:    li.unitPrice }),
        ...(li.startDate       && { StartDate:       li.startDate }),
        ...(li.endDate         && { EndDate:         li.endDate }),
        ...(li.periodBoundary  && { PeriodBoundary:  li.periodBoundary }),
        ...(li.billingFrequency && { BillingFrequency: li.billingFrequency }),
        ...(li.subscriptionTerm && { SubscriptionTerm: li.subscriptionTerm }),
      },
    });
  });

  return post(auth, '/industries/cpq/quotes/actions/get-instant-price', {
    correlationId: corrId,
    contextId,
    records,
  });
}

/**
 * Convenience wrapper: get instant price for a single product.
 * Returns { unitPrice, totalPrice, currency, lineItemPricing }
 */
export async function getPriceForProduct(auth, {
  productId,
  pricebookEntryId,
  pricebookId,
  quantity = 1,
  currencyCode = 'USD',
  startDate,
  endDate,
  periodBoundary = 'Anniversary',
  billingFrequency = 'Annual',
} = {}) {
  try {
    const result = await getInstantPricing(auth, {
      quoteContext: { pricebookId, currencyCode },
      lineItems: [{
        productId,
        pricebookEntryId,
        quantity,
        startDate,
        endDate,
        periodBoundary,
        billingFrequency,
      }],
    });

    // Parse composite response
    const lineItem = result?.records?.find(r => r.referenceId === 'refQLI1');
    const unitPrice  = lineItem?.outputValues?.UnitPrice  ?? lineItem?.record?.UnitPrice;
    const totalPrice = lineItem?.outputValues?.TotalPrice ?? lineItem?.record?.TotalPrice;
    return {
      unitPrice,
      totalPrice,
      currency: currencyCode,
      raw: result,
    };
  } catch (_) {
    return null;
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Transaction Management — Quotes & Orders
// /commerce/quotes/actions/place   and   /commerce/sales-orders/actions/place
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Place a Quote via the Commerce graph API.
 * cartItems: [{ productId, quantity, pricebookEntryId, unitPrice }]
 */
export async function placeQuote(auth, {
  quoteName,
  accountId,
  opportunityId,
  pricebookId,
  currencyCode = 'USD',
  cartItems = [],
  pricingPref = 'System',
} = {}) {
  const records = [
    {
      referenceId: 'refQuote',
      record: {
        attributes: { type: 'Quote', method: 'POST' },
        Name: quoteName ?? `Portal Quote — ${new Date().toLocaleDateString()}`,
        ...(accountId     && { QuoteAccountId: accountId }),
        ...(opportunityId && { OpportunityId:  opportunityId }),
        ...(pricebookId   && { Pricebook2Id:   pricebookId }),
        CurrencyIsoCode: currencyCode,
      },
    },
  ];

  cartItems.forEach((item, idx) => {
    records.push({
      referenceId: `refQLI${idx + 1}`,
      record: {
        attributes: { type: 'QuoteLineItem', method: 'POST' },
        QuoteId:    '@{refQuote.id}',
        Product2Id: item.productId,
        Quantity:   item.quantity ?? 1,
        ...(item.pricebookEntryId && { PricebookEntryId: item.pricebookEntryId }),
        ...(item.unitPrice  != null && { UnitPrice:  item.unitPrice }),
        ...(item.startDate  && { StartDate: item.startDate }),
        ...(item.endDate    && { EndDate:   item.endDate }),
      },
    });
  });

  return post(auth, '/commerce/quotes/actions/place', {
    pricingPref,
    configurationInput: 'RunAndAllowErrors',
    configurationOptions: {
      validateProductCatalog:    true,
      validateAmendRenewCancel:  false,
      executeConfigurationRules: true,
      addDefaultConfiguration:   true,
    },
    graph: { graphId: 'createQuote', records },
  });
}

/**
 * Poll an async operation status URL (returned by placeQuote, placeOrder, etc.)
 * until Status is 'Complete'/'Success', or until maxRetries is exhausted.
 *
 * statusURL  — full path as returned by the API, e.g.
 *              "/services/data/v66.0/sobjects/AsyncOperationTracker/..."
 * Returns the final tracker record, or null on timeout (caller should proceed anyway).
 */
export async function pollAsyncStatus(auth, statusURL, { maxRetries = 12, intervalMs = 1000 } = {}) {
  if (!statusURL) return null;
  const url = statusURL.startsWith('http')
    ? statusURL
    : `${auth.instanceUrl}${statusURL}`;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const resp = await fetch(url, {
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      });
      if (!resp.ok) return null;
      const data = await resp.json();
      const status = data?.Status ?? data?.status ?? '';
      if (/^(Complete|Success|Completed)$/i.test(status)) return data;
      if (/^(Error|Failed|Failure)$/i.test(status)) {
        const msg = data?.ErrorMessage ?? data?.Error ?? data?.errorMessage ?? 'Async operation failed';
        throw new Error(msg);
      }
      // Still in-progress — wait and retry
    } catch (fetchErr) {
      if (fetchErr.message && /failed/i.test(fetchErr.message)) throw fetchErr;
      // Network hiccup — try again
    }
    if (i < maxRetries - 1) await new Promise(r => setTimeout(r, intervalMs));
  }
  return null; // timed out — caller should proceed optimistically
}

/**
 * Place an Order via the Commerce graph API.
 */
export async function placeOrder(auth, {
  orderName,
  accountId,
  pricebookId,
  effectiveDate,
  cartItems = [],
  pricingPref = 'System',
} = {}) {
  const today = new Date().toISOString().slice(0, 10);
  const records = [
    {
      referenceId: 'refOrder',
      record: {
        attributes: { type: 'Order', method: 'POST' },
        Name:         orderName ?? `Portal Order — ${today}`,
        Status:       'Draft',
        EffectiveDate: effectiveDate ?? today,
        ...(accountId   && { AccountId:  accountId }),
        ...(pricebookId && { Pricebook2Id: pricebookId }),
      },
    },
    {
      referenceId: 'refOrderAction',
      record: {
        attributes: { type: 'OrderAction', method: 'POST' },
        OrderId: '@{refOrder.id}',
        Type:    'Add',
      },
    },
  ];

  cartItems.forEach((item, idx) => {
    records.push({
      referenceId: `refOLI${idx + 1}`,
      record: {
        attributes: { type: 'OrderItem', method: 'POST' },
        OrderId:       '@{refOrder.id}',
        OrderActionId: '@{refOrderAction.id}',
        Product2Id:    item.productId,
        Quantity:      item.quantity ?? 1,
        ...(item.pricebookEntryId && { PricebookEntryId: item.pricebookEntryId }),
        ...(item.unitPrice  != null && { UnitPrice:  item.unitPrice }),
        ...(item.startDate  && { StartDate: item.startDate }),
        ...(item.endDate    && { EndDate:   item.endDate }),
      },
    });
  });

  return post(auth, '/commerce/sales-orders/actions/place', {
    pricingPref,
    configurationInput: 'RunAndAllowErrors',
    configurationOptions: {
      validateProductCatalog:    true,
      validateAmendRenewCancel:  false,
      executeConfigurationRules: true,
      addDefaultConfiguration:   true,
    },
    graph: { graphId: 'createOrder', records },
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// Sales Transaction (New API) — /connect/rev/sales-transaction/...
// The v260+ (Spring '26, v66) preferred API for creating/updating quotes.
// Uses the same composite graph format as placeQuote, but with the newer
// /connect/rev/ endpoint and configurationPref object (not configurationInput).
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Place a sales transaction (Quote) using the v66 Rev API.
 *
 * Request body shape per Spring '26 docs:
 *   pricingPref           — "System" | "Skip" | "ForceRecalculate"
 *   catalogRatesPref      — "Skip" | "Run"
 *   configurationPref     — { configurationMethod, configurationOptions }
 *   taxPref               — "Skip" | "Run"
 *   graph                 — composite graph (same records[] format as Commerce API)
 *
 * cartItems: [{ productId, quantity, pricebookEntryId, unitPrice?, startDate?, endDate? }]
 */
export async function placeSalesTransaction(auth, {
  quoteName,
  accountId,
  pricebookId,
  currencyCode = 'USD',
  cartItems = [],
  pricingPref = 'System',
  catalogRatesPref = 'Skip',
  taxPref = 'Skip',
  configurationMethod = 'Skip',  // Platform only supports 'Skip'; use headlessConfigLoad separately for contextId
} = {}) {
  const records = [
    {
      referenceId: 'refQuote',
      record: {
        attributes: { type: 'Quote', method: 'POST' },
        Name: quoteName ?? `Portal Quote — ${new Date().toLocaleDateString()}`,
        CurrencyIsoCode: currencyCode,
        ...(accountId   && { AccountId:    accountId }),
        ...(pricebookId && { Pricebook2Id: pricebookId }),
      },
    },
  ];

  cartItems.forEach((item, idx) => {
    records.push({
      referenceId: `refQLI${idx + 1}`,
      record: {
        attributes: { type: 'QuoteLineItem', method: 'POST' },
        QuoteId:    '@{refQuote.id}',
        Product2Id: item.productId,
        Quantity:   item.quantity ?? 1,
        ...(item.pricebookEntryId && { PricebookEntryId: item.pricebookEntryId }),
        ...(item.unitPrice  != null && { UnitPrice:  item.unitPrice }),
        ...(item.startDate  && { StartDate: item.startDate }),
        ...(item.endDate    && { EndDate:   item.endDate }),
      },
    });
  });

  return post(auth, '/connect/rev/sales-transaction/actions/place', {
    pricingPref,
    catalogRatesPref,
    taxPref,
    configurationPref: {
      configurationMethod,
      configurationOptions: {
        validateProductCatalog:   true,
        validateAmendRenewCancel: false,
        executeConfigurationRules: true,
        addDefaultConfiguration:  true,
      },
    },
    graph: { graphId: 'createQuote', records },
  });
}

/**
 * Fetch QuoteLineItem pricing for a given Quote ID.
 * Returns a map of { [product2Id]: { unitPrice, totalPrice, currencyCode } }
 * so the configurator modal can display pricing after placeSalesTransaction.
 */
export async function fetchQuoteLinePricing(auth, quoteId) {
  const soql = `SELECT Id, Product2Id, UnitPrice, TotalPrice, Quantity, CurrencyIsoCode
                FROM QuoteLineItem WHERE QuoteId = '${quoteId}'`;
  const data = await query(auth, soql);
  const map = {};
  (data ?? []).forEach(row => {
    if (row.Product2Id) {
      map[row.Product2Id] = {
        unitPrice:  row.UnitPrice,
        totalPrice: row.TotalPrice,
        quantity:   row.Quantity,
        currency:   row.CurrencyIsoCode ?? 'USD',
      };
    }
  });
  return map;
}

/**
 * Place a supplemental transaction (change order after order submission).
 */
export async function placeSupplementalTransaction(auth, body) {
  return post(auth, '/connect/rev/sales-transaction/actions/place-supplemental-transaction', body);
}

/**
 * Read sales transaction data from a hydrated context.
 * Used to retrieve quote/order details efficiently.
 */
export async function readSalesTransaction(auth, {
  transactionId,
  transactionType,
  includeLineItems = true,
} = {}) {
  return post(auth, '/connect/revenue/transaction-management/sales-transactions/actions/read', {
    transactionId,
    transactionType,
    includeLineItems,
  });
}

/**
 * Clone a quote line item or order item (and its sub-items / configurations).
 */
export async function cloneSalesTransaction(auth, {
  sourceTransactionItemId,
  targetTransactionId,
  quantity,
} = {}) {
  return post(auth, '/connect/rev/sales-transaction/actions/clone', {
    sourceTransactionItemId,
    targetTransactionId,
    ...(quantity != null && { quantity }),
  });
}

/**
 * Get eligible promotions for line items in a quote or order.
 */
export async function getEligiblePromotions(auth, {
  transactionId,
  transactionType = 'Quote',
  lineItemIds,
} = {}) {
  return post(auth, '/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions', {
    transactionId,
    transactionType,
    ...(lineItemIds && { lineItemIds }),
  });
}

/**
 * Create an order from a quote.
 * Standard Salesforce invocable action.
 */
export async function createOrderFromQuote(auth, quoteId) {
  return post(auth, '/actions/standard/createOrderFromQuote', {
    inputs: [{ quoteRecordId: quoteId }],
  });
}

/**
 * Activate a draft order (set Status = Activated).
 */
export async function activateOrder(auth, orderId) {
  return patch(auth, `/sobjects/Order/${orderId}`, { Status: 'Activated' });
}

// ══════════════════════════════════════════════════════════════════════════════
// Asset Lifecycle — amendment, renewal, cancellation
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Initiate amendment on assets using the Revenue Management API.
 * POST /connect/revenue-management/assets/actions/amend
 */
export async function amendAssets(auth, {
  assetIds,
  amendStartDate,
  quantityChange,
  outputType = 'Order',
  opportunityId,
} = {}) {
  return post(auth, '/connect/revenue-management/assets/actions/amend', {
    assetIds,
    ...(amendStartDate && { amendStartDate }),
    ...(quantityChange != null && { quantityChange }),
    outputType,
    ...(opportunityId && { opportunityId }),
  });
}

/**
 * Initiate asset renewal via Revenue Management API.
 * POST /connect/revenue-management/assets/actions/renew
 */
export async function renewAssets(auth, {
  assetIds,
  outputType = 'Quote',
  opportunityId,
  contractId,
} = {}) {
  return post(auth, '/connect/revenue-management/assets/actions/renew', {
    assetIds,
    outputType,
    ...(opportunityId && { opportunityId }),
    ...(contractId   && { contractId }),
  });
}

/**
 * Initiate asset cancellation via Revenue Management API.
 * POST /connect/revenue-management/assets/actions/cancel
 */
export async function cancelAssets(auth, {
  assetIds,
  cancelStartDate,
  outputType = 'Quote',
  opportunityId,
  contractId,
} = {}) {
  return post(auth, '/connect/revenue-management/assets/actions/cancel', {
    assetIds,
    ...(cancelStartDate && { cancelStartDate }),
    outputType,
    ...(opportunityId && { opportunityId }),
    ...(contractId   && { contractId }),
  });
}

// ── Invocable action equivalents (legacy) ────────────────────────────────────

export async function initiateAmendment(auth, {
  assetIds,
  amendStartDate,
  quantityChange,
  outputType = 'Order',
} = {}) {
  return post(auth, '/actions/standard/initiateAmendment', {
    inputs: [{ amendAssetIds: assetIds, amendStartDate, quantityChange, amendOutputType: outputType }],
  });
}

export async function initiateRenewal(auth, {
  assetIds,
  outputType = 'Quote',
  opportunityId,
  contractId,
} = {}) {
  return post(auth, '/actions/standard/initiateRenewal', {
    inputs: [{
      renewAssetIds: assetIds,
      renewOutputType: outputType,
      ...(opportunityId && { renewOpportunityId: opportunityId }),
      ...(contractId   && { renewContractId: contractId }),
    }],
  });
}

export async function initiateCancellation(auth, {
  assetIds,
  cancelStartDate,
  outputType = 'Quote',
  opportunityId,
  contractId,
} = {}) {
  return post(auth, '/actions/standard/initiateCancellation', {
    inputs: [{
      cancelAssetIds: assetIds,
      ...(cancelStartDate && { cancelStartDate }),
      cancelOutputType: outputType,
      ...(opportunityId && { cancelOpportunityId: opportunityId }),
      ...(contractId   && { cancelContractId: contractId }),
    }],
  });
}

/** Update pricing source on an asset (set to LastTransaction for renewals). */
export async function updateAssetPricingSource(auth, assetId, pricingSource = 'LastTransaction') {
  return patch(auth, `/sobjects/Asset/${assetId}`, { PricingSource: pricingSource });
}

/** Create/update asset from an order. */
export async function createAssetFromOrder(auth, orderId) {
  return post(auth, '/actions/standard/createOrUpdateAssetFromOrder', {
    inputs: [{ orderId }],
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// Ramp Deals — /connect/revenue-management/sales-transaction-contexts/...
// ══════════════════════════════════════════════════════════════════════════════

/** Create a ramp deal for a line item. */
export async function createRampDeal(auth, transactionLineId, rampData) {
  return post(
    auth,
    `/connect/revenue-management/sales-transaction-contexts/${transactionLineId}/actions/ramp-deal-create`,
    rampData,
  );
}

/** Update an existing ramp deal. */
export async function updateRampDeal(auth, contextId, rampData) {
  return post(
    auth,
    `/connect/revenue-management/sales-transaction-contexts/${contextId}/actions/ramp-deal-update`,
    rampData,
  );
}

/** Delete a ramp deal. */
export async function deleteRampDeal(auth, transactionLineId) {
  return post(
    auth,
    `/connect/revenue-management/sales-transaction-contexts/${transactionLineId}/actions/ramp-deal-delete`,
    {},
  );
}

/** View ramp deal for a line item. */
export async function viewRampDeal(auth, transactionLineId, { transactionId, transactionLineItemId } = {}) {
  const params = {};
  if (transactionId)      params.transactionId     = transactionId;
  if (transactionLineItemId) params.transactionLineId = transactionLineItemId;
  return get(
    auth,
    `/connect/revenue-management/sales-transaction-contexts/${transactionLineId}/actions/ramp-deal-view`,
    params,
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// Advanced Approvals — /connect/advanced-approvals/...
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Preview approval levels for a record before submitting.
 * Returns the approval process steps that would be triggered.
 */
export async function previewApproval(auth, { recordId, recordType, processName } = {}) {
  return post(auth, '/connect/advanced-approvals/approval-submission/preview', {
    recordId,
    ...(recordType  && { recordType }),
    ...(processName && { processName }),
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SOQL & standard REST helpers
// ══════════════════════════════════════════════════════════════════════════════

/** Fetch the standard (IsStandard) pricebook for this org. */
export async function fetchStandardPricebook(auth) {
  try {
    const records = await query(auth, 'SELECT Id, Name FROM Pricebook2 WHERE IsStandard = true LIMIT 1');
    return records[0] ?? null;
  } catch (_) {
    return null;
  }
}

/**
 * Fetch PricebookEntry records for products in a specific pricebook.
 * Returns a map of { [productId]: entry }.
 */
export async function fetchPricebookEntries(auth, productIds, pricebookId) {
  if (!productIds?.length || !pricebookId) return {};
  const ids  = productIds.map(id => `'${id}'`).join(',');
  const soql = `SELECT Id, Product2Id, UnitPrice, CurrencyIsoCode
                FROM PricebookEntry
                WHERE Product2Id IN (${ids})
                  AND Pricebook2Id = '${pricebookId}'
                  AND IsActive = true`;
  try {
    const records = await query(auth, soql);
    const map = {};
    for (const r of records) map[r.Product2Id] = r;
    return map;
  } catch (_) {
    return {};
  }
}

/**
 * Fetch standard pricebook entries for a list of product IDs.
 * Returns a map of { [productId]: entry }.
 */
export async function fetchStandardPrices(auth, productIds) {
  if (!productIds?.length) return {};
  const ids  = productIds.map(id => `'${id}'`).join(',');
  try {
    const records = await query(auth,
      `SELECT Id, Product2Id, UnitPrice, CurrencyIsoCode
       FROM PricebookEntry
       WHERE Product2Id IN (${ids})
         AND Pricebook2.IsStandard = true
         AND IsActive = true`
    );
    const map = {};
    for (const r of records) map[r.Product2Id] = r;
    return map;
  } catch (_) {
    return {};
  }
}

/** Fetch org info. */
export async function fetchOrgInfo(auth) {
  try {
    const records = await query(auth, 'SELECT Id, Name, OrganizationType FROM Organization LIMIT 1');
    return records[0] ?? null;
  } catch (_) {
    return null;
  }
}

/**
 * Fetch active org branding from the BrandingSet that matches the org name.
 * Returns { companyName, logoPath, brandColor, headerBgColor } or null on failure.
 * logoPath is a relative SF path like /file-asset/... — prepend auth.instanceUrl.
 */
export async function fetchOrgBranding(auth) {
  try {
    // 1. Org name
    const orgRecords = await query(auth, 'SELECT Id, Name FROM Organization LIMIT 1');
    const companyName = orgRecords[0]?.Name ?? null;

    // 2. All BrandingSets — pick the one whose MasterLabel matches the org name,
    //    falling back to DeveloperName containing the org name, then the first record.
    const bsRecords = await query(
      auth,
      'SELECT Id, DeveloperName, MasterLabel FROM BrandingSet ORDER BY CreatedDate ASC LIMIT 20'
    );
    const orgKey = (companyName ?? '').toLowerCase().replace(/\s+/g, '');
    const match =
      bsRecords.find(b => b.MasterLabel?.toLowerCase().replace(/\s+/g, '') === orgKey) ??
      bsRecords.find(b => b.DeveloperName?.toLowerCase().includes(orgKey)) ??
      bsRecords[0] ??
      null;

    if (!match) return { companyName, logoPath: null, brandColor: null, headerBgColor: null };

    // 3. Properties for the matched BrandingSet
    const bspRecords = await query(
      auth,
      `SELECT PropertyName, PropertyValue FROM BrandingSetProperty WHERE BrandingSetId = '${match.Id}'`
    );
    const props = Object.fromEntries(bspRecords.map(r => [r.PropertyName, r.PropertyValue]));

    return {
      companyName,
      brandingSetName: match.MasterLabel,
      logoPath:        props.BRAND_IMAGE    ?? null,   // e.g. /file-asset/RLM_quantumBit_rectangle?v=1
      brandColor:      props.BRAND_COLOR    ?? null,   // e.g. #173a67
      headerBgColor:   props.HEADER_BACKGROUND_COLOR ?? null,
    };
  } catch (_) {
    return null;
  }
}

/**
 * Fetches a branding logo from Salesforce and returns a blob object URL
 * suitable for use as an <img src>.  The caller is responsible for calling
 * URL.revokeObjectURL() when the image is no longer needed.
 *
 * logoPath is a /file-asset/<DeveloperName> path from BrandingSetProperty.
 * We resolve it via the ContentAsset → ContentVersion → VersionData REST chain,
 * which works with Bearer token auth and requires no CORS or CSP changes.
 */
export async function fetchBrandLogoUrl(auth, logoPath) {
  if (!logoPath) return null;
  try {
    // Extract developer name from path like /file-asset/RLM_quantumBit_rectangle?v=1
    const devName = logoPath.replace(/^\/file-asset\//, '').replace(/\?.*$/, '');

    // 1. ContentAsset → ContentDocumentId
    const assetRecords = await query(
      auth,
      `SELECT ContentDocumentId FROM ContentAsset WHERE DeveloperName = '${devName}' LIMIT 1`
    );
    const docId = assetRecords[0]?.ContentDocumentId;
    if (!docId) return null;

    // 2. ContentVersion (latest) → Id
    const versionRecords = await query(
      auth,
      `SELECT Id FROM ContentVersion WHERE ContentDocumentId = '${docId}' AND IsLatest = true LIMIT 1`
    );
    const versionId = versionRecords[0]?.Id;
    if (!versionId) return null;

    // 3. Fetch binary via VersionData — works with Bearer token, no CORS needed
    const resp = await fetch(
      `${auth.instanceUrl}/services/data/${apiVersion}/sobjects/ContentVersion/${versionId}/VersionData`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    );
    if (!resp.ok) return null;
    const blob = await resp.blob();
    return URL.createObjectURL(blob);
  } catch (_) {
    return null;
  }
}

/** Generic SOQL query (exported for custom use). */
export { query as soqlQuery, queryRaw as soqlQueryRaw };

// ══════════════════════════════════════════════════════════════════════════════
// Formatting utilities
// ══════════════════════════════════════════════════════════════════════════════

export function formatCurrency(amount, currency = 'USD') {
  if (amount == null || amount === '') return null;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency ?? 'USD',
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

export function formatPercent(value) {
  if (value == null) return '—';
  return `${(value * 100).toFixed(1)}%`;
}
