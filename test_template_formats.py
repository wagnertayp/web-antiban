#!/usr/bin/env python3
"""
Testar diferentes formatos de envio para resolver erro #135000
Baseado na estrutura exata dos templates aprovados
"""

import requests
import os
import json
import time

def test_template_formats():
    """Testar diferentes formatos para resolver erro #135000"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = '674928665709899'
    to_number = '5548999581973'
    
    url = f'https://graph.facebook.com/v23.0/{phone_number_id}/messages'
    
    # Carregar estrutura do modelo1
    with open('approved_modelo1_final.json', 'r') as f:
        modelo1 = json.load(f)
    
    print("=== TESTANDO FORMATOS PARA RESOLVER ERRO #135000 ===\n")
    
    # Teste 1: Formato básico corrigido
    test1_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "modelo1",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        },
                        {
                            "type": "text",
                            "text": "Luan Assis"
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        }
                    ]
                }
            ]
        }
    }
    
    # Teste 2: Sem componente de botão
    test2_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "modelo1",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        },
                        {
                            "type": "text",
                            "text": "Luan Assis"
                        }
                    ]
                }
            ]
        }
    }
    
    # Teste 3: Formato completo com header/footer
    test3_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "modelo1",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        },
                        {
                            "type": "text",
                            "text": "Luan Assis"
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url", 
                    "index": 0,
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        }
                    ]
                }
            ]
        }
    }
    
    # Teste 4: Formato usando um dos templates novos criados
    test4_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "duplicate_1752574988_0",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        },
                        {
                            "type": "text",
                            "text": "Luan Assis"
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "065.370.801-77"
                        }
                    ]
                }
            ]
        }
    }
    
    tests = [
        ("Teste 1: Formato Básico Modelo1", test1_payload),
        ("Teste 2: Sem Botão", test2_payload),
        ("Teste 3: Index Numérico", test3_payload),
        ("Teste 4: Template Novo", test4_payload)
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    for test_name, payload in tests:
        print(f"{test_name}")
        print(f"Template: {payload['template']['name']}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            result = response.json()
            
            if response.status_code == 200:
                message_id = result.get('messages', [{}])[0].get('id', 'N/A')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                print(f"🎉 Formato funcionou - erro #135000 resolvido!")
                return True, test_name, payload
                
            else:
                error = result.get('error', {})
                error_code = error.get('code', 'N/A')
                error_msg = error.get('message', 'Desconhecido')
                print(f"❌ Erro {error_code}: {error_msg}")
                
        except Exception as e:
            print(f"❌ Exceção: {e}")
        
        print("\n" + "-"*50 + "\n")
        time.sleep(1)
    
    return False, None, None

def test_different_phone_id():
    """Testar com Phone Number ID diferente se disponível"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # Tentar descobrir outros Phone Number IDs
    try:
        response = requests.get(
            f'https://graph.facebook.com/v23.0/746006914691827/phone_numbers',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            phone_numbers = data.get('data', [])
            
            print("=== PHONE NUMBERS DISPONÍVEIS ===")
            for phone in phone_numbers:
                print(f"ID: {phone.get('id')}")
                print(f"Número: {phone.get('display_phone_number')}")
                print(f"Status: {phone.get('verified_name')}")
                print("-" * 30)
            
            return phone_numbers
        
    except Exception as e:
        print(f"❌ Erro ao buscar Phone Numbers: {e}")
    
    return []

if __name__ == "__main__":
    print("=== RESOLVENDO ERRO #135000 COM TEMPLATES APROVADOS ===\n")
    
    # Testar formatos diferentes
    success, working_format, working_payload = test_template_formats()
    
    if success:
        print(f"🎉 ERRO #135000 RESOLVIDO!")
        print(f"✅ Formato que funcionou: {working_format}")
        
        # Salvar formato que funciona
        with open('working_template_format.json', 'w') as f:
            json.dump({
                'success': True,
                'working_format': working_format,
                'payload': working_payload,
                'resolved_date': time.time()
            }, f, indent=2)
        
        print(f"💾 Formato salvo em: working_template_format.json")
    else:
        print(f"❌ Nenhum formato funcionou")
        print(f"🔍 Verificando Phone Numbers disponíveis...")
        
        phone_numbers = test_different_phone_id()
        
        if phone_numbers:
            print(f"💡 Tentar com Phone Number ID diferente")
        else:
            print(f"💡 Problema pode ser com a Business Account ou permissões")