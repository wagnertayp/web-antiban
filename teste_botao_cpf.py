#!/usr/bin/env python3
"""
Teste específico para verificar se o botão está enviando CPF
"""

import os
import requests

def teste_botao_cpf():
    """Test button parameter specifically"""
    
    print(f"🔘 TESTE ESPECÍFICO DO BOTÃO - CPF NO LINK")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "743517442172477"  # Da log anterior
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Template payload com parâmetros explícitos
    payload = {
        'messaging_product': 'whatsapp',
        'to': '5561999114066',
        'type': 'template',
        'template': {
            'name': 'maria_template_1753922257_9965ef8b',
            'language': {'code': 'en'},
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': 'Pedro'},  # {{1}} = Nome
                        {'type': 'text', 'text': '065.370.801-77'}   # {{2}} = CPF
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [{'type': 'text', 'text': '065.370.801-77'}]  # CPF no botão
                }
            ]
        }
    }
    
    print(f"📋 PAYLOAD ENVIADO:")
    print(f"   Body parameters: Pedro, 065.370.801-77")
    print(f"   Button parameter: 065.370.801-77")
    print(f"   Phone: {phone_id}")
    print(f"   Template: maria_template_1753922257_9965ef8b")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            
            print(f"✅ TEMPLATE ENVIADO COM SUCESSO!")
            print(f"📨 Message ID: {message_id}")
            print(f"📱 VERIFIQUE WHATSAPP +5561999114066")
            print(f"🔘 O BOTÃO DEVE ABRIR: https://example.com/065.370.801-77")
            print(f"   (Se abrir https://example.com/Pedro, ainda há erro)")
            
        else:
            error_data = response.json().get('error', {})
            print(f"❌ Erro: {error_data.get('code')} - {error_data.get('message')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    teste_botao_cpf()