#!/usr/bin/env python3
"""
Criar template neutro e aprovável para WhatsApp Business API
Template simples e profissional para aprovação rápida
"""

import requests
import json
import os

def create_neutral_template():
    """Criar template neutro e profissional"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'  # BM atual
    
    if not access_token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Template neutro e aprovável
    template_data = {
        "name": "notificacao_simples",
        "language": "pt_BR",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Olá {{1}}, esta é uma notificação importante. Documento: {{2}}. Para mais informações, entre em contato conosco."
            },
            {
                "type": "FOOTER",
                "text": "Cartório 5º Ofício de Notas"
            }
        ]
    }
    
    print(f"Criando template neutro 'notificacao_simples'...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(template_data, indent=2)}")
    
    try:
        response = requests.post(url, json=template_data, headers=headers)
        
        print(f"\nStatus: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code in [200, 201]:
            template_id = result.get('id', 'N/A')
            print(f"\n✅ TEMPLATE CRIADO COM SUCESSO!")
            print(f"Template ID: {template_id}")
            print(f"Nome: notificacao_simples")
            print(f"Status: Enviado para aprovação")
            print(f"Categoria: UTILITY (aprovação mais rápida)")
            print(f"Idioma: pt_BR")
            
            return template_id
        else:
            print(f"\n❌ ERRO AO CRIAR TEMPLATE")
            error_msg = result.get('error', {}).get('message', 'Erro desconhecido')
            print(f"Erro: {error_msg}")
            
    except Exception as e:
        print(f"ERRO: {e}")
    
    return None

def create_simple_english_template():
    """Criar template simples em inglês (aprovação mais rápida)"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    if not access_token:
        return None
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Template em inglês - aprovação mais rápida
    template_data = {
        "name": "simple_notification",
        "language": "en",
        "category": "UTILITY", 
        "components": [
            {
                "type": "BODY",
                "text": "Hello {{1}}, this is an important notification regarding document {{2}}. Please contact us for more information."
            },
            {
                "type": "FOOTER",
                "text": "5th Notary Office"
            }
        ]
    }
    
    print(f"\nCriando template em inglês 'simple_notification'...")
    
    try:
        response = requests.post(url, json=template_data, headers=headers)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code in [200, 201]:
            template_id = result.get('id', 'N/A')
            print(f"\n✅ TEMPLATE EM INGLÊS CRIADO!")
            print(f"Template ID: {template_id}")
            return template_id
            
    except Exception as e:
        print(f"ERRO: {e}")
    
    return None

if __name__ == "__main__":
    print("=== CRIAÇÃO DE TEMPLATES NEUTROS ===\n")
    
    # Criar template em português
    pt_template = create_neutral_template()
    
    # Criar template em inglês  
    en_template = create_simple_english_template()
    
    print(f"\n=== RESUMO ===")
    print(f"Template PT-BR: {'✅ Criado' if pt_template else '❌ Falhou'}")
    print(f"Template EN: {'✅ Criado' if en_template else '❌ Falhou'}")
    print(f"\nAguarde aprovação do WhatsApp (24-48h para templates UTILITY)")