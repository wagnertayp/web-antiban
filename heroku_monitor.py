#!/usr/bin/env python3
"""
Monitor de performance em tempo real para Heroku
"""

import requests
import time
import os
import json
from datetime import datetime

class HerokuMonitor:
    def __init__(self, app_url):
        self.app_url = app_url.rstrip('/')
        
    def get_system_status(self):
        """Verifica status do sistema"""
        try:
            response = requests.get(f"{self.app_url}/api/system-status", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def monitor_real_time(self, duration_minutes=30):
        """Monitor em tempo real"""
        
        print(f"🔍 MONITOR HEROKU - {self.app_url}")
        print("=" * 60)
        print(f"⏰ Monitoramento por {duration_minutes} minutos")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Status do sistema
            status = self.get_system_status()
            
            print(f"\n[{current_time}] 📊 STATUS HEROKU")
            print("-" * 40)
            
            if status:
                print(f"🚀 Dyno: {status.get('dyno', 'unknown')}")
                print(f"💾 Memory: {status.get('memory_usage', 'unknown')}")
                print(f"🔧 Workers ativos: {status.get('active_workers', 0)}")
                print(f"📨 Mensagens/min: {status.get('messages_per_minute', 0)}")
                print(f"✅ Taxa sucesso: {status.get('success_rate', 0)}%")
                
                # Alertas
                memory = status.get('memory_usage_percent', 0)
                if memory > 80:
                    print("⚠️ ALERTA: Uso de memória alto!")
                
                workers = status.get('active_workers', 0)
                if workers > 1500:
                    print("⚠️ ALERTA: Muitos workers ativos!")
                    
            else:
                print("❌ Não foi possível obter status")
            
            # Verificar sessões ativas
            try:
                sessions_response = requests.get(f"{self.app_url}/api/active-sessions", timeout=5)
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    active_count = len([s for s in sessions.get('sessions', []) if s.get('status') == 'running'])
                    
                    if active_count > 0:
                        print(f"📈 Sessões ativas: {active_count}")
                        for session in sessions.get('sessions', [])[:3]:  # Mostrar até 3
                            sent = session.get('sent', 0)
                            total = session.get('total', 0)
                            progress = (sent/total*100) if total > 0 else 0
                            print(f"   • Sessão {session.get('id', '')[:8]}: {sent}/{total} ({progress:.1f}%)")
            except:
                pass
            
            print("-" * 40)
            time.sleep(30)  # Update a cada 30 segundos
        
        print(f"\n✅ Monitoramento concluído após {duration_minutes} minutos")

    def performance_report(self):
        """Gera relatório de performance"""
        
        print("📊 RELATÓRIO DE PERFORMANCE HEROKU")
        print("=" * 50)
        
        # Verificar métricas dos últimos 24h
        try:
            metrics_response = requests.get(f"{self.app_url}/api/metrics/24h", timeout=15)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                
                print(f"📅 Período: Últimas 24 horas")
                print(f"📨 Total mensagens: {metrics.get('total_messages', 0):,}")
                print(f"✅ Enviadas: {metrics.get('sent_messages', 0):,}")
                print(f"❌ Falharam: {metrics.get('failed_messages', 0):,}")
                print(f"📈 Taxa de sucesso: {metrics.get('success_rate', 0):.1f}%")
                print(f"⚡ Pico de velocidade: {metrics.get('peak_speed', 0):,} msg/min")
                print(f"🕐 Tempo médio/msg: {metrics.get('avg_time_per_message', 0):.2f}s")
                
                # Alertas de performance
                if metrics.get('success_rate', 0) < 90:
                    print("⚠️ ALERTA: Taxa de sucesso baixa!")
                
                if metrics.get('avg_time_per_message', 0) > 2:
                    print("⚠️ ALERTA: Tempo por mensagem alto!")
                    
            else:
                print("❌ Não foi possível obter métricas")
                
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")

def main():
    print("🚀 HEROKU PERFORMANCE MONITOR")
    print("=" * 50)
    
    # URL da app
    app_url = input("Digite a URL da sua app no Heroku: ").strip()
    
    if not app_url:
        print("❌ URL necessária!")
        return
    
    monitor = HerokuMonitor(app_url)
    
    print("\nEscolha uma opção:")
    print("1. Monitor em tempo real (30 min)")
    print("2. Monitor curto (5 min)")
    print("3. Relatório de performance")
    print("4. Status atual")
    
    choice = input("\nDigite sua escolha (1-4): ").strip()
    
    if choice == "1":
        monitor.monitor_real_time(30)
    elif choice == "2":
        monitor.monitor_real_time(5)
    elif choice == "3":
        monitor.performance_report()
    elif choice == "4":
        status = monitor.get_system_status()
        if status:
            print("\n📊 STATUS ATUAL:")
            print(json.dumps(status, indent=2))
        else:
            print("❌ Não foi possível obter status")
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()