#!/usr/bin/env python3

def test_modelo2_structure():
    """Test different structures for modelo2 template"""
    
    import requests
    import json
    import os
    import time
    
    print("🔬 TESTANDO ESTRUTURAS ESPECÍFICAS DO MODELO2")
    print("=" * 55)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # ESTRUTURA 1: Buttons como array (Nova tentativa)
    structure_1 = {
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
                        {"type": "text", "text": "065.370.801-77"},
                        {"type": "text", "text": "Pedro Lima"}
                    ]
                },
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "type": "url",
                            "parameters": [
                                {"type": "text", "text": "065.370.801-77"}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    # ESTRUTURA 2: Button individual com índice correto
    structure_2 = {
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
                        {"type": "text", "text": "065.370.801-77"},
                        {"type": "text", "text": "Pedro Lima"}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "URL",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"}
                    ]
                }
            ]
        }
    }
    
    # ESTRUTURA 3: Sem header explícito, foco nos parâmetros corretos
    structure_3 = {
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
                        {"type": "text", "text": "065.370.801-77"},  # {{1}} = CPF
                        {"type": "text", "text": "Pedro Lima"}      # {{2}} = Nome
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"}  # Parâmetro para URL
                    ]
                }
            ]
        }
    }
    
    # ESTRUTURA 4: Testando com locale pt_BR
    structure_4 = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "pt_BR"},
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
    
    structures = [
        ("Estrutura 1 - Buttons Array", structure_1),
        ("Estrutura 2 - Button URL Maiúsculo", structure_2),
        ("Estrutura 3 - Padrão Corrigido", structure_3),
        ("Estrutura 4 - Locale pt_BR", structure_4)
    ]
    
    for name, payload in structures:
        print(f"\n🧪 TESTANDO: {name}")
        print("-" * 35)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
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
                print(f"✅ SUCESSO! Message ID: {message_id}")
                print("🔔 TEMPLATE MODELO2 FUNCIONOU! VERIFIQUE SEU WHATSAPP!")
                
                # Se funcionou, aguardar um pouco para confirmar
                print("\n⏳ Aguardando 15 segundos para confirmar entrega...")
                time.sleep(15)
                return True
                
            else:
                error_response = response.json()
                error = error_response.get('error', {})
                print(f"❌ FALHOU:")
                print(f"   Código: {error.get('code')}")
                print(f"   Mensagem: {error.get('message')}")
                print(f"   Detalhes: {error.get('error_data', {}).get('details')}")
                
        except Exception as e:
            print(f"❌ ERRO NA REQUISIÇÃO: {str(e)}")
        
        print("=" * 55)
        time.sleep(2)  # Aguardar entre testes
    
    print(f"\n🏁 TODOS OS TESTES CONCLUÍDOS")
    print("Se nenhuma estrutura funcionou, o template modelo2 pode estar temporariamente pausado.")
    
    return False

if __name__ == "__main__":
    test_modelo2_structure()