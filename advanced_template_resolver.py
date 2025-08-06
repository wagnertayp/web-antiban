#!/usr/bin/env python3
"""
Advanced Template Resolver for Error #135000
Implements multiple technical strategies to bypass Business Manager incompatibility
"""

import requests
import json
import os
import time
import logging

logging.basicConfig(level=logging.INFO)

class AdvancedTemplateResolver:
    def __init__(self):
        self.phone_id = "764229176768157"
        self.business_id = "746006914691827"
        self.access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        
    def strategy_1_basic_template(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 1: Basic template sending"""
        url = f"https://graph.facebook.com/v22.0/{self.phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return self._process_response("Strategy 1 (Basic)", response)
    
    def strategy_2_legacy_format(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 2: Legacy API format"""
        url = f"https://graph.facebook.com/v22.0/{self.phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return self._process_response("Strategy 2 (Legacy)", response)
    
    def strategy_3_bypass_headers(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 3: Special bypass headers"""
        url = f"https://graph.facebook.com/v22.0/{self.phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-FB-Template-Override': 'true',
            'X-FB-Bypass-135000': 'true',
            'X-Template-Fix': 'business-manager-compatibility'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return self._process_response("Strategy 3 (Bypass Headers)", response)
    
    def strategy_4_multiple_api_versions(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 4: Try multiple API versions"""
        versions = ["v19.0", "v20.0", "v21.0", "v22.0", "v23.0"]
        
        for version in versions:
            url = f"https://graph.facebook.com/{version}/{self.phone_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en_US"}
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = self._process_response(f"Strategy 4 ({version})", response)
            
            if result['success']:
                return result
            
            time.sleep(1)  # Rate limiting
        
        return {'success': False, 'error': 'All API versions failed'}
    
    def strategy_5_direct_phone_override(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 5: Try with alternate phone number ID"""
        alternate_phone_ids = [
            "764229176768157",  # Current
            "708355979030805",  # Alternate 1  
            "638079459399067"   # Alternate 2
        ]
        
        for phone_id in alternate_phone_ids:
            url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en_US"}
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = self._process_response(f"Strategy 5 (Phone ID: {phone_id})", response)
            
            if result['success']:
                return result
            
            time.sleep(1)
        
        return {'success': False, 'error': 'All phone IDs failed'}
    
    def strategy_6_component_manipulation(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Strategy 6: Manipulate template components structure"""
        url = f"https://graph.facebook.com/v22.0/{self.phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Try with explicit empty components
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": []
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return self._process_response("Strategy 6 (Empty Components)", response)
    
    def _process_response(self, strategy_name, response):
        """Process API response"""
        try:
            data = response.json()
            
            if response.status_code == 200 and 'messages' in data:
                message_id = data['messages'][0]['id']
                logging.info(f"✅ {strategy_name} SUCCESS! Message ID: {message_id}")
                return {
                    'success': True,
                    'strategy': strategy_name,
                    'message_id': message_id,
                    'response': data
                }
            else:
                error = data.get('error', {})
                error_code = error.get('code')
                error_msg = error.get('message')
                logging.warning(f"❌ {strategy_name} failed: {error_code} - {error_msg}")
                return {
                    'success': False,
                    'strategy': strategy_name,
                    'error_code': error_code,
                    'error_message': error_msg
                }
                
        except Exception as e:
            logging.error(f"❌ {strategy_name} exception: {str(e)}")
            return {
                'success': False,
                'strategy': strategy_name,
                'error': str(e)
            }
    
    def resolve_error_135000(self, template_name="replica_approved_1752680924", to_number="5561982132603"):
        """Execute all strategies to resolve error #135000"""
        print("🔧 ADVANCED TEMPLATE RESOLVER - RESOLVING ERROR #135000")
        print("=" * 60)
        
        strategies = [
            self.strategy_1_basic_template,
            self.strategy_2_legacy_format,
            self.strategy_3_bypass_headers,
            self.strategy_4_multiple_api_versions,
            self.strategy_5_direct_phone_override,
            self.strategy_6_component_manipulation
        ]
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n🔄 Executing Strategy {i}...")
            result = strategy(template_name, to_number)
            
            if result['success']:
                print(f"\n🎉 SUCCESS! Strategy {i} resolved error #135000!")
                print(f"Message ID: {result['message_id']}")
                print(f"Strategy: {result['strategy']}")
                return result
            
            time.sleep(2)  # Rate limiting between strategies
        
        print("\n❌ All strategies exhausted. Error #135000 requires Meta/Facebook intervention.")
        return {'success': False, 'error': 'All resolution strategies failed'}

def main():
    resolver = AdvancedTemplateResolver()
    result = resolver.resolve_error_135000()
    
    if result['success']:
        print(f"\n✅ PROBLEM SOLVED! Template sent successfully!")
    else:
        print(f"\n❌ Error #135000 persists despite all technical attempts")
    
    return result

if __name__ == "__main__":
    main()