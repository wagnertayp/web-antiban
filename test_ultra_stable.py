#!/usr/bin/env python3
"""
Teste do sistema ULTRA STABLE - Anti-travamento
"""

import requests
import json
import time

def test_ultra_stable():
    """Teste do sistema com configurações anti-travamento"""
    
    # Lista pequena para teste de estabilidade
    test_leads = """5561999114066,Pedro,065.370.801-77
5543999839202,LEONARDO VARGAS GOMES,062.854.289-56
5592984063001,ERVELI MOREIRA DE CASTRO,007.451.092-41
5531990641145,LUCAS MARTINS RAMOS,126.239.906-89
5521966344774,PALOMA DE OLIVEIRA PORTO,168.544.367-29
5541996501513,ELEZIANE RODRIGUES FRANCA,049.584.399-78
5561995773116,FERNANDA FERREIRA DA SILVA,053.100.941-64
5554992987963,VANESSA MOREIRA DIAS,028.906.340-00
5518996886706,ANA CLARA MATTA CRUZ,484.266.998-55
5565992107337,CHARLLES RIBEIRO DE ASSIS SILVA,021.738.621-03"""
    
    payload = {
        'leads': test_leads,
        'template_names': ['jose_template_1752883070_87d0311e', 'jose_template_1752924461_d50dcbee'],
        'phone_number_ids': ['746209145234709', '782640984922130', '775859882269062', '745498515309824', '652047048001128']
    }
    
    print("🚀 Testando sistema ULTRA STABLE...")
    print(f"📊 Testando com {len(test_leads.split())} leads")
    print(f"📱 Usando {len(payload['phone_number_ids'])} phone numbers")
    print(f"📋 Usando {len(payload['template_names'])} templates")
    
    try:
        # Enviar requisição para o endpoint ULTRA STABLE
        response = requests.post(
            'http://0.0.0.0:5000/api/ultra-speed',
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            
            if session_id:
                print(f"✅ Sessão iniciada: {session_id}")
                
                # Monitorar progresso por 60 segundos
                for i in range(60):
                    time.sleep(1)
                    
                    try:
                        progress_response = requests.get(
                            f'http://0.0.0.0:5000/api/progress/{session_id}',
                            timeout=5
                        )
                        
                        if progress_response.status_code == 200:
                            progress_data = progress_response.json()
                            sent = progress_data.get('sent', 0)
                            failed = progress_data.get('failed', 0)
                            status = progress_data.get('status', 'running')
                            
                            print(f"📈 [{i+1}s] Sent: {sent}, Failed: {failed}, Status: {status}")
                            
                            if status == 'completed':
                                print("✅ TESTE CONCLUÍDO COM SUCESSO!")
                                print(f"📊 Final: {sent} enviadas, {failed} falhas")
                                return True
                                
                        else:
                            print(f"⚠️  Erro ao buscar progresso: {progress_response.status_code}")
                            
                    except Exception as e:
                        print(f"⚠️  Erro na consulta de progresso: {e}")
                
                print("⏰ Timeout de 60 segundos atingido")
            else:
                print("❌ Session ID não retornado")
        else:
            print(f"❌ Erro na requisição: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        
    return False

if __name__ == "__main__":
    success = test_ultra_stable()
    if success:
        print("\n🎉 SISTEMA ULTRA STABLE FUNCIONANDO - SEM TRAVAMENTOS!")
    else:
        print("\n❌ Sistema ainda apresenta problemas")