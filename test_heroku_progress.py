#!/usr/bin/env python3
"""
Teste específico para progresso no Heroku
"""
import requests
import time
import json

def testar_progresso_heroku():
    """Testa se o progresso funciona no Heroku"""
    
    print("🧪 TESTE PROGRESSO HEROKU")
    print("=" * 50)
    
    # Configuração para teste
    url = "http://localhost:5000"
    token = "EAAHUCvWVsdgBPBYPZBBM5wfGDmPCguYTbcmmWlQFGFukbGn5ArSLx2UNcY5KA3Ogb9AJOfAN1OpOoRrfWdNQLlAh9MRs3lreupw2P7JXJiNGTeSN5Y6nWKUM7Alx0rTsscDEIboFWBY62lZCqbKAZBgdZA2RSPMwO94nTrdFEygZAPSMrikHZCJZBuNZBYNujxaZA2lqHKK1pi3lPGTpMhIXpXMTnpZBcKZCmRZAJJNFH9w98565JQZDZD"
    
    # Lista de teste pequena para verificar progresso
    test_leads = [
        "João Silva,12345678901,5511999999999",
        "Maria Santos,98765432100,5511888888888", 
        "Pedro Oliveira,11111111111,5511777777777"
    ]
    
    try:
        print("🚀 1. Enviando mensagens...")
        
        payload = {
            'whatsapp_connection': {
                'access_token': token,
                'business_manager_id': '2089992404820473'
            },
            'leads': '\n'.join(test_leads),
            'template_names': ['ricardo_template_1753490810_b7ac4671'],
            'phone_number_ids': ['764495823408049']
        }
        
        # Enviar via ultra-speed
        response = requests.post(f"{url}/api/ultra-speed", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"✅ Iniciado - Session: {session_id}")
            print(f"⚡ Mode: {data.get('mode', 'N/A')}")
            print(f"📊 Leads: {data.get('leads', 0)}")
            
            # Monitorar progresso
            print("\n📊 2. Monitorando progresso...")
            for i in range(30):  # 30 segundos máximo
                try:
                    progress_response = requests.get(f"{url}/api/progress/{session_id}", timeout=5)
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        sent = progress_data.get('sent', 0)
                        failed = progress_data.get('failed', 0)
                        total = progress_data.get('total', 0)  
                        progress = progress_data.get('progress', 0)
                        
                        print(f"   [{i+1:2d}s] {sent}/{total} enviadas - {failed} falhas - {progress:.1f}%")
                        
                        # Se completou, parar
                        if progress >= 100 or (sent + failed) >= total:
                            print("✅ Processamento completo!")
                            break
                            
                    else:
                        print(f"   [{i+1:2d}s] ❌ Erro ao buscar progresso: {progress_response.status_code}")
                        
                except Exception as e:
                    print(f"   [{i+1:2d}s] ❌ Erro na requisição: {str(e)[:50]}")
                
                time.sleep(1)
        else:
            print(f"❌ Erro ao iniciar: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def verificar_contador():
    """Verifica contadores ativos"""
    
    print("\n🔍 VERIFICANDO CONTADORES ATIVOS")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/progress/test", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida: {data}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_progresso_heroku()
    verificar_contador()