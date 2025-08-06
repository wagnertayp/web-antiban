#!/usr/bin/env python3
"""
Debug real do token e Business Manager
"""

import os
import requests

def debug_token_reality():
    """Debug real token permissions"""
    
    print(f"🔍 INVESTIGAÇÃO PROFUNDA DO TOKEN")
    print("=" * 60)
    
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print(f"❌ Token não encontrado")
        return
        
    print(f"🔑 Token: {token[:50]}...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Check token validity
    print(f"\n1️⃣ VERIFICANDO VALIDADE DO TOKEN")
    try:
        url = "https://graph.facebook.com/v22.0/me"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido - ID: {data.get('id', 'N/A')}")
            print(f"📱 Nome: {data.get('name', 'N/A')}")
        else:
            print(f"❌ Token inválido: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erro verificando token: {e}")
        return
    
    # 2. Check Business Manager permissions
    print(f"\n2️⃣ VERIFICANDO PERMISSÕES DA BUSINESS MANAGER")
    
    bm_id = "2089992404820473"
    try:
        # Try to access BM directly
        bm_url = f"https://graph.facebook.com/v22.0/{bm_id}"
        bm_response = requests.get(bm_url, headers=headers, timeout=10)
        
        print(f"📊 BM Status: {bm_response.status_code}")
        print(f"📋 BM Response: {bm_response.text}")
        
        if bm_response.status_code == 200:
            bm_data = bm_response.json()
            print(f"✅ BM acessível: {bm_data.get('name', 'N/A')}")
        else:
            print(f"⚠️  BM não acessível diretamente")
            
    except Exception as e:
        print(f"❌ Erro acessando BM: {e}")
    
    # 3. Check phone permissions specifically
    print(f"\n3️⃣ VERIFICANDO PERMISSÕES DOS PHONE NUMBERS")
    
    test_phones = ["776788602173980", "725492557312328"]  # GREEN e RED
    
    for phone_id in test_phones:
        print(f"\n📱 TESTANDO PHONE: {phone_id}")
        
        try:
            # Check if we can access phone info
            phone_url = f"https://graph.facebook.com/v22.0/{phone_id}"
            phone_response = requests.get(phone_url, headers=headers, timeout=10)
            
            print(f"   Status: {phone_response.status_code}")
            
            if phone_response.status_code == 200:
                phone_data = phone_response.json()
                print(f"   ✅ Phone acessível: {phone_data.get('display_phone_number', 'N/A')}")
                print(f"   📊 Quality: {phone_data.get('quality_rating', 'N/A')}")
                print(f"   📈 Status: {phone_data.get('status', 'N/A')}")
                
                # Check messaging permissions
                messaging_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
                
                # Try a minimal test message (this might fail but shows permissions)
                test_payload = {
                    'messaging_product': 'whatsapp',
                    'to': '+5561999114066',
                    'type': 'text',
                    'text': {'body': 'Test permission'}
                }
                
                msg_response = requests.post(messaging_url, json=test_payload, headers=headers, timeout=10)
                print(f"   📤 Message endpoint: {msg_response.status_code}")
                
                if msg_response.status_code == 200:
                    print(f"   ✅ Permissão de envio OK")
                else:
                    print(f"   ❌ Sem permissão de envio: {msg_response.text}")
                    
            else:
                print(f"   ❌ Phone não acessível: {phone_response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro testando phone: {e}")
    
    # 4. Check template permissions
    print(f"\n4️⃣ VERIFICANDO TEMPLATE NA BUSINESS MANAGER")
    
    template_name = "ricardo_template_1753487909_d79bcb95"
    
    try:
        # Check if template exists in BM
        templates_url = f"https://graph.facebook.com/v22.0/{bm_id}/message_templates"
        templates_response = requests.get(templates_url, headers=headers, timeout=10)
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            templates = templates_data.get('data', [])
            
            print(f"📝 {len(templates)} templates encontrados na BM")
            
            target_template = None
            for template in templates:
                if template.get('name') == template_name:
                    target_template = template
                    break
            
            if target_template:
                print(f"✅ Template encontrado: {template_name}")
                print(f"   📊 Status: {target_template.get('status', 'N/A')}")
                print(f"   🌍 Language: {target_template.get('language', 'N/A')}")
                print(f"   📋 Category: {target_template.get('category', 'N/A')}")
            else:
                print(f"❌ Template NÃO encontrado na BM: {template_name}")
                print(f"🔍 Templates disponíveis:")
                for template in templates[:5]:  # Show first 5
                    print(f"   - {template.get('name', 'N/A')} ({template.get('status', 'N/A')})")
        else:
            print(f"❌ Erro acessando templates: {templates_response.text}")
            
    except Exception as e:
        print(f"❌ Erro verificando templates: {e}")
    
    # 5. Final diagnosis
    print(f"\n5️⃣ DIAGNÓSTICO FINAL")
    print(f"🔍 POSSÍVEIS CAUSAS DA NÃO ENTREGA:")
    print(f"   1. Token sem permissões específicas para envio")
    print(f"   2. Business Manager com restrições da Meta")
    print(f"   3. Phone Numbers em revisão/pausados")
    print(f"   4. Template pausado por qualidade")
    print(f"   5. Número destinatário bloqueado/inválido")
    print(f"   6. Delay de rede WhatsApp (até 30 minutos)")
    print(f"   7. Sandbox mode vs Production")

if __name__ == "__main__":
    debug_token_reality()