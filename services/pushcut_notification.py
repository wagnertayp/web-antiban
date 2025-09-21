"""
Serviço para enviar notificações via Pushcut quando novos clientes entrarem em contato
"""
import logging
import requests
from typing import Optional, Dict, Any


class PushcutNotificationService:
    """Serviço para enviar notificações via Pushcut"""
    
    def __init__(self):
        import os
        
        # Buscar configurações do ambiente
        pushcut_api_key = os.environ.get('PUSHCUT_API_KEY')
        pushcut_notification_name = os.environ.get('PUSHCUT_NOTIFICATION_NAME', 'MinhaNotifica%C3%A7%C3%A3o')
        
        if not pushcut_api_key:
            logging.warning("⚠️ PUSHCUT_API_KEY não configurada - notificações desabilitadas")
            self.pushcut_url = None
            self.enabled = False
        else:
            # Construir URL segura
            self.pushcut_url = f"https://api.pushcut.io/{pushcut_api_key}/notifications/{pushcut_notification_name}"
            self.enabled = True
            logging.info("✅ Serviço Pushcut inicializado com sucesso")
        
    def send_new_client_notification(self, phone_number: str, message_content: str, client_name: Optional[str] = None) -> bool:
        """
        Envia notificação de novo cliente no Pushcut
        
        Args:
            phone_number: Número do telefone do cliente
            message_content: Conteúdo da primeira mensagem
            client_name: Nome do cliente (se disponível)
        
        Returns:
            bool: True se a notificação foi enviada com sucesso
        """
        try:
            # Verificar se o serviço está habilitado
            if not self.enabled or not self.pushcut_url:
                logging.warning("🔕 Pushcut não configurado - notificação ignorada")
                return False
            
            # Formatar número de telefone para exibição (mascarar para logs)
            formatted_phone = self._format_phone_number(phone_number)
            masked_phone = self._mask_phone_number(formatted_phone)
            
            # Preparar título e texto da notificação
            title = "🎯 Novo Cliente WhatsApp!"
            
            if client_name:
                text = f"📱 Cliente: {client_name}\n📞 Telefone: {formatted_phone}\n💬 Mensagem: {message_content[:100]}{'...' if len(message_content) > 100 else ''}"
            else:
                text = f"📞 Telefone: {formatted_phone}\n💬 Mensagem: {message_content[:100]}{'...' if len(message_content) > 100 else ''}"
            
            # Payload para o Pushcut
            payload = {
                "title": title,
                "text": text,
                "sound": "chime",
                "badge": 1,
                "input": {
                    "phone": phone_number,
                    "message": message_content,
                    "timestamp": self._get_current_timestamp()
                }
            }
            
            # Enviar notificação via POST
            response = requests.post(
                self.pushcut_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'WhatsApp-Business-Automation/1.0'
                },
                timeout=3  # Reduzir timeout para não bloquear o fluxo
            )
            
            if response.status_code == 200:
                logging.info(f"🔔 Notificação Pushcut enviada com sucesso para novo cliente {masked_phone}")
                return True
            else:
                logging.error(f"❌ Erro ao enviar notificação Pushcut: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            # SEGURANÇA: Não logar str(e) pois pode conter a API key na URL
            logging.error(f"❌ Erro de conexão ao enviar notificação Pushcut: Falha na requisição HTTP")
            return False
        except Exception as e:
            # SEGURANÇA: Log genérico para não vazar informações sensíveis
            logging.error(f"❌ Erro geral ao enviar notificação Pushcut: {type(e).__name__}")
            return False
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Formata número de telefone para exibição"""
        try:
            # Remove caracteres não numéricos
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # Formato brasileiro: +55 (xx) 9xxxx-xxxx
            if len(clean_phone) >= 13 and clean_phone.startswith('55'):
                # +55 61 99999-9999
                country = clean_phone[:2]
                area = clean_phone[2:4]
                part1 = clean_phone[4:9]
                part2 = clean_phone[9:]
                return f"+{country} ({area}) {part1}-{part2}"
            elif len(clean_phone) >= 11:
                # (61) 99999-9999
                area = clean_phone[:2]
                part1 = clean_phone[2:7]
                part2 = clean_phone[7:]
                return f"({area}) {part1}-{part2}"
            else:
                return phone_number
        except Exception:
            return phone_number
    
    def _mask_phone_number(self, formatted_phone: str) -> str:
        """Mascara número de telefone para logs de segurança"""
        try:
            # +55 (61) 99999-9999 -> +55 (XX) *****-9999
            import re
            masked = re.sub(r'\(\d{2}\)', '(XX)', formatted_phone)
            masked = re.sub(r'\d{5}-(\d{4})', r'*****-\1', masked)
            return masked
        except Exception:
            return "***MASKED***"
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual em formato legível"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def test_connection(self) -> bool:
        """Testa conexão com o Pushcut enviando uma notificação de teste"""
        try:
            test_payload = {
                "title": "🧪 Teste de Conexão",
                "text": "Sistema WhatsApp conectado com sucesso ao Pushcut!",
                "sound": "default"
            }
            
            response = requests.post(
                self.pushcut_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                logging.info("✅ Teste de conexão Pushcut realizado com sucesso")
            else:
                logging.error(f"❌ Falha no teste de conexão Pushcut: {response.status_code}")
                
            return success
            
        except Exception as e:
            # SEGURANÇA: Não logar str(e) pois pode conter a API key na URL
            logging.error(f"❌ Erro no teste de conexão Pushcut: {type(e).__name__}")
            return False


# Instância global do serviço
pushcut_service = PushcutNotificationService()


def send_new_client_notification(phone_number: str, message_content: str, client_name: Optional[str] = None) -> bool:
    """Função de conveniência para enviar notificação de novo cliente"""
    return pushcut_service.send_new_client_notification(phone_number, message_content, client_name)


def test_pushcut_connection() -> bool:
    """Função de conveniência para testar conexão"""
    return pushcut_service.test_connection()