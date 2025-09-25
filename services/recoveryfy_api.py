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