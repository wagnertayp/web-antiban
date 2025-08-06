#!/usr/bin/env python3
"""
Teste para verificar se estamos em SANDBOX vs PRODUCTION mode
"""

import os
import requests

def debug_sandbox_production():
    """Debug if we're in sandbox vs production"""
    
    print(f"🔍 TESTE SANDBOX VS PRODUCTION")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # 1. Verificar account mode dos phones
    print(f"\n1️⃣ VERIFICANDO ACCOUNT MODE")
    
    phones = ["776788602173980", "725492557312328"]
    headers = {'Authorization': f'Bearer {token}'}
    
    for phone_id in phones:
        url = f"https://graph.facebook.com/v22.0/{phone_id}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                account_mode = data.get('account_mode', 'N/A')
                display_number = data.get('display_phone_number', 'N/A')
                quality = data.get('quality_rating', 'N/A')
                
                print(f"📱 {phone_id} ({display_number}):")
                print(f"   Account Mode: {account_mode}")
                print(f"   Quality: {quality}")
                
                # SANDBOX só permite números test específicos
                if account_mode == 'SANDBOX':
                    print(f"   ⚠️  SANDBOX MODE - só aceita números test!")
                elif account_mode == 'LIVE':
                    print(f"   ✅ LIVE MODE - aceita qualquer número")
                else:
                    print(f"   ❓ Mode desconhecido: {account_mode}")
                    
        except Exception as e:
            print(f"❌ Erro phone {phone_id}: {e}")
    
    # 2. Testar com números oficiais de teste do WhatsApp
    print(f"\n2️⃣ TESTANDO COM NÚMEROS DE TESTE OFICIAIS")
    
    # Números de teste oficiais do WhatsApp Business API
    test_numbers = [
        "15551234567",     # US test number
        "447700900000",    # UK test number  
        "5511987654321"    # BR test number
    ]
    
    phone_id = "776788602173980"  # Use GREEN phone
    
    for test_number in test_numbers:
        print(f"\n📞 Testando para: +{test_number}")
        
        # Try simple text message first
        payload = {
            'messaging_product': 'whatsapp',
            'to': test_number,
            'type': 'text',
            'text': {
                'body': 'Test message to verify delivery'
            }
        }
        
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                messages = data.get('messages', [])
                
                if contacts:
                    contact = contacts[0]
                    wa_id = contact.get('wa_id', 'N/A')
                    print(f"   WhatsApp ID: {wa_id}")
                    
                if messages:
                    message = messages[0]
                    message_id = message.get('id', 'N/A')
                    print(f"   Message ID: {message_id}")
                    print(f"   ✅ ACEITO - pode ser problema de entrega real vs test")
                    
            else:
                error_data = response.json().get('error', {})
                error_code = error_data.get('code', 'N/A')
                error_msg = error_data.get('message', 'N/A')
                print(f"   ❌ Error {error_code}: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # 3. Verificar permissões do token
    print(f"\n3️⃣ VERIFICANDO PERMISSÕES DO TOKEN")
    
    # Get token info
    token_url = f"https://graph.facebook.com/v22.0/me?access_token={token}"
    
    try:
        response = requests.get(token_url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido para: {data.get('name', 'N/A')} (ID: {data.get('id', 'N/A')})")
        else:
            print(f"❌ Token error: {response.text}")
            
    except Exception as e:
        print(f"❌ Token exception: {e}")
    
    print(f"\n🎯 DIAGNÓSTICO FINAL")
    print(f"POSSÍVEIS CAUSAS:")
    print(f"1. SANDBOX MODE - só aceita números específicos de teste")
    print(f"2. Token sem permissão 'whatsapp_business_messaging'")
    print(f"3. Phone numbers em revisão pela Meta")
    print(f"4. Business Manager com restrições")
    print(f"5. Necessário adicionar número do usuário como teste primeiro")

if __name__ == "__main__":
    debug_sandbox_production()