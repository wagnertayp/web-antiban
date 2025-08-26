#!/usr/bin/env python3
"""
Verificar status de entrega das mensagens enviadas
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

# Configurações
ACCESS_TOKEN = "EAAUjHbSGk84BPZA4Fk5gpm3OEgowiR4sClnvTHZAvBNU4IAYMi8ec4QZBgpNtYNUWgDAeLZAoZAHviQTw75xdvHAQFHZBOEDZBTssFb06DZApZCCDQCtD7LteiEd7fudUnWBo9PKmCbB9kfNPxjMpuB24v4FLZAk91l22bCoHQBHqupKhzRRnO0v71Qottrowd5OCDUlrJPKvc5ZC1WNSKzp7RFSngxdRN5pMW8tyinH7t6zfDBqHLsVrNpeT4Y"

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Message IDs do último teste
message_ids = [
    "wamid.HBgMNTU2MTk5MTE0MDY2FQIAERgSRjQ4ODNGREQ3NjJGQzA1QzM3AA==",
    "wamid.HBgMNTU2MTk5MTE0MDY2FQIAERgSNzNCNTg0NkZFQTc1RUREQzMyAA=="  # Último ID visível
]

def check_message_status(message_id):
    """Verificar status de uma mensagem específica"""
    try:
        url = f"https://graph.facebook.com/v22.0/{message_id}"
        response = requests.get(url, headers=headers, timeout=15)
        
        logging.info(f"📋 Status Check - Message ID: {message_id[-20:]}")
        logging.info(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✅ Message Data: {json.dumps(data, indent=2)}")
            return data
        else:
            logging.error(f"❌ Error: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Exception checking message: {e}")
        return None

def test_simple_message():
    """Enviar uma mensagem simples de teste para verificar conectividade"""
    try:
        # Usar o primeiro phone number
        phone_id = "691407147399153"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': '+5561999114066',
            'type': 'text',
            'text': {'body': 'Teste de conectividade - mensagem simples'}
        }
        
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        logging.info(f"📤 Simple Message Test - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            logging.info(f"✅ SIMPLE MESSAGE SENT!")
            logging.info(f"   Message ID: {message_id}")
            return message_id
        else:
            logging.error(f"❌ Simple message failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Exception sending simple message: {e}")
        return None

def check_phone_number_status():
    """Verificar status dos phone numbers"""
    try:
        bm_id = "781046244494318"
        url = f"https://graph.facebook.com/v22.0/{bm_id}/phone_numbers"
        response = requests.get(url, headers=headers, timeout=15)
        
        logging.info(f"📱 Phone Status Check - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            phones = data.get('data', [])
            
            for phone in phones:
                phone_id = phone.get('id')
                status = phone.get('status', 'UNKNOWN')
                display = phone.get('display_phone_number')
                quality = phone.get('quality_rating', 'UNKNOWN')
                
                logging.info(f"📞 Phone: {display} | Status: {status} | Quality: {quality}")
                
                # Verificar mensagens recentes deste phone
                try:
                    messages_url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
                    msg_response = requests.get(messages_url, headers=headers, timeout=10)
                    if msg_response.status_code == 200:
                        logging.info(f"   ✅ Phone {phone_id} - Messages endpoint accessible")
                    else:
                        logging.warning(f"   ⚠️ Phone {phone_id} - Messages endpoint: {msg_response.status_code}")
                except:
                    logging.warning(f"   ⚠️ Phone {phone_id} - Could not check messages endpoint")
        else:
            logging.error(f"❌ Phone status check failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            
    except Exception as e:
        logging.error(f"❌ Exception checking phone status: {e}")

def main():
    """Função principal de verificação"""
    logging.info("🔍 INICIANDO VERIFICAÇÃO DE ENTREGA")
    
    # 1. Verificar status dos phone numbers
    logging.info("\n--- VERIFICANDO STATUS DOS PHONE NUMBERS ---")
    check_phone_number_status()
    
    # 2. Verificar status das mensagens enviadas
    logging.info("\n--- VERIFICANDO STATUS DAS MENSAGENS ---")
    for message_id in message_ids:
        check_message_status(message_id)
    
    # 3. Enviar mensagem de teste simples
    logging.info("\n--- ENVIANDO MENSAGEM DE TESTE SIMPLES ---")
    test_message_id = test_simple_message()
    
    if test_message_id:
        logging.info(f"\n--- VERIFICANDO MENSAGEM DE TESTE ---")
        import time
        time.sleep(2)  # Aguardar processamento
        check_message_status(test_message_id)
    
    logging.info("\n🎯 VERIFICAÇÃO COMPLETA")

if __name__ == "__main__":
    main()