#!/usr/bin/env python3
"""
Criar template totalmente neutro e "white" para aprovação rápida
Sem referências específicas, apenas genérico e aprovável
"""

import requests
import json
import os
import time

def create_white_template():
    """Criar template totalmente neutro"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    if not access_token:
        print("ERROR: Token não encontrado")
        return None
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Template super neutro e aprovável
    templates = [
        {
            "name": "aviso_geral",
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Olá {{1}}, temos uma informação importante para você sobre {{2}}. Entre em contato para mais detalhes."
                }
            ]
        },
        {
            "name": "info_update",
            "language": "en",
            "category": "UTILITY", 
            "components": [
                {
                    "type": "BODY",
                    "text": "Hello {{1}}, we have an important update for you regarding {{2}}. Please contact us for more details."
                }
            ]
        },
        {
            "name": "notificacao_geral",
            "language": "pt_BR",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Prezado {{1}}, informamos que há uma atualização disponível sobre {{2}}. Agradecemos sua atenção."
                }
            ]
        }
    ]
    
    created_templates = []
    
    for template in templates:
        print(f"Criando template '{template['name']}'...")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=15)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                print(f"✅ Template '{template['name']}' criado! ID: {template_id}")
                created_templates.append({
                    'name': template['name'],
                    'id': template_id,
                    'language': template['language']
                })
            else:
                error_msg = result.get('error', {}).get('message', 'Erro desconhecido')
                print(f"❌ Falhou: {error_msg}")
            
            # Pausa entre criações
            time.sleep(2)
            
        except Exception as e:
            print(f"ERRO: {e}")
    
    return created_templates

if __name__ == "__main__":
    print("=== CRIANDO TEMPLATES NEUTROS ===\n")
    
    templates = create_white_template()
    
    print(f"\n=== RESUMO ===")
    if templates:
        print(f"Templates criados: {len(templates)}")
        for t in templates:
            print(f"- {t['name']} ({t['language']}) - ID: {t['id']}")
        print(f"\n✅ Aguarde aprovação do WhatsApp (24-48h)")
    else:
        print("❌ Nenhum template foi criado")