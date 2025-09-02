#!/usr/bin/env python3
"""
Script de debug para actualizar UNA sola pintura y verificar el problema
"""

import requests
import json

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def debug_single_paint_update():
    """Debug de actualización de una sola pintura: Blanco 70.951"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        paint_id = 11609  # ID del Blanco 70.951
        shelf_position = 1
        
        print(f"🔧 DEBUG: Actualizando pintura ID {paint_id} con shelf_position = {shelf_position}")
        
        # 1. Obtener estado actual vía API pública
        print("\n1️⃣ Estado ANTES de la actualización (vía API pública):")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers)
        if response.status_code == 200:
            paints = response.json()
            paint_before = None
            for p in paints:
                if p.get('id') == paint_id:
                    paint_before = p
                    break
            
            if paint_before:
                print(f"   Nombre: {paint_before.get('name')}")
                print(f"   Código: {paint_before.get('color_code')}")
                print(f"   shelf_position: {paint_before.get('shelf_position')}")
            else:
                print(f"   ❌ No se encontró pintura ID {paint_id}")
        else:
            print(f"   ❌ Error obteniendo pinturas: {response.status_code}")
        
        # 2. Actualizar usando endpoint Android
        print(f"\n2️⃣ Ejecutando actualización vía /api/paints/{paint_id}:")
        data = {'shelf_position': shelf_position}
        print(f"   Enviando: {data}")
        
        response = requests.put(f"{API_BASE_URL}/api/paints/{paint_id}", 
                              json=data, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
        # 3. Verificar resultado vía API pública
        print(f"\n3️⃣ Estado DESPUÉS de la actualización:")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers)
        if response.status_code == 200:
            paints = response.json()
            paint_after = None
            for p in paints:
                if p.get('id') == paint_id:
                    paint_after = p
                    break
            
            if paint_after:
                print(f"   Nombre: {paint_after.get('name')}")
                print(f"   Código: {paint_after.get('color_code')}")
                print(f"   shelf_position: {paint_after.get('shelf_position')}")
                
                if paint_after.get('shelf_position') == shelf_position:
                    print(f"   ✅ ÉXITO: shelf_position actualizado correctamente")
                    return True
                else:
                    print(f"   ❌ FALLO: shelf_position no se actualizó")
                    return False
            else:
                print(f"   ❌ No se encontró pintura ID {paint_id} después")
                return False
        else:
            print(f"   ❌ Error obteniendo pinturas después: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        return False

def test_via_public_api():
    """Verificar mediante API pública /api/paints"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print(f"\n4️⃣ Verificación vía API pública:")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers)
        
        if response.status_code == 200:
            paints = response.json()
            blanco_paints = [p for p in paints if p.get('color_code') == '70.951']
            
            if blanco_paints:
                paint = blanco_paints[0]
                print(f"   Nombre: {paint.get('name')}")
                print(f"   Código: {paint.get('color_code')}")
                print(f"   shelf_position: {paint.get('shelf_position')}")
                
                if paint.get('shelf_position') is not None:
                    print(f"   ✅ shelf_position visible en API pública")
                else:
                    print(f"   ❌ shelf_position NULL en API pública")
            else:
                print(f"   ❌ No se encontró pintura 70.951")
        else:
            print(f"   ❌ Error API pública: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando API pública: {e}")

def main():
    print("🚀 DEBUG ACTUALIZACIÓN INDIVIDUAL")
    print("   Target: Blanco 70.951 (ID: 11609)")
    print("   Objetivo: shelf_position = 1")
    print()
    
    success = debug_single_paint_update()
    test_via_public_api()
    
    if success:
        print(f"\n🎉 Debug completado - Actualización funcionó")
    else:
        print(f"\n❌ Debug completado - Hay problemas en la actualización")

if __name__ == "__main__":
    main()