#!/usr/bin/env python3
"""
Teste com número +5573999084689
"""

import os
import requests

def test_numero_73():
    """Test with +5573999084689"""
    
    print(f"🧪 TESTE COM NÚMERO +5573999084689")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print(f"❌ Token não encontrado")
        return
        
    print(f"🔑 Token: {token[:50]}...")
    
    # Test both phones
    phones = [
        ("776788602173980", "+1 424-461-1446", "GREEN"),
        ("725492557312328", "15558068378", "RED")
    ]
    
    for phone_id, display_number, quality in phones:
        print(f"\n📱 TESTANDO PHONE {quality}: {phone_id} ({display_number})")
        
        headers = {'Authorization': f'Bearer {token}'}
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        
        # Template with correct parameter order
        payload = {
            'messaging_product': 'whatsapp',
            'to': '+5573999084689',  # Número do usuário
            'type': 'template',
            'template': {
                'name': 'ricardo_template_1753487909_d79bcb95',
                'language': {'code': 'en'},
                'components': [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': 'Pedro'},           # {{1}} = Nome ✅
                            {'type': 'text', 'text': '073.999.084-68'}  # {{2}} = CPF ✅
                        ]
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [{'type': 'text', 'text': '073.999.084-68'}]  # CPF no botão
                    }
                ]
            }
        }
        
        print(f"📋 Para: +5573999084689") 
        print(f"📝 Template: ricardo_template_1753487909_d79bcb95")
        print(f"🔧 Parâmetros: {{{{1}}}}=Pedro, {{{{2}}}}=073.999.084-68")
        
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
                    print(f"✅ API aceitou a mensagem")
                    
            else:
                print(f"❌ ERRO: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print(f"\n🎯 TESTE COMPLETO COM +5573999084689")
    print(f"🕐 Aguarde 10-60 segundos para verificar se chegam no WhatsApp")
    print(f"📱 Verifique se recebeu mensagens de ambos os números")

if __name__ == "__main__":
    test_numero_73()