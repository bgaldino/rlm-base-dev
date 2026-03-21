import { useState, useEffect, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { getAuth, logout } from '../utils/auth';
import { useCart } from '../context/CartContext';
import CartDrawer from './CartDrawer';
import { fetchOrgBranding, fetchBrandLogoUrl } from '../utils/rlmApi';

const NAV = [
  { to: '/shop',   label: 'Products' },
  { to: '/quotes', label: 'My Quotes' },
  { to: '/orders', label: 'My Orders' },
];

// ─────────────────────────────────────────────────────────────────────────────
// StorefrontLayout — modern consumer-style header + page wrapper.
// Uses a top navigation bar instead of a side nav to feel more e-commerce-like.
// ─────────────────────────────────────────────────────────────────────────────

export default function StorefrontLayout({ children }) {
  const navigate  = useNavigate();
  const auth      = getAuth();
  const user      = auth?.user;
  const { itemCount } = useCart();

  const [cartOpen,       setCartOpen]       = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [branding,       setBranding]       = useState(null);   // { companyName, logoPath, brandColor, ... }
  const [logoUrl,        setLogoUrl]        = useState(null);   // authenticated blob URL
  const logoBlobRef = useRef(null);  // track for cleanup

  // Fallback org name from instance hostname
  const orgName = (() => {
    try { return new URL(auth?.instanceUrl ?? '').hostname.split('.')[0]; } catch (_) { return ''; }
  })();

  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
    : '?';

  // Fetch org branding once on mount
  useEffect(() => {
    if (!auth) return;
    let cancelled = false;
    fetchOrgBranding(auth).then(async b => {
      if (cancelled || !b) return;
      setBranding(b);
      // Fetch logo as blob so we can use it in an <img> with auth
      if (b.logoPath) {
        const url = await fetchBrandLogoUrl(auth, b.logoPath);
        if (!cancelled && url) {
          // Revoke previous blob URL if any
          if (logoBlobRef.current) URL.revokeObjectURL(logoBlobRef.current);
          logoBlobRef.current = url;
          setLogoUrl(url);
        }
      }
    });
    return () => {
      cancelled = true;
      if (logoBlobRef.current) URL.revokeObjectURL(logoBlobRef.current);
    };
  }, [auth?.accessToken]);

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="sf2-shell">
      {/* ── Top navigation bar ──────────────────────────────────────────────── */}
      <header
        className="sf2-navbar"
        style={branding?.headerBgColor ? { backgroundColor: branding.headerBgColor } : undefined}
      >
        <div className="sf2-navbar__inner">
          {/* Logo / Brand */}
          <NavLink to="/shop" className="sf2-navbar__brand">
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={branding?.companyName ?? orgName}
                className="sf2-navbar__brand-img"
              />
            ) : (
              <>
                <div className="sf2-navbar__logo-mark">
                  <span>☁</span>
                </div>
                <span className="sf2-navbar__logo-text">
                  {branding?.companyName ?? 'Revenue Cloud'}
                </span>
                {!branding && orgName && (
                  <span className="sf2-navbar__org">{orgName}</span>
                )}
              </>
            )}
          </NavLink>

          {/* Desktop nav links */}
          <nav className="sf2-navbar__nav">
            {NAV.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sf2-navbar__link ${isActive ? 'sf2-navbar__link--active' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Right: cart + user */}
          <div className="sf2-navbar__right">
            {/* Cart button */}
            <button
              className="sf2-cart-btn"
              onClick={() => setCartOpen(true)}
              title="Quote cart"
            >
              <span className="sf2-cart-btn__icon">🛒</span>
              {itemCount > 0 && (
                <span className="sf2-cart-btn__badge">{itemCount}</span>
              )}
            </button>

            {/* User avatar + logout */}
            <div className="sf2-user-menu">
              <div className="sf2-user-avatar" title={user?.name ?? 'User'}>
                {initials}
              </div>
              <button className="sf2-logout-btn" onClick={handleLogout} title="Log out">
                ⎋
              </button>
            </div>

            {/* Mobile hamburger */}
            <button
              className="sf2-hamburger"
              onClick={() => setMobileMenuOpen(s => !s)}
            >
              ☰
            </button>
          </div>
        </div>

        {/* Mobile nav dropdown */}
        {mobileMenuOpen && (
          <nav className="sf2-mobile-nav">
            {NAV.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sf2-mobile-nav__link ${isActive ? 'sf2-mobile-nav__link--active' : ''}`
                }
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.label}
              </NavLink>
            ))}
            <button className="sf2-mobile-nav__logout" onClick={handleLogout}>
              Log out
            </button>
          </nav>
        )}
      </header>

      {/* ── Page content ────────────────────────────────────────────────────── */}
      <main className="sf2-page">
        {children}
      </main>

      {/* ── Cart drawer ─────────────────────────────────────────────────────── */}
      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
    </div>
  );
}
