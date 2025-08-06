#!/usr/bin/env python3
"""
Debug de entrega - por que mensagens mostram enviadas mas não chegam
"""

import os
import sys
import logging
import requests
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_delivery():
    """Debug why messages show as sent but don't arrive"""
    
    # Set the exact token
    token = "EAAHUCvWVsdgBPBFZCiKfqR9ZB9UUSlw9SI011ZBN2pY0FZBH8Qm8E4ZAWESZB3t4RJ3jd7FRE66nEGM88r2KKXxwd5YZBeMU0ZA4etg0sTXCBG59nU43rxP5YB19HU2UlQPpDqNt0q8aFEJG6RgctKbpZCGubREh0jufFMv1rYZCeucBitAeGlUGQZBecxAYKP7xldiFScQFFaJDph6VoQVXaF8YynU2ELKNHemt7o3BDHheZAnwtAZDZD"
    os.environ['WHATSAPP_ACCESS_TOKEN'] = token
    
    business_account_id = "2089992404820473"
    target_phone = "5561999114066"
    
    print(f"🔍 DIAGNÓSTICO DE ENTREGA")
    print(f"🏢 Business Manager: {business_account_id}")
    print(f"📱 Token: {token[:50]}...")
    print(f"📞 Número alvo: +{target_phone}")
    print("=" * 80)
    
    # 1. Check Business Account status
    print(f"\n1️⃣ VERIFICANDO STATUS DA BUSINESS ACCOUNT")
    try:
        url = f"https://graph.facebook.com/v22.0/{business_account_id}"
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Business Account: {data.get('name', 'N/A')}")
            print(f"📋 ID: {data.get('id', 'N/A')}")
            print(f"📊 Status: Ativa")
        else:
            print(f"❌ Erro ao verificar Business Account: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção ao verificar Business Account: {e}")
    
    # 2. Check Phone Numbers status
    print(f"\n2️⃣ VERIFICANDO PHONE NUMBERS")
    try:
        url = f"https://graph.facebook.com/v22.0/{business_account_id}/phone_numbers"
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            phones = data.get('data', [])
            print(f"📱 Total phones: {len(phones)}")
            
            for i, phone in enumerate(phones[:5]):  # Show first 5
                phone_id = phone.get('id')
                display_name = phone.get('display_phone_number')
                verified_name = phone.get('verified_name')
                quality_rating = phone.get('quality_rating')
                status = phone.get('status')
                
                print(f"📞 Phone {i+1}: {display_name}")
                print(f"   📋 ID: {phone_id}")
                print(f"   👤 Nome: {verified_name}")
                print(f"   ⭐ Quality: {quality_rating}")
                print(f"   📊 Status: {status}")
                
        else:
            print(f"❌ Erro ao verificar Phone Numbers: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção ao verificar Phone Numbers: {e}")
    
    # 3. Check specific phone number details
    print(f"\n3️⃣ VERIFICANDO PHONE NUMBER ESPECÍFICO (725492557312328)")
    phone_id = "725492557312328"
    try:
        url = f"https://graph.facebook.com/v22.0/{phone_id}"
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📱 Phone: {data.get('display_phone_number')}")
            print(f"👤 Nome verificado: {data.get('verified_name')}")
            print(f"⭐ Quality Rating: {data.get('quality_rating')}")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔗 Platform: {data.get('platform_type')}")
            print(f"🎯 Throughput: {data.get('throughput', {}).get('level')}")
            
        else:
            print(f"❌ Erro ao verificar Phone específico: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção ao verificar Phone específico: {e}")
    
    # 4. Check template status
    print(f"\n4️⃣ VERIFICANDO TEMPLATE RICARDO")
    template_name = "ricardo_template_1753487687_5860ab23"
    try:
        url = f"https://graph.facebook.com/v22.0/{business_account_id}/message_templates"
        headers = {'Authorization': f'Bearer {token}'}
        params = {'name': template_name}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            if templates:
                template = templates[0]
                print(f"📋 Template: {template.get('name')}")
                print(f"📊 Status: {template.get('status')}")
                print(f"🌍 Idioma: {template.get('language')}")
                print(f"📝 Category: {template.get('category')}")
                
                # Check components
                components = template.get('components', [])
                print(f"🧩 Components: {len(components)}")
                for comp in components:
                    print(f"   - {comp.get('type')}: {comp.get('text', 'N/A')[:50]}...")
                    
            else:
                print(f"❌ Template não encontrado: {template_name}")
                
        else:
            print(f"❌ Erro ao verificar template: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção ao verificar template: {e}")
    
    # 5. Test actual message sending with detailed logging
    print(f"\n5️⃣ TESTE DE ENVIO COM LOGGING DETALHADO")
    
    whatsapp_api = WhatsAppBusinessAPI()
    
    print(f"🚀 Enviando mensagem de teste...")
    try:
        success, result = whatsapp_api.send_template_message(
            phone=target_phone,
            template_name=template_name,
            language_code="en",
            parameters=["Pedro", "065.370.801-77"]
        )
        
        print(f"📊 Resultado: {success}")
        print(f"📋 Details: {result}")
        
        if success:
            message_id = result.get('messageId')
            contacts = result.get('contacts', [])
            
            print(f"✅ Message ID: {message_id}")
            
            if contacts:
                contact = contacts[0]
                input_phone = contact.get('input')
                wa_id = contact.get('wa_id')
                print(f"📞 Phone resolution: {input_phone} -> {wa_id}")
                
                # CRITICAL: Check if WhatsApp ID is valid
                if wa_id and len(wa_id) > 10:
                    print(f"✅ WhatsApp ID válido: {wa_id}")
                    print(f"🎯 PROVÁVEL ENTREGA: ID resolvido corretamente")
                else:
                    print(f"❌ WhatsApp ID inválido: {wa_id}")
                    print(f"⚠️  POSSÍVEL PROBLEMA: Número não tem WhatsApp ou bloqueado")
            else:
                print(f"❌ Nenhum contato retornado na resposta")
                print(f"⚠️  PROBLEMA: API não conseguiu resolver o número")
                
        else:
            error_code = result.get('error_code')
            error_msg = result.get('error')
            print(f"❌ Falha: #{error_code} - {error_msg}")
            
    except Exception as e:
        print(f"❌ Exceção no teste: {e}")
    
    # 6. Summary and diagnosis
    print(f"\n6️⃣ DIAGNÓSTICO FINAL")
    print(f"🔍 POSSÍVEIS CAUSAS:")
    print(f"   1. Número não tem WhatsApp ativo")
    print(f"   2. Número bloqueou mensagens comerciais")
    print(f"   3. Quality Rating baixo da conta")
    print(f"   4. Throttling/Rate limiting da Meta")
    print(f"   5. Conta WhatsApp Business em revisão")
    print(f"   6. Template aprovado mas com restrições")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   - Testar com número conhecido funcional")
    print(f"   - Verificar Quality Rating da conta")
    print(f"   - Aguardar alguns minutos e tentar novamente")
    print(f"   - Verificar se conta está em período de revisão")

if __name__ == "__main__":
    debug_delivery()