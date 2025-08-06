#!/usr/bin/env python3
"""
Adicionar número do usuário como número de teste
"""

import os
import requests

def adicionar_numero_teste():
    """Add user number as test number"""
    
    print(f"🔧 ADICIONANDO SEU NÚMERO COMO TESTE")
    print("=" * 50)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = "776788602173980"  # GREEN phone
    
    # 1. Primeiro verificar números de teste existentes
    print(f"\n1️⃣ VERIFICANDO NÚMEROS DE TESTE ATUAIS")
    
    test_url = f"https://graph.facebook.com/v22.0/{phone_id}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone configurado: {data.get('display_phone_number')}")
            print(f"✅ Quality: {data.get('quality_rating')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Tentar adicionar o número como teste (método 1)
    print(f"\n2️⃣ TENTANDO ADICIONAR +5573999084689 COMO NÚMERO DE TESTE")
    
    # Endpoint para adicionar número de teste
    register_url = f"https://graph.facebook.com/v22.0/{phone_id}/register"
    
    payload = {
        'messaging_product': 'whatsapp',
        'pin': '123456'  # PIN padrão para teste
    }
    
    try:
        response = requests.post(register_url, json=payload, headers=headers)
        print(f"📞 Register status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Registro iniciado")
        else:
            print(f"❌ Register error: {response.text}")
            
    except Exception as e:
        print(f"❌ Register exception: {e}")
    
    # 3. Teste direto com mensagem para verificar se agora funciona
    print(f"\n3️⃣ TESTE APÓS CONFIGURAÇÃO")
    
    message_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    # Teste com texto simples primeiro
    payload = {
        'messaging_product': 'whatsapp',
        'to': '5573999084689',  # Sem +
        'type': 'text',
        'text': {
            'body': 'TESTE APÓS CONFIGURAÇÃO - Esta mensagem deve chegar agora!'
        }
    }
    
    try:
        response = requests.post(message_url, json=payload, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            contacts = data.get('contacts', [])
            messages = data.get('messages', [])
            
            if contacts:
                contact = contacts[0]
                wa_id = contact.get('wa_id', 'N/A')
                print(f"📞 WhatsApp ID: {wa_id}")
                
            if messages:
                message = messages[0]
                message_id = message.get('id', 'N/A')
                print(f"✉️  Message ID: {message_id}")
                print(f"🎯 CONFIGURAÇÃO COMPLETA!")
                print(f"📱 Agora verifique seu WhatsApp 73999084689")
                
                return message_id
                
        else:
            print(f"❌ ERRO: {response.text}")
            
            # Se ainda não funcionar, vamos tentar outros métodos
            print(f"\n4️⃣ MÉTODO ALTERNATIVO - WEBHOOK CONFIGURATION")
            
            webhook_url = f"https://graph.facebook.com/v22.0/2089992404820473/subscribed_apps"
            
            try:
                webhook_response = requests.post(webhook_url, headers=headers)
                print(f"Webhook status: {webhook_response.status_code}")
                
            except Exception as e:
                print(f"Webhook error: {e}")
                
    except Exception as e:
        print(f"❌ Erro na mensagem: {e}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS SE AINDA NÃO FUNCIONAR:")
    print(f"1. Conta pode estar em SANDBOX mode")
    print(f"2. Necessário aprovação da Meta para produção")
    print(f"3. Seu número precisa ser adicionado manualmente no Business Manager")
    print(f"4. Token pode precisar de permissões adicionais")

if __name__ == "__main__":
    adicionar_numero_teste()