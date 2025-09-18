#!/usr/bin/env python3
"""
Descobrir configurações corretas e templates disponíveis
"""
import requests
import json
import os

def discover_real_config():
    """Descobrir configurações reais da conta"""
    
    # SEU token fornecido
    token = "EAAKrs5Jx6qgBPfeaK7WytbhiewOmUJFMWo0WrFyqpXngb2St5btTZAJY3MZAGcWvQ0y00rIs95m0PBdAkfa0q5ZAPsOjEhqGcB7FPxDCfyZAuai0IAqMTCkNtZCJA8h1zfZCNV4H6YEZCNbx6rZBvMyZCaNvl5sAPhH8Jq1rwvVXumOZA53OHvEqz8k5OrHIqUGZBDCwieOZBFtJOSxijuJHIJPmL2uSFktI4rfDJ51MSNOAywZDZD"
    
    # SEU phone number ID fornecido
    phone_id = "792231037306962"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 DESCOBRINDO CONFIGURAÇÕES REAIS")
    print("=" * 50)
    print(f"🔑 Token: {token[:30]}...")
    print(f"📱 Phone ID: {phone_id}")
    
    try:
        # 1. Verificar validade do token
        print("\n1️⃣ Verificando token...")
        me_url = "https://graph.facebook.com/v23.0/me"
        me_response = requests.get(me_url, headers=headers, timeout=10)
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            app_name = me_data.get('name', 'N/A')
            app_id = me_data.get('id', 'N/A')
            print(f"✅ Token válido! App: {app_name} (ID: {app_id})")
        else:
            print(f"❌ Token inválido: {me_response.status_code}")
            print(f"Erro: {me_response.text}")
            return None
        
        # 2. Descobrir Business Managers
        print("\n2️⃣ Descobrindo Business Managers...")
        bm_url = "https://graph.facebook.com/v23.0/me/businesses"
        bm_response = requests.get(bm_url, headers=headers, timeout=10)
        
        if bm_response.status_code == 200:
            bm_data = bm_response.json()
            businesses = bm_data.get('data', [])
            print(f"📊 {len(businesses)} Business Managers encontrados")
            
            for business in businesses:
                business_id = business['id']
                business_name = business.get('name', 'N/A')
                print(f"   📈 {business_name} (ID: {business_id})")
                
                # 3. Buscar templates no BM
                print(f"\n3️⃣ Buscando templates no BM {business_id}...")
                
                # Primeiro buscar WABAs
                waba_url = f"https://graph.facebook.com/v23.0/{business_id}?fields=owned_whatsapp_business_accounts"
                waba_response = requests.get(waba_url, headers=headers, timeout=10)
                
                if waba_response.status_code == 200:
                    waba_data = waba_response.json()
                    waba_accounts = waba_data.get('owned_whatsapp_business_accounts', {}).get('data', [])
                    
                    for waba in waba_accounts:
                        waba_id = waba['id']
                        print(f"   📞 WABA: {waba_id}")
                        
                        # Buscar templates
                        templates_url = f"https://graph.facebook.com/v23.0/{waba_id}/message_templates"
                        templates_response = requests.get(templates_url, headers=headers, timeout=10)
                        
                        if templates_response.status_code == 200:
                            templates_data = templates_response.json()
                            templates = templates_data.get('data', [])
                            
                            print(f"     📋 {len(templates)} templates encontrados:")
                            modelo_templates = []
                            
                            for template in templates:
                                name = template['name']
                                status = template.get('status', 'N/A')
                                language = template.get('language', 'N/A')
                                
                                print(f"       • {name} (Status: {status}, Lang: {language})")
                                
                                if name.startswith('modelo') and status == 'APPROVED':
                                    modelo_templates.append(name)
                            
                            if modelo_templates:
                                print(f"\n🎯 TEMPLATES 'modelo*' APROVADOS: {modelo_templates}")
                                
                                # Testar primeiro template válido
                                test_template = modelo_templates[0]
                                print(f"\n4️⃣ TESTANDO template {test_template}...")
                                return test_real_send(phone_id, token, test_template)
                            else:
                                print("⚠️ Nenhum template 'modelo*' aprovado encontrado")
                        else:
                            print(f"     ❌ Erro ao buscar templates: {templates_response.status_code}")
                else:
                    print(f"   ❌ Erro ao buscar WABAs: {waba_response.status_code}")
                    
        else:
            print(f"❌ Erro ao buscar Business Managers: {bm_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    return None

def test_real_send(phone_id, token, template_name):
    """Testar envio real com configurações descobertas"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Usar v23.0 já que v22.0 foi depreciado
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": "5561999114066",
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "en_US"
            }
        }
    }
    
    print(f"🚀 TESTANDO ENVIO REAL:")
    print(f"📱 Phone ID: {phone_id}")
    print(f"📋 Template: {template_name}")
    print(f"📞 Para: +55 61 99911-4066")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 MENSAGEM ENVIADA COM SUCESSO!")
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Salvar configurações corretas
            config = {
                'phone_id': phone_id,
                'token': token,
                'template': template_name,
                'api_version': 'v23.0'
            }
            
            with open('working_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✅ Configurações salvas em working_config.json")
            return config
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'N/A')
                error_code = error_data.get('error', {}).get('code', 'N/A')
                print(f"📝 Erro {error_code}: {error_msg}")
            except:
                print(f"📝 Resposta: {response.text}")
            
            return None
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return None

if __name__ == "__main__":
    print("🔍 DESCOBRINDO CONFIGURAÇÕES CORRETAS DO SEU WHATSAPP")
    print("=" * 60)
    
    config = discover_real_config()
    
    print("\n" + "=" * 60)
    if config:
        print("🎉 CONFIGURAÇÕES FUNCIONAIS ENCONTRADAS!")
        print(f"📱 Phone ID: {config['phone_id']}")
        print(f"📋 Template: {config['template']}")
        print(f"🔗 API: {config['api_version']}")
        print("📱 Mensagem enviada com sucesso!")
    else:
        print("⚠️ Não foi possível encontrar configurações funcionais")
        print("🔧 Verificar templates aprovados na sua conta WhatsApp")