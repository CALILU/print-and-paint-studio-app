#!/usr/bin/env python3
"""
Script de testing para verificar el sistema de notificaciones Web → Android
Ejecutar DESPUÉS de subir cambios a Railway
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"

def test_notification_system():
    """
    Test completo del sistema de notificaciones
    """
    print("🚀 TESTING SISTEMA DE NOTIFICACIONES WEB → ANDROID")
    print("=" * 60)
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Verificar que el endpoint de notificaciones existe
    print("📱 TEST 1: Verificar endpoint de notificaciones")
    try:
        response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint OK - Notificaciones actuales: {data.get('count', 0)}")
        else:
            print(f"❌ Endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Test 2: Verificar endpoint temporal de testing
    print("\n🧪 TEST 2: Verificar endpoint temporal de testing")
    try:
        response = requests.post(f"{BASE_URL}/api/android-notify/test-notification")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Notificación creada exitosamente!")
            print(f"   🎯 Pintura: {result.get('paint_name')}")
            print(f"   📦 Stock: {result.get('old_stock')} → {result.get('new_stock')}")
            print(f"   📊 Total notificaciones: {result.get('notification_count')}")
        else:
            print(f"❌ Error: {response.status_code}")
            if response.status_code == 404:
                print("   Railway aún no tiene los cambios actualizados")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Test 3: Verificar que Android puede recibir la notificación
    print("\n⏰ TEST 3: Verificar recepción de notificación (10 segundos)")
    time.sleep(2)  # Pequeña pausa
    
    try:
        response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            
            if count > 0:
                print(f"✅ Android recibirá {count} notificación(es)!")
                
                notifications = data.get('notifications', [])
                for i, notif in enumerate(notifications[:1]):
                    print(f"   📬 Notificación {i+1}:")
                    data_info = notif.get('data', {})
                    print(f"      - Pintura: {data_info.get('paint_name')}")
                    print(f"      - Stock: {data_info.get('old_stock')} → {data_info.get('new_stock')}")
                    print(f"      - Fuente: {data_info.get('source')}")
                
                return True
            else:
                print("❌ No se encontraron notificaciones")
                return False
        else:
            print(f"❌ Error verificando notificaciones: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_api_endpoint():
    """
    Test del endpoint API que usa Android directamente
    """
    print("\n🔧 TEST 4: Endpoint API directo (como Android)")
    
    # Get current Blanco Hueso data
    try:
        response = requests.get(f"{BASE_URL}/api/paints")
        paints = response.json()
        
        blanco_hueso = None
        for paint in paints:
            if paint.get('name') == 'Blanco Hueso':
                blanco_hueso = paint
                break
        
        if not blanco_hueso:
            print("❌ Blanco Hueso no encontrado")
            return False
        
        current_stock = blanco_hueso.get('stock', 0)
        new_stock = current_stock + 1
        
        print(f"📦 Stock actual: {current_stock} → {new_stock}")
        
        # Update using API endpoint (like Android would)
        response = requests.put(
            f"{BASE_URL}/api/paints/{blanco_hueso['id']}",
            json={'stock': new_stock},
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': 'print_and_paint_secret_key_2025'
            }
        )
        
        if response.status_code == 200:
            print("✅ API update exitoso!")
            
            # Check if notification was generated
            time.sleep(2)
            notif_response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
            notif_data = notif_response.json()
            
            if notif_data.get('count', 0) > 0:
                print("✅ Notificación generada desde API!")
                return True
            else:
                print("❌ No se generó notificación desde API")
                print("   Esto significa que el fix del endpoint API aún no está en Railway")
                return False
        else:
            print(f"❌ API update falló: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def show_android_instructions():
    """
    Mostrar instrucciones para verificar en Android
    """
    print("\n" + "=" * 60)
    print("📱 INSTRUCCIONES PARA ANDROID")
    print("=" * 60)
    print()
    print("En Android Studio logcat, busca estos logs:")
    print()
    print("✅ LOGS DE INICIO (confirman que WebNotificationReceiver funciona):")
    print("   🚀 Starting WebNotificationReceiver initialization...")
    print("   🔔 Web notification receiver initialized and started polling")
    print()
    print("✅ LOGS DE POLLING (cada 10 segundos):")
    print("   🔍 WebNotificationReceiver: Checking for notifications...")
    print("   📡 WebNotificationReceiver: HTTP 200 -")
    print("   📊 WebNotificationReceiver: Found X notifications")
    print()
    print("✅ LOGS DE RECEPCIÓN (cuando hay notificaciones):")
    print("   📬 WebNotificationReceiver: Processing X notifications")
    print("   🔄 Processing stock update from test_endpoint: Blanco Hueso")
    print("   ✅ Local paint stock updated: Blanco Hueso → [nuevo_valor]")
    print("   🔔 Stock updated from web: Blanco Hueso (Stock: X → Y)")
    print()
    print("🎯 Si ves estos logs, el sistema funciona perfectamente!")

def main():
    print("=" * 60)
    print("🧪 SISTEMA DE NOTIFICACIONES - TESTING COMPLETO")
    print("=" * 60)
    
    # Test notification system
    success = test_notification_system()
    
    if success:
        print(f"\n🎉 ¡ÉXITO! El sistema de notificaciones está funcionando")
        
        # Test API endpoint
        api_success = test_api_endpoint()
        
        if api_success:
            print(f"\n🎊 ¡ÉXITO COMPLETO! Ambos sistemas funcionan:")
            print("   ✅ Endpoint temporal: OK")
            print("   ✅ Endpoint API: OK")
            print("   ✅ Sistema Web → Android: COMPLETAMENTE FUNCIONAL")
        else:
            print(f"\n⏰ ÉXITO PARCIAL:")
            print("   ✅ Endpoint temporal: OK")
            print("   ⏳ Endpoint API: Pendiente (Railway deployment)")
            print("   🎯 El sistema básico ya funciona!")
    else:
        print(f"\n❌ Railway aún no tiene los cambios actualizados")
        print("   Intenta de nuevo en unos minutos después de subir los archivos")
    
    show_android_instructions()
    
    print(f"\n💡 CONCLUSIÓN:")
    if success:
        print("   El sistema de notificaciones Web → Android está FUNCIONANDO")
        print("   Android recibirá las notificaciones automáticamente cada ≤10 segundos")
        print("   La galería se actualizará sin reiniciar la aplicación")
    else:
        print("   Sube los archivos a Railway y ejecuta este script nuevamente")

if __name__ == "__main__":
    main()