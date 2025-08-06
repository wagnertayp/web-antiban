#!/usr/bin/env python3
"""
Teste enviando template para o número do usuário
"""

import requests

def send_to_user_number():
    """Envia template para o número do usuário"""
    
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    phone_id = "743171782208180"  # Phone com Quality GREEN
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    user_number = "+5561999114066"
    
    print(f"📱 Enviando template para {user_number}...")
    
    # Template modelo3 
    template_payload = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "template",
        "template": {
            "name": "modelo3",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "065.370.801-77"},
                        {"type": "text", "text": "USUARIO SISTEMA"}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [{"type": "text", "text": "065.370.801-77"}]
                }
            ]
        }
    }
    
    try:
        send_response = requests.post(
            f"{base_url}/{phone_id}/messages",
            headers=headers,
            json=template_payload,
            timeout=15
        )
        
        print(f"Status: {send_response.status_code}")
        print(f"Response: {send_response.text}")
        
        if send_response.status_code == 200:
            response_data = send_response.json()
            message_id = response_data.get('messages', [{}])[0].get('id')
            wa_id = response_data.get('contacts', [{}])[0].get('wa_id')
            
            print(f"✅ TEMPLATE ENVIADO COM SUCESSO!")
            print(f"   Template: modelo3")
            print(f"   Message ID: {message_id}")
            print(f"   WhatsApp ID: {wa_id}")
            print(f"   Phone usado: {phone_id} (Quality GREEN)")
            
            # Enviar também mensagem de texto
            print(f"\n📤 Enviando mensagem de texto adicional...")
            
            text_payload = {
                "messaging_product": "whatsapp",
                "to": user_number,
                "type": "text",
                "text": {
                    "body": "🎉 BM JOSE CARLOS FUNCIONANDO!\n\nEste é um teste da Business Manager 639849885789886\n\nPhone ID: 743171782208180\nQuality Rating: GREEN\nStatus: VERIFIED\n\nSistema operacional e pronto para campanhas!"
                }
            }
            
            text_response = requests.post(
                f"{base_url}/{phone_id}/messages",
                headers=headers,
                json=text_payload,
                timeout=15
            )
            
            print(f"Text Status: {text_response.status_code}")
            if text_response.status_code == 200:
                text_data = text_response.json()
                text_message_id = text_data.get('messages', [{}])[0].get('id')
                print(f"✅ Text Message ID: {text_message_id}")
            
            return True
            
        else:
            print(f"❌ Erro: {send_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = send_to_user_number()
    if success:
        print("\n🎉 MENSAGENS ENVIADAS PARA SEU NÚMERO!")
        print("✅ Template modelo3 enviado")
        print("✅ Mensagem de texto adicional enviada")
        print("✅ BM Jose Carlos funcionando perfeitamente")
    else:
        print("\n❌ Erro no envio")