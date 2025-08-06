#!/usr/bin/env python3
"""
ENVIO ULTRA-RÁPIDO DE 17K LEADS - Sistema com recuperação automática
Velocidade máxima + Status em tempo real + Auto-recovery
"""

import os
import sys
import time
import json
from mega_batch_simple import MegaBatchSender

# Token atualizado
TOKEN = "EAAHUCvWVsdgBPLLcZCYCfrKPWMUZBRHCstJhmuAZBNLUB1tCrLeXshgqH7B5ylSmlkKHB2I934AW6rHnzOODlpcSRwixUZCx5katC9wZAhwE6M2GjFnGN2V0ZAjZB9eONmyY6A0LWKaCz2uyyYnIQpl5Ddvw3BVV0cWXBlekkjzKofDraA6ZCEPqCjCUOUSYkVolUc7BMtHti70Qem02Wtw5IwDMEnLCkAYZCZBoUGaLGDg1PuNNkZD"

# Phone Numbers da BM 2089992404820473 (20 números ativos)
PHONE_NUMBERS = [
    '725492557312328', '800312496489716', '776788602173980', '774576132396207',
    '764495823408049', '764138826774184', '749599158230143', '747868138404614',
    '746367015221228', '736306482898341', '732911983238956', '728240807037686',
    '721222711076869', '718291801369739', '712294161968633', '706148559252459',
    '698088016726677', '674341985771514', '672331669304211', '670736396133662'
]

# Templates aprovados da BM 2089992404820473 (UTILITY - SEM AUTHENTICATION)
TEMPLATES = [
    'modelo21', 'ricardo_template_1753485590_b501867c', 'ricardo_template_1753485474_512444ac',
    'ricardo_template_1753485563_5882b9ba', 'ricardo_template_1753487895_cbe4d528',
    'ricardo_template_1753485866_2620345a', 'ricardo_template_1753485422_108ba28d',
    'ricardo_template_1753487909_d79bcb95', 'ricardo_template_1753487687_5860ab23',
    'ricardo_template_1753485525_d3a7f18d', 'ricardo_template_1753487879_89f32594'
]

def check_recovery_state():
    """Verifica se existe estado de recuperação"""
    try:
        if os.path.exists('recovery_state.txt'):
            with open('recovery_state.txt', 'r') as f:
                position = int(f.read().strip())
            print(f"🔄 ESTADO DE RECUPERAÇÃO ENCONTRADO: Retomando do lead {position}")
            return position
    except:
        pass
    return 0

def save_leads_backup(leads):
    """Salva backup dos leads para recuperação"""
    try:
        with open('leads_backup.json', 'w') as f:
            json.dump(leads, f)
        print("💾 Backup dos leads salvo")
    except Exception as e:
        print(f"⚠️ Erro ao salvar backup: {e}")

def load_leads_backup():
    """Carrega backup dos leads"""
    try:
        if os.path.exists('leads_backup.json'):
            with open('leads_backup.json', 'r') as f:
                leads = json.load(f)
            print(f"📋 Backup carregado: {len(leads)} leads")
            return leads
    except Exception as e:
        print(f"⚠️ Erro ao carregar backup: {e}")
    return None

def process_17k_leads_ultra_fast(leads_data):
    """
    Processa 17K leads com velocidade máxima e recuperação automática
    """
    print("🚀 SISTEMA ULTRA-RÁPIDO INICIADO")
    print(f"📱 Token: {TOKEN[:30]}...")
    print(f"📞 Phone Numbers: {len(PHONE_NUMBERS)} ativos")
    print(f"📝 Templates: {len(TEMPLATES)} aprovados")
    print("💥 Velocidade: MÁXIMA (1000+ msg/sec)")
    print("🔄 Sistema anti-travamento: ATIVO")
    print("=" * 60)
    
    # Parse leads data
    leads = []
    for line in leads_data.strip().split('\n'):
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) >= 3:
                leads.append({
                    'numero': parts[0].strip(),
                    'nome': parts[1].strip(),
                    'cpf': parts[2].strip()
                })
    
    print(f"📋 LEADS PROCESSADOS: {len(leads)} válidos")
    
    # Salvar backup
    save_leads_backup(leads)
    
    # Verificar recuperação
    resume_from = check_recovery_state()
    
    start_time = time.time()
    
    try:
        # Create sender and process
        sender = MegaBatchSender(TOKEN, PHONE_NUMBERS, TEMPLATES)
        result = sender.process_leads(leads, resume_from)
        
        # Limpar estado de recuperação se completou com sucesso
        if os.path.exists('recovery_state.txt'):
            os.remove('recovery_state.txt')
            print("🗑️ Estado de recuperação removido (processamento completo)")
        
        return result
        
    except KeyboardInterrupt:
        print("\n⚠️ INTERROMPIDO PELO USUÁRIO")
        print(f"💾 Progresso salvo para recuperação")
        return {'interrupted': True}
        
    except Exception as e:
        print(f"\n❌ ERRO NO PROCESSAMENTO: {e}")
        print("💾 Estado salvo para recuperação")
        return {'error': str(e)}

def auto_recovery_system():
    """Sistema de recuperação automática"""
    print("🔄 SISTEMA DE RECUPERAÇÃO AUTOMÁTICA")
    
    # Tentar carregar backup
    leads = load_leads_backup()
    if not leads:
        print("❌ Nenhum backup encontrado")
        return
    
    # Verificar posição de recuperação
    resume_from = check_recovery_state()
    if resume_from == 0:
        print("❌ Nenhum estado de recuperação encontrado")
        return
    
    print(f"🔄 RETOMANDO DO LEAD: {resume_from}")
    
    # Recriar dados em formato string
    leads_data = '\n'.join([f"{lead['numero']},{lead['nome']},{lead['cpf']}" for lead in leads])
    
    # Processar
    return process_17k_leads_ultra_fast(leads_data)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'recovery':
        print("🔄 MODO RECUPERAÇÃO ATIVADO")
        result = auto_recovery_system()
    else:
        print("🚀 SISTEMA ULTRA-RÁPIDO PRONTO")
        print("📋 Aguardando lista de 17K leads...")
        print("📝 Formato: numero,nome,cpf (um por linha)")
        print("🔄 Para recuperar: python envio_17k_ultra_rapido.py recovery")