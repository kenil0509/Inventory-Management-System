from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ── User ──────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "staff"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True

# ── Category ──────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    class Config: from_attributes = True

# ── Product ───────────────────────────────────────────
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit: str = "piece"
    cost_price: float = 0.0
    selling_price: float = 0.0
    reorder_point: int = 10
    max_stock: int = 500
    barcode: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_point: Optional[int] = None
    max_stock: Optional[int] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str]
    category_id: Optional[int]
    unit: str
    cost_price: float
    selling_price: float
    reorder_point: int
    max_stock: int
    barcode: Optional[str]
    is_active: bool
    created_at: datetime
    total_stock: Optional[int] = 0
    class Config: from_attributes = True

# ── Stock ─────────────────────────────────────────────
class StockAdjust(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    movement_type: str  # in, out, adjustment
    note: Optional[str] = None

class StockEntryOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: int
    class Config: from_attributes = True

# ── Supplier ──────────────────────────────────────────
class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    lead_time_days: int = 7

class SupplierOut(BaseModel):
    id: int
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    payment_terms: Optional[str]
    lead_time_days: int
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True

# ── Purchase Order ────────────────────────────────────
class POItemCreate(BaseModel):
    product_id: int
    quantity_ordered: int
    unit_price: float

class POCreate(BaseModel):
    supplier_id: int
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[POItemCreate]

class POItemOut(BaseModel):
    id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_price: float
    product: Optional[dict] = None
    class Config: from_attributes = True

class POOut(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    status: str
    total_amount: float
    expected_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    supplier: Optional[dict] = None
    items: List[POItemOut] = []
    class Config: from_attributes = True

# ── Customer ──────────────────────────────────────────
class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerOut(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    class Config: from_attributes = True

# ── Sales Order ───────────────────────────────────────
class SOItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class SOCreate(BaseModel):
    customer_id: int
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    items: List[SOItemCreate]

class SOItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    class Config: from_attributes = True

class SOOut(BaseModel):
    id: int
    so_number: str
    customer_id: int
    status: str
    total_amount: float
    shipping_address: Optional[str]
    notes: Optional[str]
    created_at: datetime
    customer: Optional[dict] = None
    items: List[SOItemOut] = []
    class Config: from_attributes = True

# ── Alert ─────────────────────────────────────────────
class AlertOut(BaseModel):
    id: int
    alert_type: str
    product_id: Optional[int]
    message: str
    is_read: bool
    created_at: datetime
    class Config: from_attributes = True
