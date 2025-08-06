#!/usr/bin/env python3
"""
Debug modelo2 template systematically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def debug_modelo2():
    """Debug modelo2 template systematically"""
    
    print("🔍 DEBUG SISTEMÁTICO DO MODELO2")
    print("=" * 50)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    business_id = "746006914691827"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 1. Primeiro, buscar detalhes exatos do template modelo2
    print("1. BUSCANDO DETALHES DO TEMPLATE MODELO2")
    print("-" * 40)
    
    try:
        templates_url = f'https://graph.facebook.com/v23.0/{business_id}/message_templates'
        response = requests.get(templates_url, headers=headers)
        
        if response.status_code == 200:
            templates = response.json()
            modelo2_template = None
            
            for template in templates.get('data', []):
                if template.get('name') == 'modelo2':
                    modelo2_template = template
                    break
            
            if modelo2_template:
                print("✅ Template modelo2 encontrado:")
                print(json.dumps(modelo2_template, indent=2, ensure_ascii=False))
                
                # Extrair componentes
                components = modelo2_template.get('components', [])
                
                print("\n📋 COMPONENTES DO TEMPLATE:")
                for i, comp in enumerate(components):
                    print(f"Componente {i+1}: {comp.get('type')}")
                    if comp.get('type') == 'BODY':
                        print(f"  Texto: {comp.get('text')}")
                        print(f"  Exemplo: {comp.get('example', {}).get('body_text', [])}")
                    elif comp.get('type') == 'BUTTONS':
                        buttons = comp.get('buttons', [])
                        for j, btn in enumerate(buttons):
                            print(f"  Botão {j+1}: {btn.get('type')} - {btn.get('text')}")
                            if btn.get('type') == 'URL':
                                print(f"    URL: {btn.get('url')}")
                            
            else:
                print("❌ Template modelo2 não encontrado!")
                
        else:
            print(f"❌ Erro ao buscar templates: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 2. Testar estruturas diferentes do modelo2
    print("\n2. TESTANDO DIFERENTES ESTRUTURAS DO MODELO2")
    print("-" * 40)
    
    # Estrutura 1: Mais simples
    template_v1 = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "123.456.789-00"},
                        {"type": "text", "text": "João Teste"}
                    ]
                }
            ]
        }
    }
    
    # Estrutura 2: Com parameter_name
    template_v2 = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "parameter_name": "1", "text": "123.456.789-00"},
                        {"type": "text", "parameter_name": "2", "text": "João Teste"}
                    ]
                }
            ]
        }
    }
    
    # Estrutura 3: Com header se existir
    template_v3 = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {"type": "text", "text": "Notificação Extrajudicial"}
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "123.456.789-00"},
                        {"type": "text", "text": "João Teste"}
                    ]
                }
            ]
        }
    }
    
    templates_to_test = [
        ("Estrutura Simples", template_v1),
        ("Com parameter_name", template_v2),
        ("Com Header", template_v3)
    ]
    
    for name, template_payload in templates_to_test:
        print(f"\n🧪 TESTANDO: {name}")
        print(f"Payload: {json.dumps(template_payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
                headers=headers,
                json=template_payload
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                
                # Aguardar para ver se chega
                print("⏳ Aguardando 15 segundos para verificar entrega...")
                time.sleep(15)
                
            else:
                error_data = response.json()
                error = error_data.get('error', {})
                print(f"❌ FALHOU: {error.get('message')}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        
        print("-" * 20)
    
    # 3. Testar modelo1 para comparação
    print("\n3. TESTANDO MODELO1 PARA COMPARAÇÃO")
    print("-" * 40)
    
    modelo1_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo1",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "123.456.789-00"},
                        {"type": "text", "text": "João Teste"}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=modelo1_payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    print(f"\n🏁 DEBUG CONCLUÍDO")
    print("Verifique se alguma das mensagens chegou no WhatsApp.")

if __name__ == "__main__":
    debug_modelo2()