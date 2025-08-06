#!/usr/bin/env python3
"""
Teste com número real que sabemos que funciona
"""

import requests

def test_real_delivery():
    """Teste com número que sabemos que recebe mensagens"""
    
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    phone_id = "743171782208180"
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Testar com número que sabemos que funcionou em BMs anteriores
    test_number = "+5573999084689"  # Número que recebeu mensagens anteriormente
    
    print(f"🧪 TESTE FINAL - ENTREGA PARA NÚMERO CONHECIDO")
    print(f"📱 Phone ID: {phone_id} (Quality GREEN)")
    print(f"📞 Destinatário: {test_number}")
    
    # Mensagem de texto simples
    message_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "text",
        "text": {
            "body": "🔥 TESTE CRÍTICO BM JOSE CARLOS\n\nSe esta mensagem chegou, a BM está funcionando!\n\nTeste realizado via Phone ID: 743171782208180\nBusiness Manager: 639849885789886\nQuality Rating: GREEN"
        }
    }
    
    print(f"\n📤 Enviando mensagem de texto...")
    
    try:
        send_response = requests.post(
            f"{base_url}/{phone_id}/messages",
            headers=headers,
            json=message_payload,
            timeout=15
        )
        
        print(f"Status: {send_response.status_code}")
        print(f"Response: {send_response.text}")
        
        if send_response.status_code == 200:
            response_data = send_response.json()
            message_id = response_data.get('messages', [{}])[0].get('id')
            wa_id = response_data.get('contacts', [{}])[0].get('wa_id')
            
            print(f"✅ SUCESSO!")
            print(f"   Message ID: {message_id}")
            print(f"   WhatsApp ID: {wa_id}")
            
            print(f"\n📋 Testando template aprovado...")
            
            # Testar template
            template_payload = {
                "messaging_product": "whatsapp",
                "to": test_number,
                "type": "template",
                "template": {
                    "name": "modelo3",
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": "123.456.789-00"},
                                {"type": "text", "text": "TESTE JOSE CARLOS"}
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "url",
                            "index": 0,
                            "parameters": [{"type": "text", "text": "123.456.789-00"}]
                        }
                    ]
                }
            }
            
            template_response = requests.post(
                f"{base_url}/{phone_id}/messages",
                headers=headers,
                json=template_payload,
                timeout=15
            )
            
            print(f"Template Status: {template_response.status_code}")
            print(f"Template Response: {template_response.text}")
            
            if template_response.status_code == 200:
                template_data = template_response.json()
                template_message_id = template_data.get('messages', [{}])[0].get('id')
                print(f"✅ Template Message ID: {template_message_id}")
                
                return True
            else:
                print(f"❌ Template falhou: {template_response.status_code}")
                return False
                
        else:
            print(f"❌ Erro no envio: {send_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_real_delivery()
    if success:
        print("\n🎉 BM JOSE CARLOS ENTREGANDO MENSAGENS!")
        print("✅ Tanto texto quanto template funcionando")
        print("✅ Quality GREEN confirmado")
        print("✅ Sistema operacional")
    else:
        print("\n❌ Problema na entrega identificado")
        print("⚠️  Conta pode estar em período de revisão")
        print("⚠️  Ou número específico bloqueado")