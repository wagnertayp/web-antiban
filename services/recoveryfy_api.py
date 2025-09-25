"""
Serviço para integração com a API Recoveryfy
Busca dados de entregadores e clientes
"""
import logging
import requests
import re
from typing import Dict, Any, Optional, Tuple


class RecoveryfyAPI:
    """Cliente para a API Recoveryfy"""
    
    def __init__(self):
        self.base_url = "https://recoveryfy.replit.app/api/v1"
        self.timeout = 30
        
    def _extract_phone_number(self, phone_text: str) -> str:
        """Extrai número de telefone limpo do texto"""
        # Remove todos os caracteres não numéricos
        clean_phone = re.sub(r'\D', '', phone_text)
        
        # Se começar com 55, remove (código do Brasil)
        if clean_phone.startswith('55') and len(clean_phone) > 11:
            clean_phone = clean_phone[2:]
        
        # Garante que tem pelo menos 10 dígitos
        if len(clean_phone) >= 10:
            return clean_phone
        
        return phone_text  # Retorna original se não conseguir limpar
    
    def get_delivery_partner_data(self, phone_number: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Busca dados do entregador na API usando telefone
        
        Args:
            phone_number: Número de telefone do cliente
            
        Returns:
            Tuple[bool, dict]: (success, data)
        """
        try:
            # Extrair e limpar o número de telefone
            clean_phone = self._extract_phone_number(phone_number)
            
            url = f"{self.base_url}/shopee/telefone/{clean_phone}"
            
            logging.info(f"🔍 Buscando dados do entregador na API: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('sucesso') and data.get('total_registros', 0) > 0:
                    logging.info(f"✅ Dados do entregador encontrados: {data.get('total_registros')} registros")
                    return True, data
                else:
                    logging.warning(f"⚠️ Nenhum registro encontrado para telefone {clean_phone}")
                    return False, {"error": "Nenhum registro encontrado"}
            else:
                logging.error(f"❌ Erro na API (status {response.status_code}): {response.text}")
                return False, {"error": f"Erro na API: status {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logging.error(f"⏰ Timeout na API Recoveryfy para telefone {phone_number}")
            return False, {"error": "Timeout na consulta da API"}
        except requests.exceptions.RequestException as e:
            logging.error(f"🌐 Erro de rede na API Recoveryfy: {str(e)}")
            return False, {"error": f"Erro de rede: {str(e)}"}
        except Exception as e:
            logging.error(f"💥 Erro inesperado na API Recoveryfy: {str(e)}")
            return False, {"error": f"Erro interno: {str(e)}"}
    
    def check_client_status(self, cpf: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica status do cliente na API (PENDING vs APPROVED)
        
        Args:
            cpf: CPF do cliente
            
        Returns:
            Tuple[bool, dict]: (success, data)
        """
        try:
            # Limpar CPF (apenas números)
            clean_cpf = re.sub(r'\D', '', cpf)
            
            url = f"{self.base_url}/cliente/cpf/{clean_cpf}"
            
            logging.info(f"🔍 Verificando status do cliente na API: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Status do cliente obtido: {data}")
                return True, data
            else:
                logging.error(f"❌ Erro ao verificar status (status {response.status_code}): {response.text}")
                return False, {"error": f"Erro na API: status {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logging.error(f"⏰ Timeout na verificação de status para CPF {cpf}")
            return False, {"error": "Timeout na consulta da API"}
        except requests.exceptions.RequestException as e:
            logging.error(f"🌐 Erro de rede na verificação de status: {str(e)}")
            return False, {"error": f"Erro de rede: {str(e)}"}
        except Exception as e:
            logging.error(f"💥 Erro inesperado na verificação de status: {str(e)}")
            return False, {"error": f"Erro interno: {str(e)}"}


def get_client_status(phone_number: str = None, cpf: str = None) -> Dict[str, Any]:
    """
    🎯 HELPER CENTRALIZADO - Resolve status do cliente com override persistente
    
    Verifica primeiro o override local (ConversationState), depois consulta API externa.
    
    Args:
        phone_number: Número do telefone para consulta
        cpf: CPF para consulta (opcional)
        
    Returns:
        Dict com status, source, cpf, nome, etc.
    """
    try:
        from models import ConversationState, db
        from datetime import datetime
        
        # 🔍 Primeiro: Verificar override no ConversationState
        if phone_number:
            conv_state = ConversationState.query.filter_by(phone_number=phone_number).first()
            
            if conv_state and conv_state.first_payment_status == 'approved':
                logging.info(f"✅ OVERRIDE: Cliente {phone_number} já tem pagamento APROVADO localmente")
                return {
                    'status': 'APPROVED',
                    'source': 'override',
                    'cpf': conv_state.original_cpf or 'unknown',
                    'nome': 'Cliente Aprovado',
                    'payment_at': conv_state.first_payment_at.isoformat() if conv_state.first_payment_at else None,
                    'override_source': conv_state.payment_source
                }
        
        # 🔍 Segundo: Consultar API externa se não há override
        api = RecoveryfyAPI()
        
        if cpf:
            # Consultar por CPF
            success, data = api.check_client_status(cpf)
            if success and data.get('sucesso'):
                cliente = data.get('cliente', {})
                transacao = data.get('ultima_transacao', {})
                
                status = transacao.get('status', 'PENDING')
                logging.info(f"✅ API: Status do cliente CPF {cpf}: {status}")
                
                return {
                    'status': status,
                    'source': 'api',
                    'cpf': cliente.get('cpf'),
                    'nome': cliente.get('nome'),
                    'telefone': cliente.get('telefone'),
                    'email': cliente.get('email'),
                    'transacao': transacao
                }
        
        elif phone_number:
            # Consultar por telefone (dados de entregador)
            success, data = api.get_delivery_partner_data(phone_number)
            if success and data.get('sucesso'):
                registros = data.get('registros', [])
                if registros:
                    primeiro = registros[0]
                    cpf_encontrado = primeiro.get('cpf')
                    
                    # Buscar status do cliente usando CPF encontrado
                    if cpf_encontrado:
                        return get_client_status(cpf=cpf_encontrado)
        
        # 🔍 Fallback: Status padrão PENDING
        logging.warning(f"⚠️ Status não encontrado para {phone_number or cpf}, assumindo PENDING")
        return {
            'status': 'PENDING',
            'source': 'default',
            'cpf': cpf or 'unknown',
            'nome': 'Cliente',
            'telefone': phone_number
        }
        
    except Exception as e:
        logging.error(f"💥 Erro no get_client_status: {str(e)}")
        return {
            'status': 'PENDING',
            'source': 'error',
            'error': str(e)
        }


def mark_payment_approved(phone_number: str, cpf: str = None, source: str = 'proof') -> bool:
    """
    🎯 Marca pagamento como APROVADO no override local
    
    Args:
        phone_number: Número do telefone
        cpf: CPF do cliente (opcional)
        source: Fonte da aprovação ('proof', 'api')
        
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        from models import ConversationState, db
        from datetime import datetime
        
        # Buscar ou criar ConversationState
        conv_state = ConversationState.query.filter_by(phone_number=phone_number).first()
        
        if not conv_state:
            conv_state = ConversationState(
                phone_number=phone_number,
                current_state='pending_questions',
                ai_enabled=True
            )
            db.session.add(conv_state)
        
        # 🎯 Marcar pagamento como aprovado
        conv_state.first_payment_status = 'approved'
        conv_state.first_payment_at = datetime.now()
        conv_state.payment_source = source
        conv_state.current_state = 'pending_questions'  # Estado para dúvidas/treinamento
        conv_state.ai_enabled = True
        
        if cpf:
            conv_state.original_cpf = cpf
            conv_state.cpf_status = 'APPROVED'
        
        db.session.commit()
        
        logging.info(f"✅ OVERRIDE SALVO: {phone_number} marcado como APPROVED (fonte: {source})")
        return True
        
    except Exception as e:
        logging.error(f"💥 Erro ao marcar pagamento aprovado: {str(e)}")
        db.session.rollback()
        return False