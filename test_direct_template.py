#!/usr/bin/env python3
"""
Teste direto de template com phone GREEN
"""

import os
import requests

def test_direct_template():
    """Test direct template sending"""
    
    print(f"🧪 TESTE DIRETO COM PHONE GREEN")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print(f"❌ Token não encontrado")
        return
        
    print(f"🔑 Token atualizado: {token[:50]}...")
    
    # Use GREEN phone
    phone_id = "776788602173980"  # +1 424-461-1446 (Quality: GREEN)
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Template with correct parameter order
    payload = {
        'messaging_product': 'whatsapp',
        'to': '+5561999114066',
        'type': 'template',
        'template': {
            'name': 'ricardo_template_1753487909_d79bcb95',
            'language': {'code': 'en'},
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': 'Pedro'},           # {{1}} = Nome ✅
                        {'type': 'text', 'text': '065.370.801-77'}  # {{2}} = CPF ✅
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [{'type': 'text', 'text': '065.370.801-77'}]  # CPF no botão
                }
            ]
        }
    }
    
    print(f"📱 Phone GREEN: {phone_id} (+1 424-461-1446)")
    print(f"📋 Para: +5561999114066") 
    print(f"📝 Template: ricardo_template_1753487909_d79bcb95")
    print(f"🔧 Parâmetros: {{{{1}}}}=Pedro, {{{{2}}}}=065.370.801-77")
    
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
                
                print(f"\n🎯 TESTE COM PHONE GREEN CONCLUÍDO!")
                print(f"💚 Phone Quality: GREEN")
                print(f"✅ API Status: {response.status_code} OK")
                print(f"📨 Message aceito pela API")
                print(f"🕐 Aguarde 10-30 segundos para verificar se chega")
                
                return message_id
                
        else:
            print(f"❌ ERRO: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

if __name__ == "__main__":
    test_direct_template()