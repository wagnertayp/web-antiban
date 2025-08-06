#!/usr/bin/env python3
"""
TESTE DIRETO TEMPLATE MODELO_80 CORRIGIDO
Valida que o template modelo_80 agora funciona com pt_BR
"""
import requests
import json
import sys
import os

# Add current directory to Python path
sys.path.append('.')

def test_template_modelo_80_ptbr():
    """Test template modelo_80 with corrected Portuguese configuration"""
    
    # Token atual do sistema
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("❌ WHATSAPP_ACCESS_TOKEN não encontrado")
        return False
    
    # Phone ID configurado no sistema  
    phone_id = '768334853022518'
    
    print("=== TESTE TEMPLATE modelo_80 CORRIGIDO ===")
    print(f"Token: {token[:50]}...")
    print(f"Phone ID: {phone_id}")
    
    # Test template with CORRECT Portuguese language
    payload = {
        'messaging_product': 'whatsapp',
        'to': '+5548999581973',
        'type': 'template',
        'template': {
            'name': 'modelo_80',
            'language': {
                'code': 'pt_BR'  # IDIOMA CORRIGIDO PARA PORTUGUÊS
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': '052.894.602-17'},  # CPF
                        {'type': 'text', 'text': 'Boss'}            # Nome
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {'type': 'text', 'text': '052.894.602-17'}  # CPF para URL
                    ]
                }
            ]
        }
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\nPayload estrutura corrigida:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v22.0/{phone_id}/messages',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\nSTATUS: {response.status_code}")
        print(f"RESPONSE: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"\n✅ MODELO_80 FUNCIONOU COM PT_BR! Message ID: {message_id}")
            print("🔔 VERIFIQUE SEU WHATSAPP!")
            return True
        else:
            print(f"❌ FALHOU: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    test_template_modelo_80_ptbr()