"""
Run this once to populate the database with demo data.
  cd backend
  python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine
from app.models.models import Base, User, Category, Product, Warehouse, StockEntry, Supplier, Customer, Alert
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed():
    # ── Users ──────────────────────────────────────────
    if not db.query(User).first():
        users = [
            User(name="Super Admin",  email="admin@ims.com",   hashed_password=get_password_hash("admin123"),   role="superadmin"),
            User(name="Warehouse Mgr",email="manager@ims.com", hashed_password=get_password_hash("manager123"), role="manager"),
            User(name="Staff User",   email="staff@ims.com",   hashed_password=get_password_hash("staff123"),   role="staff"),
        ]
        db.add_all(users)
        db.commit()
        print("✅ Users seeded")

    # ── Categories ─────────────────────────────────────
    if not db.query(Category).first():
        cats = [
            Category(name="Electronics",    description="Electronic devices and components"),
            Category(name="Office Supplies", description="Stationery and office items"),
            Category(name="Furniture",       description="Office and warehouse furniture"),
            Category(name="Raw Materials",   description="Production raw materials"),
            Category(name="Packaging",       description="Boxes, tapes, wrapping"),
        ]
        db.add_all(cats)
        db.commit()
        print("✅ Categories seeded")

    # ── Warehouse ──────────────────────────────────────
    if not db.query(Warehouse).first():
        whs = [
            Warehouse(name="Main Warehouse",   location="Ahmedabad, Gujarat"),
            Warehouse(name="Secondary Store",  location="Surat, Gujarat"),
        ]
        db.add_all(whs)
        db.commit()
        print("✅ Warehouses seeded")

    # ── Products ───────────────────────────────────────
    if not db.query(Product).first():
        cats = {c.name: c.id for c in db.query(Category).all()}
        products = [
            Product(sku="ELEC-001", name="Laptop Dell XPS 15",     category_id=cats["Electronics"],    unit="piece", cost_price=75000, selling_price=89999, reorder_point=5,  max_stock=50),
            Product(sku="ELEC-002", name="Wireless Mouse Logitech", category_id=cats["Electronics"],    unit="piece", cost_price=800,   selling_price=1299,  reorder_point=20, max_stock=200),
            Product(sku="ELEC-003", name="Mechanical Keyboard",     category_id=cats["Electronics"],    unit="piece", cost_price=2500,  selling_price=3999,  reorder_point=10, max_stock=100),
            Product(sku="ELEC-004", name="27\" Monitor 4K",         category_id=cats["Electronics"],    unit="piece", cost_price=25000, selling_price=32000, reorder_point=5,  max_stock=30),
            Product(sku="ELEC-005", name="USB-C Hub 7-in-1",        category_id=cats["Electronics"],    unit="piece", cost_price=1200,  selling_price=1899,  reorder_point=15, max_stock=150),
            Product(sku="OFF-001",  name="A4 Paper Ream 500 sheets",category_id=cats["Office Supplies"],unit="ream",  cost_price=180,   selling_price=250,   reorder_point=50, max_stock=500),
            Product(sku="OFF-002",  name="Ball Pen (Box of 10)",    category_id=cats["Office Supplies"],unit="box",   cost_price=50,    selling_price=90,    reorder_point=30, max_stock=300),
            Product(sku="OFF-003",  name="Sticky Notes Pack",       category_id=cats["Office Supplies"],unit="pack",  cost_price=40,    selling_price=75,    reorder_point=25, max_stock=200),
            Product(sku="FURN-001", name="Ergonomic Office Chair",  category_id=cats["Furniture"],      unit="piece", cost_price=8000,  selling_price=12500, reorder_point=3,  max_stock=20),
            Product(sku="FURN-002", name="Standing Desk Adjustable",category_id=cats["Furniture"],      unit="piece", cost_price=15000, selling_price=22000, reorder_point=2,  max_stock=15),
            Product(sku="RAW-001",  name="Aluminium Sheet 1mm",     category_id=cats["Raw Materials"],  unit="kg",    cost_price=200,   selling_price=280,   reorder_point=100,max_stock=1000),
            Product(sku="RAW-002",  name="Polypropylene Granules",  category_id=cats["Raw Materials"],  unit="kg",    cost_price=90,    selling_price=130,   reorder_point=200,max_stock=2000),
            Product(sku="PACK-001", name="Cardboard Box Large",     category_id=cats["Packaging"],      unit="piece", cost_price=25,    selling_price=45,    reorder_point=100,max_stock=1000),
            Product(sku="PACK-002", name="Bubble Wrap Roll 50m",    category_id=cats["Packaging"],      unit="roll",  cost_price=350,   selling_price=550,   reorder_point=20, max_stock=100),
        ]
        db.add_all(products)
        db.commit()
        print("✅ Products seeded")

    # ── Stock ──────────────────────────────────────────
    if not db.query(StockEntry).first():
        products = db.query(Product).all()
        wh1 = db.query(Warehouse).first()
        import random
        for p in products:
            # Give some products low stock intentionally
            if p.sku in ["ELEC-001", "FURN-002", "RAW-001"]:
                qty = p.reorder_point - 2  # below reorder point
            elif p.sku in ["PACK-001"]:
                qty = 0  # out of stock
            else:
                qty = random.randint(p.reorder_point + 1, p.reorder_point * 5)
            db.add(StockEntry(product_id=p.id, warehouse_id=wh1.id, quantity=qty))
        db.commit()
        print("✅ Stock seeded")

    # ── Suppliers ──────────────────────────────────────
    if not db.query(Supplier).first():
        suppliers = [
            Supplier(name="TechSource Pvt Ltd",    contact_person="Rahul Mehta",   email="rahul@techsource.in",  phone="9876543210", payment_terms="Net 30", lead_time_days=5),
            Supplier(name="Global Office Mart",    contact_person="Priya Shah",    email="priya@globaloffice.in",phone="9876543211", payment_terms="Net 15", lead_time_days=3),
            Supplier(name="IndiaFurnishings Co",   contact_person="Amit Patel",    email="amit@indiafurn.in",    phone="9876543212", payment_terms="Net 45", lead_time_days=14),
            Supplier(name="RawMat Industries",     contact_person="Sunita Desai",  email="sunita@rawmat.in",     phone="9876543213", payment_terms="Net 30", lead_time_days=7),
            Supplier(name="PackPro Solutions",     contact_person="Vikram Joshi",  email="vikram@packpro.in",    phone="9876543214", payment_terms="Net 10", lead_time_days=2),
        ]
        db.add_all(suppliers)
        db.commit()
        print("✅ Suppliers seeded")

    # ── Customers ──────────────────────────────────────
    if not db.query(Customer).first():
        customers = [
            Customer(name="Infosys Ltd",         email="procurement@infosys.com", phone="8000000001", address="Bangalore, Karnataka"),
            Customer(name="Tata Consultancy",    email="purchase@tcs.com",        phone="8000000002", address="Mumbai, Maharashtra"),
            Customer(name="Reliance Industries", email="orders@reliance.com",     phone="8000000003", address="Ahmedabad, Gujarat"),
            Customer(name="Wipro Technologies", email="buy@wipro.com",            phone="8000000004", address="Pune, Maharashtra"),
            Customer(name="Zomato India",        email="supply@zomato.com",       phone="8000000005", address="Delhi, NCR"),
        ]
        db.add_all(customers)
        db.commit()
        print("✅ Customers seeded")

    # ── Alerts from low stock ──────────────────────────
    if not db.query(Alert).first():
        from app.api.stock import check_and_create_alerts
        products = db.query(Product).all()
        for p in products:
            check_and_create_alerts(p.id, db)
        print("✅ Alerts generated")

    print("\n🎉 Seed complete!")
    print("   Login: admin@ims.com / admin123")
    print("   Login: manager@ims.com / manager123")

if __name__ == "__main__":
    seed()
    db.close()
