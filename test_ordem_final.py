#!/usr/bin/env python3
"""
Teste final para validar ordem dos parâmetros
"""

import os
import sys
sys.path.append('.')

from services.whatsapp_business_api import WhatsAppBusinessAPI

def test_final_order():
    """Test final parameter order"""
    
    print(f"🧪 TESTE FINAL DA ORDEM DOS PARÂMETROS")
    print("=" * 50)
    
    # Initialize API
    api = WhatsAppBusinessAPI()
    
    # Test data - SIMULAR COMO A INTERFACE ENVIA
    phone = "+5561999114066"
    template_name = "ricardo_template_1753487909_d79bcb95"
    
    # Interface envia: [CPF, Nome] - vamos simular isso
    parameters = ["065.370.801-77", "Pedro"]  # [0] = CPF, [1] = Nome
    phone_id = "725492557312328"
    
    print(f"📱 Enviando para: {phone}")
    print(f"📝 Template: {template_name}")
    print(f"📋 Parâmetros da interface: {parameters}")
    print(f"   parameters[0] = {parameters[0]} (CPF)")
    print(f"   parameters[1] = {parameters[1]} (Nome)")
    print(f"🔄 Esperado no template:")
    print(f"   {{{{1}}}} = {parameters[1]} (Nome)")
    print(f"   {{{{2}}}} = {parameters[0]} (CPF)")
    print(f"📞 Usando phone ID: {phone_id}")
    
    # Send template
    success, result = api.send_template_message(phone, template_name, 'en', parameters, phone_id)
    
    if success:
        print(f"✅ SUCESSO! Message ID: {result.get('messageId', 'N/A')}")
        print(f"📊 Template enviado com ordem FINAL:")
        print(f"   {{{{1}}}} = {parameters[1]} (Nome)")
        print(f"   {{{{2}}}} = {parameters[0]} (CPF)")
        print(f"🎯 Agora deve chegar no WhatsApp!")
    else:
        print(f"❌ ERRO: {result}")

if __name__ == "__main__":
    test_final_order()