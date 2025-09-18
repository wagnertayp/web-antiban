#!/usr/bin/env python3
"""
Enviar mensagem diretamente com o novo token através da API
"""
import requests
import json

def send_direct_whatsapp():
    """Enviar mensagem diretamente usando o novo token"""
    
    # Novo token fornecido pelo usuário
    new_token = "EAAKrs5Jx6qgBPTPJbOYU408mal45OAe52ZCQHTs8XDjhyNogP7ChZCUv5bFuVGNQtwpW6DAkW934ZBySZCCcmOXTSXdJZATWIF0CYLhVsWws4kgJnZBZCJ9zOJKtetuYQeP9zRivOjysRJIeJ5r4j8XUH3RH74TLRj1ZAbLCnfAOsTaeQAuzGNE3f8TO0mGxcUVgRbyHfJ3O08E3D5VHoV3HtNm0lWhi3eQItuX2ZC2CTlwZDZD"
    
    # Phone Number ID - preciso descobrir o correto
    phone_id = "693473723855916"  # Do log anterior
    
    # Dados da mensagem para o usuário
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {new_token}',
        'Content-Type': 'application/json'
    }
    
    # Payload usando o template modelo432 conforme solicitado
    payload = {
        "messaging_product": "whatsapp",
        "to": "+5561999114066",
        "type": "template",
        "template": {
            "name": "modelo432",
            "language": {
                "code": "pt_BR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "Usuário"},
                        {"type": "text", "text": "Teste"}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": "Usuário"}
                    ]
                }
            ]
        }
    }
    
    print("📱 ENVIANDO MENSAGEM DIRETA VIA WHATSAPP API")
    print("=" * 50)
    print(f"📞 Para: +55 61 99911-4066")
    print(f"📋 Template: modelo432 (conforme solicitado)")
    print(f"🔑 Token: {new_token[:20]}...")
    print(f"📱 Phone ID: {phone_id}")
    
    try:
        print("\n📤 Enviando para WhatsApp API...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MENSAGEM ENVIADA DIRETAMENTE!")
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'messages' in result:
                message_id = result['messages'][0]['id']
                print(f"🆔 Message ID: {message_id}")
            
            return True
        else:
            print(f"❌ ERRO: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = send_direct_whatsapp()
    print("\n" + "=" * 50)
    if success:
        print("🎉 MENSAGEM ENVIADA COM SUCESSO!")
        print("📱 Verifique seu WhatsApp agora")
    else:
        print("⚠️ Falha no envio - verifique token/configurações")