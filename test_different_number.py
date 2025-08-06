#!/usr/bin/env python3
"""
Teste com número diferente para verificar entrega
"""

import requests
import time

def test_with_different_number():
    """Testa com número diferente"""
    
    access_token = "EAAKYElksPsEBPN6szHJFCl6WsxZBW2kHnqve8RLTOUCyKS99j0UCZAOslWZCGbTXZA4k0QFeZBJ3cNBKnuqDGfJxlNNld2Rz7Cm0863RzMRJBk7HkwuvbZA7TSAy30OlGjQHpRihPCCzyMuGaVoombue544bCEC9bhv12wFu3K8fbiSPkWjvrGWGe5z8vQQyvKuPZBonZAGwyslwlqGbIpwosTcYKtupJ6LXDzHneXyv8oaQpUkPHDgecYmeWDMRHLIZD"
    
    phone_id = "743171782208180"
    api_version = "v22.0"
    base_url = f"https://graph.facebook.com/{api_version}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Lista de números para testar
    test_numbers = [
        "+5573999084689",  # Número que funcionou anteriormente
        "+5561982132603",  # Outro número teste
        "+5511999999999",  # Número genérico
    ]
    
    print("🧪 TESTANDO ENTREGA COM NÚMEROS DIFERENTES...")
    
    for i, number in enumerate(test_numbers, 1):
        print(f"\n{i}️⃣ Testando {number}...")
        
        message_payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {
                "body": f"🧪 TESTE {i} - Mensagem para {number}\n\nTeste de entrega BM Jose Carlos\nTimestamp: {int(time.time())}"
            }
        }
        
        try:
            send_response = requests.post(
                f"{base_url}/{phone_id}/messages",
                headers=headers,
                json=message_payload,
                timeout=15
            )
            
            print(f"   Status: {send_response.status_code}")
            print(f"   Response: {send_response.text}")
            
            if send_response.status_code == 200:
                response_data = send_response.json()
                message_id = response_data.get('messages', [{}])[0].get('id')
                print(f"   ✅ Message ID: {message_id}")
            else:
                print(f"   ❌ Erro: {send_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Aguardar entre testes
        time.sleep(2)
    
    # Teste com o próprio número do sistema (se possível)
    print(f"\n🔄 Testando com número do próprio sistema...")
    
    own_number = "+19798672216"  # Número do phone ID usado
    
    self_message_payload = {
        "messaging_product": "whatsapp",
        "to": own_number,
        "type": "text",
        "text": {
            "body": "🔄 AUTO-TESTE: Mensagem para o próprio número do sistema"
        }
    }
    
    try:
        self_response = requests.post(
            f"{base_url}/{phone_id}/messages",
            headers=headers,
            json=self_message_payload,
            timeout=15
        )
        
        print(f"   Status: {self_response.status_code}")
        print(f"   Response: {self_response.text}")
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_with_different_number()