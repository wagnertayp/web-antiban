#!/usr/bin/env python3
"""
Test 60-Second Target: 20K messages in 60 seconds
"""
import requests
import time
import json

def test_60_second_target():
    """Test the 60-second target with optimized configuration"""
    
    print("🚀 TESTE CONFIGURAÇÃO 60 SEGUNDOS")
    print("=" * 60)
    
    # Generate test data for speed test
    test_sizes = [100, 500, 1000]  # Start with smaller batches to verify speed
    
    sample_leads = []
    for i in range(1000):
        sample_leads.append(f"5561991{i:05d},SpeedTest{i},{str(i).zfill(3)}.456.{str(i).zfill(3)}-77")
    
    base_payload = {
        "template_names": ["ricardo_template_1753485866_2620345a"],
        "phone_number_ids": ["764495823408049"],  # Will auto-detect all 20 phones
        "whatsapp_connection": {
            "access_token": "EAAHUCvWVsdgBPBYPZBBM5wfGDmPCguYTbcmmWlQFGFukbGn5ArSLx2UNcY5KA3Ogb9AJOfaN1OpOoRrfWdNQLlAh9MRs3lreupw2P7JXJiNGTeSN5Y6nWKUM7Alx0rTsscDEIboFWBY62lZCqbKAZBgdZA2RSPMwO94nTrdFEygZAPSMrikHZCJZBuNZBYNujxaZA2lqHKK1pi3lPGTpMhIXpXMTnpZBcKZCmRZAJJNFH9w98565JQZDZD",
            "business_manager_id": "2089992404820473"
        }
    }
    
    results = []
    
    for test_size in test_sizes:
        print(f"\n🧪 TESTE: {test_size} leads (Target: {test_size/60:.1f} msg/sec)")
        print("-" * 50)
        
        # Prepare leads
        leads_text = "\n".join(sample_leads[:test_size])
        
        payload = base_payload.copy()
        payload["leads"] = leads_text
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:5000/api/ultra-speed",
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                max_workers = data.get('max_workers', 0)
                estimated_time = data.get('estimated_time_seconds', 0)
                
                print(f"✅ Iniciado - Session: {session_id}")
                print(f"⚡ Workers: {max_workers:,}")
                print(f"📊 Estimativa: {estimated_time}s")
                
                # Monitor progress
                last_progress = 0
                max_monitor_time = 90  # 90 seconds max
                monitor_start = time.time()
                
                while time.time() - monitor_start < max_monitor_time:
                    time.sleep(1)  # Check every second
                    
                    try:
                        progress_response = requests.get(f"http://localhost:5000/api/progress/{session_id}")
                        if progress_response.status_code == 200:
                            progress_data = progress_response.json()
                            
                            status = progress_data.get('status', 'running')
                            sent = progress_data.get('sent', 0)
                            total = progress_data.get('total', 0)
                            elapsed = progress_data.get('elapsed_time', 0)
                            progress = progress_data.get('progress', 0)
                            
                            if progress > last_progress:
                                speed = sent / elapsed if elapsed > 0 else 0
                                print(f"📈 {sent}/{total} ({progress:.1f}%) - {speed:.1f} msg/sec")
                                last_progress = progress
                            
                            if status == 'completed':
                                final_speed = sent / elapsed if elapsed > 0 else 0
                                
                                print(f"\n✅ COMPLETO!")
                                print(f"📊 Enviados: {sent}/{total}")
                                print(f"⏱️ Tempo: {elapsed:.1f}s")
                                print(f"🚀 Velocidade: {final_speed:.1f} msg/sec")
                                
                                # Calculate 20K projection
                                projected_20k_time = 20000 / final_speed if final_speed > 0 else 999
                                target_achieved = projected_20k_time <= 60
                                
                                print(f"🎯 20K Projeção: {projected_20k_time:.1f}s {'✅' if target_achieved else '❌'}")
                                
                                results.append({
                                    'size': test_size,
                                    'time': elapsed,
                                    'speed': final_speed,
                                    'workers': max_workers,
                                    'projection_20k': projected_20k_time,
                                    'target_achieved': target_achieved
                                })
                                break
                    except:
                        continue
                else:
                    print(f"⚠️ Timeout após {max_monitor_time}s")
                    
            else:
                print(f"❌ Erro: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Exceção: {e}")
    
    # Final analysis
    if results:
        print(f"\n🎯 ANÁLISE FINAL - META 60 SEGUNDOS")
        print("=" * 60)
        
        successful_results = [r for r in results if r['target_achieved']]
        
        if successful_results:
            best = max(successful_results, key=lambda x: x['speed'])
            print(f"✅ META ATINGIDA!")
            print(f"📊 Melhor resultado: {best['size']} leads")
            print(f"⚡ Velocidade: {best['speed']:.1f} msg/sec")
            print(f"🎯 20K em: {best['projection_20k']:.1f} segundos")
            print(f"🏭 Workers: {best['workers']:,}")
        else:
            best = max(results, key=lambda x: x['speed'])
            print(f"⚠️ Meta não atingida ainda")
            print(f"📊 Melhor resultado: {best['speed']:.1f} msg/sec")
            print(f"🎯 20K precisaria: {best['projection_20k']:.1f} segundos")
            print(f"💡 Otimização adicional necessária")
            
            # Suggest optimizations
            print(f"\n💡 SUGESTÕES PARA ATINGIR 60s:")
            needed_speed = 20000 / 60  # 333.33 msg/sec
            current_speed = best['speed']
            multiplier_needed = needed_speed / current_speed
            
            print(f"   - Velocidade necessária: {needed_speed:.1f} msg/sec")
            print(f"   - Velocidade atual: {current_speed:.1f} msg/sec")
            print(f"   - Multiplicador necessário: {multiplier_needed:.1f}x")
            
            if multiplier_needed <= 2:
                print(f"   ✅ Viável com otimização de workers")
            elif multiplier_needed <= 5:
                print(f"   ⚡ Viável usando todos os 20 phone numbers")
            else:
                print(f"   🚀 Necessário sistema multi-BM")

if __name__ == "__main__":
    test_60_second_target()