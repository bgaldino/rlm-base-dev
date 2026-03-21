import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { formatCurrency } from '../utils/rlmApi';

// ─────────────────────────────────────────────────────────────────────────────
// Cart Drawer — slides in from the right when the user clicks the cart icon.
// Shows cart items with qty controls and a "Review Quote" CTA.
// ─────────────────────────────────────────────────────────────────────────────

export default function CartDrawer({ open, onClose }) {
  const navigate = useNavigate();
  const { items, totalPrice, removeItem, updateQty } = useCart();

  const primaryCurrency = items[0]?.currency ?? 'USD';

  function handleReview() {
    onClose();
    navigate('/quote');
  }

  return (
    <>
      {/* Overlay */}
      <div
        className={`sf-drawer-overlay ${open ? 'sf-drawer-overlay--open' : ''}`}
        onClick={onClose}
      />

      {/* Drawer panel */}
      <aside className={`sf-cart-drawer ${open ? 'sf-cart-drawer--open' : ''}`}>
        {/* Header */}
        <div className="sf-cart-drawer__header">
          <h2 className="sf-cart-drawer__title">
            Your Quote
            {items.length > 0 && (
              <span className="sf-cart-drawer__count">{items.length} item{items.length !== 1 ? 's' : ''}</span>
            )}
          </h2>
          <button className="sf-modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Items */}
        <div className="sf-cart-drawer__body">
          {items.length === 0 ? (
            <div className="sf-empty-state sf-empty-state--sm">
              <div className="sf-empty-state__icon">🛒</div>
              <h4>Your quote is empty</h4>
              <p>Browse products and add them here to build your quote.</p>
            </div>
          ) : (
            <ul className="sf-cart-item-list">
              {items.map(item => (
                <li key={item.cartKey} className="sf-cart-item">
                  <div className="sf-cart-item__icon">
                    {item.family === 'Subscription' ? '🔄' : item.configData ? '⚙️' : '💎'}
                  </div>

                  <div className="sf-cart-item__info">
                    <div className="sf-cart-item__name">{item.name}</div>
                    {item.code && <div className="sf-cart-item__code">{item.code}</div>}
                    {item.configData && (
                      <div className="sf-cart-item__tag">⚙ Configured</div>
                    )}
                  </div>

                  <div className="sf-cart-item__controls">
                    <div className="sf-qty-mini">
                      <button onClick={() => updateQty(item.cartKey, item.quantity - 1)}>−</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => updateQty(item.cartKey, item.quantity + 1)}>+</button>
                    </div>
                    <div className="sf-cart-item__price">
                      {item.unitPrice != null
                        ? formatCurrency(item.unitPrice * item.quantity, item.currency)
                        : '—'}
                    </div>
                    <button
                      className="sf-cart-item__remove"
                      onClick={() => removeItem(item.cartKey)}
                      title="Remove"
                    >
                      ×
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="sf-cart-drawer__footer">
            <div className="sf-cart-drawer__total-row">
              <span>Estimated Total</span>
              <strong>{formatCurrency(totalPrice, primaryCurrency)}</strong>
            </div>
            <p className="sf-cart-drawer__disclaimer">
              Final pricing calculated at quote generation.
            </p>
            <button
              className="sf-btn sf-btn--primary sf-btn--full"
              onClick={handleReview}
            >
              Review &amp; Create Quote →
            </button>
          </div>
        )}
      </aside>
    </>
  );
}
