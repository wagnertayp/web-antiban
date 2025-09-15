#!/usr/bin/env python3
"""
Verificar conta WhatsApp Business - números aprovados e templates aprovados
"""

import requests
import json
import sys

def verify_whatsapp_account():
    """Verificar informações da conta WhatsApp Business"""
    
    # Token e ID da conta fornecidos pelo usuário
    access_token = "EAAYLvZBaHbvYBPSFAJtcYTWqp02BxufOizAA5l6H4D93yls5X7m9ONZCwTZCTbf2oJZCtMjg5mjjwy141Ow27ZAv1yC6dXJGSOKcTSEZBf2tkciWfZCraJZANY3xXCiKi2bcwpOIfD6EUNWcEgXIlYphIIyIZCSIxMT926AdMpuZBUjLnOE64c8UPKzZA4bBKcfTi2GHqZC4q3bQbeZCOvEl1q1AdohNxZCZBNdDIOXjXiuL1znl0CJVgZDZD"
    business_account_id = "1610705919605544"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== VERIFICAÇÃO DA CONTA WHATSAPP BUSINESS ===\n")
    print(f"Token: {access_token[:50]}...")
    print(f"Business Account ID: {business_account_id}")
    print("-" * 60)
    
    # 1. Verificar validade do token primeiro
    print("\n🔑 VERIFICANDO VALIDADE DO TOKEN...")
    try:
        me_response = requests.get(
            "https://graph.facebook.com/v22.0/me", 
            headers=headers, 
            timeout=10
        )
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"✅ Token válido")
            print(f"   ID: {me_data.get('id', 'N/A')}")
            print(f"   Nome: {me_data.get('name', 'N/A')}")
        else:
            print(f"❌ Token inválido: {me_response.status_code}")
            print(f"   Resposta: {me_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erro ao verificar token: {e}")
        return
    
    # 2. Verificar informações da Business Account
    print(f"\n📊 VERIFICANDO BUSINESS ACCOUNT...")
    try:
        ba_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}?fields=id,name,account_review_status,business_verification_status,currency,timezone_id",
            headers=headers,
            timeout=10
        )
        
        if ba_response.status_code == 200:
            ba_data = ba_response.json()
            print(f"✅ Business Account encontrada")
            print(f"   ID: {ba_data.get('id', 'N/A')}")
            print(f"   Nome: {ba_data.get('name', 'N/A')}")
            print(f"   Status de Review: {ba_data.get('account_review_status', 'N/A')}")
            print(f"   Status de Verificação: {ba_data.get('business_verification_status', 'N/A')}")
            print(f"   Moeda: {ba_data.get('currency', 'N/A')}")
            print(f"   Timezone: {ba_data.get('timezone_id', 'N/A')}")
        else:
            print(f"❌ Erro ao verificar Business Account: {ba_response.status_code}")
            print(f"   Resposta: {ba_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Verificar números de telefone (APPROVED)
    print(f"\n📱 VERIFICANDO NÚMEROS DE TELEFONE...")
    approved_phones = []
    total_phones = 0
    
    try:
        phones_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/phone_numbers?fields=id,display_phone_number,verified_name,code_verification_status,status,quality_rating,messaging_limit_tier",
            headers=headers,
            timeout=15
        )
        
        if phones_response.status_code == 200:
            phones_data = phones_response.json()
            phones = phones_data.get('data', [])
            total_phones = len(phones)
            
            print(f"✅ {total_phones} número(s) encontrado(s)")
            
            for i, phone in enumerate(phones, 1):
                phone_id = phone.get('id', 'N/A')
                display_number = phone.get('display_phone_number', 'N/A')
                verified_name = phone.get('verified_name', 'N/A')
                verification_status = phone.get('code_verification_status', 'N/A')
                status = phone.get('status', 'N/A')
                quality = phone.get('quality_rating', 'N/A')
                limit_tier = phone.get('messaging_limit_tier', 'N/A')
                
                print(f"\n   📞 Número {i}:")
                print(f"      ID: {phone_id}")
                print(f"      Número: {display_number}")
                print(f"      Nome Verificado: {verified_name}")
                print(f"      Status de Verificação: {verification_status}")
                print(f"      Status: {status}")
                print(f"      Quality Rating: {quality}")
                print(f"      Messaging Limit: {limit_tier}")
                
                # Contar números aprovados (status CONNECTED e verificação OK)
                if verification_status == 'VERIFIED' or status == 'CONNECTED':
                    approved_phones.append(phone)
                    
        else:
            print(f"❌ Erro ao buscar números: {phones_response.status_code}")
            print(f"   Resposta: {phones_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar números: {e}")
    
    # 4. Verificar templates aprovados
    print(f"\n📋 VERIFICANDO TEMPLATES...")
    approved_templates = []
    total_templates = 0
    
    try:
        templates_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/message_templates?fields=id,name,status,category,language,quality_score,rejected_reason",
            headers=headers,
            timeout=15
        )
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            templates = templates_data.get('data', [])
            total_templates = len(templates)
            
            print(f"✅ {total_templates} template(s) encontrado(s)")
            
            # Separar por status
            approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
            pending_templates = [t for t in templates if t.get('status') == 'PENDING']
            rejected_templates = [t for t in templates if t.get('status') == 'REJECTED']
            
            print(f"   ✅ Aprovados: {len(approved_templates)}")
            print(f"   ⏳ Pendentes: {len(pending_templates)}")
            print(f"   ❌ Rejeitados: {len(rejected_templates)}")
            
            if approved_templates:
                print(f"\n   📝 Templates Aprovados:")
                for i, template in enumerate(approved_templates, 1):
                    print(f"      {i}. {template.get('name', 'N/A')}")
                    print(f"         ID: {template.get('id', 'N/A')}")
                    print(f"         Categoria: {template.get('category', 'N/A')}")
                    print(f"         Idioma: {template.get('language', 'N/A')}")
                    quality = template.get('quality_score', {})
                    if quality:
                        print(f"         Quality Score: {quality.get('score', 'N/A')} ({quality.get('date', 'N/A')})")
                    print()
            
            if pending_templates:
                print(f"   ⏳ Templates Pendentes:")
                for template in pending_templates[:5]:  # Mostrar só os primeiros 5
                    print(f"      - {template.get('name', 'N/A')} ({template.get('category', 'N/A')})")
            
            if rejected_templates:
                print(f"   ❌ Templates Rejeitados:")
                for template in rejected_templates[:3]:  # Mostrar só os primeiros 3
                    reason = template.get('rejected_reason', 'Motivo não especificado')
                    print(f"      - {template.get('name', 'N/A')}: {reason}")
                    
        else:
            print(f"❌ Erro ao buscar templates: {templates_response.status_code}")
            print(f"   Resposta: {templates_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar templates: {e}")
    
    # 5. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    print(f"🔑 Token: {'✅ Válido' if me_response.status_code == 200 else '❌ Inválido'}")
    print(f"📱 Números Total: {total_phones}")
    print(f"📱 Números Aprovados: {len(approved_phones)}")
    print(f"📋 Templates Total: {total_templates}")
    print(f"📋 Templates Aprovados: {len(approved_templates)}")
    print("=" * 60)
    
    # Salvar dados completos em arquivo JSON
    verification_data = {
        'token_valid': me_response.status_code == 200,
        'business_account_id': business_account_id,
        'total_phones': total_phones,
        'approved_phones': len(approved_phones),
        'phones_details': phones if 'phones' in locals() else [],
        'total_templates': total_templates,
        'approved_templates_count': len(approved_templates),
        'approved_templates': approved_templates,
        'pending_templates_count': len(pending_templates) if 'pending_templates' in locals() else 0,
        'rejected_templates_count': len(rejected_templates) if 'rejected_templates' in locals() else 0
    }
    
    with open('whatsapp_verification_result.json', 'w', encoding='utf-8') as f:
        json.dump(verification_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Dados completos salvos em: whatsapp_verification_result.json")

if __name__ == "__main__":
    verify_whatsapp_account()