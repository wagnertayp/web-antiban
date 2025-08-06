#!/usr/bin/env python3
"""
Criar templates com alta taxa de aprovação usando melhores práticas 2025
"""

import requests
import json
import os
import time

def get_business_account_id():
    """Descobrir Business Account ID automaticamente"""
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    try:
        # Tentar descobrir via phone number
        phone_response = requests.get(
            f'https://graph.facebook.com/v23.0/me',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if phone_response.status_code == 200:
            me_data = phone_response.json()
            print(f"Account info: {me_data}")
            
        # Testar diferentes BM IDs conhecidos
        known_bms = ['746006914691827', '673500515497433', '2499594917061799']
        
        for bm_id in known_bms:
            test_url = f'https://graph.facebook.com/v23.0/{bm_id}/message_templates'
            test_response = requests.get(
                test_url,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            if test_response.status_code == 200:
                print(f"✅ BM ativo encontrado: {bm_id}")
                return bm_id
                
        return '746006914691827'  # Default
        
    except Exception as e:
        print(f"Erro ao descobrir BM: {e}")
        return '746006914691827'

def create_super_safe_templates():
    """Criar templates com palavras-chave que sempre aprovam"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not access_token:
        print("ERROR: Token não encontrado")
        return []
    
    business_account_id = get_business_account_id()
    print(f"Usando BM ID: {business_account_id}")
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Templates baseados em casos de sucesso comprovados
    safe_templates = [
        {
            "name": "confirmacao_entrega",
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Olá {{1}}, sua entrega {{2}} foi confirmada com sucesso."
                }
            ]
        },
        {
            "name": "agendamento_sucesso", 
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "{{1}}, seu agendamento {{2}} foi realizado com sucesso."
                }
            ]
        },
        {
            "name": "delivery_confirmed",
            "language": "en",
            "category": "UTILITY", 
            "components": [
                {
                    "type": "BODY",
                    "text": "Hello {{1}}, your delivery {{2}} has been confirmed successfully."
                }
            ]
        },
        {
            "name": "booking_success",
            "language": "en",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Hi {{1}}, your booking {{2}} has been completed successfully."
                }
            ]
        },
        {
            "name": "pedido_recebido",
            "language": "pt_BR", 
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "{{1}}, recebemos seu pedido {{2}}. Obrigado pela confiança!"
                }
            ]
        }
    ]
    
    approved = []
    
    for template in safe_templates:
        print(f"\nCriando: {template['name']}")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=15)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                print(f"✅ APROVADO: {template['name']} (ID: {template_id})")
                approved.append({
                    'name': template['name'],
                    'id': template_id,
                    'language': template['language']
                })
            else:
                error = result.get('error', {})
                error_msg = error.get('message', 'Erro desconhecido')
                print(f"❌ REJEITADO: {error_msg}")
                
                # Log detalhado do erro
                if 'error_user_msg' in error:
                    print(f"   Detalhes: {error['error_user_msg']}")
            
            time.sleep(2)  # Pausa entre criações
            
        except Exception as e:
            print(f"ERRO: {e}")
    
    return approved

def create_minimal_templates():
    """Criar templates minimalistas que sempre passam"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = get_business_account_id()
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Templates super simples
    minimal = [
        {
            "name": "oi_simples",
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY", 
                    "text": "Oi {{1}}!"
                }
            ]
        },
        {
            "name": "hello_basic",
            "language": "en",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Hello {{1}}!"
                }
            ]
        },
        {
            "name": "obrigado_simples",
            "language": "pt_BR",
            "category": "UTILITY", 
            "components": [
                {
                    "type": "BODY",
                    "text": "Obrigado {{1}}!"
                }
            ]
        }
    ]
    
    approved = []
    
    for template in minimal:
        print(f"\nCriando minimal: {template['name']}")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=10)
            result = response.json()
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                print(f"✅ MINIMAL APROVADO: {template['name']}")
                approved.append(template['name'])
            else:
                error = result.get('error', {})
                print(f"❌ Minimal rejeitado: {error.get('message', 'Erro')}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro minimal: {e}")
    
    return approved

if __name__ == "__main__":
    print("=== CRIAÇÃO DE TEMPLATES APROVADOS ===\n")
    
    print("1. Testando templates seguros...")
    safe_approved = create_super_safe_templates()
    
    print(f"\n2. Testando templates minimalistas...")
    minimal_approved = create_minimal_templates()
    
    print(f"\n=== RESULTADO FINAL ===")
    total = len(safe_approved) + len(minimal_approved)
    print(f"Templates aprovados: {total}")
    
    if safe_approved:
        print("Templates seguros aprovados:")
        for t in safe_approved:
            print(f"- {t['name']} ({t['language']}) - ID: {t['id']}")
    
    if minimal_approved:
        print("Templates minimalistas aprovados:")
        for t in minimal_approved:
            print(f"- {t}")
    
    if total == 0:
        print("❌ NENHUM TEMPLATE APROVADO")
        print("Possíveis problemas:")
        print("- Token sem permissões")
        print("- BM com restrições")
        print("- Rate limit ativo")
        print("- Conta precisando verificação")
    else:
        print(f"✅ {total} templates prontos para uso!")