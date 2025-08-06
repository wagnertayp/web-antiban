#!/usr/bin/env python3
"""
ENVIO DIRETO DE 17K LEADS - Sistema interno Replit
Token atualizado: EAAHUCvWVsdgBPLLcZCYCfrKPWMUZBRHCstJhmuAZBNLUB1tCr...
"""

import os
import sys
import time
import logging
from mega_batch_simple import send_mega_batch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Token atualizado
TOKEN = "EAAHUCvWVsdgBPLLcZCYCfrKPWMUZBRHCstJhmuAZBNLUB1tCrLeXshgqH7B5ylSmlkKHB2I934AW6rHnzOODlpcSRwixUZCx5katC9wZAhwE6M2GjFnGN2V0ZAjZB9eONmyY6A0LWKaCz2uyyYnIQpl5Ddvw3BVV0cWXBlekkjzKofDraA6ZCEPqCjCUOUSYkVolUc7BMtHti70Qem02Wtw5IwDMEnLCkAYZCZBoUGaLGDg1PuNNkZD"

# Phone Numbers da BM 2089992404820473 (20 números ativos)
PHONE_NUMBERS = [
    '725492557312328',  # Phone 1
    '800312496489716',  # Phone 2
    '776788602173980',  # Phone 3
    '774576132396207',  # Phone 4
    '764495823408049',  # Phone 5
    '764138826774184',  # Phone 6
    '749599158230143',  # Phone 7
    '747868138404614',  # Phone 8
    '746367015221228',  # Phone 9
    '736306482898341',  # Phone 10
    '732911983238956',  # Phone 11
    '728240807037686',  # Phone 12
    '721222711076869',  # Phone 13
    '718291801369739',  # Phone 14
    '712294161968633',  # Phone 15
    '706148559252459',  # Phone 16
    '698088016726677',  # Phone 17
    '674341985771514',  # Phone 18
    '672331669304211',  # Phone 19
    '670736396133662'   # Phone 20
]

# Templates aprovados da BM
TEMPLATES = [
    'modelo21',  # pt_BR template
    'ricardo_template_1753485590_b501867c',
    'ricardo_template_1753485474_512444ac',
    'ricardo_template_1753485563_5882b9ba',
    'ricardo_template_1753487895_cbe4d528',
    'ricardo_template_1753485866_2620345a',
    'ricardo_template_1753485422_108ba28d',
    'ricardo_template_1753487909_d79bcb95',
    'ricardo_template_1753487687_5860ab23',
    'ricardo_template_1753485525_d3a7f18d',
    'ricardo_template_1753487879_89f32594'
]

def process_17k_leads(leads_data):
    """
    Processa 17K leads com o sistema burst
    """
    print("🚀 INICIANDO PROCESSAMENTO DE 17K LEADS")
    print(f"📱 Token: {TOKEN[:30]}...")
    print(f"📞 Phone Numbers: {len(PHONE_NUMBERS)} ativos")
    print(f"📝 Templates: {len(TEMPLATES)} aprovados")
    print("💥 Velocidade: 300 msg/sec com rajadas")
    print("=" * 60)
    
    start_time = time.time()
    
    # Execute mega batch
    result = send_mega_batch(TOKEN, leads_data, PHONE_NUMBERS, TEMPLATES)
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("🎯 PROCESSAMENTO COMPLETO:")
    print(f"✅ Enviadas: {result.get('sent', 0)}")
    print(f"❌ Falharam: {result.get('failed', 0)}")
    print(f"⏱️ Tempo: {total_time:.1f} segundos")
    print(f"⚡ Velocidade: {result.get('speed', 0):.1f} msg/sec")
    
    return result

if __name__ == "__main__":
    print("🚀 SISTEMA PRONTO PARA 17K LEADS")
    print("📋 Cole sua lista de leads aqui e execute:")
    print("   python send_17k_leads.py")
    print("")
    print("📝 Formato esperado:")
    print("   5561999114066,Pedro,06537080177")
    print("   5511988057271,BRUNO,34655010800")
    print("   ...")