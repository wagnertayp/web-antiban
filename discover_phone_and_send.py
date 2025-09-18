#!/usr/bin/env python3
"""
Descobrir o Phone Number ID correto e enviar mensagem com template modelo432
"""
import requests
import json

def discover_and_send():
    """Descobrir Phone Number ID e enviar mensagem"""
    
    new_token = "EAAKrs5Jx6qgBPTPJbOYU408mal45OAe52ZCQHTs8XDjhyNogP7ChZCUv5bFuVGNQtwpW6DAkW934ZBySZCCcmOXTSXdJZATWIF0CYLhVsWws4kgJnZBZCJ9zOJKtetuYQeP9zRivOjysRJIeJ5r4j8XUH3RH74TLRj1ZAbLCnfAOsTaeQAuzGNE3f8TO0mGxcUVgRbyHfJ3O08E3D5VHoV3HtNm0lWhi3eQItuX2ZC2CTlwZDZD"
    
    headers = {
        'Authorization': f'Bearer {new_token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 DESCOBRINDO CONFIGURAÇÃO CORRETA")
    print("=" * 50)
    
    try:
        # Primeiro, descobrir quais apps estão disponíveis
        print("📱 1. Descobrindo WhatsApp Business Accounts...")
        me_url = "https://graph.facebook.com/v23.0/me?fields=id,name"
        me_response = requests.get(me_url, headers=headers, timeout=10)
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"✅ App conectado: {me_data.get('name', 'N/A')} (ID: {me_data.get('id')})")
            app_id = me_data.get('id')
        else:
            print(f"❌ Erro ao obter informações do app: {me_response.status_code}")
            return False
        
        # Descobrir WhatsApp Business Accounts
        print("\n📱 2. Descobrindo WhatsApp Business Accounts...")
        accounts_url = f"https://graph.facebook.com/v23.0/{app_id}?fields=whatsapp_business_accounts"
        accounts_response = requests.get(accounts_url, headers=headers, timeout=10)
        
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            waba_list = accounts_data.get('whatsapp_business_accounts', {}).get('data', [])
            
            if waba_list:
                waba_id = waba_list[0]['id']
                print(f"✅ WABA encontrado: {waba_id}")
                
                # Descobrir phone numbers
                print(f"\n📱 3. Descobrindo Phone Numbers do WABA {waba_id}...")
                phones_url = f"https://graph.facebook.com/v23.0/{waba_id}/phone_numbers"
                phones_response = requests.get(phones_url, headers=headers, timeout=10)
                
                if phones_response.status_code == 200:
                    phones_data = phones_response.json()
                    phone_list = phones_data.get('data', [])
                    
                    if phone_list:
                        phone_id = phone_list[0]['id']
                        phone_number = phone_list[0]['display_phone_number']
                        print(f"✅ Phone encontrado: {phone_number} (ID: {phone_id})")
                        
                        # Agora enviar mensagem com template modelo432
                        return send_message_modelo432(phone_id, new_token)
                    else:
                        print("❌ Nenhum phone number encontrado")
                        return False
                else:
                    print(f"❌ Erro ao buscar phone numbers: {phones_response.status_code}")
                    print(f"Resposta: {phones_response.text}")
                    return False
            else:
                print("❌ Nenhum WhatsApp Business Account encontrado")
                return False
        else:
            print(f"❌ Erro ao buscar accounts: {accounts_response.status_code}")
            print(f"Resposta: {accounts_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_message_modelo432(phone_id, token):
    """Enviar mensagem usando template modelo432"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    # Payload usando template modelo432
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
                }
            ]
        }
    }
    
    print(f"\n📤 4. ENVIANDO MENSAGEM COM TEMPLATE modelo432...")
    print(f"📞 Para: +55 61 99911-4066")
    print(f"📋 Template: modelo432")
    print(f"📱 Phone ID: {phone_id}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MENSAGEM ENVIADA COM SUCESSO!")
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
    success = discover_and_send()
    print("\n" + "=" * 50)
    if success:
        print("🎉 MENSAGEM MODELO432 ENVIADA!")
        print("📱 Verifique seu WhatsApp agora")
    else:
        print("⚠️ Falha no envio")