"""
Ultra-Fast Batch Processing System for WhatsApp Messages
Processes messages in batches of 100 with automatic memory cleanup and system restart
"""

import os
import gc
import json
import time
import logging
import threading
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.whatsapp_business_api import WhatsAppBusinessAPI

class BatchProcessor:
    """High-performance batch processor for WhatsApp messages"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppBusinessAPI()
        self.batch_size = 30      # Lotes maiores para mais velocidade
        self.max_workers = 20     # Mais threads concorrentes por lote
        self.is_running = False
        self.should_stop = False
        self.campaign_id = None
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Progress tracking
        self.progress_file = 'batch_progress.json'
        
    def save_progress(self, campaign_id: int, batch_index: int, total_batches: int, 
                     processed: int, success: int, errors: int):
        """Save current progress to file for resumption"""
        progress_data = {
            'campaign_id': campaign_id,
            'batch_index': batch_index,
            'total_batches': total_batches,
            'processed': processed,
            'success': success,
            'errors': errors,
            'timestamp': datetime.now().isoformat(),
            'template': 'modelo_5'  # Current template
        }
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f)
            logging.info(f"PROGRESS SAVED: Batch {batch_index}/{total_batches}, {processed} processed")
        except Exception as e:
            logging.error(f"Error saving progress: {e}")
    
    def load_progress(self) -> Optional[Dict]:
        """Load saved progress for resumption"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                logging.info(f"PROGRESS LOADED: Campaign {progress['campaign_id']}, Batch {progress['batch_index']}")
                return progress
        except Exception as e:
            logging.error(f"Error loading progress: {e}")
        return None
    
    def clear_progress(self):
        """Clear progress file when complete"""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
                logging.info("PROGRESS CLEARED: Processing complete")
        except Exception as e:
            logging.error(f"Error clearing progress: {e}")
    
    def process_mega_campaign(self, leads: List[Dict], template_name: str = 'modelo_5') -> Dict:
        """
        Process mega campaign with automatic batching and restart
        """
        self.is_running = True
        self.should_stop = False
        
        total_leads = len(leads)
        total_batches = (total_leads + self.batch_size - 1) // self.batch_size
        
        # Check for existing progress
        progress = self.load_progress()
        start_batch = 0
        
        if progress:
            logging.info(f"RESUMING CAMPAIGN: {progress['campaign_id']} from batch {progress['batch_index']}")
            start_batch = progress['batch_index']
            self.processed_count = progress['processed']
            self.success_count = progress['success']
            self.error_count = progress['errors']
            self.campaign_id = progress['campaign_id']
        else:
            logging.info(f"STARTING MEGA CAMPAIGN: {total_leads} leads in {total_batches} batches")
            # Use timestamp as campaign ID for simplicity
            self.campaign_id = int(datetime.now().timestamp())
            
            # Save initial progress immediately
            self.save_progress(
                self.campaign_id,
                0,
                total_batches,
                0,
                0,
                0
            )
        
        # Process batches
        for batch_index in range(start_batch, total_batches):
            if self.should_stop:
                logging.info(f"BATCH PROCESSING STOPPED by user at batch {batch_index}")
                break
                
            # Calculate batch range
            start_idx = batch_index * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_leads)
            batch_leads = leads[start_idx:end_idx]
            
            logging.info(f"PROCESSING BATCH {batch_index + 1}/{total_batches}: {len(batch_leads)} leads")
            
            # Process batch with ultra-fast parallel sending
            batch_success, batch_errors = self.process_batch_ultra_fast(batch_leads, template_name)
            
            # Update counters
            self.processed_count += len(batch_leads)
            self.success_count += batch_success
            self.error_count += batch_errors
            
            # Save progress
            self.save_progress(
                self.campaign_id,
                batch_index + 1,
                total_batches,
                self.processed_count,
                self.success_count,
                self.error_count
            )
            
            # Log batch completion
            logging.info(f"BATCH {batch_index + 1} COMPLETE: {batch_success} success, {batch_errors} errors")
            
            # Memory cleanup between batches
            self.cleanup_memory()
            
            # Delay ultra reduzido para máxima velocidade
            time.sleep(0.3)  # Pausa mínima para garantir estabilidade
        
        # Final status
        final_status = 'completed' if self.processed_count == total_leads else 'stopped'
        
        # Log final results
        logging.info(f"MEGA BATCH FINAL RESULTS: {self.success_count} success, {self.error_count} errors, Status: {final_status}")
        
        # Save final progress
        if self.campaign_id:
            self.save_progress(
                self.campaign_id,
                total_batches,
                total_batches,
                self.processed_count,
                self.success_count,
                self.error_count
            )
        
        # Clear progress if complete
        if final_status == 'completed':
            self.clear_progress()
        
        self.is_running = False
        
        return {
            'status': final_status,
            'total_leads': total_leads,
            'processed': self.processed_count,
            'success': self.success_count,
            'errors': self.error_count,
            'batches_processed': batch_index + 1 if not self.should_stop else batch_index,
            'total_batches': total_batches
        }
    
    def process_batch_ultra_fast(self, batch_leads: List[Dict], template_name: str) -> tuple:
        """Process a batch of leads with maximum speed parallel processing"""
        success_count = 0
        error_count = 0
        
        def send_single_message(lead_data):
            """Send single message with retry"""
            try:
                phone = lead_data['numero']
                nome = lead_data['nome']
                cpf = lead_data['cpf']
                
                logging.info(f"MEGA BATCH: Sending to {nome} - {phone}")
                
                # Try primary template first
                success, response = self.whatsapp_service.send_template_message_with_button(
                    phone=phone,
                    template_name=template_name,
                    language_code='en',
                    parameters=[cpf, nome],
                    button_param=nome
                )
                
                if not success:
                    logging.info(f"MEGA BATCH: Fallback to receita1 for {nome}")
                    # Fallback to receita1
                    success, response = self.whatsapp_service.send_template_message(
                        phone=phone,
                        template_name='receita1',
                        language_code='pt_BR',
                        parameters=[cpf, nome]
                    )
                
                if success:
                    logging.info(f"MEGA BATCH SUCCESS: {nome} - {phone}")
                    return True, None
                else:
                    error_msg = response.get('error', {}).get('message', 'Unknown error')
                    logging.error(f"MEGA BATCH ERROR: {nome} - {phone}: {error_msg}")
                    return False, error_msg
                    
            except Exception as e:
                logging.error(f"MEGA BATCH EXCEPTION: {lead_data.get('nome', 'Unknown')} - {str(e)}")
                return False, str(e)
        
        # Ultra-fast parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_lead = {
                executor.submit(send_single_message, lead): lead 
                for lead in batch_leads
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_lead):
                if self.should_stop:
                    break
                    
                try:
                    success, error = future.result(timeout=30)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logging.error(f"Future execution error: {e}")
                    error_count += 1
        
        return success_count, error_count
    
    def cleanup_memory(self):
        """Aggressive memory cleanup between batches"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Log memory cleanup
            logging.info(f"MEMORY CLEANUP: Batch complete, memory cleared")
            
        except Exception as e:
            logging.error(f"Memory cleanup error: {e}")
    
    def stop_processing(self):
        """Stop current processing"""
        self.should_stop = True
        logging.info("STOP REQUESTED: Batch processing will stop after current batch")
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        progress = self.load_progress()
        
        base_status = {
            'is_running': self.is_running,
            'processed': self.processed_count,
            'success': self.success_count,
            'errors': self.error_count
        }
        
        if not progress:
            return {
                **base_status,
                'current_batch': 0,
                'total_batches': 0,
                'total_leads': 0
            }
        
        return {
            **base_status,
            'campaign_id': progress.get('campaign_id'),
            'current_batch': progress.get('batch_index', 0),
            'total_batches': progress.get('total_batches', 0),
            'total_leads': progress.get('total_batches', 0) * 20 if progress.get('total_batches') else 0,  # Estimate total
            'template': progress.get('template', 'modelo_5')
        }


# Global batch processor instance
batch_processor = BatchProcessor()