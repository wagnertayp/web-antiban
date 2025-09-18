#!/usr/bin/env python3
"""
Enviar template modelo432 através do sistema web com novo token
"""
import requests
import json
import os

def update_and_send():
    """Atualizar token e enviar mensagem"""
    
    # Novo token fornecido pelo usuário
    new_token = "EAAKrs5Jx6qgBPQDDZAtl1tdpFsZB0MGcJZAK3FbjwzqqgN89bFtJlV50ScTkZCwnYsZBkoTy35nkCqFc3tgeAh6KMpSd4eySftGrGnmo6rXrnUdZAMDX53NJwiZAyJGecAlf0aoxS5wwjpOuaCC2CA7Wwa9g7uuTPWogNAcyohI3a5xy8ipBZBaE4yZA1DYGutcbZCcMo8abQ41I1Q08Iw5TWPZBKIlU3oZC2mMdwB1dXluitQZDZD"
    
    # Atualizar variável de ambiente
    os.environ['WHATSAPP_ACCESS_TOKEN'] = new_token
    
    base_url = "http://localhost:5000"
    
    # Dados para envio com template modelo432
    send_data = {
        "leads": "5561999114066,Usuário Teste,00000000000",
        "templates": ["modelo432"],  # Template específico solicitado
        "phone_numbers": ["123456789"]  # Usar configuração do sistema
    }
    
    print("📱 ENVIANDO TEMPLATE modelo432 VIA SISTEMA WEB")
    print("=" * 50)
    print(f"📞 Para: +55 61 99911-4066")
    print(f"📋 Template: modelo432 (conforme solicitado)")
    print(f"🔑 Token atualizado: {new_token[:20]}...")
    
    try:
        print("\n📤 Enviando através do sistema web...")
        response = requests.post(
            f"{base_url}/api/send-smart-distribution",
            json=send_data,
            timeout=20
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ REQUISIÇÃO PROCESSADA COM SUCESSO!")
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
        print("❌ Não foi possível conectar ao servidor web")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = update_and_send()
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEMPLATE modelo432 PROCESSADO!")
        print("📱 Verificando logs para confirmar envio...")
    else:
        print("⚠️ Falha no processamento")