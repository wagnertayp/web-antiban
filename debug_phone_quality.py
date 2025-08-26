#!/usr/bin/env python3
"""
Debug detalhado da qualidade e status dos phone numbers
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

ACCESS_TOKEN = "EAAUjHbSGk84BPZA4Fk5gpm3OEgowiR4sClnvTHZAvBNU4IAYMi8ec4QZBgpNtYNUWgDAeLZAoZAHviQTw75xdvHAQFHZBOEDZBTssFb06DZApZCCDQCtD7LteiEd7fudUnWBo9PKmCbB9kfNPxjMpuB24v4FLZAk91l22bCoHQBHqupKhzRRnO0v71Qottrowd5OCDUlrJPKvc5ZC1WNSKzp7RFSngxdRN5pMW8tyinH7t6zfDBqHLsVrNpeT4Y"
BM_ID = "781046244494318"

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def deep_phone_analysis():
    """Análise profunda dos phone numbers"""
    try:
        url = f"https://graph.facebook.com/v22.0/{BM_ID}/phone_numbers"
        params = {
            'fields': 'id,display_phone_number,verified_name,code_verification_status,status,quality_rating,messaging_limit_tier,phone_number_type,certificate,is_pin_enabled'
        }
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        logging.info(f"📱 Deep Phone Analysis - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            phones = data.get('data', [])
            
            logging.info(f"✅ ANÁLISE DETALHADA DE {len(phones)} PHONES:")
            
            for i, phone in enumerate(phones, 1):
                logging.info(f"\n--- PHONE {i}/5 ---")
                logging.info(f"ID: {phone.get('id')}")
                logging.info(f"Number: {phone.get('display_phone_number')}")
                logging.info(f"Verified Name: {phone.get('verified_name')}")
                logging.info(f"Status: {phone.get('status', 'N/A')}")
                logging.info(f"Quality Rating: {phone.get('quality_rating', 'N/A')}")
                logging.info(f"Verification Status: {phone.get('code_verification_status', 'N/A')}")
                logging.info(f"Limit Tier: {phone.get('messaging_limit_tier', 'N/A')}")
                logging.info(f"Phone Type: {phone.get('phone_number_type', 'N/A')}")
                logging.info(f"Certificate: {phone.get('certificate', 'N/A')}")
                logging.info(f"PIN Enabled: {phone.get('is_pin_enabled', 'N/A')}")
                
                # Tentar obter mais detalhes
                phone_id = phone.get('id')
                try:
                    detail_url = f"https://graph.facebook.com/v22.0/{phone_id}"
                    detail_params = {'fields': 'status,quality_rating,messaging_limit_tier,throughput'}
                    detail_response = requests.get(detail_url, headers=headers, params=detail_params, timeout=10)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        logging.info(f"Additional Details: {json.dumps(detail_data, indent=2)}")
                    else:
                        logging.warning(f"Could not get details: {detail_response.status_code}")
                except:
                    logging.warning(f"Exception getting phone details for {phone_id}")
            
            return phones
        else:
            logging.error(f"❌ Deep analysis failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        logging.error(f"❌ Exception in deep analysis: {e}")
        return []

def test_brazilian_number():
    """Testar com número brasileiro para verificar restrições geográficas"""
    try:
        phone_id = "691407147399153"  # Primeiro phone
        
        # Tentar enviar para número brasileiro
        payload = {
            'messaging_product': 'whatsapp',
            'to': '+5561999114066',
            'type': 'text',
            'text': {'body': 'Teste BR: Conectividade Brasil'}
        }
        
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        logging.info(f"📞 Test BR Number - Status: {response.status_code}")
        logging.info(f"Response: {response.text}")
        
        # Tentar enviar para número americano
        payload_us = {
            'messaging_product': 'whatsapp',
            'to': '+15551234567',  # Número americano de teste
            'type': 'text',
            'text': {'body': 'Teste US: Conectividade EUA'}
        }
        
        response_us = requests.post(url, headers=headers, json=payload_us, timeout=30)
        
        logging.info(f"📞 Test US Number - Status: {response_us.status_code}")
        logging.info(f"Response: {response_us.text}")
        
    except Exception as e:
        logging.error(f"❌ Exception testing geographical limits: {e}")

def check_business_account_limits():
    """Verificar limites da business account"""
    try:
        url = f"https://graph.facebook.com/v22.0/{BM_ID}"
        params = {
            'fields': 'id,name,business_verification_status,messaging_api_rate_limit'
        }
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        logging.info(f"🏢 Business Account Check - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✅ BUSINESS ACCOUNT INFO:")
            logging.info(f"ID: {data.get('id')}")
            logging.info(f"Name: {data.get('name')}")
            logging.info(f"Verification Status: {data.get('business_verification_status', 'N/A')}")
            logging.info(f"Rate Limit: {data.get('messaging_api_rate_limit', 'N/A')}")
        else:
            logging.error(f"❌ Business account check failed: {response.status_code}")
            logging.error(f"Response: {response.text}")
            
    except Exception as e:
        logging.error(f"❌ Exception checking business account: {e}")

def main():
    """Função principal de debug"""
    logging.info("🔍 INICIANDO DEBUG DETALHADO")
    
    # 1. Análise profunda dos phones
    logging.info("\n--- ANÁLISE PROFUNDA DOS PHONE NUMBERS ---")
    phones = deep_phone_analysis()
    
    # 2. Verificar limites da business account
    logging.info("\n--- VERIFICANDO BUSINESS ACCOUNT ---")
    check_business_account_limits()
    
    # 3. Testar restrições geográficas
    logging.info("\n--- TESTANDO RESTRIÇÕES GEOGRÁFICAS ---")
    test_brazilian_number()
    
    logging.info("\n🎯 DEBUG COMPLETO")
    
    # Conclusões
    logging.info("\n--- POSSÍVEIS CAUSAS ---")
    logging.info("1. Phone numbers americanos podem ter restrição para envio ao Brasil")
    logging.info("2. Números podem estar com quality rating baixo ou suspensos") 
    logging.info("3. Business account pode ter limitações de verificação")
    logging.info("4. Rate limits ou restrições de envio internacional")

if __name__ == "__main__":
    main()