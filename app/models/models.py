from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("RolPermiso", back_populates="rol")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rol = relationship("Role", back_populates="usuarios")
    ventas = relationship("Venta", back_populates="usuario")
    devoluciones = relationship("Devolucion", back_populates="usuario")
    carrito = relationship("CarritoCompras", back_populates="usuario")

class Funcion(Base):
    __tablename__ = "funciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    permisos = relationship("Permiso", back_populates="funcion")

class Accion(Base):
    __tablename__ = "acciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    permisos = relationship("Permiso", back_populates="accion")

class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    funcion_id = Column(Integer, ForeignKey("funciones.id", ondelete="CASCADE"), nullable=False)
    accion_id = Column(Integer, ForeignKey("acciones.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint('funcion_id', 'accion_id', name='unique_funcion_accion'),)

    funcion = relationship("Funcion", back_populates="permisos")
    accion = relationship("Accion", back_populates="permisos")
    roles = relationship("RolPermiso", back_populates="permiso")

class RolPermiso(Base):
    __tablename__ = "rol_permisos"

    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permiso_id = Column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True)

    rol = relationship("Role", back_populates="permisos")
    permiso = relationship("Permiso", back_populates="roles")

class Campus(Base):
    __tablename__ = "campus"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=True)
    celular = Column(String(20), nullable=True)

    estudiantes = relationship("Estudiante", back_populates="campus")

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=True)
    correo = Column(String(150), unique=True, nullable=True)
    celular = Column(String(20), nullable=True)
    campus_id = Column(Integer, ForeignKey("campus.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    sexo = Column(String(20), nullable=True)
    fecha_nacimiento = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campus = relationship("Campus", back_populates="estudiantes")
    usuario = relationship("Usuario")
    gestiones = relationship("EstudianteGestion", back_populates="estudiante")
    responsables = relationship("Responsable", back_populates="estudiante")
    descuentos = relationship("DescuentoEstudiante", back_populates="estudiante")
    ventas = relationship("Venta", back_populates="estudiante")

class Gestion(Base):
    __tablename__ = "gestion"

    id = Column(Integer, primary_key=True, index=True)
    nro = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('nro', 'anio', name='unique_gestion_nro_anio'),)

    estudiantes = relationship("EstudianteGestion", back_populates="gestion")

class EstudianteGestion(Base):
    __tablename__ = "estudiante_gestion"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    gestion_id = Column(Integer, ForeignKey("gestion.id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (UniqueConstraint('estudiante_id', 'gestion_id', name='unique_estudiante_gestion'),)

    estudiante = relationship("Estudiante", back_populates="gestiones")
    gestion = relationship("Gestion", back_populates="estudiantes")

class Parentesco(Base):
    __tablename__ = "parentesco"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

class Responsable(Base):
    __tablename__ = "responsables"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    parentesco_id = Column(Integer, ForeignKey("parentesco.id"), nullable=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=True)
    correo = Column(String(150), nullable=True)
    celular = Column(String(20), nullable=True)

    estudiante = relationship("Estudiante", back_populates="responsables")
    parentesco = relationship("Parentesco")

class CategoriaProducto(Base):
    __tablename__ = "categorias_producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)

    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_producto.id"), nullable=True)
    codigo = Column(String(50), unique=True, nullable=True)
    stock_actual = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    categoria = relationship("CategoriaProducto", back_populates="productos")
    precios = relationship("PrecioProducto", back_populates="producto")
    descuentos = relationship("DescuentoEstudiante", back_populates="producto")


class ListaPrecio(Base):
    __tablename__ = "listas_precios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)

    precios = relationship("PrecioProducto", back_populates="lista_precio")

class PrecioProducto(Base):
    __tablename__ = "precios_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    lista_precios_id = Column(Integer, ForeignKey("listas_precios.id", ondelete="CASCADE"), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (UniqueConstraint('producto_id', 'lista_precios_id', name='unique_producto_lista'),)

    producto = relationship("Producto", back_populates="precios")
    lista_precio = relationship("ListaPrecio", back_populates="precios")


class DescuentoEstudiante(Base):
    __tablename__ = "descuentos_estudiante"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    lista_precios_id = Column(Integer, ForeignKey("listas_precios.id", ondelete="CASCADE"), nullable=True) # Nullable for backward compatibility or if not strictly required immediately
    porcentaje_descuento = Column(Numeric(5, 2), nullable=True)
    monto_descuento = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('estudiante_id', 'producto_id', name='unique_estudiante_producto'),)

    estudiante = relationship("Estudiante", back_populates="descuentos")
    producto = relationship("Producto", back_populates="descuentos")
    lista_precio = relationship("ListaPrecio")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=True)
    cliente_nombre = Column(String(150), nullable=True)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    estado = Column(String(20), default='COMPLETADA')
    metodo_pago = Column(String(50), nullable=True)

    usuario = relationship("Usuario", back_populates="ventas")
    estudiante = relationship("Estudiante", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")

class Devolucion(Base):
    __tablename__ = "devoluciones"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(20), nullable=False)
    referencia_id = Column(Integer, nullable=True)
    motivo = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    estado = Column(String(20), default='PENDIENTE')

    usuario = relationship("Usuario", back_populates="devoluciones")
    detalles = relationship("DetalleDevolucion", back_populates="devolucion", cascade="all, delete-orphan")

class DetalleDevolucion(Base):
    __tablename__ = "detalle_devolucion"

    id = Column(Integer, primary_key=True, index=True)
    devolucion_id = Column(Integer, ForeignKey("devoluciones.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)

    devolucion = relationship("Devolucion", back_populates="detalles")
    producto = relationship("Producto")

class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo_movimiento = Column(String(50), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    referencia_tabla = Column(String(50), nullable=True)
    referencia_id = Column(Integer, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    producto = relationship("Producto")
    usuario = relationship("Usuario")

class CarritoCompras(Base):
    __tablename__ = "carrito_compras"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('usuario_id', 'producto_id', name='unique_usuario_producto_carrito'),)

    usuario = relationship("Usuario", back_populates="carrito")
    producto = relationship("Producto")




class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(255), nullable=True)
    celular = Column(String(20), nullable=True)
    nombre_responsable = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ingresos = relationship("Ingreso", back_populates="proveedor")


class Ingreso(Base):
    __tablename__ = "ingresos"

    id = Column(Integer, primary_key=True, index=True)
    proveedor = Column(String(150), nullable=True)  # Deprecated, kept for backward compatibility
    proveedor_id = Column(Integer, ForeignKey("proveedores.id", ondelete="SET NULL"), nullable=True)
    nro_factura = Column(String(50), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    estado = Column(String(20), default='COMPLETADO')
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario")
    proveedor = relationship("Proveedor", back_populates="ingresos")
    detalles = relationship("DetalleIngreso", back_populates="ingreso", cascade="all, delete-orphan")


class DetalleIngreso(Base):
    __tablename__ = "detalle_ingreso"

    id = Column(Integer, primary_key=True, index=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    ingreso = relationship("Ingreso", back_populates="detalles")
    producto = relationship("Producto")
