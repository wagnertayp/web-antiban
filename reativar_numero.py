#!/usr/bin/env python3
"""
Script para reativar número 15558075193 na Cloud API
Token: EAAKouL3CWmcBPK8jUQByoCxzuCKUrOx4PP9dPTDLJcz9kVrxjAmbqNwE5gD3A0Yx4CZCQJFxDcICbfZAtoUdMrtx7FXrDQGkIwF1TcLbBZCaZA3EXAkjc8PKkAWoKUoxuZCS3a4DhSdvE7sjMXZBRiSetsc6MPOYnn6CHdUAJwDogV6SxkHjh6pgKRZCrPt6MH9N7o9ZA8fw3kNxpyvSDTPD0OUEaasRHtWYYGfAiWbH3wZDZD
BM: 639427228458196
Phone ID: 648564628349132
"""

import requests
import json

TOKEN = "EAAKouL3CWmcBPK8jUQByoCxzuCKUrOx4PP9dPTDLJcz9kVrxjAmbqNwE5gD3A0Yx4CZCQJFxDcICbfZAtoUdMrtx7FXrDQGkIwF1TcLbBZCaZA3EXAkjc8PKkAWoKUoxuZCS3a4DhSdvE7sjMXZBRiSetsc6MPOYnn6CHdUAJwDogV6SxkHjh6pgKRZCrPt6MH9N7o9ZA8fw3kNxpyvSDTPD0OUEaasRHtWYYGfAiWbH3wZDZD"
BUSINESS_ACCOUNT_ID = "639427228458196"
PHONE_ID = "648564628349132"

def solicitar_sms():
    """Solicita código SMS para o número"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/request_code"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "code_method": "SMS",
        "language": "pt_BR"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Solicitação SMS: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def verificar_sms(codigo):
    """Verifica o código SMS recebido"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/verify_code"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "code": codigo
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Verificação SMS: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def registrar_numero(pin):
    """Registra o número na Cloud API com PIN"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/register"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "pin": pin
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Registro Cloud API: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def verificar_status():
    """Verifica status atual do número"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}"
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status do número: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def testar_envio():
    """Testa envio de mensagem"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": "556182132603",
        "type": "text",
        "text": {
            "body": "✅ TESTE: Número 15558075193 reativado com sucesso!"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Teste de envio: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    print("=== REATIVAÇÃO NÚMERO 15558075193 ===")
    print(f"Phone ID: {PHONE_ID}")
    print(f"Business Account: {BUSINESS_ACCOUNT_ID}")
    print()
    
    # 1. Verificar status atual
    print("1. Verificando status atual...")
    verificar_status()
    print()
    
    # 2. Tentar registro direto (pode falhar se precisar PIN)
    print("2. Tentando registro direto...")
    try:
        registrar_numero("")
    except:
        pass
    print()
    
    # 3. Solicitar SMS se necessário
    print("3. Solicitando SMS...")
    resultado_sms = solicitar_sms()
    print()
    
    if "error" not in resultado_sms:
        codigo = input("Digite o código SMS recebido: ")
        print("4. Verificando código SMS...")
        verificar_sms(codigo)
        print()
        
        pin = input("Digite o PIN recebido no SMS (se houver): ")
        if pin:
            print("5. Registrando na Cloud API...")
            registrar_numero(pin)
            print()
    
    # 6. Teste final
    print("6. Testando envio de mensagem...")
    testar_envio()
    print()
    
    print("=== PROCESSO CONCLUÍDO ===")