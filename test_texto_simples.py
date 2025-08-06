#!/usr/bin/env python3
"""
Teste com mensagem de texto simples para comparar
"""

import os
import requests

def test_texto_simples():
    """Test simple text message"""
    
    print(f"📱 TESTE MENSAGEM DE TEXTO SIMPLES")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "776788602173980"  # Phone GREEN
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': '+5573999084689',
        'type': 'text',
        'text': {
            'body': 'Teste de mensagem de texto simples - se esta chegar e o template não, então há problema específico com templates.'
        }
    }
    
    print(f"📞 Para: +5573999084689")
    print(f"📝 Mensagem: Texto simples")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            print(f"✅ Texto enviado - Message ID: {message_id}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_texto_simples()