#!/usr/bin/env python3
"""
Criar templates de MARKETING com linguagem leve e promocional
Templates de marketing são mais fáceis de aprovar
"""

import requests
import json
import os
import time

def create_marketing_templates():
    """Criar templates de MARKETING com linguagem promocional"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    if not access_token:
        print("ERROR: Token não encontrado")
        return []
    
    business_account_id = '746006914691827'
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Templates MARKETING com linguagem promocional e comercial
    marketing_templates = [
        {
            "name": "oferta_especial",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🎉 Olá {{1}}! Temos uma oferta especial para você! Aproveite nossa promoção exclusiva para {{2}}. Não perca essa oportunidade única!"
                }
            ]
        },
        {
            "name": "promocao_limitada",
            "language": "pt_BR", 
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "⏰ {{1}}, nossa promoção especial está acabando! Garante já o seu {{2}} com desconto exclusivo. Oferta por tempo limitado!"
                }
            ]
        },
        {
            "name": "novidade_produto",
            "language": "pt_BR",
            "category": "MARKETING", 
            "components": [
                {
                    "type": "BODY",
                    "text": "✨ Novidade para você, {{1}}! Acabou de chegar: {{2}}. Seja um dos primeiros a aproveitar. Confira já!"
                }
            ]
        },
        {
            "name": "convite_evento",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🎪 {{1}}, você está convidado para nosso evento especial! Data: {{2}}. Vagas limitadas. Reserve já a sua!"
                }
            ]
        },
        {
            "name": "special_offer",
            "language": "en",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🎁 Hi {{1}}! We have a special offer just for you! Get your {{2}} with exclusive discount. Limited time only!"
                }
            ]
        },
        {
            "name": "flash_sale",
            "language": "en",
            "category": "MARKETING", 
            "components": [
                {
                    "type": "BODY",
                    "text": "⚡ {{1}}, Flash Sale Alert! Save big on {{2}} today only. Don't miss out on this amazing deal!"
                }
            ]
        },
        {
            "name": "new_arrival",
            "language": "en",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🆕 Hey {{1}}! Check out our newest arrival: {{2}}. Be the first to get yours. Shop now!"
                }
            ]
        },
        {
            "name": "evento_exclusivo",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🌟 {{1}}, você foi selecionado para nosso evento VIP! Local: {{2}}. Entrada gratuita para convidados especiais!"
                }
            ]
        },
        {
            "name": "desconto_personalizado",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "💰 Olá {{1}}! Preparamos um desconto especial para você em {{2}}. Código exclusivo no final da mensagem!"
                }
            ]
        },
        {
            "name": "lancamento_produto",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "🚀 {{1}}, grande lançamento! Nosso novo {{2}} chegou com tudo. Seja um dos primeiros a experimentar!"
                }
            ]
        }
    ]
    
    approved = []
    
    for template in marketing_templates:
        print(f"\nCriando template MARKETING: {template['name']}")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=15)
            result = response.json()
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                template_status = result.get('status', 'UNKNOWN')
                print(f"✅ CRIADO: {template['name']} (ID: {template_id}, Status: {template_status})")
                approved.append({
                    'name': template['name'],
                    'id': template_id,
                    'status': template_status,
                    'language': template['language']
                })
            else:
                error = result.get('error', {})
                error_msg = error.get('message', 'Erro desconhecido')
                print(f"❌ REJEITADO: {error_msg}")
                
                # Log detalhado do erro
                if 'error_user_msg' in error:
                    print(f"   Detalhes: {error['error_user_msg']}")
            
            time.sleep(1)  # Pausa menor para marketing
            
        except Exception as e:
            print(f"ERRO: {e}")
    
    return approved

def create_simple_marketing():
    """Criar templates de marketing super simples"""
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    business_account_id = '746006914691827'
    
    url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Templates super simples de marketing
    simple_marketing = [
        {
            "name": "oi_promocao",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "Oi {{1}}! Promoção especial para você: {{2}}!"
                }
            ]
        },
        {
            "name": "oferta_hoje",
            "language": "pt_BR",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "{{1}}, oferta de hoje: {{2}}. Aproveite!"
                }
            ]
        },
        {
            "name": "sale_today",
            "language": "en",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "Hi {{1}}! Today's sale: {{2}}. Get yours now!"
                }
            ]
        }
    ]
    
    approved = []
    
    for template in simple_marketing:
        print(f"\nCriando MARKETING simples: {template['name']}")
        
        try:
            response = requests.post(url, json=template, headers=headers, timeout=10)
            result = response.json()
            
            if response.status_code in [200, 201]:
                template_id = result.get('id', 'N/A')
                template_status = result.get('status', 'UNKNOWN')
                print(f"✅ SIMPLES CRIADO: {template['name']} ({template_status})")
                approved.append(template['name'])
            else:
                error = result.get('error', {})
                print(f"❌ Simples rejeitado: {error.get('message', 'Erro')}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro simples: {e}")
    
    return approved

if __name__ == "__main__":
    print("=== CRIAÇÃO DE TEMPLATES MARKETING ===\n")
    
    print("1. Criando templates marketing promocionais...")
    marketing_approved = create_marketing_templates()
    
    print(f"\n2. Criando templates marketing simples...")
    simple_approved = create_simple_marketing()
    
    print(f"\n=== RESULTADO FINAL ===")
    total_marketing = len(marketing_approved) + len(simple_approved)
    print(f"Templates MARKETING criados: {total_marketing}")
    
    if marketing_approved:
        print("Templates marketing promocionais:")
        for t in marketing_approved:
            print(f"- {t['name']} ({t['language']}) - Status: {t['status']}")
    
    if simple_approved:
        print("Templates marketing simples:")
        for t in simple_approved:
            print(f"- {t}")
    
    if total_marketing == 0:
        print("❌ NENHUM TEMPLATE MARKETING CRIADO")
        print("Possíveis problemas:")
        print("- Rate limit ainda ativo")
        print("- Conta com muitos templates rejeitados")
        print("- Necessário aguardar cooldown")
    else:
        print(f"✅ {total_marketing} templates MARKETING em processo!")
        print("💡 Templates MARKETING têm aprovação mais rápida que UTILITY")
        print("📱 Aguarde alguns minutos para status de aprovação")