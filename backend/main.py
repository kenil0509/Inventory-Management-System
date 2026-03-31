from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.models import Base
from app.api import auth, products, stock, suppliers, purchase_orders, sales_orders, alerts, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="IMS - Inventory Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,            prefix="/api")
app.include_router(products.router,        prefix="/api")
app.include_router(stock.router,           prefix="/api")
app.include_router(suppliers.router,       prefix="/api")
app.include_router(purchase_orders.router, prefix="/api")
app.include_router(sales_orders.router,    prefix="/api")
app.include_router(alerts.router,          prefix="/api")
app.include_router(alerts.dashboard_router,prefix="/api")
app.include_router(reports.router,         prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "IMS"}