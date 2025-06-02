#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar o banco de dados do sistema de controle de estoque.
Este script deve ser executado uma única vez antes do primeiro uso do sistema.
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Adicionar o diretório pai ao path para importar os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o aplicativo Flask e os modelos
from src.main import app, db
from src.models import Usuario

def inicializar_banco():
    """Inicializa o banco de dados e cria o usuário administrador"""
    print("Inicializando banco de dados...")
    
    try:
        # Criar todas as tabelas definidas nos modelos
        with app.app_context():
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Verificar se já existe um usuário admin
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                # Criar usuário administrador padrão
                admin = Usuario(
                    username='admin',
                    password=generate_password_hash('admin'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Usuário administrador criado com sucesso!")
                print("  - Username: admin")
                print("  - Senha: admin")
            else:
                print("Usuário administrador já existe.")
                
        print("\nBanco de dados inicializado com sucesso!")
        print("Agora você pode executar o sistema normalmente.")
        return True
        
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")
        return False

if __name__ == "__main__":
    inicializar_banco()
