#!/usr/bin/env python3
"""
MEGA BATCH SENDER - Sistema de envio interno de 17K leads
Mesmo esquema do sistema burst: 300 msg/sec, limpeza de memória, distribuição inteligente
"""

import os
import time
import logging
import gc
import random
from services.whatsapp_business_api import WhatsAppBusinessAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MegaBatchSender:
    """
    Sistema de envio massivo interno - 17K leads em velocidade record
    Mesmo esquema do sistema burst: 300 msg/sec com limpeza automática
    """
    
    def __init__(self, token, phone_numbers, templates):
        self.token = token
        self.phone_numbers = phone_numbers
        self.templates = templates
        self.sent_count = 0
        self.failed_count = 0
        
        # Configurar WhatsApp service
        self.whatsapp = WhatsAppBusinessAPI()
        self.whatsapp._access_token = token
        self.whatsapp._business_account_id = "2089992404820473"
        
        logging.info(f"🚀 MEGA BATCH SENDER INITIALIZED:")
        logging.info(f"📱 Phone Numbers: {len(phone_numbers)}")
        logging.info(f"📝 Templates: {len(templates)}")
        logging.info(f"🎯 Target Speed: 300 msg/sec")
    
    def send_burst(self, leads_chunk, start_position):
        """
        Envia uma rajada com velocidade máxima e status em tempo real
        """
        burst_start = time.time()
        burst_sent = 0
        burst_failed = 0
        
        print(f"💥 BURST {start_position//500 + 1}: Enviando {len(leads_chunk)} mensagens...")
        
        for i, lead in enumerate(leads_chunk):
            try:
                # Calculate global position for distribution
                global_pos = start_position + i
                
                # Distribute across phone numbers (1000 per phone)
                phone_idx = (global_pos // 1000) % len(self.phone_numbers)
                phone_id = self.phone_numbers[phone_idx]
                template = self.templates[global_pos % len(self.templates)]
                
                # Format phone number
                phone = str(lead.get('numero', ''))
                if not phone.startswith('+'):
                    phone = '+55' + phone if len(phone) == 11 else '+' + phone
                
                # Send message using WhatsApp API - CORRIGIR PARÂMETROS
                success, response = self.whatsapp.send_template_message(
                    phone, template, 'en', 
                    [lead.get('cpf', ''), lead.get('nome', '')], 
                    phone_id
                )
                
                if success:
                    burst_sent += 1
                    self.sent_count += 1
                    
                    # Log message ID for confirmation (mais frequente)
                    message_id = response.get('messageId', 'N/A') if isinstance(response, dict) else 'N/A'
                    if i % 50 == 0 or burst_sent % 50 == 0:  # Log every 50 messages
                        print(f"✅ MSG {global_pos}: {phone[-8:]} | Phone {phone_idx+1} | ID: {message_id[:20]}...")
                else:
                    burst_failed += 1
                    self.failed_count += 1
                    error_msg = str(response)[:30] if response else 'Unknown'
                    print(f"❌ FALHA {global_pos}: {phone[-8:]} | Erro: {error_msg}")
                
                # VELOCIDADE MÁXIMA: Mínimo delay possível
                time.sleep(0.001)  # 1ms = 1000 msg/sec teórico
                
            except Exception as e:
                burst_failed += 1
                self.failed_count += 1
                print(f"❌ EXCEÇÃO {global_pos}: {str(e)[:50]}")
        
        # Log burst completion com status detalhado
        burst_time = time.time() - burst_start
        burst_speed = len(leads_chunk) / burst_time if burst_time > 0 else 0
        
        print(f"✅ BURST COMPLETO: {burst_sent} enviadas, {burst_failed} falharam | {burst_speed:.1f} msg/sec")
        print(f"📊 TOTAL GERAL: {self.sent_count} enviadas, {self.failed_count} falharam")
        
        return burst_sent, burst_failed
    
    def process_leads(self, leads, resume_from=0):
        """
        Processa todos os leads com velocidade máxima e recuperação automática
        """
        # Randomize leads for better distribution (only if starting fresh)
        if resume_from == 0:
            random.shuffle(leads)
        
        total_leads = len(leads)
        burst_size = 500  # Aumentado para 500 para velocidade máxima
        total_bursts = (total_leads + burst_size - 1) // burst_size
        start_burst = resume_from // burst_size
        
        print(f"🎯 INICIANDO PROCESSAMENTO:")
        print(f"📊 Total: {total_leads} leads")
        print(f"💥 Rajadas: {total_bursts} de {burst_size} cada")
        print(f"🔄 Retomando do lead: {resume_from}")
        print(f"⚡ Velocidade alvo: 1000+ msg/sec")
        print("=" * 60)
        
        start_time = time.time()
        last_update = time.time()
        
        for burst_num in range(start_burst, total_bursts):
            burst_start_time = time.time()
            start_idx = burst_num * burst_size
            end_idx = min(start_idx + burst_size, total_leads)
            
            # Skip leads before resume point
            if start_idx < resume_from:
                start_idx = resume_from
            
            burst_leads = leads[start_idx:end_idx]
            
            if not burst_leads:
                continue
            
            # STATUS EM TEMPO REAL
            processed_before = self.sent_count + self.failed_count
            progress_before = (processed_before / total_leads) * 100
            
            print(f"\n🚀 RAJADA {burst_num + 1}/{total_bursts}")
            print(f"📍 Posição: {start_idx}-{end_idx-1} ({len(burst_leads)} leads)")
            print(f"📊 Progresso: {processed_before}/{total_leads} ({progress_before:.1f}%)")
            
            # Send burst
            burst_sent, burst_failed = self.send_burst(burst_leads, start_idx)
            
            # Calculate real-time progress
            processed = self.sent_count + self.failed_count
            progress = (processed / total_leads) * 100
            elapsed = time.time() - start_time
            current_speed = processed / elapsed if elapsed > 0 else 0
            
            # STATUS DETALHADO EM TEMPO REAL
            print(f"📊 PROGRESSO ATUAL: {processed}/{total_leads} ({progress:.1f}%)")
            print(f"⚡ VELOCIDADE: {current_speed:.1f} msg/sec")
            print(f"⏱️ TEMPO: {elapsed:.1f}s")
            
            # DETECTOR DE TRAVAMENTO
            current_time = time.time()
            if current_time - last_update > 30:  # 30 segundos sem progresso
                print("⚠️ POSSÍVEL TRAVAMENTO DETECTADO!")
                print(f"🔄 Salvando progresso na posição: {processed}")
                # Salvar estado para recuperação
                with open('recovery_state.txt', 'w') as f:
                    f.write(f"{processed}")
                print("💾 Estado salvo para recuperação")
            
            last_update = current_time
            
            # MEMORY CLEANUP mais agressivo para velocidade máxima
            del burst_leads
            gc.collect()
            
            # Pausa mínima para estabilidade (reduzida para velocidade máxima)
            time.sleep(0.01)  # 10ms apenas
        
        # Final statistics
        total_time = time.time() - start_time
        final_speed = self.sent_count / total_time if total_time > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 PROCESSAMENTO COMPLETO!")
        print(f"✅ Enviadas: {self.sent_count}")
        print(f"❌ Falharam: {self.failed_count}")
        print(f"⚡ Velocidade média: {final_speed:.1f} msg/sec")
        print(f"⏱️ Tempo total: {total_time:.1f} segundos")
        print("=" * 60)
        
        return {
            'sent': self.sent_count,
            'failed': self.failed_count,
            'total_time': total_time,
            'speed': final_speed
        }

def send_mega_batch(token, leads_data, phone_numbers, templates):
    """
    Função principal para envio massivo de leads
    """
    try:
        # Parse leads data
        leads = []
        for line in leads_data.strip().split('\n'):
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    leads.append({
                        'numero': parts[0].strip(),
                        'nome': parts[1].strip(),
                        'cpf': parts[2].strip()
                    })
        
        logging.info(f"📋 PARSED LEADS: {len(leads)} valid entries")
        
        # Create sender and process
        sender = MegaBatchSender(token, phone_numbers, templates)
        result = sender.process_leads(leads)
        
        return result
        
    except Exception as e:
        logging.error(f"Mega batch failed: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🚀 MEGA BATCH SENDER - Ready for 17K leads")
    print("📝 Usage: send_mega_batch(token, leads_data, phone_numbers, templates)")