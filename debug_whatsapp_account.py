#!/usr/bin/env python3
"""
Debug da conta WhatsApp Business - verificar status e restrições
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def debug_whatsapp_account():
    """Debug completo da conta WhatsApp Business"""
    
    print("🔍 DEBUG COMPLETO DA CONTA WHATSAPP BUSINESS")
    print("=" * 50)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    business_id = "746006914691827"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 1. Verificar detalhes completos do número
    print("1. VERIFICANDO DETALHES DO NÚMERO WHATSAPP")
    print("-" * 40)
    
    try:
        response = requests.get(f'https://graph.facebook.com/v23.0/{phone_number_id}', headers=headers)
        if response.status_code == 200:
            phone_data = response.json()
            print(f"✅ Display Phone: {phone_data.get('display_phone_number')}")
            print(f"✅ Verified Name: {phone_data.get('verified_name')}")
            print(f"✅ Status: {phone_data.get('status')}")
            print(f"✅ Quality Rating: {phone_data.get('quality_rating')}")
            print(f"✅ Throughput: {phone_data.get('throughput')}")
            print(f"✅ Is Business Verified: {phone_data.get('is_business_verified')}")
            print(f"✅ Account Mode: {phone_data.get('account_mode')}")
            print(f"✅ Certificate: {phone_data.get('certificate')}")
            print(f"✅ Name Status: {phone_data.get('name_status')}")
            print(f"✅ Code Verification Status: {phone_data.get('code_verification_status')}")
            
            # Verificar se há restrições
            restrictions = phone_data.get('messaging_limit_tier')
            if restrictions:
                print(f"⚠️ Messaging Limit Tier: {restrictions}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 2. Verificar Business Account
    print("\n2. VERIFICANDO BUSINESS ACCOUNT")
    print("-" * 40)
    
    try:
        response = requests.get(f'https://graph.facebook.com/v23.0/{business_id}', headers=headers)
        if response.status_code == 200:
            business_data = response.json()
            print(f"✅ Business Name: {business_data.get('name')}")
            print(f"✅ Business ID: {business_data.get('id')}")
            print(f"✅ Status: {business_data.get('business_status')}")
            print(f"✅ Verification Status: {business_data.get('verification_status')}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 3. Verificar Analytics e Insights
    print("\n3. VERIFICANDO ANALYTICS")
    print("-" * 40)
    
    try:
        # Tentar obter insights sobre mensagens
        insights_url = f'https://graph.facebook.com/v23.0/{phone_number_id}/analytics'
        response = requests.get(insights_url, headers=headers)
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ Analytics disponíveis: {analytics}")
        else:
            print(f"⚠️ Analytics não disponíveis: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Analytics error: {str(e)}")
    
    # 4. Verificar restrições de mensagens
    print("\n4. VERIFICANDO RESTRIÇÕES")
    print("-" * 40)
    
    try:
        # Verificar se há limitações na conta
        restrictions_url = f'https://graph.facebook.com/v23.0/{business_id}/phone_numbers'
        response = requests.get(restrictions_url, headers=headers)
        if response.status_code == 200:
            phone_numbers = response.json()
            print(f"✅ Phone numbers da conta: {phone_numbers}")
            
            for phone in phone_numbers.get('data', []):
                if phone.get('id') == phone_number_id:
                    print(f"✅ Status do nosso número: {phone.get('status')}")
                    print(f"✅ Quality Rating: {phone.get('quality_rating')}")
                    print(f"✅ Throughput: {phone.get('throughput')}")
        else:
            print(f"❌ Erro ao verificar restrições: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 5. Testar com número próprio da conta
    print("\n5. TESTANDO COM NÚMERO PRÓPRIO")
    print("-" * 40)
    
    # Vamos tentar enviar para o próprio número (15558149312)
    self_test_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "+15558149312",  # Número próprio da conta
        "type": "text",
        "text": {
            "body": f"🔍 AUTOTESTE - {time.strftime('%H:%M:%S')}\n\nTeste enviado para o próprio número da conta para verificar funcionamento."
        }
    }
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=self_test_payload
        )
        
        print(f"Status do autoteste: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"✅ Autoteste Message ID: {message_id}")
        
    except Exception as e:
        print(f"❌ Erro no autoteste: {str(e)}")
    
    # 6. Verificar último erro conhecido
    print("\n6. VERIFICANDO HISTÓRICO DE ERROS")
    print("-" * 40)
    
    try:
        # Tentar obter logs de erro se disponíveis
        logs_url = f'https://graph.facebook.com/v23.0/{business_id}/logs'
        response = requests.get(logs_url, headers=headers)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Logs disponíveis: {logs}")
        else:
            print(f"⚠️ Logs não disponíveis: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Logs error: {str(e)}")
    
    print("\n🏁 DEBUG CONCLUÍDO")
    print("Verifique se alguma restrição foi identificada.")

if __name__ == "__main__":
    debug_whatsapp_account()