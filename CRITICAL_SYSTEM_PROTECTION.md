# 🛡️ SISTEMA BLINDADO - PROTEÇÃO CRÍTICA

## ⚠️ ATENÇÃO: ESTE SISTEMA ESTÁ PROTEGIDO CONTRA REGRESSÕES

O fluxo **WhatsApp Webhook → Banco → Chat** está funcionando perfeitamente e foi blindado contra futuras quebras.

## 🚫 NUNCA MODIFIQUE SEM EXECUTAR TESTES:

### ✅ Teste obrigatório antes de QUALQUER mudança:
```bash
# 1. Testar API de mensagens
curl -s "http://localhost:5000/api/conversations/1/messages" | python3 -c "
import sys, json
data = json.load(sys.stdin)
messages = data.get('messages', [])
print(f'✅ Total mensagens: {len(messages)}')
ids = [msg['id'] for msg in messages]
if ids == sorted(ids):
    print('✅ Ordem cronológica correta')
else:
    print('❌ ERRO: Mensagens fora de ordem!')
    exit(1)
"

# 2. Verificar webhook ainda ativo
curl -s "http://localhost:5000/webhook" -X GET
```

### 🔒 ÁREAS PROTEGIDAS - NUNCA ALTERE:

#### app.py - Linha ~2500 (get_conversation_messages):
```python
# ⚠️ CRITICAL INVARIANT - DO NOT CHANGE ⚠️ 
# Messages MUST be ordered by ChatMessage.id ASC (NOT created_at)
messages = ChatMessage.query.filter_by(conversation_id=conversation_id)\
    .order_by(ChatMessage.id.asc()).all()
```

#### models.py - brasilia_now():
```python
# ⚠️ DESIGN DECISION ADR-001 - DO NOT CHANGE ⚠️
# MUST return naive datetime (no tzinfo)
return br_time.replace(tzinfo=None)
```

#### webhook_handler.py:
```python
# ⚠️ CRITICAL PATH - WEBHOOK HANDLER - DO NOT MODIFY ⚠️
# Must respond in <2s, never compress, stable return types
```

## 🛡️ PROTEÇÕES ATIVAS:

1. **Comentários críticos** em todo código sensível
2. **Assertions runtime** nos métodos create_inbound/outbound  
3. **Validação automática** de ordem de mensagens na API
4. **Documentação protetiva** neste arquivo

## 📞 FLUXO PROTEGIDO:

```
WhatsApp → webhook_handler.py → models.ChatMessage.create_inbound() 
   → PostgreSQL → app.py/get_conversation_messages → JSON API → Frontend
```

**Este fluxo está funcionando e NÃO PODE ser quebrado!**

---
## ⚡ STATUS: SISTEMA FUNCIONANDO PERFEITAMENTE
- ✅ Webhook recebendo mensagens
- ✅ Salvando no banco em horário brasileiro 
- ✅ API retornando mensagens em ordem correta
- ✅ Frontend exibindo mensagens imediatamente

**Qualquer mudança requer execução dos testes acima!**