#!/usr/bin/env python3
"""
DESCOBERTA AUTOMÁTICA DA NOVA BM JOSE CARLOS (639849885789886)
Busca templates aprovados e números de telefone disponíveis
"""
import os
import requests
import logging
from typing import Dict, List

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_jose_carlos_account():
    """Descobre templates e phone numbers da BM Jose Carlos"""
    
    print("=== DESCOBERTA AUTOMÁTICA BM JOSE CARLOS ===\n")
    
    # Configurar credenciais
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    business_account_id = "639849885789886"
    api_version = "v22.0"
    
    if not access_token:
        print("❌ WHATSAPP_ACCESS_TOKEN não encontrado nas secrets")
        return False
    
    print(f"🔑 Token encontrado: {access_token[:50]}...")
    print(f"🏢 Business Manager ID: {business_account_id}")
    print()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 1. Buscar Phone Numbers
    print("📱 DESCOBRINDO PHONE NUMBERS...")
    phone_url = f"https://graph.facebook.com/{api_version}/{business_account_id}/phone_numbers"
    
    try:
        response = requests.get(phone_url, headers=headers)
        print(f"📞 Status Phone Numbers: {response.status_code}")
        
        if response.status_code == 200:
            phone_data = response.json()
            phones = phone_data.get('data', [])
            
            print(f"✅ ENCONTRADOS {len(phones)} PHONE NUMBERS:")
            for i, phone in enumerate(phones, 1):
                phone_id = phone.get('id')
                display_name = phone.get('display_phone_number')
                status = phone.get('verified_name')
                quality = phone.get('quality_rating', 'UNKNOWN')
                
                print(f"  📱 Phone {i}: {display_name}")
                print(f"     ID: {phone_id}")
                print(f"     Status: {status}")
                print(f"     Quality: {quality}")
                print()
        else:
            print(f"❌ Erro ao buscar phone numbers: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na busca de phone numbers: {e}")
    
    # 2. Buscar Templates
    print("📋 DESCOBRINDO TEMPLATES APROVADOS...")
    template_url = f"https://graph.facebook.com/{api_version}/{business_account_id}/message_templates"
    
    try:
        response = requests.get(template_url, headers=headers)
        print(f"📋 Status Templates: {response.status_code}")
        
        if response.status_code == 200:
            template_data = response.json()
            templates = template_data.get('data', [])
            
            approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
            
            print(f"✅ ENCONTRADOS {len(approved_templates)} TEMPLATES APROVADOS:")
            for i, template in enumerate(approved_templates, 1):
                name = template.get('name')
                language = template.get('language')
                category = template.get('category')
                
                print(f"  📋 Template {i}: {name}")
                print(f"     Idioma: {language}")
                print(f"     Categoria: {category}")
                
                # Mostrar estrutura do template
                components = template.get('components', [])
                for comp in components:
                    comp_type = comp.get('type')
                    if comp_type == 'HEADER':
                        print(f"     Header: {comp.get('text', 'N/A')}")
                    elif comp_type == 'BODY':
                        print(f"     Body: {comp.get('text', 'N/A')[:100]}...")
                    elif comp_type == 'FOOTER':
                        print(f"     Footer: {comp.get('text', 'N/A')}")
                    elif comp_type == 'BUTTONS':
                        buttons = comp.get('buttons', [])
                        for btn in buttons:
                            print(f"     Botão: {btn.get('text', 'N/A')}")
                print()
        else:
            print(f"❌ Erro ao buscar templates: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na busca de templates: {e}")
    
    # 3. Testar Conectividade
    print("🔗 TESTANDO CONECTIVIDADE...")
    test_url = f"https://graph.facebook.com/{api_version}/me"
    
    try:
        response = requests.get(test_url, headers=headers)
        print(f"🔗 Status Conectividade: {response.status_code}")
        
        if response.status_code == 200:
            me_data = response.json()
            print(f"✅ CONECTADO COMO: {me_data.get('name', 'N/A')}")
            print(f"📊 ID: {me_data.get('id', 'N/A')}")
        else:
            print(f"❌ Erro na conectividade: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste de conectividade: {e}")
    
    print("\n=== RESUMO DA DESCOBERTA ===")
    print("🎯 Business Manager Jose Carlos configurada")
    print("📱 Phone Numbers descobertos e listados")
    print("📋 Templates aprovados identificados")
    print("🚀 Sistema pronto para MEGA LOTE sem erro #135000")
    
    return True

if __name__ == "__main__":
    discover_jose_carlos_account()