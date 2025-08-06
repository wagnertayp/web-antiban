#!/usr/bin/env python3
"""
Script para registrar telefone +1 831 283 1347 na WhatsApp Business API
com certificado Tabelião Damião
"""

import os
import requests
import json

def get_access_token():
    """Get access token from environment"""
    return os.environ.get('WHATSAPP_ACCESS_TOKEN')

def register_phone_number():
    """Register phone number +1 831 283 1347 with WhatsApp Business API"""
    
    access_token = get_access_token()
    if not access_token:
        print("❌ ERRO: WHATSAPP_ACCESS_TOKEN não encontrado")
        return False
    
    # Phone number details
    phone_number = "8312831347"
    country_code = "1"
    verified_name = "Tabelião Damião"
    business_manager_id = "1610705919605544"
    certificate = "Cm0KKQjA69vJ0PHIAhIGZW50OndhIhBUYWJlbGnDo28gRGFtaWFvUND43sMGGkDzD8Wyf2FLY1CCR5lLV7wP7Du7slHXgrs7bZfKdnJjPkfjvihbULCVx/lQfSfrv9GR/lhqDZUDyZ89rJCh+L4FEi5tbVaQ44/EmPNatbOdqmotk1zt4F/F2M2+EkJOrTw8Uyq6WR4iOEFKncRZIaVO"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📞 Registrando telefone: +{country_code} {phone_number}")
    print(f"📝 Nome verificado: {verified_name}")
    print(f"🏢 Business Manager: {business_manager_id}")
    
    # Método 1: Tentar registrar via Business Manager
    print("\n=== MÉTODO 1: Registro via Business Manager ===")
    url = f"https://graph.facebook.com/v23.0/{business_manager_id}/phone_numbers"
    
    payload = {
        "cc": country_code,
        "phone_number": phone_number,
        "verified_name": verified_name,
        "cert": certificate
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ SUCESSO - Método 1!")
            print(f"Phone Number ID: {result.get('id')}")
            print(f"Display Name: {result.get('display_phone_number')}")
            print(f"Status: {result.get('status')}")
            return result.get('id')
        else:
            print(f"❌ Falhou - Método 1: {result.get('error', {}).get('message', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Exceção - Método 1: {str(e)}")
    
    # Método 2: Tentar descobrir WhatsApp Business Account ID correto
    print("\n=== MÉTODO 2: Descobrir WABA ID ===")
    
    # Buscar informações do usuário
    try:
        user_response = requests.get(
            "https://graph.facebook.com/v23.0/me", 
            headers=headers, 
            timeout=10
        )
        user_data = user_response.json()
        user_id = user_data.get('id')
        
        print(f"User ID: {user_id}")
        
        # Tentar buscar WhatsApp Business Account através de diferentes métodos
        possible_waba_endpoints = [
            f"https://graph.facebook.com/v23.0/{user_id}/whatsapp_business_accounts",
            f"https://graph.facebook.com/v23.0/{business_manager_id}/owned_whatsapp_business_accounts",
            f"https://graph.facebook.com/v23.0/{business_manager_id}/client_whatsapp_business_accounts"
        ]
        
        for endpoint in possible_waba_endpoints:
            try:
                waba_response = requests.get(endpoint, headers=headers, timeout=10)
                if waba_response.status_code == 200:
                    waba_data = waba_response.json()
                    print(f"✅ Encontrado WABA em: {endpoint}")
                    print(f"WABA Data: {json.dumps(waba_data, indent=2)}")
                    
                    # Se encontrar WABAs, tentar registrar telefone
                    if 'data' in waba_data and len(waba_data['data']) > 0:
                        for waba in waba_data['data']:
                            waba_id = waba['id']
                            print(f"Tentando registrar em WABA: {waba_id}")
                            
                            register_url = f"https://graph.facebook.com/v23.0/{waba_id}/phone_numbers"
                            register_response = requests.post(
                                register_url, 
                                headers=headers, 
                                json=payload, 
                                timeout=30
                            )
                            
                            if register_response.status_code == 200:
                                register_result = register_response.json()
                                print("✅ SUCESSO - Método 2!")
                                print(f"Phone Number ID: {register_result.get('id')}")
                                return register_result.get('id')
                            else:
                                register_error = register_response.json()
                                print(f"❌ Falhou em WABA {waba_id}: {register_error.get('error', {}).get('message')}")
                else:
                    print(f"❌ Falhou: {endpoint} - Status: {waba_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exceção em {endpoint}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Erro ao buscar user info: {str(e)}")
    
    # Método 3: Tentar registro direto (assumindo que telefone já foi adicionado manualmente)
    print("\n=== MÉTODO 3: Registro direto (requer Phone Number ID) ===")
    print("⚠️  Este método requer que o telefone já tenha sido adicionado ao Business Manager")
    print("    e você tenha o Phone Number ID correto.")
    
    # Se soubermos o Phone Number ID, podemos tentar registrar
    possible_phone_ids = [
        f"1{phone_number}",  # +18312831347
        f"{country_code}{phone_number}",  # 18312831347
        phone_number  # 8312831347
    ]
    
    for phone_id in possible_phone_ids:
        try:
            register_url = f"https://graph.facebook.com/v23.0/{phone_id}/register"
            register_payload = {
                "messaging_product": "whatsapp",
                "pin": "000000"  # PIN padrão - deve ser alterado
            }
            
            register_response = requests.post(
                register_url,
                headers=headers,
                json=register_payload,
                timeout=30
            )
            
            if register_response.status_code == 200:
                register_result = register_response.json()
                print(f"✅ SUCESSO - Método 3 com Phone ID: {phone_id}")
                print(f"Result: {json.dumps(register_result, indent=2)}")
                return phone_id
            else:
                register_error = register_response.json()
                print(f"❌ Falhou Phone ID {phone_id}: {register_error.get('error', {}).get('message')}")
                
        except Exception as e:
            print(f"❌ Exceção Phone ID {phone_id}: {str(e)}")
    
    print("\n❌ TODOS OS MÉTODOS FALHARAM")
    print("\n📋 PRÓXIMOS PASSOS MANUAIS:")
    print("1. Acesse o WhatsApp Business Manager: https://business.facebook.com/wa/manage/")
    print("2. Vá em 'Phone Numbers' e clique 'Add Phone Number'")
    print("3. Adicione o número +1 831 283 1347")
    print("4. Configure o nome verificado como 'Tabelião Damião'")
    print("5. Após SMS de verificação, use a API para completar o registro")
    
    return False

def test_current_setup():
    """Test current WhatsApp API setup"""
    access_token = get_access_token()
    if not access_token:
        print("❌ ERRO: Token não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== TESTANDO SETUP ATUAL ===")
    
    # Test token validity
    try:
        response = requests.get("https://graph.facebook.com/v23.0/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token válido - User: {user_data.get('name')} (ID: {user_data.get('id')})")
        else:
            print(f"❌ Token inválido: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Erro ao testar token: {str(e)}")
        return
    
    # Check permissions
    try:
        perm_response = requests.get("https://graph.facebook.com/v23.0/me/permissions", headers=headers, timeout=10)
        if perm_response.status_code == 200:
            perms = perm_response.json()
            print("📋 Permissões:")
            for perm in perms.get('data', []):
                status = "✅" if perm['status'] == 'granted' else "❌"
                print(f"  {status} {perm['permission']}")
        else:
            print(f"❌ Não foi possível verificar permissões: {perm_response.json()}")
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {str(e)}")

def complete_verification(phone_number_id: str, verification_code: str):
    """Complete phone verification with SMS code"""
    access_token = get_access_token()
    if not access_token:
        print("❌ ERRO: Token não encontrado")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"🔐 Completando verificação do Phone ID: {phone_number_id}")
    print(f"📱 Código SMS: {verification_code}")
    
    try:
        url = f"https://graph.facebook.com/v23.0/{phone_number_id}/verify_code"
        payload = {
            "code": verification_code
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            if result.get('success'):
                print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
                print("O telefone +1 831 283 1347 está agora totalmente verificado e ativo")
                
                # Check final status
                status_response = requests.get(
                    f"https://graph.facebook.com/v23.0/{phone_number_id}",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Status final: {status_data.get('code_verification_status', 'N/A')}")
                    print(f"Quality Rating: {status_data.get('quality_rating', 'N/A')}")
                    print(f"Display Name: {status_data.get('verified_name', 'N/A')}")
                
                return True
            else:
                print(f"❌ Verificação falhou: {result}")
                return False
        else:
            error_msg = result.get('error', {}).get('message', 'Erro desconhecido')
            print(f"❌ Erro na verificação: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção durante verificação: {str(e)}")
        return False

def check_phone_status(phone_number_id: str = "708355979030805"):
    """Check current status of registered phone"""
    access_token = get_access_token()
    if not access_token:
        print("❌ ERRO: Token não encontrado")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"https://graph.facebook.com/v23.0/{phone_number_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("=== STATUS ATUAL DO TELEFONE ===")
            print(f"Phone Number ID: {phone_number_id}")
            print(f"Display Phone: {data.get('display_phone_number', 'N/A')}")
            print(f"Verified Name: {data.get('verified_name', 'N/A')}")
            print(f"Code Verification: {data.get('code_verification_status', 'N/A')}")
            print(f"Quality Rating: {data.get('quality_rating', 'N/A')}")
            
            status = data.get('code_verification_status', 'UNKNOWN')
            if status == 'NOT_VERIFIED':
                print("\n⏳ Aguardando verificação por SMS")
                print("Use: python3 register_phone_whatsapp.py verify <CÓDIGO_SMS>")
            elif status == 'VERIFIED':
                print("\n✅ Telefone completamente verificado e pronto para uso!")
            else:
                print(f"\n📋 Status: {status}")
                
        else:
            error = response.json()
            print(f"❌ Erro ao verificar status: {error.get('error', {}).get('message', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "verify" and len(sys.argv) > 2:
            # Complete verification with SMS code
            sms_code = sys.argv[2]
            complete_verification("708355979030805", sms_code)
            
        elif command == "status":
            # Check current status
            check_phone_status()
            
        else:
            print("Uso:")
            print("  python3 register_phone_whatsapp.py verify <CÓDIGO_SMS>")
            print("  python3 register_phone_whatsapp.py status")
    else:
        print("🚀 INICIANDO REGISTRO DO TELEFONE WHATSAPP")
        print("=" * 50)
        
        # Test current setup first
        test_current_setup()
        
        print("\n" + "=" * 50)
        
        # Try to register phone
        result = register_phone_number()
        
        if result:
            print(f"\n🎉 TELEFONE REGISTRADO COM SUCESSO!")
            print(f"Phone Number ID: {result}")
            print("\n📱 PRÓXIMO PASSO:")
            print("Aguarde receber o SMS no telefone +1 831 283 1347")
            print("Depois execute: python3 register_phone_whatsapp.py verify <CÓDIGO_SMS>")
        else:
            print(f"\n⚠️  REGISTRO NÃO COMPLETADO VIA API")
            print("Verifique os próximos passos manuais listados acima.")