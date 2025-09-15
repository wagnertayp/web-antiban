#!/usr/bin/env python3
"""
Script para criar um template WhatsApp Business API funcional
"""

import requests
import json
import os

def create_template():
    """Cria um template simples que funciona"""
    
    # Configurações
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    business_account_id = "SEU_BUSINESS_ACCOUNT_ID"  # Precisa ser fornecido
    
    if not access_token:
        print("❌ Token de acesso não encontrado")
        return
    
    # Template simples e funcional
    template_data = {
        "name": "cartorio_notificacao",
        "language": "pt_BR",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Olá {{1}}, me chamo Sayonara Palloma e sou tabeliã do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF {{2}}."
            }
        ]
    }
    
    url = f"https://graph.facebook.com/v23.0/{business_account_id}/message_templates"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=template_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Template criado com sucesso! ID: {result.get('id')}")
        print("📋 Aguarde aprovação do Meta (pode levar até 24h)")
    else:
        print(f"❌ Erro ao criar template: {response.status_code}")
        print(f"📄 Resposta: {response.text}")

if __name__ == "__main__":
    create_template()