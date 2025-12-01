import sys
import os
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.models import Usuario, Producto, CategoriaProducto, Ingreso, Venta, DetalleIngreso, DetalleVenta, MovimientoInventario
from app.services import ingreso_service
from app.services import ventas as venta_service
from app.schemas.ingreso import IngresoCreate, DetalleIngresoCreate
from app.schemas.venta import VentaCreate, DetalleVentaCreate

def test_inventory_movements():
    db = SessionLocal()
    try:
        print("Starting Inventory Movement Tests...")

        # Setup: Get a user and a product (or create if needed)
        user = db.query(Usuario).first()
        if not user:
            print("No user found. Please ensure database is seeded.")
            return

        # Create a test category if needed
        category = db.query(CategoriaProducto).filter(CategoriaProducto.nombre == "Test Category").first()
        if not category:
            category = CategoriaProducto(nombre="Test Category")
            db.add(category)
            db.commit()
            db.refresh(category)

        # Create a test product
        product = db.query(Producto).filter(Producto.nombre == "Test Product").first()
        if not product:
            product = Producto(nombre="Test Product", categoria_id=category.id, stock_actual=100)
            db.add(product)
            db.commit()
            db.refresh(product)
        else:
            # Reset stock for consistent testing
            product.stock_actual = 100
            db.add(product)
            db.commit()
            db.refresh(product)

        initial_stock = product.stock_actual
        print(f"Initial Stock: {initial_stock}")

        # --- Test 1: Create Ingreso ---
        print("\n--- Test 1: Create Ingreso ---")
        ingreso_in = IngresoCreate(
            proveedor_id=None,
            nro_factura="TEST-001",
            detalles=[
                DetalleIngresoCreate(producto_id=product.id, cantidad=50, costo_unitario=5.0)
            ]
        )
        
        ingreso = ingreso_service.create_ingreso(db, ingreso_in, user)
        
        db.refresh(product)
        print(f"Ingreso Created. ID: {ingreso.id}, State: {ingreso.estado}")
        print(f"Stock after Ingreso: {product.stock_actual}")
        
        assert ingreso.estado == 'COMPLETADO' or ingreso.estado == 'COMPLETADA' # Allow for schema variation but expect COMPLETADO based on service
        assert product.stock_actual == initial_stock + 50
        print("✅ Create Ingreso Passed")

        # --- Test 2: Cancel Ingreso ---
        print("\n--- Test 2: Cancel Ingreso ---")
        ingreso_service.cancel_ingreso(db, ingreso.id, user)
        
        db.refresh(product)
        db.refresh(ingreso)
        print(f"Ingreso Cancelled. State: {ingreso.estado}")
        print(f"Stock after Cancel Ingreso: {product.stock_actual}")
        
        assert ingreso.estado == 'ANULADO'
        assert product.stock_actual == initial_stock
        print("✅ Cancel Ingreso Passed")

        # --- Test 3: Create Venta ---
        print("\n--- Test 3: Create Venta ---")
        venta_in = VentaCreate(
            estudiante_id=None,
            cliente_nombre="Test Client",
            metodo_pago="Efectivo",
            detalles=[
                DetalleVentaCreate(producto_id=product.id, cantidad=20, precio_unitario=15.0)
            ]
        )
        
        venta = venta_service.create_venta(db, venta_in, user.id)
        
        db.refresh(product)
        print(f"Venta Created. ID: {venta.id}, State: {venta.estado}")
        print(f"Stock after Venta: {product.stock_actual}")
        
        assert venta.estado == 'COMPLETADA'
        assert product.stock_actual == initial_stock - 20
        print("✅ Create Venta Passed")

        # --- Test 4: Cancel Venta ---
        print("\n--- Test 4: Cancel Venta ---")
        venta_service.cancel_venta(db, venta.id, user.id)
        
        db.refresh(product)
        db.refresh(venta)
        print(f"Venta Cancelled. State: {venta.estado}")
        print(f"Stock after Cancel Venta: {product.stock_actual}")
        
        assert venta.estado == 'ANULADA'
        assert product.stock_actual == initial_stock
        print("✅ Cancel Venta Passed")

        print("\n🎉 All Tests Passed!")

    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_inventory_movements()
