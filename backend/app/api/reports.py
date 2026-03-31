from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Product, StockEntry, StockMovement, SalesOrderItem, SalesOrder, PurchaseOrder

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/stock-valuation")
def stock_valuation(db: Session = Depends(get_db), _=Depends(get_current_user)):
    products = db.query(Product).filter(Product.is_active == True).all()
    result = []
    total_cost = 0
    total_retail = 0
    for p in products:
        qty = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == p.id).scalar() or 0
        cost_val = qty * p.cost_price
        retail_val = qty * p.selling_price
        total_cost += cost_val
        total_retail += retail_val
        result.append({
            "sku": p.sku,
            "name": p.name,
            "quantity": qty,
            "cost_price": p.cost_price,
            "selling_price": p.selling_price,
            "cost_value": round(cost_val, 2),
            "retail_value": round(retail_val, 2),
            "potential_profit": round(retail_val - cost_val, 2)
        })
    return {
        "items": sorted(result, key=lambda x: x["cost_value"], reverse=True),
        "totals": {
            "total_cost_value": round(total_cost, 2),
            "total_retail_value": round(total_retail, 2),
            "total_potential_profit": round(total_retail - total_cost, 2)
        }
    }

@router.get("/demand-forecast")
def demand_forecast(db: Session = Depends(get_db), _=Depends(get_current_user)):
    products = db.query(Product).filter(Product.is_active == True).all()
    result = []
    for p in products:
        # Get sold quantities from delivered SOs
        delivered_sos = db.query(SalesOrder).filter(SalesOrder.status == "delivered").all()
        total_sold = 0
        for so in delivered_sos:
            items = db.query(SalesOrderItem).filter(
                SalesOrderItem.sales_order_id == so.id,
                SalesOrderItem.product_id == p.id
            ).all()
            total_sold += sum(i.quantity for i in items)
        current_stock = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == p.id).scalar() or 0
        # Simple forecast: avg daily = total_sold / 30 days
        avg_daily = round(total_sold / 30, 2) if total_sold > 0 else 0.1
        days_remaining = int(current_stock / avg_daily) if avg_daily > 0 else 999
        reorder_needed = current_stock <= p.reorder_point
        suggested_order = max(0, p.max_stock - current_stock) if reorder_needed else 0
        result.append({
            "product_id": p.id,
            "sku": p.sku,
            "name": p.name,
            "current_stock": current_stock,
            "reorder_point": p.reorder_point,
            "total_sold_30d": total_sold,
            "avg_daily_demand": avg_daily,
            "days_of_stock": min(days_remaining, 365),
            "reorder_needed": reorder_needed,
            "suggested_order_qty": suggested_order,
            "status": "critical" if current_stock == 0 else ("reorder" if reorder_needed else "healthy")
        })
    return sorted(result, key=lambda x: x["days_of_stock"])

@router.get("/top-products")
def top_products(db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = db.query(
        SalesOrderItem.product_id,
        func.sum(SalesOrderItem.quantity).label("total_qty"),
        func.sum(SalesOrderItem.quantity * SalesOrderItem.unit_price).label("total_revenue")
    ).group_by(SalesOrderItem.product_id).order_by(func.sum(SalesOrderItem.quantity).desc()).limit(10).all()
    result = []
    for item in items:
        p = db.query(Product).filter(Product.id == item.product_id).first()
        result.append({
            "product_name": p.name if p else "",
            "sku": p.sku if p else "",
            "total_qty_sold": item.total_qty,
            "total_revenue": round(item.total_revenue, 2)
        })
    return result

@router.get("/summary")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_pos = db.query(PurchaseOrder).count()
    total_sos = db.query(SalesOrder).count()
    delivered_sos = db.query(SalesOrder).filter(SalesOrder.status == "delivered").all()
    total_revenue = sum(so.total_amount for so in delivered_sos)
    return {
        "total_products": total_products,
        "total_purchase_orders": total_pos,
        "total_sales_orders": total_sos,
        "total_revenue": round(total_revenue, 2)
    }
