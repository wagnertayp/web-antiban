"""
Proxy Service - Gerencia rotação e uso de proxies para requisições HTTP
"""

import logging
import requests
from typing import Optional, Dict, Any
from models import Proxy
from app import db

class ProxyService:
    def __init__(self):
        self.current_proxy = None
        
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy for rotation"""
        try:
            proxy = Proxy.get_next_proxy()
            if proxy:
                self.current_proxy = proxy
                proxy_dict = proxy.get_requests_proxy_dict()
                if proxy_dict:
                    logging.info(f"Using proxy: {proxy.name} ({proxy.proxy_string.split(':')[0]})")
                    return proxy_dict
            
            # No proxies available, use direct connection
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
        
        for attempt in range(max_retries):
            try:
                # Get proxy for this request
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
                if self.current_proxy and response.status_code < 400:
                    self.current_proxy.increment_success()
                
                return response
                
            except Exception as e:
                last_exception = e
                logging.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                # Mark proxy as failed if we were using one
                if self.current_proxy:
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

# Global proxy service instance
proxy_service = ProxyService()