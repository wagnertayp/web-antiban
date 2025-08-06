#!/usr/bin/env python3
"""
Testar padrões de templates baseados nos que funcionaram
"""

import requests
import os
import time

def test_working_patterns():
    """Testar padrões baseados em templates que funcionaram antes"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Baseado no padrão do hello_world_br que ficou PENDING
    test_patterns = [
        {
            "name": "ola_brasil",
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Olá Brasil!"
                }
            ]
        },
        {
            "name": "teste_simples",
            "language": "pt_BR", 
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Teste simples."
                }
            ]
        },
        {
            "name": "hello_test",
            "language": "en",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Hello test."
                }
            ]
        },
        # Tentar com AUTHENTICATION que tem aprovação mais rápida
        {
            "name": "codigo_verificacao",
            "language": "pt_BR",
            "category": "AUTHENTICATION",
            "components": [
                {
                    "type": "BODY",
                    "text": "Seu código de verificação é: {{1}}"
                }
            ]
        },
        {
            "name": "verification_code",
            "language": "en",
            "category": "AUTHENTICATION", 
            "components": [
                {
                    "type": "BODY",
                    "text": "Your verification code is: {{1}}"
                }
            ]
        }
    ]
    
    results = []
    
    for template in test_patterns:
        print(f"\nTestando padrão: {template['name']} ({template['category']})")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=10)
            result = response.json()
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                status = result.get('status', 'UNKNOWN')
                category = result.get('category', 'UNKNOWN')
                
                print(f"✅ CRIADO: {template['name']}")
                print(f"   ID: {template_id}")
                print(f"   Status: {status}")
                print(f"   Categoria: {category}")
                
                results.append({
                    'name': template['name'],
                    'id': template_id,
                    'status': status,
                    'category': category,
                    'original_category': template['category']
                })
                
                if status == 'APPROVED':
                    print(f"🎉 APROVADO INSTANTANEAMENTE: {template['name']}")
                elif status == 'PENDING':
                    print(f"⏳ EM ANÁLISE: {template['name']}")
                    
            else:
                error = result.get('error', {})
                print(f"❌ REJEITADO: {error.get('message', 'Erro desconhecido')}")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"ERRO: {e}")
    
    return results

if __name__ == "__main__":
    print("=== TESTE DE PADRÕES QUE FUNCIONAM ===\n")
    
    results = test_working_patterns()
    
    print(f"\n=== RESULTADOS ===")
    
    approved = [r for r in results if r['status'] == 'APPROVED']
    pending = [r for r in results if r['status'] == 'PENDING']
    
    if approved:
        print(f"✅ APROVADOS INSTANTANEAMENTE ({len(approved)}):")
        for t in approved:
            print(f"- {t['name']} (Categoria: {t['category']})")
    
    if pending:
        print(f"⏳ EM ANÁLISE ({len(pending)}):")
        for t in pending:
            print(f"- {t['name']} (Categoria: {t['category']})")
    
    if not results:
        print("❌ Nenhum template foi aceito")
    else:
        print(f"\n💡 Total processados: {len(results)}")
        print("📝 Aguarde alguns minutos para verificar status de aprovação")