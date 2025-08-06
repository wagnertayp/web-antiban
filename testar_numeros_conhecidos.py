#!/usr/bin/env python3
"""
Testar com números conhecidos que funcionam
"""

import os
import requests

def testar_numeros_conhecidos():
    """Test with known working numbers"""
    
    print(f"🧪 TESTE COM NÚMEROS CONHECIDOS QUE FUNCIONAM")
    print("=" * 60)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "776788602173980"  # GREEN phone
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Números de teste que já funcionaram nos testes anteriores
    test_numbers = [
        "15551234567",     # US test - funcionou antes
        "5561999114066",   # Número original do usuário que você mencionou
        "557399084689"     # Número atual formatado sem +
    ]
    
    for number in test_numbers:
        print(f"\n📞 TESTANDO NÚMERO: {number}")
        
        # Teste com mensagem simples
        payload = {
            'messaging_product': 'whatsapp',
            'to': number,
            'type': 'text',
            'text': {
                'body': f'TESTE PARA {number} - Se esta mensagem chegar, o número funciona!'
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                contacts = data.get('contacts', [])
                messages = data.get('messages', [])
                
                if contacts:
                    contact = contacts[0]
                    input_number = contact.get('input', 'N/A')
                    wa_id = contact.get('wa_id', 'N/A')
                    print(f"📱 Input: {input_number} → WhatsApp ID: {wa_id}")
                    
                if messages:
                    message = messages[0]
                    message_id = message.get('id', 'N/A')
                    message_status = message.get('message_status', 'N/A')
                    print(f"✉️  Message ID: {message_id}")
                    print(f"📈 Status: {message_status}")
                    
                    if number in ["5561999114066", "557399084689"]:
                        print(f"🎯 NÚMERO DO USUÁRIO - verifique WhatsApp!")
                    else:
                        print(f"📋 Número de teste - confirmando conectividade")
                        
            else:
                error_data = response.json().get('error', {})
                error_code = error_data.get('code', 'N/A')
                error_msg = error_data.get('message', 'N/A')
                print(f"❌ Error {error_code}: {error_msg}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Teste especial com template para 5561999114066
    print(f"\n🎯 TESTE ESPECIAL COM TEMPLATE PARA 5561999114066")
    
    template_payload = {
        'messaging_product': 'whatsapp',
        'to': '5561999114066',
        'type': 'template',
        'template': {
            'name': 'ricardo_template_1753487909_d79bcb95',
            'language': {'code': 'en'},
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': 'Pedro'},
                        {'type': 'text', 'text': '061.999.114-06'}
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [{'type': 'text', 'text': '061.999.114-06'}]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=template_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            print(f"✅ Template enviado para 5561999114066!")
            print(f"📨 Message ID: {message_id}")
            print(f"📱 VERIFIQUE WHATSAPP +5561999114066")
            
        else:
            print(f"❌ Template error: {response.text}")
            
    except Exception as e:
        print(f"❌ Template exception: {e}")
    
    print(f"\n🎯 ANÁLISE FINAL:")
    print(f"Se 15551234567 funciona mas números brasileiros não:")
    print(f"1. Conta limitada geograficamente")
    print(f"2. Números brasileiros precisam de aprovação especial")
    print(f"3. Sandbox mode só aceita números US/internacionais")
    print(f"4. Business Manager precisa de upgrade para produção")

if __name__ == "__main__":
    testar_numeros_conhecidos()