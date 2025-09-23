# 🌉 WEBHOOK BRIDGE - Solução para mTLS

## ❗ PROBLEMA
A Meta agora exige **mTLS (certificados de cliente)** para webhooks do WhatsApp Business API. 
O Replit não suporta mTLS nativamente.

## ✅ SOLUÇÃO
Ponte de webhook que roda em serviço com suporte a mTLS e encaminha para o Replit.

---

## 🚀 DEPLOY RÁPIDO - RAILWAY (RECOMENDADO)

### 1. Criar conta no Railway
- Acesse: https://railway.app/
- Conecte com GitHub

### 2. Deploy da ponte
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Criar projeto
railway new

# Deploy
railway up
```

### 3. Configurar variáveis
No painel do Railway, adicione:
```
REPLIT_WEBHOOK_URL=https://72b11919-b9c0-4779-8bc7-79c3c90ce16f-00-1mp9eaiqxt8ni.picard.replit.dev/webhook
WEBHOOK_VERIFY_TOKEN=webhook_verify_token_12345_dev_only
```

### 4. Usar URL da ponte na Meta
A Railway fornecerá uma URL como:
```
https://webhook-bridge-production-xxxx.up.railway.app/webhook
```

**USE ESTA URL na configuração do webhook da Meta!**

---

## 🔄 FLUXO COMPLETO

```
Meta/Facebook
    ↓ (mTLS)
Railway Bridge  
    ↓ (HTTPS)
Replit Webhook
    ↓
Sua aplicação
```

---

## 📁 ARQUIVOS CRIADOS

- `webhook_bridge.py` - Ponte principal
- `requirements_bridge.txt` - Dependências
- `railway.json` - Configuração Railway
- `Procfile_bridge` - Comando de start

---

## ⚡ ALTERNATIVAS

### Render.com
1. Conecte repositório no Render
2. Use `Procfile_bridge` como start command
3. Configure variáveis de ambiente

### Fly.io
1. Instale Fly CLI
2. Execute `fly launch`
3. Configure variáveis com `fly secrets set`

---

## 🧪 TESTE LOCAL

```bash
python3 deploy_bridge.py
```

Deve mostrar: `✅ Local test passed`

---

## ✅ VANTAGENS DA SOLUÇÃO

- ✅ **mTLS nativo** no Railway/Render
- ✅ **Zero downtime** - Replit continua funcionando  
- ✅ **Fallback seguro** - Se a ponte falhar, sistema continua
- ✅ **Logs completos** - Visibilidade total do fluxo
- ✅ **Custo baixo** - Railway tier gratuito suficiente

---

## 🎯 PRÓXIMOS PASSOS

1. **Deploy** a ponte no Railway
2. **Configure** as variáveis de ambiente
3. **Teste** a URL da ponte
4. **Configure** na Meta usando a URL da ponte
5. **✅ Validação** deve funcionar!