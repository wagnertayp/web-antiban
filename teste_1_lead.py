#!/usr/bin/env python3
"""
TESTE RÁPIDO - 1 lead para confirmar funcionamento
"""

import os
import sys
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Token atualizado
TOKEN = "EAAHUCvWVsdgBPLLcZCYCfrKPWMUZBRHCstJhmuAZBNLUB1tCrLeXshgqH7B5ylSmlkKHB2I934AW6rHnzOODlpcSRwixUZCx5katC9wZAhwE6M2GjFnGN2V0ZAjZB9eONmyY6A0LWKaCz2uyyYnIQpl5Ddvw3BVV0cWXBlekkjzKofDraA6ZCEPqCjCUOUSYkVolUc7BMtHti70Qem02Wtw5IwDMEnLCkAYZCZBoUGaLGDg1PuNNkZD"

# Configurar environment
os.environ['WHATSAPP_ACCESS_TOKEN'] = TOKEN

# Templates a testar (ricardo são utility/marketing)
test_templates = [
    'ricardo_template_1753485474_512444ac',
    'ricardo_template_1753485590_b501867c', 
    'ricardo_template_1753485563_5882b9ba',
    'ricardo_template_1753487895_cbe4d528'
]

# Phone numbers da BM
phone_numbers = [
    '725492557312328', '800312496489716', '776788602173980', '774576132396207'
]

def test_single_lead():
    """Testa envio para 1 lead com múltiplos templates"""
    
    print("🧪 TESTE SINGLE LEAD:")
    print(f"📱 Token: {TOKEN[:30]}...")
    print(f"📞 Phone Numbers: {len(phone_numbers)}")
    print(f"📝 Templates: {len(test_templates)}")
    print("")
    
    # Criar WhatsApp service
    whatsapp = WhatsAppBusinessAPI()
    whatsapp._access_token = TOKEN
    whatsapp._business_account_id = '2089992404820473'
    
    # Lead de teste
    test_phone = '+5561999114066'  # Pedro do arquivo
    test_name = 'Pedro'
    test_cpf = '06537080177'
    
    success_count = 0
    
    for i, template in enumerate(test_templates):
        phone_id = phone_numbers[i % len(phone_numbers)]
        
        print(f"📤 TESTE {i+1}: {template}")
        print(f"   📱 Para: {test_phone}")
        print(f"   📞 Phone ID: {phone_id}")
        
        try:
            success, response = whatsapp.send_template_message(
                test_phone, template, 'en', 
                [test_cpf, test_name], 
                phone_id
            )
            
            if success:
                success_count += 1
                message_id = response.get('messageId', 'N/A') if isinstance(response, dict) else 'N/A'
                print(f"   ✅ SUCESSO! Message ID: {message_id}")
            else:
                error_msg = str(response)[:100] if response else 'Unknown'
                print(f"   ❌ FALHOU: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ EXCEÇÃO: {str(e)[:100]}")
        
        print("")
    
    print(f"📊 RESULTADO FINAL:")
    print(f"✅ Sucessos: {success_count}/{len(test_templates)}")
    print(f"❌ Falhas: {len(test_templates) - success_count}/{len(test_templates)}")
    
    if success_count > 0:
        print("")
        print("🎉 SISTEMA FUNCIONANDO!")
        print("🚀 Pronto para processar os 18K leads!")
        return True
    else:
        print("")
        print("⚠️ Nenhum template funcionou - investigar mais")
        return False

if __name__ == "__main__":
    test_single_lead()