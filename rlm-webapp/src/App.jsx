import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './utils/auth';
import { CartProvider } from './context/CartContext';

// Pages
import LoginPage          from './pages/LoginPage';
import CallbackPage       from './pages/CallbackPage';
import CatalogBrowserPage from './pages/CatalogBrowserPage';
import QuoteReviewPage    from './pages/QuoteReviewPage';
import QuotesPage         from './pages/QuotesPage';
import OrdersPage         from './pages/OrdersPage';

// Keep legacy page available for backward compat
import ProductCatalogPage from './pages/ProductCatalogPage';

/** Redirects to /login if there's no access token in sessionStorage. */
function Protected({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <CartProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login"    element={<LoginPage />} />
          <Route path="/callback" element={<CallbackPage />} />

          {/* New storefront portal */}
          <Route path="/shop"  element={<Protected><CatalogBrowserPage /></Protected>} />
          <Route path="/quote" element={<Protected><QuoteReviewPage /></Protected>} />

          {/* My Quotes & Orders (storefront versions) */}
          <Route path="/quotes"  element={<Protected><QuotesPage /></Protected>} />
          <Route path="/orders"  element={<Protected><OrdersPage /></Protected>} />

          {/* Legacy catalog → redirect to storefront */}
          <Route path="/catalog" element={<Navigate to="/shop" replace />} />

          {/* Default → storefront */}
          <Route path="*" element={<Navigate to="/shop" replace />} />
        </Routes>
      </BrowserRouter>
    </CartProvider>
  );
}
