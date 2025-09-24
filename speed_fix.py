#!/usr/bin/env python3
"""
SPEED FIX - Resolver problema de travamento e baixa velocidade
Sistema configurado para 300 mensagens/segundo sem travamentos
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from collections import defaultdict
import os
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

class HighSpeedDispatcher:
    """
    Sistema de envio de alta velocidade otimizado para 300 msg/sec
    Resolve problemas de travamento e garante distribuição correta
    """
    
    def __init__(self, phone_numbers, templates, token):
        self.phone_numbers = phone_numbers
        self.templates = templates 
        self.token = token
        self.sent_count = 0
        self.failed_count = 0
        self.total_count = 0
        self.start_time = None
        self.lock = threading.Lock()
        
    def send_batch_fast(self, leads_batch, batch_index):
        """Envia lote de mensagens de forma rápida e estável"""
        try:
            from services.whatsapp_business_api import WhatsAppBusinessAPI
            
            # Create service instance
            whatsapp = WhatsAppBusinessAPI()
            whatsapp._access_token = self.token
            whatsapp._business_account_id = "2089992404820473"
            
            batch_sent = 0
            batch_failed = 0
            
            for i, lead in enumerate(leads_batch):
                try:
                    # DISTRIBUIÇÃO INTELIGENTE
                    global_index = (batch_index * len(leads_batch)) + i
                    phone_index = (global_index // 1000) % len(self.phone_numbers)
                    phone_id = self.phone_numbers[phone_index]['id'] if isinstance(self.phone_numbers[phone_index], dict) else self.phone_numbers[phone_index]
                    template = self.templates[global_index % len(self.templates)]
                    
                    # Format phone
                    phone = str(lead.get('numero', ''))
                    if not phone.startswith('+'):
                        phone = '+55' + phone if len(phone) == 11 else '+' + phone
                    
                    # Send message
                    result = whatsapp.send_template_message(
                        phone_number_id=phone_id,
                        to=phone,
                        template_name=template,
                        parameters=[lead.get('cpf', ''), lead.get('nome', '')]
                    )
                    
                    if result.get('success'):
                        batch_sent += 1
                    else:
                        batch_failed += 1
                        
                    # Micro delay for 300 msg/sec (0.0033s per message)
                    time.sleep(0.003)
                    
                except Exception as e:
                    batch_failed += 1
                    logging.error(f"Error sending to {lead.get('numero', 'unknown')}: {e}")
            
            # Update counters thread-safely
            with self.lock:
                self.sent_count += batch_sent
                self.failed_count += batch_failed
                
                # Calculate speed
                elapsed = time.time() - self.start_time if self.start_time else 1
                current_speed = self.sent_count / elapsed
                
                logging.info(f"🚀 BATCH {batch_index}: {batch_sent} sent, {batch_failed} failed | Speed: {current_speed:.1f} msg/sec")
                
            return batch_sent, batch_failed
            
        except Exception as e:
            logging.error(f"Batch {batch_index} failed: {e}")
            return 0, len(leads_batch)
    
    def process_leads_ultra_fast(self, leads):
        """Processa leads com velocidade ultra-rápida de 300 msg/sec"""
        try:
            self.total_count = len(leads)
            self.start_time = time.time()
            
            # Randomize leads to avoid patterns
            random.shuffle(leads)
            
            # Create batches of 50 leads each for optimal performance
            batch_size = 50
            batches = [leads[i:i+batch_size] for i in range(0, len(leads), batch_size)]
            
            logging.info(f"🚀 ULTRA FAST: Processing {len(leads)} leads in {len(batches)} batches")
            
            # Use ThreadPoolExecutor with optimal worker count
            max_workers = min(50, len(batches))  # 50 concurrent batches max
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all batches
                future_to_batch = {
                    executor.submit(self.send_batch_fast, batch, i): i 
                    for i, batch in enumerate(batches)
                }
                
                # Process completed batches
                for future in as_completed(future_to_batch):
                    batch_index = future_to_batch[future]
                    try:
                        sent, failed = future.result()
                        logging.info(f"✅ Batch {batch_index} completed: {sent} sent, {failed} failed")
                    except Exception as e:
                        logging.error(f"❌ Batch {batch_index} exception: {e}")
            
            # Final statistics
            elapsed_time = time.time() - self.start_time
            final_speed = self.sent_count / elapsed_time if elapsed_time > 0 else 0
            
            logging.info(f"🎯 FINAL RESULT: {self.sent_count} sent, {self.failed_count} failed in {elapsed_time:.1f}s")
            logging.info(f"⚡ FINAL SPEED: {final_speed:.1f} messages/second")
            
            return {
                'sent': self.sent_count,
                'failed': self.failed_count,
                'total': self.total_count,
                'speed': final_speed,
                'elapsed_time': elapsed_time
            }
            
        except Exception as e:
            logging.error(f"Ultra fast processing failed: {e}")
            return {
                'sent': self.sent_count,
                'failed': self.failed_count,
                'total': self.total_count,
                'error': str(e)
            }

if __name__ == "__main__":
    print("🚀 SPEED FIX - Sistema de alta velocidade configurado para 300 msg/sec")