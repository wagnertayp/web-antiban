#!/usr/bin/env python3
"""
Forçar atualização do token no sistema
"""
import os
import sys

def force_update_token():
    """Forçar atualização do token"""
    
    new_token = "EAAKrs5Jx6qgBPfeaK7WytbhiewOmUJFMWo0WrFyqpXngb2St5btTZAJY3MZAGcWvQ0y00rIs95m0PBdAkfa0q5ZAPsOjEhqGcB7FPxDCfyZAuai0IAqMTCkNtZCJA8h1zfZCNV4H6YEZCNbx6rZBvMyZCaNvl5sAPhH8Jq1rwvVXumOZA53OHvEqz8k5OrHIqUGZBDCwieOZBFtJOSxijuJHIJPmL2uSFktI4rfDJ51MSNOAywZDZD"
    
    print("🔄 FORÇANDO ATUALIZAÇÃO DO TOKEN")
    print("=" * 50)
    print(f"🔑 Novo token: {new_token[:20]}...")
    
    # Forçar atualização da variável de ambiente
    os.environ['WHATSAPP_ACCESS_TOKEN'] = new_token
    
    # Importar e forçar reset do sistema WhatsApp
    try:
        from services.whatsapp_business_api import whatsapp_api
        
        # Forçar reset completo
        whatsapp_api._access_token = new_token
        whatsapp_api._phone_number_id = None
        whatsapp_api._business_account_id = None
        whatsapp_api._available_phones = []
        
        # Forçar reconfiguração
        whatsapp_api.update_token(new_token)
        
        print("✅ Token forçadamente atualizado no sistema")
        print(f"🔍 Token configurado: {new_token[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao forçar atualização: {e}")
        return False

if __name__ == "__main__":
    success = force_update_token()
    if success:
        print("\n✅ TOKEN ATUALIZADO COM SUCESSO!")
        print("🚀 Sistema pronto para usar o novo token")
    else:
        print("\n❌ Falha na atualização do token")