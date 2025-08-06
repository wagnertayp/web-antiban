#!/usr/bin/env python3
import requests
import os

def test_modelo2_direct():
    """Test modelo2 directly using the exact structure found"""
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "674928665709899"
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test with the exact structure from the API discovery
    payload = {
        'messaging_product': 'whatsapp',
        'to': '+5561982132603',
        'type': 'template',
        'template': {
            'name': 'modelo2',
            'language': {
                'code': 'en'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': '065.370.801-77'  # {{1}} = CPF
                        },
                        {
                            'type': 'text',
                            'text': 'Pedro'  # {{2}} = Nome
                        }
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {
                            'type': 'text',
                            'text': '065.370.801-77'  # Button parameter = CPF
                        }
                    ]
                }
            ]
        }
    }
    
    print("=== Testing modelo2 without header/footer ===")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        message_id = data.get('messages', [{}])[0].get('id', '')
        print(f"✅ SUCCESS! Message ID: {message_id}")
        return True
    
    # Try without any components except body
    payload2 = {
        'messaging_product': 'whatsapp',
        'to': '+5561982132603',
        'type': 'template',
        'template': {
            'name': 'modelo2',
            'language': {
                'code': 'en'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': '065.370.801-77'  # {{1}} = CPF
                        },
                        {
                            'type': 'text',
                            'text': 'Pedro'  # {{2}} = Nome
                        }
                    ]
                }
            ]
        }
    }
    
    print("\n=== Testing modelo2 body only ===")
    response2 = requests.post(url, json=payload2, headers=headers)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
    
    if response2.status_code == 200:
        data = response2.json()
        message_id = data.get('messages', [{}])[0].get('id', '')
        print(f"✅ SUCCESS! Message ID: {message_id}")
        return True
    
    return False

if __name__ == "__main__":
    test_modelo2_direct()
