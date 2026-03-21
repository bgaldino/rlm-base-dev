import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuth } from '../utils/auth';
import { useCart } from '../context/CartContext';
import {
  placeSalesTransaction,
  fetchStandardPricebook,
  fetchPricebookEntries,
  formatCurrency,
} from '../utils/rlmApi';
import StorefrontLayout from '../components/StorefrontLayout';

// ─────────────────────────────────────────────────────────────────────────────
// Quote Review Page — final step before persisting the quote in Salesforce
//
// Cart items fall into two categories:
//   • Configured (transactionId present): Quote already exists in Salesforce —
//     created by placeSalesTransaction inside the configurator modal.  No
//     duplicate Quote should be created; we link directly to the existing one.
//   • Simple (no transactionId): Added via "+ Add" without configuration.
//     A new consolidated Quote is created here via placeSalesTransaction.
// ─────────────────────────────────────────────────────────────────────────────

export default function QuoteReviewPage() {
  const auth     = getAuth();
  const navigate = useNavigate();
  const { items, totalPrice, clearCart } = useCart();

  const [quoteName,  setQuoteName]  = useState(`Portal Quote — ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`);
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState('');
  const [success,    setSuccess]    = useState(null);

  const currency = items[0]?.currency ?? 'USD';

  // Partition cart into items that already have a Quote vs. those that don't
  const configuredItems = items.filter(i => i.transactionId);
  const simpleItems     = items.filter(i => !i.transactionId);

  async function handleCreateQuote() {
    if (!items.length) return;
    setSubmitting(true);
    setError('');

    try {
      let newQuoteId = null;

      if (simpleItems.length > 0) {
        // 1. Get standard pricebook for items that need one
        const pb = await fetchStandardPricebook(auth);
        const productIds = [...new Set(simpleItems.map(i => i.productId))];
        const pbeMap = pb ? await fetchPricebookEntries(auth, productIds, pb.Id) : {};

        // 2. Build cart items
        const cartItems = simpleItems.map(item => ({
          productId:        item.productId,
          quantity:         item.quantity ?? 1,
          pricebookEntryId: item.pricebookEntryId ?? pbeMap[item.productId]?.Id,
          unitPrice:        item.unitPrice,
        }));

        // 3. Create Quote via v66 Sales Transaction API
        const result = await placeSalesTransaction(auth, {
          quoteName,
          pricebookId: pb?.Id,
          cartItems,
        });

        newQuoteId = result?.salesTransactionId
          ?? result?.records?.find(r => r.referenceId === 'refQuote')?.id;

        if (!newQuoteId) throw new Error('No Quote ID returned from placeSalesTransaction');
      }

      setSuccess({
        newQuoteId,
        newQuoteName: quoteName,
        configuredQuotes: configuredItems.map(i => ({
          id:   i.transactionId,
          name: i.name,
        })),
      });
      clearCart();

    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  // ── Success state ──────────────────────────────────────────────────────────

  if (success) {
    const allQuotes = [
      ...(success.newQuoteId ? [{ id: success.newQuoteId, name: success.newQuoteName, isNew: true }] : []),
      ...success.configuredQuotes.map(q => ({ ...q, isNew: false })),
    ];
    return (
      <StorefrontLayout>
        <div className="sf-success-page">
          <div className="sf-success-page__icon">✅</div>
          <h2 className="sf-success-page__title">
            {allQuotes.length === 1 ? 'Quote Ready!' : `${allQuotes.length} Quotes Ready!`}
          </h2>
          <p className="sf-success-page__sub">
            {success.newQuoteId && !success.configuredQuotes.length
              ? <><strong>{success.newQuoteName}</strong> has been created in Salesforce.</>
              : success.configuredQuotes.length > 0 && !success.newQuoteId
              ? 'Your configured products are saved as quotes in Salesforce.'
              : 'Your cart has been saved to Salesforce.'}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, margin: '16px 0' }}>
            {allQuotes.map(q => (
              <a
                key={q.id}
                className="sf-btn sf-btn--primary"
                href={`${auth?.instanceUrl}/lightning/r/Quote/${q.id}/view`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ display: 'block', textAlign: 'center' }}
              >
                {q.isNew ? `Open "${q.name}" in Salesforce ↗` : `Open configured quote: ${q.name} ↗`}
              </a>
            ))}
          </div>

          <button
            className="sf-btn sf-btn--outline"
            onClick={() => navigate('/shop')}
          >
            Back to Catalog
          </button>
        </div>
      </StorefrontLayout>
    );
  }

  // ── Empty cart redirect ────────────────────────────────────────────────────

  if (!items.length) {
    return (
      <StorefrontLayout>
        <div className="sf-empty-state" style={{ marginTop: 80 }}>
          <div className="sf-empty-state__icon">🛒</div>
          <h3>Your quote is empty</h3>
          <p>Go back to the catalog and add some products first.</p>
          <button className="sf-btn sf-btn--primary" style={{ marginTop: 20 }} onClick={() => navigate('/shop')}>
            Browse Products
          </button>
        </div>
      </StorefrontLayout>
    );
  }

  // ── Main view ──────────────────────────────────────────────────────────────

  return (
    <StorefrontLayout>
      <div className="sf-quote-review">

        {/* Page header */}
        <div className="sf-quote-review__header">
          <button className="sf-back-btn" onClick={() => navigate('/shop')}>
            ← Back to Catalog
          </button>
          <h1 className="sf-page-header__title">Review Quote</h1>
        </div>

        <div className="sf-quote-review__body">

          {/* Left: line items */}
          <div className="sf-quote-review__left">
            {/* Quote name — only needed when simple (non-configured) items are present */}
            {simpleItems.length > 0 && (
              <div className="sf-field-group">
                <label className="sf-field-label">Quote Name</label>
                <input
                  type="text"
                  className="sf-input sf-input--lg"
                  value={quoteName}
                  onChange={e => setQuoteName(e.target.value)}
                  placeholder="Enter a name for this quote"
                />
              </div>
            )}

            {/* Line items table */}
            <div className="sf-quote-table-wrap">
              <table className="sf-quote-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Code</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(item => (
                    <tr key={item.cartKey}>
                      <td>
                        <div className="sf-quote-table__name">{item.name}</div>
                        {item.configData && (
                          <span className="sf-tag sf-tag--sm">Configured</span>
                        )}
                      </td>
                      <td className="sf-quote-table__code">
                        {item.code ?? '—'}
                      </td>
                      <td>{item.quantity ?? 1}</td>
                      <td>
                        {item.unitPrice != null
                          ? formatCurrency(item.unitPrice, item.currency)
                          : <span style={{ color: 'var(--sf2-text-muted)' }}>—</span>}
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        {item.unitPrice != null
                          ? formatCurrency(item.unitPrice * (item.quantity ?? 1), item.currency)
                          : <span style={{ color: 'var(--sf2-text-muted)' }}>—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {error && (
              <div className="sf-error-banner">{error}</div>
            )}
          </div>

          {/* Right: summary + CTA */}
          <div className="sf-quote-review__right">
            <div className="sf-quote-summary-card">
              <h3 className="sf-quote-summary-card__title">Quote Summary</h3>

              <div className="sf-quote-summary-card__rows">
                {items.map(item => (
                  <div key={item.cartKey} className="sf-quote-summary-card__row">
                    <span>{item.name} {item.quantity > 1 ? `×${item.quantity}` : ''}</span>
                    <span>
                      {item.unitPrice != null
                        ? formatCurrency(item.unitPrice * (item.quantity ?? 1), item.currency)
                        : '—'}
                    </span>
                  </div>
                ))}
              </div>

              <div className="sf-quote-summary-card__total">
                <span>Estimated Total</span>
                <strong>{formatCurrency(totalPrice, currency)}</strong>
              </div>

              <p className="sf-quote-summary-card__note">
                {configuredItems.length > 0 && simpleItems.length === 0
                  ? 'Configured products are already saved as quotes. Click below to open them in Salesforce.'
                  : 'Final pricing, taxes and discounts are calculated by Salesforce on the quote.'}
              </p>

              <button
                className="sf-btn sf-btn--primary sf-btn--full"
                onClick={handleCreateQuote}
                disabled={submitting || (simpleItems.length > 0 && !quoteName.trim())}
              >
                {submitting
                  ? 'Saving…'
                  : simpleItems.length > 0
                  ? 'Create Quote in Salesforce'
                  : 'Open Quotes in Salesforce'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </StorefrontLayout>
  );
}
