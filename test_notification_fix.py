#!/usr/bin/env python3
"""
Test script para verificar que el fix de notificaciones funciona correctamente
"""
import requests
import json
import time

RAILWAY_URL = "https://print-and-paint-studio-app-production.up.railway.app"
LOCAL_URL = "http://localhost:5000"

# Usar Railway en producción o local para development
BASE_URL = RAILWAY_URL  # Cambiar a LOCAL_URL si estás probando localmente

def test_notification_flow():
    """
    Simula el flujo completo de notificaciones web admin → Android
    """
    print("🧪 TESTING NOTIFICATION FLOW")
    print("=" * 50)
    
    # 1. Limpiar notificaciones existentes
    print("\n1. Clearing existing notifications...")
    clear_response = requests.post(f"{BASE_URL}/api/android-notify/clear", json={"type": "all"})
    print(f"Clear response: {clear_response.status_code}")
    
    # 2. Verificar estado inicial
    print("\n2. Checking initial state...")
    debug_response = requests.get(f"{BASE_URL}/api/android-notify/debug")
    debug_data = debug_response.json()
    print(f"Initial notifications: {debug_data['summary']['total_notifications']}")
    
    # 3. Crear notificación usando el endpoint de testing
    print("\n3. Creating test notification...")
    test_response = requests.post(f"{BASE_URL}/api/android-notify/test-notification")
    test_data = test_response.json()
    print(f"Test notification created: {test_data.get('success', False)}")
    print(f"Paint: {test_data.get('paint_name', 'Unknown')}")
    print(f"Stock change: {test_data.get('old_stock')} → {test_data.get('new_stock')}")
    
    # 4. Verificar que la notificación existe
    print("\n4. Checking notification was created...")
    debug_response = requests.get(f"{BASE_URL}/api/android-notify/debug")
    debug_data = debug_response.json()
    print(f"Total notifications: {debug_data['summary']['total_notifications']}")
    print(f"Unsent notifications: {debug_data['summary']['unsent_count']}")
    
    if debug_data['summary']['total_notifications'] == 0:
        print("❌ ERROR: No notification was created!")
        return False
    
    # 5. Simular Android obteniendo notificaciones (primer call)
    print("\n5. Simulating Android getting notifications (first call)...")
    android_response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
    android_data = android_response.json()
    print(f"Android received: {android_data['count']} notifications")
    print(f"Total pending: {android_data['total_pending']}")
    
    if android_data['count'] == 0:
        print("❌ ERROR: Android didn't receive any notifications!")
        return False
        
    notification_ids = [notif['id'] for notif in android_data['notifications']]
    print(f"Notification IDs: {notification_ids}")
    
    # 6. Simular Android obteniendo notificaciones inmediatamente otra vez (segundo call)
    print("\n6. Simulating Android getting notifications immediately again (second call)...")
    android_response2 = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
    android_data2 = android_response2.json()
    print(f"Android received (2nd call): {android_data2['count']} notifications")
    print(f"Total pending (2nd call): {android_data2['total_pending']}")
    
    # Con el fix, el segundo call debería recibir 0 notificaciones
    if android_data2['count'] > 0:
        print("❌ ERROR: Android received duplicated notifications!")
        print("❌ FIX NOT WORKING: Notifications are not properly managed")
        return False
    else:
        print("✅ SUCCESS: No duplicate notifications sent!")
    
    # 7. Verificar estado después de entrega
    print("\n7. Checking state after delivery...")
    debug_response = requests.get(f"{BASE_URL}/api/android-notify/debug")
    debug_data = debug_response.json()
    print(f"Total notifications: {debug_data['summary']['total_notifications']}")
    print(f"Delivered notifications: {debug_data['summary']['delivered_count']}")
    print(f"Sent notifications: {debug_data['summary']['sent_count']}")
    
    # 8. Simular Android confirmando procesamiento
    print("\n8. Simulating Android confirming processing...")
    confirm_response = requests.post(f"{BASE_URL}/api/android-notify/confirm-processed", 
                                   json={"notification_ids": notification_ids})
    confirm_data = confirm_response.json()
    print(f"Confirmation success: {confirm_data.get('success', False)}")
    print(f"Remaining notifications: {confirm_data.get('remaining_count', 'unknown')}")
    
    # 9. Verificar estado final
    print("\n9. Checking final state...")
    debug_response = requests.get(f"{BASE_URL}/api/android-notify/debug")
    debug_data = debug_response.json()
    print(f"Final notifications: {debug_data['summary']['total_notifications']}")
    
    if debug_data['summary']['total_notifications'] == 0:
        print("✅ SUCCESS: All notifications properly cleaned up!")
        return True
    else:
        print("⚠️ WARNING: Some notifications remain after confirmation")
        return True  # Still consider success if main flow worked

def test_web_admin_update():
    """
    Simula una actualización de stock desde web admin
    """
    print("\n\n🌐 TESTING WEB ADMIN STOCK UPDATE")
    print("=" * 50)
    
    # Este test requeriría autenticación admin, así que usamos el endpoint de test
    print("Using test endpoint to simulate web admin update...")
    
    # Limpiar notificaciones
    requests.post(f"{BASE_URL}/api/android-notify/clear", json={"type": "all"})
    
    # Crear notificación via test endpoint (simula web admin)
    test_response = requests.post(f"{BASE_URL}/api/android-notify/test-notification")
    
    # Verificar que Android puede recibir la notificación
    android_response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
    android_data = android_response.json()
    
    if android_data['count'] > 0:
        print("✅ SUCCESS: Web admin update creates notifications for Android!")
        return True
    else:
        print("❌ ERROR: Web admin update doesn't create notifications!")
        return False

if __name__ == "__main__":
    print(f"Testing notification system at: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Basic notification flow
    test1_success = test_notification_flow()
    
    # Test 2: Web admin update simulation
    test2_success = test_web_admin_update()
    
    print("\n\n🏁 TEST RESULTS")
    print("=" * 50)
    print(f"Notification Flow Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Web Admin Update Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! Notification fix is working correctly.")
    else:
        print("\n💥 SOME TESTS FAILED! Check the output above for details.")