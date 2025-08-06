#!/usr/bin/env python3
"""
Debug template structure to fix error #135000
"""

import requests
import os
import json

def analyze_template_structure():
    """Analisar estrutura exata do template que está falhando"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Procurar o template específico
            target_template = None
            for template in data.get('data', []):
                if template.get('name') == 'jose_receita_1752589970_e459379c':
                    target_template = template
                    break
            
            if target_template:
                print("=== ESTRUTURA EXATA DO TEMPLATE ===")
                print(json.dumps(target_template, indent=2))
                
                print("\n=== ANÁLISE DOS COMPONENTES ===")
                components = target_template.get('components', [])
                
                for i, component in enumerate(components):
                    print(f"\nComponente {i+1}:")
                    print(f"  Tipo: {component.get('type')}")
                    
                    if component.get('type') == 'HEADER':
                        print(f"  Format: {component.get('format')}")
                        print(f"  Text: {component.get('text')}")
                        
                    elif component.get('type') == 'BODY':
                        print(f"  Text: {component.get('text')}")
                        
                    elif component.get('type') == 'BUTTONS':
                        buttons = component.get('buttons', [])
                        for j, button in enumerate(buttons):
                            print(f"  Botão {j+1}:")
                            print(f"    Tipo: {button.get('type')}")
                            print(f"    Text: {button.get('text')}")
                            print(f"    URL: {button.get('url')}")
                
                print("\n=== PAYLOAD CORRETO DEVE SER ===")
                # Montar payload correto baseado na estrutura
                correct_payload = create_correct_payload(target_template)
                print(json.dumps(correct_payload, indent=2))
                
            else:
                print("Template não encontrado!")
                
        else:
            print(f"Erro: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Erro: {e}")

def create_correct_payload(template_structure):
    """Criar payload correto baseado na estrutura do template"""
    
    components = []
    
    for component in template_structure.get('components', []):
        comp_type = component.get('type')
        
        if comp_type == 'HEADER':
            # Header pode precisar de parâmetros
            header_format = component.get('format')
            if header_format == 'TEXT':
                text = component.get('text', '')
                if '{{' in text:
                    # Header tem parâmetros
                    components.append({
                        'type': 'header',
                        'parameters': [
                            {'type': 'text', 'text': 'valor_do_parametro'}
                        ]
                    })
                else:
                    # Header sem parâmetros - não incluir
                    pass
                    
        elif comp_type == 'BODY':
            # Body sempre tem parâmetros
            components.append({
                'type': 'body',
                'parameters': [
                    {'type': 'text', 'text': '065.370.801-77'},  # CPF
                    {'type': 'text', 'text': 'Pedro'}           # Nome
                ]
            })
            
        elif comp_type == 'BUTTONS':
            # Verificar se botões têm parâmetros
            buttons = component.get('buttons', [])
            for i, button in enumerate(buttons):
                if button.get('type') == 'URL':
                    url = button.get('url', '')
                    if '{{' in url:
                        # Botão tem parâmetro
                        components.append({
                            'type': 'button',
                            'sub_type': 'url',
                            'index': i,
                            'parameters': [
                                {'type': 'text', 'text': '065.370.801-77'}
                            ]
                        })
    
    return {
        'messaging_product': 'whatsapp',
        'to': '+5561982132603',
        'type': 'template',
        'template': {
            'name': 'jose_receita_1752589970_e459379c',
            'language': {'code': 'en'},
            'components': components
        }
    }

if __name__ == '__main__':
    analyze_template_structure()