#!/usr/bin/env python3
"""
Descobrir Business Accounts disponíveis para o token fornecido
"""

import requests
import json

def discover_business_account():
    """Descobrir qual Business Account está disponível para o token"""
    
    access_token = "EAAYLvZBaHbvYBPSFAJtcYTWqp02BxufOizAA5l6H4D93yls5X7m9ONZCwTZCTbf2oJZCtMjg5mjjwy141Ow27ZAv1yC6dXJGSOKcTSEZBf2tkciWfZCraJZANY3xXCiKi2bcwpOIfD6EUNWcEgXIlYphIIyIZCSIxMT926AdMpuZBUjLnOE64c8UPKzZA4bBKcfTi2GHqZC4q3bQbeZCOvEl1q1AdohNxZCZBNdDIOXjXiuL1znl0CJVgZDZD"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== DESCOBRINDO BUSINESS ACCOUNTS DISPONÍVEIS ===\n")
    print(f"Token: {access_token[:50]}...")
    print("-" * 60)
    
    # 1. Obter informações do usuário
    try:
        me_response = requests.get(
            "https://graph.facebook.com/v22.0/me", 
            headers=headers, 
            timeout=10
        )
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            user_id = me_data.get('id')
            print(f"✅ Usuário encontrado:")
            print(f"   ID: {user_id}")
            print(f"   Nome: {me_data.get('name', 'N/A')}")
        else:
            print(f"❌ Erro ao obter dados do usuário: {me_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Tentar descobrir WhatsApp Business Accounts
    print(f"\n📊 PROCURANDO WHATSAPP BUSINESS ACCOUNTS...")
    
    # Opção 1: Através do campo whatsapp_business_accounts
    try:
        waba_response = requests.get(
            f"https://graph.facebook.com/v22.0/me?fields=whatsapp_business_accounts",
            headers=headers,
            timeout=10
        )
        
        if waba_response.status_code == 200:
            waba_data = waba_response.json()
            accounts = waba_data.get('whatsapp_business_accounts', {}).get('data', [])
            
            if accounts:
                print(f"✅ {len(accounts)} WhatsApp Business Account(s) encontrada(s):")
                
                for i, account in enumerate(accounts, 1):
                    account_id = account.get('id')
                    name = account.get('name', 'N/A')
                    print(f"\n   📱 Account {i}:")
                    print(f"      ID: {account_id}")
                    print(f"      Nome: {name}")
                    
                    # Agora verificar essa Business Account
                    verify_specific_account(account_id, access_token, headers)
                    
                return accounts
            else:
                print("❌ Nenhuma WhatsApp Business Account encontrada neste endpoint")
        else:
            print(f"❌ Erro ao buscar WhatsApp Business Accounts: {waba_response.status_code}")
            print(f"   Resposta: {waba_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Opção 2: Através do campo accounts
    print(f"\n📊 PROCURANDO ATRAVÉS DO CAMPO ACCOUNTS...")
    try:
        accounts_response = requests.get(
            f"https://graph.facebook.com/v22.0/me?fields=accounts",
            headers=headers,
            timeout=10
        )
        
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            accounts = accounts_data.get('accounts', {}).get('data', [])
            
            if accounts:
                print(f"✅ {len(accounts)} Account(s) encontrada(s):")
                for account in accounts[:5]:  # Mostrar só os primeiros 5
                    print(f"   - ID: {account.get('id')}, Nome: {account.get('name', 'N/A')}")
            else:
                print("❌ Nenhuma account encontrada")
        else:
            print(f"❌ Erro ao buscar accounts: {accounts_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Opção 3: Através do campo businesses
    print(f"\n📊 PROCURANDO ATRAVÉS DO CAMPO BUSINESSES...")
    try:
        businesses_response = requests.get(
            f"https://graph.facebook.com/v22.0/me?fields=businesses",
            headers=headers,
            timeout=10
        )
        
        if businesses_response.status_code == 200:
            businesses_data = businesses_response.json()
            businesses = businesses_data.get('businesses', {}).get('data', [])
            
            if businesses:
                print(f"✅ {len(businesses)} Business(es) encontrada(s):")
                for business in businesses:
                    print(f"   - ID: {business.get('id')}, Nome: {business.get('name', 'N/A')}")
            else:
                print("❌ Nenhum business encontrado")
        else:
            print(f"❌ Erro ao buscar businesses: {businesses_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

    # Opção 4: Tentar IDs conhecidos baseados no padrão do token
    print(f"\n📊 TESTANDO BUSINESS ACCOUNTS CONHECIDAS...")
    
    # Baseado no código existente, vou testar alguns IDs conhecidos
    known_business_ids = [
        "580318035149016",  # BM Cleide
        "2089992404820473", # BM Iara
        "639849885789886",  # BM Jose Carlos  
        "1523966465251146", # BM Michele
        "1243060407061288", # BM Pamela Lins
        "721254414139146",  # Nova BM
        "746006914691827"   # Outra BM conhecida
    ]
    
    for business_id in known_business_ids:
        try:
            test_response = requests.get(
                f"https://graph.facebook.com/v22.0/{business_id}?fields=id,name",
                headers=headers,
                timeout=5
            )
            
            if test_response.status_code == 200:
                data = test_response.json()
                print(f"✅ ENCONTRADO: ID {business_id}")
                print(f"   Nome: {data.get('name', 'N/A')}")
                
                # Verificar esta conta específica
                verify_specific_account(business_id, access_token, headers)
                break
            else:
                print(f"❌ ID {business_id}: Não acessível")
                
        except Exception as e:
            print(f"❌ Erro testando ID {business_id}: {e}")

def verify_specific_account(business_account_id, access_token, headers):
    """Verificar uma Business Account específica"""
    
    print(f"\n🔍 VERIFICANDO BUSINESS ACCOUNT: {business_account_id}")
    print("-" * 40)
    
    # Verificar números de telefone
    try:
        phones_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/phone_numbers?fields=id,display_phone_number,verified_name,code_verification_status,status,quality_rating",
            headers=headers,
            timeout=10
        )
        
        if phones_response.status_code == 200:
            phones_data = phones_response.json()
            phones = phones_data.get('data', [])
            approved_phones = [p for p in phones if p.get('code_verification_status') == 'VERIFIED' or p.get('status') == 'CONNECTED']
            
            print(f"📱 Números:")
            print(f"   Total: {len(phones)}")
            print(f"   Aprovados: {len(approved_phones)}")
            
            for phone in phones:
                status_icon = "✅" if phone.get('code_verification_status') == 'VERIFIED' else "⏳"
                print(f"   {status_icon} {phone.get('display_phone_number', 'N/A')} - {phone.get('status', 'N/A')}")
        else:
            print(f"❌ Erro ao buscar números: {phones_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar números: {e}")
    
    # Verificar templates
    try:
        templates_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/message_templates?fields=id,name,status,category,language",
            headers=headers,
            timeout=10
        )
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            templates = templates_data.get('data', [])
            approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
            
            print(f"📋 Templates:")
            print(f"   Total: {len(templates)}")
            print(f"   Aprovados: {len(approved_templates)}")
            
            if approved_templates:
                print(f"   ✅ Templates Aprovados:")
                for template in approved_templates[:5]:  # Mostrar só os primeiros 5
                    print(f"      - {template.get('name', 'N/A')} ({template.get('language', 'N/A')})")
        else:
            print(f"❌ Erro ao buscar templates: {templates_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar templates: {e}")
    
    print("-" * 40)

if __name__ == "__main__":
    discover_business_account()