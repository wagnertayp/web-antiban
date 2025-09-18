import os
import logging
import requests
import config  # Import configuration to set environment variables
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import threading
import time
from datetime import datetime
from heroku_config import HerokuConfig

# Global counter for real-time progress tracking
message_counters = {}

# WhatsApp Business API limit - cada número pode enviar máximo 1000 mensagens por disparo
MAX_PER_PHONE = 1000

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database for Heroku optimization
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///whatsapp_sender.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 20,          # Increased for Heroku Performance Dynos
    "max_overflow": 30,       # Allow overflow connections
    "pool_pre_ping": True,    # Test connections before use
    "pool_recycle": 3600,     # Recycle connections every hour
    "connect_args": {
        "connect_timeout": 10,
        "application_name": "whatsapp_bulk_system"
    } if database_url and "postgresql" in database_url else {}
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    import models

    db.create_all()

from services.whatsapp_business_api import WhatsAppBusinessAPI
from services.message_service import MessageService
# from mega_batch_simple import mega_batch  # Temporarily disabled
from webhook_handler import WhatsAppWebhookHandler
# from ultra_mega_batch import ultra_mega_batch  # Temporarily disabled
from utils.validators import validate_cpf, format_phone_number, parse_leads
from template_cloner import TemplateCloner

# Initialize services
whatsapp_service = WhatsAppBusinessAPI()
message_service = MessageService(db, whatsapp_service, app)

# Initialize proxy service with app context
from services.proxy_service import init_proxy_service
proxy_service = init_proxy_service(app, db)

@app.route('/')
def index():
    """Main page with the messaging interface"""
    return render_template('index.html')

@app.route('/admin/sent-numbers')
def admin_sent_numbers():
    """Admin page to view and manage sent numbers"""
    try:
        from models import SentNumber
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Get search parameter
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = SentNumber.query
        
        if search:
            query = query.filter(
                db.or_(
                    SentNumber.phone_number.contains(search),
                    SentNumber.lead_name.contains(search),
                    SentNumber.lead_cpf.contains(search)
                )
            )
        
        # Order by most recent first
        query = query.order_by(SentNumber.sent_at.desc())
        
        # Paginate
        sent_numbers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_sent = SentNumber.query.count()
        
        return render_template('admin_sent_numbers.html', 
                             sent_numbers=sent_numbers,
                             total_sent=total_sent,
                             search=search)
        
    except Exception as e:
        logging.error(f"Error loading admin sent numbers: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/admin/clear-sent-numbers', methods=['POST'])
def clear_sent_numbers():
    """Clear all sent numbers from database"""
    try:
        from models import SentNumber
        
        count = SentNumber.query.count()
        SentNumber.query.delete()
        db.session.commit()
        
        logging.info(f"Cleared {count} sent numbers from database")
        
        return jsonify({
            'success': True,
            'message': f'{count} números removidos do banco de dados'
        })
        
    except Exception as e:
        logging.error(f"Error clearing sent numbers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/remove-sent-number/<int:number_id>', methods=['DELETE'])
def remove_sent_number(number_id):
    """Remove specific sent number from database"""
    try:
        from models import SentNumber
        
        sent_number = SentNumber.query.get_or_404(number_id)
        phone = sent_number.phone_number
        
        db.session.delete(sent_number)
        db.session.commit()
        
        logging.info(f"Removed sent number {phone} from database")
        
        return jsonify({
            'success': True,
            'message': f'Número {phone} removido do banco'
        })
        
    except Exception as e:
        logging.error(f"Error removing sent number: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-business-manager-id', methods=['POST'])
def save_business_manager_id():
    """Salva o último Business Manager ID na sessão"""
    try:
        data = request.get_json()
        business_manager_id = data.get('business_manager_id', '').strip()
        
        if business_manager_id:
            session['last_business_manager_id'] = business_manager_id
            logging.info(f"Business Manager ID salvo na sessão: {business_manager_id}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Business Manager ID vazio'}), 400
    
    except Exception as e:
        logging.error(f"Erro ao salvar Business Manager ID: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-business-manager-id', methods=['GET'])
def get_business_manager_id():
    """Retorna o último Business Manager ID da sessão"""
    try:
        last_bm_id = session.get('last_business_manager_id', '')
        return jsonify({'business_manager_id': last_bm_id})
    
    except Exception as e:
        logging.error(f"Erro ao buscar Business Manager ID: {str(e)}")
        return jsonify({'business_manager_id': ''})

@app.route('/api/connect-whatsapp', methods=['POST'])
def connect_whatsapp():
    """Conecta com WhatsApp Business API usando token fornecido"""
    try:
        data = request.get_json()
        access_token = (data.get('access_token') or '').strip()
        business_manager_id = (data.get('business_manager_id') or '').strip()
        proxy_connection = (data.get('proxy_connection') or '').strip()
        
        if not access_token:
            return jsonify({'success': False, 'message': 'Token de acesso é obrigatório'}), 400
        
        # Handle proxy connection if provided
        if proxy_connection:
            try:
                from models import Proxy
                
                # Validate proxy format
                parts = proxy_connection.split(':')
                if len(parts) < 4:
                    return jsonify({'success': False, 'message': 'Formato de proxy inválido. Use: host:port:user:password'}), 400
                
                # Check if proxy already exists, if not add it temporarily
                existing_proxy = Proxy.query.filter_by(proxy_string=proxy_connection).first()
                if not existing_proxy:
                    # Add proxy temporarily for this connection
                    temp_proxy = Proxy()
                    temp_proxy.name = f"Conexão {datetime.utcnow().strftime('%H:%M')}"
                    temp_proxy.proxy_string = proxy_connection
                    temp_proxy.is_active = True
                    
                    db.session.add(temp_proxy)
                    db.session.commit()
                    
                    logging.info(f"Proxy temporária adicionada para conexão: {proxy_connection[:20]}...")
                else:
                    # Activate existing proxy
                    existing_proxy.is_active = True
                    db.session.commit()
                    logging.info(f"Proxy existente ativada: {existing_proxy.name}")
                    
            except Exception as e:
                logging.error(f"Erro ao processar proxy: {str(e)}")
                # Continue without proxy if there's an error
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 1. Descobrir Business Manager ID testando BMs conhecidas
        discovered_bm_id = business_manager_id
        if not discovered_bm_id:
            logging.info("Testando acesso às Business Managers conhecidas...")
            # BMs conhecidas que funcionaram anteriormente
            known_bms = ['1243060407061288', '2089992404820473', '639849885789886', '1523966465251146', '580318035149016']
            
            for bm_id in known_bms:
                try:
                    test_url = f'https://graph.facebook.com/v23.0/{bm_id}/phone_numbers'
                    test_response = requests.get(test_url, headers=headers, timeout=10)
                    
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        phones = test_data.get('data', [])
                        if phones:
                            discovered_bm_id = bm_id
                            logging.info(f"✅ BM ENCONTRADA: {bm_id} com {len(phones)} números")
                            break
                    else:
                        logging.debug(f"BM {bm_id}: Status {test_response.status_code}")
                except Exception as e:
                    logging.debug(f"BM {bm_id}: Erro {e}")
            
            if not discovered_bm_id:
                return jsonify({'success': False, 'message': 'Token não tem acesso a nenhuma Business Manager conhecida'}), 400
        
        # 2. Buscar Phone Numbers
        logging.info(f"Buscando phone numbers da BM {discovered_bm_id}...")
        phones_url = f'https://graph.facebook.com/v23.0/{discovered_bm_id}/phone_numbers'
        phones_response = requests.get(phones_url, headers=headers, timeout=15)
        
        phone_numbers = []
        if phones_response.status_code == 200:
            phones_data = phones_response.json()
            for phone in phones_data.get('data', []):
                phone_numbers.append({
                    'id': phone.get('id'),
                    'display_phone_number': phone.get('display_phone_number'),
                    'quality_rating': phone.get('quality_rating', 'UNKNOWN'),
                    'verified_name': phone.get('verified_name', '')
                })
            logging.info(f"Encontrados {len(phone_numbers)} phone numbers")
        else:
            logging.warning(f"Erro ao buscar phone numbers: {phones_response.status_code}")
        
        # 3. Buscar Templates
        logging.info(f"Buscando templates da BM {discovered_bm_id}...")
        templates_url = f'https://graph.facebook.com/v23.0/{discovered_bm_id}/message_templates'
        templates_response = requests.get(templates_url, headers=headers, timeout=15)
        
        templates = []
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            for template in templates_data.get('data', []):
                if template.get('status') == 'APPROVED':
                    templates.append({
                        'name': template.get('name'),
                        'language': template.get('language'),
                        'category': template.get('category'),
                        'status': template.get('status'),
                        'has_parameters': bool(template.get('components', [])),
                        'has_buttons': any(comp.get('type') == 'BUTTONS' for comp in template.get('components', []))
                    })
            logging.info(f"Encontrados {len(templates)} templates aprovados")
        else:
            logging.warning(f"Erro ao buscar templates: {templates_response.status_code}")
        
        # 4. Salvar dados na sessão E atualizar ambiente automaticamente
        session['whatsapp_connection'] = {
            'access_token': access_token,
            'business_manager_id': discovered_bm_id,
            'connected_at': datetime.utcnow().isoformat()
        }
        session['last_business_manager_id'] = discovered_bm_id
        
        # CRÍTICO: Atualizar variáveis de ambiente para usar o token da interface
        os.environ['WHATSAPP_ACCESS_TOKEN'] = access_token
        logging.info(f"✅ TOKEN ATUALIZADO AUTOMATICAMENTE: {access_token[:50]}...")
        
        # Forçar refresh das credenciais no serviço WhatsApp
        try:
            whatsapp_service._refresh_credentials()
            logging.info("✅ Credenciais WhatsApp Service atualizadas")
        except Exception as e:
            logging.warning(f"Aviso ao atualizar credenciais: {e}")
        
        # 5. Retornar dados da conexão
        connection_data = {
            'business_manager_id': discovered_bm_id,
            'phone_numbers': phone_numbers,
            'templates': templates,
            'connected_at': datetime.utcnow().isoformat()
        }
        
        logging.info(f"🚀 CONEXÃO AUTOMÁTICA COMPLETA - BM: {discovered_bm_id}, Phones: {len(phone_numbers)}, Templates: {len(templates)}")
        logging.info(f"✅ Sistema configurado para usar token da interface automaticamente")
        
        return jsonify({
            'success': True, 
            'message': f'Conectado automaticamente! BM: {discovered_bm_id}, {len(phone_numbers)} phones, {len(templates)} templates',
            'data': connection_data
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Timeout na conexão com WhatsApp API'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Erro de conexão: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Erro ao conectar WhatsApp: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/phone-numbers', methods=['GET'])
def get_phone_numbers():
    """Busca phone numbers da Business Manager especificada ou baseado no token"""
    try:
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not access_token:
            return jsonify({'error': 'Token não configurado'}), 400
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Usar BM ID passado como parâmetro, ou da sessão
        business_manager_id = request.args.get('business_manager_id', '').strip()
        if not business_manager_id:
            business_manager_id = session.get('last_business_manager_id', '')
        
        # Se não tem BM na sessão, tentar descobrir automaticamente
        if not business_manager_id:
            # Descobrir Business Managers disponíveis
            me_url = f'https://graph.facebook.com/v23.0/me?fields=businesses'
            me_response = requests.get(me_url, headers=headers, timeout=10)
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                businesses = me_data.get('businesses', {}).get('data', [])
                
                # Tentar encontrar a BM com mais phone numbers
                best_bm = None
                max_phones = 0
                
                for business in businesses:
                    business_id = business.get('id')
                    
                    # Buscar phone numbers desta BM
                    phones_url = f'https://graph.facebook.com/v23.0/{business_id}/phone_numbers'
                    phones_response = requests.get(phones_url, headers=headers, timeout=10)
                    
                    if phones_response.status_code == 200:
                        phones_data = phones_response.json()
                        phones = phones_data.get('data', [])
                        phone_count = len(phones)
                        
                        if phone_count > max_phones:
                            max_phones = phone_count
                            best_bm = business_id
                
                if best_bm:
                    business_manager_id = best_bm
                    session['last_business_manager_id'] = business_manager_id
                    logging.info(f"BM descoberta automaticamente: {business_manager_id}")
        
        # Agora buscar phone numbers da BM
        if business_manager_id:
            phones_url = f'https://graph.facebook.com/v23.0/{business_manager_id}/phone_numbers'
            phones_response = requests.get(phones_url, headers=headers, timeout=10)
            
            if phones_response.status_code == 200:
                phones_data = phones_response.json()
                phones = phones_data.get('data', [])
                
                # Formatar phone numbers para o dropdown
                formatted_phones = []
                for phone in phones:
                    quality_icon = "🟢" if phone.get('quality_rating') == 'GREEN' else ("🟡" if phone.get('quality_rating') == 'RED' else "⚪")
                    formatted_phones.append({
                        'id': phone.get('id'),
                        'display_name': f"{quality_icon} {phone.get('display_phone_number', 'N/A')} - {phone.get('verified_name', 'N/A')}",
                        'phone_number': phone.get('display_phone_number', 'N/A'),
                        'quality': phone.get('quality_rating', 'UNKNOWN'),
                        'name': phone.get('verified_name', 'N/A')
                    })
                
                logging.info(f"Carregados {len(formatted_phones)} phone numbers da BM {business_manager_id}")
                
                return jsonify({
                    'phone_numbers': formatted_phones,
                    'business_manager_id': business_manager_id,
                    'total_phones': len(formatted_phones)
                })
            else:
                logging.error(f"Erro ao buscar phones da BM {business_manager_id}: {phones_response.text}")
                return jsonify({'error': f'Erro ao buscar números da BM {business_manager_id}'}), 400
        
        return jsonify({'error': 'Business Manager ID não encontrado'}), 400
        
    except Exception as e:
        logging.error(f"Erro ao buscar phone numbers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/discover-phones', methods=['POST'])
def discover_phones():
    """Descobre automaticamente Business Manager ID e Phone Numbers baseado no token"""
    try:
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not access_token:
            return jsonify({'success': False, 'error': 'Token não configurado'})
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Descobrir Business Managers disponíveis
        me_url = f'https://graph.facebook.com/v23.0/me?fields=businesses'
        me_response = requests.get(me_url, headers=headers, timeout=10)
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            businesses = me_data.get('businesses', {}).get('data', [])
            
            # Tentar encontrar a BM com mais phone numbers
            best_bm = None
            max_phones = 0
            
            for business in businesses:
                business_id = business.get('id')
                
                # Buscar phone numbers desta BM
                phones_url = f'https://graph.facebook.com/v23.0/{business_id}/phone_numbers'
                phones_response = requests.get(phones_url, headers=headers, timeout=10)
                
                if phones_response.status_code == 200:
                    phones_data = phones_response.json()
                    phones = phones_data.get('data', [])
                    phone_count = len(phones)
                    
                    logging.info(f"BM {business_id}: {phone_count} phone numbers encontrados")
                    
                    if phone_count > max_phones:
                        max_phones = phone_count
                        best_bm = {
                            'id': business_id,
                            'name': business.get('name', 'N/A'),
                            'phone_count': phone_count,
                            'phones': phones
                        }
            
            if best_bm and best_bm['phone_count'] > 0:
                # Salvar na sessão
                session['last_business_manager_id'] = best_bm['id']
                
                # Forçar refresh dos dados na service
                whatsapp_service._refresh_credentials()
                
                logging.info(f"Descoberta BM com mais números: {best_bm['id']} com {best_bm['phone_count']} phone numbers")
                
                return jsonify({
                    'success': True,
                    'business_manager_id': best_bm['id'],
                    'business_manager_name': best_bm['name'],
                    'phone_count': best_bm['phone_count'],
                    'message': f"Descobertos {best_bm['phone_count']} números na Business Manager {best_bm['id']}"
                })
        
        return jsonify({'success': False, 'error': 'Não foi possível descobrir automaticamente'})
        
    except Exception as e:
        logging.error(f"Erro ao descobrir phone numbers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validate-leads', methods=['POST'])
def validate_leads():
    """Validate leads format and return parsed data - NO DATABASE"""
    try:
        data = request.get_json()
        
        if not data:
            logging.error("No JSON data received")
            return jsonify({'error': 'Nenhum dado recebido'}), 400
            
        leads_text = data.get('leads', '').strip()
        
        if not leads_text:
            logging.error("Empty leads text")
            return jsonify({'error': 'Lista de leads não pode estar vazia'}), 400
        
        logging.info(f"Processing {len(leads_text.split())} lines of leads data")
        
        # Parse leads from input (sem filtro de banco)
        leads, errors = parse_leads(leads_text)
        
        # Summary simples sem banco de dados
        summary_message = f"✅ {len(leads)} leads válidos prontos para envio."
        
        logging.info(f"VALIDAÇÃO LEADS: {len(leads)} leads válidos, {len(errors)} erros encontrados")
        
        return jsonify({
            'leads': leads,
            'errors': errors,
            'total_valid': len(leads),
            'total_errors': len(errors),
            'original_count': len(leads) + len(errors),
            'filtered_count': 0,
            'already_sent': [],
            'summary': summary_message
        })
    
    except Exception as e:
        logging.error(f"Error validating leads: {str(e)}")
        import traceback
        logging.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/api/preview-message', methods=['POST'])
def preview_message():
    """Preview message with variable substitution"""
    try:
        data = request.get_json()
        template = data.get('template', '')
        sample_lead = data.get('sample_lead', {})
        
        if not template:
            return jsonify({'error': 'Template não pode estar vazio'}), 400
        
        # Replace variables in template
        preview = template
        preview = preview.replace('{nome}', sample_lead.get('nome', '[NOME]'))
        preview = preview.replace('{cpf}', sample_lead.get('cpf', '[CPF]'))
        preview = preview.replace('{numero}', sample_lead.get('numero', '[NUMERO]'))
        
        return jsonify({'preview': preview})
    
    except Exception as e:
        logging.error(f"Error previewing message: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/send-messages', methods=['POST'])
def send_messages():
    """Start bulk message sending process"""
    try:
        data = request.get_json()
        leads = data.get('leads', [])
        template_name = data.get('template_name', '')
        buttons = data.get('buttons', [])
        phone_number_id = data.get('phone_number_id', '')
        
        if not leads:
            return jsonify({'error': 'Nenhum lead válido fornecido'}), 400
        
        # Aplicar limite de 1000 mensagens por número
        if len(leads) > MAX_PER_PHONE:
            return jsonify({
                'error': f'Máximo de {MAX_PER_PHONE} mensagens por número. Lista contém {len(leads)} leads. Use o modo Smart Distribution para listas maiores.'
            }), 400
        
        if not template_name:
            return jsonify({'error': 'Nome do template é obrigatório'}), 400
            
        if not phone_number_id:
            return jsonify({'error': 'Phone Number ID é obrigatório'}), 400
        
        # Validate WhatsApp Business API configuration
        if not whatsapp_service.is_configured():
            return jsonify({'error': 'WhatsApp Business API não configurada. Verifique a variável WHATSAPP_ACCESS_TOKEN'}), 400
        
        # Set the phone number ID for this request
        whatsapp_service.set_phone_number_id(phone_number_id)
        
        # Send messages directly without campaign system
        def send_messages_async():
            with app.app_context():
                success_count = 0
                error_count = 0
                
                for lead in leads:
                    try:
                        # Send message to each lead (auto-detect language)
                        result = whatsapp_service.send_template_message(
                            lead['numero'], template_name, [lead['cpf'], lead['nome']]
                        )
                        if result['success']:
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        logging.error(f"Error sending message to {lead['numero']}: {str(e)}")
                
                logging.info(f"Bulk sending completed: {success_count} success, {error_count} errors")
        
        thread = threading.Thread(target=send_messages_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Envio de mensagens iniciado',
            'total_leads': len(leads)
        })
    
    except Exception as e:
        logging.error(f"Error starting message campaign: {str(e)}")
        return jsonify({'error': 'Erro ao iniciar campanha de mensagens'}), 500

@app.route('/api/send-instant', methods=['POST'])
def send_instant():
    """Send messages instantly without database storage"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não recebidos'}), 400
            
        leads_input = data.get('leads', [])
        template_name = data.get('template_name', '').strip()
        phone_number_id = data.get('phone_number_id', '').strip()
        
        # Initialize leads variable
        leads = []
        parse_errors = []
        
        # Parse leads based on input type
        if isinstance(leads_input, str) and leads_input.strip():
            # Input is a string - parse it
            from utils.validators import parse_leads
            leads, parse_errors = parse_leads(leads_input.strip())
            if parse_errors:
                return jsonify({'error': f'Erros no parsing dos leads: {"; ".join(parse_errors)}'}), 400
        elif isinstance(leads_input, list):
            # Input is already a list - validate it
            leads = leads_input
        else:
            # Invalid input type
            return jsonify({'error': 'Formato de leads inválido. Esperado: string ou lista'}), 400
        
        # Final validation of leads
        if not leads or len(leads) == 0:
            return jsonify({'error': 'Nenhum lead válido fornecido'}), 400
        
        # Aplicar limite de 1000 mensagens por número
        if len(leads) > MAX_PER_PHONE:
            return jsonify({
                'error': f'Máximo de {MAX_PER_PHONE} mensagens por número. Lista contém {len(leads)} leads. Use o modo Smart Distribution para listas maiores.'
            }), 400
        
        if not template_name:
            return jsonify({'error': 'Nome do template é obrigatório'}), 400
            
        if not phone_number_id:
            return jsonify({'error': 'Phone Number ID é obrigatório'}), 400
        
        # Validate WhatsApp Business API configuration
        if not whatsapp_service.is_configured():
            return jsonify({'error': 'WhatsApp Business API não configurada'}), 400
        
        # Set the phone number ID for this request
        whatsapp_service.set_phone_number_id(phone_number_id)
        
        # Send messages with auto-retry and resumption system
        def send_instant_async():
            import time
            import gc
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            total_leads = len(leads)
            batch_size = 50   # Smaller batches for faster processing
            batch_delay = 0.1   # Minimal delay between batches for instant start
            max_workers = 20  # More concurrent threads per batch
            max_retries = 3   # Maximum retry attempts per batch
            
            total_success = 0
            total_errors = 0
            
            logging.info(f"AUTO-RETRY BATCH PROCESSING: {total_leads} leads in batches of {batch_size}")
            
            def send_single_message_with_retry(lead_data, retry_count=0):
                idx, lead = lead_data
                max_single_retries = 2  # Retry individual messages up to 2 times
                
                for attempt in range(max_single_retries + 1):
                    try:
                        phone_number = lead.get('numero', '').strip()
                        customer_name = lead.get('nome', 'Cliente').strip()
                        customer_cpf = lead.get('cpf', 'N/A').strip()
                        
                        # Format phone number
                        if phone_number.startswith('55'):
                            formatted_phone = '+' + phone_number
                        elif not phone_number.startswith('+'):
                            formatted_phone = '+55' + phone_number
                        else:
                            formatted_phone = phone_number
                        
                        # ENVIAR APENAS TEMPLATES APROVADOS - SEM FALLBACK
                        # Usar auto-detecção de linguagem
                        success, response = whatsapp_service.send_template_message(
                            formatted_phone, template_name, 'en',  # Language code will be auto-detected
                            [customer_cpf, customer_name]  # {{1}} = CPF, {{2}} = Nome
                        )
                        
                        if success:
                            if attempt > 0:
                                logging.info(f"RETRY SUCCESS {idx+1} (attempt {attempt+1}): {customer_name} - {formatted_phone}")
                            else:
                                logging.info(f"AUTO-RETRY SUCCESS {idx+1}: {customer_name} - {formatted_phone}")
                            return True
                        else:
                            # Fix error handling for both dict and string responses
                            error_msg = 'Unknown error'
                            if isinstance(response, dict):
                                error_msg = response.get('error', 'Unknown error')
                                if isinstance(error_msg, dict):
                                    error_msg = error_msg.get('message', 'Unknown error')
                            elif isinstance(response, str):
                                error_msg = response
                            else:
                                error_msg = str(response)
                            
                            if attempt < max_single_retries:
                                logging.warning(f"RETRY ATTEMPT {attempt+1} for {idx+1}: {customer_name} - {error_msg}")
                                time.sleep(0.1)  # Minimal wait before retry for instant feedback
                            else:
                                logging.error(f"AUTO-RETRY ERROR {idx+1} (final attempt): {customer_name} - {error_msg}")
                            
                    except Exception as e:
                        if attempt < max_single_retries:
                            logging.warning(f"RETRY EXCEPTION {idx+1} attempt {attempt+1}: {str(e)}")
                            time.sleep(1)  # Wait 1 second before retry
                        else:
                            logging.error(f"AUTO-RETRY EXCEPTION {idx+1} (final attempt): {str(e)}")
                
                return False
            
            # Process leads in batches with retry capability
            batch_num = 0
            while batch_num < total_leads:
                batch_leads = leads[batch_num:batch_num + batch_size]
                current_batch = (batch_num // batch_size) + 1
                total_batches = (total_leads + batch_size - 1) // batch_size
                
                batch_success = 0
                batch_errors = 0
                retry_attempt = 0
                
                while retry_attempt <= max_retries:
                    try:
                        if retry_attempt > 0:
                            logging.info(f"RETRYING BATCH {current_batch}/{total_batches} (attempt {retry_attempt+1}): {len(batch_leads)} leads")
                        else:
                            logging.info(f"AUTO-RETRY BATCH {current_batch}/{total_batches}: {len(batch_leads)} leads")
                        
                        # Process current batch with high parallelism
                        with ThreadPoolExecutor(max_workers=max_workers) as executor:
                            futures = [executor.submit(send_single_message_with_retry, (batch_num + idx, lead)) 
                                      for idx, lead in enumerate(batch_leads)]
                            
                            batch_success = 0
                            batch_errors = 0
                            for future in as_completed(futures):
                                try:
                                    result = future.result(timeout=30)  # 30 second timeout per message
                                    if result:
                                        batch_success += 1
                                    else:
                                        batch_errors += 1
                                except Exception as e:
                                    batch_errors += 1
                                    logging.error(f"Future exception: {str(e)}")
                        
                        # Batch completed successfully, break retry loop
                        break
                        
                    except Exception as e:
                        retry_attempt += 1
                        if retry_attempt <= max_retries:
                            logging.warning(f"BATCH {current_batch} CONNECTION ERROR, retrying in 1 second... (attempt {retry_attempt+1})")
                            time.sleep(1)
                        else:
                            logging.error(f"BATCH {current_batch} FAILED after {max_retries+1} attempts: {str(e)}")
                            batch_errors = len(batch_leads)  # Mark all as errors
                            break
                
                total_success += batch_success
                total_errors += batch_errors
                
                progress_percent = int((total_success + total_errors) * 100 / total_leads)
                logging.info(f"AUTO-RETRY BATCH {current_batch} COMPLETE: {batch_success} success, {batch_errors} errors")
                logging.info(f"AUTO-RETRY PROGRESS: {total_success} success, {total_errors} errors, {progress_percent}% ({total_success + total_errors}/{total_leads})")
                
                # Quick memory cleanup
                gc.collect()
                
                # Move to next batch
                batch_num += batch_size
                
                # Minimal wait between batches
                if batch_num < total_leads:
                    time.sleep(batch_delay)
            
            logging.info(f"AUTO-RETRY COMPLETE: {total_success} success, {total_errors} errors out of {total_leads} total")
            if total_leads > 0:
                logging.info(f"FINAL SUCCESS RATE: {int(total_success * 100 / total_leads)}%")
        
        # Start instant sending in background
        thread = threading.Thread(target=send_instant_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Envio instantâneo iniciado',
            'total_leads': len(leads),
            'mode': 'instant'
        })
    
    except Exception as e:
        logging.error(f"Error in instant sending: {str(e)}")
        return jsonify({'error': 'Erro no envio instantâneo'}), 500



@app.route('/api/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """Test WhatsApp Business API connection"""
    try:
        # Force credential refresh before testing
        whatsapp_service._refresh_credentials()
        result = whatsapp_service.test_connection()
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error testing WhatsApp Business API: {str(e)}")
        return jsonify({'error': 'Erro ao testar conexão com WhatsApp Business API'}), 500

@app.route('/api/get-templates', methods=['GET', 'POST'])
def get_templates():
    """Get all available templates from WhatsApp Business account"""
    try:
        # Get business account ID from request
        business_account_id = None
        if request.method == 'POST':
            data = request.json or {}
            business_account_id = data.get('business_account_id')
        
        if not business_account_id:
            return jsonify({'success': False, 'error': 'Business Account ID é obrigatório'}), 400
        
        # Get access token from environment
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not access_token:
            return jsonify({'success': False, 'error': 'Token WHATSAPP_ACCESS_TOKEN não configurado'}), 400
        
        # Fetch templates directly from Facebook API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        templates_url = f'https://graph.facebook.com/v23.0/{business_account_id}/message_templates'
        templates_response = requests.get(templates_url, headers=headers, timeout=15)
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            raw_templates = templates_data.get('data', [])
            
            # Filter only approved templates
            approved_templates = []
            for template in raw_templates:
                if template.get('status') == 'APPROVED':
                    approved_templates.append({
                        'name': template.get('name'),
                        'language': template.get('language'),
                        'category': template.get('category'),
                        'status': template.get('status'),
                        'has_parameters': bool(template.get('components', [])),
                        'has_buttons': any(comp.get('type') == 'BUTTONS' for comp in template.get('components', []))
                    })
            
            logging.info(f"Encontrados {len(approved_templates)} templates aprovados na BM {business_account_id}")
            
            return jsonify({
                'success': True,
                'templates': approved_templates,
                'count': len(approved_templates),
                'total_found': len(raw_templates),
                'business_account_id': business_account_id
            })
        else:
            error_data = templates_response.json() if templates_response.content else {}
            error_msg = error_data.get('error', {}).get('message', f'Erro HTTP {templates_response.status_code}')
            
            logging.error(f"Erro ao buscar templates da BM {business_account_id}: {error_msg}")
            return jsonify({'success': False, 'error': f'Erro na API: {error_msg}'}), 400
    
    except Exception as e:
        logging.error(f"Error getting templates: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/send-mega-batch', methods=['POST'])
def send_mega_batch():
    """Start mega batch processing for large lists (5000+ leads)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Validate leads
        leads_text = data.get('leads', '').strip()
        template_name = data.get('template_name', 'modelo_5').strip()
        phone_number_id = data.get('phone_number_id', '')
        
        if not leads_text:
            return jsonify({'error': 'Lista de leads é obrigatória'}), 400
            
        if not phone_number_id:
            return jsonify({'error': 'Phone Number ID é obrigatório'}), 400
        
        # Set the phone number ID for this request
        whatsapp_service.set_phone_number_id(phone_number_id)
            
        # Parse leads - agora tolera erros e continua processando
        all_leads, validation_errors = parse_leads(leads_text)
        
        # Filtrar apenas leads válidos
        valid_leads = []
        invalid_count = 0
        
        for lead in all_leads:
            try:
                # Validar CPF individualmente
                if validate_cpf(lead['cpf']):
                    valid_leads.append(lead)
                else:
                    invalid_count += 1
                    logging.warning(f"CPF inválido ignorado: {lead.get('nome', 'N/A')} - {lead.get('cpf', 'N/A')}")
            except:
                invalid_count += 1
                logging.warning(f"Lead inválido ignorado: {lead}")
        
        # Se não há leads válidos, retorna erro
        if len(valid_leads) == 0:
            return jsonify({
                'error': 'Nenhum lead válido encontrado na lista',
                'total_leads': len(all_leads),
                'invalid_leads': invalid_count,
                'validation_errors': validation_errors[:5] if validation_errors else []
            }), 400
        
        # Log informativo sobre leads processados
        if invalid_count > 0:
            logging.info(f"MEGA BATCH: {invalid_count} leads inválidos ignorados. Processando {len(valid_leads)} leads válidos de {len(all_leads)} total.")
        
        leads = valid_leads
        
        # Escolher sistema baseado no tamanho da lista
        if len(leads) >= 20000:
            # ULTRA MEGA LOTE para listas enormes (20k+)
            def start_ultra_processing():
                try:
                    # Use the ultra_mega_batch module for large lists
                    mega_batch.start_mega_processing(leads, template_name, phone_number_id)
                    logging.info(f"🚀 ULTRA MEGA BATCH COMPLETE")
                except Exception as e:
                    logging.error(f"Ultra mega batch processing error: {e}")
            
            logging.info(f"🚀 ULTRA MEGA BATCH INITIATED: Starting ultra processing for {len(leads)} leads")
            import threading
            processing_thread = threading.Thread(target=start_ultra_processing, daemon=True)
            processing_thread.start()
        else:
            # MEGA LOTE normal para listas menores
            def start_mega_processing():
                try:
                    mega_batch.start_mega_processing(leads, template_name, phone_number_id)
                    logging.info(f"MEGA BATCH COMPLETE")
                except Exception as e:
                    logging.error(f"Mega batch processing error: {e}")
            
            logging.info(f"MEGA BATCH INITIATED: Starting background processing for {len(leads)} leads")
            import threading
            processing_thread = threading.Thread(target=start_mega_processing, daemon=True)
            processing_thread.start()
        
        # Wait a moment to ensure thread starts
        import time
        time.sleep(0.5)
        
        # Calcular batch size dinamicamente
        batch_size = 50 if len(leads) > MAX_PER_PHONE else 20
        
        return jsonify({
            'success': True,
            'message': f'MEGA LOTE iniciado para {len(leads)} leads válidos' + (f' ({invalid_count} inválidos ignorados)' if invalid_count > 0 else ''),
            'total_leads': len(leads),
            'invalid_leads': invalid_count,
            'batch_size': batch_size,
            'estimated_batches': (len(leads) + batch_size - 1) // batch_size,
            'estimated_time_minutes': ((len(leads) + batch_size - 1) // batch_size) * 0.5  # Estimativa de tempo
        }), 200
        
    except Exception as e:
        logging.error(f"Error in mega batch processing: {str(e)}")
        return jsonify({'error': 'Erro no processamento em lotes'}), 500

@app.route('/api/batch-status')
def get_batch_status():
    """Get current batch processing status"""
    try:
        # Use only the mega_batch system
        mega_status = mega_batch.get_status()
        return jsonify(mega_status), 200
    except Exception as e:
        logging.error(f"Error getting batch status: {str(e)}")
        return jsonify({'error': 'Erro ao obter status'}), 500

@app.route('/api/stop-batch', methods=['POST'])
def stop_batch_processing():
    """Stop current batch processing"""
    try:
        # Stop the mega batch system
        mega_batch.is_running = False
        return jsonify({'success': True, 'message': 'Processamento será interrompido'}), 200
    except Exception as e:
        logging.error(f"Error stopping batch: {str(e)}")
        return jsonify({'error': 'Erro ao parar processamento'}), 500

@app.route('/api/send-smart-distribution', methods=['POST'])
def send_smart_distribution():
    """Send messages with intelligent load balancing across phones and templates with proxy rotation"""
    try:
        # Import proxy service locally to avoid circular imports
        from services.proxy_service import proxy_service
        
        data = request.get_json()
        leads_text = data.get('leads', '')
        template_names = data.get('templates', [])
        phone_number_ids = data.get('phone_numbers', [])
        
        logging.info(f"🔍 RECEIVED DATA: {len(template_names)} templates, {len(phone_number_ids)} phone_numbers")
        logging.info(f"📱 Phone IDs: {phone_number_ids}")
        logging.info(f"📋 Templates: {template_names}")
        
        # Validate that we have actual phone IDs, not None values
        valid_phone_ids = [pid for pid in phone_number_ids if pid and pid != 'None']
        if len(valid_phone_ids) != len(phone_number_ids):
            logging.error(f"❌ Invalid phone IDs detected: {phone_number_ids}")
            return jsonify({'error': 'Phone Number IDs inválidos detectados'}), 400
        
        if not leads_text or not template_names or not valid_phone_ids:
            return jsonify({'error': 'Leads, templates e phone numbers são obrigatórios'}), 400
        
        # Parse and validate leads
        leads = []
        invalid_count = 0
        for line in leads_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) >= 3:
                numero = parts[0].strip()
                nome = parts[1].strip()
                cpf = parts[2].strip()
                
                # Basic validation
                if numero and nome and cpf:
                    leads.append({
                        'numero': numero,
                        'nome': nome, 
                        'cpf': cpf
                    })
                else:
                    invalid_count += 1
            else:
                invalid_count += 1
        
        if not leads:
            return jsonify({'error': 'Nenhum lead válido encontrado'}), 400
        
        # Use valid phone IDs for the rest of the process
        phone_number_ids = valid_phone_ids
        
        # ✨ SISTEMA DE ROTAÇÃO AUTOMÁTICA DE PROXIES ✨
        from services.proxy_service import get_proxy_service
        proxy_svc = get_proxy_service()
        if proxy_svc:
            proxy_distribution = proxy_svc.distribute_leads_across_proxies(len(leads))
        else:
            logging.error("Proxy service not available")
            return jsonify({'success': False, 'error': 'Proxy service not available'}), 500
        if proxy_distribution['success']:
            logging.info(f"🔄 ROTAÇÃO DE PROXIES ATIVADA: {proxy_distribution['total_proxies']} proxies para {len(leads)} leads")
            for proxy_info in proxy_distribution['proxies']:
                logging.info(f"   • {proxy_info['proxy_name']}: {proxy_info['leads_count']} leads")
        else:
            logging.warning(f"⚠️ Nenhuma proxy ativa detectada - continuando sem rotação de proxies")
            logging.warning(f"    Motivo: {proxy_distribution['message']}")
        
        # CRÍTICO: Verificar token atual no ultra-speed
        current_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        logging.info(f"🔍 TOKEN ATUAL NO ULTRA-SPEED: {current_token[:50] if current_token else 'VAZIO'}...")
        
        # Force refresh WhatsApp service before sending
        whatsapp_service._refresh_credentials()
        
        logging.info(f"🚀 ULTRA-SPEED SMART DISTRIBUTION INITIATED: {len(leads)} leads, {len(phone_number_ids)} phones, {len(template_names)} templates")
        logging.info(f"⚡ MAXIMUM PARALLEL MODE: Simulating {len(phone_number_ids) * len(template_names) * 20} simultaneous tabs for ultra-fast delivery")
        
        # FIXED: Create distribution with proper phone ID handling
        def create_smart_distribution():
            try:
                # Distribute leads among phone numbers (max 1000 per phone)
                leads_per_phone = min(MAX_PER_PHONE, len(leads) // len(phone_number_ids) + 1)
                phone_groups = []
                
                for i, phone_id in enumerate(phone_number_ids):
                    start_idx = i * leads_per_phone
                    end_idx = min(start_idx + leads_per_phone, len(leads))
                    if start_idx < len(leads):
                        phone_leads = leads[start_idx:end_idx]
                        phone_groups.append({
                            'phone_id': phone_id,
                            'leads': phone_leads
                        })
                
                # Distribute templates evenly within each phone group
                for group in phone_groups:
                    group_leads = group['leads']
                    leads_per_template = len(group_leads) // len(template_names)
                    remainder = len(group_leads) % len(template_names)
                    
                    template_groups = []
                    start_idx = 0
                    
                    for i, template_name in enumerate(template_names):
                        # Add one extra lead to first 'remainder' templates
                        template_leads_count = leads_per_template + (1 if i < remainder else 0)
                        end_idx = start_idx + template_leads_count
                        
                        if start_idx < len(group_leads):
                            template_leads = group_leads[start_idx:end_idx]
                            template_groups.append({
                                'template': template_name,
                                'leads': template_leads
                            })
                            start_idx = end_idx
                    
                    group['template_groups'] = template_groups
                
                # Process each group in parallel
                import concurrent.futures
                import threading
                import gc  # Garbage collection for memory optimization
                
                # Thread-safe counters
                total_sent = 0
                total_errors = 0
                counter_lock = threading.Lock()
                
                def process_template_group(phone_id, template_name, template_leads):
                    # CRITICAL: Push Flask app context for database operations
                    with app.app_context():
                        nonlocal total_sent, total_errors
                        sent_count = 0
                        error_count = 0
                        
                        worker_id = threading.current_thread().name[-4:]  # Get worker ID
                        logging.info(f"⚡ Worker-{worker_id} Phone {phone_id[:15]}... processing {len(template_leads)} leads with {template_name}")
                        
                        # ULTRA-FAST PROCESSING with PROXY ROTATION - No delays, maximum parallel execution
                        def send_single_message(lead, lead_index=None):
                            try:
                                phone = str(lead.get('numero', '')).strip()
                                nome = lead.get('nome', '')
                                cpf = lead.get('cpf', '')
                                if not phone:
                                    logging.warning("Lead missing phone")
                                    return False
                                if not phone.startswith('+'):
                                    if phone.startswith('55') and len(phone) >= 12:
                                        phone = '+' + phone
                                    elif len(phone) == 11:
                                        phone = '+55' + phone
                                    else:
                                        phone = '+55' + phone
                                try:
                                    success, result = whatsapp_service.send_template_message(
                                        phone, template_name, [cpf, nome], phone_id, lead_index=lead_index
                                    )
                                except Exception as send_error:
                                    logging.warning(f"Send error for {nome}: {send_error}")
                                    success = False
                                if success:
                                    logging.info(f"Worker-{worker_id}: ✅ {nome} - {phone} (lead #{lead_index + 1 if lead_index is not None else '?'})")
                                    return True
                                else:
                                    logging.warning(f"Worker-{worker_id}: ❌ {nome} - {phone} (lead #{lead_index + 1 if lead_index is not None else '?'})")
                                    return False
                            except Exception as e:
                                logging.error(f"Worker-{worker_id}: ❌ {lead.get('nome', 'Unknown')}: {e}")
                                return False
                    
                        # MAXIMUM SPEED - Process all leads with proper phone ID distribution
                        logging.info(f"🔍 Worker-{worker_id} using phone ID: {phone_id}")
                        
                        # Calculate lead indexes for proxy rotation
                        for i, lead in enumerate(template_leads):
                            try:
                                # Calculate global lead index for proxy rotation
                                global_lead_index = leads.index(lead)
                                if send_single_message(lead, global_lead_index):
                                    sent_count += 1
                                else:
                                    error_count += 1
                            except Exception:
                                error_count += 1
                        
                        # Update totals (thread-safe)
                        with counter_lock:
                            total_sent += sent_count
                            total_errors += error_count
                        
                        # Memory cleanup for each worker
                        gc.collect()
                        
                        logging.info(f"🏁 Worker-{worker_id} COMPLETED: {sent_count} sent, {error_count} errors from {len(template_leads)} leads")
                
                # TAB STRATEGY OPTIMIZATION - Optimized for single tab with 1 phone number
                # For 20-tab strategy, each tab uses 1 phone with up to 1000 leads
                is_single_tab = len(phone_number_ids) == 1 and len(leads) <= MAX_PER_PHONE
                
                if is_single_tab:
                    # Single tab optimization - faster processing for small focused batches
                    base_workers = len(template_names) * 50  # 50 workers per template for ULTRA speed
                    max_workers = min(500, base_workers)  # High workers for maximum speed
                    logging.info(f"🎯 SINGLE TAB OPTIMIZATION: {len(leads)} leads, 1 phone, {len(template_names)} templates")
                else:
                    # Multi-tab fallback - ULTRA high-speed processing
                    base_workers = len(phone_number_ids) * len(template_names)
                    max_workers = min(2000, base_workers * 100)  # 100x multiplier for ULTRA speed
                    logging.info(f"🚀 MULTI-TAB MODE: {len(phone_number_ids)} phones, {len(template_names)} templates")
                
                logging.info(f"⚡ OPTIMIZED CONFIG: {base_workers} base workers → {max_workers} total workers")
                logging.info(f"🎯 TARGET: ~{max_workers * 5} mensagens por minuto (tab-optimized)")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    
                    # Create multiple workers per template group for maximum speed
                    for group in phone_groups:
                        for template_group in group['template_groups']:
                            # Split each template group into MAXIMUM micro-batches for parallel processing
                            template_leads = template_group['leads']
                            micro_batch_size = 1  # 1 lead per worker for ABSOLUTE maximum speed
                            
                            # Create micro-batches for maximum parallelism
                            if len(template_leads) > micro_batch_size:
                                for i in range(0, len(template_leads), micro_batch_size):
                                    micro_batch = template_leads[i:i + micro_batch_size]
                                    if micro_batch:
                                        future = executor.submit(
                                            process_template_group,
                                            group['phone_id'],
                                            template_group['template'],
                                            micro_batch
                                        )
                                        futures.append(future)
                            else:
                                # For small groups, create one worker per lead for maximum speed
                                for lead in template_leads:
                                    future = executor.submit(
                                        process_template_group,
                                        group['phone_id'],
                                        template_group['template'],
                                        [lead]  # Single lead per worker
                                    )
                                    futures.append(future)
                    
                    logging.info(f"🚀 ULTRA-SPEED MODE: {len(futures)} parallel workers initiated (like {len(futures)} tabs)")
                    
                    # Wait for all workers to complete - no timeout for maximum throughput
                    completed = 0
                    total_workers = len(futures)
                    
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            future.result()  # Get result to handle any exceptions
                            completed += 1
                            
                            # Progress logging every 100 completed workers
                            if completed % 100 == 0:
                                progress = (completed / total_workers) * 100
                                logging.info(f"🔥 PROGRESS: {completed}/{total_workers} workers completed ({progress:.1f}%)")
                        except Exception as e:
                            logging.error(f"Worker failed with error: {e}")
                            completed += 1
                    
                    # Final memory cleanup
                    gc.collect()
                
                logging.info(f"🏁 ULTRA-SPEED DISTRIBUTION COMPLETE: {total_sent} sent, {total_errors} errors from {len(leads)} total leads")
                logging.info(f"⚡ PERFORMANCE: Processed with {len(futures)} parallel workers - Maximum possible speed achieved")
                
            except Exception as e:
                logging.error(f"Smart distribution error: {e}")
        
        # Start processing in background thread
        import threading
        processing_thread = threading.Thread(target=create_smart_distribution, daemon=True)
        processing_thread.start()
        
        # Wait a moment to ensure thread starts
        import time
        time.sleep(0.5)
        
        # Calculate estimated workers for MAXIMUM speed feedback
        estimated_workers = len(leads)  # One worker per lead for absolute maximum speed
        estimated_speed = estimated_workers * 2  # Estimated messages per minute at maximum speed
        
        return jsonify({
            'success': True,
            'message': f'MÁXIMA VELOCIDADE Distribution iniciada para {len(leads)} leads',
            'total_leads': len(leads),
            'invalid_leads': invalid_count,
            'phone_numbers': len(phone_number_ids),
            'templates': len(template_names),
            'parallel_workers': estimated_workers,
            'estimated_speed': f'{estimated_speed} mensagens/minuto',
            'distribution_strategy': f'1 worker por lead, {estimated_workers} workers simultâneos',
            'speed_mode': 'MÁXIMA VELOCIDADE ABSOLUTA - Sem limitações'
        }), 200
        
    except Exception as e:
        logging.error(f"Error in smart distribution: {str(e)}")
        return jsonify({'error': 'Erro na distribuição inteligente'}), 500

# Inicializar webhook handler
webhook_handler = WhatsAppWebhookHandler(db=db)

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Endpoint para receber webhooks do WhatsApp Business API"""
    if request.method == 'GET':
        # Verificação inicial do webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token and challenge:
            challenge_response = webhook_handler.verify_webhook(mode, token, challenge)
            if challenge_response:
                return challenge_response
            else:
                return "Forbidden", 403
        else:
            return "Bad Request", 400
    
    elif request.method == 'POST':
        # Processar webhook recebido
        try:
            webhook_data = request.get_json()
            
            if not webhook_data:
                return "Bad Request", 400
            
            # Log do webhook recebido
            logging.info(f"Webhook recebido: {str(webhook_data)}")
            
            # Processar webhook
            result = webhook_handler.process_webhook(webhook_data)
            
            # Responder com status 200 (obrigatório para WhatsApp)
            return jsonify(result), 200
            
        except Exception as e:
            logging.error(f"Erro ao processar webhook: {str(e)}")
            return "Internal Server Error", 500

@app.route('/api/ultra-speed', methods=['POST'])
def ultra_speed_smart_distribution():
    """Ultra-speed with smart distribution: up to 1000 messages per phone, randomized templates"""
    try:
        data = request.get_json()
        leads_input = data.get('leads', [])
        template_names = data.get('template_names', [])
        phone_number_ids = data.get('phone_number_ids', [])
        connection_data = data.get('whatsapp_connection', {})
        
        # Get session ID for progress tracking
        session_id = str(int(time.time() * 1000))
        
        # Initialize session progress
        if 'progress_sessions' not in globals():
            global progress_sessions
            progress_sessions = {}
        
        progress_sessions[session_id] = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'status': 'starting',
            'start_time': time.time(),
            'last_update': time.time()
        }
        
        logging.info(f"🔍 ULTRA-SPEED SMART SESSION: {session_id}")
        
        # Update WhatsApp service with connection data if provided
        if connection_data and connection_data.get('access_token'):
            logging.info("🔄 Updating WhatsApp connection with provided token...")
            whatsapp_service.update_connection(connection_data)
        
        # Validate inputs
        if not leads_input or not template_names or not phone_number_ids:
            return jsonify({'error': 'Leads, templates e phone numbers são obrigatórios'}), 400
        
        # Parse leads if it's a string
        leads = []
        if isinstance(leads_input, str):
            parse_errors = []
            for line in leads_input.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 3:
                    numero = parts[0].strip()
                    nome = parts[1].strip()
                    cpf = parts[2].strip()
                    
                    if numero and nome and cpf:
                        leads.append({
                            'numero': numero,
                            'nome': nome,
                            'cpf': cpf
                        })
                    else:
                        parse_errors.append(f"Lead inválido: {line}")
                else:
                    parse_errors.append(f"Formato inválido: {line}")
            
            if parse_errors:
                return jsonify({'error': f'Erros no parsing: {"; ".join(parse_errors)}'}), 400
        else:
            leads = leads_input
        
        if not leads:
            return jsonify({'error': 'Nenhum lead válido fornecido'}), 400
        
        # Update progress total
        progress_sessions[session_id]['total'] = len(leads)
        progress_sessions[session_id]['status'] = 'running'
        
        # SMART DISTRIBUTION: Up to 1000 messages per phone number with randomized templates
        def ultra_speed_smart_distribution():
            import random
            import concurrent.futures
            from concurrent.futures import ThreadPoolExecutor
            import threading
            
            sent_count = 0
            failed_count = 0
            counter_lock = threading.Lock()
            
            # Create WhatsApp service instance for this worker thread
            from services.whatsapp_business_api import WhatsAppBusinessAPI
            worker_whatsapp = WhatsAppBusinessAPI()
            
            # Apply connection data to worker instance
            if connection_data and connection_data.get('access_token'):
                worker_whatsapp.update_connection(connection_data)
                logging.info(f"⚡ Worker using connection with token: {connection_data.get('access_token', '')[:50]}...")
            
            # SMART DISTRIBUTION: Distribute leads across phone numbers (max 1000 per phone)
            max_per_phone = MAX_PER_PHONE
            total_capacity = len(phone_number_ids) * max_per_phone
            
            if len(leads) > total_capacity:
                logging.warning(f"⚠️ Lista muito grande! {len(leads)} leads > capacidade máxima {total_capacity}")
                # Truncate to maximum capacity
                leads_to_process = leads[:total_capacity]
                logging.info(f"🔄 Processando apenas {len(leads_to_process)} leads (máximo da capacidade)")
            else:
                leads_to_process = leads
            
            # Randomize leads order for better distribution
            random.shuffle(leads_to_process)
            
            # Create phone groups with maximum 1000 leads per phone
            phone_groups = {}
            for phone_id in phone_number_ids:
                phone_groups[phone_id] = []
            
            # Distribute leads round-robin style among phone numbers
            for i, lead in enumerate(leads_to_process):
                phone_id = phone_number_ids[i % len(phone_number_ids)]
                if len(phone_groups[phone_id]) < max_per_phone:
                    phone_groups[phone_id].append(lead)
            
            logging.info(f"📊 SMART DISTRIBUTION:")
            for phone_id, group_leads in phone_groups.items():
                logging.info(f"📱 Phone {phone_id[:15]}...: {len(group_leads)} leads")
            
            # Process each lead with randomized template selection
            def process_single_lead(lead_index, lead, assigned_phone_id):
                nonlocal sent_count, failed_count
                
                try:
                    # RANDOMIZE TEMPLATE for each message
                    template_name = random.choice(template_names)
                    
                    phone = lead['numero']
                    nome = lead['nome']
                    cpf = lead['cpf']
                    
                    # Format phone number
                    if not phone.startswith('+'):
                        if phone.startswith('55'):
                            phone = '+' + phone
                        elif len(phone) == 11:
                            phone = '+55' + phone
                        else:
                            phone = '+55' + phone
                    
                    # Send message with randomized template via assigned phone  
                    success = worker_whatsapp.send_template_message(
                        phone, template_name, 'en', [cpf, nome], assigned_phone_id
                    )
                    
                    with counter_lock:
                        if success:
                            sent_count += 1
                            logging.info(f"⚡ SENT {lead_index+1}: {nome} - {template_name} via Phone {assigned_phone_id[:15]}...")
                        else:
                            failed_count += 1
                            logging.warning(f"⚡ FAILED {lead_index+1}: {nome} - {template_name}")
                        
                        # Update progress
                        progress_sessions[session_id]['sent'] = sent_count
                        progress_sessions[session_id]['failed'] = failed_count
                        progress_sessions[session_id]['last_update'] = time.time()
                
                except Exception as e:
                    with counter_lock:
                        failed_count += 1
                        progress_sessions[session_id]['failed'] = failed_count
                        progress_sessions[session_id]['last_update'] = time.time()
                    logging.error(f"⚡ ERROR {lead_index+1}: {e}")
            
            # MAXIMUM PARALLEL PROCESSING
            total_leads_to_process = sum(len(group_leads) for group_leads in phone_groups.values())
            max_workers = min(500, total_leads_to_process)  # Optimal worker count
            
            logging.info(f"🚀 ULTRA-SPEED SMART: {max_workers} workers, {total_leads_to_process} leads, {len(template_names)} templates randomized")
            
            start_time = time.time()
            
            # Process all leads simultaneously with smart distribution
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                lead_counter = 0
                
                # Submit all leads with their assigned phone numbers
                for phone_id, group_leads in phone_groups.items():
                    for lead in group_leads:
                        future = executor.submit(process_single_lead, lead_counter, lead, phone_id)
                        futures.append(future)
                        lead_counter += 1
                
                # Wait for all to complete
                concurrent.futures.wait(futures)
            
            end_time = time.time()
            
            # Final progress update
            progress_sessions[session_id]['status'] = 'completed'
            progress_sessions[session_id]['last_update'] = time.time()
            
            logging.info(f"🎯 SMART DISTRIBUTION COMPLETE: {sent_count} sent, {failed_count} failed")
            logging.info(f"⚡ ULTRA SPEED ACHIEVED: {sent_count / (end_time - start_time):.1f} messages/second")
            logging.info(f"🚀 PROCESSED {total_leads_to_process} MESSAGES IN {end_time - start_time:.1f} SECONDS")
            logging.info(f"📊 DISTRIBUTION: Max {max_per_phone} per phone, {len(template_names)} templates randomized")
        
        # Start processing in background thread
        processing_thread = threading.Thread(target=ultra_speed_smart_distribution)
        processing_thread.daemon = True
        processing_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'ULTRA-SPEED SMART iniciado para {len(leads)} leads',
            'session_id': session_id,
            'total_leads': len(leads),
            'max_per_phone': MAX_PER_PHONE,
            'total_capacity': len(phone_number_ids) * MAX_PER_PHONE,
            'templates': len(template_names),
            'phone_numbers': len(phone_number_ids),
            'randomized_templates': True
        }), 200
        
    except Exception as e:
        logging.error(f"ULTRA-SPEED ERROR: {str(e)}")
        return jsonify({'error': 'Erro no processamento ultra-velocidade'}), 500

# Progress tracking endpoint
@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """Get real-time progress for a session"""
    try:
        if 'progress_sessions' not in globals():
            return jsonify({'error': 'Session not found'}), 404
        
        if session_id not in progress_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = progress_sessions[session_id]
        progress = (session_data['sent'] / session_data['total'] * 100) if session_data['total'] > 0 else 0
        elapsed_time = time.time() - session_data['start_time']
        
        return jsonify({
            'total': session_data['total'],
            'sent': session_data['sent'], 
            'failed': session_data['failed'],
            'progress': progress,
            'status': session_data['status'],
            'elapsed_time': elapsed_time,
            'recovery_active': False,
            'success': True
        })
    except Exception as e:
        logging.error(f"Progress error: {e}")
        return jsonify({'error': 'Erro ao obter progresso'}), 500

# PROXY MANAGEMENT ROUTES
@app.route('/api/proxies', methods=['GET'])
def get_proxies():
    """Get all proxies"""
    try:
        from models import Proxy
        proxies = Proxy.query.all()
        
        proxies_data = []
        for proxy in proxies:
            proxies_data.append({
                'id': proxy.id,
                'name': proxy.name,
                'proxy_string': proxy.proxy_string,
                'is_active': proxy.is_active,
                'last_used': proxy.last_used.isoformat() if proxy.last_used else None,
                'success_count': proxy.success_count,
                'error_count': proxy.error_count,
                'created_at': proxy.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'proxies': proxies_data,
            'total': len(proxies_data)
        })
    
    except Exception as e:
        logging.error(f"Error getting proxies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/proxies', methods=['POST'])
def add_proxy():
    """Add new proxy"""
    try:
        from models import Proxy
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        name = data.get('name', '').strip()
        proxy_string = data.get('proxy_string', '').strip()
        
        if not name or not proxy_string:
            return jsonify({'success': False, 'error': 'Nome e proxy são obrigatórios'}), 400
        
        # Validate proxy format
        parts = proxy_string.split(':')
        if len(parts) < 4:
            return jsonify({'success': False, 'error': 'Formato inválido. Use: host:port:user:pass'}), 400
        
        # Check if proxy already exists
        existing = Proxy.query.filter_by(proxy_string=proxy_string).first()
        if existing:
            return jsonify({'success': False, 'error': 'Proxy já existe'}), 400
        
        # Create new proxy
        proxy = Proxy()
        proxy.name = name
        proxy.proxy_string = proxy_string
        proxy.is_active = True
        
        db.session.add(proxy)
        db.session.commit()
        
        logging.info(f"Proxy adicionado: {name}")
        
        return jsonify({
            'success': True,
            'message': 'Proxy adicionado com sucesso',
            'proxy': {
                'id': proxy.id,
                'name': proxy.name,
                'proxy_string': proxy.proxy_string,
                'is_active': proxy.is_active
            }
        })
    
    except Exception as e:
        logging.error(f"Error adding proxy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/proxies/<int:proxy_id>', methods=['PUT'])
def update_proxy(proxy_id):
    """Update proxy"""
    try:
        from models import Proxy
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        proxy = Proxy.query.get_or_404(proxy_id)
        
        name = data.get('name', '').strip()
        proxy_string = data.get('proxy_string', '').strip()
        is_active = data.get('is_active', True)
        
        if name:
            proxy.name = name
        
        if proxy_string:
            # Validate proxy format
            parts = proxy_string.split(':')
            if len(parts) < 4:
                return jsonify({'success': False, 'error': 'Formato inválido. Use: host:port:user:pass'}), 400
            proxy.proxy_string = proxy_string
        
        proxy.is_active = is_active
        proxy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logging.info(f"Proxy atualizado: {proxy.name}")
        
        return jsonify({
            'success': True,
            'message': 'Proxy atualizado com sucesso',
            'proxy': {
                'id': proxy.id,
                'name': proxy.name,
                'proxy_string': proxy.proxy_string,
                'is_active': proxy.is_active
            }
        })
    
    except Exception as e:
        logging.error(f"Error updating proxy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/proxies/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    """Delete proxy"""
    try:
        from models import Proxy
        proxy = Proxy.query.get_or_404(proxy_id)
        
        proxy_name = proxy.name
        db.session.delete(proxy)
        db.session.commit()
        
        logging.info(f"Proxy deletado: {proxy_name}")
        
        return jsonify({
            'success': True,
            'message': f'Proxy {proxy_name} deletado com sucesso'
        })
    
    except Exception as e:
        logging.error(f"Error deleting proxy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/proxies/<int:proxy_id>/test', methods=['POST'])
def test_proxy(proxy_id):
    """Test proxy connection"""
    try:
        from models import Proxy
        import requests
        
        proxy = Proxy.query.get_or_404(proxy_id)
        proxy_dict = proxy.get_requests_proxy_dict()
        
        if not proxy_dict:
            return jsonify({'success': False, 'error': 'Formato de proxy inválido'}), 400
        
        # Test proxy with a simple request
        test_url = 'https://httpbin.org/ip'
        
        try:
            response = requests.get(test_url, proxies=proxy_dict, timeout=10)
            if response.status_code == 200:
                result = response.json()
                proxy.increment_success()
                
                return jsonify({
                    'success': True,
                    'message': 'Proxy funcionando corretamente',
                    'ip': result.get('origin', 'N/A'),
                    'response_time': response.elapsed.total_seconds()
                })
            else:
                proxy.increment_error()
                return jsonify({'success': False, 'error': f'HTTP {response.status_code}'}), 400
                
        except requests.exceptions.RequestException as e:
            proxy.increment_error()
            return jsonify({'success': False, 'error': f'Erro de conexão: {str(e)}'}), 400
    
    except Exception as e:
        logging.error(f"Error testing proxy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/proxy-manager')
def proxy_manager():
    """Proxy management page"""
    return render_template('proxy_manager.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
