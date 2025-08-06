#!/usr/bin/env python3
"""
Debug completo do erro #135000 - Template não encontrado/indisponível
"""

import os
import requests

def debug_error_135000():
    """Debug complete error #135000 analysis"""
    
    print(f"🔍 DEBUG COMPLETO DO ERRO #135000")
    print("=" * 60)
    
    # Token da nova BM detectada
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"🆔 TOKEN ATUAL: {token[:50]}...")
    
    # 1. Verificar qual BM está sendo usada
    print(f"\n1️⃣ VERIFICANDO BUSINESS MANAGER ATUAL")
    
    bm_url = f"https://graph.facebook.com/v22.0/me/businesses"
    
    try:
        response = requests.get(bm_url, headers=headers)
        if response.status_code == 200:
            businesses = response.json().get('data', [])
            
            for bm in businesses:
                bm_id = bm.get('id')
                bm_name = bm.get('name')
                print(f"📊 BM: {bm_id} - {bm_name}")
                
                # Verificar se é a BM 721254414139146 dos logs
                if bm_id == "721254414139146":
                    print(f"✅ ESTA É A BM ATIVA DOS LOGS!")
                    
    except Exception as e:
        print(f"❌ Erro BM: {e}")
    
    # 2. Verificar phone number que causou erro
    bm_id = "721254414139146"  # Da log INFO
    error_phone = "693473723855916"  # Da log de erro
    
    print(f"\n2️⃣ ANALISANDO PHONE NUMBER QUE FALHOU: {error_phone}")
    
    phone_url = f"https://graph.facebook.com/v22.0/{error_phone}"
    
    try:
        response = requests.get(phone_url, headers=headers)
        if response.status_code == 200:
            phone_data = response.json()
            
            print(f"📱 Display Name: {phone_data.get('display_phone_number', 'N/A')}")
            print(f"📊 Quality: {phone_data.get('quality_rating', 'N/A')}")
            print(f"✅ Status: {phone_data.get('status', 'N/A')}")
            print(f"🏢 Verified Name: {phone_data.get('verified_name', 'N/A')}")
            
        else:
            print(f"❌ Erro phone info: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro phone: {e}")
    
    # 3. Listar templates disponíveis para este phone
    print(f"\n3️⃣ TEMPLATES DISPONÍVEIS PARA PHONE {error_phone}")
    
    templates_url = f"https://graph.facebook.com/v22.0/{bm_id}/message_templates"
    
    try:
        response = requests.get(templates_url, headers=headers)
        if response.status_code == 200:
            templates = response.json().get('data', [])
            
            print(f"📋 Total templates na BM: {len(templates)}")
            
            # Procurar especificamente o template que estava sendo usado
            target_template = "maria_template_1753924869_9d7a8f62"  # Da log de erro
            
            found_target = False
            approved_templates = []
            
            for template in templates:
                name = template.get('name', '')
                status = template.get('status', '')
                
                if name == target_template:
                    found_target = True
                    print(f"🎯 TEMPLATE ALVO ENCONTRADO: {name}")
                    print(f"   Status: {status}")
                    print(f"   Category: {template.get('category', 'N/A')}")
                    print(f"   Language: {template.get('language', 'N/A')}")
                    
                    if status != 'APPROVED':
                        print(f"❌ PROBLEMA: Template não está APPROVED!")
                
                if status == 'APPROVED':
                    approved_templates.append(name)
            
            if not found_target:
                print(f"❌ PROBLEMA CRÍTICO: Template {target_template} NÃO EXISTE na BM!")
                
            print(f"\n✅ Templates APROVADOS disponíveis:")
            for approved in approved_templates[:10]:  # Mostrar primeiros 10
                print(f"   - {approved}")
                
            if len(approved_templates) > 10:
                print(f"   ... e mais {len(approved_templates) - 10} templates")
                
        else:
            print(f"❌ Erro templates: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro templates: {e}")
    
    # 4. Testar com um template aprovado da lista
    print(f"\n4️⃣ TESTE COM TEMPLATE APROVADO")
    
    # Primeiro, pegar um template aprovado qualquer
    if 'approved_templates' in locals() and approved_templates:
        test_template = approved_templates[0]
        print(f"🧪 Testando com: {test_template}")
        
        # Get template details
        template_detail_url = f"https://graph.facebook.com/v22.0/{bm_id}/message_templates"
        template_params = {'name': test_template}
        
        try:
            response = requests.get(template_detail_url, headers=headers, params=template_params)
            if response.status_code == 200:
                template_data = response.json().get('data', [])
                
                if template_data:
                    template_info = template_data[0]
                    components = template_info.get('components', [])
                    
                    print(f"📋 Template info:")
                    print(f"   Nome: {template_info.get('name')}")
                    print(f"   Categoria: {template_info.get('category')}")
                    print(f"   Idioma: {template_info.get('language')}")
                    
                    # Construir payload básico
                    template_payload = {
                        'messaging_product': 'whatsapp',
                        'to': '5561999114066',
                        'type': 'template',
                        'template': {
                            'name': test_template,
                            'language': {'code': template_info.get('language', 'en')}
                        }
                    }
                    
                    # Verificar se precisa de parâmetros
                    has_params = any('{{' in str(comp) for comp in components)
                    
                    if has_params:
                        print(f"⚠️  Template tem parâmetros - usando valores genéricos")
                        template_payload['template']['components'] = [
                            {
                                'type': 'body',
                                'parameters': [
                                    {'type': 'text', 'text': 'Pedro'},
                                    {'type': 'text', 'text': '123.456.789-00'}
                                ]
                            }
                        ]
                    
                    # Tentar enviar
                    message_url = f"https://graph.facebook.com/v22.0/{error_phone}/messages"
                    
                    send_response = requests.post(message_url, json=template_payload, headers=headers)
                    
                    print(f"📤 Resultado do teste:")
                    print(f"   Status: {send_response.status_code}")
                    
                    if send_response.status_code == 200:
                        result = send_response.json()
                        message_id = result.get('messages', [{}])[0].get('id', 'N/A')
                        print(f"   ✅ Sucesso! Message ID: {message_id}")
                        print(f"   📱 VERIFIQUE WHATSAPP +5561999114066")
                    else:
                        error_info = send_response.json().get('error', {})
                        print(f"   ❌ Erro: {error_info.get('code')} - {error_info.get('message')}")
                        
        except Exception as e:
            print(f"❌ Erro teste: {e}")
    
    print(f"\n🎯 ANÁLISE DO ERRO #135000:")
    print(f"Erro #135000 = 'Template not found' ou 'Template unavailable'")
    print(f"POSSÍVEIS CAUSAS:")
    print(f"1. Template maria_template_1753924869_9d7a8f62 não existe na BM nova")
    print(f"2. Template existe mas não está APPROVED")
    print(f"3. Template foi deletado/modificado")
    print(f"4. Phone number não tem acesso ao template")
    print(f"5. BM mudou e sistema está usando templates da BM antiga")
    
    print(f"\n✅ SOLUÇÃO: Fallback funcionou - mensagem de texto foi entregue")
    print(f"📨 Message ID do sucesso: wamid.HBgMNTU2MTk5MTE0MDY2FQIAERgSOEI5MjVERkE1NTMzRjczNTFBAA==")

if __name__ == "__main__":
    debug_error_135000()