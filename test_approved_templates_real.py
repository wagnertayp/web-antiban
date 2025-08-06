#!/usr/bin/env python3
"""
Teste real com templates modelo1 e modelo2 aprovados
"""

import requests
import os

def test_both_approved_templates():
    """Testar envio real com modelo1 e modelo2 aprovados"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '674928665709899')
    
    url = f'https://graph.facebook.com/v23.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    test_phone = '+5573999084689'
    test_cpf = '123.456.789-00'
    test_nome = 'Teste Sistema'
    
    templates_to_test = [
        {
            'name': 'modelo1',
            'language': 'en',
            'payload': {
                'messaging_product': 'whatsapp',
                'to': test_phone,
                'type': 'template',
                'template': {
                    'name': 'modelo1',
                    'language': {'code': 'en'},
                    'components': [
                        {
                            'type': 'body',
                            'parameters': [
                                {'type': 'text', 'text': test_cpf},
                                {'type': 'text', 'text': test_nome}
                            ]
                        },
                        {
                            'type': 'button',
                            'sub_type': 'url',
                            'index': 0,
                            'parameters': [{'type': 'text', 'text': test_cpf}]
                        }
                    ]
                }
            }
        },
        {
            'name': 'modelo2',
            'language': 'en',
            'payload': {
                'messaging_product': 'whatsapp',
                'to': test_phone,
                'type': 'template',
                'template': {
                    'name': 'modelo2',
                    'language': {'code': 'en'},
                    'components': [
                        {
                            'type': 'body',
                            'parameters': [
                                {'type': 'text', 'text': test_cpf},
                                {'type': 'text', 'text': test_nome}
                            ]
                        },
                        {
                            'type': 'button',
                            'sub_type': 'url',
                            'index': 0,
                            'parameters': [{'type': 'text', 'text': test_cpf}]
                        }
                    ]
                }
            }
        }
    ]
    
    results = []
    
    for template_config in templates_to_test:
        template_name = template_config['name']
        payload = template_config['payload']
        
        print(f"=== TESTANDO {template_name.upper()} ===")
        print(f"Status: APROVADO")
        print(f"Idioma: {template_config['language']}")
        print(f"Telefone: {test_phone}")
        print(f"CPF: {test_cpf}")
        print(f"Nome: {test_nome}")
        print(f"\nEnviando...")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', 'N/A')
                
                print(f"✅ {template_name.upper()} ENVIADO COM SUCESSO!")
                print(f"Message ID: {message_id}")
                
                results.append({
                    'template': template_name,
                    'status': 'SUCCESS',
                    'message_id': message_id
                })
                
            else:
                error_data = response.json() if response.content else {}
                error_code = error_data.get('error', {}).get('code')
                error_message = error_data.get('error', {}).get('message', response.text)
                
                print(f"❌ {template_name.upper()} FALHOU:")
                print(f"Status: {response.status_code}")
                print(f"Código: {error_code}")
                print(f"Erro: {error_message}")
                
                results.append({
                    'template': template_name,
                    'status': 'FAILED',
                    'error_code': error_code,
                    'error_message': error_message
                })
                
        except Exception as e:
            print(f"❌ ERRO DE CONEXÃO ({template_name}): {e}")
            results.append({
                'template': template_name,
                'status': 'CONNECTION_ERROR',
                'error': str(e)
            })
        
        print("\n" + "="*50 + "\n")
    
    return results

def check_templates_status():
    """Verificar status atual dos templates"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '746006914691827')
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            modelo1 = next((t for t in templates if t['name'] == 'modelo1'), None)
            modelo2 = next((t for t in templates if t['name'] == 'modelo2'), None)
            
            print("=== STATUS DOS TEMPLATES ===")
            
            if modelo1:
                print(f"modelo1: {modelo1['status']} (ID: {modelo1['id']})")
            else:
                print("modelo1: NÃO ENCONTRADO")
            
            if modelo2:
                print(f"modelo2: {modelo2['status']} (ID: {modelo2['id']})")
            else:
                print("modelo2: NÃO ENCONTRADO")
            
            return modelo1, modelo2
            
        else:
            print(f"Erro ao verificar templates: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None, None

if __name__ == "__main__":
    print("=== TESTE COMPLETO DOS TEMPLATES APROVADOS ===\n")
    
    # Verificar status primeiro
    modelo1, modelo2 = check_templates_status()
    
    if not modelo1 or not modelo2:
        print("❌ Templates não encontrados ou não aprovados")
        exit(1)
    
    if modelo1['status'] != 'APPROVED' or modelo2['status'] != 'APPROVED':
        print("❌ Templates não estão aprovados")
        print(f"modelo1: {modelo1['status'] if modelo1 else 'N/A'}")
        print(f"modelo2: {modelo2['status'] if modelo2 else 'N/A'}")
        exit(1)
    
    print("✅ Ambos templates confirmados como APROVADOS\n")
    
    # Testar envios
    results = test_both_approved_templates()
    
    # Resumo final
    print("=== RESUMO FINAL ===")
    
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    errors = [r for r in results if r['status'] == 'CONNECTION_ERROR']
    
    if successful:
        print(f"✅ TEMPLATES FUNCIONANDO: {len(successful)}")
        for r in successful:
            print(f"   - {r['template']}: {r['message_id']}")
    
    if failed:
        print(f"❌ TEMPLATES COM ERRO: {len(failed)}")
        for r in failed:
            error_135000 = r.get('error_code') == 135000
            print(f"   - {r['template']}: {r['error_code']} {'(BUG #135000)' if error_135000 else ''}")
    
    if errors:
        print(f"🔌 ERROS DE CONEXÃO: {len(errors)}")
        for r in errors:
            print(f"   - {r['template']}: {r['error']}")
    
    total_success = len(successful)
    if total_success == 2:
        print(f"\n🎉 SISTEMA 100% OPERACIONAL!")
        print(f"✅ Ambos templates aprovados e funcionando")
        print(f"🚀 Pronto para processar 29K contatos")
    elif total_success == 1:
        print(f"\n⚠️ 1 template funcionando")
        print(f"💡 Usar o template que funciona para envios")
    else:
        print(f"\n❌ Nenhum template funcionando")
        print(f"🔧 Ativar sistema de fallback #135000")