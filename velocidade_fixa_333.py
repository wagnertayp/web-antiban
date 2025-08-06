#!/usr/bin/env python3
"""
Sistema Velocidade Fixa: 333 msg/sec independente do número de phones
"""

def calcular_velocidade_fixa():
    """Calcula configuração para 333 msg/sec fixo"""
    
    print("🎯 SISTEMA VELOCIDADE FIXA: 333 MSG/SEC")
    print("=" * 60)
    
    FIXED_SPEED = 333  # Velocidade FIXA independente de phones
    
    # Cenários com diferentes quantidades de phones
    scenarios = [
        {"phones": 1, "name": "Cenário Mínimo"},
        {"phones": 5, "name": "Cenário Pequeno"}, 
        {"phones": 10, "name": "Cenário Médio"},
        {"phones": 20, "name": "Cenário Atual (BM Iara)"},
        {"phones": 50, "name": "Cenário Máximo"}
    ]
    
    print(f"🔢 VELOCIDADE FIXA: {FIXED_SPEED} msg/sec")
    print(f"⏱️ TEMPO PARA 20K: {20000/FIXED_SPEED:.1f} segundos")
    print()
    
    for scenario in scenarios:
        phones = scenario["phones"]
        msg_per_phone = FIXED_SPEED / phones
        workers_per_phone = max(50, int(msg_per_phone * 3))  # 3x multiplier
        total_workers = workers_per_phone * phones
        
        print(f"📱 {scenario['name']} ({phones} phones):")
        print(f"   Msg/phone/sec: {msg_per_phone:.1f}")
        print(f"   Workers/phone: {workers_per_phone}")
        print(f"   Total workers: {total_workers:,}")
        print(f"   Velocidade total: {FIXED_SPEED} msg/sec ✅")
        print()
    
    print("💡 VANTAGENS DO SISTEMA VELOCIDADE FIXA:")
    print("=" * 60)
    print("✅ Velocidade SEMPRE 333 msg/sec")
    print("✅ Funciona com 1 phone ou 50 phones") 
    print("✅ Auto-ajuste de workers por phone")
    print("✅ 20K mensagens SEMPRE em 60 segundos")
    print("✅ Previsibilidade total")
    
    print("\n🔧 IMPLEMENTAÇÃO:")
    print("- Workers calculados: 333 × 2 = 666 base workers")
    print("- Distribuição automática entre phones disponíveis")
    print("- 1 phone = 666 workers | 20 phones = 33 workers/phone")
    print("- Resultado: SEMPRE 333 msg/sec total")

def demonstrar_auto_ajuste():
    """Demonstra como o sistema se auto-ajusta"""
    
    print(f"\n🔄 DEMONSTRAÇÃO AUTO-AJUSTE")
    print("=" * 60)
    
    base_workers = 333 * 2  # 666 workers base para 333 msg/sec
    
    phone_counts = [1, 5, 10, 15, 20, 25]
    
    print("Phone Count | Workers/Phone | Total Workers | Speed")
    print("-" * 50)
    
    for phones in phone_counts:
        workers_per_phone = max(50, base_workers // phones)
        total_workers = workers_per_phone * phones
        theoretical_speed = total_workers // 2  # 2 workers per msg/sec
        
        print(f"{phones:2d} phones   | {workers_per_phone:4d}         | {total_workers:6,}     | {min(theoretical_speed, 333)} msg/sec")
    
    print("\n📊 RESULTADO:")
    print("- Independente do número de phones")
    print("- Velocidade SEMPRE próxima de 333 msg/sec")
    print("- System se adapta automaticamente")

if __name__ == "__main__":
    calcular_velocidade_fixa()
    demonstrar_auto_ajuste()