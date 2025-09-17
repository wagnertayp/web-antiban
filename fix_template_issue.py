#!/usr/bin/env python3
"""
CORREÇÃO EMERGENCIAL: Descobrir templates válidos e atualizar sistema
"""
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_valid_templates():
    """Descobrir templates realmente aprovados"""
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not access_token:
        print("❌ Token não encontrado")
        return None
    
    # Business Manager ID do log
    bm_id = "1042625774627654"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f'https://graph.facebook.com/v23.0/{bm_id}/message_templates'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            approved_templates = []
            for template in templates:
                if template.get('status') == 'APPROVED':
                    template_info = {
                        'name': template.get('name'),
                        'language': template.get('language'),
                        'category': template.get('category'),
                        'components': template.get('components', [])
                    }
                    approved_templates.append(template_info)
            
            print(f"✅ TEMPLATES APROVADOS ENCONTRADOS ({len(approved_templates)}):")
            for template in approved_templates:
                print(f"  📋 {template['name']} - {template['language']} - {template['category']}")
                
                # Check if has parameters
                has_params = False
                has_buttons = False
                for comp in template['components']:
                    if comp.get('type') == 'BODY' and '{{' in comp.get('text', ''):
                        has_params = True
                    if comp.get('type') == 'BUTTONS':
                        has_buttons = True
                
                print(f"    Parameters: {has_params}, Buttons: {has_buttons}")
            
            # Return the first valid template
            if approved_templates:
                best_template = approved_templates[0]
                print(f"\n🎯 TEMPLATE RECOMENDADO: {best_template['name']}")
                return best_template['name']
            
        else:
            print(f"❌ Erro ao buscar templates: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    valid_template = get_valid_templates()
    if valid_template:
        print(f"\n✅ USE ESTE TEMPLATE: {valid_template}")
    else:
        print("\n❌ Nenhum template válido encontrado")