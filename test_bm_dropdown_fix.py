#!/usr/bin/env python3
"""
Teste específico para resolver problema de BM com dropdown de header
Baseado na documentação oficial da Meta para erro #135000
"""

import requests
import json
import os

def test_different_structures():
    """Testar diferentes estruturas para resolver #135000 em BMs com dropdown"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = '674928665709899'
    
    if not access_token:
        print("ERROR: WHATSAPP_ACCESS_TOKEN não encontrado")
        return
    
    url = f'https://graph.facebook.com/v23.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Estruturas diferentes para testar
    structures = [
        # 1. Estrutura mínima - apenas body
        {
            "name": "Teste 1: Apenas body",
            "payload": {
                "messaging_product": "whatsapp",
                "to": "5561982132603",
                "type": "template",
                "template": {
                    "name": "modelo1",
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": "065.370.801-77"},
                                {"type": "text", "text": "Pedro Lima"}
                            ]
                        }
                    ]
                }
            }
        },
        
        # 2. Com index como string
        {
            "name": "Teste 2: Index como string",
            "payload": {
                "messaging_product": "whatsapp",
                "to": "5561982132603", 
                "type": "template",
                "template": {
                    "name": "modelo1",
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
                            "sub_type": "url",
                            "index": "0",
                            "parameters": [{"type": "text", "text": "065.370.801-77"}]
                        }
                    ]
                }
            }
        },
        
        # 3. Sem sub_type
        {
            "name": "Teste 3: Sem sub_type",
            "payload": {
                "messaging_product": "whatsapp",
                "to": "5561982132603",
                "type": "template", 
                "template": {
                    "name": "modelo1",
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
                            "index": 0,
                            "parameters": [{"type": "text", "text": "065.370.801-77"}]
                        }
                    ]
                }
            }
        },
        
        # 4. Template simples hello_world (deve funcionar)
        {
            "name": "Teste 4: Hello World",
            "payload": {
                "messaging_product": "whatsapp",
                "to": "5561982132603",
                "type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {"code": "en_US"}
                }
            }
        }
    ]
    
    for i, test in enumerate(structures, 1):
        print(f"\n=== {test['name']} ===")
        
        try:
            response = requests.post(url, json=test['payload'], headers=headers)
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ SUCESSO!")
                return test  # Retorna o teste que funcionou
            else:
                print("❌ FALHOU")
                
        except Exception as e:
            print(f"ERRO: {e}")
    
    return None

if __name__ == "__main__":
    working_structure = test_different_structures()
    
    if working_structure:
        print(f"\n🎉 ESTRUTURA QUE FUNCIONA: {working_structure['name']}")
        print(f"Payload: {json.dumps(working_structure['payload'], indent=2)}")
    else:
        print("\n😞 Nenhuma estrutura funcionou - problema específico desta BM")