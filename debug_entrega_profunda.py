#!/usr/bin/env python3
"""
Investigação profunda do problema de entrega
"""

import os
import requests
import time

def debug_entrega_profunda():
    """Debug deep delivery issues"""
    
    print(f"🔍 INVESTIGAÇÃO PROFUNDA - PROBLEMA DE ENTREGA")
    print("=" * 60)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # 1. Verificar status da Business Manager
    print(f"\n1️⃣ VERIFICANDO STATUS DA BUSINESS MANAGER")
    bm_url = f"https://graph.facebook.com/v22.0/2089992404820473"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(bm_url, headers=headers)
        if response.status_code == 200:
            bm_data = response.json()
            print(f"✅ BM Nome: {bm_data.get('name')}")
            print(f"✅ BM ID: {bm_data.get('id')}")
        else:
            print(f"❌ BM Error: {response.text}")
    except Exception as e:
        print(f"❌ BM Exception: {e}")
    
    # 2. Verificar quality rating dos phones
    print(f"\n2️⃣ VERIFICANDO QUALITY RATING DOS PHONES")
    
    phones = [
        ("776788602173980", "GREEN"),
        ("725492557312328", "RED")
    ]
    
    for phone_id, expected_quality in phones:
        phone_url = f"https://graph.facebook.com/v22.0/{phone_id}"
        try:
            response = requests.get(phone_url, headers=headers)
            if response.status_code == 200:
                phone_data = response.json()
                display_name = phone_data.get('display_phone_number', 'N/A')
                quality = phone_data.get('quality_rating', 'N/A')
                status = phone_data.get('account_mode', 'N/A')
                verified = phone_data.get('verified_name', 'N/A')
                
                print(f"📱 Phone {phone_id}:")
                print(f"   Display: {display_name}")
                print(f"   Quality: {quality}")
                print(f"   Status: {status}")
                print(f"   Verified: {verified}")
                
                # Verificar messaging limits
                msg_url = f"https://graph.facebook.com/v22.0/{phone_id}/message_templates"
                msg_response = requests.get(msg_url, headers=headers)
                if msg_response.status_code == 200:
                    templates = msg_response.json().get('data', [])
                    print(f"   Templates: {len(templates)} disponíveis")
                else:
                    print(f"   Templates: ERRO {msg_response.status_code}")
                    
        except Exception as e:
            print(f"❌ Phone {phone_id} Exception: {e}")
    
    # 3. Verificar status do template específico
    print(f"\n3️⃣ VERIFICANDO TEMPLATE ESPECÍFICO")
    template_url = f"https://graph.facebook.com/v22.0/2089992404820473/message_templates"
    
    try:
        response = requests.get(template_url, headers=headers)
        if response.status_code == 200:
            templates = response.json().get('data', [])
            ricardo_template = None
            
            for template in templates:
                if template.get('name') == 'ricardo_template_1753487909_d79bcb95':
                    ricardo_template = template
                    break
            
            if ricardo_template:
                print(f"✅ Template encontrado:")
                print(f"   Nome: {ricardo_template.get('name')}")
                print(f"   Status: {ricardo_template.get('status')}")
                print(f"   Language: {ricardo_template.get('language')}")
                print(f"   Category: {ricardo_template.get('category')}")
                
                # Verificar se está pausado
                if ricardo_template.get('status') != 'APPROVED':
                    print(f"⚠️  PROBLEMA: Template não está APPROVED!")
                    print(f"   Status atual: {ricardo_template.get('status')}")
                    
            else:
                print(f"❌ Template ricardo_template_1753487909_d79bcb95 NÃO ENCONTRADO!")
                print(f"Templates disponíveis:")
                for template in templates[:5]:
                    print(f"   - {template.get('name')} ({template.get('status')})")
                    
    except Exception as e:
        print(f"❌ Template Exception: {e}")
    
    # 4. Teste com número internacional conhecido
    print(f"\n4️⃣ TESTE COM NÚMERO INTERNACIONAL")
    phone_id = "776788602173980"  # GREEN phone
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': '15551234567',  # Número teste US
        'type': 'template',
        'template': {
            'name': 'hello_world',  # Template padrão
            'language': {'code': 'en_US'}
        }
    }
    
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📞 Teste hello_world para +15551234567:")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   Message ID: {message_id}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Teste internacional Exception: {e}")
    
    # 5. Verificar webhook/delivery status
    print(f"\n5️⃣ VERIFICANDO WEBHOOKS")
    webhook_url = f"https://graph.facebook.com/v22.0/2089992404820473/subscribed_apps"
    
    try:
        response = requests.get(webhook_url, headers=headers)
        if response.status_code == 200:
            apps = response.json().get('data', [])
            print(f"✅ Apps suscritas: {len(apps)}")
            for app in apps:
                print(f"   - {app.get('name', 'N/A')}")
        else:
            print(f"❌ Webhook Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook Exception: {e}")
    
    print(f"\n🎯 DIAGNÓSTICO COMPLETO")
    print(f"Se todos os status estão OK mas mensagens não chegam:")
    print(f"1. Token pode ser SANDBOX (só funciona para números test)")
    print(f"2. Business Manager pode ter restrições da Meta")
    print(f"3. Phone numbers podem estar em review/paused")
    print(f"4. Template pode estar pausado por quality issues")
    print(f"5. Número destinatário pode estar em blacklist")

if __name__ == "__main__":
    debug_entrega_profunda()