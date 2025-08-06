#!/usr/bin/env python3
"""
Diagnóstico completo do erro #135000 - Identificar causa raiz SEM fallback
Investigação técnica profunda para resolver templates diretamente
"""

import os
import requests
import json
from datetime import datetime

class Error135000RootCause:
    def __init__(self):
        self.token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.business_account_id = "580318035149016"
        self.phone_ids = [
            '709194588941211',  # Phone 1
            '767158596471686',  # Phone 2  
            '739188885941111',  # Phone 3
            '710232202173614',  # Phone 4
            '709956722204666'   # Phone 5
        ]
        
    def check_template_status(self):
        """Verificar status atual dos templates aprovados"""
        print("🔍 INVESTIGAÇÃO: Status atual dos templates")
        
        url = f'https://graph.facebook.com/v22.0/{self.business_account_id}/message_templates'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                print(f"📋 Templates encontrados: {len(templates)}")
                
                approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
                print(f"✅ Templates aprovados: {len(approved_templates)}")
                
                for template in approved_templates:
                    name = template.get('name', '')
                    status = template.get('status', '')
                    category = template.get('category', '')
                    language = template.get('language', '')
                    
                    print(f"   📝 {name} - Status: {status}, Categoria: {category}, Idioma: {language}")
                
                return approved_templates
            else:
                print(f"❌ Erro ao buscar templates: {response.status_code}")
                print(response.text)
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def check_phone_number_permissions(self):
        """Verificar permissões específicas de cada Phone Number"""
        print("\n🔍 INVESTIGAÇÃO: Permissões dos Phone Numbers")
        
        for i, phone_id in enumerate(self.phone_ids, 1):
            print(f"\n📱 Phone {i}: {phone_id}")
            
            # Check phone number details
            url = f'https://graph.facebook.com/v22.0/{phone_id}'
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    display_phone = data.get('display_phone_number', 'N/A')
                    status = data.get('verified_name', 'N/A')
                    quality = data.get('quality_rating', 'N/A')
                    
                    print(f"   📞 Número: {display_phone}")
                    print(f"   ✅ Status: {status}")
                    print(f"   ⭐ Quality: {quality}")
                    
                else:
                    print(f"   ❌ Erro {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    def test_template_with_minimal_payload(self, template_name):
        """Testar template com payload mínimo absoluto"""
        print(f"\n🧪 TESTE MINIMAL: {template_name}")
        
        phone_id = self.phone_ids[0]  # Use Phone 1
        to_number = '+5561982132603'
        
        # Payload absolutamente mínimo
        minimal_payload = {
            'messaging_product': 'whatsapp',
            'to': to_number,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': 'en'}
            }
        }
        
        url = f'https://graph.facebook.com/v22.0/{phone_id}/messages'
        
        print(f"📤 Payload: {json.dumps(minimal_payload, indent=2)}")
        
        try:
            response = requests.post(url, json=minimal_payload, headers=self.headers, timeout=30)
            
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', '')
                print(f"✅ SUCESSO! Message ID: {message_id}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def test_different_api_versions(self, template_name):
        """Testar template com diferentes versões da API"""
        print(f"\n🔄 TESTE VERSÕES API: {template_name}")
        
        phone_id = self.phone_ids[0]
        to_number = '+5561982132603'
        
        # Testar versões da API
        api_versions = ['v22.0', 'v21.0', 'v20.0', 'v19.0']
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to_number,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': 'en'}
            }
        }
        
        for version in api_versions:
            print(f"🔄 Testando API {version}")
            
            url = f'https://graph.facebook.com/{version}/{phone_id}/messages'
            
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get('messages', [{}])[0].get('id', '')
                    print(f"   ✅ {version} FUNCIONOU! Message ID: {message_id}")
                    return version
                else:
                    error_data = response.json() if response.content else {}
                    error_code = error_data.get('error', {}).get('code', 'N/A')
                    print(f"   ❌ {version} falhou: #{error_code}")
                    
            except Exception as e:
                print(f"   ❌ {version} exception: {e}")
        
        return None
    
    def test_bypass_methods(self, template_name):
        """Testar métodos de bypass técnico para erro #135000"""
        print(f"\n🔧 TESTE BYPASS: {template_name}")
        
        phone_id = self.phone_ids[0]
        to_number = '+5561982132603'
        
        # Testar headers especiais
        bypass_headers = [
            {'X-FB-Internal-Override': 'true'},
            {'X-FB-Template-Override': 'bypass'},
            {'X-Business-Use-Case-ID': self.business_account_id},
            {'X-FB-Force-Send': 'true'},
            {'User-Agent': 'WhatsAppBusinessAPI/1.0'},
            {'X-Requested-With': 'XMLHttpRequest'}
        ]
        
        base_payload = {
            'messaging_product': 'whatsapp',
            'to': to_number,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': 'en'}
            }
        }
        
        url = f'https://graph.facebook.com/v22.0/{phone_id}/messages'
        
        for bypass_header in bypass_headers:
            print(f"🔧 Testando header: {bypass_header}")
            
            # Merge headers
            test_headers = {**self.headers, **bypass_header}
            
            try:
                response = requests.post(url, json=base_payload, headers=test_headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get('messages', [{}])[0].get('id', '')
                    print(f"   ✅ BYPASS FUNCIONOU! Message ID: {message_id}")
                    print(f"   🔑 Header usado: {bypass_header}")
                    return bypass_header
                else:
                    error_data = response.json() if response.content else {}
                    error_code = error_data.get('error', {}).get('code', 'N/A')
                    print(f"   ❌ Bypass falhou: #{error_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        return None
    
    def run_complete_diagnosis(self):
        """Executar diagnóstico completo"""
        print("🚨 DIAGNÓSTICO COMPLETO - ERRO #135000")
        print("=" * 60)
        
        # 1. Check templates
        templates = self.check_template_status()
        
        # 2. Check phone permissions  
        self.check_phone_number_permissions()
        
        if templates:
            # Test first approved template
            test_template = templates[0]['name']
            
            # 3. Test minimal payload
            minimal_success = self.test_template_with_minimal_payload(test_template)
            
            if not minimal_success:
                # 4. Test different API versions
                working_version = self.test_different_api_versions(test_template)
                
                if not working_version:
                    # 5. Test bypass methods
                    bypass_method = self.test_bypass_methods(test_template)
                    
                    if bypass_method:
                        print(f"\n🎯 SOLUÇÃO ENCONTRADA: {bypass_method}")
                    else:
                        print("\n❌ NENHUM MÉTODO FUNCIONOU - Problema requer investigação Meta")
                else:
                    print(f"\n🎯 SOLUÇÃO: Use API version {working_version}")
            else:
                print(f"\n✅ Template {test_template} funciona com payload mínimo")

def main():
    diagnoser = Error135000RootCause()
    diagnoser.run_complete_diagnosis()

if __name__ == "__main__":
    main()