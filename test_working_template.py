#!/usr/bin/env python3

def test_working_template():
    """Test a template we know works"""
    
    import requests
    import json
    import os
    
    print("🔍 TESTANDO TEMPLATES QUE FUNCIONAM")
    print("=" * 45)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    business_id = "746006914691827"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 1. Buscar todos os templates disponíveis
    print("1. BUSCANDO TODOS OS TEMPLATES DISPONÍVEIS")
    print("-" * 40)
    
    try:
        templates_url = f'https://graph.facebook.com/v23.0/{business_id}/message_templates'
        response = requests.get(templates_url, headers=headers)
        
        if response.status_code == 200:
            templates = response.json()
            available_templates = []
            
            for template in templates.get('data', []):
                name = template.get('name')
                status = template.get('status')
                category = template.get('category')
                language = template.get('language')
                
                print(f"Template: {name}")
                print(f"  Status: {status}")
                print(f"  Categoria: {category}")
                print(f"  Idioma: {language}")
                
                if status == 'APPROVED':
                    available_templates.append(template)
                    
                print()
                
            print(f"✅ Templates aprovados: {len(available_templates)}")
            
        else:
            print(f"❌ Erro ao buscar templates: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return
    
    # 2. Testar templates simples primeiro
    print("\n2. TESTANDO TEMPLATES SIMPLES (SEM BOTÕES)")
    print("-" * 40)
    
    for template in available_templates:
        name = template.get('name')
        components = template.get('components', [])
        
        # Verificar se tem botões
        has_buttons = any(comp.get('type') == 'BUTTONS' for comp in components)
        
        if not has_buttons:
            print(f"\n🧪 TESTANDO TEMPLATE SIMPLES: {name}")
            
            # Estrutura básica para templates sem botões
            simple_payload = {
                "messaging_product": "whatsapp",
                "to": test_number,
                "type": "template",
                "template": {
                    "name": name,
                    "language": {"code": "en"}
                }
            }
            
            # Adicionar parâmetros se necessário
            body_component = next((comp for comp in components if comp.get('type') == 'BODY'), None)
            if body_component and '{{' in body_component.get('text', ''):
                # Template tem parâmetros
                param_count = body_component.get('text', '').count('{{')
                if param_count > 0:
                    simple_payload["template"]["components"] = [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": f"Param{i+1}"} for i in range(param_count)
                            ]
                        }
                    ]
            
            try:
                response = requests.post(
                    f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
                    headers=headers,
                    json=simple_payload
                )
                
                print(f"STATUS: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get('messages', [{}])[0].get('id')
                    print(f"✅ TEMPLATE {name} FUNCIONOU! Message ID: {message_id}")
                    print("🔔 VERIFIQUE SEU WHATSAPP!")
                    return name  # Retorna o primeiro que funciona
                else:
                    print(f"❌ Falhou: {response.text}")
                    
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
    
    # 3. Testar hello_world se existir (template padrão)
    print("\n3. TESTANDO HELLO_WORLD (PADRÃO)")
    print("-" * 40)
    
    hello_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=hello_payload
        )
        
        print(f"STATUS: {response.status_code}")
        print(f"RESPONSE: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"✅ HELLO_WORLD FUNCIONOU! Message ID: {message_id}")
            return "hello_world"
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    print(f"\n🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_working_template()