#!/usr/bin/env python3
"""
Teste direto dos templates aprovados da nova BM
"""

import os
import sys
import json
import logging
import requests
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_approved_templates():
    """Get all approved templates from the Business Manager"""
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    bm_id = "721254414139146"
    
    url = f"https://graph.facebook.com/v22.0/{bm_id}/message_templates"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'fields': 'name,status,language,components',
        'limit': 50
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            approved_templates = []
            for template in templates:
                if template.get('status') == 'APPROVED':
                    approved_templates.append(template)
            
            return approved_templates
        else:
            print(f"❌ Erro ao buscar templates: {response.status_code}")
            print(response.text)
            return []
            
    except Exception as e:
        print(f"❌ Exceção ao buscar templates: {e}")
        return []

def test_template_direct(template_name, language_code, phone="5561999114066"):
    """Test template directly via API"""
    
    # Initialize WhatsApp API
    whatsapp_api = WhatsAppBusinessAPI()
    
    # Test parameters (CPF, Nome)
    test_parameters = ["065.370.801-77", "Pedro"]
    
    print(f"\n🧪 TESTANDO TEMPLATE DIRETO: {template_name} ({language_code})")
    
    try:
        success, result = whatsapp_api.send_template_message(
            phone=phone,
            template_name=template_name,
            language_code=language_code,
            parameters=test_parameters
        )
        
        if success:
            print(f"✅ SUCESSO: Template {template_name} enviado!")
            print(f"📨 Message ID: {result.get('messageId', 'N/A')}")
            print(f"📋 Status: {result.get('status', 'N/A')}")
            
            # Check if contacts info is available
            if 'contacts' in result and result['contacts']:
                contact = result['contacts'][0]
                wa_id = contact.get('wa_id', 'N/A')
                input_phone = contact.get('input', 'N/A')
                print(f"📞 Input: {input_phone} -> WhatsApp ID: {wa_id}")
            
            return True
        else:
            error_code = result.get('error_code', 'N/A')
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ FALHOU: {template_name} - Erro #{error_code}: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: Erro ao testar {template_name}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 BUSCANDO TEMPLATES APROVADOS NA BM 721254414139146")
    print("=" * 60)
    
    # Get approved templates
    approved_templates = get_approved_templates()
    
    if not approved_templates:
        print("❌ Nenhum template aprovado encontrado!")
        sys.exit(1)
    
    print(f"📋 ENCONTRADOS {len(approved_templates)} TEMPLATES APROVADOS:")
    for i, template in enumerate(approved_templates, 1):
        name = template.get('name', 'N/A')
        language = template.get('language', 'N/A')
        components = template.get('components', [])
        comp_types = [comp.get('type') for comp in components]
        print(f"  {i}. {name} ({language}) - Componentes: {comp_types}")
    
    print(f"\n🧪 TESTANDO TEMPLATES PARA +5561999114066")
    print("=" * 60)
    
    success_count = 0
    
    # Test each approved template
    for template in approved_templates[:3]:  # Test first 3 templates
        name = template.get('name')
        language = template.get('language', 'en')
        
        if test_template_direct(name, language):
            success_count += 1
            print(f"🎯 TEMPLATE {name} FUNCIONOU! Parando teste.")
            break
    
    print(f"\n📊 RESULTADO: {success_count} template(s) funcionaram de {min(3, len(approved_templates))} testados")
    
    if success_count == 0:
        print("\n⚠️ PROBLEMA: Nenhum template funcionou!")
        print("💡 Possíveis causas:")
        print("  - Templates podem ter estrutura específica não suportada")
        print("  - Permissões de template podem estar restritas")
        print("  - Business Manager pode ter limitações ativas")
    
    sys.exit(0 if success_count > 0 else 1)