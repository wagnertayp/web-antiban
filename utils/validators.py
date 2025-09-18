import re
import logging
from typing import List, Dict, Tuple, TYPE_CHECKING

# Import WhatsAppBusinessAPI only for type hints to avoid circular imports
if TYPE_CHECKING:
    from services.whatsapp_business_api import WhatsAppBusinessAPI

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF format and checksum"""
    # Remove non-numeric characters
    cpf = re.sub(r'\D', '', cpf)
    
    # Check if it has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate first verification digit
    sum1 = 0
    for i in range(9):
        sum1 += int(cpf[i]) * (10 - i)
    
    remainder1 = sum1 % 11
    digit1 = 0 if remainder1 < 2 else 11 - remainder1
    
    if int(cpf[9]) != digit1:
        return False
    
    # Calculate second verification digit
    sum2 = 0
    for i in range(10):
        sum2 += int(cpf[i]) * (11 - i)
    
    remainder2 = sum2 % 11
    digit2 = 0 if remainder2 < 2 else 11 - remainder2
    
    if int(cpf[10]) != digit2:
        return False
    
    return True

def format_phone_number(phone: str) -> str:
    """Format Brazilian phone number for Z-API (with country code 55)"""
    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    
    # Remove leading zero from area code if present
    if len(phone) == 11 and phone.startswith('0'):
        phone = phone[1:]
    
    # Ensure we have 11 digits for mobile (DDD + 9 + 8 digits)
    if len(phone) == 10:
        # Add digit 9 for mobile numbers if missing
        if phone[2] in '6789':  # Mobile number indicators
            phone = phone[:2] + '9' + phone[2:]
    
    # Add country code 55 if not present
    if len(phone) == 11 and not phone.startswith('55'):
        phone = '55' + phone
    
    return phone

def parse_leads(leads_text: str) -> Tuple[List[Dict], List[str]]:
    """Parse leads from text format: numero,nome,CPF"""
    leads = []
    errors = []
    
    lines = leads_text.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        parts = [part.strip() for part in line.split(',')]
        
        if len(parts) != 3:
            errors.append(f"Linha {line_num}: Formato inválido. Use: numero,nome,CPF")
            continue
        
        numero, nome, cpf = parts
        
        # Validate phone number
        if not numero:
            errors.append(f"Linha {line_num}: Número de telefone é obrigatório")
            continue
        
        formatted_phone = format_phone_number(numero)
        if len(formatted_phone) < 10:
            errors.append(f"Linha {line_num}: Número de telefone inválido: {numero}")
            continue
        
        # Validate name
        if not nome:
            errors.append(f"Linha {line_num}: Nome é obrigatório")
            continue
        
        # Validate CPF
        if not validate_cpf(cpf):
            errors.append(f"Linha {line_num}: CPF inválido: {cpf}")
            continue
        
        # Format CPF
        cpf_clean = re.sub(r'\D', '', cpf)
        cpf_formatted = f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
        
        leads.append({
            'numero': formatted_phone,
            'nome': nome,
            'cpf': cpf_formatted
        })
    
    return leads, errors


def parse_leads_with_whatsapp_verification(
    leads_text: str, 
    whatsapp_service: 'WhatsAppBusinessAPI'
) -> Dict:
    """
    Parse leads from text format and verify WhatsApp availability.
    
    Baseada na função parse_leads existente, mas adiciona verificação de WhatsApp
    para filtrar apenas números com WhatsApp ativo.
    
    Args:
        leads_text (str): Texto com leads no formato: numero,nome,CPF
        whatsapp_service (WhatsAppBusinessAPI): Instância do serviço WhatsApp
        
    Returns:
        Dict: {
            'valid_leads': [leads com WhatsApp ativo],
            'validation_errors': [erros de formato dos leads],
            'whatsapp_verification': {
                'total_numbers_checked': int,
                'numbers_removed': int,
                'numbers_without_whatsapp': [lista dos números removidos],
                'verification_errors': [erros técnicos durante verificação]
            }
        }
    """
    logging.info("🚀 INICIANDO PARSE DE LEADS COM VERIFICAÇÃO WHATSAPP")
    
    # 1. Primeiro, parsear os leads usando a lógica existente
    logging.info("📋 Parseando leads usando lógica existente...")
    parsed_leads, validation_errors = parse_leads(leads_text)
    
    logging.info(f"✅ Parse inicial: {len(parsed_leads)} leads válidos, {len(validation_errors)} erros de validação")
    
    # 2. Inicializar estrutura de retorno
    result = {
        'valid_leads': [],
        'validation_errors': validation_errors,
        'whatsapp_verification': {
            'total_numbers_checked': 0,
            'numbers_removed': 0,
            'numbers_without_whatsapp': [],
            'verification_errors': []
        }
    }
    
    # 3. Se não há leads válidos para verificar, retornar early
    if not parsed_leads:
        logging.warning("⚠️ Nenhum lead válido encontrado para verificação WhatsApp")
        return result
    
    # 4. Verificar se o serviço WhatsApp está configurado
    if not whatsapp_service or not whatsapp_service.is_configured():
        logging.warning("⚠️ WhatsApp Business API não configurada - retornando leads sem verificação")
        result['valid_leads'] = parsed_leads
        result['whatsapp_verification']['verification_errors'].append(
            "WhatsApp Business API não configurada - verificação ignorada"
        )
        return result
    
    # 5. Extrair números para verificação
    phone_numbers = [lead['numero'] for lead in parsed_leads]
    
    logging.info(f"🔍 Verificando {len(phone_numbers)} números no WhatsApp...")
    
    # 6. Aplicar rate limiting durante verificação (usar delay padrão)
    try:
        verification_result = whatsapp_service.verify_whatsapp_numbers(
            phone_numbers, 
            rate_limit_delay=0.5  # Usar delay padrão conforme especificado
        )
        
        logging.info(f"✅ Verificação WhatsApp concluída")
        logging.info(f"📊 Resultado: {len(verification_result.get('valid_numbers', []))} válidos, "
                    f"{len(verification_result.get('invalid_numbers', []))} inválidos")
        
        # 7. Processar resultados da verificação
        valid_numbers = set(verification_result.get('valid_numbers', []))
        invalid_numbers = verification_result.get('invalid_numbers', [])
        verification_errors = verification_result.get('errors', [])
        
        # 8. Filtrar leads baseado nos números válidos no WhatsApp
        # Preservar informações de nome e CPF dos leads que passaram na verificação
        filtered_leads = []
        numbers_without_whatsapp = []
        
        for lead in parsed_leads:
            if lead['numero'] in valid_numbers:
                filtered_leads.append(lead)
                logging.debug(f"✅ Lead mantido: {lead['nome']} - {lead['numero']}")
            else:
                # Preservar informações do lead removido
                numbers_without_whatsapp.append({
                    'numero': lead['numero'],
                    'nome': lead['nome'],
                    'cpf': lead['cpf']
                })
                logging.debug(f"❌ Lead removido (sem WhatsApp): {lead['nome']} - {lead['numero']}")
        
        # 9. Atualizar estrutura de retorno
        result['valid_leads'] = filtered_leads
        result['whatsapp_verification']['total_numbers_checked'] = verification_result.get('total_checked', len(phone_numbers))
        result['whatsapp_verification']['numbers_removed'] = len(invalid_numbers)
        result['whatsapp_verification']['numbers_without_whatsapp'] = numbers_without_whatsapp
        result['whatsapp_verification']['verification_errors'] = verification_errors
        
        # 10. Logs detalhados do processo
        logging.info(f"🎯 RESULTADO FINAL DA VERIFICAÇÃO:")
        logging.info(f"   📱 Números verificados: {result['whatsapp_verification']['total_numbers_checked']}")
        logging.info(f"   ✅ Leads com WhatsApp: {len(result['valid_leads'])}")
        logging.info(f"   ❌ Números removidos: {result['whatsapp_verification']['numbers_removed']}")
        logging.info(f"   🚨 Erros de verificação: {len(result['whatsapp_verification']['verification_errors'])}")
        
        if verification_errors:
            logging.warning(f"⚠️ Erros encontrados durante verificação: {verification_errors}")
        
        return result
        
    except Exception as e:
        # 11. Error handling para erros técnicos durante verificação
        error_msg = f"Erro técnico durante verificação WhatsApp: {str(e)}"
        logging.error(f"💥 {error_msg}")
        
        # Em caso de erro técnico, retornar leads originais com aviso
        result['valid_leads'] = parsed_leads
        result['whatsapp_verification']['verification_errors'].append(error_msg)
        result['whatsapp_verification']['total_numbers_checked'] = len(phone_numbers)
        
        return result
