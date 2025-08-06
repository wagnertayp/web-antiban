#!/usr/bin/env python3

def test_modelo1():
    """Test modelo1 for comparison"""
    
    import requests
    import json
    import os
    
    print("🔍 TESTANDO MODELO1 PARA COMPARAÇÃO")
    print("=" * 45)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    business_id = "746006914691827"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Primeiro buscar detalhes do modelo1
    print("1. VERIFICANDO DETALHES DO MODELO1")
    print("-" * 40)
    
    try:
        templates_url = f'https://graph.facebook.com/v23.0/{business_id}/message_templates'
        response = requests.get(templates_url, headers=headers)
        
        if response.status_code == 200:
            templates = response.json()
            
            for template in templates.get('data', []):
                if template.get('name') == 'modelo1':
                    print("✅ Template modelo1 encontrado:")
                    print(json.dumps(template, indent=2, ensure_ascii=False))
                    break
                    
        else:
            print(f"❌ Erro ao buscar templates: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Testar modelo1 - estrutura simples
    print("\n2. TESTANDO MODELO1")
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
                        {"type": "text", "text": "123.456.789-00"},  # {{1}} = CPF  
                        {"type": "text", "text": "João Silva"}      # {{2}} = Nome
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "123.456.789-00"}  # CPF no botão
                    ]
                }
            ]
        }
    }
    
    print(f"Payload modelo1: {json.dumps(modelo1_payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=modelo1_payload
        )
        
        print(f"\nSTATUS: {response.status_code}")
        print(f"RESPONSE: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"\n✅ MODELO1 FUNCIONOU! Message ID: {message_id}")
            print("🔔 VERIFIQUE SEU WHATSAPP!")
            return True
        else:
            error_data = response.json()
            error = error_data.get('error', {})
            print(f"\n❌ MODELO1 FALHOU:")
            print(f"   Código: {error.get('code')}")
            print(f"   Mensagem: {error.get('message')}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    # Verificar se é problema da conta
    print("\n3. VERIFICANDO STATUS DA CONTA")
    print("-" * 40)
    
    try:
        account_url = f'https://graph.facebook.com/v23.0/{phone_number_id}'
        response = requests.get(account_url, headers=headers)
        
        if response.status_code == 200:
            account_data = response.json()
            print("Status da conta:")
            for key, value in account_data.items():
                print(f"  {key}: {value}")
        else:
            print(f"Erro ao verificar conta: {response.text}")
            
    except Exception as e:
        print(f"Erro: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_modelo1()