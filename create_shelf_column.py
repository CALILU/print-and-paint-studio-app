#!/usr/bin/env python3
"""
Script para crear la columna shelf_position en la tabla paints de Railway
Usa el nuevo endpoint /admin/create-shelf-position-column
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def create_shelf_position_column():
    """Crear la columna shelf_position usando el endpoint admin"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("🔧 Creando columna shelf_position en Railway PostgreSQL...")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/create-shelf-position-column",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ {result['message']}")
            return True, result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error creando columna: {e}")
        return False, str(e)

def verify_column_creation():
    """Verificar que la columna se creó correctamente"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("\n🔍 Verificando que la columna se creó correctamente...")
        
        # Obtener una pintura y verificar que incluye shelf_position
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            paints = response.json()
            if paints:
                first_paint = paints[0]
                has_shelf_position = 'shelf_position' in first_paint
                
                print(f"📊 Primera pintura: {first_paint.get('name', 'Unknown')}")
                print(f"📊 Claves disponibles: {list(first_paint.keys())}")
                print(f"📊 Tiene shelf_position: {'✅ SÍ' if has_shelf_position else '❌ NO'}")
                
                if has_shelf_position:
                    print(f"📊 Valor shelf_position: {first_paint['shelf_position']}")
                
                return has_shelf_position
            else:
                print("❌ No hay pinturas en la base de datos")
                return False
        else:
            print(f"❌ Error verificando: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando columna: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CREAR COLUMNA SHELF_POSITION EN RAILWAY")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Endpoint: POST /admin/create-shelf-position-column")
    print()
    
    # 1. Crear la columna
    print("1️⃣ Creando columna shelf_position...")
    success, result = create_shelf_position_column()
    
    if not success:
        print(f"❌ No se pudo crear la columna: {result}")
        return
    
    # 2. Verificar creación
    print("\n2️⃣ Verificando creación de columna...")
    column_exists = verify_column_creation()
    
    if column_exists:
        print(f"\n🎉 ¡COLUMNA CREADA EXITOSAMENTE!")
        print(f"   - La columna shelf_position está disponible en la API")
        print(f"   - Ahora puedes ejecutar la migración de datos")
    else:
        print(f"\n❌ La columna no está disponible en la API")
        print(f"   - Es posible que necesites reiniciar la aplicación Railway")

if __name__ == "__main__":
    main()