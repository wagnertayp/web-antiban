#!/usr/bin/env python3
"""
Teste com número americano para verificar se o problema é roteamento internacional
"""

import os
import sys
import logging
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_american_phone():
    """Test sending to American phone number (same region as BM)"""
    
    # Initialize WhatsApp API
    whatsapp_api = WhatsAppBusinessAPI()
    
    # Test with American phone number (similar to the BM phone numbers)
    test_phone = "15558015919"  # Same as display_phone_number from BM
    
    # Test parameters (CPF, Nome)
    test_parameters = ["065.370.801-77", "Pedro"]
    
    print(f"🧪 TESTANDO COM NÚMERO AMERICANO: {test_phone}")
    print(f"📋 Business Manager: {whatsapp_api.business_account_id}")
    print(f"📱 Primeiro Phone Number da BM: 693473723855916 (15558015919)")
    
    try:
        # Try simple text message first
        simple_message = "Hello Pedro, this is a test message from the new WhatsApp Business Account. Please confirm if you receive this message."
        
        success, result = whatsapp_api.send_text_message(
            phone=test_phone,
            message=simple_message
        )
        
        if success:
            print(f"✅ SUCESSO: Mensagem de texto enviada!")
            print(f"📨 Message ID: {result.get('messageId', 'N/A')}")
            print(f"📞 WhatsApp ID: {result.get('whatsAppId', 'N/A')}")
            return True
        else:
            print(f"❌ FALHOU: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")
        return False

def test_brazilian_phone():
    """Test sending to Brazilian phone number"""
    
    # Initialize WhatsApp API
    whatsapp_api = WhatsAppBusinessAPI()
    
    # Test with Brazilian phone number
    test_phone = "5561999114066"
    
    print(f"\n🧪 TESTANDO COM NÚMERO BRASILEIRO: {test_phone}")
    
    try:
        # Try simple text message
        simple_message = "Olá Pedro, esta é uma mensagem de teste da nova conta WhatsApp Business. Por favor confirme se você recebe esta mensagem."
        
        success, result = whatsapp_api.send_text_message(
            phone=test_phone,
            message=simple_message
        )
        
        if success:
            print(f"✅ SUCESSO: Mensagem para Brasil enviada!")
            print(f"📨 Message ID: {result.get('messageId', 'N/A')}")
            print(f"📞 WhatsApp ID: {result.get('whatsAppId', 'N/A')}")
            return True
        else:
            print(f"❌ FALHOU: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO: Testando roteamento de mensagens")
    print("=" * 50)
    
    # Test American phone first
    american_success = test_american_phone()
    
    # Test Brazilian phone
    brazilian_success = test_brazilian_phone()
    
    print("\n📊 RESULTADOS:")
    print(f"📞 Número Americano: {'✅ Funcionou' if american_success else '❌ Falhou'}")
    print(f"🇧🇷 Número Brasileiro: {'✅ Funcionou' if brazilian_success else '❌ Falhou'}")
    
    if american_success and not brazilian_success:
        print("\n⚠️ PROBLEMA IDENTIFICADO: Roteamento internacional")
        print("💡 SOLUÇÃO: Usar BM com números brasileiros ou do mesmo país do destinatário")
    elif not american_success and not brazilian_success:
        print("\n⚠️ PROBLEMA: Conta WhatsApp Business não está funcionando")
    else:
        print("\n✅ SISTEMA FUNCIONANDO NORMALMENTE")
    
    sys.exit(0 if (american_success or brazilian_success) else 1)