import os
import logging
import requests
import time
import json
from typing import Optional, Dict, List, Tuple

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
            logging.info("🔄 Token atualizado com sucesso")
            
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
                # Use proxy service for request with fallback
                proxy_service = None
                try:
                    import services.proxy_service as proxy_module
                    proxy_service = proxy_module.get_proxy_service()
                except (ImportError, AttributeError):
                    proxy_service = None
                
                if proxy_service and hasattr(proxy_service, 'get'):
                    me_response = proxy_service.get(f"{self.base_url}/me", headers=headers, timeout=10)
                else:
                    me_response = requests.get(f"{self.base_url}/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    user_id = me_data.get('id')
                    
                    if user_id:
                        # Try to get WhatsApp Business Accounts
                        waba_url = f"{self.base_url}/{user_id}?fields=whatsapp_business_accounts"
                        try:
                            if proxy_service and hasattr(proxy_service, 'get'):
                                waba_response = proxy_service.get(waba_url, headers=headers, timeout=10)
                            else:
                                waba_response = requests.get(waba_url, headers=headers, timeout=10)
                        except (AttributeError):
                            waba_response = requests.get(waba_url, headers=headers, timeout=10)
                        
                        if waba_response.status_code == 200:
                            waba_data = waba_response.json()
                            accounts = waba_data.get('whatsapp_business_accounts', {}).get('data', [])
                            
                            if accounts:
                                business_account_id = accounts[0]['id']
                                
                                # Get phone numbers for this business account
                                phones_url = f"{self.base_url}/{business_account_id}/phone_numbers"
                                try:
                                    if proxy_service and hasattr(proxy_service, 'get'):
                                        phones_response = proxy_service.get(phones_url, headers=headers, timeout=10)
                                    else:
                                        phones_response = requests.get(phones_url, headers=headers, timeout=10)
                                except (AttributeError):
                                    phones_response = requests.get(phones_url, headers=headers, timeout=10)
                                
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

    def check_template_availability(self, template_name: str = "hello_world", language_code: str = "pt_BR") -> Tuple[bool, Optional[str]]:
        """Check if a specific template is available for use with language validation
        
        Returns:
            Tuple[bool, Optional[str]]: (template_available, available_language_code)
            - template_available: True if template exists and is approved
            - available_language_code: The language code that's actually available (None if template not found)
        """
        if not self.is_configured():
            return False, None
        
        try:
            url = f"{self.base_url}/{self._business_account_id}/message_templates"
            params = {'name': template_name}
            
            # Enhanced proxy service usage with fallback chain
            response = None
            try:
                import services.proxy_service as proxy_module
                # Try get_proxy_service() first
                try:
                    proxy_service = proxy_module.get_proxy_service()
                    if proxy_service and hasattr(proxy_service, 'get'):
                        response = proxy_service.get(url, headers=self._headers, params=params, timeout=10)
                except (AttributeError, TypeError):
                    # Fallback to proxy_module.proxy_service
                    if hasattr(proxy_module, 'proxy_service'):
                        proxy_service = proxy_module.proxy_service
                        if proxy_service and hasattr(proxy_service, 'get'):
                            response = proxy_service.get(url, headers=self._headers, params=params, timeout=10)
                
                # If proxy methods fail, fallback to direct requests
                if response is None:
                    response = requests.get(url, headers=self._headers, params=params, timeout=10)
                    
            except (ImportError, AttributeError):
                response = requests.get(url, headers=self._headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                # Check if template exists and is approved
                for template in templates:
                    if template.get('name') == template_name and template.get('status') == 'APPROVED':
                        # Check language availability
                        languages = template.get('language', [])
                        if isinstance(languages, list):
                            available_languages = [lang for lang in languages if isinstance(lang, str)]
                        else:
                            # Sometimes language might be a string directly
                            available_languages = [languages] if languages else []
                        
                        # Check if requested language is available
                        if language_code in available_languages:
                            return True, language_code
                        # Check for fallback languages
                        elif "en_US" in available_languages:
                            return True, "en_US"
                        elif "en" in available_languages:
                            return True, "en"
                        elif available_languages:
                            # Return the first available language
                            return True, available_languages[0]
                        else:
                            # Template found but no language info - assume it works
                            return True, language_code
                            
            return False, None
        except Exception as e:
            logging.warning(f"Erro ao verificar template {template_name}: {e}")
            return False, None

    def send_text_message(self, phone: str, message: str, phone_number_id: Optional[str] = None) -> Tuple[bool, Dict]:
        """Send simple text message"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            # Use provided phone_number_id or default
            used_phone_id = phone_number_id or self._phone_number_id
            if not used_phone_id:
                return False, {'error': 'Phone number ID não configurado'}
            url = f"{self.base_url}/{used_phone_id}/messages"
            
            # Accept phone number in E.164 format or already formatted
            formatted_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            # Enhanced proxy service usage with fallback chain
            response = None
            try:
                import services.proxy_service as proxy_module
                # Try get_proxy_service() first
                try:
                    proxy_service = proxy_module.get_proxy_service()
                    if proxy_service and hasattr(proxy_service, 'post'):
                        response = proxy_service.post(url, headers=self._headers, json=payload, timeout=10)
                except (AttributeError, TypeError):
                    # Fallback to proxy_module.proxy_service
                    if hasattr(proxy_module, 'proxy_service'):
                        proxy_service = proxy_module.proxy_service
                        if proxy_service and hasattr(proxy_service, 'post'):
                            response = proxy_service.post(url, headers=self._headers, json=payload, timeout=10)
                
                # If proxy methods fail, fallback to direct requests
                if response is None:
                    response = requests.post(url, headers=self._headers, json=payload, timeout=10)
                    
            except (ImportError, AttributeError):
                response = requests.post(url, headers=self._headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                return True, {
                    'messageId': response_data.get('messages', [{}])[0].get('id', ''),
                    'whatsAppId': response_data.get('contacts', [{}])[0].get('wa_id', ''),
                    'status': 'sent'
                }
            else:
                error_data = response.json() if response.content else {}
                error_info = error_data.get('error', {})
                return False, {
                    'error': error_info.get('message', 'Erro desconhecido'),
                    'error_code': error_info.get('code'),
                    'error_subcode': error_info.get('error_subcode'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem de texto para {phone}: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}

    def send_template_message(self, phone: str, template_name: str, language_code: str = 'en', 
                            parameters: Optional[List[str]] = None, phone_number_id: Optional[str] = None) -> Tuple[bool, Dict]:
        """Send template message"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            # Use provided phone_number_id or default
            used_phone_id = phone_number_id or self._phone_number_id
            if not used_phone_id:
                return False, {'error': 'Phone number ID não configurado'}
            url = f"{self.base_url}/{used_phone_id}/messages"
            
            # Accept phone number in E.164 format or already formatted
            formatted_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            # Build template payload
            template_payload = {
                "name": template_name,
                "language": {"code": language_code}
            }
            
            # Add parameters if provided
            if parameters:
                template_payload["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": str(param)} for param in parameters]
                }]
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "template",
                "template": template_payload
            }
            
            # Enhanced proxy service usage with fallback chain
            response = None
            try:
                import services.proxy_service as proxy_module
                # Try get_proxy_service() first
                try:
                    proxy_service = proxy_module.get_proxy_service()
                    if proxy_service and hasattr(proxy_service, 'post'):
                        response = proxy_service.post(url, headers=self._headers, json=payload, timeout=10)
                except (AttributeError, TypeError):
                    # Fallback to proxy_module.proxy_service
                    if hasattr(proxy_module, 'proxy_service'):
                        proxy_service = proxy_module.proxy_service
                        if proxy_service and hasattr(proxy_service, 'post'):
                            response = proxy_service.post(url, headers=self._headers, json=payload, timeout=10)
                
                # If proxy methods fail, fallback to direct requests
                if response is None:
                    response = requests.post(url, headers=self._headers, json=payload, timeout=10)
                    
            except (ImportError, AttributeError):
                response = requests.post(url, headers=self._headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                return True, {
                    'messageId': response_data.get('messages', [{}])[0].get('id', ''),
                    'whatsAppId': response_data.get('contacts', [{}])[0].get('wa_id', ''),
                    'status': 'sent'
                }
            else:
                error_data = response.json() if response.content else {}
                error_info = error_data.get('error', {})
                return False, {
                    'error': error_info.get('message', 'Erro desconhecido'),
                    'error_code': error_info.get('code'),
                    'error_subcode': error_info.get('error_subcode'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logging.error(f"Erro ao enviar template para {phone}: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}

    def verify_whatsapp_numbers(self, phone_numbers: List[str], rate_limit_delay: float = 0.5, 
                               template_name: str = "hello_world", language_code: str = "pt_BR") -> Dict:
        """
        Verificar quais números da lista têm WhatsApp ativo.
        
        Baseado na documentação da Meta, não existe endpoint direto para verificação,
        então tentamos enviar uma mensagem de teste e capturamos códigos de erro específicos.
        
        Args:
            phone_numbers: Lista de números de telefone formatados
            rate_limit_delay: Delay em segundos entre requisições (padrão: 0.5s)
            
        Returns:
            Dict com resultado da verificação:
            {
                'valid_numbers': [números que têm WhatsApp],
                'invalid_numbers': [números que não têm WhatsApp],
                'errors': [erros encontrados],
                'total_checked': int,
                'total_removed': int
            }
        """
        if not self.is_configured():
            return {
                'valid_numbers': [],
                'invalid_numbers': [],
                'errors': ['WhatsApp Business API não configurada'],
                'total_checked': 0,
                'total_removed': 0
            }
        
        logging.info(f"🔍 INICIANDO VERIFICAÇÃO DE {len(phone_numbers)} NÚMEROS WHATSAPP")
        
        # Verificar se template de verificação está disponível
        template_available, available_language = self.check_template_availability(template_name, language_code)
        if not template_available:
            logging.warning(f"⚠️ Template '{template_name}' não disponível, continuando sem validação de template")
        
        # Use fallback language if pt_BR not available
        if not available_language:
            language_code = "en_US"
            logging.info(f"🔄 Usando fallback de idioma: {language_code}")
        else:
            language_code = available_language
            logging.info(f"✅ Usando idioma: {language_code}")
        
        valid_numbers = []
        invalid_numbers = []
        errors = []
        total_checked = 0
        
        for idx, phone in enumerate(phone_numbers):
            total_checked += 1
            
            try:
                # Log do progresso
                logging.info(f"📱 Verificando número {idx + 1}/{len(phone_numbers)}: {phone}")
                
                # Accept phone number in E.164 format or already formatted
                formatted_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                
                # Tentar enviar template de verificação (evita restrições de 24h)
                success, response = self.send_template_message(formatted_phone, template_name, language_code)
                
                if success:
                    valid_numbers.append(phone)
                    logging.info(f"✅ VÁLIDO: {phone} - WhatsApp ativo")
                else:
                    # Analisar código de erro específico
                    error_code = response.get('error_code')
                    error_subcode = response.get('error_subcode')
                    error_message = response.get('error', 'Erro desconhecido')
                    status_code = response.get('status_code')
                    
                    # Códigos de erro que indicam número inválido/sem WhatsApp:
                    # 131026 - Número não tem WhatsApp
                    # 131047 - Número bloqueado/inválido
                    # 131048 - Número fora de serviço
                    # 131049 - Número com restrições
                    # 131051 - Número não verificado/inválido
                    invalid_error_codes = [131026, 131047, 131048, 131049, 131051]
                    
                    if error_code in invalid_error_codes or error_subcode in invalid_error_codes:
                        invalid_numbers.append(phone)
                        code_info = f"código: {error_code}" + (f", subcode: {error_subcode}" if error_subcode else "")
                        logging.warning(f"❌ INVÁLIDO: {phone} - {code_info}: {error_message}")
                    elif status_code == 400 and any(keyword in error_message.lower() for keyword in ['invalid', 'not found', 'does not exist']):
                        # Fallback para mensagens de erro em texto
                        invalid_numbers.append(phone)
                        logging.warning(f"❌ INVÁLIDO: {phone} - {error_message}")
                    else:
                        # Outros erros (rate limit, problemas de rede, etc.)
                        code_info = f"código: {error_code}" + (f", subcode: {error_subcode}" if error_subcode else "")
                        error_detail = f"Número {phone}: {error_message} ({code_info})"
                        errors.append(error_detail)
                        logging.error(f"⚠️ ERRO: {phone} - {error_message} ({code_info})")
                        
                        # Em caso de erro técnico, não categorizar como inválido
                        # O número pode estar válido, mas houve problema técnico
                
                # Rate limiting para evitar bloqueios
                if idx < len(phone_numbers) - 1:  # Não fazer delay no último número
                    time.sleep(rate_limit_delay)
                    
            except Exception as e:
                error_detail = f"Número {phone}: Exceção - {str(e)}"
                errors.append(error_detail)
                logging.error(f"💥 EXCEÇÃO ao verificar {phone}: {str(e)}")
                
                # Rate limiting mesmo em caso de exceção
                if idx < len(phone_numbers) - 1:
                    time.sleep(rate_limit_delay)
        
        total_removed = len(invalid_numbers)
        
        # Log final do resultado
        logging.info(f"📊 VERIFICAÇÃO CONCLUÍDA (template: {template_name}):")
        logging.info(f"   ✅ Números válidos: {len(valid_numbers)}")
        logging.info(f"   ❌ Números inválidos: {len(invalid_numbers)}")
        logging.info(f"   ⚠️ Erros técnicos: {len(errors)}")
        logging.info(f"   📱 Total verificados: {total_checked}")
        logging.info(f"   🗑️ Total removidos: {total_removed}")
        
        # Log detalhado dos números válidos
        if valid_numbers:
            logging.info(f"📋 NÚMEROS VÁLIDOS: {', '.join(valid_numbers[:10])}{'...' if len(valid_numbers) > 10 else ''}")
        
        # Log detalhado dos números inválidos
        if invalid_numbers:
            logging.info(f"🚫 NÚMEROS INVÁLIDOS: {', '.join(invalid_numbers[:10])}{'...' if len(invalid_numbers) > 10 else ''}")
        
        return {
            'valid_numbers': valid_numbers,
            'invalid_numbers': invalid_numbers,
            'errors': errors,
            'total_checked': total_checked,
            'total_removed': total_removed
        }