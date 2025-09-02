# 🚀 Guía Manual: Crear Columna shelf_position en Railway PostgreSQL

## ❌ Problema Identificado
- La columna `shelf_position` NO existe en la base de datos Railway PostgreSQL
- Los endpoints API existen en el código pero Railway no se ha redeplegado
- Las migraciones fallan porque intentan actualizar una columna inexistente

## ✅ Solución Manual: Ejecutar SQL Directamente en Railway

### 📋 Opción 1: Railway Web Dashboard (RECOMENDADO)

1. **Abrir Railway Dashboard**
   - Ir a: https://railway.app/dashboard
   - Buscar proyecto: `print-and-paint-studio-app-production`

2. **Acceder a PostgreSQL**
   - Clic en el servicio PostgreSQL 
   - Clic en "Data" tab
   - Abrir "Query" console

3. **Ejecutar SQL de Creación**
   ```sql
   -- 1. Verificar columna (debe devolver 0 filas)
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'paints' AND column_name = 'shelf_position';
   
   -- 2. Crear columna
   ALTER TABLE paints ADD COLUMN shelf_position INTEGER;
   
   -- 3. Verificar creación (debe devolver 1 fila)
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'paints' AND column_name = 'shelf_position';
   ```

4. **Migrar Datos de Prueba**
   ```sql
   -- Ejemplo: Primeras 10 posiciones
   UPDATE paints SET shelf_position = 1 WHERE brand = 'VALLEJO' AND color_code = '70.951';
   UPDATE paints SET shelf_position = 2 WHERE brand = 'VALLEJO' AND color_code = '70.919';
   UPDATE paints SET shelf_position = 3 WHERE brand = 'VALLEJO' AND color_code = '70.820';
   UPDATE paints SET shelf_position = 4 WHERE brand = 'VALLEJO' AND color_code = '70.918';
   UPDATE paints SET shelf_position = 5 WHERE brand = 'VALLEJO' AND color_code = '70.928';
   ```

5. **Verificar Resultado**
   ```sql
   SELECT name, color_code, shelf_position 
   FROM paints 
   WHERE brand = 'VALLEJO' AND shelf_position IS NOT NULL 
   ORDER BY shelf_position;
   ```

### 📋 Opción 2: Railway CLI (Alternativa)

1. **Instalar Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login y Conectar**
   ```bash
   railway login
   railway connect [project-id]
   ```

3. **Acceder a PostgreSQL**
   ```bash
   railway run psql
   ```

4. **Ejecutar Mismo SQL del paso anterior**

## 🔄 Después de Crear la Columna

### ✅ Verificar que Funciona
Ejecutar este script para confirmar que la API ahora devuelve `shelf_position`:

```bash
cd "/mnt/c/Repositorio GitHub VSC/print-and-paint-studio-app"
python3 test_shelf_position.py
```

**Resultado Esperado:**
```
✅ Encontradas 1161 pinturas VALLEJO
📊 Pintura Blanco 70.951:
  - Shelf Position: 1  # ← DEBE mostrar valor, no None
  ✅ shelf_position = 1
  
📊 Pinturas VALLEJO con shelf_position: 5  # ← DEBE ser > 0
```

### 🎯 Ejecutar Migración Completa
Una vez confirmado que funciona, ejecutar migración de los 490 registros:

```bash
python3 migrate_direct_railway.py
```

## 📊 Estados Esperados

### ❌ Estado Actual (Columna NO existe)
```json
{
  "brand": "VALLEJO",
  "color_code": "70.951", 
  "name": "Blanco",
  "shelf_position": null  // ← Campo faltante
}
```

### ✅ Estado Deseado (Columna existe)
```json
{
  "brand": "VALLEJO",
  "color_code": "70.951", 
  "name": "Blanco",
  "shelf_position": 1  // ← Campo con valor
}
```

## 🚨 Importante

- **NO reiniciar** el servicio Railway durante la migración
- **Verificar SIEMPRE** antes de migración masiva
- **Hacer backup** si es crítico (Railway hace backups automáticos)
- La migración completa actualizará **490 pinturas VALLEJO**

## 📝 Archivos de Referencia

- `create_shelf_position_column.sql` - Script SQL completo
- `test_shelf_position.py` - Verificación API 
- `migrate_direct_railway.py` - Migración completa
- `vallejo_model_color.csv` - Datos fuente (490 registros)

---
**Fecha**: 2025-09-02  
**Proyecto**: PaintScanner - Railway Backend  
**Acción**: Crear columna shelf_position manualmente