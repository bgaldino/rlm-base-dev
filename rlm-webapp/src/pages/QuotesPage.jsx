import { useState, useEffect, useCallback, useRef } from 'react';
import { getAuth } from '../utils/auth';
import {
  fetchQuotes, fetchQuoteLineItems, fetchQuoteStatuses,
  formatCurrency, formatDate,
} from '../utils/salesforce';
import Layout  from '../components/Layout';
import Spinner from '../components/Spinner';

const PAGE_SIZE = 50;

function quoteBadge(status) {
  const map = {
    'Draft':        'badge-gray',
    'Needs Review': 'badge-yellow',
    'In Review':    'badge-yellow',
    'Approved':     'badge-green',
    'Rejected':     'badge-red',
    'Presented':    'badge-blue',
    'Accepted':     'badge-teal',
    'Denied':       'badge-red',
  };
  return <span className={`badge ${map[status] ?? 'badge-gray'}`}>{status ?? '—'}</span>;
}

// ── Quote detail drawer ───────────────────────────────────────────────────────
function QuoteDrawer({ quote, auth, onClose }) {
  const [lineItems, setLineItems] = useState(null);

  useEffect(() => {
    if (!quote) return;
    fetchQuoteLineItems(auth, quote.Id)
      .then(setLineItems)
      .catch(() => setLineItems([]));
  }, [quote?.Id]);

  if (!quote) return null;

  const total = quote.GrandTotal ?? quote.TotalPrice;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">
            <h2>{quote.Name}</h2>
            <p>Quote · {quote.Id}</p>
          </div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-body">
          {/* Status + total callout */}
          <div style={{
            background: 'var(--sf-blue-light)',
            borderRadius: 'var(--radius-sm)',
            padding: '14px 16px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Status</div>
              {quoteBadge(quote.Status)}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Grand Total</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--sf-blue)' }}>
                {formatCurrency(total)}
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="detail-section">
            <h4>Quote Details</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Account</label>
                <span>{quote.Account?.Name ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Opportunity</label>
                <span>{quote.Opportunity?.Name ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Expiration Date</label>
                <span>{formatDate(quote.ExpirationDate)}</span>
              </div>
              <div className="detail-item">
                <label>Syncing</label>
                <span>{quote.IsSyncing
                  ? <span className="badge badge-teal">Yes</span>
                  : <span className="badge badge-gray">No</span>}
                </span>
              </div>
              <div className="detail-item">
                <label>Created</label>
                <span>{formatDate(quote.CreatedDate)}</span>
              </div>
              <div className="detail-item">
                <label>Last Modified</label>
                <span>{formatDate(quote.LastModifiedDate)}</span>
              </div>
            </div>
          </div>

          {/* Description */}
          {quote.Description && (
            <div className="detail-section">
              <h4>Description</h4>
              <p style={{ fontSize: 13.5, color: 'var(--text-2)', lineHeight: 1.6 }}>{quote.Description}</p>
            </div>
          )}

          {/* Line items */}
          <div className="detail-section">
            <h4>Line Items</h4>
            {lineItems === null
              ? <Spinner />
              : lineItems.length === 0
                ? <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No line items found.</p>
                : (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="line-items-table">
                      <thead>
                        <tr>
                          <th>Product</th>
                          <th>Qty</th>
                          <th>Unit Price</th>
                          <th>Discount</th>
                          <th>Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lineItems.map(li => (
                          <tr key={li.Id}>
                            <td>
                              <div style={{ fontWeight: 600 }}>{li.Product2?.Name ?? '—'}</div>
                              {li.Product2?.ProductCode && (
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                                  {li.Product2.ProductCode}
                                </div>
                              )}
                            </td>
                            <td>{li.Quantity ?? '—'}</td>
                            <td>{formatCurrency(li.UnitPrice)}</td>
                            <td>{li.Discount != null ? `${li.Discount}%` : '—'}</td>
                            <td style={{ fontWeight: 700 }}>{formatCurrency(li.TotalPrice)}</td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colSpan={4} style={{ textAlign: 'right', fontWeight: 700, paddingTop: 12 }}>
                            Grand Total
                          </td>
                          <td style={{ fontWeight: 800, color: 'var(--sf-blue)', fontSize: 15 }}>
                            {formatCurrency(total)}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )
            }
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function QuotesPage() {
  const auth = getAuth();

  const [quotes,    setQuotes]    = useState([]);
  const [statuses,  setStatuses]  = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');
  const [search,    setSearch]    = useState('');
  const [status,    setStatus]    = useState('');
  const [page,      setPage]      = useState(0);
  const [totalSize, setTotalSize] = useState(0);
  const [selected,  setSelected]  = useState(null);

  const debounce = useRef(null);

  const load = useCallback(async (s, st, p) => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchQuotes(auth, { search: s, status: st, offset: p * PAGE_SIZE, limit: PAGE_SIZE });
      setQuotes(result.records);
      setTotalSize(result.totalSize);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [auth?.accessToken]);

  useEffect(() => {
    fetchQuoteStatuses(auth).then(setStatuses).catch(() => {});
  }, []);

  useEffect(() => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      setPage(0);
      load(search, status, 0);
    }, 300);
  }, [search, status]);

  useEffect(() => {
    load(search, status, page);
  }, [page]);

  const totalPages = Math.ceil(totalSize / PAGE_SIZE);

  return (
    <Layout pageTitle="Quotes">
      <div className="controls-row">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="search"
            className="search-input"
            placeholder="Search by quote name…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {statuses.length > 0 && (
          <select
            className="filter-select"
            value={status}
            onChange={e => { setStatus(e.target.value); setPage(0); }}
          >
            <option value="">All Statuses</option>
            {statuses.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        )}

        {!loading && (
          <span className="result-count">
            {totalSize.toLocaleString()} quote{totalSize !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {loading
        ? <Spinner />
        : quotes.length === 0
          ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <h3>No quotes found</h3>
              <p>Try adjusting your filters, or create quotes in Salesforce first.</p>
            </div>
          )
          : (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Quote Name</th>
                      <th>Status</th>
                      <th>Account</th>
                      <th>Opportunity</th>
                      <th>Total</th>
                      <th>Expires</th>
                      <th>Modified</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quotes.map(q => (
                      <tr key={q.Id} onClick={() => setSelected(q)}>
                        <td style={{ fontWeight: 600 }}>{q.Name}</td>
                        <td>{quoteBadge(q.Status)}</td>
                        <td>{q.Account?.Name ?? '—'}</td>
                        <td>{q.Opportunity?.Name ?? '—'}</td>
                        <td style={{ fontWeight: 700 }}>
                          {formatCurrency(q.GrandTotal ?? q.TotalPrice)}
                        </td>
                        <td>{formatDate(q.ExpirationDate)}</td>
                        <td>{formatDate(q.LastModifiedDate)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

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

      {selected && (
        <QuoteDrawer quote={selected} auth={auth} onClose={() => setSelected(null)} />
      )}
    </Layout>
  );
}
