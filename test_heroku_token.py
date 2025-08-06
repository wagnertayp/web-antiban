#!/usr/bin/env python3
"""
Test script to verify Heroku token handling
"""
import requests
import json
import time

def test_heroku_token():
    """Test if Heroku is using the token from interface correctly"""
    
    # Test data - real numbers for validation
    test_data = {
        "leads": "+5561999114066,Pedro,065.370.801-77",
        "template_names": ["ricardo_template_1753487909_d79bcb95"],
        "phone_number_ids": ["732911983238956"],
        "whatsapp_connection": {
            "access_token": "EAAHUCvWVsdgBPBQcf6RR09biZAHXwJD3AQ4gVODA65jwoS5Yy",
            "business_manager_id": "2089992404820473"
        }
    }
    
    print("🧪 TESTANDO HEROKU TOKEN HANDLING...")
    print(f"📱 Phone ID: {test_data['phone_number_ids'][0]}")
    print(f"🔑 Token: {test_data['whatsapp_connection']['access_token'][:50]}...")
    print(f"📝 Template: {test_data['template_names'][0]}")
    
    try:
        # Send test request
        response = requests.post(
            'https://disparador-85c599c32e28.herokuapp.com/api/ultra-speed',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"\n📊 RESPONSE STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result}")
            
            # Check progress after a delay
            session_id = result.get('session_id')
            if session_id:
                print(f"\n🔍 CHECKING PROGRESS: Session {session_id}")
                time.sleep(3)
                
                progress_response = requests.get(
                    f'https://disparador-85c599c32e28.herokuapp.com/api/progress/{session_id}',
                    timeout=10
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"📈 PROGRESS: {progress}")
                    
                    if progress.get('sent', 0) > 0:
                        print("🎉 HEROKU TOKEN WORKING! Messages sent successfully!")
                        return True
                    else:
                        print("❌ HEROKU TOKEN ISSUE: 0 messages sent")
                        return False
                else:
                    print(f"❌ Progress check failed: {progress_response.status_code}")
                    return False
        else:
            error_text = response.text
            print(f"❌ ERROR RESPONSE: {error_text}")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_heroku_token()
    print(f"\n🏁 FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")