import os

# Definir estructura de carpetas backend
folders = [
    'app',
    'app/api',
    'app/api/v1',
    'app/api/v1/endpoints',
    'app/core',
    'app/db',
    'app/models',
    'app/schemas',
    'app/services',
    'tests',
    'tests/api',
    'tests/api/v1',
    'alembic',
    'alembic/versions'
]

# Archivos __init__.py a crear
init_files = [
    'app/__init__.py',
    'app/api/__init__.py',
    'app/api/v1/__init__.py',
    'app/api/v1/endpoints/__init__.py',
    'app/core/__init__.py',
    'app/db/__init__.py',
    'app/models/__init__.py',
    'app/schemas/__init__.py',
    'app/services/__init__.py',
    'tests/__init__.py',
    'tests/api/__init__.py',
    'tests/api/v1/__init__.py'
]

# Archivos de configuración
config_files = [
    'requirements.txt',
    'README.md',
    '.env',
    '.gitignore',
    'alembic.ini'
]

# Crear carpetas
print("📁 Creando estructura de carpetas...")
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"  ✅ {folder}")

# Crear archivos __init__.py
print("\n📄 Creando archivos __init__.py...")
for file in init_files:
    open(file, 'a').close()
    print(f"  ✅ {file}")

# Crear archivos de configuración
print("\n⚙️ Creando archivos de configuración...")
for file in config_files:
    open(file, 'a').close()
    print(f"  ✅ {file}")

print("\n🎉 ¡Estructura del proyecto creada exitosamente!")