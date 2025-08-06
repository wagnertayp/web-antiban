"""
REPLIT DEPLOYMENT CONFIGURATION
Sistema otimizado para 300 mensagens/segundo sem travamento em 964 mensagens
"""

# CONFIGURAÇÃO REPLIT DEPLOY - ANTI-TRAVAMENTO
REPLIT_CONFIG = {
    'max_workers': 1000,          # 1K WORKERS para evitar travamentos
    'batch_size': 200,            # LOTES PEQUENOS para estabilidade
    'connection_pool_size': 500,  # Pool reduzido para evitar crash
    'rate_limit_delay': 0.001,    # Delay mínimo para velocidade
    'burst_mode': False,          # DISABLE burst para estabilidade
    'api_calls_per_second': 300,  # EXACTLY 300 msg/sec target
    'timeout': 15,                # Timeout reduzido para Replit
    'memory_management': True,    # Limpeza automática de memória
    'parallel_optimization': False, # Disable para estabilidade
    'instant_mode': False,        # Sequential mode mais estável
    'phone_multiplier': 20,       # USAR TODOS os 20 phones
    'messages_per_second_target': 300, # TARGET: 300 messages/sec
    'replit_stable_mode': True,   # Enable Replit stability mode
    'micro_batch_size': 50,       # 50 mensagens por micro-batch
    'anti_thread_crash': True,    # Sistema anti-travamento de threads
}

# CONFIGURAÇÃO ESPECÍFICA PARA LISTAS GRANDES (964+ leads)
ANTI_CRASH_CONFIG = {
    'batch_size': 3000,           # LOTES GRANDES para 300 msg/sec
    'max_workers': 15000,         # 15K WORKERS para máxima velocidade
    'delay_between_batches': 0.00001, # Delay nano-mínimo para 300 msg/sec
    'memory_cleanup_interval': 5,  # Limpeza a cada 5 lotes
    'connection_timeout': 10,      # Timeout reduzido para conexões
    'retry_attempts': 2,           # Máximo 2 tentativas por mensagem
}

# CONFIGURAÇÃO DE DEPLOYMENT REPLIT
DEPLOYMENT_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'threaded': True,
    'use_reloader': False,
    'processes': 1,
    'max_content_length': 16 * 1024 * 1024,  # 16MB max
}

# CONFIGURAÇÃO GUNICORN PARA REPLIT
GUNICORN_CONFIG = {
    'bind': '0.0.0.0:5000',
    'workers': 1,
    'worker_class': 'sync',
    'worker_connections': 1000,
    'max_requests': 10000,
    'max_requests_jitter': 1000,
    'timeout': 30,
    'keepalive': 2,
    'preload_app': True,
    'reload': False,
}

def get_config_for_lead_count(lead_count):
    """
    Retorna configuração otimizada baseada no número de leads
    """
    if lead_count > 900:
        # MODO ANTI-TRAVAMENTO para listas grandes
        return {
            **REPLIT_CONFIG,
            **ANTI_CRASH_CONFIG,
            'mode': 'anti_crash',
            'description': f'Anti-crash mode for {lead_count} leads'
        }
    elif lead_count > 500:
        # MODO OTIMIZADO para listas médias
        return {
            **REPLIT_CONFIG,
            'batch_size': 25,
            'max_workers': 12,
            'delay_between_batches': 0.08,
            'mode': 'optimized',
            'description': f'Optimized mode for {lead_count} leads'
        }
    else:
        # MODO PADRÃO para listas pequenas
        return {
            **REPLIT_CONFIG,
            'mode': 'standard',
            'description': f'Standard mode for {lead_count} leads'
        }

def calculate_estimated_time(lead_count, config):
    """
    Calcula tempo estimado baseado na configuração
    """
    batch_size = config['batch_size']
    delay = config.get('delay_between_batches', 0.1)  # Default 100ms
    batches = (lead_count + batch_size - 1) // batch_size
    
    # Tempo = (número de lotes * delay) + tempo de processamento
    processing_time = lead_count / 300  # 300 msg/sec target
    delay_time = batches * delay
    
    return processing_time + delay_time

# VALIDAÇÃO DE CONFIGURAÇÃO
def validate_replit_config():
    """
    Valida se a configuração está otimizada para Replit
    """
    checks = {
        'workers_safe': REPLIT_CONFIG['max_workers'] <= 200,
        'batch_size_optimal': REPLIT_CONFIG['batch_size'] <= 50,
        'delay_sustainable': REPLIT_CONFIG['rate_limit_delay'] >= 0.003,
        'target_achievable': REPLIT_CONFIG['messages_per_second_target'] == 300,
        'anti_crash_enabled': REPLIT_CONFIG['anti_thread_crash'] == True,
    }
    
    return all(checks.values()), checks