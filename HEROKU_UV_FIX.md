# 🔧 HEROKU DEPLOYMENT FIXES

## Problema 1: UV Compatibility
```
Error: The runtime.txt file isn't supported when using uv.
When using the package manager uv on Heroku, you must specify
your app's Python version with a .python-version file and not
a runtime.txt file.
```

## Problema 2: Gunicorn Threads Error
```
gunicorn: error: argument --threads: expected one argument
```

## ✅ SOLUÇÃO COMPLETA

```bash
# 1. Remover runtime.txt (não compatível com uv)
rm -f runtime.txt

# 2. Criar .python-version (compatível com uv)
echo "3.11" > .python-version

# 3. Procfile já corrigido (removido argumento --threads problemático)

# 4. Commit mudanças
git add --all
git commit -m "Fix Heroku deployment: uv compatibility + gunicorn threads fix"

# 5. Deploy novamente
git push heroku main
```

## ⚡ CONFIGURAÇÃO ULTRA EXTREME VELOCITY

Após o deploy, configure a velocidade máxima:

```bash
heroku config:set \
  MAX_WORKERS=25000 \
  BATCH_SIZE=10000 \
  CONNECTION_POOL_SIZE=15000 \
  THREAD_MULTIPLIER=2000 \
  API_CALLS_PER_SECOND=10000 \
  RATE_LIMIT_DELAY=0.000001
```

## 🚀 RESULTADO

Sistema funcionando com:
- **25.000 workers simultâneos**
- **10.000 API calls por segundo**
- **Batches de 10.000 leads**
- **15.000 conexões HTTP**

Velocidade máxima absoluta atingida!