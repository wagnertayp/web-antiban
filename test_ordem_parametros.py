#!/usr/bin/env python3
"""
Teste para verificar se a ordem dos parâmetros está correta
"""

import os
import sys
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_template_order():
    """Test template parameter order"""
    
    print(f"🧪 TESTANDO ORDEM CORRETA DOS PARÂMETROS")
    print("=" * 50)
    
    try:
        from services.whatsapp_business_api import WhatsAppBusinessAPI
        
        # Create instance
        api = WhatsAppBusinessAPI()
        
        # Test template send with correct order
        phone = "+5561999114066"
        template_name = "ricardo_template_1753487909_d79bcb95"
        parameters = ["065.370.801-77", "Pedro"]  # CPF, Nome
        
        print(f"📱 Enviando para: {phone}")
        print(f"📝 Template: {template_name}")
        print(f"📋 Parâmetros: CPF={parameters[0]}, Nome={parameters[1]}")
        print(f"🔄 Ordem esperada no template: {{{{1}}}} = Nome, {{{{2}}}} = CPF")
        
        # Get available phones
        phones = api.get_all_phone_numbers()
        if not phones:
            print(f"❌ Nenhum phone number disponível")
            return
            
        # Use correct phone from BM 2089992404820473
        phone_id = "725492557312328"  # Phone da BM correta
        print(f"📞 Usando phone ID correto da BM: {phone_id}")
        
        # Send template (ordem correta: phone, template_name, language_code, parameters, phone_id)
        success, result = api.send_template_message(phone, template_name, 'en', parameters, phone_id)
        
        if success:
            print(f"✅ SUCESSO! Message ID: {result.get('messageId', 'N/A')}")
            print(f"📊 Template enviado com ordem CORRETA:")
            print(f"   {{{{1}}}} = {parameters[1]} (Nome)")
            print(f"   {{{{2}}}} = {parameters[0]} (CPF)")
        else:
            print(f"❌ ERRO: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_template_order()