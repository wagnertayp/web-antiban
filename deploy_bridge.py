"""
🚀 DEPLOY BRIDGE - Script para deployar a ponte de webhook
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

def deploy_to_service(service_name="railway"):
    """Deploy da bridge para serviço com suporte a mTLS"""
    
    # Configurações para diferentes serviços
    services = {
        "railway": {
            "info": "Railway.app - Suporte nativo a mTLS",
            "docs": "https://railway.app/",
            "deploy_command": "railway up"
        },
        "render": {
            "info": "Render.com - SSL/TLS avançado",
            "docs": "https://render.com/",
            "deploy_command": "render deploy"
        },
        "fly": {
            "info": "Fly.io - Configuração completa de TLS",
            "docs": "https://fly.io/",
            "deploy_command": "flyctl deploy"
        }
    }
    
    if service_name in services:
        service = services[service_name]
        logging.info(f"🚀 DEPLOY TARGET: {service['info']}")
        logging.info(f"📖 Docs: {service['docs']}")
        logging.info(f"⚡ Command: {service['deploy_command']}")
        return service
    else:
        logging.warning(f"❌ Serviço {service_name} não configurado")
        return None

def test_bridge_locally():
    """Testa a bridge localmente"""
    try:
        from webhook_bridge import create_bridge_app
        
        app = create_bridge_app()
        
        # Teste de verificação
        with app.test_client() as client:
            response = client.get('/webhook?hub.mode=subscribe&hub.verify_token=webhook_verify_token_12345_dev_only&hub.challenge=test123')
            
            if response.status_code == 200 and response.data.decode() == 'test123':
                logging.info("✅ BRIDGE LOCAL TEST PASSED")
                return True
            else:
                logging.error(f"❌ BRIDGE LOCAL TEST FAILED - Status: {response.status_code}")
                return False
                
    except Exception as e:
        logging.error(f"❌ LOCAL TEST ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("🌉 WEBHOOK BRIDGE DEPLOYMENT")
    print("=" * 50)
    
    # Teste local
    if test_bridge_locally():
        print("✅ Local test passed")
    else:
        print("❌ Local test failed")
        
    # Opções de deploy
    print("\n🚀 DEPLOY OPTIONS:")
    deploy_to_service("railway")
    deploy_to_service("render")
    deploy_to_service("fly")