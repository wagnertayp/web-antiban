#!/usr/bin/env python3
"""
Atualizar o token do sistema
"""
import requests
import json

def update_token():
    """Atualizar token no sistema"""
    
    new_token = "EAAKrs5Jx6qgBPTPJbOYU408mal45OAe52ZCQHTs8XDjhyNogP7ChZCUv5bFuVGNQtwpW6DAkW934ZBySZCCcmOXTSXdJZATWIF0CYLhVsWws4kgJnZBZCJ9zOJKtetuYQeP9zRivOjysRJIeJ5r4j8XUH3RH74TLRj1ZAbLCnfAOsTaeQAuzGNE3f8TO0mGxcUVgRbyHfJ3O08E3D5VHoV3HtNm0lWhi3eQItuX2ZC2CTlwZDZD"
    
    base_url = "http://localhost:5000"
    
    print("🔑 ATUALIZANDO TOKEN DO SISTEMA")
    print("=" * 50)
    print(f"🔑 Novo token: {new_token[:20]}...")
    
    try:
        # Teste de conexão com o novo token
        update_data = {
            "token": new_token,
            "action": "update_token"
        }
        
        print("\n📤 Enviando atualização...")
        response = requests.post(
            f"{base_url}/api/update-connection",
            json=update_data,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ TOKEN ATUALIZADO!")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    update_token()