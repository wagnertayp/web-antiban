#!/bin/bash

# Heroku Setup Script - WhatsApp Bulk Messaging System
# Run this script to deploy and configure your app on Heroku

echo "🚀 HEROKU DEPLOYMENT SETUP"
echo "=========================="

read -p "Digite o nome da sua app no Heroku: " APP_NAME
read -p "Digite seu WHATSAPP_ACCESS_TOKEN: " ACCESS_TOKEN

echo ""
echo "🔧 Criando app no Heroku..."
heroku create $APP_NAME

echo ""
echo "⚡ Configurando Performance Dyno..."
heroku ps:type performance-l -a $APP_NAME

echo ""
echo "🗄️ Adicionando PostgreSQL..."
heroku addons:create heroku-postgresql:standard-0 -a $APP_NAME

echo ""
echo "🔐 Configurando variáveis de ambiente..."
heroku config:set WHATSAPP_ACCESS_TOKEN="$ACCESS_TOKEN" -a $APP_NAME
heroku config:set MAX_WORKERS=2000 -a $APP_NAME
heroku config:set BATCH_SIZE=1000 -a $APP_NAME
heroku config:set THREAD_MULTIPLIER=100 -a $APP_NAME
heroku config:set CONNECTION_POOL_SIZE=500 -a $APP_NAME
heroku config:set RATE_LIMIT_DELAY=0.001 -a $APP_NAME

echo ""
echo "🚀 Fazendo deploy..."
git add .
git commit -m "Heroku deployment configuration with .python-version"
git push heroku main

echo ""
echo "✅ DEPLOYMENT COMPLETO!"
echo ""
echo "🌐 Sua app está disponível em: https://$APP_NAME.herokuapp.com"
echo "📊 Para ver logs: heroku logs --tail -a $APP_NAME"
echo "⚙️ Para configurar: heroku config -a $APP_NAME"
echo ""
echo "💰 Custo estimado: ~$550/mês (Performance-L + PostgreSQL Standard)"
echo ""
echo "🚀 CONFIGURAÇÃO ULTRA-SPEED:"
echo "   • 2000 workers simultâneos"
echo "   • 1000 leads por batch"
echo "   • 500 conexões de pool"
echo "   • Processamento de 10.000+ mensagens/minuto"