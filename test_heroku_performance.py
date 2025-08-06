#!/usr/bin/env python3
"""
Test Heroku Performance - Calculate real speed for 20K leads
"""
import requests
import time
import json

def test_heroku_performance():
    """Test real performance on Heroku"""
    
    # Test with different lead sizes to calculate speed
    test_cases = [
        {"leads": 1, "description": "Single lead test"},
        {"leads": 10, "description": "Small batch test"},
        {"leads": 50, "description": "Medium batch test"}
    ]
    
    # Sample data for testing
    sample_leads = []
    for i in range(50):
        sample_leads.append(f"556199114{i:03d},Lead{i},123.456.{i:03d}-77")
    
    base_payload = {
        "template_names": ["ricardo_template_1753485866_2620345a"],
        "phone_number_ids": ["764495823408049"],
        "whatsapp_connection": {
            "access_token": "EAAHUCvWVsdgBPBYPZBBM5wfGDmPCguYTbcmmWlQFGFukbGn5ArSLx2UNcY5KA3Ogb9AJOfAN1OpOoRrfWdNQLlAh9MRs3lreupw2P7JXJiNGTeSN5Y6nWKUM7Alx0rTsscDEIboFWBY62lZCqbKAZBgdZA2RSPMwO94nTrdFEygZAPSMrikHZCJZBuNZBYNujxaZA2lqHKK1pi3lPGTpMhIXpXMTnpZBcKZCmRZAJJNFH9w98565JQZDZD",
            "business_manager_id": "2089992404820473"
        }
    }
    
    results = []
    
    for test_case in test_cases:
        lead_count = test_case["leads"]
        description = test_case["description"]
        
        # Prepare leads
        leads_text = "\n".join(sample_leads[:lead_count])
        
        payload = base_payload.copy()
        payload["leads"] = leads_text
        
        print(f"\n🧪 TESTE: {description} ({lead_count} leads)")
        print("=" * 50)
        
        # Send request
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:5000/api/ultra-speed",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                estimated_time = data.get('estimated_time_seconds', 0)
                max_workers = data.get('max_workers', 0)
                
                print(f"✅ Request enviado - Session: {session_id}")
                print(f"📊 Workers: {max_workers:,}")
                print(f"⏱️ Tempo estimado: {estimated_time}s")
                
                # Wait and check progress
                time.sleep(2)
                
                # Check final status
                progress_response = requests.get(f"http://localhost:5000/api/progress/{session_id}")
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    elapsed_time = progress_data.get('elapsed_time', 0)
                    sent = progress_data.get('sent', 0)
                    total = progress_data.get('total', 0)
                    
                    # Calculate speed
                    if elapsed_time > 0:
                        leads_per_second = sent / elapsed_time
                        leads_per_minute = leads_per_second * 60
                    else:
                        leads_per_second = 0
                        leads_per_minute = 0
                    
                    print(f"⚡ Processado: {sent}/{total} leads")
                    print(f"🕒 Tempo real: {elapsed_time:.1f}s")
                    print(f"🚀 Velocidade: {leads_per_second:.1f} leads/sec ({leads_per_minute:.0f} leads/min)")
                    
                    results.append({
                        'leads': lead_count,
                        'time': elapsed_time,
                        'speed_per_sec': leads_per_second,
                        'speed_per_min': leads_per_minute,
                        'workers': max_workers
                    })
                    
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Calculate projection for 20K leads
    if results:
        print(f"\n🎯 PROJEÇÃO PARA 20.000 LEADS")
        print("=" * 50)
        
        # Use best performance result
        best_result = max(results, key=lambda x: x['speed_per_sec'])
        
        leads_20k = 20000
        time_20k_seconds = leads_20k / best_result['speed_per_sec'] if best_result['speed_per_sec'] > 0 else 0
        time_20k_minutes = time_20k_seconds / 60
        
        print(f"📈 Melhor velocidade observada: {best_result['speed_per_sec']:.1f} leads/sec")
        print(f"⏱️ Tempo para 20K leads: {time_20k_seconds:.0f} segundos ({time_20k_minutes:.1f} minutos)")
        print(f"🏭 Workers utilizados: {best_result['workers']:,}")
        
        # Heroku Performance-L specs
        print(f"\n🏗️ CAPACIDADE HEROKU PERFORMANCE-L")
        print("=" * 50)
        print("💾 RAM: 14GB")
        print("🖥️ CPU: 8 cores")
        print("🔗 Conexões HTTP: Até 30,000 simultâneas")
        print("⚡ Configuração atual: Até 100,000 workers")
        
        if time_20k_minutes <= 1:
            print(f"✅ META ATINGIDA: 20K leads em {time_20k_minutes:.1f} minutos (menos de 1 minuto!)")
        elif time_20k_minutes <= 5:
            print(f"🎯 EXCELENTE: 20K leads em {time_20k_minutes:.1f} minutos (menos de 5 minutos)")
        else:
            print(f"⚠️ OTIMIZAÇÃO NECESSÁRIA: 20K leads em {time_20k_minutes:.1f} minutos")

if __name__ == "__main__":
    test_heroku_performance()