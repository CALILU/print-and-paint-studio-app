-- Migración para agregar la columna sync_status a la tabla paints
-- Para ejecutar en Railway CLI o pgAdmin

-- 1. Verificar si la columna ya existe (ejecutar primero)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'paints' AND column_name = 'sync_status';

-- 2. Si no existe, ejecutar estos comandos:

-- Agregar la columna sync_status con valor por defecto 'synced'
ALTER TABLE paints 
ADD COLUMN IF NOT EXISTS sync_status VARCHAR(20) DEFAULT 'synced';

-- Actualizar todos los registros existentes para asegurar que tengan el valor por defecto
UPDATE paints 
SET sync_status = 'synced' 
WHERE sync_status IS NULL OR sync_status = '';

-- 3. Verificar que la migración fue exitosa
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'paints' AND column_name = 'sync_status';

-- 4. Verificar algunos registros de ejemplo
SELECT id, name, brand, sync_status 
FROM paints 
LIMIT 5;