#!/usr/bin/env python3

def test_modelo2_variations():
    """Test different variations of modelo2 template structure"""
    
    import requests
    import json
    import os
    
    print("🎯 TESTE FINAL MODELO2 - VARIÁVEIS CORRETAS")
    print("=" * 50)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # CPF e Nome para teste
    cpf = "065.370.801-77"  # {{1}} = CPF
    nome = "Pedro Lima"     # {{2}} = Nome
    
    # VARIAÇÃO 1: Estrutura correta com variáveis na ordem certa
    variation_1 = {
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
                        {"type": "text", "text": cpf},   # {{1}} = CPF
                        {"type": "text", "text": nome}   # {{2}} = Nome
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": cpf}    # URL parameter = CPF
                    ]
                }
            ]
        }
    }
    
    # VARIAÇÃO 2: Com recipient_type explícito
    variation_2 = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
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
    
    # VARIAÇÃO 3: Teste com dados exatos do exemplo do template
    variation_3 = {
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
                        {"type": "text", "text": "065.370.801-77"},  # Exato do exemplo
                        {"type": "text", "text": "Pedro Lima"}      # Exato do exemplo
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"}  # Exato do exemplo
                    ]
                }
            ]
        }
    }
    
    # VARIAÇÃO 4: Com o SEU CPF real para teste
    variation_4 = {
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
                        {"type": "text", "text": "123.456.789-00"},  # CPF de teste
                        {"type": "text", "text": "João Silva"}      # Seu nome
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
    
    variations = [
        ("Variação 1 - Estrutura Padrão", variation_1),
        ("Variação 2 - Com recipient_type", variation_2),
        ("Variação 3 - Dados do Exemplo", variation_3),
        ("Variação 4 - Dados de Teste", variation_4)
    ]
    
    for name, payload in variations:
        print(f"\n🧪 TESTANDO: {name}")
        print("-" * 40)
        
        # Mostrar estrutura
        components = payload["template"]["components"]
        body_params = components[0]["parameters"]
        button_params = components[1]["parameters"]
        
        print(f"CPF ({{{{1}}}}): {body_params[0]['text']}")
        print(f"Nome ({{{{2}}}}): {body_params[1]['text']}")
        print(f"URL Botão: https://www.intimacao.org/{button_params[0]['text']}")
        print()
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
                headers=headers,
                json=payload
            )
            
            print(f"\nSTATUS: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id')
                contact = result.get('contacts', [{}])[0]
                
                print(f"✅ SUCESSO! TEMPLATE MODELO2 FUNCIONOU!")
                print(f"   Message ID: {message_id}")
                print(f"   WhatsApp ID: {contact.get('wa_id')}")
                print(f"   URL final: https://www.intimacao.org/{button_params[0]['text']}")
                print("\n🔔 VERIFIQUE SEU WHATSAPP AGORA!")
                print("   A mensagem deve ter chegado com o botão 'Regularizar meu CPF'")
                
                return True  # Sucesso!
                
            else:
                error_response = response.json()
                error = error_response.get('error', {})
                print(f"❌ FALHOU:")
                print(f"   Código: {error.get('code')}")
                print(f"   Mensagem: {error.get('message')}")
                print(f"   Detalhes: {error.get('error_data', {}).get('details')}")
                
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
        
        print("=" * 50)
    
    print(f"\n🏁 TESTE CONCLUÍDO")
    print("Se todas as variações falharam, pode haver um problema temporário com o template.")
    
    return False

if __name__ == "__main__":
    test_modelo2_variations()