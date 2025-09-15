"""
Proxy Service - Gerencia rotação e uso de proxies para requisições HTTP
"""

import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

class ProxyService:
    def __init__(self, app=None, db=None):
        self.current_proxy = None
        self.rotation_index = 0
        self._active_proxies_cache = []
        self._last_cache_refresh = None
        self.app = app
        self.db = db
        
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy for rotation"""
        try:
            if self.app:
                with self.app.app_context():
                    from models import Proxy
                    proxy = Proxy.get_next_proxy()
                    if proxy:
                        # CRITICAL: Update proxy usage with proper Flask context
                        proxy.last_used = datetime.utcnow()
                        self.db.session.commit()
                        self.current_proxy = proxy
                        proxy_dict = proxy.get_requests_proxy_dict()
                        if proxy_dict:
                            logging.info(f"Using proxy: {proxy.name} ({proxy.proxy_string.split(':')[0]})")
                            return proxy_dict
                    
                    # No proxies available, use direct connection
                    logging.warning("No proxies available, using direct connection")
                    self.current_proxy = None
                    return None
            else:
                # Fallback: try direct import (for when already in app context)
                from models import Proxy
                proxy = Proxy.get_next_proxy()
                if proxy:
                    self.current_proxy = proxy
                    proxy_dict = proxy.get_requests_proxy_dict()
                    if proxy_dict:
                        logging.info(f"Using proxy: {proxy.name} ({proxy.proxy_string.split(':')[0]})")
                        return proxy_dict
                
                logging.warning("No proxies available, using direct connection")
                self.current_proxy = None
                return None
            
        except Exception as e:
            logging.error(f"Error getting proxy: {str(e)}")
            self.current_proxy = None
            return None
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with proxy rotation"""
        max_retries = 3
        last_exception = None
        
        # Check if specific proxy is provided (for rotation)
        specific_proxy = kwargs.pop('proxies', None)
        
        for attempt in range(max_retries):
            try:
                # Use specific proxy if provided, otherwise get next proxy
                if specific_proxy:
                    proxy_dict = specific_proxy
                    # Don't change self.current_proxy for external proxy calls
                else:
                    proxy_dict = self.get_next_proxy()
                
                # Add proxy to request if available
                if proxy_dict:
                    kwargs['proxies'] = proxy_dict
                    kwargs['timeout'] = kwargs.get('timeout', 15)  # Increase timeout for proxy
                else:
                    kwargs['timeout'] = kwargs.get('timeout', 10)  # Normal timeout for direct
                
                # Make the request
                response = requests.request(method, url, **kwargs)
                
                # If successful, mark proxy as successful
                if response.status_code < 400:
                    if specific_proxy and proxy_dict:
                        # For specific proxy, need to find which proxy object it belongs to
                        active_proxies = self.get_active_proxies()
                        for proxy in active_proxies:
                            if proxy.get_requests_proxy_dict() == proxy_dict:
                                proxy.increment_success()
                                break
                    elif self.current_proxy:
                        self.current_proxy.increment_success()
                
                return response
                
            except Exception as e:
                last_exception = e
                logging.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                # Mark proxy as failed if we were using one
                if specific_proxy and proxy_dict:
                    # For specific proxy, need to find which proxy object it belongs to
                    active_proxies = self.get_active_proxies()
                    for proxy in active_proxies:
                        if proxy.get_requests_proxy_dict() == proxy_dict:
                            proxy.increment_error()
                            logging.warning(f"Marking proxy {proxy.name} as failed")
                            break
                elif self.current_proxy:
                    self.current_proxy.increment_error()
                    logging.warning(f"Marking proxy {self.current_proxy.name} as failed")
                
                # If this was the last attempt, raise the exception
                if attempt == max_retries - 1:
                    logging.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
                    raise last_exception
        
        # Should never reach here, but just in case
        raise last_exception or Exception("Unknown error in make_request")
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request with proxy rotation"""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request with proxy rotation"""
        return self.make_request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Make PUT request with proxy rotation"""
        return self.make_request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Make DELETE request with proxy rotation"""
        return self.make_request('DELETE', url, **kwargs)
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get statistics about proxy usage"""
        try:
            with current_app.app_context():
                from models import Proxy
                proxies = Proxy.query.all()
                active_proxies = [p for p in proxies if p.is_active]
                
                total_success = sum(p.success_count for p in proxies)
                total_errors = sum(p.error_count for p in proxies)
                total_requests = total_success + total_errors
                
                success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
                
                return {
                    'total_proxies': len(proxies),
                    'active_proxies': len(active_proxies),
                    'total_requests': total_requests,
                    'total_success': total_success,
                    'total_errors': total_errors,
                    'success_rate': round(success_rate, 2),
                    'current_proxy': self.current_proxy.name if self.current_proxy else 'Direct Connection'
                }
            
        except Exception as e:
            logging.error(f"Error getting proxy stats: {str(e)}")
            return {}
    
    def get_active_proxies(self):
        """Get all active proxies for rotation"""
        try:
            from datetime import datetime, timedelta
            
            # Refresh cache if older than 30 seconds or empty
            now = datetime.utcnow()
            if (not self._last_cache_refresh or 
                (now - self._last_cache_refresh).total_seconds() > 30 or
                not self._active_proxies_cache):
                
                if self.app:
                    with self.app.app_context():
                        from models import Proxy
                        self._active_proxies_cache = Proxy.query.filter_by(is_active=True).all()
                        self._last_cache_refresh = now
                        logging.info(f"🔄 Cache de proxies atualizado: {len(self._active_proxies_cache)} proxies ativas")
                else:
                    # Fallback: try direct import (for when already in app context)
                    from models import Proxy
                    self._active_proxies_cache = Proxy.query.filter_by(is_active=True).all()
                    self._last_cache_refresh = now
                    logging.info(f"🔄 Cache de proxies atualizado: {len(self._active_proxies_cache)} proxies ativas")
            
            return self._active_proxies_cache
            
        except Exception as e:
            logging.error(f"Error getting active proxies: {str(e)}")
            return []
    
    def get_proxy_for_rotation(self, lead_index: int) -> Optional[Dict]:
        """Get specific proxy based on rotation index for distributed sending"""
        try:
            active_proxies = self.get_active_proxies()
            
            if not active_proxies:
                logging.warning("❌ Nenhuma proxy ativa para rotação - usando conexão direta")
                return None
            
            # Calculate which proxy to use based on lead index
            proxy_index = lead_index % len(active_proxies)
            selected_proxy = active_proxies[proxy_index]
            
            proxy_dict = selected_proxy.get_requests_proxy_dict()
            if proxy_dict:
                logging.info(f"🔄 Lead #{lead_index + 1} → Proxy #{proxy_index + 1}: {selected_proxy.name}")
                self.current_proxy = selected_proxy
                return proxy_dict
            else:
                logging.warning(f"⚠️ Proxy {selected_proxy.name} inválida")
                return None
                
        except Exception as e:
            logging.error(f"Error in proxy rotation: {str(e)}")
            return None
    
    def distribute_leads_across_proxies(self, total_leads: int) -> Dict[str, Any]:
        """Calculate lead distribution across active proxies"""
        try:
            active_proxies = self.get_active_proxies()
            
            if not active_proxies:
                return {
                    'success': False,
                    'message': 'Nenhuma proxy ativa encontrada',
                    'proxies': [],
                    'distribution': {}
                }
            
            # Calculate distribution
            leads_per_proxy = total_leads // len(active_proxies)
            remaining_leads = total_leads % len(active_proxies)
            
            distribution = {}
            proxy_info = []
            
            for i, proxy in enumerate(active_proxies):
                # First proxies get +1 lead if there are remaining leads
                proxy_leads = leads_per_proxy + (1 if i < remaining_leads else 0)
                
                distribution[proxy.id] = {
                    'proxy_name': proxy.name,
                    'proxy_host': proxy.proxy_string.split(':')[0],
                    'leads_count': proxy_leads,
                    'start_index': sum(distribution[p['proxy_id']]['leads_count'] 
                                     for p in proxy_info) if proxy_info else 0
                }
                distribution[proxy.id]['end_index'] = distribution[proxy.id]['start_index'] + proxy_leads - 1
                
                proxy_info.append({
                    'proxy_id': proxy.id,
                    'proxy_name': proxy.name,
                    'proxy_host': proxy.proxy_string.split(':')[0],
                    'leads_count': proxy_leads
                })
            
            logging.info(f"📊 DISTRIBUIÇÃO AUTOMÁTICA: {total_leads} leads → {len(active_proxies)} proxies")
            for info in proxy_info:
                logging.info(f"   • {info['proxy_name']}: {info['leads_count']} leads")
            
            return {
                'success': True,
                'total_leads': total_leads,
                'total_proxies': len(active_proxies),
                'leads_per_proxy_base': leads_per_proxy,
                'remaining_leads': remaining_leads,
                'proxies': proxy_info,
                'distribution': distribution
            }
            
        except Exception as e:
            logging.error(f"Error distributing leads: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao distribuir leads: {str(e)}',
                'proxies': [],
                'distribution': {}
            }

# Global proxy service instance will be initialized in app.py
# Global proxy_service instance - use singleton pattern
_proxy_service: Optional[ProxyService] = None

def init_proxy_service(app=None, db=None):
    """Initialize proxy service with Flask app context"""
    global _proxy_service
    _proxy_service = ProxyService(app, db)
    logging.info("✅ Proxy service initialized successfully")
    return _proxy_service

def get_proxy_service() -> Optional[ProxyService]:
    """Get the current proxy service instance"""
    return _proxy_service

def request_with_proxy(method: str, url: str, **kwargs):
    """Make request with proxy if available, fallback to direct request"""
    svc = get_proxy_service()
    if svc:
        return svc.make_request(method, url, **kwargs)
    else:
        logging.warning("Proxy service not available, making direct request")
        return requests.request(method, url, **kwargs)

# Backward compatibility - keep old reference for existing code
proxy_service = None