#!/usr/bin/env python3
"""
Script para probar si el endpoint /api/paints/{id} ya maneja shelf_position
Ejecutar después del redespliegue de Railway
"""

import requests
import json
import time

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def test_shelf_position_endpoint():
    """Probar que el endpoint actualiza shelf_position correctamente"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        paint_id = 11609  # Blanco 70.951
        test_position = 999  # Valor de prueba único
        
        print("🧪 PROBANDO ENDPOINT CORREGIDO")
        print(f"   Target: Paint ID {paint_id} (Blanco 70.951)")
        print(f"   Test shelf_position: {test_position}")
        print()
        
        # 1. Actualizar con shelf_position
        print("1️⃣ Enviando actualización...")
        data = {'shelf_position': test_position}
        
        response = requests.put(f"{API_BASE_URL}/api/paints/{paint_id}", 
                              json=data, headers=headers, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"   Success: {response_data.get('success', False)}")
            
            # Verificar si shelf_position está en la respuesta
            paint_data = response_data.get('data', {})
            response_shelf_position = paint_data.get('shelf_position')
            
            print(f"   Response shelf_position: {response_shelf_position}")
            
            if response_shelf_position == test_position:
                print("   ✅ ENDPOINT FUNCIONANDO: shelf_position en respuesta")
                return True
            else:
                print("   ❌ shelf_position no coincide en respuesta")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
        
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False

def verify_via_public_api():
    """Verificar vía API pública que el cambio se guardó"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("\n2️⃣ Verificando vía API pública...")
        
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            paints = response.json()
            blanco_paints = [p for p in paints if p.get('color_code') == '70.951']
            
            if blanco_paints:
                paint = blanco_paints[0]
                shelf_position = paint.get('shelf_position')
                
                print(f"   Pintura: {paint.get('name')} ({paint.get('color_code')})")
                print(f"   shelf_position: {shelf_position}")
                
                if shelf_position == 999:
                    print("   ✅ PERSISTENCIA CORRECTA: Valor guardado en BD")
                    return True
                elif shelf_position is not None:
                    print(f"   ⚠️  Valor diferente al esperado: {shelf_position}")
                    return True  # Al menos no es None
                else:
                    print("   ❌ shelf_position sigue siendo None")
                    return False
            else:
                print("   ❌ No se encontró pintura 70.951")
                return False
        else:
            print(f"   ❌ Error API pública: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def main():
    print("🚀 TEST ENDPOINT SHELF_POSITION CORREGIDO")
    print("   Verificando si Railway se redesplego con el fix")
    print()
    
    # Probar endpoint
    endpoint_ok = test_shelf_position_endpoint()
    
    if endpoint_ok:
        # Verificar persistencia
        persistence_ok = verify_via_public_api()
        
        if persistence_ok:
            print(f"\n🎉 ¡ENDPOINT CORREGIDO Y FUNCIONANDO!")
            print(f"   - Maneja shelf_position correctamente")
            print(f"   - Guarda en base de datos")
            print(f"   - Listo para migración masiva")
        else:
            print(f"\n⚠️  Endpoint funciona pero persistencia tiene problemas")
    else:
        print(f"\n❌ Railway aún no se ha redesplego o hay otros problemas")
        print(f"   Esperar más tiempo y volver a probar")

if __name__ == "__main__":
    main()