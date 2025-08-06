#!/usr/bin/env python3
"""
Debug profundo do erro #135000 - investigar causa raiz
"""

import requests
import os
import json

def check_business_account_status():
    """Verificar status da Business Account"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    print("=== VERIFICANDO STATUS DA BUSINESS ACCOUNT ===\n")
    
    # Verificar Business Account
    try:
        response = requests.get(
            f'https://graph.facebook.com/v23.0/{business_account_id}?fields=id,name,account_review_status,business_verification_status,on_behalf_of_business_info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Business Account ID: {data.get('id')}")
            print(f"Nome: {data.get('name', 'N/A')}")
            print(f"Review Status: {data.get('account_review_status', 'N/A')}")
            print(f"Verification Status: {data.get('business_verification_status', 'N/A')}")
            print(f"On Behalf Of: {data.get('on_behalf_of_business_info', 'N/A')}")
        else:
            print(f"❌ Erro ao verificar Business Account: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def check_phone_number_capabilities():
    """Verificar capacidades do Phone Number"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = '674928665709899'
    
    print("\n=== VERIFICANDO PHONE NUMBER CAPABILITIES ===\n")
    
    try:
        response = requests.get(
            f'https://graph.facebook.com/v23.0/{phone_number_id}?fields=id,verified_name,display_phone_number,quality_rating,throughput,messaging_limit,account_mode,certificate',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Phone Number ID: {data.get('id')}")
            print(f"Nome Verificado: {data.get('verified_name')}")
            print(f"Número: {data.get('display_phone_number')}")
            print(f"Quality Rating: {data.get('quality_rating')}")
            print(f"Throughput: {data.get('throughput')}")
            print(f"Messaging Limit: {data.get('messaging_limit', 'N/A')}")
            print(f"Account Mode: {data.get('account_mode', 'N/A')}")
            print(f"Certificate: {data.get('certificate', 'N/A')}")
        else:
            print(f"❌ Erro ao verificar Phone Number: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_simple_text_message():
    """Testar mensagem de texto simples para confirmar conectividade"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = '674928665709899'
    
    print("\n=== TESTANDO MENSAGEM DE TEXTO SIMPLES ===\n")
    
    payload = {
        "messaging_product": "whatsapp",
        "to": "5548999581973",
        "type": "text",
        "text": {
            "body": "Teste de conectividade - mensagem simples"
        }
    }
    
    try:
        response = requests.post(
            f'https://graph.facebook.com/v23.0/{phone_number_id}/messages',
            json=payload,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"✅ Mensagem texto enviada com sucesso!")
            print(f"Message ID: {message_id}")
            return True
        else:
            print(f"❌ Erro na mensagem texto: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_template_permissions():
    """Verificar permissões específicas de templates"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    print("\n=== VERIFICANDO PERMISSÕES DE TEMPLATES ===\n")
    
    # Verificar limite de templates
    try:
        response = requests.get(
            f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates?fields=id,name,status,category,quality_score&limit=5',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            print(f"Total de templates encontrados: {len(templates)}")
            
            approved_count = 0
            for template in templates:
                status = template.get('status')
                name = template.get('name')
                quality = template.get('quality_score', {})
                
                print(f"Template: {name}")
                print(f"  Status: {status}")
                print(f"  Category: {template.get('category')}")
                print(f"  Quality: {quality.get('score', 'N/A')}")
                
                if status == 'APPROVED':
                    approved_count += 1
                
                print()
            
            print(f"Templates aprovados: {approved_count}")
            
            if approved_count == 0:
                print("⚠️  PROBLEMA: Nenhum template realmente aprovado!")
                return False
            
            return True
            
        else:
            print(f"❌ Erro ao verificar templates: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_message_permissions():
    """Verificar permissões de envio de mensagens"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    print("\n=== VERIFICANDO PERMISSÕES DO TOKEN ===\n")
    
    try:
        response = requests.get(
            f'https://graph.facebook.com/v23.0/me?fields=id,name,permissions',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"User ID: {data.get('id')}")
            print(f"Name: {data.get('name', 'N/A')}")
            
            permissions = data.get('permissions', {})
            if permissions:
                print("Permissões:")
                for perm in permissions.get('data', []):
                    print(f"  - {perm.get('permission')}: {perm.get('status')}")
            else:
                print("Permissões: Não disponível via API")
        else:
            print(f"❌ Erro ao verificar token: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("=== DEBUG PROFUNDO ERRO #135000 ===\n")
    
    # 1. Verificar Business Account
    check_business_account_status()
    
    # 2. Verificar Phone Number
    check_phone_number_capabilities()
    
    # 3. Testar mensagem simples
    text_works = test_simple_text_message()
    
    # 4. Verificar templates
    templates_ok = check_template_permissions()
    
    # 5. Verificar permissões
    check_message_permissions()
    
    print("\n=== DIAGNÓSTICO FINAL ===")
    
    if text_works and not templates_ok:
        print("🔍 CAUSA IDENTIFICADA: Problema específico com templates")
        print("💡 SOLUÇÃO: Templates podem estar com restrições na Business Account")
    elif text_works and templates_ok:
        print("🔍 CAUSA PROVÁVEL: Bug específico #135000 da Meta")
        print("💡 SOLUÇÃO: Usar fallback de texto com conteúdo idêntico")
    elif not text_works:
        print("🔍 CAUSA IDENTIFICADA: Problema de conectividade/permissões")
        print("💡 SOLUÇÃO: Verificar token e permissões da conta")
    else:
        print("🔍 CAUSA INDEFINIDA: Múltiplos problemas identificados")
        print("💡 SOLUÇÃO: Investigação adicional necessária")