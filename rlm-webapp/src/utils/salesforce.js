// ─────────────────────────────────────────────────────────────────────────────
// Salesforce REST API helpers
// All functions accept { accessToken, instanceUrl } from getAuth().
// ─────────────────────────────────────────────────────────────────────────────

import { config } from '../config';

const { apiVersion } = config;

// ── Core fetch wrapper ────────────────────────────────────────────────────────

async function sfFetch(instanceUrl, accessToken, path, options = {}) {
  const url = `${instanceUrl}/services/data/${apiVersion}${path}`;
  const resp = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (resp.status === 401) {
    throw Object.assign(new Error('Session expired. Please log in again.'), { code: 'UNAUTHORIZED' });
  }
  if (!resp.ok) {
    const body = await resp.json().catch(() => [{}]);
    const msg  = Array.isArray(body) ? body[0]?.message : body?.message;
    throw new Error(msg ?? `Salesforce error ${resp.status}`);
  }

  // 204 No Content
  if (resp.status === 204) return null;
  return resp.json();
}

/** Run a SOQL query and return the records array. Handles nextRecordsUrl pagination. */
async function query(instanceUrl, accessToken, soql, allPages = false) {
  const encoded = encodeURIComponent(soql);
  let data = await sfFetch(instanceUrl, accessToken, `/query/?q=${encoded}`);
  let records = [...data.records];

  if (allPages) {
    while (data.nextRecordsUrl) {
      // nextRecordsUrl is a full path like /services/data/vXX.0/query/01g...
      data = await fetch(`${instanceUrl}${data.nextRecordsUrl}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      }).then(r => r.json());
      records = records.concat(data.records);
    }
  }

  return records;
}

/** Run a SOQL query, returning the full QueryResult (includes totalSize). */
async function queryRaw(instanceUrl, accessToken, soql) {
  const encoded = encodeURIComponent(soql);
  return sfFetch(instanceUrl, accessToken, `/query/?q=${encoded}`);
}

// ── Product Catalog ───────────────────────────────────────────────────────────

/**
 * Fetch the list of Product Catalogs (Revenue Cloud).
 * Falls back gracefully if the object doesn't exist.
 */
export async function fetchProductCatalogs(auth) {
  try {
    return await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, Name, Status, Description
       FROM ProductCatalog
       WHERE Status = 'Active'
       ORDER BY Name
       LIMIT 50`,
    );
  } catch (e) {
    if (e.message?.includes('sObject type')) return [];
    throw e;
  }
}

/**
 * Fetch products, optionally filtered by search term and/or family.
 */
export async function fetchProducts(auth, { search = '', family = '', offset = 0, limit = 48 } = {}) {
  let where = 'IsActive = true';
  if (search) {
    const s = search.replace(/'/g, "\\'");
    where += ` AND (Name LIKE '%${s}%' OR ProductCode LIKE '%${s}%' OR Description LIKE '%${s}%')`;
  }
  if (family) {
    where += ` AND Family = '${family.replace(/'/g, "\\'")}'`;
  }

  const soql = `SELECT Id, Name, ProductCode, Description, Family, IsActive, StockKeepingUnit,
                       LastModifiedDate
                FROM Product2
                WHERE ${where}
                ORDER BY Name
                LIMIT ${limit}
                OFFSET ${offset}`;

  const result = await queryRaw(auth.instanceUrl, auth.accessToken, soql);
  return { records: result.records, totalSize: result.totalSize, done: result.done };
}

/** Fetch all distinct product families for the filter dropdown. */
export async function fetchProductFamilies(auth) {
  try {
    const records = await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Family FROM Product2 WHERE IsActive = true AND Family != null GROUP BY Family ORDER BY Family`,
    );
    return records.map(r => r.Family).filter(Boolean);
  } catch (_) {
    return [];
  }
}

/** Fetch price book entries for a product (standard price book). */
export async function fetchProductPricing(auth, productId) {
  try {
    return await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, UnitPrice, CurrencyIsoCode, Pricebook2.Name, Pricebook2.IsStandard,
              IsActive
       FROM PricebookEntry
       WHERE Product2Id = '${productId}'
         AND IsActive = true
       ORDER BY Pricebook2.IsStandard DESC, UnitPrice ASC
       LIMIT 10`,
    );
  } catch (_) {
    return [];
  }
}

/** Fetch standard pricebook entries for products (used for catalog price display). */
export async function fetchStandardPrices(auth, productIds) {
  if (!productIds.length) return {};
  const ids = productIds.map(id => `'${id}'`).join(',');
  try {
    const records = await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, Product2Id, UnitPrice, CurrencyIsoCode
       FROM PricebookEntry
       WHERE Product2Id IN (${ids})
         AND Pricebook2.IsStandard = true
         AND IsActive = true`,
    );
    return Object.fromEntries(records.map(r => [r.Product2Id, r]));
  } catch (_) {
    return {};
  }
}

// ── Quotes ────────────────────────────────────────────────────────────────────

export async function fetchQuotes(auth, { search = '', status = '', offset = 0, limit = 50 } = {}) {
  let where = '';
  const conditions = [];
  if (search) {
    const s = search.replace(/'/g, "\\'");
    conditions.push(`(Name LIKE '%${s}%')`);
  }
  if (status) {
    conditions.push(`Status = '${status.replace(/'/g, "\\'")}'`);
  }
  if (conditions.length) where = `WHERE ${conditions.join(' AND ')}`;

  const soql = `SELECT Id, Name, Status, OpportunityId, Opportunity.Name,
                       AccountId, Account.Name,
                       TotalPrice, GrandTotal, ExpirationDate,
                       LastModifiedDate, CreatedDate,
                       IsSyncing, Description
                FROM Quote
                ${where}
                ORDER BY LastModifiedDate DESC
                LIMIT ${limit}
                OFFSET ${offset}`;

  try {
    const result = await queryRaw(auth.instanceUrl, auth.accessToken, soql);
    return { records: result.records, totalSize: result.totalSize };
  } catch (e) {
    if (e.message?.includes('sObject type')) return { records: [], totalSize: 0 };
    throw e;
  }
}

export async function fetchQuoteLineItems(auth, quoteId) {
  try {
    return await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, Product2.Name, Product2.ProductCode, Product2.Family,
              Quantity, UnitPrice, TotalPrice, Discount, Description
       FROM QuoteLineItem
       WHERE QuoteId = '${quoteId}'
       ORDER BY SortOrder, Product2.Name`,
    );
  } catch (_) {
    return [];
  }
}

export async function fetchQuoteStatuses(auth) {
  try {
    const meta = await sfFetch(auth.instanceUrl, auth.accessToken, '/sobjects/Quote/describe');
    const field = meta.fields?.find(f => f.name === 'Status');
    return field?.picklistValues?.filter(v => v.active).map(v => v.value) ?? [];
  } catch (_) {
    return ['Draft', 'Needs Review', 'In Review', 'Approved', 'Rejected', 'Presented', 'Accepted', 'Denied'];
  }
}

// ── Orders ────────────────────────────────────────────────────────────────────

export async function fetchOrders(auth, { search = '', status = '', offset = 0, limit = 50 } = {}) {
  const conditions = ['Status != null'];
  if (search) {
    const s = search.replace(/'/g, "\\'");
    conditions.push(`(OrderNumber LIKE '%${s}%' OR Account.Name LIKE '%${s}%')`);
  }
  if (status) {
    conditions.push(`Status = '${status.replace(/'/g, "\\'")}'`);
  }

  const soql = `SELECT Id, OrderNumber, Status, TotalAmount, CurrencyIsoCode,
                       AccountId, Account.Name,
                       EffectiveDate, EndDate,
                       BillingCity, BillingCountry,
                       Type, Description,
                       LastModifiedDate, CreatedDate
                FROM Order
                WHERE ${conditions.join(' AND ')}
                ORDER BY LastModifiedDate DESC
                LIMIT ${limit}
                OFFSET ${offset}`;

  try {
    const result = await queryRaw(auth.instanceUrl, auth.accessToken, soql);
    return { records: result.records, totalSize: result.totalSize };
  } catch (e) {
    if (e.message?.includes('sObject type')) return { records: [], totalSize: 0 };
    throw e;
  }
}

export async function fetchOrderItems(auth, orderId) {
  try {
    return await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, Product2.Name, Product2.ProductCode, Product2.Family,
              Quantity, UnitPrice, TotalPrice, Description,
              OrderItemType
       FROM OrderItem
       WHERE OrderId = '${orderId}'
       ORDER BY Product2.Name`,
    );
  } catch (_) {
    return [];
  }
}

export async function fetchOrderStatuses(auth) {
  try {
    const meta = await sfFetch(auth.instanceUrl, auth.accessToken, '/sobjects/Order/describe');
    const field = meta.fields?.find(f => f.name === 'Status');
    return field?.picklistValues?.filter(v => v.active).map(v => v.value) ?? [];
  } catch (_) {
    return ['Draft', 'Activated', 'Cancelled'];
  }
}

// ── Org info ──────────────────────────────────────────────────────────────────

export async function fetchOrgInfo(auth) {
  try {
    const records = await query(
      auth.instanceUrl,
      auth.accessToken,
      `SELECT Id, Name, OrganizationType FROM Organization LIMIT 1`,
    );
    return records[0] ?? null;
  } catch (_) {
    return null;
  }
}

// ── Formatting utilities ──────────────────────────────────────────────────────

export function formatCurrency(amount, currency = 'USD') {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}
