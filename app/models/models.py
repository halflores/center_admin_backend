from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, UniqueConstraint, Numeric, Date, Time
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
    niveles_academicos = relationship("NivelAcademicoEstudiante", back_populates="estudiante", cascade="all, delete-orphan")


class NivelAcademicoEstudiante(Base):
    """Asignación de nivel académico a un estudiante basado en evaluación de ubicación"""
    __tablename__ = "niveles_academicos_estudiante"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    gestion_id = Column(Integer, ForeignKey("gestion.id"), nullable=True)
    programa_id = Column(Integer, ForeignKey("programas.id"), nullable=True)
    nivel_id = Column(Integer, ForeignKey("niveles.id"), nullable=True)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=True)
    comentario_evaluacion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    estudiante = relationship("Estudiante", back_populates="niveles_academicos")
    gestion = relationship("Gestion")
    programa = relationship("Programa")
    nivel = relationship("Nivel")
    modulo = relationship("Modulo")

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
    tipo_producto_id = Column(Integer, ForeignKey("tipos_producto.id"), nullable=True)
    codigo = Column(String(50), unique=True, nullable=True)
    stock_actual = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    categoria = relationship("CategoriaProducto", back_populates="productos")
    tipo_producto = relationship("TipoProducto", back_populates="productos")
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
    tipo_transaccion_id = Column(Integer, ForeignKey("tipos_transaccion.id"), nullable=True)
    nro_voucher = Column(String(100), nullable=True)

    usuario = relationship("Usuario", back_populates="ventas")
    estudiante = relationship("Estudiante", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    tipo_transaccion = relationship("TipoTransaccion")

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    descuento = Column(Numeric(10, 2), default=0.00, nullable=False)
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
    anulado = Column(Boolean, default=False)

    producto = relationship("Producto")
    usuario = relationship("Usuario")

class CarritoCompras(Base):
    __tablename__ = "carrito_compras"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    descuento = Column(Numeric(10, 2), default=0.0)
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


# =====================================================
# ESTRUCTURA ACADÉMICA - Programas, Niveles, Módulos
# =====================================================

class Programa(Base):
    __tablename__ = "programas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    niveles = relationship("Nivel", back_populates="programa")


class Nivel(Base):
    __tablename__ = "niveles"

    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("programas.id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(20), nullable=True)  # A1, A2, B1, etc.
    nombre = Column(String(100), nullable=False)  # Fundamentos, Independencia, etc.
    nombre_comercial = Column(String(100), nullable=True)  # Beginner, Elementary, etc.
    orden = Column(Integer, default=0)
    duracion_sugerida = Column(String(50), nullable=True)  # "2-3 Módulos", "4 Meses"
    enfoque_principal = Column(Text, nullable=True)
    duracion_meses = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    programa = relationship("Programa", back_populates="niveles")
    modulos = relationship("Modulo", back_populates="nivel")


class Modulo(Base):
    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, index=True)
    nivel_id = Column(Integer, ForeignKey("niveles.id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(20), nullable=True)  # 1.1, 1.2, 2.1, etc.
    nombre = Column(String(150), nullable=False)  # Foundations, My World, The Past, etc.
    duracion_semanas = Column(Integer, nullable=True)
    horas_presenciales = Column(Integer, nullable=True)
    horas_totales = Column(Integer, nullable=True)
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    nivel = relationship("Nivel", back_populates="modulos")
    cursos = relationship("Curso", back_populates="modulo")


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    modulo_id = Column(Integer, ForeignKey("modulos.id", ondelete="CASCADE"), nullable=False)
    profesor_id = Column(Integer, ForeignKey("profesores.id"), nullable=True)
    campus_id = Column(Integer, ForeignKey("campus.id"), nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    cupo_maximo = Column(Integer, nullable=True)
    estado = Column(String(20), default='ACTIVO')  # ACTIVO, FINALIZADO, CANCELADO
    created_at = Column(DateTime, default=datetime.utcnow)

    modulo = relationship("Modulo", back_populates="cursos")
    profesor = relationship("Profesor", back_populates="cursos")
    campus = relationship("Campus")
    horarios = relationship("Horario", back_populates="curso", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="curso")


class Aula(Base):
    __tablename__ = "aulas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    capacidad = Column(Integer, nullable=True)
    ubicacion = Column(String(100), nullable=True)
    
    horarios = relationship("Horario", back_populates="aula_rel")


class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    dia_semana = Column(String(20), nullable=False)  # Lunes, Martes, etc.
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    aula_id = Column(Integer, ForeignKey("aulas.id"), nullable=True)

    curso = relationship("Curso", back_populates="horarios")
    aula_rel = relationship("Aula", back_populates="horarios")


class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    gestion_id = Column(Integer, ForeignKey("gestion.id"), nullable=False)
    fecha_inscripcion = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default='ACTIVO')  # ACTIVO, RETIRADO, COMPLETADO
    monto_pagado = Column(Numeric(10, 2), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('estudiante_id', 'curso_id', 'gestion_id', name='unique_inscripcion'),)

    estudiante = relationship("Estudiante")
    curso = relationship("Curso", back_populates="inscripciones")
    gestion = relationship("Gestion")


# =====================================================
# PROFESORES
# =====================================================

class NivelFormacion(Base):
    __tablename__ = "niveles_formacion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    profesores = relationship("Profesor", back_populates="nivel_formacion_rel")


class Profesor(Base):
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    ci = Column(String(20), unique=True, nullable=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    sexo = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    celular = Column(String(20), nullable=True)
    correo = Column(String(150), nullable=True)
    nivel_formacion_id = Column(Integer, ForeignKey("niveles_formacion.id"), nullable=True)
    experiencia_anios = Column(Integer, nullable=True)
    comentarios = Column(Text, nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    fecha_salida = Column(Date, nullable=True)
    tipo_contrato = Column(String(50), nullable=True)  # Planta, Contrato, Por horas
    salario_hora = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario")
    nivel_formacion_rel = relationship("NivelFormacion", back_populates="profesores")
    campus_list = relationship("ProfesorCampus", back_populates="profesor")
    cursos = relationship("Curso", back_populates="profesor")
    pagos = relationship("PagoProfesor", back_populates="profesor")


class ProfesorCampus(Base):
    __tablename__ = "profesor_campus"

    profesor_id = Column(Integer, ForeignKey("profesores.id", ondelete="CASCADE"), primary_key=True)
    campus_id = Column(Integer, ForeignKey("campus.id", ondelete="CASCADE"), primary_key=True)
    principal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profesor = relationship("Profesor", back_populates="campus_list")
    campus = relationship("Campus")


class PagoProfesor(Base):
    __tablename__ = "pagos_profesor"

    id = Column(Integer, primary_key=True, index=True)
    profesor_id = Column(Integer, ForeignKey("profesores.id", ondelete="CASCADE"), nullable=False)
    gestion_id = Column(Integer, ForeignKey("gestion.id"), nullable=True)
    # periodo = Column(String(50), nullable=True)  # REMOVED
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    tipo_transaccion_id = Column(Integer, ForeignKey("tipos_transaccion.id"), nullable=True)
    nro_voucher = Column(String(100), nullable=True)  # Required for QR/TRANSFERENCIA
    horas_trabajadas = Column(Integer, nullable=True)
    monto_hora = Column(Numeric(10, 2), nullable=True)
    monto_total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), default='PENDIENTE')  # PENDIENTE, PAGADO, CANCELADO
    fecha_pago = Column(Date, nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profesor = relationship("Profesor", back_populates="pagos")
    gestion = relationship("Gestion")
    usuario = relationship("Usuario")
    tipo_transaccion = relationship("TipoTransaccion")


# =====================================================
# TIPOS DE TRANSACCIÓN - Métodos de pago
# =====================================================

class TipoTransaccion(Base):
    __tablename__ = "tipos_transaccion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)  # QR, TRANSFERENCIA, EFECTIVO
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================
# TIPOS DE PRODUCTO - Clasificación de productos
# =====================================================

class TipoProducto(Base):
    __tablename__ = "tipos_producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)  # SERVICIO, MATERIAL_FISICO, MATERIAL_DIGITAL
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    productos = relationship("Producto", back_populates="tipo_producto")


# =====================================================
# PAQUETES - Agrupación de productos por nivel académico
# =====================================================

class Paquete(Base):
    __tablename__ = "paquetes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    programa_id = Column(Integer, ForeignKey("programas.id"), nullable=True)
    nivel_id = Column(Integer, ForeignKey("niveles.id"), nullable=True)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=True)
    precio_total = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    programa = relationship("Programa")
    nivel = relationship("Nivel")
    modulo = relationship("Modulo")
    productos = relationship("PaqueteProducto", back_populates="paquete", cascade="all, delete-orphan")
    inscripciones = relationship("InscripcionPaquete", back_populates="paquete")


class PaqueteProducto(Base):
    __tablename__ = "paquete_productos"

    id = Column(Integer, primary_key=True, index=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, default=1)

    __table_args__ = (UniqueConstraint('paquete_id', 'producto_id', name='unique_paquete_producto'),)

    paquete = relationship("Paquete", back_populates="productos")
    producto = relationship("Producto")


# =====================================================
# INSCRIPCIÓN A PAQUETE - Seguimiento académico
# =====================================================

class InscripcionPaquete(Base):
    __tablename__ = "inscripcion_paquete"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)
    gestion_id = Column(Integer, ForeignKey("gestion.id"), nullable=True)
    estado_academico = Column(String(20), default='INSCRITO')  # INSCRITO, APROBADO, REPROBADO
    fecha_inscripcion = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)
    profesor_id = Column(Integer, ForeignKey("profesores.id"), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    estudiante = relationship("Estudiante")
    paquete = relationship("Paquete", back_populates="inscripciones")
    venta = relationship("Venta")
    gestion = relationship("Gestion")
    profesor = relationship("Profesor")
