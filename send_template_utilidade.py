#!/usr/bin/env python3
"""
Enviar template 'utilidade' para número específico usando os 3 números disponíveis
"""

import requests
import json
import time

def send_template_utilidade():
    """Enviar template utilidade para o número especificado"""
    
    # Configurações
    access_token = "EAAYLvZBaHbvYBPSFAJtcYTWqp02BxufOizAA5l6H4D93yls5X7m9ONZCwTZCTbf2oJZCtMjg5mjjwy141Ow27ZAv1yC6dXJGSOKcTSEZBf2tkciWfZCraJZANY3xXCiKi2bcwpOIfD6EUNWcEgXIlYphIIyIZCSIxMT926AdMpuZBUjLnOE64c8UPKzZA4bBKcfTi2GHqZC4q3bQbeZCOvEl1q1AdohNxZCZBNdDIOXjXiuL1znl0CJVgZDZD"
    business_account_id = "746006914691827"
    target_number = "5561999114066"  # Número de destino
    
    # Números disponíveis (sem +1 e caracteres especiais)
    available_phones = [
        "15558149312",      # Primeiro número
        "15674669530",      # +1 567-466-9530 -> 15674669530  
        "18312831347"       # +1 831-283-1347 -> 18312831347
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== ENVIANDO TEMPLATE UTILIDADE ===\n")
    print(f"Template: utilidade")
    print(f"Destino: {target_number}")
    print(f"Números disponíveis: {len(available_phones)}")
    print("-" * 60)
    
    # 1. Primeiro obter a estrutura do template "utilidade"
    print("\n🔍 OBTENDO ESTRUTURA DO TEMPLATE...")
    try:
        template_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/message_templates?fields=id,name,status,category,language,components",
            headers=headers,
            timeout=15
        )
        
        if template_response.status_code == 200:
            templates_data = template_response.json()
            templates = templates_data.get('data', [])
            
            # Encontrar template "utilidade"
            utilidade_template = None
            for template in templates:
                if template.get('name') == 'utilidade':
                    utilidade_template = template
                    break
            
            if not utilidade_template:
                print("❌ Template 'utilidade' não encontrado!")
                return False
                
            print(f"✅ Template encontrado:")
            print(f"   ID: {utilidade_template.get('id')}")
            print(f"   Status: {utilidade_template.get('status')}")
            print(f"   Categoria: {utilidade_template.get('category')}")
            print(f"   Idioma: {utilidade_template.get('language')}")
            print(f"   Componentes: {len(utilidade_template.get('components', []))}")
            
            # Mostrar estrutura dos componentes
            components = utilidade_template.get('components', [])
            for i, comp in enumerate(components):
                print(f"      Componente {i+1}: {comp.get('type')}")
                if comp.get('type') == 'BODY' and 'text' in comp:
                    print(f"         Texto: {comp['text'][:100]}...")
                if comp.get('type') == 'HEADER' and 'text' in comp:
                    print(f"         Header: {comp['text']}")
                    
        else:
            print(f"❌ Erro ao buscar templates: {template_response.status_code}")
            print(f"   Resposta: {template_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter template: {e}")
        return False
    
    # 2. Preparar mensagem do template
    template_message = {
        "messaging_product": "whatsapp",
        "to": target_number,
        "type": "template",
        "template": {
            "name": "utilidade",
            "language": {
                "code": utilidade_template.get('language', 'en')
            }
        }
    }
    
    # Se o template tiver parâmetros, precisaria incluir components
    # Por ora, assumindo que é um template simples sem parâmetros
    
    print(f"\n📤 ENVIANDO ATRAVÉS DOS {len(available_phones)} NÚMEROS...")
    
    success_count = 0
    results = []
    
    # 3. Enviar através de cada número disponível
    for i, phone_id in enumerate(available_phones, 1):
        print(f"\n📱 Número {i}: {phone_id}")
        
        try:
            # URL para envio de mensagem
            send_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
            
            response = requests.post(
                send_url, 
                json=template_message, 
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'N/A')
                
                print(f"✅ ENVIADO com sucesso!")
                print(f"   Message ID: {message_id}")
                print(f"   Status: Entregue")
                
                success_count += 1
                results.append({
                    'phone_id': phone_id,
                    'success': True,
                    'message_id': message_id,
                    'status': 'sent'
                })
                
            else:
                error_response = response.json()
                error_msg = error_response.get('error', {}).get('message', 'Erro desconhecido')
                
                print(f"❌ FALHOU!")
                print(f"   Status: {response.status_code}")
                print(f"   Erro: {error_msg}")
                
                results.append({
                    'phone_id': phone_id,
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                })
                
        except Exception as e:
            print(f"❌ ERRO ao enviar: {e}")
            results.append({
                'phone_id': phone_id,
                'success': False,
                'error': str(e),
                'status_code': 'exception'
            })
        
        # Pequena pausa entre os envios
        if i < len(available_phones):
            time.sleep(2)
    
    # 4. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO ENVIO")
    print("=" * 60)
    print(f"Template: utilidade")
    print(f"Destino: {target_number}")
    print(f"Números utilizados: {len(available_phones)}")
    print(f"Enviados com sucesso: {success_count}")
    print(f"Taxa de sucesso: {(success_count/len(available_phones)*100):.1f}%")
    
    print(f"\n📋 DETALHES:")
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result['success'] else "❌"
        print(f"   {status_icon} Número {i} ({result['phone_id']}): ", end="")
        
        if result['success']:
            print(f"Enviado (ID: {result.get('message_id', 'N/A')})")
        else:
            print(f"Falhou - {result.get('error', 'Erro desconhecido')}")
    
    print("=" * 60)
    
    # Salvar resultado
    final_result = {
        'template_name': 'utilidade',
        'target_number': target_number,
        'business_account_id': business_account_id,
        'total_phones': len(available_phones),
        'successful_sends': success_count,
        'success_rate': (success_count/len(available_phones)*100),
        'results': results,
        'timestamp': int(time.time())
    }
    
    with open('template_send_result.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultado salvo em: template_send_result.json")
    
    return success_count > 0

if __name__ == "__main__":
    success = send_template_utilidade()
    if success:
        print("\n🎉 Pelo menos um envio foi bem-sucedido!")
    else:
        print("\n❌ Nenhum envio foi bem-sucedido.")