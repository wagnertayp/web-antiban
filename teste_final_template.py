#!/usr/bin/env python3
"""
Teste final com template após configuração
"""

import os
import requests

def teste_final_template():
    """Final template test after configuration"""
    
    print(f"🎯 TESTE FINAL COM TEMPLATE")
    print("=" * 40)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "776788602173980"  # GREEN phone
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Template test
    payload = {
        'messaging_product': 'whatsapp',
        'to': '5573999084689',
        'type': 'template',
        'template': {
            'name': 'ricardo_template_1753487909_d79bcb95',
            'language': {'code': 'en'},
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': 'Pedro'},           # {{1}} = Nome
                        {'type': 'text', 'text': '073.999.084-68'}  # {{2}} = CPF
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [{'type': 'text', 'text': '073.999.084-68'}]
                }
            ]
        }
    }
    
    print(f"📱 Para: 5573999084689")
    print(f"📝 Template: ricardo_template_1753487909_d79bcb95")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            print(f"✅ Template enviado!")
            print(f"📨 Message ID: {message_id}")
            print(f"🎯 SISTEMA FUNCIONANDO 100%!")
            
            return message_id
            
        else:
            print(f"❌ Template error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    teste_final_template()