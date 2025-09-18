#!/usr/bin/env python3
"""
Testar o novo token diretamente na API do WhatsApp
"""
import requests
import json

def test_new_token():
    """Testar novo token diretamente"""
    
    new_token = "EAAKrs5Jx6qgBPfeaK7WytbhiewOmUJFMWo0WrFyqpXngb2St5btTZAJY3MZAGcWvQ0y00rIs95m0PBdAkfa0q5ZAPsOjEhqGcB7FPxDCfyZAuai0IAqMTCkNtZCJA8h1zfZCNV4H6YEZCNbx6rZBvMyZCaNvl5sAPhH8Jq1rwvVXumOZA53OHvEqz8k5OrHIqUGZBDCwieOZBFtJOSxijuJHIJPmL2uSFktI4rfDJ51MSNOAywZDZD"
    
    headers = {
        'Authorization': f'Bearer {new_token}',
        'Content-Type': 'application/json'
    }
    
    print("🧪 TESTANDO NOVO TOKEN DIRETAMENTE")
    print("=" * 50)
    print(f"🔑 Token: {new_token[:20]}...")
    
    try:
        # Testar se o token está válido
        print("\n1️⃣ Testando validade do token...")
        me_url = "https://graph.facebook.com/v23.0/me"
        me_response = requests.get(me_url, headers=headers, timeout=10)
        
        print(f"📊 Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"✅ Token válido! App: {me_data.get('name', 'N/A')} (ID: {me_data.get('id')})")
            
            # Descobrir Business Managers
            print("\n2️⃣ Descobrindo Business Managers...")
            bm_url = "https://graph.facebook.com/v23.0/me/businesses"
            bm_response = requests.get(bm_url, headers=headers, timeout=10)
            
            if bm_response.status_code == 200:
                bm_data = bm_response.json()
                businesses = bm_data.get('data', [])
                
                print(f"📊 {len(businesses)} Business Managers encontrados")
                
                for business in businesses:
                    business_id = business['id']
                    business_name = business.get('name', 'N/A')
                    print(f"   📈 {business_name} (ID: {business_id})")
                    
                    # Buscar WhatsApp Business Accounts
                    print(f"\n3️⃣ Buscando WABAs no BM {business_id}...")
                    waba_url = f"https://graph.facebook.com/v23.0/{business_id}?fields=owned_whatsapp_business_accounts"
                    waba_response = requests.get(waba_url, headers=headers, timeout=10)
                    
                    if waba_response.status_code == 200:
                        waba_data = waba_response.json()
                        waba_accounts = waba_data.get('owned_whatsapp_business_accounts', {}).get('data', [])
                        
                        print(f"📱 {len(waba_accounts)} WABAs encontrados")
                        
                        for waba in waba_accounts:
                            waba_id = waba['id']
                            print(f"   📞 WABA: {waba_id}")
                            
                            # Buscar phone numbers
                            phones_url = f"https://graph.facebook.com/v23.0/{waba_id}/phone_numbers"
                            phones_response = requests.get(phones_url, headers=headers, timeout=10)
                            
                            if phones_response.status_code == 200:
                                phones_data = phones_response.json()
                                phone_list = phones_data.get('data', [])
                                
                                for phone in phone_list:
                                    phone_id = phone['id']
                                    phone_number = phone['display_phone_number']
                                    status = phone.get('status', 'N/A')
                                    print(f"     📲 {phone_number} (ID: {phone_id}) - Status: {status}")
                                    
                                    # TENTAR ENVIAR MENSAGEM COM PRIMEIRO PHONE VÁLIDO
                                    if status == 'CONNECTED':
                                        print(f"\n4️⃣ TENTANDO ENVIAR MENSAGEM VIA {phone_number}...")
                                        return send_message_direct(phone_id, new_token)
                            else:
                                print(f"   ❌ Erro ao buscar phones: {phones_response.status_code}")
                    else:
                        print(f"   ❌ Erro ao buscar WABAs: {waba_response.status_code}")
                        
                return False
            else:
                print(f"❌ Erro ao buscar Business Managers: {bm_response.status_code}")
                return False
        else:
            print(f"❌ Token inválido: {me_response.status_code}")
            print(f"Resposta: {me_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_message_direct(phone_id, token):
    """Enviar mensagem diretamente"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    # Payload simples com template modelo432
    payload = {
        "messaging_product": "whatsapp",
        "to": "5561999114066",
        "type": "template",
        "template": {
            "name": "modelo432",
            "language": {
                "code": "en_US"
            }
        }
    }
    
    print(f"📤 Enviando template modelo432 para +55 61 99911-4066...")
    print(f"📱 Phone ID: {phone_id}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 MENSAGEM ENVIADA COM SUCESSO!")
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'messages' in result:
                message_id = result['messages'][0]['id']
                print(f"🆔 Message ID: {message_id}")
            
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'N/A')
                error_code = error_data.get('error', {}).get('code', 'N/A')
                print(f"📝 Erro {error_code}: {error_msg}")
            except:
                print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no envio: {e}")
        return False

if __name__ == "__main__":
    success = test_new_token()
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEMPLATE modelo432 ENVIADO COM SUCESSO!")
        print("📱 Verifique seu WhatsApp!")
    else:
        print("⚠️ Não foi possível enviar")
        print("🔧 Verificar configurações do token/WhatsApp")