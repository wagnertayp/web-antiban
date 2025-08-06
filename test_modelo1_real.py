#!/usr/bin/env python3
"""
Teste real com template modelo1 aprovado
"""

import requests
import os

def test_modelo1_approved():
    """Testar envio real com modelo1 que está aprovado"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '674928665709899')
    
    url = f'https://graph.facebook.com/v23.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Teste com dados reais
    test_phone = '+5573999084689'
    test_cpf = '123.456.789-00'
    test_nome = 'Teste Sistema'
    
    # Template modelo1 aprovado (ID: 1409279126974744)
    template_payload = {
        'messaging_product': 'whatsapp',
        'to': test_phone,
        'type': 'template',
        'template': {
            'name': 'modelo1',
            'language': {
                'code': 'en'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': test_cpf
                        },
                        {
                            'type': 'text', 
                            'text': test_nome
                        }
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {
                            'type': 'text',
                            'text': test_cpf
                        }
                    ]
                }
            ]
        }
    }
    
    print("=== TESTE TEMPLATE MODELO1 APROVADO ===")
    print(f"Template: modelo1 (ID: 1409279126974744)")
    print(f"Status: APPROVED")
    print(f"Telefone: {test_phone}")
    print(f"CPF: {test_cpf}")
    print(f"Nome: {test_nome}")
    print(f"\nEnviando...")
    
    try:
        response = requests.post(url, json=template_payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            
            print(f"✅ MENSAGEM ENVIADA COM SUCESSO!")
            print(f"Message ID: {message_id}")
            print(f"🎉 Template modelo1 está funcionando perfeitamente!")
            
            return True, message_id
            
        else:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', {}).get('message', response.text)
            
            print(f"❌ ERRO NO ENVIO:")
            print(f"Status: {response.status_code}")
            print(f"Erro: {error_message}")
            
            return False, error_message
            
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        return False, str(e)

if __name__ == "__main__":
    success, result = test_modelo1_approved()
    
    if success:
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"✅ Template modelo1 aprovado e funcional")
        print(f"📱 Sistema pronto para envio em massa")
        print(f"🚀 Pode processar até 29K contatos com modelo1")
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"📝 Erro: {result}")
        print(f"🔧 Verificar configuração do token/phone ID")