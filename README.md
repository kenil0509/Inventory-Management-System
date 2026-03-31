# 📦 InvenTrack — Inventory Management System

Full-stack IMS built with **FastAPI + PostgreSQL + HTML/CSS/JS (Bootstrap-style custom)**.

---

## 🗂️ Project Structure

```
ims/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── seed.py                  # Demo data seeder
│   ├── requirements.txt
│   ├── .env                     # DB + JWT config
│   └── app/
│       ├── core/
│       │   ├── config.py        # Settings (pydantic-settings)
│       │   ├── database.py      # SQLAlchemy engine + session
│       │   └── security.py      # JWT auth, password hashing
│       ├── models/
│       │   └── models.py        # All DB models (12 tables)
│       ├── schemas/
│       │   └── schemas.py       # Pydantic request/response models
│       └── api/
│           ├── auth.py          # Login, register, /me
│           ├── products.py      # Product + category CRUD
│           ├── stock.py         # Stock levels, adjustments, movements
│           ├── suppliers.py     # Supplier CRUD
│           ├── purchase_orders.py  # Full PO lifecycle
│           ├── sales_orders.py  # Full SO lifecycle + customers
│           ├── alerts.py        # Alerts + Dashboard stats
│           └── reports.py       # Valuation, forecast, top products
└── frontend/
    ├── pages/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── products.html
    │   ├── stock.html
    │   ├── movements.html
    │   ├── suppliers.html
    │   ├── purchase-orders.html
    │   ├── sales-orders.html
    │   ├── customers.html
    │   ├── alerts.html
    │   ├── reports.html
    │   └── forecast.html
    └── static/
        ├── css/main.css         # Full custom design system
        └── js/
            ├── app.js           # API client, auth, toast, helpers
            └── sidebar.js       # Sidebar HTML template
```

---

## ⚙️ Setup Instructions

### 1. PostgreSQL Database

```bash
# Create DB and user
psql -U postgres
CREATE DATABASE ims_db;
CREATE USER ims_user WITH PASSWORD 'ims_password';
GRANT ALL PRIVILEGES ON DATABASE ims_db TO ims_user;
\q
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (edit if needed)
# DATABASE_URL=postgresql://ims_user:ims_password@localhost:5432/ims_db

# Seed demo data
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be live at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 3. Frontend Setup

The frontend is plain HTML — no build step needed.

```bash
# Option A: Python simple server (from project root)
cd frontend
python -m http.server 3000

# Option B: VS Code Live Server extension
# Right-click frontend/pages/login.html → Open with Live Server

# Option C: Any static file server
npx serve frontend -p 3000
```

Open: **http://localhost:3000/pages/login.html**

---

## 🔐 Demo Credentials

| Role       | Email              | Password    |
|------------|--------------------|-------------|
| Super Admin| admin@ims.com      | admin123    |
| Manager    | manager@ims.com    | manager123  |
| Staff      | staff@ims.com      | staff123    |

---

## 📋 Features

### Core Modules
- **Dashboard** — KPI stats, stock by category chart, order status chart, recent movements, active alerts
- **Products** — Full CRUD with categories, cost/selling price, reorder thresholds, stock visibility
- **Stock Levels** — Real-time qty per warehouse, visual stock bar, quick adjust modal
- **Stock Movements** — Complete audit trail of every stock change
- **Alerts** — Auto-generated for low stock, out of stock, overstock — with read/unread management

### Procurement
- **Suppliers** — Vendor profiles with lead times, payment terms, contact info
- **Purchase Orders** — Full lifecycle: Draft → Submitted → Approved → Received (auto-updates stock)

### Sales
- **Sales Orders** — Full lifecycle: Pending → Confirmed → Picked → Shipped (auto-deducts stock) → Delivered
- **Customers** — Customer database linked to sales orders

### Analytics
- **Reports** — Stock valuation (cost vs retail), top products by revenue, overall summary
- **Demand Forecast** — Days-of-stock calculation, avg daily demand, reorder suggestions per SKU

---

## 🗄️ Database Schema

| Table                | Purpose                          |
|----------------------|----------------------------------|
| users                | Auth + role management           |
| categories           | Product categories               |
| products             | Product catalog with pricing     |
| warehouses           | Warehouse/location management    |
| stock_entries        | Current stock qty per product+WH |
| stock_movements      | Immutable movement audit trail   |
| suppliers            | Vendor profiles                  |
| purchase_orders      | PO headers                       |
| purchase_order_items | PO line items                    |
| customers            | Customer profiles                |
| sales_orders         | SO headers                       |
| sales_order_items    | SO line items                    |
| alerts               | Auto-generated stock alerts      |

---

## 🔌 API Endpoints Summary

```
POST   /api/auth/login
POST   /api/auth/register
GET    /api/auth/me

GET    /api/products/
POST   /api/products/
PUT    /api/products/{id}
DELETE /api/products/{id}
GET    /api/products/categories/all

GET    /api/stock/
POST   /api/stock/adjust
GET    /api/stock/movements
GET    /api/stock/warehouses

GET    /api/suppliers/
POST   /api/suppliers/
PUT    /api/suppliers/{id}

GET    /api/purchase-orders/
POST   /api/purchase-orders/
PUT    /api/purchase-orders/{id}/status

GET    /api/sales-orders/
POST   /api/sales-orders/
PUT    /api/sales-orders/{id}/status
GET    /api/sales-orders/customers
POST   /api/sales-orders/customers

GET    /api/alerts/
PUT    /api/alerts/{id}/read
PUT    /api/alerts/read-all

GET    /api/dashboard/stats
GET    /api/dashboard/recent-movements
GET    /api/dashboard/stock-by-category

GET    /api/reports/stock-valuation
GET    /api/reports/demand-forecast
GET    /api/reports/top-products
GET    /api/reports/summary
```

---

## 🚀 Production Checklist

- [ ] Change `SECRET_KEY` in `.env` to a random 64-char string
- [ ] Set `CORS allow_origins` to your domain only (not `*`)
- [ ] Use Alembic for DB migrations instead of `create_all`
- [ ] Add HTTPS (Nginx + Certbot)
- [ ] Set up PostgreSQL backups
- [ ] Add rate limiting to auth endpoints
