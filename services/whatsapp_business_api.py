import os
import logging
import requests
from typing import Optional, Dict, List

class WhatsAppBusinessAPI:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v23.0"
        self._access_token = None
        self._phone_number_id = None
        self._business_account_id = None
        self._headers = None
        self._available_phones = []
        self._current_phone_index = 0
        self._has_error_135000 = False
        self._total_phones_discovered = 0
        self._approved_templates = []
        self._interface_session = {}
        
        # Initialize if token exists
        self._refresh_credentials()

    def _refresh_credentials(self):
        """🎯 APENAS TOKEN DA INTERFACE - NENHUM FALLBACK"""
        new_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        
        if new_token:
            self._access_token = new_token
            logging.info(f"🔄 Token atualizado: {new_token[:50]}...")
            
            # Update headers
            self._headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json'
            }
            
            # 🎯 SEMPRE DESCOBERTA DINÂMICA - NENHUM FALLBACK
            logging.info("🔥 FORÇANDO DESCOBERTA DINÂMICA - NENHUM FALLBACK PERMITIDO")
            
            discovered = self._discover_business_manager()
            if discovered:
                self._business_account_id = discovered['business_account_id']
                self._available_phones = discovered['phone_numbers']
                self._has_error_135000 = discovered.get('has_error_135000', False)
                logging.info(f"✅ DESCOBERTO VIA API: BM {self._business_account_id} - {len(self._available_phones)} phones")
                
                # Set first phone as default
                if self._available_phones:
                    self._phone_number_id = self._available_phones[0]
                    logging.info(f"📱 PHONE PADRÃO: {self._phone_number_id}")
            else:
                logging.error("❌ FALHA NA DESCOBERTA - TOKEN INVÁLIDO OU SEM PERMISSÕES")
                self._business_account_id = None
                self._available_phones = []
                self._phone_number_id = None
        else:
            logging.warning("⚠️ NENHUM TOKEN ENCONTRADO")

    def _discover_business_manager(self) -> Optional[Dict]:
        """Discover Business Manager and Phone Numbers via API"""
        try:
            if not self._access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get WhatsApp Business Accounts directly
            try:
                import services.proxy_service as proxy_module
                me_response = proxy_module.proxy_service.get(f"{self.base_url}/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    user_id = me_data.get('id')
                    
                    if user_id:
                        # Try to get WhatsApp Business Accounts
                        waba_url = f"{self.base_url}/{user_id}?fields=whatsapp_business_accounts"
                        waba_response = proxy_module.proxy_service.get(waba_url, headers=headers, timeout=10)
                        
                        if waba_response.status_code == 200:
                            waba_data = waba_response.json()
                            accounts = waba_data.get('whatsapp_business_accounts', {}).get('data', [])
                            
                            if accounts:
                                business_account_id = accounts[0]['id']
                                
                                # Get phone numbers for this business account
                                phones_url = f"{self.base_url}/{business_account_id}/phone_numbers"
                                phones_response = proxy_module.proxy_service.get(phones_url, headers=headers, timeout=10)
                                
                                if phones_response.status_code == 200:
                                    phones_data = phones_response.json()
                                    phone_numbers = [phone['id'] for phone in phones_data.get('data', [])]
                                    
                                    if phone_numbers:
                                        logging.info(f"✅ DESCOBERTO VIA API: BM {business_account_id} com {len(phone_numbers)} phones")
                                        return {
                                            'business_account_id': business_account_id,
                                            'phone_numbers': phone_numbers,
                                            'has_error_135000': False
                                        }
            except Exception as e:
                logging.warning(f"Erro na descoberta via API: {e}")
            
            return None
            
        except Exception as e:
            logging.error(f"Erro geral na descoberta da BM: {e}")
            return None

    def set_connection(self, access_token: str, business_manager_id: str, phone_ids: list):
        """Set connection data directly from UI discovery - bypasses token fallbacks"""
        self._access_token = access_token
        self._business_account_id = business_manager_id
        self._available_phones = phone_ids
        self._phone_number_id = phone_ids[0] if phone_ids else None
        self._has_error_135000 = False
        
        # Update headers
        self._headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }
        
        # Update environment for workers
        os.environ['WHATSAPP_ACCESS_TOKEN'] = access_token
        
        logging.info(f"🎯 CONNECTION SET DIRECTLY: BM {business_manager_id}, {len(phone_ids)} phones, primary phone: {self._phone_number_id}")
        logging.info(f"🔗 BYPASSING TOKEN FALLBACKS - Using UI-discovered credentials")

    def set_phone_number_id(self, phone_number_id: str):
        """Set the phone number ID for this request"""
        self._phone_number_id = phone_number_id
        logging.info(f"Phone Number ID set to: {phone_number_id}")

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self._access_token and self._phone_number_id)

    def get_available_phones(self) -> List[str]:
        """Get list of available phone numbers"""
        return self._available_phones.copy()

    def get_business_account_id(self) -> Optional[str]:
        """Get the current business account ID"""
        return self._business_account_id