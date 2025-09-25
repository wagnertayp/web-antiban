import os
import requests
import logging
import time
import random
import threading
import json
import tempfile
import fcntl
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import defaultdict
# 📡 ENVIO DIRETO - Removida funcionalidade de proxy conforme solicitado

class SharedRateLimiter:
    """🛡️ Rate limiter compartilhado entre processos/workers com file locking atômico"""
    _rate_file_path = Path(tempfile.gettempdir()) / "whatsapp_rate_limiter.json"
    
    @classmethod
    def check_and_wait(cls, phone_number_id: str):
        """Verificar rate limit e aguardar se necessário (atômico entre processos)"""
        current_time = time.time()
        wait_time = 0
        
        # File locking atômico para evitar race conditions entre workers
        try:
            # Abrir arquivo com lock exclusivo
            with open(cls._rate_file_path, 'a+') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                
                # Ler dados atuais (início do arquivo)
                f.seek(0)
                try:
                    content = f.read()
                    rate_data = json.loads(content) if content.strip() else {}
                except (json.JSONDecodeError, ValueError):
                    rate_data = {}
                
                # Obter último envio para este phone_id
                last_send = rate_data.get(phone_number_id, 0)
                
                # Calcular delay necessário (0.3-0.8s entre mensagens)
                time_since_last = current_time - last_send
                min_delay = random.uniform(0.3, 0.8)
                
                wait_time = max(0, min_delay - time_since_last)
                
                # Atualizar timestamp
                rate_data[phone_number_id] = current_time + wait_time
                
                # Limpar dados antigos (> 1 hora)
                cutoff = current_time - 3600
                rate_data = {k: v for k, v in rate_data.items() if v > cutoff}
                
                # Escrever dados atualizados atomicamente
                f.seek(0)
                f.truncate()
                json.dump(rate_data, f)
                f.flush()
                
                # Lock liberado automaticamente ao sair do context
                
        except Exception as e:
            logging.warning(f"Falha no rate limiter compartilhado: {e}")
            # Fallback para delay mínimo se file locking falhar
            wait_time = random.uniform(0.3, 0.8)
        
        # Sleep fora do lock
        if wait_time > 0:
            logging.info(f"🔄 Rate limit atômico phone {phone_number_id}: {wait_time:.1f}s")
            time.sleep(wait_time)

class WhatsAppBusinessAPI:
    """Service for WhatsApp Business API (Facebook Cloud API) integration"""
    
    def __init__(self):
        self.api_version = 'v23.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        
        # Initialize with empty credentials
        self._access_token = None
        self._phone_number_id = None
        self._business_account_id = None
        self._headers = None
        self._available_phones = []
        self._current_phone_index = 0
        
        # 🔒 Track credential source (session vs environment) - Solução Replit
        self._credentials_from_session = False
        
        # 🛡️ PROTEÇÃO ANTI-BAN - Rate limiting por phone_number_id (thread-safe)
        self._rate_limiter_lock = threading.Lock()
        self._phone_last_message = defaultdict(float)  # phone_id -> timestamp
        self._phone_message_count = defaultdict(int)   # phone_id -> count
        self._phone_minute_start = defaultdict(float)  # phone_id -> minute start
        
        # Initialize optimized HTTP session for maximum speed
        self.session = requests.Session()
        
        # ✅ OTIMIZADO PARA REPLIT - Performance balanceada
        retry_strategy = Retry(
            total=2,  # Duas tentativas para melhor confiabilidade
            backoff_factor=0.3,  # Backoff moderado
            status_forcelist=[500, 502, 503, 504],  # Retry em erros de servidor
        )
        adapter = HTTPAdapter(
            pool_connections=10,  # 10 pools - suficiente para WhatsApp
            pool_maxsize=20,      # 20 connections por pool - otimizado
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Load initial credentials
        self._refresh_credentials()
        
        if self._access_token:
            logging.info("✅ WhatsApp Business API otimizado para Replit - Performance balanceada")
        else:
            logging.warning("WhatsApp Business API credentials not found in environment variables")
    
    def _anti_ban_protection_per_phone(self, phone_number_id: str):
        """🛡️ PROTEÇÃO POR NÚMERO - Rate limiting compartilhado entre workers"""
        # Usar novo sistema de rate limiting compartilhado
        SharedRateLimiter.check_and_wait(phone_number_id)
        logging.info(f"📡 Enviando mensagem diretamente - sem proxy")

    def _get_randomized_headers(self):
        """🎭 Headers randomizados para parecer mais humano"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        base_headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json',
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache'
        }
        
        return base_headers

    def _send_direct(self, url: str, payload: dict, phone_number_id: str = None):
        """📡 ENVIO DIRETO - Sem proxy conforme solicitado"""
        # 🛡️ PROTEÇÃO ANTI-BAN POR NÚMERO (thread-safe)
        if phone_number_id:
            self._anti_ban_protection_per_phone(phone_number_id)
        else:
            # Fallback para proteção global mínima se phone_id não fornecido
            time.sleep(random.uniform(0.1, 0.3))
        
        # 🎭 HEADERS RANDOMIZADOS
        randomized_headers = self._get_randomized_headers()
        
        try:
            logging.info("📡 Enviando mensagem diretamente - sem proxy")
            response = requests.post(url, json=payload, headers=randomized_headers, timeout=10)
            return response
            
        except requests.exceptions.Timeout:
            logging.error("Timeout na conexão - tentando novamente")
            # Segunda tentativa com timeout menor
            response = requests.post(url, json=payload, headers=randomized_headers, timeout=5)
            return response

    def update_credentials(self, access_token: str, business_account_id: str = None, phone_number_id: str = None):
        """🔒 Atualizar credenciais via sessão (Solução Replit)"""
        self._access_token = access_token
        self._credentials_from_session = True
        
        if business_account_id:
            self._business_account_id = business_account_id
        if phone_number_id:
            self._phone_number_id = phone_number_id
            
        # Atualizar headers (corrigido: usar _headers)
        self._headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        masked_token = "..." + access_token[-4:] if len(access_token) > 4 else "****"
        logging.info(f"🔒 Credenciais atualizadas via sessão: {masked_token}")
    
    def _refresh_credentials(self):
        """Refresh credentials from environment variables with multi-BM support"""
        # 🚨 PRODUÇÃO: SEMPRE usar secrets - priorizar environment variables
        new_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        
        # ✅ Se há token nas secrets, SEMPRE usar esse (produção)
        if new_token:
            # Reset session credentials se há token no ambiente
            if self._credentials_from_session:
                logging.info("🔄 SUBSTITUINDO credenciais da sessão por secrets do ambiente")
                self._credentials_from_session = False
        else:
            # ✅ DETECÇÃO DE MUDANÇA DE TOKEN - só verificar sessão se não há secrets
            if self._credentials_from_session and self._access_token:
                # Verificar se é a mesma conta/token da sessão - se sim, não atualizar
                from flask import session
                try:
                    session_token = session.get('whatsapp_access_token')
                    if session_token and self._access_token == session_token:
                        logging.debug("🔒 Mantendo credenciais da sessão (mesmo token)")
                        return
                    # Se tokens diferentes, permitir atualização
                    elif session_token and self._access_token != session_token:
                        logging.info(f"🔄 MUDANÇA DE CONTA DETECTADA - Atualizando credenciais")
                        self._credentials_from_session = False  # Reset para permitir atualização
                except RuntimeError:
                    # Fora do contexto da sessão - continuar normalmente
                    pass
        
        # ✅ FALLBACK: Se não há token no ambiente, carregar do banco
        if not new_token:
            try:
                # Criar contexto de aplicação se necessário
                from flask import current_app
                try:
                    # Verificar se já estamos em um contexto
                    current_app.config
                    app_context = None
                except RuntimeError:
                    # Criar contexto se não existir
                    from app import app
                    app_context = app.app_context()
                    app_context.push()
                
                try:
                    from models import SystemConfig
                    stored_token = SystemConfig.get_config('whatsapp_access_token')
                    stored_connected = SystemConfig.get_config('whatsapp_connected')
                    if stored_token and stored_connected == 'true':
                        new_token = stored_token
                        logging.info(f"🔄 Token carregado do banco: ...{new_token[-4:]}")
                finally:
                    # Limpar contexto se criamos um
                    if app_context:
                        app_context.pop()
                        
            except Exception as e:
                logging.warning(f"Erro ao carregar token do banco: {e}")
        
        if new_token:
            self._access_token = new_token
            logging.info(f"🔄 Token carregado do ambiente: ...{new_token[-4:]}")
            
            # DEBUG: Log masked token for security
            masked_token = "..." + new_token[-4:] if len(new_token) > 4 else "****"
            logging.info(f"🔍 Token ativo: {masked_token}")
        
        # Auto-detect Business Manager and Phone based on token
            
            # Tentar descobrir automaticamente primeiro
            discovered = self._get_cached_fallback()
            if discovered:
                self._business_account_id = discovered['business_account_id']
                self._available_phones = discovered['phone_numbers']
                self._has_error_135000 = discovered.get('has_error_135000', False)
                logging.info(f"AUTO-DESCOBERTO: BM {self._business_account_id} - {len(self._available_phones)} phones")
            else:
                # Descoberta dinâmica via API apenas - sem números hardcoded
                discovered = self._discover_business_manager()
                if discovered:
                    self._business_account_id = discovered['business_account_id']
                    self._available_phones = discovered['phone_numbers']
                    self._has_error_135000 = discovered.get('has_error_135000', False)
                    logging.info(f"📱 DESCOBERTO VIA API: {len(self._available_phones)} números da BM {self._business_account_id}")
                else:
                    # ✅ USAR SECRETS DIRETAMENTE - SEM API CALLS
                    bm_from_env = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
                    phone_from_env = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
                    
                    if bm_from_env and phone_from_env:
                        logging.info(f"📍 USANDO CREDENCIAIS DAS SECRETS: BM {bm_from_env}, Phone {phone_from_env}")
                        self._business_account_id = bm_from_env
                        self._phone_number_id = phone_from_env
                        
                        # Buscar dados reais via API do phone number
                        try:
                            import requests
                            phone_url = f"https://graph.facebook.com/v23.0/{phone_from_env}"
                            phone_response = requests.get(phone_url, headers=self._headers, timeout=10)
                            
                            if phone_response.status_code == 200:
                                phone_data = phone_response.json()
                                self._available_phones = [{
                                    'id': phone_from_env,
                                    'display_phone_number': phone_data.get('display_phone_number', 'Desconhecido'),
                                    'quality_rating': phone_data.get('quality_rating', 'UNKNOWN'),
                                    'verified_name': phone_data.get('verified_name', 'Nome não verificado')
                                }]
                                real_name = phone_data.get('verified_name', 'Nome não verificado')
                                logging.info(f"✅ DADOS REAIS CARREGADOS VIA API: {real_name}")
                            else:
                                # Fallback se API falhar
                                self._available_phones = [{
                                    'id': phone_from_env,
                                    'display_phone_number': 'Carregando...',
                                    'quality_rating': 'UNKNOWN',
                                    'verified_name': 'Carregando dados...'
                                }]
                                logging.warning(f"⚠️ Falha na API do phone: {phone_response.status_code}")
                        except Exception as e:
                            # Fallback se houver erro
                            self._available_phones = [{
                                'id': phone_from_env,
                                'display_phone_number': 'Erro na conexão',
                                'quality_rating': 'UNKNOWN',
                                'verified_name': 'Erro ao carregar'
                            }]
                            logging.error(f"❌ Erro ao buscar dados do phone: {e}")
                        
                        self._has_error_135000 = False
                        logging.info(f"✅ CREDENCIAIS CARREGADAS DAS SECRETS: BM e Phone configurados")
                    else:
                        # Sem secrets - deixar vazio para seleção do usuário
                        self._available_phones = []
                        self._has_error_135000 = False
                        logging.warning(f"⚠️ SECRETS NÃO ENCONTRADAS - USAR SELEÇÃO DO USUÁRIO")
            
            # Usar primeiro phone disponível ou None se não há phones (CORRIGIDO: extrair apenas o ID)
            if self._available_phones:
                first_phone = self._available_phones[0]
                new_phone_id = first_phone['id'] if isinstance(first_phone, dict) else first_phone
            else:
                new_phone_id = None
                
        elif new_token:
            # ALWAYS FORCE FRESH - NO CACHE EVER
            self._business_account_id = None
            new_phone_id = None
            logging.info("🔥 CACHE COMPLETAMENTE DESABILITADO - SEMPRE FRESH TOKEN DA INTERFACE")
        else:
            # Token hasn't changed, keep current phone ID
            new_phone_id = self._phone_number_id
        
        # Update if changed
        if new_token != self._access_token or new_phone_id != self._phone_number_id:
            self._access_token = new_token
            self._phone_number_id = new_phone_id
            
            if self._access_token:
                self._headers = {
                    'Authorization': f'Bearer {self._access_token}',
                    'Content-Type': 'application/json'
                }
                logging.info(f"🔥 TOKEN DA INTERFACE - {len(self._available_phones)} phones descobertos FRESH (cache desabilitado)")
            else:
                self._headers = {}
    

                logging.warning("WhatsApp credentials not available")
    
    def _get_cached_fallback(self):
        """Return cached fallback based on current token pattern - DEPRECATED: Use dynamic discovery instead"""
        # Todos os números hardcoded foram removidos - usar apenas descoberta dinâmica via API
        return None

    def _discover_business_manager(self) -> Optional[Dict]:
        """Discover Business Manager and Phone Numbers via API for unknown tokens"""
        try:
            if not self._access_token:
                return None
            
            # 🔒 Construir headers correto com token
            headers = {
                'Authorization': f'Bearer {self._access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get WhatsApp Business Accounts directly
            try:
                # 🔐 Conectar diretamente (sem proxy para debugging)
                logging.info(f"🔍 Testing token with /me endpoint...")
                # Obfuscar token para segurança
                safe_headers = {k: v if k != 'Authorization' else f"Bearer ...{v[-4:]}" if v.startswith('Bearer ') else '***' for k, v in headers.items()}
                logging.info(f"🔍 Headers being sent: {safe_headers}")
                logging.info(f"🔍 URL: {self.base_url}/me")
                
                me_response = requests.get(f"{self.base_url}/me", headers=headers, timeout=10)
                logging.info(f"🔍 /me response: {me_response.status_code}")
                
                if me_response.status_code != 200:
                    logging.error(f"🔍 Error response: {me_response.text}")
                else:
                    logging.info(f"🔍 Success response: {me_response.json()}")
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    user_id = me_data.get('id')
                    
                    if user_id:
                        # Try to get WhatsApp Business Accounts
                        waba_url = f"{self.base_url}/{user_id}?fields=whatsapp_business_accounts"
                        # Conexão direta removida funcionalidade de proxy
                        waba_response = requests.get(waba_url, headers=headers, timeout=10)
                        
                        if waba_response.status_code == 200:
                            waba_data = waba_response.json()
                            accounts = waba_data.get('whatsapp_business_accounts', {}).get('data', [])
                            
                            if accounts:
                                business_account_id = accounts[0]['id']
                                
                                # Get phone numbers for this business account
                                phones_url = f"{self.base_url}/{business_account_id}/phone_numbers"
                                # Conexão direta removida funcionalidade de proxy
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

    def _discover_whatsapp_ids_original(self, access_token: str) -> Optional[Dict]:
        """Auto-discover both Business Manager ID and Phone Number ID"""
        try:
            # First, get the Business Account ID
            headers = self.headers  # 🔒 Usar headers da sessão atualizada
            
            # Try to get business account from me endpoint
            # Direct API call without proxy for speed
            me_response = requests.get(f"{self.base_url}/me", headers=headers, timeout=10)
            if me_response.status_code != 200:
                return None
            
            me_data = me_response.json()
            user_id = me_data.get('id')
            
            if not user_id:
                return None
            
            # Get business accounts associated with this user
            # Try different approaches to find WhatsApp Business Account
            possible_endpoints = [
                f"{self.base_url}/{user_id}?fields=accounts",
                f"{self.base_url}/me?fields=accounts",
                f"{self.base_url}/me?fields=businesses"
            ]
            
            business_account_id = None
            
            for endpoint in possible_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        # Look for accounts or businesses data
                        accounts = data.get('accounts', {}).get('data', []) or data.get('businesses', {}).get('data', [])
                        if accounts:
                            business_account_id = accounts[0].get('id')
                            break
                except:
                    continue
            
            # If we couldn't find business account, try a direct approach
            # Use a known pattern or try common business account discovery
            if not business_account_id:
                # Sometimes the phone numbers are directly accessible
                try:
                    # Try to get WhatsApp Business accounts directly
                    # Proxy removido - usando conexão direta
                    waba_response = requests.get(f"{self.base_url}/me?fields=whatsapp_business_accounts", headers=headers, timeout=10)
                    if waba_response.status_code == 200:
                        waba_data = waba_response.json()
                        accounts = waba_data.get('whatsapp_business_accounts', {}).get('data', [])
                        if accounts:
                            business_account_id = accounts[0].get('id')
                except:
                    pass
            
            # If still no business account, try to scan known patterns or use fallback
            if not business_account_id:
                # Check if the WHATSAPP_PHONE_NUMBER_ID actually contains a business account ID
                current_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
                if current_phone_id and len(current_phone_id) > 10:
                    # Try using it as business account ID
                    try:
                        # Proxy removido - usando conexão direta
                        phones_response = requests.get(f"{self.base_url}/{current_phone_id}/phone_numbers", headers=headers, timeout=10)
                        if phones_response.status_code == 200:
                            phones_data = phones_response.json()
                            phone_numbers = phones_data.get('data', [])
                            if phone_numbers:
                                phone_ids = [phone.get('id') for phone in phone_numbers if phone.get('id')]
                                return {
                                    'business_account_id': current_phone_id,
                                    'phone_numbers': phone_ids,
                                    'has_error_135000': False
                                }
                    except:
                        pass
                
                return None
            
            # Now get phone numbers from business account
            # Proxy removido - usando conexão direta
            phones_response = requests.get(f"{self.base_url}/{business_account_id}/phone_numbers", headers=headers, timeout=10)
            if phones_response.status_code == 200:
                phones_data = phones_response.json()
                phone_numbers = phones_data.get('data', [])
                if phone_numbers:
                    # Extract all phone number IDs
                    phone_ids = [phone.get('id') for phone in phone_numbers if phone.get('id')]
                    logging.info(f"Discovered {len(phone_ids)} phone numbers from business account {business_account_id}")
                    
                    # Check if this BM has known error #135000 issues
                    has_error_135000 = False  # Disabled - test templates directly first
                    
                    return {
                        'business_account_id': business_account_id,
                        'phone_numbers': phone_ids,
                        'has_error_135000': has_error_135000
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Error discovering WhatsApp IDs: {str(e)}")
            return None
    
    @property
    def business_account_id(self):
        """Get business account ID"""
        return self._business_account_id
    
    @property
    def access_token(self):
        """Get access token - FAST VERSION"""
        return self._access_token
    
    @property
    def phone_number_id(self):
        """Get phone number ID - FAST VERSION"""
        return self._phone_number_id
    
    @property
    def headers(self):
        """Get headers - FAST VERSION"""
        return self._headers
    
    def set_phone_number_id(self, phone_number_id: str):
        """Set the phone number ID for this request"""
        self._phone_number_id = phone_number_id
        logging.info(f"Phone Number ID set to: {phone_number_id}")
    
    def is_configured(self) -> bool:
        """Check if WhatsApp Business API is properly configured - FAST VERSION"""
        # Quick check without refresh for speed
        return bool(self._access_token)  # Only check token, phone ID will be set per request
    
    def _check_template_has_button(self, template_name: str) -> bool:
        """Check if a template has button components"""
        try:
            # Get available templates to check structure
            templates = self.get_available_templates()
            
            for template in templates:
                if template.get('name') == template_name:
                    # Check if template has button components
                    components = template.get('components', [])
                    for component in components:
                        if component.get('type') == 'BUTTONS':
                            return True
                    return False
            
            # If template not found, assume it has buttons for safety
            return True
            
        except Exception as e:
            logging.warning(f"Could not check template button structure: {e}")
            # Default to assuming it has buttons for safety
            return True
    
    def _get_template_structure(self, template_name: str) -> Optional[Dict]:
        """Get the complete structure of a template"""
        try:
            # Get available templates to extract structure
            templates = self.get_available_templates()
            
            for template in templates:
                if template.get('name') == template_name:
                    return template
            
            return None
            
        except Exception as e:
            logging.warning(f"Could not get template structure: {e}")
            return None


    

    

    def test_connection(self) -> Dict:
        """Test WhatsApp Business API connection"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WhatsApp Business API não configurada. Configure WHATSAPP_ACCESS_TOKEN'
            }
        
        try:
            # Test by sending a simple API call to verify connection
            url = f"{self.base_url}/me"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Conexão WhatsApp Business API estabelecida com sucesso',
                    'phone_number': self.phone_number_id,
                    'status': 'connected'
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': f'Erro na conexão: {response.status_code} - {error_data.get("error", {}).get("message", "Erro desconhecido")}'
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"WhatsApp Business API connection test failed: {str(e)}")
            return {
                'success': False,
                'error': f'Erro de conexão: {str(e)}'
            }
    
    def _simulate_typing_indicator(self, phone: str, message_length: int = 50):
        """Simula indicador de 'digitando' com pausa baseada no tamanho da mensagem"""
        try:
            # Calcular tempo de pausa baseado no comprimento da mensagem
            # Mensagens curtas: 1-2s, mensagens longas: 2-4s
            base_delay = 1.0  # Base de 1 segundo
            length_delay = min(message_length / 100, 3.0)  # Máximo 3s adicional
            total_delay = base_delay + length_delay
            
            logging.info(f"💬 Simulando digitação para {phone} por {total_delay:.1f}s...")
            import time
            time.sleep(total_delay)
            
        except Exception as e:
            logging.warning(f"Erro no simulador de digitação: {str(e)}")
            # Continua sem pausa se houver erro

    def send_text_message(self, phone: str, message: str, phone_number_id: str = None, lead_index: int = None) -> Tuple[bool, Dict]:
        """Send simple text message - OTIMIZADO PARA VELOCIDADE"""
        # SIMULAR INDICADOR DE DIGITAÇÃO
        self._simulate_typing_indicator(phone, len(message))
        
        # QUICK CHECK: Skip heavy verifications for speed
        if not self._access_token:
            self._refresh_credentials()
            if not self._access_token:
                return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            # Use provided phone_number_id or default
            used_phone_id = phone_number_id or self._phone_number_id
            logging.info(f"📱 Enviando mensagem: phone_number_id={phone_number_id}, self.phone_number_id={self._phone_number_id}, used_phone_id={used_phone_id}")
            
            if not used_phone_id:
                return False, {'error': 'Phone Number ID não especificado'}
            
            url = f"{self.base_url}/{used_phone_id}/messages"
            
            # Format phone number (remove country code if present for international format)
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': formatted_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            logging.info(f"Sending text message payload: {payload}")
            
            # Enviar diretamente (proxy removido)
            try:
                response = self._send_direct(url, payload, self._phone_number_id)
            except Exception as e:
                logging.error(f"Direct connection failed: {str(e)}")
                return False, {'error': f'Erro de conexão: {str(e)}'}
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"WhatsApp text message API response: {data}")
                
                # Check if message was actually accepted and get contact status
                if data.get('messages') and len(data.get('messages', [])) > 0:
                    message_id = data.get('messages', [{}])[0].get('id', '')
                    contacts = data.get('contacts', [])
                    
                    # Log detailed contact information for debugging delivery issues
                    if contacts:
                        contact_info = contacts[0]
                        wa_id = contact_info.get('wa_id', 'unknown')
                        input_phone = contact_info.get('input', 'unknown')
                        logging.info(f"Message queued - Input: {input_phone}, WhatsApp ID: {wa_id}, Message ID: {message_id}")
                        
                        # Check if the WhatsApp ID was properly resolved
                        if wa_id == 'unknown' or not wa_id:
                            logging.warning(f"WhatsApp ID not resolved for phone {formatted_phone} - message may not be delivered")
                    
                    return True, {
                        'messageId': message_id,
                        'whatsAppId': message_id,
                        'status': 'sent',
                        'contacts': contacts,
                        'phone_resolved': formatted_phone
                    }
                else:
                    logging.error(f"API returned 200 but no messages in response: {data}")
                    return False, {
                        'error': 'API retornou sucesso mas sem mensagens',
                        'details': str(data)
                    }
            else:
                error_data = response.json() if response.content else {}
                logging.error(f"Text message API error: {response.status_code} - {error_data}")
                return False, {
                    'error': f'Erro HTTP {response.status_code}',
                    'details': error_data.get('error', {}).get('message', response.text)
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending WhatsApp message: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}
    
    def send_interactive_buttons(self, recipient: str, message_text: str, buttons: list) -> Tuple[bool, Dict]:
        """
        Envia mensagem com botões interativos de resposta rápida
        """
        try:
            if not self._phone_number_id:
                return False, {'error': 'Phone number ID não configurado'}
            
            # Validar botões (máximo 3)
            if len(buttons) > 3:
                buttons = buttons[:3]
                logging.warning("⚠️ Limitando a 3 botões interativos")
            
            # Preparar payload para botões interativos
            interactive_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": recipient,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": []
                    }
                }
            }
            
            # Adicionar botões ao payload
            for i, button in enumerate(buttons):
                button_data = {
                    "type": "reply",
                    "reply": {
                        "id": button.get('id', f"btn_{i}"),
                        "title": button.get('title', '')[:20]  # Máximo 20 caracteres
                    }
                }
                interactive_payload["interactive"]["action"]["buttons"].append(button_data)
            
            logging.info(f"📱 Enviando botões interativos: {[b['title'] for b in buttons]}")
            
            # 🛡️ RATE LIMITING ANTI-BAN
            SharedRateLimiter.check_and_wait(self._phone_number_id)
            
            # Enviar via método seguro
            url = f"https://graph.facebook.com/v23.0/{self._phone_number_id}/messages"
            response = self._send_direct(url, interactive_payload, self._phone_number_id)
            
            if response.status_code == 200:
                response_data = response.json()
                logging.info(f"✅ Botões interativos enviados com sucesso")
                return True, response_data
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                logging.error(f"❌ Falha ao enviar botões: {response.status_code} - {error_data}")
                return False, error_data
                
        except Exception as e:
            logging.error(f"Erro ao enviar botões interativos: {str(e)}")
            return False, {'error': f'Erro inesperado: {str(e)}'}
    
    def send_cta_url_button(self, recipient: str, message_text: str, button_text: str, url: str) -> Tuple[bool, Dict]:
        """
        Envia mensagem com botão de link CTA (Call to Action)
        """
        try:
            if not self._phone_number_id:
                return False, {'error': 'Phone number ID não configurado'}
            
            # Validar comprimento do texto do botão (máximo 20 caracteres)
            if len(button_text) > 20:
                button_text = button_text[:17] + "..."  # 17 + 3 = 20
                logging.warning(f"⚠️ Texto do botão truncado para: {button_text}")
            
            # Preparar payload para botão CTA
            cta_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient, 
                "type": "interactive",
                "interactive": {
                    "type": "cta_url",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "name": "cta_url",
                        "parameters": {
                            "display_text": button_text,
                            "url": url
                        }
                    }
                }
            }
            
            logging.info(f"🔗 Enviando botão CTA: {button_text} -> {url}")
            
            # 🛡️ RATE LIMITING ANTI-BAN
            SharedRateLimiter.check_and_wait(self._phone_number_id)
            
            # Enviar via método seguro
            url_endpoint = f"https://graph.facebook.com/v23.0/{self._phone_number_id}/messages"
            response = self._send_direct(url_endpoint, cta_payload, self._phone_number_id)
            
            if response.status_code == 200:
                response_data = response.json()
                logging.info(f"✅ Botão CTA enviado com sucesso")
                return True, response_data
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                logging.error(f"❌ Falha ao enviar CTA: {response.status_code} - {error_data}")
                return False, error_data
                
        except Exception as e:
            logging.error(f"Erro ao enviar botão CTA: {str(e)}")
            return False, {'error': f'Erro inesperado: {str(e)}'}
    
    def _get_template_structure(self, template_name: str) -> Optional[Dict]:
        """Busca estrutura e linguagem de um template específico via API"""
        try:
            if not self.business_account_id:
                return None
                
            url = f"{self.base_url}/{self.business_account_id}/message_templates"
            headers = self.headers  # 🔒 Usar headers da sessão atualizada
            
            params = {
                'fields': 'name,status,language,components',
                'name': template_name
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                # Buscar template específico por nome
                for template in templates:
                    if template.get('name') == template_name and template.get('status') == 'APPROVED':
                        return {
                            'name': template.get('name'),
                            'language': template.get('language'),
                            'components': template.get('components', [])
                        }
                        
            return None
            
        except Exception as e:
            logging.warning(f"Erro ao buscar estrutura do template {template_name}: {e}")
            return None
    
    def _discover_phones_from_bm(self, business_account_id: str) -> Optional[List[str]]:
        """Descobre phone numbers de uma Business Manager específica"""
        try:
            url = f"{self.base_url}/{business_account_id}/phone_numbers"
            headers = self.headers  # 🔒 Usar headers da sessão atualizada
            
            # 🔐 PROXY PROTEGIDO - Anti-ban da Meta
            # Proxy removido - usando conexão direta
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                phones = []
                for phone_data in data.get('data', []):
                    phone_id = phone_data.get('id')
                    if phone_id:
                        phones.append(phone_id)
                
                logging.info(f"📱 DESCOBERTOS {len(phones)} PHONES NA BM {business_account_id}")
                return phones if phones else None
                        
            else:
                logging.warning(f"Erro ao buscar phones da BM {business_account_id}: {response.status_code}")
                return None
            
        except Exception as e:
            logging.warning(f"Erro ao descobrir phones da BM {business_account_id}: {e}")
            return None
    
    def send_template_message(self, phone: str, template_name: str, language_code: str = None, 
                            parameters: Optional[List[str]] = None, phone_number_id: Optional[str] = None,
                            lead_index: int = None) -> Tuple[bool, Dict]:
        """
        Envia template message usando Phone Number ID específico dos 5 phones ativos
        Business Manager 580318035149016 - sem erro #135000
        """
        # SIMULAR INDICADOR DE DIGITAÇÃO PARA TEMPLATES
        message_length = len(template_name) + (len(str(parameters)) if parameters else 0)
        self._simulate_typing_indicator(phone, message_length)
        
        # CRITICAL: Always refresh credentials before sending
        self._refresh_credentials()
        
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            # All Phone IDs have access to approved templates - use selected Phone ID directly
            used_phone_id = phone_number_id or self.phone_number_id
            url = f"{self.base_url}/{used_phone_id}/messages"
            
            # FORÇA DETECÇÃO PARA TEMPLATES MODELO_* - SEMPRE PORTUGUÊS BRASILEIRO
            if template_name.lower().startswith('modelo'):
                language_code = 'pt_BR'
                logging.info(f"🇧🇷 FORÇADO PT_BR: Template '{template_name}' detectado como português brasileiro")
            # AUTO-DETECT LANGUAGE CODE - BUSCA DINÂMICA NA API
            elif not language_code or len(language_code) > 10 or ' ' in language_code:
                # Tentar buscar linguagem real do template via API
                try:
                    template_info = self._get_template_structure(template_name)
                    if template_info and 'language' in template_info:
                        language_code = template_info['language']
                        logging.info(f"🔍 LANGUAGE AUTO-DETECTADO VIA API: '{language_code}' para template {template_name}")
                    else:
                        # Fallback para mapeamento manual conhecido
                        template_languages = {
                            # BM 2089992404820473 (Ricardo/Iara) - Templates em inglês
                            'ricardo_template_1753485474_512444ac': 'en',
                            'ricardo_template_1753487909_d79bcb95': 'en', 
                            'ricardo_template_1753485525_d3a7f18d': 'en',
                            'ricardo_template_1753485590_b501867c': 'en',
                            'ricardo_template_1753485866_2620345a': 'en',
                            'ricardo_template_1753485422_108ba28d': 'en',
                            'ricardo_template_1753487895_cbe4d528': 'en',
                            'ricardo_template_1753487687_5860ab23': 'en',
                            'ricardo_template_1753487879_89f32594': 'en',
                            'ricardo_template_1753485563_5882b9ba': 'en',
                            'modelo21': 'pt_BR',  # Template em português
                            'modelo_80': 'pt_BR',  # Template em português brasileiro - CORRIGIDO
                            'aaut': 'en',  # Template em inglês
                            'modelo1': 'en',
                            'modelo2': 'en', 
                            'modelo3': 'en',
                            # BM 1243060407061288 (Pamela Lins) - TODOS em inglês
                            'kleber_template_1753741080_9db55e1f': 'en',
                            'kleber_template_1753740861_1352659a': 'en',
                            'kleber_template_1753740788_105c5281': 'en',
                            'kleber_template_1753740673_863dbbd4': 'en',
                            'kleber_template_1753740646_1b1e0fa5': 'en',
                            'kleber_template_1753740590_b8149029': 'en',
                            'kleber_template_1753740575_e78517c8': 'en',
                            'kleber_template_1753740559_6a596614': 'en',
                            'maria_template_1753740220_12264620': 'en',
                            'maria_template_1753740069_92fd4c2d': 'en'
                        }
                        # SMART FALLBACK: Se template não estiver mapeado, detectar pelo nome
                        if template_name in template_languages:
                            language_code = template_languages[template_name]
                        elif template_name.lower().startswith('modelo'):
                            language_code = 'pt_BR'
                        else:
                            language_code = 'en'
                        logging.info(f"🔧 LANGUAGE FALLBACK MANUAL: '{language_code}' para template {template_name}")
                except Exception as e:
                    logging.warning(f"⚠️ Erro ao buscar linguagem do template: {e}")
                    # SMART DEFAULT: Templates que começam com "modelo" são em português brasileiro
                    if template_name.lower().startswith('modelo'):
                        language_code = 'pt_BR'
                    else:
                        language_code = 'en'
                    logging.info(f"🔧 LANGUAGE PADRÃO APLICADO: '{language_code}' para template {template_name}")
            else:
                # Usar o language_code fornecido se válido
                logging.info(f"🔍 USANDO LANGUAGE CODE FORNECIDO: '{language_code}' para template {template_name}")
                    
            logging.info(f"TENTANDO TEMPLATE APROVADO: {template_name}")
            logging.info(f"Phone Number ID: {used_phone_id}")
            logging.info(f"Language Code: {language_code}")
            
            # Format phone number
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            # Try different template structures to bypass error #135000
            success = False
            error_msg = ""
            
            # Method 1: Minimal structure without optional components
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language_code
                    }
                }
            }
            
            # Add components only if parameters provided
            if parameters:
                components = []
                
                # Add body with parameters - ORDEM CORRIGIDA: {{1}} = CPF, {{2}} = Nome
                if len(parameters) >= 2:
                    components.append({
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': str(parameters[0])},  # {{1}} = CPF (parameters[0])
                            {'type': 'text', 'text': str(parameters[1])}   # {{2}} = Nome (parameters[1])
                        ]
                    })
                
                # Add button with CPF parameter if available - CPF continua sendo parameters[0]
                if len(parameters) >= 1:
                    components.append({
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {'type': 'text', 'text': str(parameters[0])}  # Button URL usa CPF
                        ]
                    })
                
                payload['template']['components'] = components
            
            logging.info(f"Payload tentativa: {payload}")
            
            # Enviar diretamente (proxy removido)
            try:
                response = self._send_direct(url, payload, self._phone_number_id)
            except Exception as e:
                logging.error(f"Direct connection failed: {str(e)}")
                return False, {'error': f'Erro de conexão: {str(e)}'}
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', '')
                
                # CRITICAL DEBUGGING: Log complete API response
                logging.info(f"🔍 COMPLETE API RESPONSE: {data}")
                logging.info(f"✅ TEMPLATE APPROVED SENT - Message ID: {message_id}")
                logging.info(f"📱 MESSAGE SENT TO: {formatted_phone} - TEMPLATE: {template_name}")
                
                # Check contact resolution for delivery validation
                contacts = data.get('contacts', [])
                if contacts:
                    contact_info = contacts[0]
                    wa_id = contact_info.get('wa_id', 'unknown')
                    input_phone = contact_info.get('input', 'unknown')
                    logging.info(f"📋 CONTACT INFO: Input={input_phone}, WhatsApp_ID={wa_id}")
                    
                    # WARNING: Check if WhatsApp ID was resolved properly
                    if wa_id == 'unknown' or not wa_id:
                        logging.warning(f"⚠️  WhatsApp ID NOT RESOLVED for {formatted_phone} - MESSAGE MAY NOT BE DELIVERED!")
                else:
                    logging.warning(f"⚠️  NO CONTACT INFO in response - MESSAGE MAY NOT BE DELIVERED!")
                
                return True, {
                    'messageId': message_id,
                    'whatsAppId': message_id,
                    'status': 'sent',
                    'template_used': template_name,
                    'contacts': contacts,
                    'api_response': data
                }
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', response.text)
                error_code = error_data.get('error', {}).get('code')
                
                # ERRO #135000: Tentar fallback para mensagem de texto (CONFIRMADO que esta BM também tem o problema)
                if error_code == 135000:
                    logging.warning(f"⚠️ ERRO #135000 DETECTADO - TENTANDO FALLBACK PARA MENSAGEM DE TEXTO")
                    
                    # Construir mensagem baseada no template e parâmetros
                    if parameters and len(parameters) >= 2:
                        # CORREÇÃO ORDEM: parameters[0] = CPF, parameters[1] = Nome (ordem correta conforme template)
                        cpf = str(parameters[0])
                        nome = str(parameters[1])
                        fallback_message = f"Olá {nome},\n\nVocê possui pendências financeiras no CPF {cpf}.\n\nPara consultar detalhes e negociar, acesse: https://example.com/{cpf}\n\nAtenciosamente,\nEquipe"
                        
                        # Enviar como mensagem de texto
                        text_success, text_result = self.send_text_message(phone, fallback_message, used_phone_id)
                        
                        if text_success:
                            logging.info(f"✅ FALLBACK SUCESSO: Mensagem enviada como texto após erro #135000")
                            return True, {
                                'messageId': text_result.get('messageId', ''),
                                'whatsAppId': text_result.get('whatsAppId', ''),
                                'status': 'sent_as_text',
                                'template_used': f"{template_name}_fallback",
                                'fallback_reason': 'Template error #135000 - sent as text message',
                                'contacts': text_result.get('contacts', [])
                            }
                        else:
                            logging.error(f"❌ FALLBACK FAILED: Erro também no envio de texto")
                
                # Log erro original se fallback não funcionou ou não foi aplicável
                logging.error(f"❌ TEMPLATE FAILED: {template_name} ({language_code}) - Error #{error_code}: {error_message}")
                
                return False, {
                    'error': f'Template {template_name} falhou (#{error_code}): {error_message}',
                    'error_code': error_code,
                    'business_manager_id': self._business_account_id,
                    'template_name': template_name,
                    'language_code': language_code,
                    'phone_number_id': used_phone_id
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão ao enviar template aprovado: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}
    
    def send_template_message_with_button(self, phone: str, template_name: str, language_code: str = 'en', 
                                        parameters: Optional[List[str]] = None, button_param: str = '', 
                                        lead_index: int = None) -> Tuple[bool, Dict]:
        """Send template message with button parameter (like modelo_3)"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            # Format phone number
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            # Build template payload with button
            components = []
            
            # Body component with parameters
            if parameters:
                formatted_params = []
                for param in parameters:
                    param_index = len(formatted_params)
                    formatted_params.append({
                        'type': 'text',
                        'parameter_name': str(param_index + 1),
                        'text': str(param).strip()
                    })
                
                components.append({
                    'type': 'body',
                    'parameters': formatted_params
                })
            
            # Button component with parameter - correct format for URL buttons
            if button_param:
                components.append({
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,  # Use integer instead of string
                    'parameters': [{
                        'type': 'text',
                        'text': str(button_param).strip()
                    }]
                })
            
            template_payload = {
                'name': template_name,
                'language': {
                    'code': language_code
                },
                'components': components
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'template',
                'template': template_payload
            }
            
            # Enviar diretamente (proxy removido)
            try:
                response = self._send_direct(url, payload, self._phone_number_id)
            except Exception as e:
                logging.error(f"Direct connection failed: {str(e)}")
                return False, {'error': f'Erro de conexão: {str(e)}'}
            
            if response.status_code == 200:
                data = response.json()
                return True, {
                    'messageId': data.get('messages', [{}])[0].get('id', ''),
                    'whatsAppId': data.get('messages', [{}])[0].get('id', ''),
                    'status': 'sent'
                }
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', response.text)
                
                logging.error(f"Template with button failed: {response.status_code} - {error_message}")
                logging.error(f"Failed payload was: {payload}")
                
                return False, {
                    'error': f'Erro HTTP {response.status_code}',
                    'details': error_message
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending WhatsApp template with button: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}
    
    def send_button_message(self, phone: str, message: str, buttons: List[Dict]) -> Tuple[bool, Dict]:
        """Send message with interactive buttons (template-based)"""
        # Note: WhatsApp Business API requires pre-approved templates for button messages
        # This is a simplified implementation - in production, you'd need approved templates
        
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        if not buttons:
            # If no buttons, send as simple text
            return self.send_text_message(phone, message)
        
        # For now, send as text message with button descriptions
        # In production, you'd use approved interactive templates
        button_text = "\n\n📱 Opções disponíveis:"
        for i, button in enumerate(buttons, 1):
            button_text += f"\n{i}. {button.get('text', button.get('label', 'Opção'))}"
            if button.get('url'):
                button_text += f" - {button['url']}"
        
        full_message = message + button_text
        return self.send_text_message(phone, full_message)
    
    def send_interactive_cta_url_message(self, phone: str, message: str, button_text: str, url: str) -> Tuple[bool, Dict]:
        """Send Interactive CTA URL Button Message (no template approval needed)"""
        # SIMULAR INDICADOR DE DIGITAÇÃO PARA BOTÕES
        self._simulate_typing_indicator(phone, len(message))
        
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            # Format phone number (same pattern as other methods)
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "cta_url",
                    "body": {
                        "text": message
                    },
                    "action": {
                        "name": "cta_url",
                        "parameters": {
                            "display_text": button_text,
                            "url": url
                        }
                    }
                }
            }
            
            # Send via direct connection
            url_endpoint = f"{self.base_url}/{self.phone_number_id}/messages"
            response = self._send_direct(url_endpoint, payload, self._phone_number_id)
            
            if response.status_code == 200:
                data = response.json()
                return True, {
                    'messageId': data.get('messages', [{}])[0].get('id', ''),
                    'status': 'sent'
                }
            else:
                logging.error(f"CTA URL button failed: {response.status_code} - {response.text}")
                return False, {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Error sending CTA URL button: {str(e)}")
            return False, {'error': str(e)}
    
    def send_interactive_copy_code_message(self, phone: str, message: str, button_text: str, code_to_copy: str) -> Tuple[bool, Dict]:
        """Send an interactive message with a copy code button"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        # Simulate typing indicator
        self._simulate_typing_indicator(phone, len(message))
        
        try:
            # Format phone number (same pattern as other methods)
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "copy_code_button",
                                    "title": button_text[:20]  # WhatsApp limit 20 chars
                                }
                            }
                        ]
                    }
                }
            }
            
            # Send via direct connection
            url_endpoint = f"{self.base_url}/{self.phone_number_id}/messages"
            response = self._send_direct(url_endpoint, payload, self._phone_number_id)
            
            if response.status_code == 200:
                data = response.json()
                # Automaticamente enviar o código após o botão (WhatsApp não suporta copia e cola nativo)
                import time
                time.sleep(1)
                
                # Enviar código em mensagem separada para facilitar cópia
                code_message = f"📋 *CÓDIGO PIX:*\n```{code_to_copy}```\n\n💡 Toque e segure no código acima para copiar!"
                
                # Enviar código copia e cola
                self.send_text_message(phone, code_message)
                
                return True, {
                    'messageId': data.get('messages', [{}])[0].get('id', ''),
                    'status': 'sent'
                }
            else:
                logging.error(f"Copy code button failed: {response.status_code} - {response.text}")
                return False, {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Error sending copy code button: {str(e)}")
            return False, {'error': str(e)}
    
    def get_message_status(self, message_id: str) -> Tuple[bool, Dict]:
        """Get message delivery status"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        try:
            url = f"{self.base_url}/{message_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, {
                    'status': data.get('status', 'unknown'),
                    'timestamp': data.get('timestamp', ''),
                    'recipient_id': data.get('recipient_id', '')
                }
            else:
                return False, {'error': f'Erro ao consultar status: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting message status: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}

    def get_business_account_id(self) -> Optional[str]:
        """Get Business Account ID from current WhatsApp Business account"""
        if not self.is_configured():
            return None
        
        try:
            # Get business account info
            url = f"{self.base_url}/{self.phone_number_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Extract business account ID from the response
                business_account_id = data.get('business_account_id')
                if business_account_id:
                    logging.info(f"Business Account ID found: {business_account_id}")
                    return business_account_id
                else:
                    logging.warning("Business Account ID not found in response")
                    return None
            else:
                logging.error(f"Failed to get business account info: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting business account ID: {str(e)}")
            return None

    def get_available_templates(self, business_account_id_override: Optional[str] = None) -> List[Dict]:
        """Get all available message templates from the WhatsApp Business account"""
        if not self.is_configured():
            return []
        
        try:
            # Use the current Business Manager with 10 phones active
            business_account_id = business_account_id_override or self._business_account_id or "1779444112928258"
            
            url = f"{self.base_url}/{business_account_id}/message_templates"
            logging.info(f"Buscando templates do Business Account: {business_account_id}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                # Lista de templates aprovados específicos baseada na BM atual
                if business_account_id == "639849885789886":
                    # BM Jose Carlos - usar templates reais descobertos
                    approved_template_names = [
                        'jose_template_1752924484_01d5f008',
                        'jose_template_1752924461_d50dcbee',
                        'modelo3',
                        'jose_template_1752883070_87d0311e',
                        'jose_template_1752882617_40dc6e72'
                    ]
                elif business_account_id == "580318035149016":
                    # BM Cleide
                    approved_template_names = [
                        'cleide_template_1752692476_0f370e02',
                        'modelo1',
                        'modelo2'
                    ]
                elif business_account_id == "1523966465251146":
                    # BM Michele - templates descobertos dinamicamente
                    approved_template_names = [
                        'michele_template_1753101024_fef7402b',
                        'michele_template_1753073988_55619758',
                        'aviso'
                    ]
                else:
                    # BM padrão
                    approved_template_names = [
                        'replica_approved_4402f709',
                        'replica_approved_30b53a7c', 
                        'final_approved_a251c625',
                        'final_approved_246bd703',
                        'final_approved_eace7f6f'
                    ]
                
                formatted_templates = []
                for template in templates:
                    # FILTRAR APENAS TEMPLATES APROVADOS E NA LISTA ESPECÍFICA
                    template_status = template.get('status', 'UNKNOWN')
                    template_name = template.get('name', '')
                    
                    if template_status != 'APPROVED':
                        continue  # Pular templates não aprovados
                    
                    if template_name not in approved_template_names:
                        continue  # Pular templates não na lista específica
                    
                    # Process template data
                    template_info = {
                        'name': template.get('name', ''),
                        'language': template.get('language', 'en'),
                        'category': template.get('category', 'UTILITY'),
                        'status': template_status,
                        'components': template.get('components', []),
                        'has_parameters': any(
                            comp.get('text', '').find('{{') != -1 
                            for comp in template.get('components', [])
                            if comp.get('type') == 'BODY'
                        ),
                        'has_buttons': any(
                            comp.get('type') == 'BUTTONS' 
                            for comp in template.get('components', [])
                        )
                    }
                    formatted_templates.append(template_info)
                
                logging.info(f"Encontrados {len(formatted_templates)} templates APROVADOS (filtrados de {len(templates)} totais)")
                return formatted_templates
                
            else:
                logging.error(f"Erro ao buscar templates: {response.status_code} - {response.text}")
                # Fallback para templates conhecidos
                return self._get_fallback_templates()
                
        except Exception as e:
            logging.error(f"Erro na busca de templates: {str(e)}")
            return self._get_fallback_templates()
    
    def _get_fallback_templates(self) -> List[Dict]:
        """Templates reais aprovados na conta (ID: 746006914691827)"""
        logging.info("Usando templates APROVADOS da conta")
        return [
            {
                'name': 'modelo1',
                'language': 'en',
                'category': 'UTILITY', 
                'status': 'APPROVED',
                'id': '1409279126974744',
                'components': [
                    {
                        'type': 'BODY',
                        'text': 'Prezado (a) {{2}}, me chamo Damião Alves e sou tabelião do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{{1}}.*\n\nPara evitar restrições ou bloqueios nas próximas horas, orientamos que verifique sua situação e regularize imediatamente.\n\nAtenciosamente,\nCartório 5º Ofício de Notas'
                    },
                    {
                        'type': 'FOOTER',
                        'text': 'PROCESSO Nº: 0009-13.2025.0100-NE'
                    },
                    {
                        'type': 'BUTTONS',
                        'buttons': [
                            {
                                'type': 'URL',
                                'text': 'Regularizar meu CPF',
                                'url': 'https://www.intimacao.org/{{1}}'
                            }
                        ]
                    }
                ],
                'has_parameters': True,
                'has_buttons': True
            },
            {
                'name': 'modelo2',
                'language': 'en',
                'category': 'UTILITY', 
                'status': 'APPROVED',
                'id': '1100293608691435',
                'components': [
                    {
                        'type': 'HEADER',
                        'format': 'TEXT',
                        'text': 'Notificação Extrajudicial'
                    },
                    {
                        'type': 'BODY',
                        'text': 'Prezado (a) {{2}}, me chamo Damião Alves Vaz. Sou tabelião do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{{1}}.*\n\nPara evitar restrições ou bloqueios nas próximas horas, orientamos que verifique sua situação e regularize imediatamente.\n\nAtenciosamente,\nCartório 5º Ofício de Notas'
                    },
                    {
                        'type': 'FOOTER',
                        'text': 'PROCESSO Nº: 0009-13.2025.0100-NE'
                    },
                    {
                        'type': 'BUTTONS',
                        'buttons': [
                            {
                                'type': 'URL',
                                'text': 'Regularizar meu CPF',
                                'url': 'https://www.intimacao.org/{{1}}'
                            }
                        ]
                    }
                ],
                'has_parameters': True,
                'has_buttons': True
            }
        ]
    
    def get_next_phone_id(self) -> str:
        """Get next phone ID in rotation for load balancing"""
        if not hasattr(self, '_available_phones') or not self._available_phones:
            # Initialize with working phones if not set
            self._available_phones = [
                "739188885941111",  # Phone 1: +1 804-210-0219 (Tabelião Cleide Maria)
                "710232202173614",  # Phone 2: +1 830-445-8877 (Tabelião Cleide Maria)
                "709194588941211"   # Phone 3: 15558146853 (Cleide Maria Da Silva)
            ]
            self._current_phone_index = 0
        
        # Rotate to next phone
        phone_id = self._available_phones[self._current_phone_index]
        self._current_phone_index = (self._current_phone_index + 1) % len(self._available_phones)
        
        return phone_id
    
    def get_all_phone_numbers(self) -> List[Dict]:
        """Get all available phone numbers with their details"""
        return [
            {'id': '739188885941111', 'number': '+1 804-210-0219', 'name': 'Tabelião Cleide Maria'},
            {'id': '710232202173614', 'number': '+1 830-445-8877', 'name': 'Tabelião Cleide Maria'},
            {'id': '709194588941211', 'number': '15558146853', 'name': 'Cleide Maria Da Silva'}
        ]
    
    def send_template_with_load_balancing(self, phone: str, template_name: str, language_code: str = 'en', 
                                        parameters: Optional[List[str]] = None, lead_index: int = None) -> Tuple[bool, Dict]:
        """Send template message using load balancing across multiple phone numbers"""
        if not self.is_configured():
            return False, {'error': 'WhatsApp Business API não configurada'}
        
        # Get next phone ID for load balancing
        phone_id = self.get_next_phone_id()
        
        try:
            url = f"{self.base_url}/{phone_id}/messages"
            
            # Format phone number
            formatted_phone = phone
            if phone.startswith('55'):
                formatted_phone = '+' + phone
            elif not phone.startswith('+'):
                formatted_phone = '+55' + phone
            
            # Build template payload
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {'code': language_code}
                }
            }
            
            # Add components if parameters provided
            if parameters:
                components = []
                
                # Add body with parameters - ORDEM CORRIGIDA: Interface envia [CPF, Nome], template espera {{1}}=CPF, {{2}}=Nome
                if len(parameters) >= 2:
                    cpf_param = str(parameters[0])   # parameters[0] = CPF (da interface)
                    nome_param = str(parameters[1])  # parameters[1] = Nome (da interface)
                    components.append({
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': nome_param},  # {{1}} = Nome
                            {'type': 'text', 'text': cpf_param}   # {{2}} = CPF
                        ]
                    })
                
                # Add button with CPF parameter - template URL espera CPF
                if len(parameters) >= 1:
                    # CORREÇÃO CRÍTICA: Template URL precisa do CPF, parameters[0] = CPF (da interface)
                    cpf_param = str(parameters[0])  # parameters[0] = CPF para o link
                    logging.info(f"🔘 BOTÃO DEBUG: parameters={parameters}, cpf_param='{cpf_param}'")
                    components.append({
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [{'type': 'text', 'text': cpf_param}]
                    })
                
                payload['template']['components'] = components
            
            # Enviar diretamente (proxy removido)
            try:
                response = self._send_direct(url, payload, self._phone_number_id)
            except Exception as e:
                logging.error(f"Direct connection failed: {str(e)}")
                return False, {'error': f'Erro de conexão: {str(e)}'}
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', '')
                
                # Get phone details for logging
                phone_details = next((p for p in self.get_all_phone_numbers() if p['id'] == phone_id), 
                                   {'number': phone_id, 'name': 'Unknown'})
                
                logging.info(f"Template sent via {phone_details['number']} ({phone_details['name']}): {message_id}")
                
                return True, {
                    'messageId': message_id,
                    'whatsAppId': message_id,
                    'status': 'sent',
                    'phone_used': phone_details['number'],
                    'phone_name': phone_details['name'],
                    'template_used': template_name
                }
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', response.text)
                
                logging.error(f"Template failed from phone {phone_id}: {error_message}")
                
                return False, {
                    'error': f'Template "{template_name}" failed: {error_message}',
                    'phone_used': phone_id,
                    'template_name': template_name
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection error sending template: {str(e)}")
            return False, {'error': f'Connection error: {str(e)}'}
    
    def test_all_phones(self) -> Dict:
        """Test all phone numbers to verify which ones are working"""
        results = {}
        
        for phone_info in self.get_all_phone_numbers():
            phone_id = phone_info['id']
            phone_number = phone_info['number']
            
            try:
                # Test with a simple status check
                url = f"{self.base_url}/{phone_id}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results[phone_number] = {
                        'status': 'working',
                        'quality': data.get('quality_rating', 'unknown'),
                        'verified_name': data.get('verified_name', 'unknown'),
                        'id': phone_id
                    }
                else:
                    results[phone_number] = {
                        'status': 'error',
                        'error': f'HTTP {response.status_code}',
                        'id': phone_id
                    }
            except Exception as e:
                results[phone_number] = {
                    'status': 'error',
                    'error': str(e),
                    'id': phone_id
                }
        
        return results