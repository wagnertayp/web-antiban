#!/usr/bin/env python3
"""
TESTE DIRETO COM TOKEN CORRETO
Valida que o template modelo21 funciona com pt_BR
"""
import requests
import json
import sys
import os

# Add current directory to Python path
sys.path.append('.')

def test_template_modelo21():
    """Test template modelo21 with correct configuration"""
    
    # Token correto fornecido pelo usuário
    token = 'EAAHUCvWVsdgBPHkcZCTfAaXvv3ZBIHjvJeyOXxGZAHtl100cGnTQ4TCZBD13QBejypSoAwIZAz0UIQijq5ZCCdljcwLAs5HeWgDocYUXZBkZBVjezZACRKCScaPZA5F0Yo6YGP62EWK5PqZCiSN8AEWfOwp9wZAmU8c0hm606hidXa5rdGz8dVN0zwO2yo2ydceIX2usTO7zVWWwg7eZBqaDtNDJBcc37HBKnicKjKrME9NaoG4bJ2wZDZD'
    
    # Phone ID que funciona
    phone_id = '774576132396207'
    
    # Configure environment
    os.environ['WHATSAPP_ACCESS_TOKEN'] = token
    
    print("=== TESTE TEMPLATE modelo21 ===")
    
    # Test template with correct language
    payload = {
        'messaging_product': 'whatsapp',
        'to': '+5561999114066',
        'type': 'template',
        'template': {
            'name': 'modelo21',
            'language': {
                'code': 'pt_BR'  # IDIOMA CORRETO
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': '065.370.801-77'},
                        {'type': 'text', 'text': 'Pedro'}
                    ]
                },
                {
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {'type': 'text', 'text': '065.370.801-77'}
                    ]
                }
            ]
        }
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://graph.facebook.com/v22.0/{phone_id}/messages'
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', '')
            print(f"✅ SUCCESS: Template modelo21 enviado!")
            print(f"✅ Message ID: {message_id}")
            print(f"✅ Language: pt_BR (correto)")
            print(f"✅ Phone ID: {phone_id}")
            return True
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ FAILED: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def update_environment_with_correct_token():
    """Update system to use correct token"""
    token = 'EAAHUCvWVsdgBPHkcZCTfAaXvv3ZBIHjvJeyOXxGZAHtl100cGnTQ4TCZBD13QBejypSoAwIZAz0UIQijq5ZCCdljcwLAs5HeWgDocYUXZBkZBVjezZACRKCScaPZA5F0Yo2YGP62EWK5PqZCiSN8AEWfOwp9wZAmU8c0hm606hidXa5rdGz8dVN0zwO2yo2ydceIX2usTO7zVWWwg7eZBqaDtNDJBcc37HBKnicKjKrME9NaoG4bJ2wZDZD'
    
    # Set environment variable
    os.environ['WHATSAPP_ACCESS_TOKEN'] = token
    
    # Test WhatsApp service with new token
    from services.whatsapp_business_api import WhatsAppBusinessAPI
    
    api = WhatsAppBusinessAPI()
    api._access_token = token  # Force token update
    
    # Test getting templates
    templates = api.get_available_templates()
    print(f"\n=== TEMPLATES DISPONÍVEIS COM TOKEN CORRETO ===")
    print(f"Total: {len(templates)}")
    
    for template in templates[:5]:
        name = template.get('name', 'unknown')
        lang = template.get('language', 'unknown')
        status = template.get('status', 'unknown')
        print(f"  - {name} ({lang}, {status})")
    
    # Look specifically for modelo21
    modelo21 = None
    for template in templates:
        if template.get('name') == 'modelo21':
            modelo21 = template
            break
    
    if modelo21:
        print(f"\n✅ MODELO21 ENCONTRADO:")
        print(f"  Language: {modelo21.get('language')}")
        print(f"  Status: {modelo21.get('status')}")
        print(f"  Category: {modelo21.get('category')}")
        return True
    else:
        print(f"\n❌ modelo21 não encontrado")
        return False

if __name__ == "__main__":
    print("=== CONFIGURAÇÃO E TESTE DO SISTEMA ===")
    
    # 1. Test direct template send
    template_success = test_template_modelo21()
    
    # 2. Update system environment
    system_success = update_environment_with_correct_token()
    
    print(f"\n=== RESULTADO ===")
    print(f"Template direto: {'✅ SUCESSO' if template_success else '❌ FALHOU'}")
    print(f"Sistema atualizado: {'✅ SUCESSO' if system_success else '❌ FALHOU'}")
    
    if template_success and system_success:
        print(f"\n🚀 SISTEMA CORRIGIDO: modelo21 com pt_BR funcionando!")
    else:
        print(f"\n⚠️ AJUSTES NECESSÁRIOS")