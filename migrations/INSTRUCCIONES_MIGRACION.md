# Instrucciones para Ejecutar la Migración

## Opción 1: Usando pgAdmin

1. Abrir pgAdmin
2. Conectarse a la base de datos `instituto_db`
3. Abrir Query Tool (Herramientas → Query Tool)
4. Copiar y pegar el siguiente SQL:

```sql
-- Add descuento column to detalle_venta table
ALTER TABLE detalle_venta 
ADD COLUMN descuento NUMERIC(10, 2) DEFAULT 0.00 NOT NULL;

-- Add comment to the column
COMMENT ON COLUMN detalle_venta.descuento IS 'Discount amount applied to this sale detail item';

-- Update existing records to have 0.00 discount
UPDATE detalle_venta SET descuento = 0.00 WHERE descuento IS NULL;
```

5. Ejecutar (F5 o botón Execute)

## Opción 2: Usando psql desde la línea de comandos

Si PostgreSQL está instalado, encontrar la ruta de psql (generalmente en `C:\Program Files\PostgreSQL\{version}\bin\psql.exe`) y ejecutar:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d instituto_db -f "e:\INSTITUTE\institute_lms\center_admin\migrations\add_descuento_to_detalle_venta.sql"
```

## Opción 3: Ejecutar SQL directamente

Conectarse a PostgreSQL y ejecutar:

```sql
ALTER TABLE detalle_venta ADD COLUMN descuento NUMERIC(10, 2) DEFAULT 0.00 NOT NULL;
```

## Verificar que la migración se ejecutó correctamente

```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'detalle_venta' AND column_name = 'descuento';
```

Debería mostrar:
- column_name: descuento
- data_type: numeric
- column_default: 0.00

## Después de ejecutar la migración

1. Reiniciar el servidor backend FastAPI
2. Probar la funcionalidad de descuentos en la interfaz de ventas
