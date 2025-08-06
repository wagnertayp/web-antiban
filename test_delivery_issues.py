#!/usr/bin/env python3
"""
Identificar problemas de entrega específicos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def test_delivery_issues():
    """Identificar problemas de entrega específicos"""
    
    print("🔍 TESTE COMPLETO DE ENTREGA")
    print("=" * 40)
    
    # Usar token atualizado
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 1. Enviar mensagem de texto simples
    print("1. TESTANDO MENSAGEM DE TEXTO")
    print("-" * 30)
    
    text_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "+5561982132603",
        "type": "text",
        "text": {
            "body": f"🔍 TESTE DE CONECTIVIDADE - {time.strftime('%H:%M:%S')}\n\nEste é um teste para verificar se as mensagens estão chegando corretamente.\n\nSe você recebeu esta mensagem, responda com 'OK' para confirmar."
        }
    }
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=text_payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            contact = result.get('contacts', [{}])[0]
            
            print(f"✅ Message ID: {message_id}")
            print(f"✅ Input: {contact.get('input')}")
            print(f"✅ WhatsApp ID: {contact.get('wa_id')}")
            
            # Aguardar um pouco
            print("\n⏳ Aguardando 10 segundos...")
            time.sleep(10)
            
            # 2. Verificar status da mensagem
            print("\n2. VERIFICANDO STATUS DA MENSAGEM")
            print("-" * 30)
            
            # Tentar obter status (nem sempre disponível imediatamente)
            try:
                status_response = requests.get(
                    f'https://graph.facebook.com/v23.0/{message_id}',
                    headers=headers
                )
                print(f"Status check: {status_response.status_code}")
                if status_response.status_code == 200:
                    print(f"Status data: {status_response.text}")
                else:
                    print("Status ainda não disponível (normal)")
            except Exception as e:
                print(f"Status check error: {str(e)}")
            
        else:
            print(f"❌ Erro no envio: {response.status_code}")
            print(f"Detalhes: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
    
    # 3. Testar template modelo2
    print("\n3. TESTANDO TEMPLATE MODELO2")
    print("-" * 30)
    
    template_payload = {
        "messaging_product": "whatsapp",
        "to": "+5561982132603",
        "type": "template",
        "template": {
            "name": "modelo2",
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
                            "text": "Pedro Teste"
                        }
                    ]
                }
            ]
        }
    }
    
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
            print(f"✅ Template Message ID: {message_id}")
        else:
            print(f"❌ Template falhou: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no template: {str(e)}")
    
    print("\n🏁 TESTE CONCLUÍDO")
    print("Verifique seu WhatsApp para confirmar o recebimento das mensagens.")

if __name__ == "__main__":
    test_delivery_issues()