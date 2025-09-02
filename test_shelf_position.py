#!/usr/bin/env python3
"""
Script para verificar que shelf_position está funcionando correctamente
"""

import requests
import json

API_BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"
API_KEY = "print_and_paint_secret_key_2025"

def test_specific_paint():
    """Buscar una pintura específica que sabemos que se actualizó"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        print("🔍 Buscando pinturas VALLEJO para verificar shelf_position...")
        response = requests.get(f"{API_BASE_URL}/api/paints", headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_paints = response.json()
            vallejo_paints = [paint for paint in all_paints if paint.get('brand') == 'VALLEJO']
            
            print(f"✅ Encontradas {len(vallejo_paints)} pinturas VALLEJO")
            
            # Buscar específicamente el Blanco 70.951
            blanco_paints = [paint for paint in vallejo_paints if paint.get('color_code') == '70.951']
            
            if blanco_paints:
                paint = blanco_paints[0]
                print(f"\n📊 Pintura Blanco 70.951:")
                print(f"  - ID: {paint.get('id')}")
                print(f"  - Nombre: {paint.get('name')}")
                print(f"  - Código: {paint.get('color_code')}")
                print(f"  - Marca: {paint.get('brand')}")
                print(f"  - Shelf Position: {paint.get('shelf_position')}")
                
                # Verificar si tiene shelf_position
                if paint.get('shelf_position') is not None:
                    print(f"  ✅ shelf_position = {paint.get('shelf_position')}")
                else:
                    print("  ❌ shelf_position es NULL")
                    
                # Mostrar todas las claves disponibles
                print(f"\n  Claves disponibles: {list(paint.keys())}")
                
            else:
                print("❌ No se encontró pintura Blanco 70.951")
            
            # Buscar cualquier pintura con shelf_position
            with_shelf_position = [paint for paint in vallejo_paints if paint.get('shelf_position') is not None]
            
            print(f"\n📊 Pinturas VALLEJO con shelf_position: {len(with_shelf_position)}")
            
            if with_shelf_position:
                print("\n  Primeros 5 ejemplos:")
                for i, paint in enumerate(with_shelf_position[:5]):
                    print(f"    {i+1}. {paint.get('name')} ({paint.get('color_code')}) - Posición: {paint.get('shelf_position')}")
            else:
                print("  ❌ No se encontraron pinturas con shelf_position")
                
        else:
            print(f"❌ Error obteniendo pinturas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_paint()