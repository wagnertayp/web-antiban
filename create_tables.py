#!/usr/bin/env python3
"""
Criar tabelas do banco de dados para interações e status
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def create_tables():
    """Criar todas as tabelas do banco de dados"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar tabelas criadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Tabelas no banco: {tables}")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {str(e)}")

if __name__ == "__main__":
    create_tables()