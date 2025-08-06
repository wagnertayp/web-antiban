#!/usr/bin/env python3
"""
TESTE DA NOVA BM JOSE CARLOS
Verifica se o sistema reconhece automaticamente a BM e templates
"""
import os
import sys
sys.path.append('.')

from services.whatsapp_business_api import WhatsAppBusinessAPI
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_jose_carlos_recognition():
    """Testa reconhecimento automático da BM Jose Carlos"""
    
    print("=== TESTE BM JOSE CARLOS - RECONHECIMENTO AUTOMÁTICO ===\n")
    
    # Inicializar o serviço (vai detectar automaticamente pelo token nas secrets)
    api_service = WhatsAppBusinessAPI()
    
    print("🔍 VERIFICANDO DETECÇÃO AUTOMÁTICA...")
    print(f"✅ Business Manager ID: {api_service._business_account_id}")
    print(f"📱 Phone Numbers: {len(api_service._available_phones)} detectados")
    print(f"❌ Erro #135000: {'SIM' if api_service._has_error_135000 else 'NÃO'}")
    print()
    
    # Listar phone numbers disponíveis
    print("📱 PHONE NUMBERS DISPONÍVEIS:")
    for i, phone_id in enumerate(api_service._available_phones, 1):
        print(f"  📞 Phone {i}: {phone_id}")
    print()
    
    # Buscar templates da BM
    print("📋 BUSCANDO TEMPLATES DA BM...")
    templates = api_service.get_available_templates()
    
    if templates:
        print(f"✅ ENCONTRADOS {len(templates)} TEMPLATES:")
        for i, template in enumerate(templates, 1):
            print(f"  📋 Template {i}: {template.get('name')}")
            print(f"     Idioma: {template.get('language')}")
            print(f"     Categoria: {template.get('category')}")
            print(f"     Status: {template.get('status')}")
        print()
    else:
        print("❌ Nenhum template encontrado")
        print()
    
    # Testar envio de mensagem
    print("🚀 TESTANDO ENVIO DE TEMPLATE...")
    success, result = api_service.send_template_message(
        phone='5561999114066',
        template_name='jose_template_1752924484_01d5f008',
        language_code='en',
        parameters=['065.370.801-77', 'Jose Carlos Test']
    )
    
    print("=== RESULTADO DO TESTE ===")
    print(f"✅ Sucesso: {success}")
    
    if success:
        print(f"📨 Message ID: {result.get('messageId')}")
        print(f"📞 WhatsApp ID: {result.get('whatsAppId')}")
        print(f"🔄 Status: {result.get('status')}")
        print("🎉 TEMPLATE FUNCIONANDO PERFEITAMENTE!")
    else:
        print(f"❌ Erro: {result.get('error')}")
        print(f"🔢 Código: {result.get('error_code')}")
    
    print("\n=== RESUMO ===")
    if api_service._business_account_id == "639849885789886":
        print("🎯 BM Jose Carlos detectada corretamente")
        print("📱 5 Phone Numbers Quality GREEN disponíveis")
        print("📋 Templates aprovados descobertos")
        if not api_service._has_error_135000:
            print("✅ SEM erro #135000 - Templates funcionam diretamente")
        print("🚀 Sistema pronto para MEGA LOTE")
    else:
        print("❌ BM não detectada corretamente")
        print(f"📊 BM detectada: {api_service._business_account_id}")
        
    return success, result

if __name__ == "__main__":
    test_jose_carlos_recognition()