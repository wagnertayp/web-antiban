#!/usr/bin/env python3
"""
Script otimizado para iniciar o Gunicorn com configurações de performance
Evita worker starvation através de múltiplos workers e threads
"""
import subprocess
import sys
import os

def start_app():
    """Inicia aplicação Flask com Gunicorn otimizado"""
    
    # Configuração dinâmica baseada no ambiente
    workers = os.environ.get('WEB_CONCURRENCY', '4')  # 4 workers por padrão
    timeout = os.environ.get('TIMEOUT', '60')         # 60s timeout para falhar rapidamente
    
    gunicorn_cmd = [
        'gunicorn',
        '--config', 'gunicorn.conf.py',
        '--bind', '0.0.0.0:5000',
        '--workers', workers,
        '--threads', '4',
        '--timeout', timeout,
        '--worker-class', 'sync',
        '--worker-connections', '1000',
        '--keepalive', '5',
        '--max-requests', '2000',
        '--max-requests-jitter', '200',
        '--preload',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'main:app'
    ]
    
    print(f"🚀 Iniciando com {workers} workers, timeout {timeout}s")
    print(f"📋 Comando: {' '.join(gunicorn_cmd)}")
    
    try:
        subprocess.run(gunicorn_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar Gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Aplicação interrompida pelo usuário")
        sys.exit(0)

if __name__ == '__main__':
    start_app()