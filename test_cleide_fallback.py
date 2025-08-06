#!/usr/bin/env python3
"""
Script para testar fallback inteligente da BM Cleide com erro #135000
"""

import os
import requests
import json
from datetime import datetime

# Token e configurações fornecidas
TEST_TOKEN = "EAAJc6cZAxck4BPAiugr1YWJJmRcNuutBiwONUTwk7qGsftXclDhs3SXzFax2RtiutG0Kx2Jrid6uZB0wCZCsFmGpH9Ee6zKoSp0ywRR0sRYyi1kiG1PZCLoW8JDIc65SDmW4yRZAtD5DDrgbPpYxNixPnMVfbZBTwgoGg6BIjT7vQW483xcDtbCZBzcy3ne6qZC89WzQvdZBDjmAltYv3hMfI82p3M5bGLVh49INMIBPEv2JBMwZDZD"
BUSINESS_ACCOUNT_ID = "580318035149016"
BASE_URL = "https://graph.facebook.com/v22.0"

# Template e dados para teste
TEMPLATE_NAME = "cleide_template_1752692476_0f370e02"
TEST_PHONE = "5561982132603"
TEST_CPF = "061.982.132-60"
TEST_NOME = "Teste Cleide"

# Phone numbers da BM Cleide
CLEIDE_PHONES = [
    {"id": "709194588941211", "name": "15558146853 (Cleide Maria Da Silva)"},
    {"id": "767158596471686", "name": "+1 269-392-0840 (Cleide Maria Tabeliã)"},
    {"id": "739188885941111", "name": "+1 804-210-0219 (Tabeliã Cleide Maria)"},
    {"id": "710232202173614", "name": "+1 830-445-8877 (Tabeliã Cleide Maria)"}
]

def get_template_exact_content(cpf, nome):
    """Gera o conteúdo EXATO do template cleide_template_1752692476_0f370e02"""
    
    # Conteúdo EXATO do template aprovado
    template_content = f"""*Notificação Extrajudicial*

Prezado (a) {nome}, me chamo Cleide Ferrer. Sou tabelião do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{cpf}.*

Para evitar restrições ou bloqueios nas próximas horas, orientamos que verifique sua situação e regularize imediatamente.

Atenciosamente,  
Cartório 5º Ofício de Notas

PROCESSO Nº: 0009-13.2025.0100-NE

Regularizar meu CPF: https://irpf.intimacao.org/{cpf}"""
    
    return template_content

def send_text_message_fallback(phone_id, phone_name, cpf, nome):
    """Envia mensagem de texto com conteúdo EXATO do template (fallback #135000)"""
    print(f"🔄 FALLBACK #135000 - Enviando texto de {phone_name}")
    
    headers = {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{phone_id}/messages"
    
    # Mensagem de texto com conteúdo EXATO do template
    message_text = get_template_exact_content(cpf, nome)
    
    payload = {
        "messaging_product": "whatsapp",
        "to": TEST_PHONE,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   ✅ FALLBACK SUCESSO! Message ID: {message_id}")
            return True, message_id
        else:
            print(f"   ❌ ERRO FALLBACK {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO FALLBACK: {str(e)}")
        return False, None

def send_template_message(phone_id, phone_name, cpf, nome):
    """Tenta enviar template primeiro, usa fallback se erro #135000"""
    print(f"🚀 TENTANDO TEMPLATE de {phone_name} (ID: {phone_id})")
    
    headers = {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{phone_id}/messages"
    
    # Payload do template
    payload = {
        "messaging_product": "whatsapp",
        "to": TEST_PHONE,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": cpf},
                        {"type": "text", "text": nome}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {"type": "text", "text": cpf}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   ✅ TEMPLATE SUCESSO! Message ID: {message_id}")
            return True, message_id, "template"
        else:
            print(f"   ❌ ERRO TEMPLATE {response.status_code}: {response.text}")
            
            # Verificar se é erro #135000
            if "135000" in response.text:
                print(f"   🔥 ERRO #135000 DETECTADO - Aplicando fallback inteligente")
                
                # Aplicar fallback
                success, message_id = send_text_message_fallback(phone_id, phone_name, cpf, nome)
                return success, message_id, "fallback"
            else:
                return False, None, "error"
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {str(e)}")
        return False, None, "error"

def main():
    """Função principal"""
    print("=" * 80)
    print("🔥 TESTE BM CLEIDE - FALLBACK INTELIGENTE #135000")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏢 Business Manager: {BUSINESS_ACCOUNT_ID} (com erro #135000)")
    print(f"📋 Template: {TEMPLATE_NAME}")
    print(f"📱 Número destino: {TEST_PHONE}")
    print(f"🔄 Fallback: Mensagem de texto com conteúdo EXATO do template")
    print("=" * 80)
    
    success_count = 0
    template_count = 0
    fallback_count = 0
    
    for i, phone in enumerate(CLEIDE_PHONES, 1):
        print(f"\n📞 TESTE {i}/{len(CLEIDE_PHONES)}")
        
        success, message_id, method = send_template_message(
            phone["id"], 
            phone["name"], 
            TEST_CPF, 
            TEST_NOME
        )
        
        if success:
            success_count += 1
            if method == "template":
                template_count += 1
            elif method == "fallback":
                fallback_count += 1
        
        # Pausa entre envios
        if i < len(CLEIDE_PHONES):
            print(f"   ⏳ Aguardando 2 segundos...")
            import time
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print("📊 RESULTADO FINAL - BM CLEIDE")
    print("=" * 80)
    print(f"✅ Mensagens enviadas com sucesso: {success_count}/{len(CLEIDE_PHONES)}")
    print(f"📋 Templates diretos: {template_count}")
    print(f"🔄 Fallbacks aplicados: {fallback_count}")
    print(f"📈 Taxa de entrega: {(success_count/len(CLEIDE_PHONES))*100:.1f}%")
    
    if success_count == len(CLEIDE_PHONES):
        print("\n🎉 100% ENTREGA GARANTIDA COM FALLBACK INTELIGENTE!")
        print("🔥 BM Cleide funcionando com sistema anti-erro #135000")
    
    print("=" * 80)

if __name__ == "__main__":
    main()