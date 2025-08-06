#!/usr/bin/env python3
"""
Teste direto com estrutura simplificada
"""

import requests
import os
import time

def test_simple_approval():
    """Teste com estrutura mais simples possível"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # Testar diferentes versões da API
    test_configs = [
        {
            'version': 'v23.0',
            'bm_id': '746006914691827'
        },
        {
            'version': 'v20.0', 
            'bm_id': '746006914691827'
        },
        {
            'version': 'v19.0',
            'bm_id': '746006914691827'
        }
    ]
    
    timestamp = str(int(time.time()))
    
    for config in test_configs:
        url = f"https://graph.facebook.com/{config['version']}/{config['bm_id']}/message_templates"
        
        template = {
            "name": f"test_{config['version'].replace('.', '')}_{timestamp}",
            "language": "pt_BR",
            "category": "AUTHENTICATION",
            "components": [
                {
                    "type": "BODY",
                    "text": "Código {{1}}"
                }
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"\nTestando {config['version']}...")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=10)
            result = response.json()
            
            if response.status_code in [200, 201]:
                status = result.get('status', 'UNKNOWN')
                template_id = result.get('id', 'N/A')
                
                print(f"✅ SUCESSO: {template['name']}")
                print(f"   Status: {status}")
                print(f"   ID: {template_id}")
                
                if status == 'APPROVED':
                    print(f"🎉 APROVADO IMEDIATAMENTE!")
                    return template['name'], template_id
                elif status == 'PENDING':
                    print(f"⏳ EM ANÁLISE")
                
            else:
                error = result.get('error', {})
                print(f"❌ Falhou: {error.get('message', 'Erro')}")
                
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(1)
    
    return None, None

if __name__ == "__main__":
    name, template_id = test_simple_approval()
    
    if template_id:
        print(f"\n✅ Template criado: {name} (ID: {template_id})")
    else:
        print(f"\n❌ Nenhum template foi aprovado")