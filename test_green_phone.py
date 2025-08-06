#!/usr/bin/env python3
"""
Teste com phone GREEN para verificar entrega
"""

import os
import requests
import time

def test_green_delivery():
    """Test delivery with GREEN quality phone"""
    
    print(f"🧪 TESTANDO ENTREGA COM PHONE QUALITY GREEN")
    print("=" * 60)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print(f"❌ Token não encontrado")
        return
        
    print(f"🔑 Token: {token[:50]}...")
    
    # Headers
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test different Business Manager endpoints to find the correct one
    bm_ids = ["2089992404820473"]  # Your BM ID
    
    for bm_id in bm_ids:
        print(f"\n🏢 TESTANDO BM: {bm_id}")
        
        # Get phones from this BM
        phones_url = f"https://graph.facebook.com/v22.0/{bm_id}/phone_numbers"
        
        try:
            phones_response = requests.get(phones_url, headers=headers, timeout=10)
            
            if phones_response.status_code == 200:
                phones_data = phones_response.json()
                phones = phones_data.get('data', [])
                
                print(f"📞 {len(phones)} phone numbers encontrados:")
                
                green_phones = []
                for phone in phones:
                    phone_id = phone.get('id')
                    display = phone.get('display_phone_number', 'N/A')
                    quality = phone.get('quality_rating', 'UNKNOWN')
                    status = phone.get('status', 'N/A')
                    
                    print(f"   - {display} (ID: {phone_id}) - Quality: {quality}, Status: {status}")
                    
                    if quality == 'GREEN':
                        green_phones.append(phone_id)
                
                # Test with GREEN phone if available
                if green_phones:
                    print(f"\n💚 TESTANDO COM PHONE GREEN: {green_phones[0]}")
                    test_message_delivery(green_phones[0], token)
                else:
                    print(f"⚠️  Nenhum phone GREEN disponível, testando com primeiro phone")
                    if phones:
                        test_message_delivery(phones[0]['id'], token)
                        
            else:
                print(f"❌ Erro ao buscar phones: {phones_response.status_code} - {phones_response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_message_delivery(phone_id, token):
    """Test message delivery to specific phone"""
    
    print(f"🚀 ENVIANDO MENSAGEM DE TESTE")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Test with corrected template order
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
    
    print(f"📱 Phone ID: {phone_id}")
    print(f"📋 Para: +5561999114066")
    print(f"📝 Template: ricardo_template_1753487909_d79bcb95")
    print(f"🔧 Parâmetros CORRETOS: {{{{1}}}}=Pedro, {{{{2}}}}=065.370.801-77")
    
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
                
                print(f"\n✅ MENSAGEM ENVIADA COM SUCESSO!")
                print(f"🕐 Aguarde 10-30 segundos para a mensagem chegar no WhatsApp")
                print(f"📱 Verifique o WhatsApp do número: +5561999114066")
                
                # Additional logging
                print(f"\n📋 DETALHES TÉCNICOS:")
                print(f"   - API Status: {response.status_code} OK")
                print(f"   - Message ID: {message_id}")
                print(f"   - WhatsApp ID resolvido: {wa_id}")
                print(f"   - Phone Number ID: {phone_id}")
                print(f"   - Template usado: ricardo_template_1753487909_d79bcb95")
                print(f"   - Ordem parâmetros: {{{{1}}}}=Pedro, {{{{2}}}}=CPF")
                
                # Test simple text message for comparison
                print(f"\n🧪 ENVIANDO MENSAGEM DE TEXTO PARA COMPARAÇÃO")
                
                text_payload = {
                    'messaging_product': 'whatsapp',
                    'to': '+5561999114066',
                    'type': 'text',
                    'text': {
                        'body': 'Teste de texto simples - se esta mensagem chegar, o problema não é de conectividade'
                    }
                }
                
                text_response = requests.post(url, json=text_payload, headers=headers, timeout=30)
                
                if text_response.status_code == 200:
                    text_data = text_response.json()
                    text_messages = text_data.get('messages', [])
                    
                    if text_messages:
                        text_message_id = text_messages[0].get('id', 'N/A')
                        print(f"✅ Texto enviado - Message ID: {text_message_id}")
                else:
                    print(f"❌ Erro no texto: {text_response.text}")
                
        else:
            print(f"❌ ERRO: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_green_delivery()