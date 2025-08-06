#!/usr/bin/env python3
"""
Remove ALL cache systems from WhatsApp Business API
"""
import re

def remove_cache_from_file():
    """Remove all cache references from the WhatsApp service file"""
    
    with open('services/whatsapp_business_api.py', 'r') as f:
        content = f.read()
    
    # Remove all cache-related code patterns
    patterns_to_remove = [
        r'.*cache.*para evitar rate limits.*\n',
        r'.*cached_phone_numbers.*\n',
        r'.*Usando credenciais em cache.*\n',
        r'.*rate limit prevention.*\n',
        r'.*_last_token_check.*\n',
        r'.*hasattr.*_cached_phone_numbers.*\n'
    ]
    
    original_content = content
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Force all _refresh_credentials calls to always discover fresh
    content = content.replace(
        'if not hasattr(self, \'_cached_phone_numbers\') or not self._cached_phone_numbers:',
        '# ALWAYS FRESH - NO CACHE'
    )
    
    content = content.replace(
        'else:\n                logging.info("Usando credenciais em cache para evitar rate limits")',
        ''
    )
    
    # Write back
    with open('services/whatsapp_business_api.py', 'w') as f:
        f.write(content)
    
    print("✅ All cache systems removed from WhatsApp Business API")
    print(f"📝 Content changed: {len(original_content)} -> {len(content)} characters")

if __name__ == "__main__":
    remove_cache_from_file()