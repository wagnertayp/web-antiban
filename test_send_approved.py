#!/usr/bin/env python3
"""
Teste direto para enviar templates aprovados
"""
import os
import requests

def test_send_template():
    """Testar envio do template modelo2 (mais simples)"""
    
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Usar Phone ID 1
    phone_id = "709194588941211"
    to_number = "+5561982132603"
    
    print(f"📱 Testando Phone ID: {phone_id}")
    print(f"📞 Para número: {to_number}")
    
    # TESTE 1: Template modelo2 (mais simples - sem parâmetros)
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'type': 'template',
        'template': {
            'name': 'modelo2',
            'language': {
                'code': 'en'
            }
        }
    }
    
    print(f"\n🧪 TESTE 1: Template modelo2")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('messages'):
                message_id = data['messages'][0].get('id', '')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                return True
        else:
            print(f"❌ FALHA: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    return False

def test_send_codig():
    """Testar template codig com parâmetros"""
    
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Usar Phone ID 1
    phone_id = "709194588941211"
    to_number = "+5561982132603"
    
    print(f"\n📱 Testando Phone ID: {phone_id}")
    print(f"📞 Para número: {to_number}")
    
    # TESTE 2: Template codig (com parâmetro)
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'type': 'template',
        'template': {
            'name': 'codig',
            'language': {
                'code': 'pt_BR'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': '065.370.801-77'
                        }
                    ]
                }
            ]
        }
    }
    
    print(f"\n🧪 TESTE 2: Template codig")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('messages'):
                message_id = data['messages'][0].get('id', '')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                return True
        else:
            print(f"❌ FALHA: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 TESTANDO TEMPLATES APROVADOS REAIS")
    
    # Teste modelo2 primeiro (mais simples)
    success1 = test_send_template()
    
    # Teste codig com parâmetros
    success2 = test_send_codig()
    
    if success1 or success2:
        print(f"\n✅ PELO MENOS UM TEMPLATE FUNCIONOU!")
    else:
        print(f"\n❌ NENHUM TEMPLATE FUNCIONOU - INVESTIGAR MAIS")