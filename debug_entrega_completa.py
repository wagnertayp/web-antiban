#!/usr/bin/env python3
"""
Debug completo para descobrir por que mensagens não chegam
"""

import os
import sys
import logging
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_delivery():
    """Debug complete delivery pipeline"""
    
    print(f"🔍 INVESTIGANDO POR QUE MENSAGENS NÃO CHEGAM")
    print("=" * 60)
    
    # Get token from environment
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print(f"❌ Token não encontrado")
        return
        
    print(f"🔑 Token: {token[:50]}...")
    
    # Headers for all requests
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Discover Business Manager and phones
    print(f"\n🏢 DESCOBRINDO BUSINESS MANAGER")
    try:
        url = f"https://graph.facebook.com/v22.0/me?fields=whatsapp_business_accounts"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            waba = data.get('whatsapp_business_accounts', {}).get('data', [])
            
            for account in waba:
                account_id = account.get('id')
                account_name = account.get('name', 'N/A')
                print(f"   📱 BM: {account_name} (ID: {account_id})")
                
                # Get phones for this BM
                phones_url = f"https://graph.facebook.com/v22.0/{account_id}/phone_numbers"
                phones_response = requests.get(phones_url, headers=headers, timeout=10)
                
                if phones_response.status_code == 200:
                    phones_data = phones_response.json()
                    phones = phones_data.get('data', [])
                    print(f"   📞 {len(phones)} phone numbers:")
                    
                    green_phones = []
                    red_phones = []
                    unknown_phones = []
                    
                    for phone in phones:
                        phone_id = phone.get('id')
                        display = phone.get('display_phone_number', 'N/A')
                        quality = phone.get('quality_rating', 'UNKNOWN')
                        status = phone.get('status', 'N/A')
                        
                        phone_info = f"     - {display} (ID: {phone_id}) - Quality: {quality}, Status: {status}"
                        print(phone_info)
                        
                        if quality == 'GREEN':
                            green_phones.append(phone_id)
                        elif quality == 'RED':
                            red_phones.append(phone_id)
                        else:
                            unknown_phones.append(phone_id)
                    
                    print(f"   💚 GREEN phones: {len(green_phones)}")
                    print(f"   🔴 RED phones: {len(red_phones)}")  
                    print(f"   ⚪ UNKNOWN phones: {len(unknown_phones)}")
                    
                    # Test message with GREEN phone if available
                    if green_phones:
                        print(f"\n🧪 TESTANDO COM PHONE GREEN: {green_phones[0]}")
                        test_green_phone(green_phones[0], token)
                    elif unknown_phones:
                        print(f"\n🧪 TESTANDO COM PHONE UNKNOWN: {unknown_phones[0]}")
                        test_green_phone(unknown_phones[0], token)
                    else:
                        print(f"\n⚠️  NENHUM PHONE DISPONÍVEL PARA TESTE")
                        
        else:
            print(f"❌ Erro ao buscar BM: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao descobrir BM: {e}")

def test_green_phone(phone_id, token):
    """Test message with specific phone"""
    
    print(f"🚀 ENVIANDO MENSAGEM DE TESTE")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Test with template message
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
                        {'type': 'text', 'text': 'Pedro'},           # {{1}} = Nome
                        {'type': 'text', 'text': '065.370.801-77'}  # {{2}} = CPF
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
    print(f"🔧 Parâmetros: {{{{1}}}}=Pedro, {{{{2}}}}=065.370.801-77")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract details
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
                
                # Check if WhatsApp ID was resolved
                if wa_id and wa_id != input_number:
                    print(f"✅ NÚMERO VÁLIDO: WhatsApp ID resolvido corretamente")
                    
                    # Wait and check message status
                    print(f"⏳ Aguardando 10 segundos para verificar status...")
                    time.sleep(10)
                    
                    # Try to get message status (may not be available)
                    try:
                        status_url = f"https://graph.facebook.com/v22.0/{message_id}"
                        status_response = requests.get(status_url, headers=headers, timeout=10)
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"📊 Message status: {status_data}")
                        else:
                            print(f"⚠️  Status não disponível: {status_response.status_code}")
                            
                    except Exception as e:
                        print(f"⚠️  Não foi possível verificar status: {e}")
                        
                    print(f"\n🤔 DIAGNÓSTICO:")
                    print(f"   ✅ API retornou 200 OK")
                    print(f"   ✅ Message ID gerado: {message_id}")
                    print(f"   ✅ WhatsApp ID resolvido: {wa_id}")
                    print(f"   ✅ Message status: {message_status}")
                    print(f"   🔍 Se mensagem não chegou, pode ser:")
                    print(f"      - Phone number com restrições da Meta")
                    print(f"      - Número bloqueado/inválido")
                    print(f"      - Template pausado temporariamente")
                    print(f"      - Delay de entrega da rede WhatsApp")
                    
                else:
                    print(f"❌ NÚMERO INVÁLIDO: WhatsApp ID não resolvido")
                    
        else:
            print(f"❌ ERRO: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Also test with simple text message
    print(f"\n🧪 TESTANDO MENSAGEM DE TEXTO SIMPLES")
    
    text_payload = {
        'messaging_product': 'whatsapp',
        'to': '+5561999114066',
        'type': 'text',
        'text': {
            'body': 'Teste de entrega - mensagem de texto simples'
        }
    }
    
    try:
        text_response = requests.post(url, json=text_payload, headers=headers, timeout=30)
        
        print(f"📊 Status texto: {text_response.status_code}")
        print(f"📋 Response texto: {text_response.text}")
        
        if text_response.status_code == 200:
            text_data = text_response.json()
            text_messages = text_data.get('messages', [])
            
            if text_messages:
                text_message_id = text_messages[0].get('id', 'N/A')
                print(f"✉️  Text Message ID: {text_message_id}")
                print(f"💬 Mensagem de texto enviada - verifique se chega")
        else:
            print(f"❌ Erro texto: {text_response.text}")
            
    except Exception as e:
        print(f"❌ Erro texto: {e}")

if __name__ == "__main__":
    debug_delivery()