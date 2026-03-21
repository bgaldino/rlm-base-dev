import { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { getAuth, logout } from '../utils/auth';

const NAV = [
  { to: '/shop',    icon: '🏪', label: 'Shop' },
  { to: '/catalog', icon: '📦', label: 'Product Catalog' },
  { to: '/quotes',  icon: '📋', label: 'Quotes' },
  { to: '/orders',  icon: '🛒', label: 'Orders' },
];

export default function Layout({ children, pageTitle }) {
  const navigate  = useNavigate();
  const auth      = getAuth();
  const user      = auth?.user;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [orgName, setOrgName] = useState('');

  // Close sidebar on route change (mobile)
  useEffect(() => { setSidebarOpen(false); }, [pageTitle]);

  // Derive initials for avatar
  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
    : '?';

  // Try to show the org hostname
  useEffect(() => {
    if (auth?.instanceUrl) {
      try {
        const host = new URL(auth.instanceUrl).hostname;
        setOrgName(host.split('.')[0]);
      } catch (_) {}
    }
  }, [auth?.instanceUrl]);

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="app-shell">
      {/* Sidebar overlay (mobile) */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="logo-mark">
            <div className="logo-icon">☁️</div>
            <div>
              <div className="logo-text">Revenue Cloud</div>
              <div className="logo-sub">Portal</div>
            </div>
          </div>
        </div>

        <div className="sidebar-nav">
          <div className="nav-section-label">Navigation</div>
          {NAV.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="user-row">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <div className="user-name">{user?.name ?? 'Salesforce User'}</div>
              <div className="user-email">{user?.email ?? orgName}</div>
            </div>
            <button className="logout-btn" onClick={handleLogout} title="Log out">⎋</button>
          </div>
        </div>
      </nav>

      {/* Main area */}
      <div className="main-area">
        <header className="top-bar">
          <button className="hamburger" onClick={() => setSidebarOpen(s => !s)}>☰</button>
          <span className="top-bar-title">{pageTitle}</span>
          {orgName && <span className="top-bar-org">🔗 {orgName}</span>}
        </header>

        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
}
