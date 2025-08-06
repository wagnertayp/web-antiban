#!/usr/bin/env python3
"""
Investigação de limitações específicas da conta
"""

import os
import requests

def debug_limitacoes_conta():
    """Debug account specific limitations"""
    
    print(f"🔍 INVESTIGAÇÃO DE LIMITAÇÕES DA CONTA")
    print("=" * 60)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Verificar status detalhado da Business Manager
    print(f"\n1️⃣ STATUS DETALHADO DA BUSINESS MANAGER")
    
    bm_url = f"https://graph.facebook.com/v22.0/2089992404820473"
    
    try:
        response = requests.get(bm_url, headers=headers)
        if response.status_code == 200:
            bm_data = response.json()
            print(f"✅ Nome: {bm_data.get('name')}")
            print(f"✅ Moeda: {bm_data.get('currency')}")
            print(f"✅ Timezone: {bm_data.get('timezone_id')}")
            
            # Verificar se há campos indicando restrições
            for key, value in bm_data.items():
                if 'restrict' in key.lower() or 'limit' in key.lower() or 'disable' in key.lower():
                    print(f"⚠️  {key}: {value}")
                    
    except Exception as e:
        print(f"❌ Erro BM: {e}")
    
    # 2. Verificar messaging limits dos phone numbers
    print(f"\n2️⃣ VERIFICANDO MESSAGING LIMITS")
    
    phones = [
        ("776788602173980", "+1 424-461-1446", "GREEN"),
        ("725492557312328", "15558068378", "RED")
    ]
    
    for phone_id, display, quality in phones:
        print(f"\n📱 Phone {phone_id} ({display}) - Quality: {quality}")
        
        # Get detailed phone info
        phone_url = f"https://graph.facebook.com/v22.0/{phone_id}"
        
        try:
            response = requests.get(phone_url, headers=headers)
            if response.status_code == 200:
                phone_data = response.json()
                
                # Verificar todos os campos relacionados a limites
                important_fields = [
                    'quality_rating', 'account_mode', 'status', 'verified_name',
                    'messaging_limit_tier', 'max_daily_conversation_per_phone',
                    'current_limit', 'throughput', 'name_status'
                ]
                
                for field in important_fields:
                    if field in phone_data:
                        value = phone_data[field]
                        print(f"   {field}: {value}")
                
                # Verificar se há indicadores de sandbox/development
                if 'sandbox' in str(phone_data).lower():
                    print(f"   🚨 SANDBOX MODE DETECTADO!")
                    
                if 'development' in str(phone_data).lower():
                    print(f"   🚨 DEVELOPMENT MODE DETECTADO!")
                    
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # 3. Verificar permissões específicas do token
    print(f"\n3️⃣ VERIFICANDO PERMISSÕES DO TOKEN")
    
    # Get app permissions
    app_url = f"https://graph.facebook.com/v22.0/me/permissions"
    
    try:
        response = requests.get(app_url, headers=headers)
        if response.status_code == 200:
            permissions = response.json().get('data', [])
            
            whatsapp_perms = []
            for perm in permissions:
                permission = perm.get('permission', '')
                status = perm.get('status', '')
                
                if 'whatsapp' in permission.lower() or 'business' in permission.lower():
                    whatsapp_perms.append(f"{permission}: {status}")
            
            if whatsapp_perms:
                print(f"✅ Permissões WhatsApp:")
                for perm in whatsapp_perms:
                    print(f"   - {perm}")
            else:
                print(f"❌ PROBLEMA: Nenhuma permissão WhatsApp encontrada!")
                
        else:
            print(f"❌ Erro permissões: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro permissões: {e}")
    
    # 4. Teste com webhook verification
    print(f"\n4️⃣ VERIFICANDO DELIVERY WEBHOOKS")
    
    webhook_url = f"https://graph.facebook.com/v22.0/2089992404820473/subscribed_apps"
    
    try:
        response = requests.get(webhook_url, headers=headers)
        if response.status_code == 200:
            apps = response.json().get('data', [])
            print(f"✅ Apps configuradas: {len(apps)}")
            
            for app in apps:
                app_id = app.get('id', 'N/A')
                print(f"   App ID: {app_id}")
                
                # Verificar subscriptions específicas
                sub_url = f"https://graph.facebook.com/v22.0/{app_id}/subscriptions"
                try:
                    sub_response = requests.get(sub_url, headers=headers)
                    if sub_response.status_code == 200:
                        subs = sub_response.json().get('data', [])
                        for sub in subs:
                            print(f"   - Objeto: {sub.get('object')}")
                            print(f"   - Campos: {sub.get('fields', [])}")
                except:
                    pass
                    
    except Exception as e:
        print(f"❌ Erro webhook: {e}")
    
    # 5. Teste final com delivery status check
    print(f"\n5️⃣ TESTE COM VERIFICAÇÃO DE STATUS")
    
    # Send a message and try to check its status
    phone_id = "776788602173980"
    message_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': '5573999084689',
        'type': 'text',
        'text': {
            'body': 'TESTE FINAL - Verificação de delivery status'
        }
    }
    
    try:
        response = requests.post(message_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', None)
            
            if message_id:
                print(f"✅ Mensagem enviada: {message_id}")
                
                # Try to get message status (may not be available immediately)
                import time
                time.sleep(2)
                
                status_url = f"https://graph.facebook.com/v22.0/{message_id}"
                try:
                    status_response = requests.get(status_url, headers=headers)
                    print(f"📊 Status check: {status_response.status_code}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"📋 Status data: {status_data}")
                except:
                    print(f"ℹ️  Status não disponível (normal)")
                    
        else:
            print(f"❌ Erro envio: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro teste: {e}")
    
    print(f"\n🎯 DIAGNÓSTICO FINAL")
    print(f"POSSÍVEIS CAUSAS DA NÃO ENTREGA:")
    print(f"1. 🔒 CONTA EM SANDBOX - limitada a números específicos")
    print(f"2. 🚫 RESTRIÇÕES DA META - conta nova/em revisão")
    print(f"3. 📱 PHONE NUMBERS não aprovados para produção")
    print(f"4. 🔑 TOKEN sem permissões de envio real")
    print(f"5. 🌍 LIMITAÇÕES GEOGRÁFICAS - números brasileiros bloqueados")
    print(f"6. ⏱️  DELAY SEVERO - mensagens podem chegar em horas")

if __name__ == "__main__":
    debug_limitacoes_conta()