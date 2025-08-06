#!/usr/bin/env python3
"""
Descobrir Business Manager com templates aprovados e replicar estrutura exata
"""

import requests
import os
import json
import time

def discover_business_manager_with_templates():
    """Descobrir Business Manager que contém os templates aprovados"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    
    # Lista de Business Manager IDs conhecidos + tentativa de auto-descoberta
    potential_bm_ids = [
        '746006914691827',  # Atual
        '2499594917061799', # Anterior com templates
        '673500515497433',  # Conhecido
        '1289588222582398', # Descoberto antes
        # Auto-descobrir através do phone number
    ]
    
    # Tentar auto-descobrir Business Manager ID
    try:
        # Usar endpoint do phone number para descobrir BM
        phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '674928665709899')
        phone_url = f'https://graph.facebook.com/v23.0/{phone_id}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(phone_url, headers=headers, timeout=10)
        if response.status_code == 200:
            phone_data = response.json()
            if 'whatsapp_business_account_id' in phone_data:
                discovered_bm = phone_data['whatsapp_business_account_id']
                potential_bm_ids.insert(0, discovered_bm)  # Adicionar no início
                print(f"✅ Auto-descoberto BM ID: {discovered_bm}")
    except:
        pass
    
    print("=== BUSCANDO TEMPLATES APROVADOS ===\n")
    
    for bm_id in potential_bm_ids:
        print(f"Verificando BM: {bm_id}")
        
        url = f'https://graph.facebook.com/v23.0/{bm_id}/message_templates'
        params = {
            'fields': 'id,name,status,category,language,components,quality_score'
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                # Procurar especificamente modelo1 e modelo2
                modelo1 = next((t for t in templates if t['name'] == 'modelo1'), None)
                modelo2 = next((t for t in templates if t['name'] == 'modelo2'), None)
                
                approved_templates = [t for t in templates if t.get('status') == 'APPROVED']
                
                if modelo1 or modelo2 or approved_templates:
                    print(f"✅ ENCONTRADOS EM {bm_id}:")
                    
                    if modelo1:
                        print(f"   modelo1: {modelo1['status']} (ID: {modelo1['id']})")
                    if modelo2:
                        print(f"   modelo2: {modelo2['status']} (ID: {modelo2['id']})")
                    
                    if approved_templates:
                        print(f"   {len(approved_templates)} aprovados total")
                        for t in approved_templates:
                            print(f"     - {t['name']}: {t['status']}")
                    
                    return bm_id, templates
                else:
                    print(f"   ❌ Nenhum template aprovado")
                    
            else:
                error_data = response.json() if response.content else {}
                print(f"   ❌ Erro {response.status_code}: {error_data.get('error', {}).get('message', 'Desconhecido')}")
                
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}")
        
        time.sleep(1)  # Evitar rate limits
    
    return None, []

def analyze_approved_template_structure(bm_id, templates):
    """Analisar estrutura exata dos templates aprovados"""
    
    approved = [t for t in templates if t.get('status') == 'APPROVED']
    
    if not approved:
        print("❌ Nenhum template aprovado para analisar")
        return []
    
    print(f"\n=== ANALISANDO {len(approved)} TEMPLATE(S) APROVADO(S) ===\n")
    
    structures = []
    
    for template in approved:
        print(f"--- {template['name'].upper()} ---")
        print(f"Business Manager: {bm_id}")
        print(f"ID: {template['id']}")
        print(f"Status: {template['status']}")
        print(f"Categoria: {template['category']}")
        print(f"Idioma: {template['language']}")
        
        # Analisar componentes em detalhes
        print(f"Componentes ({len(template.get('components', []))}):")
        for i, comp in enumerate(template.get('components', [])):
            print(f"  [{i}] {comp.get('type')}")
            if 'text' in comp:
                print(f"      📝 Texto: {comp['text'][:100]}...")
            if 'format' in comp:
                print(f"      🎨 Formato: {comp['format']}")
            if 'buttons' in comp:
                print(f"      🔘 Botões: {len(comp['buttons'])}")
                for j, btn in enumerate(comp['buttons']):
                    print(f"         [{j}] {btn.get('type')}: {btn.get('text', 'N/A')}")
                    if 'url' in btn:
                        print(f"             URL: {btn['url']}")
        
        # Salvar estrutura completa
        filename = f'approved_{template["name"]}_bm_{bm_id}.json'
        with open(filename, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"💾 Estrutura salva: {filename}")
        
        structures.append(template)
        print("\n" + "="*50 + "\n")
    
    return structures

def replicate_exact_structure(approved_structures, target_bm_id):
    """Replicar estrutura EXATA dos templates aprovados"""
    
    if not approved_structures:
        print("❌ Nenhuma estrutura para replicar")
        return False
    
    print(f"=== REPLICANDO NO BM {target_bm_id} ===\n")
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    url = f'https://graph.facebook.com/v23.0/{target_bm_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    timestamp = str(int(time.time()))
    success_count = 0
    
    for template in approved_structures:
        print(f"Replicando: {template['name']}")
        
        # Criar payload IDÊNTICO
        replica_payload = {
            'name': f"exact_{template['name']}_{timestamp}",
            'language': template['language'],
            'category': template['category'],
            'components': template['components']  # Cópia byte-a-byte
        }
        
        print(f"Nome: {replica_payload['name']}")
        print(f"Estrutura: {len(replica_payload['components'])} componentes")
        
        try:
            response = requests.post(url, json=replica_payload, headers=headers, timeout=15)
            result = response.json()
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                status = result.get('status', 'UNKNOWN')
                
                print(f"✅ Criado: {template_id}")
                print(f"Status: {status}")
                
                if status == 'APPROVED':
                    print(f"🎉 APROVADO INSTANTANEAMENTE!")
                    success_count += 1
                elif status == 'PENDING':
                    print(f"⏳ Em análise - estrutura correta")
                    success_count += 1
                else:
                    print(f"❓ Status inesperado: {status}")
                    
            else:
                error = result.get('error', {})
                print(f"❌ Falhou:")
                print(f"   Código: {error.get('code', 'N/A')}")
                print(f"   Mensagem: {error.get('message', 'Desconhecido')}")
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print("\n" + "-"*40 + "\n")
        time.sleep(2)
    
    return success_count > 0

if __name__ == "__main__":
    print("=== DESCOBERTA E REPLICAÇÃO DE TEMPLATES APROVADOS ===\n")
    
    # Descobrir BM com templates aprovados
    source_bm, all_templates = discover_business_manager_with_templates()
    
    if not source_bm:
        print("❌ Nenhum Business Manager com templates aprovados encontrado")
        exit(1)
    
    # Analisar estrutura dos templates aprovados
    approved_structures = analyze_approved_template_structure(source_bm, all_templates)
    
    if not approved_structures:
        print("❌ Nenhuma estrutura aprovada para analisar")
        exit(1)
    
    # Replicar para BM atual
    current_bm = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '746006914691827')
    
    if source_bm != current_bm:
        print(f"Replicando de {source_bm} para {current_bm}")
        success = replicate_exact_structure(approved_structures, current_bm)
        
        if success:
            print("🎉 REPLICAÇÃO BEM-SUCEDIDA!")
        else:
            print("❌ Replicação falhou")
    else:
        print("✅ Templates já estão no BM atual")
        print("🔍 Verificar se funcionam sem erro #135000")