/* Sidebar HTML - injected by each page */
function renderSidebar(containerId = 'sidebar-mount') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
<aside class="sidebar" id="sidebar">
  <div class="sidebar-brand">
    <div class="brand-icon">📦</div>
    <div>
      <div class="brand-name">InvenTrack</div>
      <div class="brand-sub">Inventory Management</div>
    </div>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Overview</div>
    <nav class="sidebar-nav">
      <a href="dashboard.html"><span class="nav-icon">🏠</span> Dashboard</a>
      <a href="alerts.html">
        <span class="nav-icon">🔔</span> Alerts
        <span class="badge-pill" id="alert-badge" style="display:none">0</span>
      </a>
    </nav>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Inventory</div>
    <nav class="sidebar-nav">
      <a href="products.html"><span class="nav-icon">🏷️</span> Products</a>
      <a href="stock.html"><span class="nav-icon">📊</span> Stock Levels</a>
      <a href="movements.html"><span class="nav-icon">↕️</span> Movements</a>
    </nav>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Procurement</div>
    <nav class="sidebar-nav">
      <a href="suppliers.html"><span class="nav-icon">🏭</span> Suppliers</a>
      <a href="purchase-orders.html"><span class="nav-icon">📋</span> Purchase Orders</a>
    </nav>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Sales</div>
    <nav class="sidebar-nav">
      <a href="sales-orders.html"><span class="nav-icon">🛒</span> Sales Orders</a>
      <a href="customers.html"><span class="nav-icon">👥</span> Customers</a>
    </nav>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Analytics</div>
    <nav class="sidebar-nav">
      <a href="reports.html"><span class="nav-icon">📈</span> Reports</a>
      <a href="forecast.html"><span class="nav-icon">🔮</span> Demand Forecast</a>
    </nav>
  </div>

  <div class="sidebar-footer">
    <div class="sidebar-user" id="sidebar-user-info"></div>
  </div>
</aside>`;
}
