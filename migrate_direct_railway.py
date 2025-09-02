#!/usr/bin/env python3
"""
Script para migrar directamente usando los endpoints existentes de Railway
Actualiza las pinturas una por una usando PUT /api/paints/{id}
"""

import requests
import json
import time
import csv
from datetime import datetime

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def load_positions_from_csv(csv_path):
    """Cargar las posiciones desde el archivo CSV"""
    positions_data = {}
    
    try:
        print(f"📖 Cargando datos desde: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row['codigo'].strip()
                posicion = int(row['posicion'])
                positions_data[codigo] = posicion
                
        print(f"✅ Cargados {len(positions_data)} registros del CSV")
        return positions_data
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {csv_path}")
        return {}
    except Exception as e:
        print(f"❌ Error al leer CSV: {e}")
        return {}

def get_vallejo_paints():
    """Obtener todas las pinturas VALLEJO"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("📊 Obteniendo pinturas VALLEJO...")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_paints = response.json()
            vallejo_paints = [paint for paint in all_paints if paint.get('brand', '').upper() == 'VALLEJO']
            print(f"✅ Encontradas {len(vallejo_paints)} pinturas VALLEJO")
            return vallejo_paints
        else:
            print(f"❌ Error obteniendo pinturas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo pinturas: {e}")
        return []

def update_paint_with_shelf_position(paint_id, shelf_position, paint_name, color_code):
    """Actualizar una pintura específica con su posición de estantería"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        # Solo enviar el campo shelf_position para actualizar
        data = {
            'shelf_position': shelf_position
        }
        
        response = requests.put(f"{API_BASE_URL}/api/paints/{paint_id}", 
                              json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True, "OK"
        else:
            return False, f"Error {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"

def migrate_shelf_positions(paints, positions_data):
    """Migrar las posiciones usando el endpoint PUT existente"""
    updated_count = 0
    errors = []
    not_found = []
    
    print(f"\n🔄 Iniciando migración directa de {len(positions_data)} posiciones...")
    
    # Crear diccionario de pinturas por código para búsqueda rápida
    paints_by_code = {}
    for paint in paints:
        color_code = paint.get('color_code')
        if color_code:
            if color_code not in paints_by_code:
                paints_by_code[color_code] = []
            paints_by_code[color_code].append(paint)
    
    processed = 0
    for codigo, posicion in positions_data.items():
        processed += 1
        
        if codigo in paints_by_code:
            for paint in paints_by_code[codigo]:
                paint_id = paint['id']
                paint_name = paint['name']
                
                success, message = update_paint_with_shelf_position(
                    paint_id, posicion, paint_name, codigo
                )
                
                if success:
                    updated_count += 1
                    print(f"  ✓ [{processed}/{len(positions_data)}] {paint_name} ({codigo}) - Posición: {posicion}")
                else:
                    errors.append(f"{codigo}: {message}")
                    print(f"  ❌ Error: {paint_name} ({codigo}) - {message}")
                
                # Pequeña pausa para no sobrecargar Railway
                time.sleep(0.2)
        else:
            not_found.append(codigo)
            print(f"  ⚠️  [{processed}/{len(positions_data)}] No encontrado: {codigo}")
    
    return updated_count, errors, not_found

def verify_migration():
    """Verificar que la migración funcionó"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("\n🔍 Verificando migración...")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_paints = response.json()
            vallejo_paints = [paint for paint in all_paints if paint.get('brand', '').upper() == 'VALLEJO']
            
            with_position = [paint for paint in vallejo_paints if paint.get('shelf_position') is not None]
            
            print(f"\n📊 Verificación final:")
            print(f"  - Total pinturas VALLEJO: {len(vallejo_paints)}")
            print(f"  - Pinturas con shelf_position: {len(with_position)}")
            
            if with_position:
                print(f"\n  Primeros 5 ejemplos:")
                examples = sorted(with_position, key=lambda x: x.get('shelf_position', 0))[:5]
                for paint in examples:
                    print(f"    • {paint['name']} ({paint['color_code']}) - Posición: {paint['shelf_position']}")
                    
                return len(with_position)
            else:
                print("  ❌ No se encontraron pinturas con shelf_position")
                return 0
                
        else:
            print(f"❌ Error verificando: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return 0

def main():
    """Función principal"""
    print("🚀 Migración DIRECTA de posiciones de estantería en Railway")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Método: Actualización directa vía PUT /api/paints/{id}")
    print()
    
    # Ruta del archivo CSV
    csv_path = '/mnt/c/paintscanner/vallejo_model_color.csv'
    
    # 1. Cargar datos del CSV
    print("1️⃣ Cargando datos del CSV...")
    positions_data = load_positions_from_csv(csv_path)
    
    if not positions_data:
        print("❌ No se pudieron cargar datos del CSV")
        return
    
    # 2. Obtener pinturas VALLEJO
    print("\n2️⃣ Obteniendo pinturas VALLEJO...")
    paints = get_vallejo_paints()
    
    if not paints:
        print("❌ No se encontraron pinturas VALLEJO")
        return
    
    # 3. Migrar posiciones
    print(f"\n3️⃣ Migrando {len(positions_data)} posiciones...")
    updated_count, errors, not_found = migrate_shelf_positions(paints, positions_data)
    
    # 4. Verificar migración
    print("\n4️⃣ Verificando migración...")
    verified_count = verify_migration()
    
    # Resumen final
    print(f"\n🎉 RESUMEN DE MIGRACIÓN:")
    print(f"   - Pinturas procesadas: {len(positions_data)}")
    print(f"   - Actualizaciones exitosas: {updated_count}")
    print(f"   - Errores: {len(errors)}")
    print(f"   - No encontrados: {len(not_found)}")
    print(f"   - Verificados con shelf_position: {verified_count}")
    
    if verified_count > 0:
        print(f"\n✅ ¡Migración EXITOSA! {verified_count} pinturas tienen shelf_position")
    else:
        print(f"\n❌ Migración falló - No se encontraron pinturas con shelf_position")
    
    if errors:
        print(f"\n⚠️  Primeros 5 errores:")
        for error in errors[:5]:
            print(f"     • {error}")

if __name__ == "__main__":
    main()