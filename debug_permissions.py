#!/usr/bin/env python3
import requests
import os

def debug_permissions():
    """Debug permissions and phone number association"""
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "674928665709899"
    business_id = "746006914691827"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 1. Verificar phone number permissions
    print("=== 1. Phone Number Permissions ===")
    phone_url = f"https://graph.facebook.com/v23.0/{phone_id}?fields=verified_name,display_phone_number,quality_rating,messaging_limit,throughput"
    response = requests.get(phone_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 2. Verificar Business Account permissions
    print("\n=== 2. Business Account Info ===")
    business_url = f"https://graph.facebook.com/v23.0/{business_id}?fields=name,business_verification_status,primary_page"
    response = requests.get(business_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 3. Verificar se phone number está associado ao business account
    print("\n=== 3. Phone Numbers no Business Account ===")
    phones_url = f"https://graph.facebook.com/v23.0/{business_id}/phone_numbers"
    response = requests.get(phones_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 4. Verificar apps associados
    print("\n=== 4. Apps do Business Account ===")
    apps_url = f"https://graph.facebook.com/v23.0/{business_id}/client_whatsapp_business_accounts"
    response = requests.get(apps_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 5. Testar com template mais simples que sabemos que existe
    print("\n=== 5. Testando template modelo1 ===")
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
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
                }
            ]
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_permissions()
