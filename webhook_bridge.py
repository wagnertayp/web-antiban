"""
🌉 WEBHOOK BRIDGE - Solução para contornar mTLS da Meta
Este serviço cria uma ponte entre a Meta e o Replit, resolvendo o problema do mTLS
"""

import os
import logging
import requests
from flask import Flask, request, jsonify

# Configurar logging
logging.basicConfig(level=logging.INFO)

class WebhookBridge:
    """Ponte de webhook que contorna limitações de mTLS"""
    
    def __init__(self):
        self.replit_webhook_url = os.environ.get('REPLIT_WEBHOOK_URL', 
            'https://72b11919-b9c0-4779-8bc7-79c3c90ce16f-00-1mp9eaiqxt8ni.picard.replit.dev/webhook')
        self.verify_token = os.environ.get('WEBHOOK_VERIFY_TOKEN', 'webhook_verify_token_12345_dev_only')
        
    def handle_verification(self, args):
        """Processa verificação do webhook"""
        mode = args.get('hub.mode')
        token = args.get('hub.verify_token')
        challenge = args.get('hub.challenge')
        
        logging.info(f"🔍 BRIDGE VERIFICATION - Mode: {mode}, Token: {token}")
        
        if mode == 'subscribe' and token == self.verify_token and challenge:
            logging.info(f"✅ BRIDGE VERIFICATION SUCCESS - Challenge: {challenge}")
            return challenge
        else:
            logging.error(f"❌ BRIDGE VERIFICATION FAILED")
            return None
            
    def forward_webhook(self, data, headers):
        """Encaminha webhook para o Replit"""
        try:
            # Headers importantes para manter
            forward_headers = {
                'Content-Type': 'application/json',
                'User-Agent': headers.get('User-Agent', 'Meta-Webhook-Bridge'),
                'X-Hub-Signature-256': headers.get('X-Hub-Signature-256', ''),
                'X-Forwarded-For': headers.get('X-Forwarded-For', '')
            }
            
            # Encaminhar para o Replit
            response = requests.post(
                self.replit_webhook_url,
                json=data,
                headers=forward_headers,
                timeout=10
            )
            
            logging.info(f"📨 BRIDGE FORWARD - Status: {response.status_code}")
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"❌ BRIDGE FORWARD ERROR: {str(e)}")
            return False

# Instância global da bridge
webhook_bridge = WebhookBridge()

def create_bridge_app():
    """Cria aplicação Flask para a bridge"""
    app = Flask(__name__)
    
    @app.route('/webhook', methods=['GET', 'POST'])
    def webhook_endpoint():
        """Endpoint principal da bridge"""
        
        if request.method == 'GET':
            # Verificação do webhook
            challenge = webhook_bridge.handle_verification(request.args)
            if challenge:
                return challenge, 200
            else:
                return "Forbidden", 403
                
        elif request.method == 'POST':
            # Encaminhamento do webhook
            try:
                data = request.get_json()
                success = webhook_bridge.forward_webhook(data, request.headers)
                
                if success:
                    return "OK", 200
                else:
                    return "Forward Failed", 500
                    
            except Exception as e:
                logging.error(f"❌ BRIDGE ERROR: {str(e)}")
                return "Internal Server Error", 500
                
        return "Method Not Allowed", 405
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check para monitoramento"""
        return {"status": "ok", "bridge": "active"}, 200
    
    return app

if __name__ == '__main__':
    app = create_bridge_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)