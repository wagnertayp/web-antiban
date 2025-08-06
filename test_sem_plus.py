#!/usr/bin/env python3
"""
Teste sem o símbolo + nos números
"""

import os
import requests

def test_sem_plus():
    """Test without + symbol"""
    
    print(f"🧪 TESTE SEM + NO NÚMERO")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # Test both phones without +
    phones = [
        ("776788602173980", "GREEN"),
        ("725492557312328", "RED")
    ]
    
    for phone_id, quality in phones:
        print(f"\n📱 PHONE {quality}: {phone_id}")
        
        headers = {'Authorization': f'Bearer {token}'}
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        
        # Template sem + no número
        payload = {
            'messaging_product': 'whatsapp',
            'to': '5573999084689',  # SEM + ✅
            'type': 'template',
            'template': {
                'name': 'ricardo_template_1753487909_d79bcb95',
                'language': {'code': 'en'},
                'components': [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': 'Pedro'},
                            {'type': 'text', 'text': '073.999.084-68'}
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
        
        print(f"📋 Para: 5573999084689 (SEM +)")
        print(f"📝 Template: ricardo_template_1753487909_d79bcb95")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                contacts = data.get('contacts', [])
                messages = data.get('messages', [])
                
                if contacts:
                    contact = contacts[0]
                    input_number = contact.get('input', 'N/A')
                    wa_id = contact.get('wa_id', 'N/A')
                    print(f"📞 Input: {input_number} → WhatsApp ID: {wa_id}")
                    
                if messages:
                    message = messages[0]
                    message_id = message.get('id', 'N/A')
                    message_status = message.get('message_status', 'N/A')
                    print(f"✉️  Message ID: {message_id}")
                    print(f"📈 Status: {message_status}")
                    print(f"💚 Quality: {quality}")
                    print(f"✅ Enviado SEM + no número")
                    
            else:
                print(f"❌ ERRO: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print(f"\n🎯 TESTE SEM + COMPLETO")
    print(f"📱 Agora verifique se chegam no WhatsApp 73999084689")

if __name__ == "__main__":
    test_sem_plus()