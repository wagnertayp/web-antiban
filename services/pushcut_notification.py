"""
Serviço para enviar notificações via Pushcut quando novos clientes entrarem em contato
"""
import logging
import requests
from typing import Optional, Dict, Any


class PushcutNotificationService:
    """Serviço para enviar notificações via Pushcut"""
    
    def __init__(self):
        # URL do Pushcut fornecida pelo usuário
        self.pushcut_url = "https://api.pushcut.io/CwRJR0BYsyJYezzN-no_e/notifications/MinhaNotifica%C3%A7%C3%A3o"
        
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
            # Formatar número de telefone para exibição
            formatted_phone = self._format_phone_number(phone_number)
            
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
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"🔔 Notificação Pushcut enviada com sucesso para novo cliente {formatted_phone}")
                return True
            else:
                logging.error(f"❌ Erro ao enviar notificação Pushcut: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Erro de conexão ao enviar notificação Pushcut: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"❌ Erro geral ao enviar notificação Pushcut: {str(e)}")
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
            logging.error(f"❌ Erro no teste de conexão Pushcut: {str(e)}")
            return False


# Instância global do serviço
pushcut_service = PushcutNotificationService()


def send_new_client_notification(phone_number: str, message_content: str, client_name: Optional[str] = None) -> bool:
    """Função de conveniência para enviar notificação de novo cliente"""
    return pushcut_service.send_new_client_notification(phone_number, message_content, client_name)


def test_pushcut_connection() -> bool:
    """Função de conveniência para testar conexão"""
    return pushcut_service.test_connection()