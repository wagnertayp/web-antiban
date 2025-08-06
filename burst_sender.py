#!/usr/bin/env python3
"""
BURST SENDER - Envia 300 mensagens/segundo usando mensagens de texto
com conteúdo EXATO dos templates aprovados para BM com erro #135000
"""

import os
import sys
import time
import requests
import threading
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict

# Token da BM 2089992404820473
TOKEN = "EAAHUCvWVsdgBPLLcZCYCfrKPWMUZBRHCstJhmuAZBNLUB1tCrLeXshgqH7B5ylSmlkKHB2I934AW6rHnzOODlpcSRwixUZCx5katC9wZAhwE6M2GjFnGN2V0ZAjZB9eONmyY6A0LWKaCz2uyyYnIQpl5Ddvw3BVV0cWXBlekkjzKofDraA6ZCEPqCjCUOUSYkVolUc7BMtHti70Qem02Wtw5IwDMEnLCkAYZCZBoUGaLGDg1PuNNkZD"

# Phone numbers da BM 2089992404820473
PHONE_NUMBERS = [
    '725492557312328', '800312496489716', '776788602173980', '774576132396207',
    '764495823408049', '764138826774184', '749599158230143', '747868138404614', 
    '746367015221228', '736306482898341', '732911983238956', '728240807037686',
    '721222711076869', '718291801369739', '712294161968633', '706148559252459',
    '698088016726677', '674341985771514', '672331669304211', '670736396133662'
]

# Conteúdo EXATO dos templates aprovados (sem usar API de templates)
TEMPLATE_CONTENTS = [
    "Olá {nome}, você tem intimação no cartório. Acesse https://intimacao.org/{cpf} para visualizar. Tabelião Ricardo Iara",
    "Prezado {nome}, nova intimação disponível. CPF: {cpf}. Consulte: https://intimacao.org/{cpf}. Cartório Ricardo",  
    "Intimação para {nome}. Documento: {cpf}. Link: https://intimacao.org/{cpf}. Tabelião Ricardo Iara",
    "Sr(a) {nome}, intimação urgente. CPF {cpf}. Acesse: https://intimacao.org/{cpf}. Cartório",
    "Atenção {nome}! Intimação disponível para CPF {cpf}. Link: https://intimacao.org/{cpf}. Tabelião Ricardo"
]

# Contadores globais thread-safe
sent_count = 0
failed_count = 0
count_lock = threading.Lock()

def send_text_message(phone: str, message: str, phone_id: str) -> Tuple[bool, str]:
    """Envia mensagem de texto via WhatsApp API"""
    try:
        url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Formatar número
        formatted_phone = phone
        if phone.startswith('55'):
            formatted_phone = '+' + phone
        elif not phone.startswith('+'):
            formatted_phone = '+55' + phone
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': formatted_phone,  
            'type': 'text',
            'text': {'body': message}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            if messages:
                message_id = messages[0].get('id', 'N/A')
                return True, message_id
            else:
                return False, 'No messages in response'
        else:
            error_data = response.json() if response.content else {}
            return False, f"HTTP {response.status_code}: {error_data}"
            
    except Exception as e:
        return False, str(e)

def process_lead(lead_data: str, phone_id: str, template_content: str) -> None:
    """Processa um lead individual"""
    global sent_count, failed_count
    
    try:
        # Parse lead: phone,name,cpf
        parts = lead_data.strip().split(',')
        if len(parts) >= 3:
            phone = parts[0].strip()
            name = parts[1].strip()  
            cpf = parts[2].strip()
            
            # Criar mensagem com conteúdo do template
            message = template_content.replace('{nome}', name).replace('{cpf}', cpf)
            
            # Enviar mensagem
            success, result = send_text_message(phone, message, phone_id)
            
            with count_lock:
                if success:
                    sent_count += 1
                    print(f"✅ ENVIADA {sent_count}: {phone[:5]}***{phone[-4:]} | {name[:10]} | ID: {result[:15]}...")
                else:
                    failed_count += 1  
                    error_msg = str(result)[:50]
                    print(f"❌ FALHA {failed_count}: {phone[-8:]} | Erro: {error_msg}")
        else:
            with count_lock:
                failed_count += 1
                print(f"❌ FALHA {failed_count}: Lead inválido: {lead_data[:30]}")
                
    except Exception as e:
        with count_lock:
            failed_count += 1
            print(f"❌ FALHA {failed_count}: Exceção: {str(e)[:50]}")

def process_burst(leads: List[str], burst_size: int = 300) -> Dict:
    """Processa burst de leads com distribuição inteligente"""
    global sent_count, failed_count
    
    start_time = time.time()
    total_leads = len(leads)
    
    print(f"🚀 INICIANDO BURST: {total_leads} leads, {burst_size} por burst")
    print(f"📱 Distribuindo entre {len(PHONE_NUMBERS)} phone numbers")
    print("")
    
    # Processar em bursts
    for burst_start in range(0, total_leads, burst_size):
        burst_leads = leads[burst_start:burst_start + burst_size]
        burst_num = (burst_start // burst_size) + 1
        
        print(f"💥 BURST {burst_num}: {len(burst_leads)} leads")
        
        # Distribuir leads entre phone numbers e templates
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            
            for i, lead in enumerate(burst_leads):
                phone_id = PHONE_NUMBERS[i % len(PHONE_NUMBERS)]
                template_content = TEMPLATE_CONTENTS[i % len(TEMPLATE_CONTENTS)]
                
                future = executor.submit(process_lead, lead, phone_id, template_content)
                futures.append(future)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                future.result()  # Captura exceptions
        
        # Estatísticas do burst
        burst_time = time.time() - start_time
        speed = (sent_count + failed_count) / burst_time if burst_time > 0 else 0
        
        print(f"✅ BURST {burst_num} COMPLETO: {sent_count} enviadas, {failed_count} falharam | {speed:.1f} msg/sec")
        
        # Limpeza de memória entre bursts
        gc.collect()
        
        # Pausa curta entre bursts
        if burst_start + burst_size < total_leads:
            time.sleep(0.5)
    
    # Estatísticas finais
    total_time = time.time() - start_time
    total_processed = sent_count + failed_count
    avg_speed = total_processed / total_time if total_time > 0 else 0
    
    print(f"📊 TOTAL GERAL: {sent_count} enviadas, {failed_count} falharam")
    print(f"📊 PROGRESSO ATUAL: {total_processed}/{total_leads} ({(total_processed/total_leads)*100:.1f}%)")
    print(f"⚡ VELOCIDADE: {avg_speed:.1f} msg/sec")
    print(f"⏱️ TEMPO: {total_time:.1f}s")
    
    return {
        'sent': sent_count,
        'failed': failed_count,
        'total_time': total_time,
        'speed': avg_speed
    }

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 BURST SENDER - MENSAGENS DE TEXTO COM CONTEÚDO DE TEMPLATES")
    print("=" * 60)
    
    # Carregar leads
    try:
        with open('attached_assets/Pasted-5548998019385-GIRLIAN-PASSOS-GUIMARAES-08332990939-5561999114066-Pedro-06537080177-5519993086424-JAC-1753812324550_1753812324552.txt', 'r') as f:
            leads_data = f.read()
        
        leads = [line.strip() for line in leads_data.strip().split('\n') if line.strip()]
        print(f"📋 CARREGADOS: {len(leads)} leads")
        
        # Processar com sistema burst
        result = process_burst(leads, burst_size=300)
        
        print("")
        print("=" * 60)
        print("🎯 PROCESSAMENTO COMPLETO!")
        print(f"✅ Enviadas: {result['sent']}")
        print(f"❌ Falharam: {result['failed']}")
        print(f"⚡ Velocidade média: {result['speed']:.1f} msg/sec")  
        print(f"⏱️ Tempo total: {result['total_time']:.1f} segundos")
        print("=" * 60)
        
    except FileNotFoundError:
        print("❌ Arquivo de leads não encontrado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()