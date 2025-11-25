from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, UniqueConstraint
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
