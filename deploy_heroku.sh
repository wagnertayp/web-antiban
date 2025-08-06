#!/bin/bash

# WhatsApp Bulk Messaging System - Heroku Deploy Script
# Otimizado para Performance-L Dynos com máxima velocidade

echo "🚀 DEPLOYING WHATSAPP BULK SYSTEM TO HEROKU - ULTRA EXTREME VELOCITY MODE"
echo "=================================================="

# Fix Heroku uv compatibility issues
echo "🔧 Fixing Heroku uv compatibility..."
rm -f runtime.txt
echo "3.11" > .python-version

# Check if heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    echo "   Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login check
echo "🔐 Checking Heroku login..."
heroku auth:whoami || {
    echo "❌ Please login to Heroku first: heroku login"
    exit 1
}

# App name (you can change this)
APP_NAME="${1:-whatsapp-bulk-system}"

echo "📱 Creating Heroku app: $APP_NAME"

# Create app with Performance-L dyno
heroku create $APP_NAME --region us

# Add PostgreSQL addon
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:standard-0 --app $APP_NAME

# Set config vars for ULTRA EXTREME VELOCITY
echo "⚡ Setting ULTRA EXTREME VELOCITY configuration..."
heroku config:set \
  FLASK_ENV=production \
  WEB_CONCURRENCY=8 \
  TIMEOUT=1200 \
  MAX_WORKERS=25000 \
  BATCH_SIZE=10000 \
  CONNECTION_POOL_SIZE=15000 \
  THREAD_MULTIPLIER=2000 \
  API_CALLS_PER_SECOND=10000 \
  RATE_LIMIT_DELAY=0.000001 \
  --app $APP_NAME

# Initial scaling (user can change this in Heroku dashboard)
echo "🔥 Setting up initial dyno configuration..."
echo "   You can scale to your preferred dyno type and quantity in Heroku dashboard"
echo "   Recommended configurations:"
echo "   • Standard-2X: heroku ps:scale web=2:standard-2x"
echo "   • Performance-M: heroku ps:scale web=1:performance-m" 
echo "   • Performance-L: heroku ps:scale web=1:performance-l"
echo "   • Multiple dynos: heroku ps:scale web=5:standard-2x"

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy WhatsApp Bulk System - Maximum Velocity Mode"
git push heroku main

# Open app
echo "✅ Deployment complete! Opening app..."
heroku open --app $APP_NAME

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "=================================================="
echo "App URL: https://$APP_NAME.herokuapp.com"
echo "Initial Setup: Standard-2X dyno (configurable)"
echo "Scalability: Configure multiple dynos as needed"
echo "Workers: Up to 5,000 concurrent workers per dyno"
echo ""
echo "📋 Next steps:"
echo "1. Set your WHATSAPP_ACCESS_TOKEN in Heroku dashboard"
echo "2. Test the system with a small list first"
echo "3. Scale up for massive campaigns!"
echo ""
echo "🔧 Useful commands:"
echo "heroku logs --tail --app $APP_NAME                    # View logs"
echo "heroku config --app $APP_NAME                         # View config"
echo "heroku ps --app $APP_NAME                             # View dynos"
echo "heroku ps:scale web=3:standard-2x --app $APP_NAME     # Scale to 3 Standard-2X dynos"
echo "heroku ps:scale web=1:performance-l --app $APP_NAME   # Scale to 1 Performance-L dyno"
echo "heroku ps:scale web=5:performance-m --app $APP_NAME   # Scale to 5 Performance-M dynos"