#!/usr/bin/env python3

def test_template_with_header():
    """Test templates with proper header structure"""
    
    import requests
    import json
    import os
    
    print("🔧 TESTANDO TEMPLATES COM CABEÇALHO CORRETO")
    print("=" * 50)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # TESTE 1: MODELO2 COM HEADER + BODY + BUTTON
    print("🧪 TESTANDO MODELO2 COM ESTRUTURA COMPLETA")
    print("-" * 45)
    
    modelo2_complete = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": []  # Header sem parâmetros
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"},  # {{1}} = CPF
                        {"type": "text", "text": "Pedro Lima"}      # {{2}} = Nome
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"}  # CPF para URL
                    ]
                }
            ]
        }
    }
    
    print(f"Estrutura completa: {json.dumps(modelo2_complete, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=modelo2_complete
        )
        
        print(f"\nSTATUS: {response.status_code}")
        print(f"RESPONSE: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"\n✅ MODELO2 FUNCIONOU COM HEADER! Message ID: {message_id}")
            print("🔔 VERIFIQUE SEU WHATSAPP!")
            return True
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    # TESTE 2: MODELO1 COM ESTRUTURA CORRETA (SEM HEADER)
    print(f"\n🧪 TESTANDO MODELO1 (SEM HEADER)")
    print("-" * 35)
    
    modelo1_correct = {
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
                        {"type": "text", "text": "065.370.801-77"},  # {{1}} = CPF
                        {"type": "text", "text": "Luan Assis"}       # {{2}} = Nome (do exemplo)
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"}  # CPF para URL
                    ]
                }
            ]
        }
    }
    
    print(f"Estrutura modelo1: {json.dumps(modelo1_correct, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=modelo1_correct
        )
        
        print(f"\nSTATUS: {response.status_code}")
        print(f"RESPONSE: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"\n✅ MODELO1 FUNCIONOU! Message ID: {message_id}")
            print("🔔 VERIFIQUE SEU WHATSAPP!")
            return True
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    # TESTE 3: DIFERENTES CÓDIGOS DE LINGUAGEM
    print(f"\n🧪 TESTANDO DIFERENTES IDIOMAS")
    print("-" * 35)
    
    languages = ["en", "en_US", "pt_BR"]
    
    for lang in languages:
        print(f"\nTestando linguagem: {lang}")
        
        lang_payload = {
            "messaging_product": "whatsapp",
            "to": test_number,
            "type": "template",
            "template": {
                "name": "modelo2",
                "language": {"code": lang},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "065.370.801-77"},
                            {"type": "text", "text": "Pedro Lima"}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": 0,
                        "parameters": [
                            {"type": "text", "text": "065.370.801-77"}
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
                headers=headers,
                json=lang_payload
            )
            
            print(f"Status {lang}: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                print(f"✅ SUCESSO com {lang}! Message ID: {message_id}")
                return True
            else:
                error_data = response.json()
                error = error_data.get('error', {})
                print(f"❌ Falhou {lang}: {error.get('message')}")
                
        except Exception as e:
            print(f"❌ Erro {lang}: {str(e)}")
    
    print(f"\n🏁 TESTE CONCLUÍDO")
    return False

if __name__ == "__main__":
    test_template_with_header()