#!/usr/bin/env python3
"""
Teste direto para verificar templates disponíveis e suas estruturas
"""
import os
import requests

def test_templates_direct():
    """Testar diretamente os templates disponíveis"""
    
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Business Manager ID correto
    business_id = "580318035149016"
    
    print(f"🔍 Testando Business Manager ID: {business_id}")
    
    # Buscar todos os templates
    url = f"https://graph.facebook.com/v22.0/{business_id}/message_templates?limit=50"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            print(f"\n📋 TOTAL DE TEMPLATES: {len(templates)}")
            
            approved_templates = []
            for template in templates:
                name = template.get('name', '')
                status = template.get('status', '')
                language = template.get('language', '')
                category = template.get('category', '')
                
                print(f"\n📄 Template: {name}")
                print(f"   Status: {status}")
                print(f"   Language: {language}")
                print(f"   Category: {category}")
                
                if status == 'APPROVED':
                    approved_templates.append(name)
                    
                    # Mostrar componentes
                    components = template.get('components', [])
                    for comp in components:
                        comp_type = comp.get('type', '')
                        if comp_type == 'BODY':
                            text = comp.get('text', '')
                            print(f"   Body: {text[:100]}...")
                        elif comp_type == 'BUTTONS':
                            buttons = comp.get('buttons', [])
                            print(f"   Buttons: {len(buttons)} button(s)")
            
            print(f"\n✅ TEMPLATES APROVADOS ({len(approved_templates)}):")
            for name in approved_templates:
                print(f"   - {name}")
                
        else:
            print(f"ERRO: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def test_phone_ids():
    """Testar Phone IDs disponíveis"""
    
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    business_id = "580318035149016"
    
    print(f"\n📱 Testando Phone Numbers do Business Manager: {business_id}")
    
    url = f"https://graph.facebook.com/v22.0/{business_id}/phone_numbers"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            phones = data.get('data', [])
            
            print(f"\n📞 TOTAL DE PHONE NUMBERS: {len(phones)}")
            
            for phone in phones:
                phone_id = phone.get('id', '')
                display_name = phone.get('display_phone_number', '')
                verified_name = phone.get('verified_name', '')
                status = phone.get('account_mode', '')
                
                print(f"\n📱 Phone ID: {phone_id}")
                print(f"   Display: {display_name}")
                print(f"   Name: {verified_name}")
                print(f"   Status: {status}")
                
        else:
            print(f"ERRO: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_templates_direct()
    test_phone_ids()