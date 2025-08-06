#!/usr/bin/env python3
"""
Analisar templates aprovados para replicar estrutura exata
"""

import requests
import os
import json
import time

def analyze_approved_structure():
    """Analisar estrutura EXATA dos templates aprovados"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    params = {
        'fields': 'id,name,status,category,language,components,quality_score,rejected_reason,previous_category'
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            # Separar por status
            approved = [t for t in templates if t.get('status') == 'APPROVED']
            pending = [t for t in templates if t.get('status') == 'PENDING']
            rejected = [t for t in templates if t.get('status') == 'REJECTED']
            
            print("=== ANÁLISE DETALHADA DOS TEMPLATES ===\n")
            
            # Analisar templates aprovados
            print("✅ TEMPLATES APROVADOS:")
            for template in approved:
                print(f"\n--- {template['name']} ---")
                print(f"ID: {template['id']}")
                print(f"Status: {template['status']}")
                print(f"Categoria: {template['category']}")
                print(f"Idioma: {template['language']}")
                print(f"Componentes: {len(template.get('components', []))}")
                
                # Analisar componentes detalhadamente
                for i, comp in enumerate(template.get('components', [])):
                    print(f"  Componente {i+1}: {comp.get('type', 'N/A')}")
                    if 'text' in comp:
                        print(f"    Texto: {comp['text'][:50]}...")
                    if 'buttons' in comp:
                        print(f"    Botões: {len(comp['buttons'])}")
                
                # Salvar estrutura completa
                with open(f'approved_{template["name"]}.json', 'w') as f:
                    json.dump(template, f, indent=2)
                
                print(f"💾 Estrutura salva em: approved_{template['name']}.json")
            
            # Analisar templates pending para comparação
            print(f"\n⏳ TEMPLATES PENDING ({len(pending)}):")
            for template in pending:
                print(f"- {template['name']} (Categoria: {template['category']}, Idioma: {template['language']})")
            
            print(f"\n❌ TEMPLATES REJEITADOS ({len(rejected)}):")
            for template in rejected[:3]:  # Só os primeiros 3
                print(f"- {template['name']} (Motivo: {template.get('rejected_reason', 'N/A')})")
            
            return approved, pending, rejected
            
        else:
            print(f"Erro ao buscar templates: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"Erro: {e}")
        return None, None, None

def replicate_approved_structure():
    """Replicar EXATAMENTE a estrutura dos templates aprovados"""
    
    # Carregar estrutura do template aprovado
    try:
        with open('approved_modelo1.json', 'r') as f:
            modelo1_structure = json.load(f)
    except:
        print("Erro: Execute analyze_approved_structure() primeiro")
        return False
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    timestamp = str(int(time.time()))
    
    # Criar template IDÊNTICO ao aprovado, só mudando nome e texto
    new_template = {
        'name': f'replica_{timestamp}',
        'language': modelo1_structure['language'],
        'category': modelo1_structure['category'],
        'components': []
    }
    
    # Copiar componentes EXATAMENTE
    for comp in modelo1_structure['components']:
        new_comp = comp.copy()
        
        # Modificar apenas o texto minimamente
        if comp['type'] == 'BODY' and 'text' in comp:
            # Manter estrutura exata, mudar só palavras específicas
            original_text = comp['text']
            new_text = original_text.replace('Damião Alves', 'José Silva')
            new_text = new_text.replace('5º Ofício', '6º Ofício')
            new_comp['text'] = new_text
        
        new_template['components'].append(new_comp)
    
    print(f"=== REPLICANDO ESTRUTURA APROVADA ===")
    print(f"Template original: modelo1")
    print(f"Nova réplica: {new_template['name']}")
    print(f"Categoria: {new_template['category']}")
    print(f"Idioma: {new_template['language']}")
    print(f"Componentes: {len(new_template['components'])}")
    
    try:
        response = requests.post(url, json=new_template, headers=headers, timeout=15)
        result = response.json()
        
        if response.status_code in [200, 201]:
            template_id = result.get('id', 'N/A')
            status = result.get('status', 'UNKNOWN')
            
            print(f"\n✅ RÉPLICA CRIADA!")
            print(f"ID: {template_id}")
            print(f"Status: {status}")
            
            if status == 'APPROVED':
                print(f"🎉 APROVADO INSTANTANEAMENTE!")
                print(f"🔥 ESTRUTURA FUNCIONA!")
                return True
            elif status == 'PENDING':
                print(f"⏳ EM ANÁLISE - Aguardar 5 minutos")
                return True
            else:
                print(f"❓ Status inesperado: {status}")
                return False
                
        else:
            error = result.get('error', {})
            print(f"\n❌ RÉPLICA FALHOU:")
            print(f"Erro: {error.get('message', 'Desconhecido')}")
            return False
            
    except Exception as e:
        print(f"Erro ao criar réplica: {e}")
        return False

if __name__ == "__main__":
    print("=== ANÁLISE E REPLICAÇÃO DE TEMPLATES APROVADOS ===\n")
    
    # Analisar estrutura dos aprovados
    approved, pending, rejected = analyze_approved_structure()
    
    if approved:
        print(f"\n🔍 {len(approved)} template(s) aprovado(s) analisado(s)")
        
        # Tentar replicar estrutura
        print(f"\n🔄 Tentando replicar estrutura...")
        success = replicate_approved_structure()
        
        if success:
            print(f"\n🎉 SUCESSO! Estrutura replicada com sucesso")
        else:
            print(f"\n❌ Falha na replicação")
    else:
        print("❌ Nenhum template aprovado encontrado para análise")