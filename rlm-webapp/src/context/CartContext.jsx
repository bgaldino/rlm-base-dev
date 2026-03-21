import { createContext, useContext, useReducer, useCallback } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// Cart state: holds products the user has added (with config + pricing data)
// ─────────────────────────────────────────────────────────────────────────────

const CartContext = createContext(null);

function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD_ITEM': {
      const exists = state.items.find(i => i.cartKey === action.item.cartKey);
      if (exists) {
        return {
          ...state,
          items: state.items.map(i =>
            i.cartKey === action.item.cartKey
              ? { ...i, quantity: i.quantity + (action.item.quantity ?? 1) }
              : i
          ),
        };
      }
      return { ...state, items: [...state.items, action.item] };
    }

    case 'REMOVE_ITEM':
      return { ...state, items: state.items.filter(i => i.cartKey !== action.cartKey) };

    case 'UPDATE_QTY':
      return {
        ...state,
        items: state.items.map(i =>
          i.cartKey === action.cartKey ? { ...i, quantity: action.quantity } : i
        ).filter(i => i.quantity > 0),
      };

    case 'CLEAR':
      return { ...state, items: [] };

    default:
      return state;
  }
}

const initialState = { items: [] };

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  const addItem = useCallback((product, { quantity = 1, configData, contextId, transactionId, lineItemId, pricing } = {}) => {
    // Use a unique cartKey — if configured, suffix with timestamp so same product
    // can be added multiple times with different configurations.
    const cartKey = configData || contextId || transactionId
      ? `${product.id ?? product.Id}_${Date.now()}`
      : (product.id ?? product.Id);
    dispatch({
      type: 'ADD_ITEM',
      item: {
        cartKey,
        productId: product.id ?? product.Id,
        name:      product.name ?? product.Name,
        code:      product.productCode ?? product.ProductCode ?? product.stockKeepingUnit ?? product.StockKeepingUnit,
        family:    product.family ?? product.Family,
        quantity,
        unitPrice: pricing?.totalPrice ?? pricing?.netUnitPrice ?? product.price?.unitPrice,
        currency:  pricing?.currency ?? pricing?.currencyCode ?? product.price?.currencyCode ?? 'USD',
        configData,
        contextId,
        transactionId,   // ID of the pre-created Quote (if any)
        lineItemId,      // ID of the QuoteLineItem (if any)
        pricebookEntryId: product.pricebookEntryId,
        // Keep raw product for display
        product,
      },
    });
    return cartKey;
  }, []);

  const removeItem = useCallback((cartKey) => {
    dispatch({ type: 'REMOVE_ITEM', cartKey });
  }, []);

  const updateQty = useCallback((cartKey, quantity) => {
    dispatch({ type: 'UPDATE_QTY', cartKey, quantity });
  }, []);

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR' });
  }, []);

  const itemCount  = state.items.reduce((sum, i) => sum + (i.quantity ?? 1), 0);
  const totalPrice = state.items.reduce((sum, i) => {
    const p = i.unitPrice ?? 0;
    return sum + p * (i.quantity ?? 1);
  }, 0);

  return (
    <CartContext.Provider value={{ items: state.items, itemCount, totalPrice, addItem, removeItem, updateQty, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside <CartProvider>');
  return ctx;
}
