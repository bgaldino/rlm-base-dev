import { useState, useEffect, useCallback, useRef } from 'react';
import { getAuth } from '../utils/auth';
import {
  fetchOrders, fetchOrderItems, fetchOrderStatuses,
  formatCurrency, formatDate,
} from '../utils/salesforce';
import Layout  from '../components/Layout';
import Spinner from '../components/Spinner';

const PAGE_SIZE = 50;

function orderBadge(status) {
  const map = {
    'Draft':      'badge-gray',
    'Activated':  'badge-green',
    'Active':     'badge-green',
    'Cancelled':  'badge-red',
    'Closed':     'badge-teal',
    'Suspended':  'badge-yellow',
    'Terminated': 'badge-red',
    'Pending':    'badge-yellow',
  };
  return <span className={`badge ${map[status] ?? 'badge-blue'}`}>{status ?? '—'}</span>;
}

// ── Order detail drawer ───────────────────────────────────────────────────────
function OrderDrawer({ order, auth, onClose }) {
  const [items, setItems] = useState(null);

  useEffect(() => {
    if (!order) return;
    fetchOrderItems(auth, order.Id)
      .then(setItems)
      .catch(() => setItems([]));
  }, [order?.Id]);

  if (!order) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">
            <h2>Order #{order.OrderNumber}</h2>
            <p>{order.Account?.Name ?? 'No account'}</p>
          </div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>

        <div className="drawer-body">
          {/* Status + amount callout */}
          <div style={{
            background: 'var(--sf-blue-light)',
            borderRadius: 'var(--radius-sm)',
            padding: '14px 16px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Status</div>
              {orderBadge(order.Status)}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Total Amount</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--sf-blue)' }}>
                {formatCurrency(order.TotalAmount, order.CurrencyIsoCode)}
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="detail-section">
            <h4>Order Details</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Account</label>
                <span>{order.Account?.Name ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Type</label>
                <span>{order.Type ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Effective Date</label>
                <span>{formatDate(order.EffectiveDate)}</span>
              </div>
              <div className="detail-item">
                <label>End Date</label>
                <span>{formatDate(order.EndDate)}</span>
              </div>
              <div className="detail-item">
                <label>Billing Location</label>
                <span>
                  {[order.BillingCity, order.BillingCountry].filter(Boolean).join(', ') || '—'}
                </span>
              </div>
              <div className="detail-item">
                <label>Currency</label>
                <span>{order.CurrencyIsoCode ?? '—'}</span>
              </div>
              <div className="detail-item">
                <label>Created</label>
                <span>{formatDate(order.CreatedDate)}</span>
              </div>
              <div className="detail-item">
                <label>Last Modified</label>
                <span>{formatDate(order.LastModifiedDate)}</span>
              </div>
              <div className="detail-item" style={{ gridColumn: '1 / -1' }}>
                <label>Salesforce ID</label>
                <span style={{ fontFamily: 'monospace', fontSize: 11 }}>{order.Id}</span>
              </div>
            </div>
          </div>

          {/* Description */}
          {order.Description && (
            <div className="detail-section">
              <h4>Description</h4>
              <p style={{ fontSize: 13.5, color: 'var(--text-2)', lineHeight: 1.6 }}>{order.Description}</p>
            </div>
          )}

          {/* Order Items */}
          <div className="detail-section">
            <h4>Order Products</h4>
            {items === null
              ? <Spinner />
              : items.length === 0
                ? <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No order products found.</p>
                : (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="line-items-table">
                      <thead>
                        <tr>
                          <th>Product</th>
                          <th>Qty</th>
                          <th>Unit Price</th>
                          <th>Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map(item => (
                          <tr key={item.Id}>
                            <td>
                              <div style={{ fontWeight: 600 }}>{item.Product2?.Name ?? '—'}</div>
                              {item.Product2?.ProductCode && (
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                                  {item.Product2.ProductCode}
                                </div>
                              )}
                              {item.Product2?.Family && (
                                <span className="badge badge-blue" style={{ marginTop: 3, fontSize: 10 }}>
                                  {item.Product2.Family}
                                </span>
                              )}
                            </td>
                            <td>{item.Quantity ?? '—'}</td>
                            <td>{formatCurrency(item.UnitPrice, order.CurrencyIsoCode)}</td>
                            <td style={{ fontWeight: 700 }}>
                              {formatCurrency(item.TotalPrice, order.CurrencyIsoCode)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colSpan={3} style={{ textAlign: 'right', fontWeight: 700, paddingTop: 12 }}>
                            Order Total
                          </td>
                          <td style={{ fontWeight: 800, color: 'var(--sf-blue)', fontSize: 15 }}>
                            {formatCurrency(order.TotalAmount, order.CurrencyIsoCode)}
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
export default function OrdersPage() {
  const auth = getAuth();

  const [orders,    setOrders]    = useState([]);
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
      const result = await fetchOrders(auth, { search: s, status: st, offset: p * PAGE_SIZE, limit: PAGE_SIZE });
      setOrders(result.records);
      setTotalSize(result.totalSize);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [auth?.accessToken]);

  useEffect(() => {
    fetchOrderStatuses(auth).then(setStatuses).catch(() => {});
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
    <Layout pageTitle="Orders">
      <div className="controls-row">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="search"
            className="search-input"
            placeholder="Search by order number or account…"
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
            {totalSize.toLocaleString()} order{totalSize !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {loading
        ? <Spinner />
        : orders.length === 0
          ? (
            <div className="empty-state">
              <div className="empty-state-icon">🛒</div>
              <h3>No orders found</h3>
              <p>Try adjusting your filters, or activate orders in Salesforce first.</p>
            </div>
          )
          : (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Order #</th>
                      <th>Status</th>
                      <th>Account</th>
                      <th>Type</th>
                      <th>Total</th>
                      <th>Effective Date</th>
                      <th>Modified</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map(o => (
                      <tr key={o.Id} onClick={() => setSelected(o)}>
                        <td style={{ fontWeight: 700, fontFamily: 'monospace', fontSize: 13 }}>
                          {o.OrderNumber}
                        </td>
                        <td>{orderBadge(o.Status)}</td>
                        <td>{o.Account?.Name ?? '—'}</td>
                        <td>{o.Type
                          ? <span className="badge badge-purple">{o.Type}</span>
                          : '—'}
                        </td>
                        <td style={{ fontWeight: 700 }}>
                          {formatCurrency(o.TotalAmount, o.CurrencyIsoCode)}
                        </td>
                        <td>{formatDate(o.EffectiveDate)}</td>
                        <td>{formatDate(o.LastModifiedDate)}</td>
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
        <OrderDrawer order={selected} auth={auth} onClose={() => setSelected(null)} />
      )}
    </Layout>
  );
}
