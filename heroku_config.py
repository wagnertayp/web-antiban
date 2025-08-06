"""
Heroku-specific configuration optimizations for maximum performance
"""
import os

class HerokuConfig:
    """Configuration class optimized for Heroku deployment"""
    
    # Heroku Dyno optimization settings
    HEROKU_DYNO_TYPE = os.environ.get('DYNO', 'web.1')
    
    # Ultra-speed processing configuration for Heroku Performance Dynos
    ULTRA_SPEED_CONFIG = {
        # Maximum workers based on Heroku Performance-L specs (14GB RAM, 8 cores)
        'max_workers': int(os.environ.get('MAX_WORKERS', '2000')),          # Ultra-high for Performance Dynos
        'batch_size': int(os.environ.get('BATCH_SIZE', '1000')),           # Large batches for efficiency
        'thread_multiplier': int(os.environ.get('THREAD_MULTIPLIER', '100')), # Maximum parallelism
        'connection_pool_size': int(os.environ.get('CONNECTION_POOL_SIZE', '500')),
        'rate_limit_delay': float(os.environ.get('RATE_LIMIT_DELAY', '0.001')), # Minimal delay
        'memory_cleanup_interval': int(os.environ.get('CLEANUP_INTERVAL', '100')),
    }
    
    # Database optimization for Heroku Postgres
    DATABASE_CONFIG = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '20')),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '30')),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
    }
    
    # WhatsApp API optimization
    WHATSAPP_CONFIG = {
        'timeout': int(os.environ.get('WHATSAPP_TIMEOUT', '30')),
        'max_retries': int(os.environ.get('WHATSAPP_MAX_RETRIES', '3')),
        'concurrent_connections': int(os.environ.get('WHATSAPP_CONNECTIONS', '1000')),
    }
    
    @classmethod
    def is_heroku(cls):
        """Check if running on Heroku"""
        return 'DYNO' in os.environ
    
    @classmethod
    def get_dyno_info(cls):
        """Get Heroku dyno information"""
        return {
            'dyno': os.environ.get('DYNO', 'unknown'),
            'dyno_ram': os.environ.get('WEB_MEMORY', 'unknown'),
            'port': os.environ.get('PORT', '5000')
        }
    
    @classmethod
    def optimize_for_performance_dyno(cls):
        """Apply optimizations specific to Heroku Performance Dynos"""
        if cls.is_heroku():
            # Set high-performance defaults for Performance-L Dynos
            os.environ.setdefault('MAX_WORKERS', '2000')
            os.environ.setdefault('BATCH_SIZE', '1000')  
            os.environ.setdefault('THREAD_MULTIPLIER', '100')
            os.environ.setdefault('CONNECTION_POOL_SIZE', '500')
            
            print(f"🚀 HEROKU PERFORMANCE DYNO DETECTED - Aplicando configurações ultra-otimizadas:")
            print(f"   • Workers máximos: {cls.ULTRA_SPEED_CONFIG['max_workers']}")
            print(f"   • Batch size: {cls.ULTRA_SPEED_CONFIG['batch_size']}")
            print(f"   • Thread multiplier: {cls.ULTRA_SPEED_CONFIG['thread_multiplier']}")
            print(f"   • Connection pool: {cls.ULTRA_SPEED_CONFIG['connection_pool_size']}")
            
            return cls.ULTRA_SPEED_CONFIG
        
        return None

# Auto-apply optimizations on import
if HerokuConfig.is_heroku():
    HerokuConfig.optimize_for_performance_dyno()