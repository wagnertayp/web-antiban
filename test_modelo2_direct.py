#!/usr/bin/env python3

def test_modelo2_direct():
    """Test modelo2 template directly"""
    
    import requests
    import json
    import os
    
    print("🎯 ENVIANDO CONTEÚDO EXATO DO TEMPLATE MODELO2")
    print("=" * 50)
    
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = "674928665709899"
    test_number = "+5573999084689"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Dados do lead
    cpf = "065.370.801-77"
    nome = "Pedro Lima"
    
    # CONTEÚDO EXATO DO TEMPLATE MODELO2 APROVADO
    # Replicando exatamente a estrutura do template como texto
    
    template_content = f"""*Notificação Extrajudicial*

Prezado (a) {nome}, me chamo Damião Alves Vaz. Sou tabelião do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{cpf}.*

Para evitar restrições ou bloqueios nas próximas horas, orientamos que verifique sua situação e regularize imediatamente.

Atenciosamente,  
Cartório 5º Ofício de Notas

PROCESSO Nº: 0009-13.2025.0100-NE

🔗 Regularizar meu CPF: https://www.intimacao.org/{cpf}"""
    
    print("CONTEÚDO DA MENSAGEM:")
    print("-" * 30)
    print(template_content)
    print("-" * 30)
    print()
    
    # Payload para mensagem de texto com conteúdo do template
    text_payload = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "text",
        "text": {
            "body": template_content
        }
    }
    
    print("PAYLOAD:")
    print(json.dumps(text_payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        print("Enviando mensagem com conteúdo do template modelo2...")
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            headers=headers,
            json=text_payload,
            timeout=15
        )
        
        print(f"STATUS: {response.status_code}")
        response_data = response.json()
        print(f"RESPONSE: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            message_id = response_data.get('messages', [{}])[0].get('id')
            contacts = response_data.get('contacts', [])
            
            print(f"\n✅ SUCESSO! MENSAGEM MODELO2 ENVIADA!")
            print(f"   Message ID: {message_id}")
            if contacts:
                wa_id = contacts[0].get('wa_id')
                print(f"   WhatsApp ID: {wa_id}")
            print(f"   URL: https://www.intimacao.org/{cpf}")
            print("\n🔔 VERIFIQUE SEU WHATSAPP AGORA!")
            print("   A mensagem contém:")
            print("   ✓ Header: 'Notificação Extrajudicial'")
            print(f"   ✓ CPF personalizado: {cpf}")
            print(f"   ✓ Nome personalizado: {nome}")
            print("   ✓ Footer: 'PROCESSO Nº: 0009-13.2025.0100-NE'")
            print("   ✓ Link para regularização")
            print("\n📋 CONTEÚDO IDÊNTICO AO TEMPLATE APROVADO!")
            
            return True
            
        else:
            error = response_data.get('error', {})
            print(f"\n❌ FALHOU:")
            print(f"   Código: {error.get('code')}")
            print(f"   Mensagem: {error.get('message')}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_modelo2_direct()