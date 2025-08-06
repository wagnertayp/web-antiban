#!/usr/bin/env python3

def test_modelo2_button():
    """Test modelo2 with exact button structure"""
    
    import requests
    import json
    import os
    
    print("🎯 MODELO2 - ESTRUTURA EXATA DO TEMPLATE APROVADO")
    print("=" * 55)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Dados exatos do exemplo do template
    cpf = "065.370.801-77"  # {{1}}
    nome = "Pedro Lima"     # {{2}}
    
    print(f"Template: modelo2")
    print(f"Header: 'Notificação Extrajudicial' (FIXO)")
    print(f"Body param 1: {cpf} (CPF)")
    print(f"Body param 2: {nome} (Nome)")
    print(f"Footer: 'PROCESSO Nº: 0009-13.2025.0100-NE' (FIXO)")
    print(f"Button URL: https://www.intimacao.org/{cpf}")
    print()
    
    # ESTRUTURA CORRETA - Header + Body + Footer + Buttons
    # Header e Footer são FIXOS (sem parâmetros)
    # Body tem 2 parâmetros: {{1}} = CPF, {{2}} = Nome
    # Button tem 1 parâmetro para URL: {{1}} = CPF
    
    correct_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "template",
        "template": {
            "name": "modelo2",
            "language": {"code": "en"},
            "components": [
                # Header é FIXO - não precisa de parâmetros
                # O WhatsApp já sabe que é "Notificação Extrajudicial"
                
                # Body com os 2 parâmetros obrigatórios
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": cpf},   # {{1}} = CPF
                        {"type": "text", "text": nome}   # {{2}} = Nome
                    ]
                },
                
                # Footer é FIXO - não precisa de parâmetros
                # O WhatsApp já sabe que é "PROCESSO Nº: 0009-13.2025.0100-NE"
                
                # Button com parâmetro para URL
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": cpf}    # {{1}} para URL
                    ]
                }
            ]
        }
    }
    
    print("PAYLOAD CORRETO:")
    print(json.dumps(correct_payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        print("Enviando template modelo2...")
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=correct_payload,
            timeout=15
        )
        
        print(f"STATUS: {response.status_code}")
        response_data = response.json()
        print(f"RESPONSE: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            message_id = response_data.get('messages', [{}])[0].get('id')
            contacts = response_data.get('contacts', [])
            
            print(f"\n✅ SUCESSO! TEMPLATE MODELO2 ENVIADO!")
            print(f"   Message ID: {message_id}")
            if contacts:
                wa_id = contacts[0].get('wa_id')
                print(f"   WhatsApp ID: {wa_id}")
            print(f"   URL gerada: https://www.intimacao.org/{cpf}")
            print("\n🔔 VERIFIQUE SEU WHATSAPP AGORA!")
            print("   A mensagem deve aparecer com:")
            print("   - Header: 'Notificação Extrajudicial'")
            print(f"   - Texto personalizado com CPF {cpf} e nome {nome}")
            print("   - Footer: 'PROCESSO Nº: 0009-13.2025.0100-NE'")
            print("   - Botão: 'Regularizar meu CPF'")
            
            return True
            
        else:
            error = response_data.get('error', {})
            error_code = error.get('code')
            error_message = error.get('message')
            
            print(f"\n❌ FALHOU:")
            print(f"   Código: {error_code}")
            print(f"   Mensagem: {error_message}")
            
            if error_code == 135000:
                print("\n💡 ANÁLISE DO ERRO 135000:")
                print("   - Template aprovado mas com problema de uso")
                print("   - Pode ser limitação temporária de URL buttons")
                print("   - Conta está verde mas templates com botões falham")
                
    except Exception as e:
        print(f"\n❌ ERRO DE CONEXÃO: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_modelo2_button()