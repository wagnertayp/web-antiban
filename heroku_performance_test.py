#!/usr/bin/env python3
"""
Real Heroku Performance Test - Test optimized configuration
"""
import requests
import time
import json

def test_optimized_performance():
    """Test with optimized configuration"""
    
    # Test larger batches to see real speed
    test_cases = [
        {"leads": 100, "description": "Optimized 100 leads"},
        {"leads": 500, "description": "Optimized 500 leads"}, 
        {"leads": 1000, "description": "Optimized 1000 leads"}
    ]
    
    # Generate realistic test data
    sample_leads = []
    for i in range(1000):
        sample_leads.append(f"5561991{i:05d},Lead{i},{str(i).zfill(3)}.456.{str(i).zfill(3)}-77")
    
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
        
        print(f"\n🚀 TESTE OTIMIZADO: {description}")
        print("=" * 60)
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:5000/api/ultra-speed",
                json=payload,
                timeout=600  # 10 minute timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                max_workers = data.get('max_workers', 0)
                
                print(f"✅ Processamento iniciado - Session: {session_id}")
                print(f"⚡ Workers otimizados: {max_workers:,}")
                
                # Monitor progress in real-time
                max_wait_time = 300  # 5 minutes max
                start_monitor = time.time()
                last_sent = 0
                
                while time.time() - start_monitor < max_wait_time:
                    time.sleep(2)
                    
                    progress_response = requests.get(f"http://localhost:5000/api/progress/{session_id}")
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        status = progress_data.get('status', 'running')
                        sent = progress_data.get('sent', 0)
                        total = progress_data.get('total', 0)
                        elapsed = progress_data.get('elapsed_time', 0)
                        
                        if sent > last_sent:
                            speed = sent / elapsed if elapsed > 0 else 0
                            print(f"📊 Progress: {sent}/{total} ({speed:.1f} leads/sec)")
                            last_sent = sent
                        
                        if status == 'completed':
                            final_time = elapsed
                            final_speed = sent / elapsed if elapsed > 0 else 0
                            
                            print(f"\n✅ TESTE COMPLETO!")
                            print(f"📈 Enviado: {sent}/{total} leads")
                            print(f"⏱️ Tempo total: {final_time:.1f} segundos")
                            print(f"🚀 Velocidade: {final_speed:.1f} leads/sec ({final_speed * 60:.0f} leads/min)")
                            
                            results.append({
                                'leads': lead_count,
                                'time': final_time,
                                'speed_per_sec': final_speed,
                                'speed_per_min': final_speed * 60,
                                'workers': max_workers,
                                'sent': sent,
                                'total': total
                            })
                            break
                else:
                    print(f"⚠️ Timeout - teste excedeu {max_wait_time}s")
                    
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Calculate realistic projection for 20K leads
    if results:
        print(f"\n🎯 PROJEÇÃO REALÍSTICA PARA 20.000 LEADS")
        print("=" * 60)
        
        # Use largest successful test for projection
        best_result = max([r for r in results if r['sent'] == r['total']], 
                         key=lambda x: x['speed_per_sec'], default=None)
        
        if best_result:
            leads_20k = 20000
            projected_time_sec = leads_20k / best_result['speed_per_sec']
            projected_time_min = projected_time_sec / 60
            
            print(f"📊 Melhor resultado: {best_result['leads']} leads em {best_result['time']:.1f}s")
            print(f"⚡ Velocidade sustentada: {best_result['speed_per_sec']:.1f} leads/sec")
            print(f"🎯 PROJEÇÃO 20K: {projected_time_sec:.0f} segundos ({projected_time_min:.1f} minutos)")
            print(f"🏭 Workers necessários: {best_result['workers']:,}")
            
            # Performance categories
            if projected_time_min <= 3:
                print(f"🏆 ULTRA RÁPIDO: Menos de 3 minutos!")
            elif projected_time_min <= 10:
                print(f"🚀 RÁPIDO: {projected_time_min:.1f} minutos")
            elif projected_time_min <= 30:
                print(f"⚡ ACEITÁVEL: {projected_time_min:.1f} minutos")
            else:
                print(f"⚠️ LENTO: {projected_time_min:.1f} minutos - otimização necessária")
            
            # Heroku cost estimation
            minutes_per_hour = 60
            cost_per_hour_performance_l = 25  # USD
            hourly_capacity = best_result['speed_per_sec'] * 3600
            
            print(f"\n💰 ANÁLISE DE CUSTO HEROKU PERFORMANCE-L")
            print("=" * 60)
            print(f"💵 Custo: ${cost_per_hour_performance_l}/hora")
            print(f"📊 Capacidade: {hourly_capacity:,.0f} leads/hora")
            print(f"💸 Custo por 20K leads: ${(projected_time_min/60) * cost_per_hour_performance_l:.2f}")

if __name__ == "__main__":
    test_optimized_performance()