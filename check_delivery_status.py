#!/usr/bin/env python3
import requests
import time

def check_delivery_status():
    """Verificar status de entrega das mensagens"""
    
    token = 'EAAYLvZBaHbvYBPKCwMnvhXM2kPkWMUlyhVqjtgplZAGrZCRtxZAvH6lZCfP9voDg6UByPd7q6ZBx76kRGMoFsnhBiP7ScXOYD5LqRRppEjc71PRapP1S5oAJCPsoXn9kkPlUMURv53nG0V2wZC5iXZAiZAfSfTGvqsX2NzENeoKDVoura97AZAOxsDd21f97RJJcQSUxfnZBB9x1UkfbUnAU0hLo9N3rZAOwJS4UGLWQwjRVsB0ZD'
    phone_id = "674928665709899"
    business_id = "746006914691827"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 1. Verificar configurações da conta
    print("=== 1. Business Account Settings ===")
    business_url = f"https://graph.facebook.com/v23.0/{business_id}?fields=name,message_template_namespace,currency,timezone_id"
    response = requests.get(business_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 2. Verificar qualidade do número
    print("\n=== 2. Phone Number Quality ===")
    phone_url = f"https://graph.facebook.com/v23.0/{phone_id}?fields=verified_name,display_phone_number,quality_rating,messaging_limit,throughput"
    response = requests.get(phone_url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 3. Testar envio simples para verificar se é problema de conteúdo
    print("\n=== 3. Teste com mensagem simples ===")
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    simple_payload = {
        'messaging_product': 'whatsapp',
        'to': '5561982132603',
        'type': 'text',
        'text': {
            'body': 'Olá, esta é uma mensagem de teste simples.'
        }
    }
    
    response = requests.post(url, json=simple_payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        message_id = data.get('messages', [{}])[0].get('id', '')
        print(f"Message ID: {message_id}")
        
        # Aguardar e verificar status
        print("\nAguardando 10 segundos para verificar status...")
        time.sleep(10)
        
        # Verificar webhooks (se configurados)
        print("\n=== 4. Verificar Webhooks (se disponível) ===")
        webhook_url = f"https://graph.facebook.com/v23.0/{business_id}/subscribed_apps"
        response = requests.get(webhook_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    check_delivery_status()
