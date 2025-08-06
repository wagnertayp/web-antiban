#!/usr/bin/env python3
"""
Encontrar templates modelo1 e modelo2 aprovados em todas as páginas
"""

import requests
import os
import json

def find_all_approved_templates():
    """Buscar todos os templates aprovados em todas as páginas"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    base_url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    params = {
        'fields': 'id,name,status,category,language,components,quality_score',
        'limit': 100
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    all_templates = []
    next_url = None
    page = 1
    
    print("=== BUSCANDO TODOS OS TEMPLATES ===\n")
    
    while True:
        if next_url:
            url = next_url
        else:
            url = base_url
        
        print(f"Página {page}...")
        
        try:
            if next_url:
                response = requests.get(url, headers=headers, timeout=15)
            else:
                response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                print(f"  {len(templates)} templates encontrados")
                all_templates.extend(templates)
                
                # Verificar se há próxima página
                paging = data.get('paging', {})
                next_url = paging.get('next')
                
                if not next_url:
                    print("  Última página")
                    break
                    
                page += 1
                
            else:
                print(f"Erro: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Erro: {e}")
            break
    
    print(f"\nTotal: {len(all_templates)} templates\n")
    
    # Filtrar por status
    approved = [t for t in all_templates if t.get('status') == 'APPROVED']
    pending = [t for t in all_templates if t.get('status') == 'PENDING']
    rejected = [t for t in all_templates if t.get('status') == 'REJECTED']
    
    print(f"=== RESUMO POR STATUS ===")
    print(f"✅ APROVADOS: {len(approved)}")
    print(f"⏳ PENDING: {len(pending)}")
    print(f"❌ REJEITADOS: {len(rejected)}")
    
    # Procurar especificamente modelo1 e modelo2
    modelo1 = next((t for t in all_templates if t['name'] == 'modelo1'), None)
    modelo2 = next((t for t in all_templates if t['name'] == 'modelo2'), None)
    
    print(f"\n=== TEMPLATES ESPECÍFICOS ===")
    
    if modelo1:
        print(f"modelo1: {modelo1['status']} (ID: {modelo1['id']})")
        if modelo1['status'] == 'APPROVED':
            print("🎉 MODELO1 APROVADO!")
    else:
        print("modelo1: NÃO ENCONTRADO")
    
    if modelo2:
        print(f"modelo2: {modelo2['status']} (ID: {modelo2['id']})")
        if modelo2['status'] == 'APPROVED':
            print("🎉 MODELO2 APROVADO!")
    else:
        print("modelo2: NÃO ENCONTRADO")
    
    print(f"\n=== TODOS OS TEMPLATES APROVADOS ===")
    
    if approved:
        for template in approved:
            print(f"✅ {template['name']}")
            print(f"   ID: {template['id']}")
            print(f"   Categoria: {template['category']}")
            print(f"   Idioma: {template['language']}")
            print(f"   Componentes: {len(template.get('components', []))}")
            
            # Salvar estrutura
            filename = f'approved_{template["name"]}_final.json'
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"   💾 Salvo: {filename}")
            print()
    else:
        print("Nenhum template aprovado encontrado")
    
    return all_templates, approved, modelo1, modelo2

def analyze_approved_structure(approved_templates):
    """Analisar estrutura detalhada dos templates aprovados"""
    
    if not approved_templates:
        print("❌ Nenhum template aprovado para analisar")
        return
    
    print("=== ANÁLISE DETALHADA DOS APROVADOS ===\n")
    
    for template in approved_templates:
        print(f"--- {template['name'].upper()} ---")
        print(f"Estrutura JSON completa:")
        print(json.dumps(template, indent=2, ensure_ascii=False))
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("=== BUSCA COMPLETA POR TEMPLATES APROVADOS ===\n")
    
    all_templates, approved, modelo1, modelo2 = find_all_approved_templates()
    
    if approved:
        print(f"✅ ENCONTRADOS {len(approved)} TEMPLATE(S) APROVADO(S)!")
        
        # Analisar estrutura detalhada
        analyze_approved_structure(approved)
        
        if modelo1 and modelo1['status'] == 'APPROVED':
            print("🎯 MODELO1 CONFIRMADO APROVADO")
        
        if modelo2 and modelo2['status'] == 'APPROVED':
            print("🎯 MODELO2 CONFIRMADO APROVADO")
            
        print("\n💡 Agora posso replicar a estrutura exata!")
        
    else:
        print("❌ Nenhum template aprovado encontrado")
        print("🔍 Verificar se estão em outra conta ou foram removidos")