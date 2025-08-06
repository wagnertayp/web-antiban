#!/usr/bin/env python3

def test_modelo2_exact():
    """Test modelo2 with exact structure variations"""
    
    import requests
    import json
    import os
    
    print("🎯 TESTE MODELO2 - ESTRUTURA EXATA")
    print("=" * 40)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Dados de teste exatos
    cpf = "065.370.801-77"  # {{1}}
    nome = "Pedro Lima"     # {{2}}
    
    # TESTE 1: Modelo2 com header se tiver
    test1 = {
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
                        {"type": "text", "text": cpf},   # {{1}}
                        {"type": "text", "text": nome}   # {{2}}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": cpf}    # URL param
                    ]
                }
            ]
        }
    }
    
    # TESTE 2: Modelo2 sem header explícito
    test2 = {
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
                        {"type": "text", "text": cpf},
                        {"type": "text", "text": nome}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": cpf}
                    ]
                }
            ]
        }
    }
    
    # TESTE 3: Sem footer explícito, apenas body + button
    test3 = {
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
                        {"type": "text", "text": cpf},
                        {"type": "text", "text": nome}
                    ]
                }
            ]
        }
    }
    
    tests = [
        ("TESTE 1 - Com Header", test1),
        ("TESTE 2 - Sem Header", test2), 
        ("TESTE 3 - Só Body", test3)
    ]
    
    for name, payload in tests:
        print(f"\n{name}")
        print("-" * 30)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        try:
            response = requests.post(
                f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            print(f"\nSTATUS: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                print("🔔 TEMPLATE MODELO2 FUNCIONOU!")
                return True
            else:
                error_data = response.json()
                error = error_data.get('error', {})
                print(f"❌ FALHOU: {error.get('code')} - {error.get('message')}")
                
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
        
        print("=" * 40)
    
    return False

if __name__ == "__main__":
    test_modelo2_exact()