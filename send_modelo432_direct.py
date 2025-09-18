#!/usr/bin/env python3
"""
Tentar enviar template modelo432 diretamente testando diferentes configurações
"""
import requests
import json

def try_send_modelo432():
    """Tentar enviar modelo432 testando diferentes abordagens"""
    
    new_token = "EAAKrs5Jx6qgBPQDDZAtl1tdpFsZB0MGcJZAK3FbjwzqqgN89bFtJlV50ScTkZCwnYsZBkoTy35nkCqFc3tgeAh6KMpSd4eySftGrGnmo6rXrnUdZAMDX53NJwiZAyJGecAlf0aoxS5wwjpOuaCC2CA7Wwa9g7uuTPWogNAcyohI3a5xy8ipBZBaE4yZA1DYGutcbZCcMo8abQ41I1Q08Iw5TWPZBKIlU3oZC2mMdwB1dXluitQZDZD"
    
    headers = {
        'Authorization': f'Bearer {new_token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 DESCOBRINDO BUSINESS MANAGERS DISPONÍVEIS")
    print("=" * 50)
    
    try:
        # Tentar descobrir Business Managers
        print("📱 1. Buscando Business Managers...")
        bm_url = "https://graph.facebook.com/v23.0/me/businesses"
        bm_response = requests.get(bm_url, headers=headers, timeout=10)
        
        if bm_response.status_code == 200:
            bm_data = bm_response.json()
            businesses = bm_data.get('data', [])
            
            if businesses:
                for business in businesses:
                    business_id = business['id']
                    business_name = business.get('name', 'N/A')
                    print(f"✅ Business encontrado: {business_name} (ID: {business_id})")
                    
                    # Tentar descobrir WhatsApp Business Accounts neste BM
                    print(f"\n📱 2. Buscando WBAAs no BM {business_id}...")
                    waba_url = f"https://graph.facebook.com/v23.0/{business_id}?fields=owned_whatsapp_business_accounts"
                    waba_response = requests.get(waba_url, headers=headers, timeout=10)
                    
                    if waba_response.status_code == 200:
                        waba_data = waba_response.json()
                        waba_accounts = waba_data.get('owned_whatsapp_business_accounts', {}).get('data', [])
                        
                        if waba_accounts:
                            for waba in waba_accounts:
                                waba_id = waba['id']
                                print(f"✅ WABA encontrado: {waba_id}")
                                
                                # Tentar buscar phone numbers
                                phones_url = f"https://graph.facebook.com/v23.0/{waba_id}/phone_numbers"
                                phones_response = requests.get(phones_url, headers=headers, timeout=10)
                                
                                if phones_response.status_code == 200:
                                    phones_data = phones_response.json()
                                    phone_list = phones_data.get('data', [])
                                    
                                    if phone_list:
                                        for phone in phone_list:
                                            phone_id = phone['id']
                                            phone_number = phone['display_phone_number']
                                            print(f"✅ Phone: {phone_number} (ID: {phone_id})")
                                            
                                            # Tentar enviar mensagem
                                            success = send_template_modelo432(phone_id, new_token)
                                            if success:
                                                return True
                                else:
                                    print(f"⚠️ Erro ao buscar phones do WABA {waba_id}: {phones_response.status_code}")
                        else:
                            print(f"⚠️ Nenhum WABA encontrado no BM {business_id}")
                    else:
                        print(f"⚠️ Erro ao buscar WABAs do BM {business_id}: {waba_response.status_code}")
            else:
                print("❌ Nenhum Business Manager encontrado")
        else:
            print(f"❌ Erro ao buscar Business Managers: {bm_response.status_code}")
            print(f"Resposta: {bm_response.text}")
        
        # Se não encontrou através de BMs, tentar abordagem direta
        print(f"\n🔄 Tentando abordagem alternativa...")
        return try_direct_approach(new_token)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def try_direct_approach(token):
    """Tentar descobrir configuração através de apps"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("📱 3. Tentando descobrir através de apps...")
        apps_url = "https://graph.facebook.com/v23.0/me/accounts"
        apps_response = requests.get(apps_url, headers=headers, timeout=10)
        
        if apps_response.status_code == 200:
            apps_data = apps_response.json()
            print(f"📊 Dados recebidos: {json.dumps(apps_data, indent=2)}")
            
            # Se ainda não funcionar, vou tentar com IDs conhecidos do log
            known_phone_ids = [
                "693473723855916",  # Do log anterior
                "123456789",  # Usado nos testes
            ]
            
            for phone_id in known_phone_ids:
                print(f"\n🔄 Testando Phone ID conhecido: {phone_id}")
                success = send_template_modelo432(phone_id, token)
                if success:
                    return True
            
            return False
        else:
            print(f"❌ Erro ao buscar apps: {apps_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na abordagem direta: {e}")
        return False

def send_template_modelo432(phone_id, token):
    """Enviar mensagem usando template modelo432"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    # Payload com template modelo432 - versão simplificada
    payload = {
        "messaging_product": "whatsapp",
        "to": "5561999114066",  # Sem o + para testar
        "type": "template",
        "template": {
            "name": "modelo432",
            "language": {
                "code": "pt_BR"
            }
        }
    }
    
    print(f"\n📤 ENVIANDO TEMPLATE modelo432...")
    print(f"📞 Para: 5561999114066")
    print(f"📱 Phone ID: {phone_id}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCESSO! TEMPLATE modelo432 ENVIADO!")
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
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
    success = try_send_modelo432()
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEMPLATE modelo432 ENVIADO COM SUCESSO!")
        print("📱 Verifique seu WhatsApp agora!")
    else:
        print("⚠️ Não foi possível enviar o template modelo432")
        print("🔧 Pode ser necessário verificar as configurações do WhatsApp Business API")