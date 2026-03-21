import { useState, useEffect, useCallback, useRef } from 'react';
import { getAuth } from '../utils/auth';
import { listCatalogs, listCategories, listProducts, globalSearch, getInstantPricing, formatCurrency } from '../utils/rlmApi';
import { fetchStandardPrices, fetchProducts as fetchProductsSoql } from '../utils/salesforce';
import { useCart } from '../context/CartContext';
import StorefrontLayout from '../components/StorefrontLayout';
import Spinner from '../components/Spinner';
import ProductConfiguratorModal from '../components/ProductConfiguratorModal';

const PAGE_SIZE = 24;

// ── PSM helpers ───────────────────────────────────────────────────────────────

/**
 * Derive PSM bucket from a pricingModel object.
 * Returns 'OneTime' | 'Annual' | 'Monthly'.
 */
function productPsmType(pricingModel) {
  const type = (
    pricingModel?.pricingModelType ??
    pricingModel?.sellingModelType ??
    ''
  ).trim();
  if (!type || type === 'OneTime') return 'OneTime';
  if (type === 'Evergreen') return 'Monthly';
  if (type === 'TermDefined') {
    const freq = (
      pricingModel?.frequency ??
      pricingModel?.occurrence ??
      pricingModel?.pricingTermUnit ??
      ''
    ).toLowerCase();
    if (freq.includes('annual') || freq.includes('year')) return 'Annual';
    return 'Monthly';
  }
  return 'OneTime';
}

/**
 * Normalise a product's prices[] array into selectable PSM options.
 * Each entry: { key, label, period, psmType, price, currency, isDefault, name }
 */
function getProductPsmOptions(product) {
  const prices = product.prices ?? [];
  if (!prices.length) return [];
  return prices.map((pe, idx) => {
    const pm      = pe.pricingModel ?? pe.PricingModel ?? {};
    const psmType = productPsmType(pm);
    const period  = psmType === 'Annual' ? '/yr' : psmType === 'Monthly' ? '/mo' : '';
    const label   = psmType === 'Annual' ? 'Annual' : psmType === 'Monthly' ? 'Monthly' : 'One-Time';
    return {
      key:       `${idx}-${psmType}-${pe.price ?? 0}`,
      label,
      period,
      psmType,
      price:     pe.price ?? pe.Price ?? pe.unitPrice ?? pe.UnitPrice ?? 0,
      currency:  pe.currencyCode ?? pe.CurrencyIsoCode ?? pe.currencyIsoCode ?? 'USD',
      isDefault: pe.isDefault ?? false,
      // Human-readable name from the pricingModel if available
      name:      pm.name ?? pe.name ?? null,
    };
  });
}

/**
 * Pick the default PSM option from an options array.
 * Priority: Term Annual > isDefault flag > first entry.
 */
function getDefaultPsmOption(options) {
  if (!options.length) return null;
  const annual = options.find(o => o.psmType === 'Annual');
  if (annual) return annual;
  const def = options.find(o => o.isDefault);
  if (def) return def;
  return options[0];
}

// ── Product Card ──────────────────────────────────────────────────────────────

function ProductCard({ product, price, onConfigure, onAddToCart, instanceUrl }) {
  const name        = product.name ?? product.Name ?? '—';
  const description = product.description ?? product.Description;
  const code        = product.productCode ?? product.ProductCode ?? product.stockKeepingUnit ?? product.StockKeepingUnit;
  const family      = product.family ?? product.Family;
  const isBundle    = product.nodeType === 'bundleProduct'
                   || product.productType === 'Bundle' || product.type === 'Bundle'
                   || product.configureDuringSale === 'Required'
                   || product.hasOptions === true || product.hasComponents === true;

  // ── PSM selection state ──────────────────────────────────────────────────
  const psmOptions   = getProductPsmOptions(product);
  const [selectedPsm, setSelectedPsm] = useState(() => getDefaultPsmOption(psmOptions));
  const [psmOpen,     setPsmOpen]     = useState(false);
  const psmRef = useRef(null);

  // Close PSM dropdown on outside click
  useEffect(() => {
    if (!psmOpen) return;
    function handleOutside(e) {
      if (psmRef.current && !psmRef.current.contains(e.target)) setPsmOpen(false);
    }
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, [psmOpen]);

  // ── Resolved price display ───────────────────────────────────────────────
  // Priority: selected PSM price from catalog > standard pricebook price prop
  const activePsm    = selectedPsm ?? psmOptions[0] ?? null;
  const psmPrice     = activePsm?.price ?? null;
  const psmCurrency  = activePsm?.currency ?? price?.currencyCode ?? price?.CurrencyIsoCode ?? 'USD';
  const psmPeriod    = activePsm?.period ?? '';
  const rawPrice     = psmPrice ?? price?.unitPrice ?? price?.UnitPrice ?? null;
  const displayPrice = rawPrice != null ? formatCurrency(rawPrice, psmCurrency) : null;

  // ── Product image ────────────────────────────────────────────────────────
  const rawImgPath = product.displayUrl ?? product.imageUrl ?? null;
  const imgSrc = rawImgPath
    ? (rawImgPath.startsWith('http') ? rawImgPath : (instanceUrl ? instanceUrl + rawImgPath : null))
    : null;

  const fallbackIcon = family === 'Subscription' ? '🔄'
    : family === 'Service' ? '⚙️'
    : isBundle ? '📦'
    : '💎';

  return (
    <div className="sf-product-card">
      {/* Product image — real image or styled emoji placeholder */}
      <div className="sf-product-card__img">
        {imgSrc ? (
          <img
            src={imgSrc}
            alt={name}
            className="sf-product-card__img-real"
            onError={e => { e.currentTarget.style.display = 'none'; e.currentTarget.nextSibling.style.display = 'flex'; }}
          />
        ) : null}
        <span
          className="sf-product-card__img-icon"
          style={imgSrc ? { display: 'none' } : {}}
        >
          {fallbackIcon}
        </span>
      </div>

      {/* Body */}
      <div className="sf-product-card__body">
        <div className="sf-product-card__meta">
          {family && <span className="sf-tag">{family}</span>}
          {isBundle && <span className="sf-tag sf-tag--bundle">Bundle</span>}
        </div>

        <h3 className="sf-product-card__name">{name}</h3>
        {code && <div className="sf-product-card__code">{code}</div>}

        {description && (
          <p className="sf-product-card__desc">{description}</p>
        )}
      </div>

      {/* Footer */}
      <div className="sf-product-card__footer">
        {/* Price + PSM selector */}
        {displayPrice ? (
          <div className="sf-product-card__price-row">
            <span className="sf-product-card__price">
              {displayPrice}
              {psmPeriod && (
                <span className="sf-product-card__price-period">{psmPeriod}</span>
              )}
            </span>

            {/* PSM selector trigger — only show when multiple models available */}
            {psmOptions.length > 1 && (
              <div className="sf-psm-anchor" ref={psmRef}>
                <button
                  className="sf-psm-trigger"
                  onClick={e => { e.stopPropagation(); setPsmOpen(o => !o); }}
                  title="Change selling model"
                  aria-label="Select selling model"
                >
                  🏷
                </button>

                {psmOpen && (
                  <div className="sf-psm-dropdown">
                    <div className="sf-psm-dropdown__header">Selling Model</div>
                    {psmOptions.map(opt => (
                      <button
                        key={opt.key}
                        className={`sf-psm-option${selectedPsm?.key === opt.key ? ' sf-psm-option--active' : ''}`}
                        onClick={() => { setSelectedPsm(opt); setPsmOpen(false); }}
                      >
                        <span className="sf-psm-option__label">
                          {opt.name || opt.label}
                        </span>
                        <span className="sf-psm-option__price">
                          {formatCurrency(opt.price, opt.currency)}{opt.period}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="sf-product-card__price sf-product-card__price--empty">
            Pricing available on configure
          </div>
        )}

        {isBundle ? (
          <button
            className="sf-btn sf-btn--primary sf-btn--sm"
            onClick={() => onConfigure(product)}
          >
            Configure
          </button>
        ) : (
          <button
            className="sf-btn sf-btn--outline sf-btn--sm"
            onClick={() => onAddToCart(product, price)}
          >
            + Add
          </button>
        )}
      </div>
    </div>
  );
}

// ── Category Tree ─────────────────────────────────────────────────────────────

function CategoryTree({ categories, selectedId, onSelect }) {
  return (
    <nav className="sf-cat-nav">
      <button
        className={`sf-cat-item ${!selectedId ? 'sf-cat-item--active' : ''}`}
        onClick={() => onSelect(null)}
      >
        <span className="sf-cat-item__icon">🏠</span>
        All Products
      </button>
      {categories.map(cat => (
        <button
          key={cat.id ?? cat.Id}
          className={`sf-cat-item ${selectedId === (cat.id ?? cat.Id) ? 'sf-cat-item--active' : ''}`}
          onClick={() => onSelect(cat.id ?? cat.Id)}
        >
          <span className="sf-cat-item__icon">📁</span>
          {cat.name ?? cat.Name}
        </button>
      ))}
    </nav>
  );
}

// ── Instant Pricing parser ────────────────────────────────────────────────────
// Maps the graph composite response back to { [productId]: { unitPrice, currencyCode } }

function parseInstantPriceMap(result, productIds) {
  const map = {};
  // The graph response may have records[] (composite graph) or results[] (graph batch)
  const records = result?.records ?? result?.results ?? [];
  records.forEach(rec => {
    const refId = rec.referenceId;
    if (!refId || refId === 'refQuote') return;
    // referenceId is 'refQLI1', 'refQLI2', … (1-indexed)
    const match = refId.match(/refQLI(\d+)/);
    if (!match) return;
    const qliIdx    = parseInt(match[1], 10) - 1; // convert to 0-indexed
    const productId = productIds[qliIdx];
    if (!productId) return;
    // Price is on the returned record (field or nested)
    const row       = rec.record ?? rec.result ?? rec;
    const unitPrice = row.UnitPrice ?? row.unitPrice ?? row.NetUnitPrice;
    const currency  = row.CurrencyIsoCode ?? row.currencyCode ?? 'USD';
    if (unitPrice != null) {
      map[productId] = { unitPrice, currencyCode: currency };
    }
  });
  return map;
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function CatalogBrowserPage() {
  const auth = getAuth();
  const { addItem, itemCount } = useCart();

  // Catalog / category state
  const [catalogs,    setCatalogs]    = useState([]);
  const [categories,  setCategories]  = useState([]);
  const [activeCatalog,  setActiveCatalog]  = useState(null);
  const [activeCategory, setActiveCategory] = useState(null);

  // Product grid state
  const [products,      setProducts]      = useState([]);
  const [prices,        setPrices]        = useState({});
  const [loading,       setLoading]       = useState(true);
  const [error,         setError]         = useState('');
  const [search,        setSearch]        = useState('');
  const [cursor,        setCursor]        = useState(null);
  const [hasMore,       setHasMore]       = useState(false);
  const [totalCount,    setTotalCount]    = useState(null);
  const [catSidebarOpen, setCatSidebarOpen] = useState(false);

  // Configurator modal
  const [configuringProduct, setConfiguringProduct] = useState(null);

  // Add-to-cart feedback
  const [addedKey,    setAddedKey]    = useState(null);

  const debounce = useRef(null);

  // ── Load catalogs ────────────────────────────────────────────────────────

  useEffect(() => {
    listCatalogs(auth)
      .then(cats => {
        setCatalogs(cats);
        // Only set default catalog on first load — don't overwrite user's selection.
        // Prefer "QuantumBit Software" (the org's default discovery catalog); fall back to first.
        setActiveCatalog(prev => {
          if (prev) return prev;
          const preferred = cats.find(c =>
            (c.name ?? c.Name ?? '').toLowerCase().includes('software')
          );
          return preferred ?? cats[0] ?? null;
        });
        // If CPQ returns no catalogs the product load will run with no catalogId,
        // which is fine — the SOQL fallback in loadProducts will kick in.
      })
      .catch(e => {
        console.error('[Shop] listCatalogs error:', e.message);
        // Still let loadProducts run via the debounce effect (with no catalogId)
      });
  }, []);

  // ── Load categories when catalog changes ─────────────────────────────────

  useEffect(() => {
    if (!activeCatalog) return;
    const catId = activeCatalog.id ?? activeCatalog.Id;
    listCategories(auth, catId).then(cats => {
      setCategories(cats);
      setActiveCategory(null);
    }).catch(() => setCategories([]));
  }, [activeCatalog]);

  // ── Load products ────────────────────────────────────────────────────────

  const loadProducts = useCallback(async (reset = true) => {
    setLoading(true);
    if (reset) setError('');

    try {
      const catalogId  = activeCatalog?.id ?? activeCatalog?.Id;
      const categoryId = activeCategory;

      // Use Global Search when a search term is present, Products List otherwise
      let result;
      if (search) {
        result = await globalSearch(auth, {
          searchTerm: search,
          catalogId,
          categoryId,
          limit: PAGE_SIZE,
          cursor: reset ? null : cursor,
        });
      } else {
        result = await listProducts(auth, {
          catalogId,
          categoryId,
          limit: PAGE_SIZE,
          cursor: reset ? null : cursor,
        });
      }

      let newProducts = result.products ?? [];

      // ── SOQL fallback if CPQ API returned nothing ────────────────────────
      // This covers orgs where the CPQ catalog isn't set up yet, or the
      // products API needs a catalogId that we don't have yet.
      if (newProducts.length === 0 && reset) {
        console.warn('[Shop] CPQ products API returned 0 results — falling back to SOQL');
        try {
          const soqlProducts = await fetchProductsSoql(auth, {
            search: search || '',
            limit: PAGE_SIZE,
            offset: 0,
          });
          // Normalise SOQL records to the same shape as CPQ response fields
          newProducts = soqlProducts.map(p => ({
            id:          p.Id,
            name:        p.Name,
            productCode: p.ProductCode,
            description: p.Description,
            productType: p.Type,
            family:      p.Family,
            isActive:    p.IsActive,
            _source:     'soql',
          }));
        } catch (soqlErr) {
          console.error('[Shop] SOQL fallback also failed:', soqlErr.message);
        }
      }

      setProducts(prev => reset ? newProducts : [...prev, ...newProducts]);
      setCursor(result.nextPageToken);
      setHasMore(!!result.nextPageToken);
      setTotalCount(result.totalCount ?? newProducts.length);

      // ── Fetch prices ─────────────────────────────────────────────────────
      const ids = newProducts.map(p => p.id ?? p.Id).filter(Boolean);
      if (ids.length > 0) {
        getInstantPricing(auth, {
          lineItems: ids.map(id => ({ productId: id, quantity: 1 })),
        })
          .then(pricingResult => {
            const map = parseInstantPriceMap(pricingResult, ids);
            if (Object.keys(map).length > 0) {
              setPrices(prev => ({ ...prev, ...map }));
            } else {
              return fetchStandardPrices(auth, ids)
                .then(pm => setPrices(prev => ({ ...prev, ...pm })));
            }
          })
          .catch(() => {
            fetchStandardPrices(auth, ids)
              .then(pm => setPrices(prev => ({ ...prev, ...pm })))
              .catch(() => {});
          });
      }
    } catch (e) {
      console.error('[Shop] loadProducts error:', e.message, e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [auth?.accessToken, activeCatalog, activeCategory, search]);

  // Debounce search + reload on filter change
  useEffect(() => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => loadProducts(true), 350);
  }, [search, activeCatalog, activeCategory]);

  // ── Handlers ─────────────────────────────────────────────────────────────

  function handleAddToCart(product, price) {
    const key = addItem(product, {
      quantity: 1,
      pricing: price ? {
        unitPrice: price.UnitPrice ?? price.unitPrice,
        currencyCode: price.CurrencyIsoCode ?? price.currencyCode ?? 'USD',
      } : undefined,
    });
    setAddedKey(key);
    setTimeout(() => setAddedKey(null), 1800);
  }

  function handleConfigureComplete(product, result) {
    const contextId     = result?.contextId;
    const transactionId = result?.transactionId;
    const lineItemId    = result?.lineItemId;
    const pricing       = result?.pricing;
    addItem(product, {
      quantity: 1,
      contextId,
      transactionId,
      lineItemId,
      pricing,
      configData: result?.configData,
    });
    setConfiguringProduct(null);
  }

  const activeCatalogName = activeCatalog?.name ?? activeCatalog?.Name ?? 'Products';

  return (
    <StorefrontLayout>
      {/* ── Top bar: catalog selector + search ─────────────────────────────── */}
      <div className="sf-page-header">
        <div className="sf-page-header__left">
          <h1 className="sf-page-header__title">Browse Products</h1>
          {catalogs.length > 1 && (
            <select
              className="sf-select"
              value={activeCatalog?.id ?? activeCatalog?.Id ?? ''}
              onChange={e => {
                const cat = catalogs.find(c => (c.id ?? c.Id) === e.target.value);
                setActiveCatalog(cat ?? null);
              }}
            >
              {catalogs.map(cat => (
                <option key={cat.id ?? cat.Id} value={cat.id ?? cat.Id}>
                  {cat.name ?? cat.Name}
                </option>
              ))}
            </select>
          )}
          {catalogs.length === 1 && (
            <span className="sf-page-header__catalog">{activeCatalogName}</span>
          )}
        </div>

        <div className="sf-page-header__right">
          {totalCount != null && (
            <span className="sf-result-count">{totalCount.toLocaleString()} products</span>
          )}
          <div className="sf-searchbox">
            <span className="sf-searchbox__icon">🔍</span>
            <input
              type="search"
              className="sf-searchbox__input"
              placeholder="Search products…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          {/* Mobile category toggle */}
          <button
            className="sf-btn sf-btn--ghost sf-btn--sm sf-cat-toggle"
            onClick={() => setCatSidebarOpen(s => !s)}
          >
            ≡ Categories
          </button>
        </div>
      </div>

      {/* ── Body: category sidebar + product grid ──────────────────────────── */}
      <div className="sf-catalog-body">
        {/* Category sidebar */}
        <aside className={`sf-cat-sidebar ${catSidebarOpen ? 'sf-cat-sidebar--open' : ''}`}>
          {categories.length > 0 && (
            <CategoryTree
              categories={categories}
              selectedId={activeCategory}
              onSelect={id => { setActiveCategory(id); setCatSidebarOpen(false); }}
            />
          )}
        </aside>

        {/* Product area */}
        <section className="sf-catalog-main">
          {error && (
            <div className="sf-error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          {loading && products.length === 0
            ? <div className="sf-catalog-spinner"><Spinner /></div>
            : products.length === 0
              ? (
                <div className="sf-empty-state">
                  <div className="sf-empty-state__icon">🔍</div>
                  <h3>No products found</h3>
                  <p>Try a different search or select another category.</p>
                </div>
              )
              : (
                <>
                  <div className="sf-product-grid">
                    {products.map(p => {
                      const pid   = p.id ?? p.Id;
                      const price = prices[pid];
                      return (
                        <ProductCard
                          key={pid}
                          product={p}
                          price={price}
                          onConfigure={setConfiguringProduct}
                          onAddToCart={handleAddToCart}
                          instanceUrl={auth?.instanceUrl}
                        />
                      );
                    })}
                  </div>

                  {/* Load more */}
                  {hasMore && (
                    <div className="sf-load-more">
                      <button
                        className="sf-btn sf-btn--outline"
                        onClick={() => loadProducts(false)}
                        disabled={loading}
                      >
                        {loading ? 'Loading…' : 'Load more products'}
                      </button>
                    </div>
                  )}
                </>
              )
          }
        </section>
      </div>

      {/* ── Add-to-cart toast ───────────────────────────────────────────────── */}
      {addedKey && (
        <div className="sf-toast">
          ✓ Added to quote
        </div>
      )}

      {/* ── Product Configurator Modal ──────────────────────────────────────── */}
      {configuringProduct && (
        <ProductConfiguratorModal
          product={configuringProduct}
          auth={auth}
          catalogId={activeCatalog?.id ?? activeCatalog?.Id}
          onClose={() => setConfiguringProduct(null)}
          onSave={result => handleConfigureComplete(configuringProduct, result)}
        />
      )}
    </StorefrontLayout>
  );
}
