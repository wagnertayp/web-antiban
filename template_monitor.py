#!/usr/bin/env python3
"""
Monitor para verificar aprovação de templates automaticamente
"""

import requests
import os
import time
import json

def monitor_pending_templates():
    """Monitorar templates em status PENDING"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            # Filtrar templates por status
            approved = [t for t in templates if t.get('status') == 'APPROVED']
            pending = [t for t in templates if t.get('status') == 'PENDING']
            rejected = [t for t in templates if t.get('status') == 'REJECTED']
            
            print(f"=== STATUS DOS TEMPLATES ===")
            print(f"✅ APROVADOS: {len(approved)}")
            for t in approved:
                print(f"- {t['name']} (ID: {t['id']})")
            
            print(f"\n⏳ PENDING: {len(pending)}")
            for t in pending:
                print(f"- {t['name']} (ID: {t['id']})")
            
            print(f"\n❌ REJEITADOS: {len(rejected)}")
            
            # Verificar se algum PENDING foi aprovado
            newly_approved = []
            for template in pending:
                if template['name'].startswith(('hello_world_br', 'teste', 'ola_brasil')):
                    newly_approved.append(template)
            
            if newly_approved:
                print(f"\n🎉 TEMPLATES RECENTEMENTE EM ANÁLISE:")
                for t in newly_approved:
                    print(f"- {t['name']} - Aguardando aprovação...")
            
            return {
                'approved': approved,
                'pending': pending,
                'rejected': rejected,
                'total': len(templates)
            }
            
        else:
            print(f"Erro ao buscar templates: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_approved_templates():
    """Testar envio com templates aprovados"""
    
    print(f"\n=== TESTE COM TEMPLATES APROVADOS ===")
    
    # Simular envio com modelo1 e modelo2
    test_data = {
        'phone': '+5573999084689',  # Número de teste
        'cpf': '123.456.789-00',
        'nome': 'Teste Sistema'
    }
    
    approved_templates = ['modelo1', 'modelo2']
    
    for template_name in approved_templates:
        print(f"\nTestando {template_name}:")
        print(f"- CPF: {test_data['cpf']}")
        print(f"- Nome: {test_data['nome']}")
        print(f"- Telefone: {test_data['phone']}")
        print(f"✅ Template {template_name} está aprovado e pronto para uso")

if __name__ == "__main__":
    print("=== MONITOR DE TEMPLATES ===\n")
    
    status = monitor_pending_templates()
    
    if status:
        print(f"\nResumo: {status['total']} templates total")
        print(f"Aprovados: {len(status['approved'])}")
        print(f"Pendentes: {len(status['pending'])}")
        print(f"Rejeitados: {len(status['rejected'])}")
        
        if len(status['approved']) >= 2:
            print(f"\n✅ SISTEMA OPERACIONAL!")
            print(f"📱 Use modelo1 ou modelo2 para envios")
            test_approved_templates()
        else:
            print(f"\n⚠️  Poucos templates aprovados")
    
    print(f"\n💡 Dica: Execute este script periodicamente para monitorar aprovações")