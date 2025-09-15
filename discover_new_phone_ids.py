#!/usr/bin/env python3
"""
Descobrir Phone Number IDs da nova Business Manager
Token: EAAZAPHnka8gYBPHlrKFZCTAv291bu3OXuGJRi225eIP6SQj5WqL2dPNcMFa5QPOt05HlHD9ZC0A0ZBUDer2tSpScL1umZBX9uxWcPNA6TygiFSPCSAJWMZBoV9agvXl5zWaUk1G5LE1r4rLyYFcetC5d0qx4ueYGeNPeyzvWULOCYRx1AcYzsW600pax2EToJYOy4qsnZBZC7XRplvqRChZAbht6WA4QpchnQMNc2CDDC0wZDZD
Números esperados: +1 804-210-0219 e +1 830-445-8877
"""

import requests
import json
import time

class PhoneIDDiscovery:
    def __init__(self):
        self.token = "EAAZAPHnka8gYBPHlrKFZCTAv291bu3OXuGJRi225eIP6SQj5WqL2dPNcMFa5QPOt05HlHD9ZC0A0ZBUDer2tSpScL1umZBX9uxWcPNA6TygiFSPCSAJWMZBoV9agvXl5zWaUk1G5LE1r4rLyYFcetC5d0qx4ueYGeNPeyzvWULOCYRx1AcYzsW600pax2EToJYOy4qsnZBZC7XRplvqRChZAbht6WA4QpchnQMNc2CDDC0wZDZD"
        self.expected_numbers = ["+18042100219", "+18304458877"]
        self.found_phone_ids = []
    
    def discover_business_accounts(self):
        """Descobrir todas as Business Accounts associadas"""
        print("🔍 Descobrindo Business Accounts...")
        
        # Método 1: Via user me
        url = "https://graph.facebook.com/v23.0/me"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('id')
            print(f"User ID: {user_id}")
            
            # Tentar buscar contas associadas
            return self._search_accounts_systematically(user_id)
        
        return []
    
    def _search_accounts_systematically(self, user_id):
        """Buscar contas sistematicamente"""
        possible_endpoints = [
            f"https://graph.facebook.com/v23.0/{user_id}/accounts",
            f"https://graph.facebook.com/v23.0/{user_id}/business_users",
            f"https://graph.facebook.com/v23.0/me/businesses",
            f"https://graph.facebook.com/v23.0/me/accounts"
        ]
        
        business_accounts = []
        
        for endpoint in possible_endpoints:
            try:
                response = requests.get(endpoint, headers={'Authorization': f'Bearer {self.token}'})
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        for item in data['data']:
                            if 'id' in item:
                                business_accounts.append(item['id'])
                                print(f"Found account: {item['id']}")
            except:
                continue
        
        return business_accounts
    
    def test_phone_id_patterns(self):
        """Testar padrões de Phone ID baseados nos números conhecidos"""
        print("🎯 Testando padrões de Phone ID...")
        
        # Padrões baseados nos números de telefone
        patterns = []
        
        # Padrão 1: Baseado no número 804-210-0219
        base_804 = "804210"
        for suffix in range(0, 1000000, 100000):  # 0, 100000, 200000, etc.
            patterns.append(f"{base_804}{suffix:06d}")
        
        # Padrão 2: Baseado no número 830-445-8877  
        base_830 = "830445"
        for suffix in range(0, 1000000, 100000):
            patterns.append(f"{base_830}{suffix:06d}")
        
        # Padrão 3: IDs de 15 dígitos comuns do WhatsApp
        common_prefixes = ["1", "10", "100", "108", "180", "183"]
        for prefix in common_prefixes:
            for i in range(5):
                pattern = f"{prefix}{'0' * (15-len(prefix)-1)}{i}"
                patterns.append(pattern)
        
        # Testar até 20 padrões para não sobrecarregar
        for pattern in patterns[:20]:
            if self._test_phone_id(pattern):
                break
            time.sleep(0.5)  # Rate limiting
    
    def _test_phone_id(self, phone_id):
        """Testar se um Phone ID é válido"""
        url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Enviar mensagem de teste
        payload = {
            "messaging_product": "whatsapp",
            "to": "5561982132603",
            "type": "text",
            "text": {"body": "Test discovery"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if response.status_code == 200 and 'messages' in data:
                message_id = data['messages'][0]['id']
                print(f"✅ PHONE ID ENCONTRADO: {phone_id}")
                print(f"   Message ID: {message_id}")
                self.found_phone_ids.append(phone_id)
                
                # Verificar detalhes do phone
                self._get_phone_details(phone_id)
                return True
            else:
                error = data.get('error', {})
                error_code = error.get('code')
                
                # Log apenas erros interessantes
                if error_code not in [100, 803, 400]:
                    print(f"❌ {phone_id}: Error {error_code}")
                
        except Exception as e:
            pass  # Ignorar erros de conexão
        
        return False
    
    def _get_phone_details(self, phone_id):
        """Obter detalhes do Phone Number"""
        url = f"https://graph.facebook.com/v23.0/{phone_id}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   Número: {data.get('display_phone_number', 'N/A')}")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Verificado: {data.get('verified_name', 'N/A')}")
        except:
            pass
    
    def brute_force_discovery(self):
        """Descoberta por força bruta (últimos dígitos)"""
        print("💪 Descoberta por força bruta...")
        
        # Baseado nos números conhecidos, tentar variações
        known_patterns = [
            # Padrões baseados em números anteriores que funcionaram
            "764229176768157",
            "708355979030805", 
            "687372631129372",
            "638079459399067"
        ]
        
        for base_pattern in known_patterns:
            # Modificar últimos dígitos
            base = base_pattern[:-3]  # Remove últimos 3 dígitos
            for i in range(1000):  # Testa 000-999
                test_id = f"{base}{i:03d}"
                if self._test_phone_id(test_id):
                    break
                if i % 100 == 0:  # Progress indicator
                    print(f"   Testando: {base}xxx")
    
    def run_discovery(self):
        """Executar descoberta completa"""
        print("🚀 DESCOBERTA DE PHONE NUMBER IDs - NOVA BM")
        print("=" * 50)
        
        # Método 1: Descobrir Business Accounts
        self.discover_business_accounts()
        
        # Método 2: Testar padrões baseados nos números
        self.test_phone_id_patterns()
        
        # Método 3: Força bruta se necessário
        if not self.found_phone_ids:
            self.brute_force_discovery()
        
        # Resultados
        print("\n📋 RESULTADOS:")
        if self.found_phone_ids:
            print("✅ Phone IDs encontrados:")
            for phone_id in self.found_phone_ids:
                print(f"   - {phone_id}")
        else:
            print("❌ Nenhum Phone ID encontrado")
            print("   Token pode não ter acesso aos números cadastrados")
        
        return self.found_phone_ids

def main():
    discovery = PhoneIDDiscovery()
    found_ids = discovery.run_discovery()
    
    if found_ids:
        print(f"\n🎯 SUCESSO! Encontrados {len(found_ids)} Phone ID(s)")
        
        # Testar template em cada Phone ID encontrado
        for phone_id in found_ids:
            print(f"\n🧪 Testando templates no Phone ID: {phone_id}")
            # Aqui podemos testar templates se necessário
    else:
        print("\n💀 Descoberta falhou - Token não tem acesso aos Phone Numbers")

if __name__ == "__main__":
    main()