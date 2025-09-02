-- SQL Script para crear columna shelf_position en Railway PostgreSQL
-- Ejecutar en Railway PostgreSQL Console o pgAdmin

-- 1. Verificar si la columna ya existe
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'paints' AND column_name = 'shelf_position';

-- 2. Crear la columna si no existe (este comando fallará si ya existe)
ALTER TABLE paints ADD COLUMN shelf_position INTEGER;

-- 3. Verificar que se creó correctamente
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'paints' AND column_name = 'shelf_position';

-- 4. Migrar datos de posición para primeras 50 pinturas (EJEMPLO)
-- Código 70.951 → Posición 1
UPDATE paints SET shelf_position = 1 WHERE brand = 'VALLEJO' AND color_code = '70.951';
UPDATE paints SET shelf_position = 2 WHERE brand = 'VALLEJO' AND color_code = '70.919';
UPDATE paints SET shelf_position = 3 WHERE brand = 'VALLEJO' AND color_code = '70.820';
UPDATE paints SET shelf_position = 4 WHERE brand = 'VALLEJO' AND color_code = '70.918';
UPDATE paints SET shelf_position = 5 WHERE brand = 'VALLEJO' AND color_code = '70.928';
UPDATE paints SET shelf_position = 6 WHERE brand = 'VALLEJO' AND color_code = '70.815';
UPDATE paints SET shelf_position = 7 WHERE brand = 'VALLEJO' AND color_code = '70.835';
UPDATE paints SET shelf_position = 8 WHERE brand = 'VALLEJO' AND color_code = '70.805';
UPDATE paints SET shelf_position = 9 WHERE brand = 'VALLEJO' AND color_code = '70.944';
UPDATE paints SET shelf_position = 10 WHERE brand = 'VALLEJO' AND color_code = '70.803';

-- 5. Verificar que las actualizaciones funcionaron
SELECT name, brand, color_code, shelf_position 
FROM paints 
WHERE brand = 'VALLEJO' AND shelf_position IS NOT NULL 
ORDER BY shelf_position 
LIMIT 10;

-- 6. Contar cuántas pinturas tienen shelf_position
SELECT 
    COUNT(*) as total_vallejo,
    COUNT(shelf_position) as with_shelf_position,
    COUNT(*) - COUNT(shelf_position) as without_shelf_position
FROM paints 
WHERE brand = 'VALLEJO';

-- INSTRUCCIONES:
-- 1. Conectar a Railway PostgreSQL Console
-- 2. Ejecutar comandos uno por uno o copiar todo el script
-- 3. Verificar resultados con las queries SELECT
-- 4. Una vez confirmado, ejecutar la migración completa con los 490 registros