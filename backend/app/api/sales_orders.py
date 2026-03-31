from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import SalesOrder, SalesOrderItem, Customer, Product, StockEntry, StockMovement
from app.schemas.schemas import SOCreate, CustomerCreate, CustomerOut
from app.api.stock import check_and_create_alerts

router = APIRouter(prefix="/sales-orders", tags=["sales-orders"])

def so_to_dict(so: SalesOrder, db: Session) -> dict:
    customer = db.query(Customer).filter(Customer.id == so.customer_id).first()
    items = []
    for item in so.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "",
            "product_sku": product.sku if product else "",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.quantity * item.unit_price
        })
    return {
        "id": so.id,
        "so_number": so.so_number,
        "customer_id": so.customer_id,
        "customer_name": customer.name if customer else "",
        "status": so.status,
        "total_amount": so.total_amount,
        "shipping_address": so.shipping_address,
        "notes": so.notes,
        "created_at": so.created_at.isoformat() if so.created_at else None,
        "items": items
    }

@router.get("/customers")
def list_customers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Customer).all()

@router.post("/customers")
def create_customer(data: CustomerCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/")
def list_sos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    sos = db.query(SalesOrder).order_by(SalesOrder.created_at.desc()).all()
    return [so_to_dict(so, db) for so in sos]

@router.post("/")
def create_so(data: SOCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check stock availability
    for item in data.items:
        from sqlalchemy import func
        total = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == item.product_id).scalar() or 0
        if total < item.quantity:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name if product else item.product_id}")
    count = db.query(SalesOrder).count()
    so_number = f"SO-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
    total = sum(i.quantity * i.unit_price for i in data.items)
    so = SalesOrder(
        so_number=so_number,
        customer_id=data.customer_id,
        status="pending",
        total_amount=total,
        shipping_address=data.shipping_address,
        notes=data.notes,
        created_by=current_user.id
    )
    db.add(so)
    db.flush()
    for item in data.items:
        soi = SalesOrderItem(
            sales_order_id=so.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(soi)
    db.commit()
    db.refresh(so)
    return so_to_dict(so, db)

@router.put("/{so_id}/status")
def update_so_status(so_id: int, status: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).first()
    if not so:
        raise HTTPException(status_code=404, detail="SO not found")
    valid = ["pending", "confirmed", "picked", "shipped", "delivered", "cancelled"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status")
    # Deduct stock when shipped
    if status == "shipped" and so.status not in ["shipped", "delivered"]:
        for item in so.items:
            entry = db.query(StockEntry).filter(
                StockEntry.product_id == item.product_id,
                StockEntry.warehouse_id == 1
            ).first()
            if not entry or entry.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock to ship")
            entry.quantity -= item.quantity
            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                movement_type="out", quantity=item.quantity,
                reference=so.so_number, created_by=current_user.id
            )
            db.add(movement)
        db.commit()
        for item in so.items:
            check_and_create_alerts(item.product_id, db)
    so.status = status
    db.commit()
    return so_to_dict(so, db)
