#!/usr/bin/env python3
"""
Debug específico do status das mensagens enviadas
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

def check_message_delivery():
    """Verifica o status de entrega das mensagens"""
    
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    business_account_id = "639849885789886"
    phone_id = "743171782208180"  # Phone com Quality GREEN
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 TESTANDO ENTREGA DE MENSAGEM ESPECÍFICA...")
    
    # 1. Enviar mensagem de teste para número real
    test_number = "+5561999114066"  # Número conhecido
    
    message_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "text",
        "text": {
            "body": "🧪 TESTE ENTREGA - Jose Carlos BM\n\nMensagem de teste enviada em " + str(int(time.time())) + "\n\nSe você recebeu esta mensagem, o sistema está funcionando!"
        }
    }
    
    print(f"📤 Enviando para {test_number} via phone {phone_id}...")
    
    send_response = requests.post(
        f"{base_url}/{phone_id}/messages",
        headers=headers,
        json=message_payload,
        timeout=15
    )
    
    print(f"Status: {send_response.status_code}")
    print(f"Response: {send_response.text}")
    
    if send_response.status_code != 200:
        print("❌ Erro no envio!")
        return False
    
    response_data = send_response.json()
    message_id = response_data.get('messages', [{}])[0].get('id')
    wa_id = response_data.get('contacts', [{}])[0].get('wa_id')
    
    print(f"✅ Message ID: {message_id}")
    print(f"📱 WhatsApp ID: {wa_id}")
    
    # 2. Aguardar e verificar webhooks (se configurado)
    print("\n⏳ Aguardando 10 segundos para entrega...")
    time.sleep(10)
    
    # 3. Tentar diferentes tipos de mensagem
    print("\n📋 Testando template aprovado...")
    
    template_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo3",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"},
                        {"type": "text", "text": "Pedro Teste"}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [{"type": "text", "text": "065.370.801-77"}]
                }
            ]
        }
    }
    
    template_response = requests.post(
        f"{base_url}/{phone_id}/messages",
        headers=headers,
        json=template_payload,
        timeout=15
    )
    
    print(f"Template Status: {template_response.status_code}")
    print(f"Template Response: {template_response.text}")
    
    if template_response.status_code == 200:
        template_data = template_response.json()
        template_message_id = template_data.get('messages', [{}])[0].get('id')
        print(f"✅ Template Message ID: {template_message_id}")
    
    # 4. Verificar se número está bloqueado ou tem restrições
    print("\n🔍 Verificando informações do destinatário...")
    
    # Esta chamada pode não estar disponível, mas vamos tentar
    try:
        contact_info = requests.get(
            f"{base_url}/{phone_id}/contacts/{wa_id}",
            headers=headers,
            timeout=10
        )
        
        print(f"Contact Info Status: {contact_info.status_code}")
        if contact_info.status_code == 200:
            print(f"Contact Info: {contact_info.text}")
    except Exception as e:
        print(f"❌ Não foi possível obter info do contato: {e}")
    
    # 5. Verificar limites de mensagens
    print("\n📊 Verificando limites de mensagens...")
    
    try:
        limits_response = requests.get(
            f"{base_url}/{business_account_id}?fields=messaging_limit_tier",
            headers=headers,
            timeout=10
        )
        
        print(f"Limits Status: {limits_response.status_code}")
        if limits_response.status_code == 200:
            print(f"Limits: {limits_response.text}")
    except Exception as e:
        print(f"❌ Erro ao verificar limites: {e}")
    
    print("\n💡 POSSÍVEIS CAUSAS:")
    print("1. Número de destino bloqueou mensagens comerciais")
    print("2. Conta WhatsApp Business precisa ser verificada pelo Meta")
    print("3. Templates precisam de aprovação adicional")
    print("4. Número de destino não está no WhatsApp")
    print("5. Conta em período de revisão silenciosa")
    
    return True

if __name__ == "__main__":
    check_message_delivery()