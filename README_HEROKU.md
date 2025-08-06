# Deploy no Heroku - Sistema WhatsApp Bulk Messaging

## Preparação para Deploy

### 1. Arquivos de Configuração
- `Procfile`: Configurado para Performance Dynos com 4 workers + 16 threads
- `.python-version`: Python 3.11 (compatível com buildpack uv do Heroku)
- `app.json`: Configuração completa com addons e variáveis
- `heroku_config.py`: Otimizações específicas para Heroku Performance Dynos

### 2. Configurações de Performance
- **Performance-L Dyno**: 14GB RAM, 8 CPU cores
- **Workers**: Até 2000 workers simultâneos 
- **Batch Size**: 1000 leads por batch
- **Thread Multiplier**: 100x paralelismo
- **Connection Pool**: 500 conexões simultâneas

### 3. Variáveis de Ambiente Necessárias

#### Obrigatórias:
```bash
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxx  # Token do Facebook Business
```

#### Opcionais (auto-descobertas):
```bash
WHATSAPP_BUSINESS_ACCOUNT_ID=xxxxxxxxxxxxx  # Business Manager ID
WHATSAPP_PHONE_NUMBER_ID=xxxxxxxxxxxxx     # Phone Number ID
SESSION_SECRET=xxxxxxxxxxxxxxxxx           # Gerado automaticamente
```

### 4. Comandos de Deploy

#### Deploy via Heroku CLI:
```bash
# 1. Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Criar app
heroku create seu-app-whatsapp

# 4. Configurar Performance Dyno
heroku ps:type performance-l -a seu-app-whatsapp

# 5. Adicionar PostgreSQL
heroku addons:create heroku-postgresql:standard-0 -a seu-app-whatsapp

# 6. Configurar variáveis
heroku config:set WHATSAPP_ACCESS_TOKEN=seu_token_aqui -a seu-app-whatsapp

# 7. Deploy
git push heroku main
```

#### Deploy via Heroku Button:
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/seu-usuario/seu-repo)

### 5. Configurações de Otimização

#### Performance Dynos (Recomendado):
- **Performance-L**: $500/mês - 14GB RAM, 8 cores
- **Performance-M**: $250/mês - 2.5GB RAM, 2 cores  
- **Performance-S**: $25/mês - 512MB RAM, 1 core

#### Configuração de Workers:
```bash
# Para Performance-L (máximo desempenho)
heroku config:set MAX_WORKERS=2000 -a seu-app
heroku config:set BATCH_SIZE=1000 -a seu-app
heroku config:set THREAD_MULTIPLIER=100 -a seu-app

# Para Performance-M (balanceado)
heroku config:set MAX_WORKERS=1000 -a seu-app
heroku config:set BATCH_SIZE=500 -a seu-app
heroku config:set THREAD_MULTIPLIER=50 -a seu-app
```

### 6. Monitoramento

#### Logs em Tempo Real:
```bash
heroku logs --tail -a seu-app-whatsapp
```

#### Métricas de Performance:
```bash
heroku ps -a seu-app-whatsapp
heroku config -a seu-app-whatsapp
```

### 7. Database PostgreSQL

O sistema usa automaticamente o PostgreSQL do Heroku com:
- **Pool Size**: 20 conexões
- **Max Overflow**: 30 conexões
- **Pool Recycle**: 1 hora
- **Connection Timeout**: 10 segundos

### 8. Troubleshooting

#### Erro R14 (Memory quota exceeded):
```bash
# Reduzir workers
heroku config:set MAX_WORKERS=1000 -a seu-app
heroku restart -a seu-app
```

#### Erro H12 (Request timeout):
```bash
# Aumentar timeout
heroku config:set WHATSAPP_TIMEOUT=60 -a seu-app
```

#### Rate Limits do WhatsApp:
```bash
# Reduzir velocidade
heroku config:set RATE_LIMIT_DELAY=0.1 -a seu-app
```

### 9. Capacidade Máxima

Com Performance-L Dyno:
- **Processamento**: 10.000+ mensagens/minuto
- **Concorrência**: 2000 workers simultâneos
- **Memória**: 14GB disponível
- **CPU**: 8 cores dedicados

### 10. Custo Estimado (Performance-L)

- **Dyno Performance-L**: $500/mês
- **PostgreSQL Standard**: $50/mês
- **Total**: ~$550/mês para capacidade máxima

## Comandos Rápidos

```bash
# Deploy completo
git add .
git commit -m "Deploy Heroku optimized"
git push heroku main

# Escalar para máxima performance
heroku ps:scale web=1:performance-l

# Verificar status
heroku ps
heroku logs --tail
```