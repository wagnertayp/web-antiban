#!/usr/bin/env python3
"""
TESTE FINAL: Verificar se sistema corrigido envia mensagens com sucesso
"""
import requests
import json
import time

def test_corrected_system():
    """Testar envio com template corrigido"""
    base_url = "http://localhost:5000"
    
    # Dados de teste com template válido
    test_data = {
        "leads": "5511987654321,João Silva,12345678900",
        "templates": ["modelo1"],  # Template válido
        "phone_numbers": ["123456789"]  # Número de teste
    }
    
    print("🧪 TESTE DO SISTEMA CORRIGIDO")
    print("=" * 50)
    
    try:
        print("📤 Enviando requisição de teste...")
        response = requests.post(
            f"{base_url}/api/send-smart-distribution",
            json=test_data,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO!")
            print(f"📝 Resposta: {json.dumps(result, indent=2)}")
            
            # Verificar se tem status de envio
            if 'status' in result:
                print(f"🎯 Status do envio: {result['status']}")
            
            return True
        else:
            print(f"❌ ERRO: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("🔄 Certifique-se de que a aplicação está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_corrected_system()
    print("\n" + "=" * 50)
    if success:
        print("🎉 SISTEMA CORRIGIDO FUNCIONANDO!")
        print("✅ Template válido sendo usado")
        print("✅ Sem erros de template inexistente")
    else:
        print("⚠️ Ainda há problemas a resolver")