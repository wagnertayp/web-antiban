#!/usr/bin/env python3
"""
Teste específico do template maria_template_1753924898_0fdcf437
"""

import os
import sys
import logging
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_maria_template():
    """Send specific maria template to the target number"""
    
    # Set the exact token as environment variable
    os.environ['WHATSAPP_ACCESS_TOKEN'] = "EAAKO6zbFUSwBPHReXSemlG3px1ZCnBBdLJ9KaCaZCm3TE1iZCIIhHhc2a8zkCouLAsb8G6tF8PWAyTjeHWCvbavHGsZCJZCBI1CnPu8XHZArw0TAyzxcZCtYZAhvRio7ZBZCivj25r0STRlB6ZCiXRwunr9zwSG4nOBWTk6XTjZCgZCo1ZA3D0NykiufaDcrbds051Sqw6MCo83BzIO26EZBFsdZA0jE5I839MWRZAUhiqi9g8NMp5sWDEQZCHEbAJu9dLiYFaREgZD"
    
    # Initialize WhatsApp API
    whatsapp_api = WhatsAppBusinessAPI()
    
    # Target details
    target_phone = "5561999114066"
    template_name = "maria_template_1753924898_0fdcf437"
    language_code = "en"
    
    # Parameters: CPF, Nome (conforme ordem correta)
    parameters = ["065.370.801-77", "Pedro"]
    
    print(f"🚀 ENVIANDO TEMPLATE MARIA ESPECÍFICO")
    print(f"📱 Número: +{target_phone}")
    print(f"📋 Template: {template_name}")
    print(f"🌍 Idioma: {language_code}")
    print(f"📝 Parâmetros: {parameters}")
    print(f"🏢 Business Manager: 721254414139146")
    print("=" * 60)
    
    try:
        success, result = whatsapp_api.send_template_message(
            phone=target_phone,
            template_name=template_name,
            language_code=language_code,
            parameters=parameters
        )
        
        if success:
            print(f"✅ SUCESSO: Template enviado!")
            print(f"📨 Message ID: {result.get('messageId', 'N/A')}")
            print(f"📋 Status: {result.get('status', 'N/A')}")
            
            # Check if message actually sent or used fallback
            if result.get('status') == 'sent_as_text':
                print(f"⚠️  NOTA: Template falhou com erro #135000 mas fallback enviou como texto")
                print(f"📄 A mensagem chegou ao destinatário com o conteúdo do template")
            elif result.get('status') == 'sent':
                print(f"🎯 PERFEITO: Template enviado diretamente sem fallback!")
            
            # Show contact resolution details
            if 'contacts' in result and result['contacts']:
                contact = result['contacts'][0]
                wa_id = contact.get('wa_id', 'N/A')
                input_phone = contact.get('input', 'N/A')
                print(f"📞 Input: {input_phone} -> WhatsApp ID: {wa_id}")
            
            return True
            
        else:
            error_code = result.get('error_code', 'N/A')
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ FALHOU: Erro #{error_code}: {error_msg}")
            
            # Try to understand the specific error
            if error_code == 135000:
                print("🔍 DIAGNÓSTICO: Erro #135000 - Business Manager não suporta este template")
                print("💡 SOLUÇÃO: O fallback deveria ter funcionado, mas algo bloqueou")
            elif error_code == 132001:
                print("🔍 DIAGNÓSTICO: Template não existe ou linguagem incorreta")
            elif error_code == 100:
                print("🔍 DIAGNÓSTICO: Token sem permissões para este Phone Number ID")
            
            return False
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_maria_template()
    
    if success:
        print("\n🎉 TEMPLATE MARIA ENVIADO COM SUCESSO!")
        print("📱 Verifique o WhatsApp do destinatário para confirmar recebimento")
    else:
        print("\n💥 FALHA NO ENVIO DO TEMPLATE MARIA")
        print("🔧 Verifique os logs acima para detalhes do erro")
    
    sys.exit(0 if success else 1)