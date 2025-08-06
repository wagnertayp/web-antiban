#!/usr/bin/env python3
import requests

def test_modelo1():
    token = 'EAAYLvZBaHbvYBPKCwMnvhXM2kPkWMUlyhVqjtgplZAGrZCRtxZAvH6lZCfP9voDg6UByPd7q6ZBx76kRGMoFsnhBiP7ScXOYD5LqRRppEjc71PRapP1S5oAJCPsoXn9kkPlUMURv53nG0V2wZC5iXZAiZAfSfTGvqsX2NzENeoKDVoura97AZAOxsDd21f97RJJcQSUxfnZBB9x1UkfbUnAU0hLo9N3rZAOwJS4UGLWQwjRVsB0ZD'
    phone_id = "674928665709899"
    
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test modelo1 com parâmetros
    payload = {
        'messaging_product': 'whatsapp',
        'to': '5561982132603',
        'type': 'template',
        'template': {
            'name': 'modelo1',
            'language': {'code': 'en'},
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': '065.370.801-77'},
                        {'type': 'text', 'text': 'Pedro'}
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {'type': 'text', 'text': '065.370.801-77'}
                    ]
                }
            ]
        }
    }
    
    print("=== Testing modelo1 ===")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        message_id = data.get('messages', [{}])[0].get('id', '')
        print(f"✅ SUCCESS! Message ID: {message_id}")
        return True
    else:
        print(f"❌ FAILED: {response.status_code}")
    
    return False

if __name__ == "__main__":
    test_modelo1()
