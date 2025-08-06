#!/usr/bin/env python3
"""
Script para corrigir problemas comuns de deployment no Heroku
"""

import os
import subprocess
import sys

def fix_python_version():
    """Corrige arquivo de versão Python para Heroku uv buildpack"""
    
    print("🔧 Corrigindo versão Python para Heroku...")
    
    # Remove runtime.txt se existir
    if os.path.exists('runtime.txt'):
        os.remove('runtime.txt')
        print("✅ runtime.txt removido")
    
    # Cria .python-version
    with open('.python-version', 'w') as f:
        f.write('3.11\n')
    print("✅ .python-version criado com Python 3.11")

def check_pyproject_toml():
    """Verifica e corrige pyproject.toml se necessário"""
    
    print("🔧 Verificando pyproject.toml...")
    
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml não encontrado!")
        return False
    
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    # Verificar se tem dependências necessárias
    required_deps = [
        'flask',
        'flask-sqlalchemy', 
        'gunicorn',
        'psycopg2-binary',
        'requests'
    ]
    
    missing_deps = []
    for dep in required_deps:
        if dep.lower() not in content.lower():
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"⚠️ Dependências possivelmente ausentes: {missing_deps}")
        print("💡 Verifique se todas as dependências estão no pyproject.toml")
    else:
        print("✅ pyproject.toml parece correto")
    
    return True

def create_heroku_friendly_procfile():
    """Cria Procfile otimizado para Heroku"""
    
    print("🔧 Criando Procfile otimizado...")
    
    procfile_content = """web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 8 --timeout 120 --keep-alive 10 --max-requests 2000 --max-requests-jitter 200 --preload main:app"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Procfile criado/atualizado")

def verify_main_module():
    """Verifica se main.py existe e está correto"""
    
    print("🔧 Verificando main.py...")
    
    if not os.path.exists('main.py'):
        print("❌ main.py não encontrado!")
        
        # Criar main.py básico
        main_content = """from app import app

if __name__ == "__main__":
    app.run(debug=True)
"""
        with open('main.py', 'w') as f:
            f.write(main_content)
        print("✅ main.py criado")
    else:
        print("✅ main.py encontrado")

def check_environment_variables():
    """Lista variáveis de ambiente necessárias"""
    
    print("🔧 Verificando variáveis de ambiente...")
    
    required_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'DATABASE_URL',  # Será fornecida automaticamente pelo Heroku Postgres
        'SESSION_SECRET'  # Será gerada automaticamente
    ]
    
    print("📝 Variáveis de ambiente necessárias no Heroku:")
    for var in required_vars:
        status = "✅ Configurada" if os.environ.get(var) else "❌ Não configurada"
        print(f"   {var}: {status}")
    
    print("\n💡 Configure no Heroku com:")
    print("   heroku config:set WHATSAPP_ACCESS_TOKEN=seu_token_aqui")

def run_git_commands():
    """Executa comandos git necessários"""
    
    print("🔧 Preparando commit para Heroku...")
    
    try:
        # Add arquivos
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Arquivos adicionados ao git")
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Fix Heroku deployment - use .python-version'], check=False)
        print("✅ Commit realizado")
        
        print("🚀 Pronto para push no Heroku:")
        print("   git push heroku main")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro no git: {e}")
        print("💡 Execute manualmente:")
        print("   git add .")
        print("   git commit -m 'Fix Heroku deployment'")
        print("   git push heroku main")

def main():
    """Executa correções para deployment no Heroku"""
    
    print("🚀 CORREÇÃO DEPLOYMENT HEROKU")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app.py'):
        print("❌ app.py não encontrado! Execute este script no diretório raiz do projeto.")
        sys.exit(1)
    
    # Executar correções
    fix_python_version()
    check_pyproject_toml()
    create_heroku_friendly_procfile()
    verify_main_module()
    check_environment_variables()
    run_git_commands()
    
    print("\n" + "=" * 50)
    print("✅ CORREÇÕES APLICADAS!")
    print("\n📋 Próximos passos:")
    print("1. git push heroku main")
    print("2. heroku config:set WHATSAPP_ACCESS_TOKEN=seu_token")
    print("3. heroku ps:scale web=1:performance-l")
    print("4. heroku logs --tail")
    
    print("\n🎯 O deployment deve funcionar agora!")

if __name__ == "__main__":
    main()