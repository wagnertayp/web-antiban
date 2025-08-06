#!/usr/bin/env python3
"""
Test template loading para BM Michele após a correção
"""
import os
import sys
sys.path.append('/home/runner/workspace')

from services.whatsapp_business_api import WhatsAppBusinessAPI

def test_michele_templates():
    api = WhatsAppBusinessAPI()
    
    print(f"Business Account ID: {api.business_account_id}")
    
    # Get templates
    templates = api.get_available_templates(business_account_id_override="1523966465251146")
    
    print(f"Templates encontrados: {len(templates)}")
    
    for template in templates:
        print(f"- {template}")

if __name__ == "__main__":
    test_michele_templates()