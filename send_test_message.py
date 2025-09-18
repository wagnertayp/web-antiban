#!/usr/bin/env python3
"""
Enviar mensagem de teste para o número do usuário
"""
import requests
import json
import os

def send_test_message():
    """Enviar mensagem de teste usando o sistema corrigido"""
    
    # Novo token fornecido pelo usuário
    new_token = "EAAKrs5Jx6qgBPTPJbOYU408mal45OAe52ZCQHTs8XDjhyNogP7ChZCUv5bFuVGNQtwpW6DAkW934ZBySZCCcmOXTSXdJZATWIF0CYLhVsWws4kgJnZBZCJ9zOJKtetuYQeP9zRivOjysRJIeJ5r4j8XUH3RH74TLRj1ZAbLCnfAOsTaeQAuzGNE3f8TO0mGxcUVgRbyHfJ3O08E3D5VHoV3HtNm0lWhi3eQItuX2ZC2CTlwZDZD"
    
    # Definir o token como variável de ambiente temporariamente
    os.environ['WHATSAPP_ACCESS_TOKEN'] = new_token
    
    base_url = "http://localhost:5000"
    
    # Dados para envio - número do usuário + template solicitado
    test_data = {
        "leads": "5561999114066,Usuário Teste,00000000000",  # Número do usuário
        "templates": ["modelo432"],  # Template solicitado pelo usuário
        "phone_numbers": ["123456789"]  # Placeholder para phone number
    }
    
    print("📱 ENVIANDO MENSAGEM DE TESTE")
    print("=" * 50)
    print(f"📞 Número: +55 61 99911-4066")
    print(f"📋 Template: modelo432 (conforme solicitado)")
    print(f"🔑 Token: {new_token[:20]}...")
    
    try:
        print("\n📤 Enviando requisição...")
        response = requests.post(
            f"{base_url}/api/send-smart-distribution",
            json=test_data,
            timeout=15
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ REQUISIÇÃO ENVIADA COM SUCESSO!")
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ ERRO HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = send_test_message()
    print("\n" + "=" * 50)
    if success:
        print("🎉 MENSAGEM ENVIADA!")
        print("📱 Verifique seu WhatsApp em alguns segundos")
    else:
        print("⚠️ Houve algum problema no envio")