from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Product, Category, StockEntry
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut

router = APIRouter(prefix="/products", tags=["products"])

def enrich_product(p: Product, db: Session) -> dict:
    total = db.query(func.sum(StockEntry.quantity)).filter(StockEntry.product_id == p.id).scalar() or 0
    d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
    d["total_stock"] = total
    return d

@router.get("/", response_model=List[dict])
def list_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    q = db.query(Product).filter(Product.is_active == True)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    products = q.all()
    result = [enrich_product(p, db) for p in products]
    if low_stock:
        result = [p for p in result if p["total_stock"] <= p["reorder_point"]]
    return result

@router.post("/", response_model=dict)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return enrich_product(product, db)

@router.get("/{product_id}", response_model=dict)
def get_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return enrich_product(p, db)

@router.put("/{product_id}", response_model=dict)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return enrich_product(p, db)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.is_active = False
    db.commit()
    return {"detail": "Product deactivated"}

# Categories
@router.get("/categories/all", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Category).all()

@router.post("/categories/", response_model=CategoryOut)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
