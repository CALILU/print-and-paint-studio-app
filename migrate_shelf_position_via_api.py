#!/usr/bin/env python3
"""
Script de migración para añadir posición de estantería usando la API de Railway
Carga los datos desde vallejo_model_color.csv y actualiza vía API REST
"""

import os
import sys
import csv
import requests
import json
import time
from datetime import datetime

# Configuración de la API de Railway
API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def test_api_connection():
    """Probar conexión a Railway API"""
    try:
        print("🔗 Probando conexión a Railway API...")
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Railway disponible")
            return True
        else:
            print(f"❌ API responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a API: {e}")
        return False

def get_paints_by_brand(brand="VALLEJO"):
    """Obtener todas las pinturas de una marca específica"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print(f"📊 Obteniendo pinturas de marca: {brand}...")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_paints = response.json()
            brand_paints = [paint for paint in all_paints if paint.get('brand', '').upper() == brand.upper()]
            print(f"✅ Encontradas {len(brand_paints)} pinturas de {brand}")
            return brand_paints
        else:
            print(f"❌ Error obteniendo pinturas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo pinturas: {e}")
        return []

def update_paint_shelf_position(paint_id, shelf_position):
    """Actualizar la posición de estantería de una pintura específica"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        data = {
            'shelf_position': shelf_position
        }
        
        response = requests.put(f"{API_BASE_URL}/api/paints/{paint_id}", 
                              json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True, "OK"
        else:
            return False, f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"

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

def update_shelf_positions(paints, positions_data):
    """Actualizar las posiciones en la base de datos vía API"""
    updated_count = 0
    errors = []
    not_found = []
    
    print(f"\n🔄 Iniciando actualización de {len(positions_data)} posiciones...")
    
    # Crear diccionario de pinturas por código para búsqueda rápida
    paints_by_code = {}
    for paint in paints:
        color_code = paint.get('color_code')
        if color_code:
            paints_by_code[color_code] = paint
    
    for codigo, posicion in positions_data.items():
        if codigo in paints_by_code:
            paint = paints_by_code[codigo]
            paint_id = paint['id']
            paint_name = paint['name']
            
            success, message = update_paint_shelf_position(paint_id, posicion)
            
            if success:
                updated_count += 1
                print(f"  ✓ Actualizado: {paint_name} ({codigo}) - Posición: {posicion}")
            else:
                errors.append(f"{codigo}: {message}")
                print(f"  ❌ Error: {paint_name} ({codigo}) - {message}")
        else:
            not_found.append(codigo)
        
        # Pequeña pausa para no sobrecargar la API
        time.sleep(0.1)
    
    print(f"\n📊 Resumen de actualización:")
    print(f"  - Pinturas actualizadas: {updated_count}")
    print(f"  - Errores: {len(errors)}")
    print(f"  - Códigos no encontrados: {len(not_found)}")
    
    if errors and len(errors) <= 10:
        print(f"  - Primeros errores: {errors[:5]}")
    elif errors:
        print(f"  - Primeros 5 errores: {errors[:5]}...")
        
    if not_found and len(not_found) <= 10:
        print(f"  - Códigos no encontrados: {', '.join(not_found[:10])}")
    elif not_found:
        print(f"  - Primeros 10 códigos no encontrados: {', '.join(not_found[:10])}...")
    
    return updated_count, errors, not_found

def verify_update():
    """Verificar que la actualización se realizó correctamente"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("\n🔍 Verificando actualización...")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_paints = response.json()
            vallejo_paints = [paint for paint in all_paints if paint.get('brand', '').upper() == 'VALLEJO']
            
            with_position = [paint for paint in vallejo_paints if paint.get('shelf_position') is not None]
            without_position = [paint for paint in vallejo_paints if paint.get('shelf_position') is None]
            
            print(f"\n📊 Verificación final:")
            print(f"  - Pinturas VALLEJO con posición: {len(with_position)}")
            print(f"  - Pinturas VALLEJO sin posición: {len(without_position)}")
            
            if with_position:
                print(f"\n  Ejemplos de pinturas con posición:")
                # Mostrar los primeros 5 ejemplos ordenados por posición
                examples = sorted(with_position, key=lambda x: x.get('shelf_position', 0))[:5]
                for paint in examples:
                    print(f"    • {paint['name']} ({paint['color_code']}) - Posición: {paint['shelf_position']}")
        else:
            print(f"❌ Error verificando: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al verificar: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando migración de posiciones de estantería vía API...")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ruta del archivo CSV
    csv_path = '/mnt/c/paintscanner/vallejo_model_color.csv'
    
    # Verificar que el archivo CSV existe
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró el archivo CSV en {csv_path}")
        sys.exit(1)
    
    # 1. Probar conexión a la API
    print("1️⃣ Probando conexión a Railway...")
    if not test_api_connection():
        print("❌ No se puede conectar a la API de Railway")
        sys.exit(1)
    
    # 2. Cargar datos del CSV
    print("\n2️⃣ Cargando datos del CSV...")
    positions_data = load_positions_from_csv(csv_path)
    
    if not positions_data:
        print("❌ No se pudieron cargar datos del CSV")
        sys.exit(1)
    
    # 3. Obtener pinturas VALLEJO de la API
    print("\n3️⃣ Obteniendo pinturas VALLEJO de la API...")
    paints = get_paints_by_brand("VALLEJO")
    
    if not paints:
        print("❌ No se encontraron pinturas VALLEJO en la API")
        sys.exit(1)
    
    # 4. Actualizar posiciones vía API
    print(f"\n4️⃣ Actualizando {len(positions_data)} posiciones vía API...")
    updated_count, errors, not_found = update_shelf_positions(paints, positions_data)
    
    # 5. Verificar actualización
    print("\n5️⃣ Verificando actualización...")
    verify_update()
    
    if updated_count > 0:
        print(f"\n✅ Migración completada exitosamente!")
        print(f"   - {updated_count} pinturas actualizadas con posición de estantería")
        if errors:
            print(f"   - {len(errors)} errores durante la actualización")
        if not_found:
            print(f"   - {len(not_found)} códigos no encontrados en la base de datos")
    else:
        print(f"\n⚠️  Migración completada pero no se actualizó ninguna pintura")
        
    print(f"\n🕒 Migración finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()