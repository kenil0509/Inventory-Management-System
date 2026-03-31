from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import PurchaseOrder, PurchaseOrderItem, Product, Supplier, StockEntry, StockMovement
from app.schemas.schemas import POCreate
from app.api.stock import check_and_create_alerts

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])

def po_to_dict(po: PurchaseOrder, db: Session) -> dict:
    supplier = db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
    items = []
    for item in po.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "",
            "product_sku": product.sku if product else "",
            "quantity_ordered": item.quantity_ordered,
            "quantity_received": item.quantity_received,
            "unit_price": item.unit_price
        })
    return {
        "id": po.id,
        "po_number": po.po_number,
        "supplier_id": po.supplier_id,
        "supplier_name": supplier.name if supplier else "",
        "status": po.status,
        "total_amount": po.total_amount,
        "expected_date": po.expected_date.isoformat() if po.expected_date else None,
        "notes": po.notes,
        "created_at": po.created_at.isoformat() if po.created_at else None,
        "items": items
    }

@router.get("/")
def list_pos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()
    return [po_to_dict(po, db) for po in pos]

@router.post("/")
def create_po(data: POCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    count = db.query(PurchaseOrder).count()
    po_number = f"PO-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
    total = sum(i.quantity_ordered * i.unit_price for i in data.items)
    po = PurchaseOrder(
        po_number=po_number,
        supplier_id=data.supplier_id,
        status="draft",
        total_amount=total,
        expected_date=data.expected_date,
        notes=data.notes,
        created_by=current_user.id
    )
    db.add(po)
    db.flush()
    for item in data.items:
        poi = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item.product_id,
            quantity_ordered=item.quantity_ordered,
            unit_price=item.unit_price
        )
        db.add(poi)
    db.commit()
    db.refresh(po)
    return po_to_dict(po, db)

@router.get("/{po_id}")
def get_po(po_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    return po_to_dict(po, db)

@router.put("/{po_id}/status")
def update_po_status(po_id: int, status: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    valid = ["draft", "submitted", "approved", "received", "cancelled"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid}")
    po.status = status
    # On receive, add stock
    if status == "received":
        for item in po.items:
            entry = db.query(StockEntry).filter(
                StockEntry.product_id == item.product_id,
                StockEntry.warehouse_id == 1
            ).first()
            if not entry:
                entry = StockEntry(product_id=item.product_id, warehouse_id=1, quantity=0)
                db.add(entry)
                db.flush()
            qty = item.quantity_ordered - item.quantity_received
            entry.quantity += qty
            item.quantity_received = item.quantity_ordered
            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                movement_type="in", quantity=qty,
                reference=po.po_number, created_by=current_user.id
            )
            db.add(movement)
        db.commit()
        for item in po.items:
            check_and_create_alerts(item.product_id, db)
    db.commit()
    return po_to_dict(po, db)
