#!/usr/bin/env python3
"""
Test script para enviar template ricardo_template_1753490810_b7ac4671 
dos 20 números da BM Iara para o celular 5561982132603
"""

import os
import requests
import logging
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_ricardo_template():
    """Test sending ricardo_template from all 20 phone numbers"""
    
    # Initialize WhatsApp API
    whatsapp = WhatsAppBusinessAPI()
    
    if not whatsapp.is_configured():
        print("❌ WhatsApp API não configurado corretamente")
        return
    
    print(f"✅ Business Manager ID: {whatsapp.business_account_id}")
    print(f"✅ Phone Numbers disponíveis: {len(whatsapp._available_phones)}")
    
    # Test parameters
    template_name = "ricardo_template_1753490810_b7ac4671"
    destination_phone = "+5561999114066"
    test_cpf = "065.370.801-77"
    test_nome = "Usuário Teste"
    
    print(f"\n🎯 TESTE: Enviando template '{template_name}' para {destination_phone}")
    print(f"📋 Parâmetros: CPF={test_cpf}, Nome={test_nome}")
    print(f"📱 Enviando dos {len(whatsapp._available_phones)} números disponíveis...\n")
    
    success_count = 0
    failed_count = 0
    
    # Send from all 20 available phone numbers
    for i, phone_id in enumerate(whatsapp._available_phones):  # All 20 numbers
        print(f"📞 [{i+1}/20] Phone ID: {phone_id[:15]}...")
        
        try:
            # Send template message
            success, response = whatsapp.send_template_message(
                destination_phone, 
                template_name, 
                'en',  # Language
                [test_cpf, test_nome],  # Parameters: {{1}}=CPF, {{2}}=Nome
                phone_id
            )
            
            if success:
                message_id = response.get('messageId', 'Unknown') if isinstance(response, dict) else 'Unknown'
                print(f"   ✅ SUCESSO - Message ID: {message_id}")
                success_count += 1
            else:
                error_msg = response.get('error', str(response)) if isinstance(response, dict) else str(response)
                print(f"   ❌ FALHOU - {error_msg}")
                failed_count += 1
                
        except Exception as e:
            print(f"   💥 ERRO - {str(e)}")
            failed_count += 1
        
        print()
    
    print(f"📊 RESULTADO FINAL:")
    print(f"   ✅ Sucessos: {success_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📈 Taxa de sucesso: {(success_count/(success_count+failed_count)*100):.1f}%")
    
    if success_count > 0:
        print(f"\n🎉 TESTE CONCLUÍDO! {success_count} mensagem(s) enviada(s) com sucesso!")
        print(f"📱 Verifique seu celular {destination_phone} para confirmar o recebimento.")
    else:
        print(f"\n⚠️  NENHUMA MENSAGEM ENVIADA COM SUCESSO")
        print(f"🔧 Verifique o token, Business Manager ID e Phone Numbers")

if __name__ == "__main__":
    test_ricardo_template()