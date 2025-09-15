#!/usr/bin/env python3
"""
Obter os IDs corretos dos phone numbers e enviar template
"""

import requests
import json
import time

def send_template_with_correct_ids():
    """Obter IDs corretos e enviar template"""
    
    access_token = "EAAYLvZBaHbvYBPXLjVBpp95RQaBLDKjaWZCnRxCIgdgapOrTqWsdkgr9kVEfCZC2mmx3QNWBhChM1jdZC8QySpZAlDIA9o3O7wEQjrJ9ZAYZBnuO4kZCRZBX6pMxjc6sa7s2LJlakDSdVaHdEAR3jZAoOtCTfFmfHhrcbPQGEZCVYZBPOZCDC3KugAfAizdwsLVvK6C13Q29CQnOHyWPN7aYx4KYwWt5mBzKRFxY6n70PmiDZAWD7tZBYIZD"
    business_account_id = "746006914691827"
    target_number = "5561999114066"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== OBTENDO IDs CORRETOS DOS NÚMEROS ===\n")
    
    # 1. Obter os IDs reais dos phone numbers
    try:
        phones_response = requests.get(
            f"https://graph.facebook.com/v22.0/{business_account_id}/phone_numbers?fields=id,display_phone_number,verified_name,code_verification_status,status,quality_rating,messaging_limit_tier",
            headers=headers,
            timeout=15
        )
        
        if phones_response.status_code == 200:
            phones_data = phones_response.json()
            phones = phones_data.get('data', [])
            
            print(f"✅ {len(phones)} número(s) encontrado(s):")
            
            phone_ids = []
            for i, phone in enumerate(phones, 1):
                phone_id = phone.get('id')  # Este é o ID real para usar na API
                display_number = phone.get('display_phone_number', 'N/A')
                status = phone.get('status', 'N/A')
                verification = phone.get('code_verification_status', 'N/A')
                
                print(f"\n   📞 Número {i}:")
                print(f"      ID Real: {phone_id}")
                print(f"      Número Display: {display_number}")
                print(f"      Status: {status}")
                print(f"      Verificação: {verification}")
                
                # Adicionar apenas números conectados
                if status == 'CONNECTED':
                    phone_ids.append(phone_id)
                    print(f"      ✅ Adicionado para envio")
                else:
                    print(f"      ⏸️ Não adicionado (status: {status})")
                    
            if not phone_ids:
                print("❌ Nenhum número conectado encontrado!")
                return False
                
            print(f"\n📱 Total de números conectados para envio: {len(phone_ids)}")
            
        else:
            print(f"❌ Erro ao buscar números: {phones_response.status_code}")
            print(f"   Resposta: {phones_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 2. Preparar mensagem do template
    template_message = {
        "messaging_product": "whatsapp",
        "to": target_number,
        "type": "template",
        "template": {
            "name": "utilidade",
            "language": {
                "code": "en"
            }
        }
    }
    
    print(f"\n📤 ENVIANDO TEMPLATE ATRAVÉS DOS {len(phone_ids)} NÚMEROS...")
    print(f"Template: utilidade")
    print(f"Destino: {target_number}")
    print("-" * 60)
    
    success_count = 0
    results = []
    
    # 3. Enviar através de cada número conectado
    for i, phone_id in enumerate(phone_ids, 1):
        print(f"\n📱 Enviando via número {i} (ID: {phone_id})...")
        
        try:
            send_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
            
            response = requests.post(
                send_url,
                json=template_message,
                headers=headers,
                timeout=15
            )
            
            print(f"   Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'N/A')
                
                print(f"   ✅ ENVIADO COM SUCESSO!")
                print(f"   Message ID: {message_id}")
                
                success_count += 1
                results.append({
                    'phone_id': phone_id,
                    'success': True,
                    'message_id': message_id,
                    'attempt': i
                })
                
            else:
                error_response = response.json() if response.content else {}
                error_msg = error_response.get('error', {}).get('message', 'Erro desconhecido')
                error_code = error_response.get('error', {}).get('code', 'N/A')
                
                print(f"   ❌ FALHOU!")
                print(f"   Código: {error_code}")
                print(f"   Erro: {error_msg}")
                
                results.append({
                    'phone_id': phone_id,
                    'success': False,
                    'error': error_msg,
                    'error_code': error_code,
                    'status_code': response.status_code,
                    'attempt': i
                })
                
        except Exception as e:
            print(f"   ❌ EXCEÇÃO: {e}")
            results.append({
                'phone_id': phone_id,
                'success': False,
                'error': str(e),
                'attempt': i
            })
        
        # Pequena pausa entre envios
        if i < len(phone_ids):
            print(f"   ⏳ Aguardando 3 segundos...")
            time.sleep(3)
    
    # 4. Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL DO ENVIO")
    print("=" * 70)
    print(f"Template enviado: utilidade")
    print(f"Número de destino: {target_number}")
    print(f"Tentativas realizadas: {len(phone_ids)}")
    print(f"Enviados com sucesso: {success_count}")
    print(f"Taxa de sucesso: {(success_count/len(phone_ids)*100):.1f}%")
    
    print(f"\n📋 DETALHES POR TENTATIVA:")
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        attempt = result['attempt']
        
        print(f"   {status_icon} Tentativa {attempt} (Phone ID: {result['phone_id'][:15]}...):")
        
        if result['success']:
            print(f"       ✓ Enviado com sucesso")
            print(f"       ✓ Message ID: {result.get('message_id', 'N/A')}")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            print(f"       ✗ Falhou: {error_msg}")
            if 'error_code' in result:
                print(f"       ✗ Código: {result['error_code']}")
    
    print("=" * 70)
    
    # Salvar resultado detalhado
    final_result = {
        'template_name': 'utilidade',
        'target_number': target_number,
        'business_account_id': business_account_id,
        'total_attempts': len(phone_ids),
        'successful_sends': success_count,
        'success_rate': (success_count/len(phone_ids)*100) if phone_ids else 0,
        'phone_ids_used': phone_ids,
        'detailed_results': results,
        'timestamp': int(time.time())
    }
    
    with open('template_send_detailed_result.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultado detalhado salvo em: template_send_detailed_result.json")
    
    if success_count > 0:
        print(f"\n🎉 SUCESSO! {success_count} envio(s) realizado(s) com sucesso!")
        print(f"✅ Você deve receber {success_count} mensagem(s) no seu WhatsApp em instantes.")
    else:
        print(f"\n❌ FALHA! Nenhum envio foi bem-sucedido.")
        print(f"🔍 Verifique os detalhes acima para mais informações.")
    
    return success_count > 0

if __name__ == "__main__":
    success = send_template_with_correct_ids()
    exit(0 if success else 1)