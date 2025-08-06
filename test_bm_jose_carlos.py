#!/usr/bin/env python3
"""
Teste da BM Jose Carlos - ID: 639849885789886
"""

import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_bm_jose_carlos():
    """Teste direto da BM Jose Carlos"""
    
    # Token da BM Jose Carlos
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    print(f"✅ Token carregado: {access_token[:20]}...")
    
    # BM Jose Carlos - ID fornecido
    business_account_id = "639849885789886"
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 1. Descobrir Phone Numbers da BM Jose Carlos
    print(f"\n🔍 Descobrindo phone numbers da BM {business_account_id}...")
    
    phones_response = requests.get(
        f"{base_url}/{business_account_id}/phone_numbers",
        headers=headers,
        timeout=10
    )
    
    print(f"📊 Status phone numbers: {phones_response.status_code}")
    print(f"📊 Response: {phones_response.text}")
    
    if phones_response.status_code != 200:
        print(f"❌ Erro ao buscar phones: {phones_response.status_code}")
        return
    
    phones_data = phones_response.json()
    phone_numbers = phones_data.get('data', [])
    
    print(f"✅ Encontrados {len(phone_numbers)} phone numbers:")
    for phone in phone_numbers:
        print(f"   📱 {phone.get('id')} - {phone.get('display_phone_number', 'N/A')} - {phone.get('quality_rating', 'UNKNOWN')}")
    
    if not phone_numbers:
        print("❌ Nenhum phone number encontrado na BM Jose Carlos")
        return
    
    # Usar o primeiro phone number
    phone_id = phone_numbers[0]['id']
    print(f"\n📱 Usando Phone ID: {phone_id}")
    
    # 2. Descobrir templates da BM Jose Carlos
    print(f"\n🔍 Descobrindo templates da BM {business_account_id}...")
    
    templates_response = requests.get(
        f"{base_url}/{business_account_id}/message_templates",
        headers=headers,
        timeout=10
    )
    
    print(f"📊 Status templates: {templates_response.status_code}")
    print(f"📊 Response: {templates_response.text}")
    
    if templates_response.status_code != 200:
        print(f"❌ Erro ao buscar templates: {templates_response.status_code}")
        return
    
    templates_data = templates_response.json()
    templates = templates_data.get('data', [])
    
    # Filtrar apenas templates aprovados
    approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
    
    print(f"✅ Encontrados {len(approved_templates)} templates aprovados:")
    for template in approved_templates:
        print(f"   📋 {template.get('name')} - {template.get('language')} - {template.get('category')}")
    
    if not approved_templates:
        print("❌ Nenhum template aprovado encontrado na BM Jose Carlos")
        return
    
    # Usar o primeiro template aprovado
    template_name = approved_templates[0]['name']
    template_language = approved_templates[0]['language']
    print(f"\n📋 Usando template: {template_name} ({template_language})")
    
    # 3. Enviar mensagem de teste
    target_number = "+5561999114066"
    cpf = "065.370.801-77"
    nome = "Pedro"
    
    print(f"\n📤 Enviando template para {target_number}...")
    
    message_payload = {
        "messaging_product": "whatsapp",
        "to": target_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": template_language},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": cpf},
                        {"type": "text", "text": nome}
                    ]
                }
            ]
        }
    }
    
    # Verificar se template tem botão
    template_components = approved_templates[0].get('components', [])
    has_button = any(comp.get('type') == 'BUTTONS' for comp in template_components)
    
    if has_button:
        print("🔘 Template tem botão - adicionando parâmetro URL")
        message_payload["template"]["components"].append({
            "type": "button",
            "sub_type": "url",
            "index": 0,
            "parameters": [{"type": "text", "text": cpf}]
        })
    
    print(f"📝 Payload: {message_payload}")
    
    # Enviar mensagem
    send_response = requests.post(
        f"{base_url}/{phone_id}/messages",
        headers=headers,
        json=message_payload,
        timeout=15
    )
    
    print(f"\n📊 Status: {send_response.status_code}")
    print(f"📊 Response: {send_response.text}")
    
    if send_response.status_code == 200:
        response_data = send_response.json()
        message_id = response_data.get('messages', [{}])[0].get('id')
        print(f"✅ SUCESSO! Message ID: {message_id}")
        return True
    else:
        print(f"❌ ERRO: {send_response.status_code} - {send_response.text}")
        return False

if __name__ == "__main__":
    success = test_bm_jose_carlos()
    if success:
        print("\n🎉 BM JOSE CARLOS FUNCIONANDO 100%!")
    else:
        print("\n❌ BM Jose Carlos apresenta problemas")