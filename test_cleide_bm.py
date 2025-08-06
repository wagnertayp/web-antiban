#!/usr/bin/env python3
"""
Script para testar BM Cleide com token fornecido
"""

import os
import requests
import json
from datetime import datetime

# Token e configurações fornecidas
TEST_TOKEN = "EAAJc6cZAxck4BPAiugr1YWJJmRcNuutBiwONUTwk7qGsftXclDhs3SXzFax2RtiutG0Kx2Jrid6uZB0wCZCsFmGpH9Ee6zKoSp0ywRR0sRYyi1kiG1PZCLoW8JDIc65SDmW4yRZAtD5DDrgbPpYxNixPnMVfbZBTwgoGg6BIjT7vQW483xcDtbCZBzcy3ne6qZC89WzQvdZBDjmAltYv3hMfI82p3M5bGLVh49INMIBPEv2JBMwZDZD"
BUSINESS_ACCOUNT_ID = "580318035149016"
BASE_URL = "https://graph.facebook.com/v22.0"

# Template e dados para teste
TEMPLATE_NAME = "cleide_template_1752692476_0f370e02"
TEST_PHONE = "5561982132603"
TEST_CPF = "061.982.132-60"
TEST_NOME = "Teste Cleide"

def discover_phone_numbers():
    """Descobre os phone numbers ativos na BM"""
    print(f"🔍 DESCOBRINDO PHONE NUMBERS DA BM {BUSINESS_ACCOUNT_ID}")
    
    headers = {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Buscar phone numbers
    url = f"{BASE_URL}/{BUSINESS_ACCOUNT_ID}/phone_numbers"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            phone_numbers = data.get('data', [])
            
            print(f"   ✅ Encontrados {len(phone_numbers)} phone numbers:")
            active_phones = []
            
            for phone in phone_numbers:
                phone_id = phone.get('id', 'N/A')
                display_name = phone.get('display_phone_number', 'N/A')
                verified = phone.get('verified_name', 'N/A')
                quality = phone.get('quality_rating', 'N/A')
                
                print(f"      📱 ID: {phone_id}")
                print(f"         Número: {display_name}")
                print(f"         Nome: {verified}")
                print(f"         Quality: {quality}")
                print()
                
                active_phones.append({
                    'id': phone_id,
                    'number': display_name,
                    'name': verified,
                    'quality': quality
                })
            
            return active_phones
            
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {str(e)}")
        return []

def get_template_structure():
    """Busca a estrutura do template específico"""
    print(f"🔍 BUSCANDO TEMPLATE {TEMPLATE_NAME}")
    
    headers = {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{BUSINESS_ACCOUNT_ID}/message_templates"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            for template in templates:
                if template.get('name') == TEMPLATE_NAME:
                    print(f"   ✅ Template encontrado:")
                    print(f"      Status: {template.get('status', 'N/A')}")
                    print(f"      Idioma: {template.get('language', 'N/A')}")
                    print(f"      Categoria: {template.get('category', 'N/A')}")
                    
                    components = template.get('components', [])
                    print(f"      Componentes: {len(components)}")
                    
                    for comp in components:
                        comp_type = comp.get('type', 'N/A')
                        print(f"         - {comp_type}")
                    
                    return template
            
            print(f"   ❌ Template {TEMPLATE_NAME} não encontrado")
            print(f"   📋 Templates disponíveis:")
            for template in templates:
                name = template.get('name', 'N/A')
                status = template.get('status', 'N/A')
                print(f"      - {name} ({status})")
            
            return None
            
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {str(e)}")
        return None

def send_template_message(phone_id, phone_name):
    """Envia mensagem usando o template"""
    print(f"🚀 ENVIANDO TEMPLATE de {phone_name} (ID: {phone_id})")
    
    headers = {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{phone_id}/messages"
    
    # Payload do template cleide
    payload = {
        "messaging_product": "whatsapp",
        "to": TEST_PHONE,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": TEST_CPF},
                        {"type": "text", "text": TEST_NOME}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {"type": "text", "text": TEST_CPF}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   ✅ SUCESSO! Message ID: {message_id}")
            return True, message_id
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            
            # Verificar se é erro #135000
            if "135000" in response.text:
                print(f"   🔥 ERRO #135000 DETECTADO - BM com incompatibilidade de templates")
            
            return False, None
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {str(e)}")
        return False, None

def main():
    """Função principal"""
    print("=" * 80)
    print("🔥 TESTE BM CLEIDE - TOKEN FORNECIDO")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏢 Business Manager: {BUSINESS_ACCOUNT_ID}")
    print(f"📋 Template: {TEMPLATE_NAME}")
    print(f"📱 Número destino: {TEST_PHONE}")
    print("=" * 80)
    
    # 1. Descobrir phone numbers
    phones = discover_phone_numbers()
    
    if not phones:
        print("❌ FALHA: Não foi possível descobrir phone numbers")
        return
    
    print("=" * 80)
    
    # 2. Verificar template
    template = get_template_structure()
    
    if not template:
        print("❌ FALHA: Template não encontrado ou inacessível")
        return
    
    print("=" * 80)
    
    # 3. Testar envio com primeiro phone ativo
    if phones:
        first_phone = phones[0]
        success, message_id = send_template_message(first_phone['id'], first_phone['name'])
        
        if success:
            print(f"\n🎉 TEMPLATE ENVIADO COM SUCESSO!")
            print(f"📞 Phone: {first_phone['name']}")
            print(f"📨 Message ID: {message_id}")
        else:
            print(f"\n💥 FALHA NO ENVIO DO TEMPLATE")
            print(f"🔄 BM pode ter erro #135000 - necessário fallback")
    
    print("=" * 80)

if __name__ == "__main__":
    main()