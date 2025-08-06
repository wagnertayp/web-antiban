#!/usr/bin/env python3
"""
Descobrir TODOS os templates aprovados em todas as contas associadas
"""

import requests
import os
import json

def discover_all_business_accounts():
    """Descobrir todas as Business Accounts associadas ao token"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    endpoints_to_try = [
        'https://graph.facebook.com/v23.0/me',
        'https://graph.facebook.com/v23.0/me/accounts',
        'https://graph.facebook.com/v23.0/me/businesses',
        'https://graph.facebook.com/v23.0/me/adaccounts'
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    all_accounts = []
    
    for endpoint in endpoints_to_try:
        print(f"Testando endpoint: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resposta: {data}")
                
                # Extrair IDs de contas
                if 'data' in data:
                    for item in data['data']:
                        if 'id' in item:
                            all_accounts.append(item['id'])
                elif 'id' in data:
                    all_accounts.append(data['id'])
                    
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Erro: {e}")
    
    # Tentar alguns Business Manager IDs conhecidos
    known_bm_ids = [
        '746006914691827',  # Atual
        '2499594917061799', # Anterior que tinha template
        '673500515497433',  # Outro conhecido
        '1289588222582398'  # Descoberto anteriormente
    ]
    
    all_accounts.extend(known_bm_ids)
    return list(set(all_accounts))  # Remover duplicatas

def search_templates_all_accounts():
    """Buscar templates em todas as contas possíveis"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    accounts = discover_all_business_accounts()
    
    print(f"=== BUSCANDO TEMPLATES EM {len(accounts)} CONTAS ===\n")
    
    all_approved = []
    
    for account_id in accounts:
        print(f"Verificando conta: {account_id}")
        
        url = f'https://graph.facebook.com/v23.0/{account_id}/message_templates'
        params = {
            'fields': 'id,name,status,category,language,components,quality_score'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                approved = [t for t in templates if t.get('status') == 'APPROVED']
                pending = [t for t in templates if t.get('status') == 'PENDING']
                
                if approved:
                    print(f"✅ {len(approved)} APROVADOS encontrados!")
                    for template in approved:
                        print(f"   - {template['name']} (ID: {template['id']})")
                        all_approved.append({
                            'account_id': account_id,
                            'template': template
                        })
                        
                        # Salvar estrutura
                        filename = f"approved_{template['name']}_{account_id}.json"
                        with open(filename, 'w') as f:
                            json.dump(template, f, indent=2)
                        print(f"     💾 Salvo: {filename}")
                
                if pending:
                    print(f"⏳ {len(pending)} PENDING: {[t['name'] for t in pending]}")
                
                if not approved and not pending:
                    print(f"❌ Nenhum template encontrado")
                    
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Erro {response.status_code}: {error_data.get('error', {}).get('message', 'Desconhecido')}")
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print()  # Linha em branco
    
    return all_approved

def replicate_found_approved():
    """Replicar templates aprovados encontrados"""
    
    approved_templates = search_templates_all_accounts()
    
    if not approved_templates:
        print("❌ Nenhum template aprovado encontrado em nenhuma conta")
        return False
    
    print(f"=== REPLICANDO {len(approved_templates)} TEMPLATE(S) APROVADO(S) ===\n")
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    current_bm = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{current_bm}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    for approved_item in approved_templates:
        template = approved_item['template']
        source_account = approved_item['account_id']
        
        print(f"Replicando: {template['name']} (de conta {source_account})")
        
        # Criar réplica exata
        replica = {
            'name': f"copy_{template['name']}_{int(time.time())}",
            'language': template['language'],
            'category': template['category'],
            'components': template['components']
        }
        
        try:
            response = requests.post(url, json=replica, headers=headers, timeout=15)
            result = response.json()
            
            if response.status_code in [200, 201]:
                status = result.get('status', 'UNKNOWN')
                template_id = result.get('id', 'N/A')
                
                print(f"✅ Réplica criada: {replica['name']}")
                print(f"   Status: {status}")
                print(f"   ID: {template_id}")
                
                if status == 'APPROVED':
                    print(f"🎉 APROVADO INSTANTANEAMENTE!")
                    return True
                    
            else:
                error = result.get('error', {})
                print(f"❌ Falhou: {error.get('message', 'Desconhecido')}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        print()
    
    return False

if __name__ == "__main__":
    print("=== DESCOBRINDO TODOS OS TEMPLATES APROVADOS ===\n")
    
    success = replicate_found_approved()
    
    if success:
        print("🎉 SUCESSO! Template aprovado replicado com sucesso!")
    else:
        print("❌ Nenhuma replicação bem-sucedida")