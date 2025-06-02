#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Configuração
DB_PATH = os.path.join('instance', 'estoque.db')
NUM_PRODUTOS = 20000
CATEGORIAS = ['Eletrônicos', 'Escritório', 'Limpeza', 'Ferramentas', 'Informática', 
              'Papelaria', 'Móveis', 'Alimentos', 'Bebidas', 'Vestuário']
NUM_MOVIMENTACOES = 50000  # Número de movimentações a serem geradas

# Inicializar Faker para dados aleatórios em português
fake = Faker('pt_BR')

def criar_conexao():
    """Cria uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def gerar_codigo_produto(indice):
    """Gera um código de produto único baseado no índice"""
    prefixos = ['PROD', 'ITEM', 'SKU', 'EST', 'MAT']
    prefixo = random.choice(prefixos)
    return f"{prefixo}{indice:06d}"

def gerar_produtos(conn, quantidade):
    """Gera produtos aleatórios no banco de dados"""
    print(f"Gerando {quantidade} produtos...")
    
    # Preparar lista de produtos
    produtos = []
    for i in range(1, quantidade + 1):
        codigo = gerar_codigo_produto(i)
        nome = fake.word().capitalize() + ' ' + fake.word().capitalize()
        quantidade_estoque = random.randint(0, 100)
        categoria = random.choice(CATEGORIAS)
        descricao = fake.sentence()
        
        produtos.append((codigo, nome, quantidade_estoque, categoria, descricao))
        
        # Inserir em lotes para melhor performance
        if i % 1000 == 0 or i == quantidade:
            conn.executemany(
                "INSERT INTO produtos (codigo, nome, quantidade, categoria, descricao) VALUES (?, ?, ?, ?, ?)",
                produtos
            )
            conn.commit()
            print(f"  Inseridos {i} produtos...")
            produtos = []

def gerar_movimentacoes(conn, quantidade):
    """Gera movimentações aleatórias no banco de dados"""
    print(f"Gerando {quantidade} movimentações...")
    
    # Obter todos os códigos de produtos
    cursor = conn.cursor()
    cursor.execute("SELECT codigo FROM produtos")
    codigos_produtos = [row[0] for row in cursor.fetchall()]
    
    # Gerar datas aleatórias nos últimos 90 dias
    data_atual = datetime.now()
    
    # Preparar lista de movimentações
    movimentacoes = []
    for i in range(1, quantidade + 1):
        codigo = random.choice(codigos_produtos)
        tipo = random.choice(['Entrada', 'Saída'])
        quantidade_mov = random.randint(1, 10)
        
        # Data aleatória nos últimos 90 dias
        dias_atras = random.randint(0, 90)
        data = data_atual - timedelta(days=dias_atras)
        data_str = data.strftime("%Y-%m-%d %H:%M:%S")
        
        observacao = fake.sentence() if random.random() > 0.3 else None
        
        movimentacoes.append((codigo, tipo, quantidade_mov, data_str, observacao))
        
        # Inserir em lotes para melhor performance
        if i % 1000 == 0 or i == quantidade:
            conn.executemany(
                "INSERT INTO movimentacoes (codigo_produto, tipo, quantidade, data, observacao) VALUES (?, ?, ?, ?, ?)",
                movimentacoes
            )
            conn.commit()
            print(f"  Inseridas {i} movimentações...")
            movimentacoes = []

def atualizar_quantidades(conn):
    """Atualiza as quantidades dos produtos com base nas movimentações"""
    print("Atualizando quantidades de produtos com base nas movimentações...")
    
    # Obter todos os produtos
    cursor = conn.cursor()
    cursor.execute("SELECT codigo FROM produtos")
    produtos = cursor.fetchall()
    
    for produto in produtos:
        codigo = produto[0]
        
        # Calcular quantidade com base nas movimentações
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'Entrada' THEN quantidade ELSE 0 END) as entradas,
                SUM(CASE WHEN tipo = 'Saída' THEN quantidade ELSE 0 END) as saidas
            FROM movimentacoes
            WHERE codigo_produto = ?
        """, (codigo,))
        
        result = cursor.fetchone()
        entradas = result[0] or 0
        saidas = result[1] or 0
        
        # Quantidade base aleatória entre 10 e 50
        quantidade_base = random.randint(10, 50)
        nova_quantidade = max(0, quantidade_base + entradas - saidas)
        
        # Atualizar quantidade do produto
        conn.execute("UPDATE produtos SET quantidade = ? WHERE codigo = ?", (nova_quantidade, codigo))
    
    conn.commit()
    print("Quantidades atualizadas com sucesso!")

def criar_indices(conn):
    """Cria índices para otimizar consultas"""
    print("Criando índices para otimização...")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos (nome)",
        "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos (categoria)",
        "CREATE INDEX IF NOT EXISTS idx_movimentacoes_codigo_produto ON movimentacoes (codigo_produto)",
        "CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes (data)",
    ]
    
    for sql in indices:
        conn.execute(sql)
    
    conn.commit()
    print("Índices criados com sucesso!")

def main():
    """Função principal"""
    try:
        # Verificar se o banco de dados existe
        if not os.path.exists(DB_PATH):
            print(f"Erro: Banco de dados '{DB_PATH}' não encontrado.")
            print("Execute primeiro o aplicativo para criar a estrutura do banco.")
            return 1
        
        # Criar conexão
        conn = criar_conexao()
        
        # Verificar se já existem muitos produtos
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        count = cursor.fetchone()[0]
        
        if count > 1000:
            resposta = input(f"Já existem {count} produtos no banco. Deseja limpar e gerar novos dados? (s/n): ")
            if resposta.lower() == 's':
                conn.execute("DELETE FROM movimentacoes")
                conn.execute("DELETE FROM produtos")
                conn.commit()
                print("Dados existentes removidos.")
            else:
                print("Operação cancelada.")
                return 0
        
        # Gerar dados
        gerar_produtos(conn, NUM_PRODUTOS)
        gerar_movimentacoes(conn, NUM_MOVIMENTACOES)
        atualizar_quantidades(conn)
        criar_indices(conn)
        
        # Otimizar banco SQLite
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        conn.commit()
        
        print("\nGeração de dados concluída com sucesso!")
        print(f"Foram gerados {NUM_PRODUTOS} produtos e {NUM_MOVIMENTACOES} movimentações.")
        print("O sistema está pronto para testes de performance.")
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    # Verificar se Faker está instalado
    try:
        import faker
    except ImportError:
        print("Erro: O pacote 'faker' não está instalado.")
        print("Execute 'pip install faker' e tente novamente.")
        sys.exit(1)
    
    sys.exit(main())
