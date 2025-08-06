"""
ULTRA-SPEED SMART DISTRIBUTION - FIXED VERSION
Addresses the critical Phone ID 'None' issue by completely rewriting the distribution logic
"""

import threading
import concurrent.futures
import time
import logging
import gc
from services.whatsapp_business_api import WhatsAppBusinessAPI

def ultra_speed_distribution(leads, template_names, phone_number_ids):
    """
    MAXIMUM SPEED distribution with proper phone ID handling
    """
    logging.info(f"🚀 ULTRA-SPEED DISTRIBUTION STARTING")
    logging.info(f"📊 {len(leads)} leads, {len(template_names)} templates, {len(phone_number_ids)} phones")
    
    # Validate phone IDs first
    valid_phones = [pid for pid in phone_number_ids if pid and pid != 'None']
    if not valid_phones:
        logging.error("❌ No valid phone IDs provided")
        return {'total_sent': 0, 'total_errors': len(leads), 'error': 'Invalid phone IDs'}
    
    # Counters and locks
    total_sent = 0
    total_errors = 0
    counter_lock = threading.Lock()
    
    def send_message_worker(lead, phone_id, template_name, worker_id):
        """Individual worker for sending one message"""
        try:
            # Validate inputs
            if not phone_id or phone_id == 'None':
                logging.error(f"⚡ Worker-{worker_id}: ❌ Invalid phone ID: {phone_id}")
                return False
                
            # Get WhatsApp service
            whatsapp = WhatsAppBusinessAPI()
            
            # Format phone number
            phone = lead['numero']
            if not phone.startswith('+'):
                if phone.startswith('55'):
                    phone = '+' + phone
                elif len(phone) == 11:
                    phone = '+55' + phone
                else:
                    phone = '+55' + phone
            
            # Send message
            success = whatsapp.send_template_message(
                phone, template_name, [lead['cpf'], lead['nome']], phone_id
            )
            
            if success:
                logging.info(f"⚡ Worker-{worker_id}: ✅ {lead['nome']} - {phone} via {phone_id[:15]}...")
                return True
            else:
                logging.warning(f"⚡ Worker-{worker_id}: ❌ {lead['nome']} - {phone}")
                return False
                
        except Exception as e:
            logging.error(f"⚡ Worker-{worker_id}: ❌ {lead['nome']}: {e}")
            return False
    
    # Create workers - distribute across phones and templates
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        futures = []
        worker_id = 0
        
        for lead in leads:
            # Round-robin phone selection
            phone_id = valid_phones[worker_id % len(valid_phones)]
            # Round-robin template selection  
            template_name = template_names[worker_id % len(template_names)]
            
            # Submit worker
            future = executor.submit(send_message_worker, lead, phone_id, template_name, worker_id)
            futures.append(future)
            worker_id += 1
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    with counter_lock:
                        total_sent += 1
                else:
                    with counter_lock:
                        total_errors += 1
            except Exception:
                with counter_lock:
                    total_errors += 1
    
    logging.info(f"🏁 ULTRA-SPEED DISTRIBUTION COMPLETE: {total_sent} sent, {total_errors} errors")
    
    return {
        'total_sent': total_sent,
        'total_errors': total_errors,
        'success': True
    }