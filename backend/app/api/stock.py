from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import StockEntry, StockMovement, Product, Warehouse, Alert
from app.schemas.schemas import StockAdjust

router = APIRouter(prefix="/stock", tags=["stock"])

def check_and_create_alerts(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return
    total = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == product_id).scalar() or 0
    db.query(Alert).filter(Alert.product_id == product_id, Alert.is_read == False).delete()
    if total == 0:
        alert = Alert(alert_type="out_of_stock", product_id=product_id,
                      message=f"🚨 {product.name} is OUT OF STOCK")
        db.add(alert)
    elif total <= product.reorder_point:
        alert = Alert(alert_type="low_stock", product_id=product_id,
                      message=f"⚠️ {product.name} is LOW on stock ({total} remaining, reorder at {product.reorder_point})")
        db.add(alert)
    elif total >= product.max_stock:
        alert = Alert(alert_type="overstock", product_id=product_id,
                      message=f"📦 {product.name} is OVERSTOCKED ({total} units, max is {product.max_stock})")
        db.add(alert)
    db.commit()

@router.get("/")
def get_stock_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    entries = db.query(StockEntry).all()
    result = []
    for e in entries:
        product = db.query(Product).filter(Product.id == e.product_id).first()
        warehouse = db.query(Warehouse).filter(Warehouse.id == e.warehouse_id).first()
        result.append({
            "id": e.id,
            "product_id": e.product_id,
            "product_name": product.name if product else "",
            "product_sku": product.sku if product else "",
            "warehouse_id": e.warehouse_id,
            "warehouse_name": warehouse.name if warehouse else "",
            "quantity": e.quantity,
            "reorder_point": product.reorder_point if product else 0,
            "status": "out" if e.quantity == 0 else ("low" if e.quantity <= (product.reorder_point if product else 0) else "ok")
        })
    return result

@router.post("/adjust")
def adjust_stock(data: StockAdjust, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    entry = db.query(StockEntry).filter(
        StockEntry.product_id == data.product_id,
        StockEntry.warehouse_id == data.warehouse_id
    ).first()
    if not entry:
        entry = StockEntry(product_id=data.product_id, warehouse_id=data.warehouse_id, quantity=0)
        db.add(entry)
        db.flush()
    if data.movement_type == "in":
        entry.quantity += data.quantity
    elif data.movement_type == "out":
        if entry.quantity < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        entry.quantity -= data.quantity
    elif data.movement_type == "adjustment":
        entry.quantity = data.quantity
    movement = StockMovement(
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        note=data.note,
        created_by=current_user.id
    )
    db.add(movement)
    db.commit()
    check_and_create_alerts(data.product_id, db)
    return {"detail": "Stock updated", "new_quantity": entry.quantity}

@router.get("/movements")
def get_movements(db: Session = Depends(get_db), _=Depends(get_current_user)):
    movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(100).all()
    result = []
    for m in movements:
        product = db.query(Product).filter(Product.id == m.product_id).first()
        warehouse = db.query(Warehouse).filter(Warehouse.id == m.warehouse_id).first()
        result.append({
            "id": m.id,
            "product_name": product.name if product else "",
            "warehouse_name": warehouse.name if warehouse else "",
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "note": m.note,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })
    return result

@router.get("/warehouses")
def list_warehouses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Warehouse).filter(Warehouse.is_active == True).all()

@router.post("/warehouses")
def create_warehouse(name: str, location: str = "", db: Session = Depends(get_db), _=Depends(get_current_user)):
    w = Warehouse(name=name, location=location)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w
