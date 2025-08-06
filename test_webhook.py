#!/usr/bin/env python3
"""
Testar webhook do WhatsApp Business API
"""
import requests
import json

def test_webhook():
    """Testa o endpoint de webhook"""
    base_url = "http://localhost:5000"
    
    # 1. Testar verificação do webhook (GET)
    print("🔍 TESTANDO VERIFICAÇÃO DO WEBHOOK")
    print("=" * 40)
    
    verify_params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'webhook_verify_token_12345',
        'hub.challenge': 'test_challenge_123'
    }
    
    response = requests.get(f"{base_url}/webhook", params=verify_params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 2. Testar webhook de clique em botão (POST)
    print("\n📱 TESTANDO WEBHOOK DE CLIQUE EM BOTÃO")
    print("=" * 40)
    
    # Exemplo de webhook real do WhatsApp quando usuário clica em botão
    button_webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1289588222582398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15558060539",
                                "phone_number_id": "687372631129372"
                            },
                            "messages": [
                                {
                                    "from": "5561982132603",
                                    "id": "wamid.HBgMNTU2MTgyMTMyNjAzFQIAERgSQUYxMzY0MjNGQkIzNkQwOTE0AA==",
                                    "timestamp": "1721064123",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "verify_button",
                                            "title": "Verificar Situação"
                                        }
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    response = requests.post(f"{base_url}/webhook", json=button_webhook_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 3. Testar webhook de status de mensagem
    print("\n📊 TESTANDO WEBHOOK DE STATUS DE MENSAGEM")
    print("=" * 40)
    
    status_webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1289588222582398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15558060539",
                                "phone_number_id": "687372631129372"
                            },
                            "statuses": [
                                {
                                    "id": "wamid.HBgMNTU2MTgyMTMyNjAzFQIAERgSQUYxMzY0MjNGQkIzNkQwOTE0AA==",
                                    "status": "delivered",
                                    "timestamp": "1721064150",
                                    "recipient_id": "5561982132603"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    response = requests.post(f"{base_url}/webhook", json=status_webhook_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 4. Testar endpoint de consulta de interações
    print("\n🔍 TESTANDO CONSULTA DE INTERAÇÕES")
    print("=" * 40)
    
    response = requests.get(f"{base_url}/api/button-interactions")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_webhook()