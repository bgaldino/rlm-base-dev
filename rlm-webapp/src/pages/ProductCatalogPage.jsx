import { useState, useEffect, useCallback, useRef } from 'react';
import { getAuth } from '../utils/auth';
import {
  fetchProducts, fetchProductFamilies, fetchStandardPrices,
  fetchProductPricing, formatCurrency, formatDate,
} from '../utils/salesforce';
import Layout  from '../components/Layout';
import Spinner from '../components/Spinner';

const PAGE_SIZE = 48;

function statusBadge(isActive) {
  return isActive
    ? <span className="badge badge-green">Active</span>
    : <span className="badge badge-gray">Inactive</span>;
}

// ── Product detail drawer ─────────────────────────────────────────────────────
function ProductDrawer({ product, auth, onClose }) {
  const [pricing, setPricing] = useState(null);

  useEffect(() => {
    if (!product) return;
    fetchProductPricing(auth, product.Id)
      .then(setPricing)
      .catch(() => setPricing([]));
  }, [product?.Id]);

  if (!product) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">
            <h2>{product.Name}</h2>
            <p>{product.ProductCode ?? product.StockKeepingUnit ?? '—'}</p>
          </div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-body">
          {/* Summary */}
          <div className="detail-section">
            <h4>Product Details</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Status</label>
                <span>{statusBadge(product.IsActive)}</span>
              </div>
              <div className="detail-item">
                <label>Family</label>
                <span>{product.Family ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Product Code</label>
                <span style={{ fontFamily: 'monospace', fontSize: 12.5 }}>
                  {product.ProductCode ?? '—'}
                </span>
              </div>
              <div className="detail-item">
                <label>SKU</label>
                <span style={{ fontFamily: 'monospace', fontSize: 12.5 }}>
                  {product.StockKeepingUnit ?? '—'}
                </span>
              </div>
              <div className="detail-item">
                <label>Last Modified</label>
                <span>{formatDate(product.LastModifiedDate)}</span>
              </div>
              <div className="detail-item">
                <label>Salesforce ID</label>
                <span style={{ fontFamily: 'monospace', fontSize: 11 }}>{product.Id}</span>
              </div>
            </div>
          </div>

          {/* Description */}
          {product.Description && (
            <div className="detail-section">
              <h4>Description</h4>
              <p style={{ fontSize: 13.5, color: 'var(--text-2)', lineHeight: 1.6 }}>
                {product.Description}
              </p>
            </div>
          )}

          {/* Pricing */}
          <div className="detail-section">
            <h4>Pricebook Entries</h4>
            {pricing === null
              ? <Spinner />
              : pricing.length === 0
                ? <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No pricebook entries found.</p>
                : (
                  <table className="line-items-table">
                    <thead>
                      <tr>
                        <th>Pricebook</th>
                        <th>Price</th>
                        <th>Currency</th>
                        <th>Active</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pricing.map(pe => (
                        <tr key={pe.Id}>
                          <td>
                            {pe.Pricebook2?.Name ?? '—'}
                            {pe.Pricebook2?.IsStandard && (
                              <span className="badge badge-blue" style={{ marginLeft: 6, fontSize: 10 }}>Standard</span>
                            )}
                          </td>
                          <td style={{ fontWeight: 700 }}>
                            {formatCurrency(pe.UnitPrice, pe.CurrencyIsoCode)}
                          </td>
                          <td>{pe.CurrencyIsoCode ?? '—'}</td>
                          <td>{pe.IsActive
                            ? <span className="badge badge-green">Yes</span>
                            : <span className="badge badge-gray">No</span>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
            }
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function ProductCatalogPage() {
  const auth = getAuth();

  const [products,  setProducts]  = useState([]);
  const [prices,    setPrices]    = useState({});
  const [families,  setFamilies]  = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');
  const [search,    setSearch]    = useState('');
  const [family,    setFamily]    = useState('');
  const [page,      setPage]      = useState(0);
  const [totalSize, setTotalSize] = useState(0);
  const [selected,  setSelected]  = useState(null);

  const debounce = useRef(null);

  const load = useCallback(async (s, f, p) => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchProducts(auth, { search: s, family: f, offset: p * PAGE_SIZE, limit: PAGE_SIZE });
      setProducts(result.records);
      setTotalSize(result.totalSize);

      // Fetch standard prices for these products
      const ids = result.records.map(r => r.Id);
      fetchStandardPrices(auth, ids).then(setPrices).catch(() => {});
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [auth?.accessToken]);

  // Load families once
  useEffect(() => {
    fetchProductFamilies(auth).then(setFamilies).catch(() => {});
  }, []);

  // Debounced search
  useEffect(() => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      setPage(0);
      load(search, family, 0);
    }, 300);
  }, [search, family]);

  useEffect(() => {
    load(search, family, page);
  }, [page]);

  const totalPages = Math.ceil(totalSize / PAGE_SIZE);

  return (
    <Layout pageTitle="Product Catalog">
      {/* Controls */}
      <div className="controls-row">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="search"
            className="search-input"
            placeholder="Search by name, code, or description…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {families.length > 0 && (
          <select
            className="filter-select"
            value={family}
            onChange={e => { setFamily(e.target.value); setPage(0); }}
          >
            <option value="">All Families</option>
            {families.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        )}

        {!loading && (
          <span className="result-count">
            {totalSize.toLocaleString()} product{totalSize !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Error */}
      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Content */}
      {loading
        ? <Spinner />
        : products.length === 0
          ? (
            <div className="empty-state">
              <div className="empty-state-icon">📦</div>
              <h3>No products found</h3>
              <p>Try adjusting your search or filters, or verify that Product2 records exist in this org.</p>
            </div>
          )
          : (
            <>
              <div className="card-grid">
                {products.map(p => {
                  const pe = prices[p.Id];
                  return (
                    <div key={p.Id} className="card" onClick={() => setSelected(p)}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                        <div className="card-title">{p.Name}</div>
                        {statusBadge(p.IsActive)}
                      </div>

                      {p.ProductCode && <div className="card-code">{p.ProductCode}</div>}

                      {p.Family && (
                        <span className="badge badge-blue" style={{ alignSelf: 'flex-start', fontSize: 11 }}>
                          {p.Family}
                        </span>
                      )}

                      {p.Description && <div className="card-desc">{p.Description}</div>}

                      <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                        <div className="card-price">
                          {pe ? formatCurrency(pe.UnitPrice, pe.CurrencyIsoCode) : '—'}
                        </div>
                        <div className="card-meta">{formatDate(p.LastModifiedDate)}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  <button className="page-btn" onClick={() => setPage(p => p - 1)} disabled={page === 0}>
                    ← Prev
                  </button>
                  <span className="page-info">Page {page + 1} of {totalPages}</span>
                  <button className="page-btn" onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1}>
                    Next →
                  </button>
                </div>
              )}
            </>
          )
      }

      {/* Detail drawer */}
      {selected && (
        <ProductDrawer
          product={selected}
          auth={auth}
          onClose={() => setSelected(null)}
        />
      )}
    </Layout>
  );
}
