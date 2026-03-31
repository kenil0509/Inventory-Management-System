from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Supplier
from app.schemas.schemas import SupplierCreate, SupplierOut

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("/", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Supplier).filter(Supplier.is_active == True).all()

@router.post("/", response_model=SupplierOut)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = Supplier(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return s

@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, data: SupplierCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    s.is_active = False
    db.commit()
    return {"detail": "Supplier removed"}
