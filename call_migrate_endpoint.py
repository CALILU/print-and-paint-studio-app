#!/usr/bin/env python3
"""
Script para llamar al endpoint existente /admin/migrate-shelf-positions
que ahora incluye la creación de columna automática
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def call_migrate_endpoint():
    """Llamar al endpoint de migración que crea columna y migra datos"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("🚀 Llamando endpoint de migración shelf_position...")
        print("   URL: POST /admin/migrate-shelf-positions")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/migrate-shelf-positions",
            headers=headers,
            timeout=60  # Más tiempo para la migración
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Migración exitosa!")
            print(f"   - Pinturas actualizadas: {result.get('updated_count', 'N/A')}")
            print(f"   - Errores: {len(result.get('errors', []))}")
            print(f"   - No encontrados: {len(result.get('not_found', []))}")
            return True, result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error llamando endpoint: {e}")
        return False, str(e)

def verify_migration_success():
    """Verificar que la migración funcionó"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("\n🔍 Verificando resultado de migración...")
        
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            paints = response.json()
            vallejo_paints = [p for p in paints if p.get('brand', '').upper() == 'VALLEJO']
            with_shelf_position = [p for p in vallejo_paints if p.get('shelf_position') is not None]
            
            print(f"📊 Pinturas VALLEJO: {len(vallejo_paints)}")
            print(f"📊 Con shelf_position: {len(with_shelf_position)}")
            
            if with_shelf_position:
                print(f"\n✅ ÉXITO! Ejemplos de pinturas con posición:")
                for i, paint in enumerate(sorted(with_shelf_position, key=lambda x: x.get('shelf_position', 0))[:5]):
                    print(f"   {i+1}. {paint['name']} ({paint['color_code']}) → Posición: {paint['shelf_position']}")
                return True
            else:
                print(f"\n❌ No se encontraron pinturas con shelf_position")
                return False
        else:
            print(f"❌ Error verificando: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 MIGRACIÓN SHELF_POSITION VIA ENDPOINT")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Endpoint: POST /admin/migrate-shelf-positions")
    print("   Acción: Crear columna + Migrar primeros 50 registros")
    print()
    
    # 1. Llamar al endpoint de migración
    print("1️⃣ Ejecutando migración...")
    success, result = call_migrate_endpoint()
    
    if not success:
        print(f"❌ Migración falló: {result}")
        return
    
    # 2. Verificar resultado
    print("\n2️⃣ Verificando resultado...")
    verification_success = verify_migration_success()
    
    if verification_success:
        print(f"\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print(f"   - La columna shelf_position existe y tiene datos")
        print(f"   - Ahora puedes ejecutar la migración completa con todos los 490 registros")
    else:
        print(f"\n❌ La verificación falló")

if __name__ == "__main__":
    main()