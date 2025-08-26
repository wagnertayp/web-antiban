#!/usr/bin/env python3
"""
Teste do novo BM e token para envio do template ailanaa1
BM: 781046244494318
Token: EAAUjHbSGk84BPRZA898niMAXLZBU5pOXUTPP9BuWNZCyb2TRZCj0cYgFo884MBihuapssDyi2zTzcy10EhT04UW1hWD1IECVBzkbo4ClEuyDUmzn6VWI1VA26oiQ8gvVUXPRN4DAPb9x8Ww73XcpTbqZCZBiZCcZBb9PZAJZBMnGO2PvZAO6H3s8GbwlTPJvDSeQuDWUft3KOZA71LjntsrDhkX6OMzS2tXCoUixRi6ZC0O4TDML0H56aCpBMvpoZD
"""

import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)

# Configurações do novo BM
ACCESS_TOKEN = "EAAUjHbSGk84BPRZA898niMAXLZBU5pOXUTPP9BuWNZCyb2TRZCj0cYgFo884MBihuapssDyi2zTzcy10EhT04UW1hWD1IECVBzkbo4ClEuyDUmzn6VWI1VA26oiQ8gvVUXPRN4DAPb9x8Ww73XcpTbqZCZBiZCcZBb9PZAJZBMnGO2PvZAO6H3s8GbwlTPJvDSeQuDWUft3KOZA71LjntsrDhkX6OMzS2tXCoUixRi6ZC0O4TDML0H56aCpBMvpoZD"
BM_ID = "781046244494318"
TEMPLATE_NAME = "ailanaa1"
TARGET_PHONE = "5561999114066"

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def discover_phone_numbers():
    """Descobrir phone numbers da BM"""
    try:
        url = f"https://graph.facebook.com/v22.0/{BM_ID}/phone_numbers"
        response = requests.get(url, headers=headers, timeout=15)
        
        logging.info(f"📱 Phone Numbers Discovery - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            phone_numbers = data.get('data', [])
            
            logging.info(f"✅ DESCOBERTOS {len(phone_numbers)} PHONE NUMBERS:")
            for i, phone in enumerate(phone_numbers, 1):
                phone_id = phone.get('id', 'N/A')
                display_name = phone.get('display_phone_number', 'N/A')
                verified = phone.get('verified_name', 'N/A')
                logging.info(f"  {i}. ID: {phone_id} | Number: {display_name} | Verified: {verified}")
            
            return phone_numbers
        else:
            logging.error(f"❌ Erro ao buscar phones: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        logging.error(f"❌ Exception ao descobrir phones: {e}")
        return []

def get_template_info():
    """Verificar se o template ailanaa1 existe e está aprovado"""
    try:
        url = f"https://graph.facebook.com/v22.0/{BM_ID}/message_templates"
        params = {'name': TEMPLATE_NAME}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        logging.info(f"🔍 Template Discovery - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            if templates:
                template = templates[0]
                status = template.get('status', 'UNKNOWN')
                language = template.get('language', 'UNKNOWN')
                logging.info(f"✅ TEMPLATE ENCONTRADO: {TEMPLATE_NAME}")
                logging.info(f"   Status: {status}")
                logging.info(f"   Language: {language}")
                logging.info(f"   Full Data: {json.dumps(template, indent=2)}")
                return template
            else:
                logging.warning(f"⚠️ Template {TEMPLATE_NAME} não encontrado")
                return None
        else:
            logging.error(f"❌ Erro ao buscar template: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Exception ao buscar template: {e}")
        return None

def send_template_message(phone_id, template_info):
    """Enviar template para o número especificado"""
    try:
        # Determinar idioma do template
        language_code = template_info.get('language', 'pt_BR')
        
        # Preparar payload básico
        payload = {
            'messaging_product': 'whatsapp',
            'to': f'+{TARGET_PHONE}',
            'type': 'template',
            'template': {
                'name': TEMPLATE_NAME,
                'language': {'code': language_code}
            }
        }
        
        # Adicionar componentes se necessário
        components = template_info.get('components', [])
        if components:
            template_components = []
            
            for component in components:
                comp_type = component.get('type')
                
                if comp_type == 'BODY':
                    # Template de corpo - pode ter parâmetros
                    text = component.get('text', '')
                    if '{{1}}' in text or '{{2}}' in text:
                        # Template tem parâmetros - usando dados de exemplo
                        template_components.append({
                            'type': 'body',
                            'parameters': [
                                {'type': 'text', 'text': 'Cliente'},  # {{1}}
                                {'type': 'text', 'text': '123.456.789-00'}   # {{2}}
                            ]
                        })
                    
                elif comp_type == 'BUTTON':
                    # Template tem botão com URL dinâmica
                    buttons = component.get('buttons', [])
                    for button in buttons:
                        if button.get('type') == 'URL':
                            template_components.append({
                                'type': 'button',
                                'sub_type': 'url',
                                'index': 0,
                                'parameters': [{'type': 'text', 'text': '123456789'}]
                            })
            
            if template_components:
                payload['template']['components'] = template_components
        
        logging.info(f"📤 Enviando template via Phone ID: {phone_id}")
        logging.info(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        logging.info(f"📨 Send Response - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            logging.info(f"✅ MENSAGEM ENVIADA COM SUCESSO!")
            logging.info(f"   Message ID: {message_id}")
            logging.info(f"   Para: +{TARGET_PHONE}")
            logging.info(f"   Via Phone: {phone_id}")
            return True
        else:
            logging.error(f"❌ Erro no envio: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Exception no envio: {e}")
        return False

def main():
    """Função principal"""
    logging.info("🚀 INICIANDO TESTE DA NOVA BM")
    logging.info(f"📋 BM ID: {BM_ID}")
    logging.info(f"📞 Target: +{TARGET_PHONE}")
    logging.info(f"📝 Template: {TEMPLATE_NAME}")
    
    # 1. Descobrir phone numbers
    phone_numbers = discover_phone_numbers()
    if not phone_numbers:
        logging.error("❌ Nenhum phone number encontrado. Abortando teste.")
        return
    
    # 2. Verificar template
    template_info = get_template_info()
    if not template_info:
        logging.error("❌ Template não encontrado. Abortando teste.")
        return
    
    # 3. Enviar para os 5 primeiros phones
    phones_to_test = phone_numbers[:5]  # Primeiros 5 phones
    
    logging.info(f"📨 ENVIANDO PARA {len(phones_to_test)} PHONE NUMBERS:")
    
    success_count = 0
    for i, phone in enumerate(phones_to_test, 1):
        phone_id = phone.get('id')
        display_number = phone.get('display_phone_number', 'N/A')
        
        logging.info(f"\n--- TENTATIVA {i}/{len(phones_to_test)} ---")
        logging.info(f"Phone ID: {phone_id}")
        logging.info(f"Display Number: {display_number}")
        
        if send_template_message(phone_id, template_info):
            success_count += 1
            logging.info(f"✅ Sucesso {i}/{len(phones_to_test)}")
        else:
            logging.error(f"❌ Falha {i}/{len(phones_to_test)}")
        
        # Pequena pausa entre envios
        if i < len(phones_to_test):
            time.sleep(1)
    
    logging.info(f"\n🎯 RESULTADO FINAL:")
    logging.info(f"   Total enviados: {success_count}/{len(phones_to_test)}")
    logging.info(f"   Target: +{TARGET_PHONE}")
    logging.info(f"   Template: {TEMPLATE_NAME}")

if __name__ == "__main__":
    main()