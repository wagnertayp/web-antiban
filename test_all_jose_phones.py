#!/usr/bin/env python3
"""
Script para testar envio de mensagens de todos os 5 números da BM Jose Carlos
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Configurações
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
BASE_URL = "https://graph.facebook.com/v22.0"

# Phone Numbers da BM Jose Carlos (639849885789886)
JOSE_PHONES = [
    {"id": "746209145234709", "name": "15558104254 (Jose Carlos Raimundo Dos Santos)"},
    {"id": "782640984922130", "name": "+1 940-364-8302 (Jose Carlos Tabelião)"},
    {"id": "775859882269062", "name": "+1 979-346-7705 (Tabelião Jose Carlos Raimundo Dos Santos)"},
    {"id": "745498515309824", "name": "+1 571-661-2703 (Tabelião Jose Carlos Raimundo)"},
    {"id": "652047048001128", "name": "+1 831-833-3522 (Tabelião Jose Carlos Raimundo)"}
]

# Template aprovado
TEMPLATE_NAME = "jose_template_1752924484_01d5f008"

# Dados para teste
TEST_DATA = {
    "cpf": "061.999.114-06",
    "nome": "Teste José",
    "numero": "5561999114066"
}

def send_template_message(phone_id, phone_name, to_number, template_name, cpf, nome):
    """Envia mensagem usando template aprovado"""
    url = f"{BASE_URL}/{phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Payload do template
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
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
    
    print(f"\n🚀 ENVIANDO de {phone_name} (ID: {phone_id})")
    print(f"   Para: {to_number}")
    print(f"   Template: {template_name}")
    print(f"   CPF: {cpf}, Nome: {nome}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   ✅ SUCESSO! Message ID: {message_id}")
            return True, message_id
        else:
            print(f"   ❌ ERRO {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ EXCEÇÃO: {str(e)}")
        return False, None

def main():
    """Função principal"""
    print("=" * 80)
    print("🔥 TESTE TODOS OS 5 NÚMEROS DA BM JOSE CARLOS")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📱 Número destino: {TEST_DATA['numero']}")
    print(f"🏢 Business Manager: Jose Carlos (639849885789886)")
    print(f"📋 Template: {TEMPLATE_NAME}")
    print("=" * 80)
    
    if not WHATSAPP_ACCESS_TOKEN:
        print("❌ ERRO: WHATSAPP_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
        return
    
    success_count = 0
    total_phones = len(JOSE_PHONES)
    
    for i, phone in enumerate(JOSE_PHONES, 1):
        print(f"\n📞 TESTE {i}/{total_phones}")
        
        success, message_id = send_template_message(
            phone_id=phone["id"],
            phone_name=phone["name"],
            to_number=TEST_DATA["numero"],
            template_name=TEMPLATE_NAME,
            cpf=TEST_DATA["cpf"],
            nome=TEST_DATA["nome"]
        )
        
        if success:
            success_count += 1
        
        # Pausa entre envios para evitar rate limit
        if i < total_phones:
            print(f"   ⏳ Aguardando 2 segundos...")
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print("📊 RESULTADO FINAL")
    print("=" * 80)
    print(f"✅ Mensagens enviadas com sucesso: {success_count}/{total_phones}")
    print(f"❌ Mensagens com erro: {total_phones - success_count}/{total_phones}")
    print(f"📈 Taxa de sucesso: {(success_count/total_phones)*100:.1f}%")
    
    if success_count == total_phones:
        print("\n🎉 TODOS OS 5 NÚMEROS FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Sistema pronto para MEGA LOTE com velocidade 5x")
    elif success_count > 0:
        print(f"\n⚠️  {success_count} números funcionando, {total_phones - success_count} com problemas")
    else:
        print("\n💥 NENHUM NÚMERO FUNCIONANDO - VERIFICAR CONFIGURAÇÃO")
    
    print("=" * 80)

if __name__ == "__main__":
    main()