# Heroku Deployment Instructions - WhatsApp Bulk System

## Quick Deploy para Máxima Velocidade

### 1. Pré-requisitos
```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login no Heroku
heroku login
```

### 2. Deploy Automático (Recomendado)
```bash
# Execute o script de deploy
./deploy_heroku.sh seu-app-name
```

### 3. Deploy Manual (Alternativo)

#### Criar App
```bash
heroku create seu-app-name --region us
```

#### Adicionar PostgreSQL
```bash
heroku addons:create heroku-postgresql:standard-0
```

#### Configurar Variáveis de Performance
```bash
heroku config:set \
  FLASK_ENV=production \
  MAX_WORKERS=10000 \
  BATCH_SIZE=2000 \
  THREAD_MULTIPLIER=500 \
  CONNECTION_POOL_SIZE=3000 \
  RATE_LIMIT_DELAY=0.00001 \
  API_CALLS_PER_SECOND=2000
```

#### Escalar para Performance-L
```bash
heroku ps:scale web=1:performance-l
```

#### Deploy
```bash
git add .
git commit -m "Deploy WhatsApp System"
git push heroku main
```

### 4. Configuração de Token WhatsApp

No dashboard do Heroku ou via CLI:
```bash
heroku config:set WHATSAPP_ACCESS_TOKEN=your_token_here
```

### 5. Verificação do Sistema

```bash
# Ver logs em tempo real
heroku logs --tail

# Verificar status dos dynos
heroku ps

# Verificar configurações
heroku config
```

## Especificações de Performance

- **Dyno Type**: Performance-L (14GB RAM, 8 CPU cores)
- **Workers**: Até 10.000 simultâneos
- **Batch Size**: 2.000 mensagens por lote
- **API Calls**: 2.000 chamadas/segundo
- **Conexões HTTP**: 3.000 simultâneas
- **Database**: PostgreSQL Standard-0

## Resolução de Problemas

### "This app has no process types yet"
Certifique-se que os arquivos estão presentes:
- `Procfile` ✓
- `runtime.txt` ✓
- `requirements.txt` ou `pyproject.toml` ✓

### Performance Lenta
1. Verifique se está usando Performance-L dyno
2. Confirme as variáveis de ambiente de performance
3. Monitore logs para rate limits da API WhatsApp

### Timeout Errors
- Aumente timeout no Procfile
- Reduza batch_size se necessário
- Verifique conexão com WhatsApp API

## Monitoramento

```bash
# Métricas do app
heroku ps:scale
heroku logs --tail
heroku run python -c "from app import app; print('App running!')"
```

## Custos Aproximados

- Performance-L Dyno: ~$250/mês
- PostgreSQL Standard-0: ~$50/mês
- Total: ~$300/mês para operação 24/7

Para campanhas pontuais, você pode escalar up/down conforme necessário.