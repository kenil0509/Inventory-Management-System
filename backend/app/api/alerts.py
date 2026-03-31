from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Alert, Product, StockEntry, PurchaseOrder, SalesOrder, StockMovement

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
def get_alerts(db: Session = Depends(get_db), _=Depends(get_current_user)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    result = []
    for a in alerts:
        d = {c.name: getattr(a, c.name) for c in a.__table__.columns}
        if a.created_at:
            d["created_at"] = a.created_at.isoformat()
        if a.product_id:
            p = db.query(Product).filter(Product.id == a.product_id).first()
            d["product_name"] = p.name if p else ""
        result.append(d)
    return result

@router.put("/{alert_id}/read")
def mark_read(alert_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()
    return {"detail": "Marked as read"}

@router.put("/read-all")
def mark_all_read(db: Session = Depends(get_db), _=Depends(get_current_user)):
    db.query(Alert).filter(Alert.is_read == False).update({"is_read": True})
    db.commit()
    return {"detail": "All alerts marked as read"}

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_stock_value = 0
    low_stock_count = 0
    products = db.query(Product).filter(Product.is_active == True).all()
    for p in products:
        qty = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == p.id).scalar() or 0
        total_stock_value += qty * p.cost_price
        if qty <= p.reorder_point:
            low_stock_count += 1
    pending_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_(["draft", "submitted", "approved"])).count()
    pending_sos = db.query(SalesOrder).filter(SalesOrder.status.in_(["pending", "confirmed", "picked"])).count()
    unread_alerts = db.query(Alert).filter(Alert.is_read == False).count()
    return {
        "total_products": total_products,
        "total_stock_value": round(total_stock_value, 2),
        "low_stock_count": low_stock_count,
        "pending_pos": pending_pos,
        "pending_sos": pending_sos,
        "unread_alerts": unread_alerts
    }

@dashboard_router.get("/recent-movements")
def recent_movements(db: Session = Depends(get_db), _=Depends(get_current_user)):
    movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(10).all()
    result = []
    for m in movements:
        p = db.query(Product).filter(Product.id == m.product_id).first()
        result.append({
            "product_name": p.name if p else "",
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "reference": m.reference,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })
    return result

@dashboard_router.get("/stock-by-category")
def stock_by_category(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.models import Category
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        products = db.query(Product).filter(Product.category_id == cat.id, Product.is_active == True).all()
        total = 0
        for p in products:
            total += db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == p.id).scalar() or 0
        result.append({"category": cat.name, "total_stock": total, "product_count": len(products)})
    return result
