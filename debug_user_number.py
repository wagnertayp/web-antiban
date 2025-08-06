#!/usr/bin/env python3
"""
Debug específico do número do usuário - Por que não chegou?
"""

import requests
import time

def debug_user_number():
    """Debug específico para o número do usuário"""
    
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    business_account_id = "639849885789886"
    phone_id = "743171782208180"
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    user_number = "+5561999114066"
    
    print("🔍 INVESTIGANDO POR QUE MENSAGEM NÃO CHEGOU...")
    print(f"📱 Número alvo: {user_number}")
    print(f"📋 Phone ID: {phone_id}")
    print(f"🏢 Business Manager: {business_account_id}")
    
    # 1. Verificar status detalhado da conta WhatsApp Business
    print("\n1️⃣ Verificando status da conta WhatsApp Business...")
    
    account_response = requests.get(
        f"{base_url}/{business_account_id}",
        headers=headers,
        timeout=10
    )
    
    if account_response.status_code == 200:
        account_data = account_response.json()
        print(f"✅ Account Name: {account_data.get('name')}")
        print(f"✅ Currency: {account_data.get('currency')}")
        print(f"✅ Namespace: {account_data.get('message_template_namespace')}")
    else:
        print(f"❌ Erro na conta: {account_response.status_code}")
    
    # 2. Verificar status específico do phone number
    print(f"\n2️⃣ Verificando phone number {phone_id}...")
    
    phone_response = requests.get(
        f"{base_url}/{phone_id}",
        headers=headers,
        timeout=10
    )
    
    if phone_response.status_code == 200:
        phone_data = phone_response.json()
        print(f"✅ Display Number: {phone_data.get('display_phone_number')}")
        print(f"✅ Quality Rating: {phone_data.get('quality_rating')}")
        print(f"✅ Verification Status: {phone_data.get('code_verification_status')}")
        print(f"✅ Platform: {phone_data.get('platform_type')}")
        print(f"✅ Throughput: {phone_data.get('throughput', {}).get('level')}")
    else:
        print(f"❌ Erro no phone: {phone_response.status_code}")
    
    # 3. Testar mensagem simples novamente
    print(f"\n3️⃣ Enviando nova mensagem de teste...")
    
    current_time = int(time.time())
    
    simple_message = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {
            "body": f"🧪 TESTE CRÍTICO {current_time}\n\nSe você está vendo esta mensagem, o sistema BM Jose Carlos está funcionando!\n\nDetalhes:\n- Phone: +1 979-867-2216\n- Quality: GREEN\n- BM: 639849885789886\n- Timestamp: {current_time}"
        }
    }
    
    send_response = requests.post(
        f"{base_url}/{phone_id}/messages",
        headers=headers,
        json=simple_message,
        timeout=15
    )
    
    print(f"Status: {send_response.status_code}")
    print(f"Response: {send_response.text}")
    
    if send_response.status_code == 200:
        response_data = send_response.json()
        message_id = response_data.get('messages', [{}])[0].get('id')
        wa_id = response_data.get('contacts', [{}])[0].get('wa_id')
        
        print(f"✅ Message ID: {message_id}")
        print(f"✅ WhatsApp ID: {wa_id}")
        
        # 4. Tentar segundo phone number da BM
        print(f"\n4️⃣ Testando com segundo phone number...")
        
        second_phone_id = "696547163548546"  # Segundo número da BM
        
        second_message = {
            "messaging_product": "whatsapp",
            "to": user_number,
            "type": "text",
            "text": {
                "body": f"🔄 TESTE PHONE 2 - {current_time}\n\nTeste com segundo número da BM Jose Carlos\n\nPhone: +1 260-256-3215\nPhone ID: {second_phone_id}"
            }
        }
        
        second_response = requests.post(
            f"{base_url}/{second_phone_id}/messages",
            headers=headers,
            json=second_message,
            timeout=15
        )
        
        print(f"Second Phone Status: {second_response.status_code}")
        print(f"Second Phone Response: {second_response.text}")
        
        if second_response.status_code == 200:
            second_data = second_response.json()
            second_message_id = second_data.get('messages', [{}])[0].get('id')
            print(f"✅ Second Message ID: {second_message_id}")
        
        # 5. Verificar possíveis limitações
        print(f"\n5️⃣ Possíveis causas da não entrega:")
        print("1. ⚠️  Número bloqueou mensagens comerciais do WhatsApp Business")
        print("2. ⚠️  Configuração de privacidade do WhatsApp do destinatário")
        print("3. ⚠️  Conta WhatsApp Business em período de 'shadow ban'")
        print("4. ⚠️  Rate limiting silencioso da Meta/Facebook")
        print("5. ⚠️  Número não está ativo no WhatsApp")
        print("6. ⚠️  Conta precisa de verificação adicional")
        
        return True
    else:
        print(f"❌ Falhou: {send_response.status_code}")
        return False

if __name__ == "__main__":
    debug_user_number()