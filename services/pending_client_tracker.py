"""
Serviço para rastreamento automático de clientes PENDING
Verifica status na API Recoverify e envia follow-ups automáticos
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import List, Optional
from app import app, db
from models import PendingClient, Contact, Conversation, brasilia_now

class PendingClientTracker:
    """Serviço para rastrear e fazer follow-up de clientes PENDING"""
    
    def __init__(self, whatsapp_api):
        self.whatsapp_api = whatsapp_api
    
    def check_and_update_all_pending_clients(self) -> int:
        """
        Verificar todos os clientes PENDING na API Recoverify
        Retorna número de clientes processados
        """
        try:
            with app.app_context():
                # Buscar clientes que precisam ser verificados (últimos 5+ minutos)
                clients_to_check = PendingClient.get_clients_for_check()
                
                if not clients_to_check:
                    logging.info("🔍 Nenhum cliente PENDING para verificar no momento")
                    return 0
                
                logging.info(f"🔍 Verificando {len(clients_to_check)} clientes PENDING na API Recoverify")
                
                processed_count = 0
                for client in clients_to_check:
                    try:
                        # Verificar status na API
                        new_status = self._check_client_status_in_api(client.cpf)
                        
                        if new_status:
                            client.update_payment_status(new_status)
                            
                            if new_status == 'APPROVED':
                                logging.info(f"✅ Cliente {client.cpf} mudou para APPROVED - removido do rastreamento")
                            else:
                                logging.info(f"🔄 Cliente {client.cpf} ainda PENDING - continuando rastreamento")
                        else:
                            # Apenas atualizar último check mesmo se API falhou
                            client.last_checked_at = brasilia_now()
                            db.session.commit()
                        
                        processed_count += 1
                        
                    except Exception as e:
                        logging.error(f"Erro ao verificar cliente {client.cpf}: {str(e)}")
                        continue
                
                logging.info(f"✅ Verificação concluída: {processed_count} clientes processados")
                return processed_count
                
        except Exception as e:
            logging.error(f"Erro na verificação de clientes PENDING: {str(e)}")
            return 0
    
    def send_first_followup_messages(self) -> int:
        """
        Enviar primeira mensagem de follow-up para clientes PENDING
        Retorna número de mensagens enviadas
        """
        try:
            with app.app_context():
                # Buscar clientes que ainda não receberam primeira mensagem
                clients_for_followup = PendingClient.get_clients_for_first_followup()
                
                if not clients_for_followup:
                    logging.info("📨 Nenhum cliente precisando de primeira mensagem de follow-up")
                    return 0
                
                logging.info(f"📨 Enviando primeira mensagem de follow-up para {len(clients_for_followup)} clientes")
                
                sent_count = 0
                for client in clients_for_followup:
                    try:
                        success = self._send_first_followup_message(client)
                        if success:
                            client.mark_first_followup_sent()
                            sent_count += 1
                            logging.info(f"✅ Primeira mensagem de follow-up enviada para {client.first_name} ({client.cpf})")
                        else:
                            logging.error(f"❌ Falha ao enviar primeira mensagem para {client.cpf}")
                            
                    except Exception as e:
                        logging.error(f"Erro ao enviar primeira mensagem para {client.cpf}: {str(e)}")
                        continue
                
                logging.info(f"✅ Primeira mensagem de follow-up: {sent_count} enviadas")
                return sent_count
                
        except Exception as e:
            logging.error(f"Erro no envio de primeiras mensagens de follow-up: {str(e)}")
            return 0
    
    def send_daily_followup_messages(self) -> int:
        """
        Enviar mensagem diária (12:00) para clientes PENDING
        Retorna número de mensagens enviadas
        """
        try:
            with app.app_context():
                # Buscar clientes que precisam receber mensagem diária
                clients_for_daily = PendingClient.get_clients_for_daily_followup()
                
                if not clients_for_daily:
                    logging.info("📨 Nenhum cliente precisando de mensagem diária")
                    return 0
                
                logging.info(f"📨 Enviando mensagem diária para {len(clients_for_daily)} clientes")
                
                sent_count = 0
                for client in clients_for_daily:
                    try:
                        success = self._send_daily_followup_message(client)
                        if success:
                            client.mark_daily_followup_sent()
                            sent_count += 1
                            logging.info(f"✅ Mensagem diária enviada para {client.first_name} ({client.cpf})")
                        else:
                            logging.error(f"❌ Falha ao enviar mensagem diária para {client.cpf}")
                            
                    except Exception as e:
                        logging.error(f"Erro ao enviar mensagem diária para {client.cpf}: {str(e)}")
                        continue
                
                logging.info(f"✅ Mensagem diária: {sent_count} enviadas")
                return sent_count
                
        except Exception as e:
            logging.error(f"Erro no envio de mensagens diárias: {str(e)}")
            return 0
    
    def _check_client_status_in_api(self, cpf: str) -> Optional[str]:
        """Verificar status do cliente na API Recoverify"""
        try:
            api_url = f"https://recoveryfy.replit.app/api/v1/cliente/cpf/{cpf}"
            
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair status da última transação
                ultima_transacao = data.get('ultima_transacao', {})
                status = ultima_transacao.get('status', 'PENDING')
                
                logging.debug(f"🔍 Status API para {cpf}: {status}")
                return status
            else:
                logging.warning(f"❌ API Recoverify retornou status {response.status_code} para CPF {cpf}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao consultar API Recoverify para CPF {cpf}: {str(e)}")
            return None
    
    def _send_first_followup_message(self, client: PendingClient) -> bool:
        """Enviar primeira mensagem de follow-up com urgência"""
        try:
            # Criar link de pagamento personalizado
            payment_link = f"https://shopee.acesso.inc/{client.cpf}"
            
            # Mensagem com urgência e primeiro nome
            message = (
                f"Oi {client.first_name}! 👋\n\n"
                f"Vi que você ainda não finalizou o pagamento para garantir sua vaga como entregador da Shopee! 😟\n\n"
                f"⚠️ *ATENÇÃO:* As vagas estão se esgotando rapidamente na sua região!\n\n"
                f"🚨 Não perca essa oportunidade de trabalhar com horário flexível e ganhos de R$ 500-750/dia.\n\n"
                f"Você ainda tem interesse na vaga de entregador? 🤔"
            )
            
            # Enviar mensagem com botão de pagamento
            success, result = self.whatsapp_api.send_interactive_cta_url_message(
                client.phone_number,
                message,
                "💳 Finalizar Pagamento",
                payment_link
            )
            
            if success:
                # Salvar mensagem no histórico da conversa
                self._save_followup_message(client, message + f"\n[Botão: Finalizar Pagamento - {payment_link}]")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Erro ao enviar primeira mensagem de follow-up: {str(e)}")
            return False
    
    def _send_daily_followup_message(self, client: PendingClient) -> bool:
        """Enviar mensagem diária (12:00) mais intensa"""
        try:
            # Criar link de pagamento personalizado
            payment_link = f"https://shopee.acesso.inc/{client.cpf}"
            
            # Mensagem diária mais intensa
            message = (
                f"🚨 *ÚLTIMA OPORTUNIDADE {client.first_name}!*\n\n"
                f"Sua vaga como entregador Shopee está prestes a expirar! ⏰\n\n"
                f"📊 Apenas 24 horas restantes para garantir:\n"
                f"• Horário 100% flexível 🕐\n"
                f"• Ganhos de R$ 500-750 por dia 💰\n"
                f"• Kit EPI completo incluso 🦺\n"
                f"• Treinamento gratuito online 📚\n\n"
                f"⚠️ Se não finalizar hoje, sua vaga será liberada para outro candidato!\n\n"
                f"💳 Finalize agora mesmo:"
            )
            
            # Enviar mensagem com botão de pagamento
            success, result = self.whatsapp_api.send_interactive_cta_url_message(
                client.phone_number,
                message,
                "🚨 FINALIZAR AGORA",
                payment_link
            )
            
            if success:
                # Salvar mensagem no histórico da conversa
                self._save_followup_message(client, message + f"\n[Botão: FINALIZAR AGORA - {payment_link}]")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem diária: {str(e)}")
            return False
    
    def _save_followup_message(self, client: PendingClient, message_content: str):
        """Salvar mensagem de follow-up no histórico da conversa"""
        try:
            # Buscar ou criar contato
            contact = Contact.get_or_create(client.phone_number, client.full_name)
            
            # Buscar ou criar conversa (usar phone_number_id padrão)
            conversation = Conversation.get_or_create(contact.id, self.whatsapp_api.phone_number_id)
            
            # Salvar mensagem no histórico
            from models import ChatMessage
            ChatMessage.create_outbound(conversation.id, message_content)
            
        except Exception as e:
            logging.error(f"Erro ao salvar mensagem de follow-up no histórico: {str(e)}")