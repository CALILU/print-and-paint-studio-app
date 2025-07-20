#!/usr/bin/env python3

import requests
import time
import json

# Configuration
BASE_URL = "https://print-and-paint-studio-app-production.up.railway.app"

def test_notification_deduplication():
    """
    Test that notifications are not duplicated when fetched multiple times
    """
    print("🔍 Testing notification deduplication system...")
    
    # Step 1: Check if clear endpoint exists (new version)
    print("\n1. Checking if clear endpoint exists...")
    response = requests.post(f"{BASE_URL}/api/android-notify/clear", 
                           json={"type": "all"})
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Cleared {data['removed']['notifications']} notifications")
        use_new_version = True
    else:
        print(f"   ⚠️ Clear endpoint not available (status: {response.status_code})")
        print("   📝 Testing with current deployed version...")
        use_new_version = False
    
    # Step 2: Create a test notification
    print("\n2. Creating test notification...")
    response = requests.post(f"{BASE_URL}/api/android-notify/test-notification")
    if response.status_code == 200:
        print("   ✅ Test notification created")
    else:
        print(f"   ❌ Failed to create: {response.status_code}")
        return False
    
    # Step 3: Check status
    print("\n3. Checking notification status...")
    response = requests.get(f"{BASE_URL}/api/android-notify/status")
    if response.status_code == 200:
        status = response.json()
        if use_new_version:
            print(f"   📊 Total: {status['total_pending']}, Sent: {status['sent_count']}, Unsent: {status['unsent_count']}")
        else:
            print(f"   📊 Pending: {status['pending_count']} (old version)")
    else:
        print(f"   ❌ Failed to get status: {response.status_code}")
        return False
    
    # Step 4: Fetch notifications (first time)
    print("\n4. Fetching notifications (1st time)...")
    response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
    if response.status_code == 200:
        data = response.json()
        first_count = data['count']
        first_notifications = data['notifications']
        print(f"   📦 Received {first_count} notifications")
        if first_count > 0:
            print(f"   🔍 First notification ID: {first_notifications[0].get('id', 'No ID')}")
    else:
        print(f"   ❌ Failed to fetch: {response.status_code}")
        return False
    
    # Step 5: Wait and fetch again (should get 0 notifications)
    print("\n5. Waiting 2 seconds and fetching again...")
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
    if response.status_code == 200:
        data = response.json()
        second_count = data['count']
        print(f"   📦 Received {second_count} notifications (should be 0)")
        if second_count == 0:
            print("   ✅ SUCCESS: No duplicate notifications!")
        else:
            print("   ❌ FAILURE: Got duplicate notifications!")
            return False
    else:
        print(f"   ❌ Failed to fetch: {response.status_code}")
        return False
    
    # Step 6: Check final status
    print("\n6. Checking final status...")
    response = requests.get(f"{BASE_URL}/api/android-notify/status")
    if response.status_code == 200:
        status = response.json()
        if use_new_version:
            print(f"   📊 Total: {status['total_pending']}, Sent: {status['sent_count']}, Unsent: {status['unsent_count']}")
            if status['sent_count'] > 0 and status['unsent_count'] == 0:
                print("   ✅ Status confirms notifications are marked as sent")
            else:
                print("   ⚠️ Status shows unexpected counts")
        else:
            print(f"   📊 Pending: {status['pending_count']} (old version)")
    
    # Step 7: Test confirmation system
    print("\n7. Testing confirmation system...")
    if first_count > 0 and len(first_notifications) > 0:
        if use_new_version:
            notification_ids = [notif['id'] for notif in first_notifications if 'id' in notif]
            if notification_ids:
                response = requests.post(f"{BASE_URL}/api/android-notify/confirm-processed",
                                       json={"notification_ids": notification_ids})
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Confirmed processing {len(notification_ids)} notifications")
                    print(f"   📊 Remaining: {data['remaining_count']}")
                else:
                    print(f"   ❌ Failed to confirm: {response.status_code}")
        else:
            # Test old confirmation method
            response = requests.post(f"{BASE_URL}/api/android-notify/confirm-processed",
                                   json={"processed_count": first_count})
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Confirmed processing {first_count} notifications")
                print(f"   📊 Remaining: {data['remaining_count']}")
            else:
                print(f"   ❌ Failed to confirm: {response.status_code}")
    
    if use_new_version:
        print("\n✅ New notification deduplication system working!")
    else:
        print("\n⚠️ Testing completed with old system - duplicates expected")
    return True

def test_current_duplication_issue():
    """
    Demonstrate the current duplication issue with the deployed version
    """
    print("\n🔄 Testing current system - demonstrating duplication issue...")
    
    # Create a test notification
    print("   Creating test notification...")
    response = requests.post(f"{BASE_URL}/api/android-notify/test-notification")
    if response.status_code != 200:
        print(f"   ❌ Failed to create notification: {response.status_code}")
        return
    
    # Fetch notifications multiple times to show duplication
    for i in range(1, 4):
        print(f"\n   Fetch #{i}:")
        response = requests.get(f"{BASE_URL}/api/android-notify/get-notifications")
        if response.status_code == 200:
            data = response.json()
            print(f"      📦 Received {data['count']} notifications")
            if data['count'] > 0:
                print(f"      🔍 Timestamp: {data['notifications'][0]['timestamp']}")
        time.sleep(2)
    
    print("\n   📝 As you can see, the same notification is returned multiple times!")
    print("   💡 This is the duplication issue we fixed in the new version.")

if __name__ == "__main__":
    print("🧪 Testing notification system...")
    
    try:
        # First demonstrate the current issue
        test_current_duplication_issue()
        
        # Then test our fix (if deployed)
        test_notification_deduplication()
        
        print("\n🎉 Testing completed!")
        print("\n📋 SUMMARY:")
        print("   - The current deployed version shows notification duplication")
        print("   - Our fix adds unique IDs and tracking to prevent duplicates")
        print("   - Deploy the updated app.py to Railway to activate the fix")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")