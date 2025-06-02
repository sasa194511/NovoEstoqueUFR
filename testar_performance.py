#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import sqlite3
from datetime import datetime

# Configuração
DB_PATH = os.path.join('instance', 'estoque.db')
TESTES = [
    {
        'nome': 'Listagem de Produtos',
        'query': 'SELECT * FROM produtos LIMIT 1000',
        'repeticoes': 5
    },
    {
        'nome': 'Busca por Nome',
        'query': "SELECT * FROM produtos WHERE nome LIKE '%a%' LIMIT 100",
        'repeticoes': 5
    },
    {
        'nome': 'Busca por Categoria',
        'query': "SELECT * FROM produtos WHERE categoria = 'Eletrônicos' LIMIT 100",
        'repeticoes': 5
    },
    {
        'nome': 'Contagem Total',
        'query': "SELECT COUNT(*) FROM produtos",
        'repeticoes': 5
    },
    {
        'nome': 'Movimentações por Produto',
        'query': "SELECT m.* FROM movimentacoes m JOIN produtos p ON m.codigo_produto = p.codigo LIMIT 100",
        'repeticoes': 5
    },
    {
        'nome': 'Agrupamento por Categoria',
        'query': "SELECT categoria, COUNT(*) FROM produtos GROUP BY categoria",
        'repeticoes': 5
    },
    {
        'nome': 'Produtos com Estoque Baixo',
        'query': "SELECT * FROM produtos WHERE quantidade > 0 AND quantidade < 10 LIMIT 100",
        'repeticoes': 5
    },
    {
        'nome': 'Movimentações Recentes',
        'query': "SELECT * FROM movimentacoes ORDER BY data DESC LIMIT 100",
        'repeticoes': 5
    }
]

def criar_conexao():
    """Cria uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def executar_teste(conn, teste):
    """Executa um teste de performance e retorna o tempo médio"""
    cursor = conn.cursor()
    tempos = []
    
    print(f"Executando teste: {teste['nome']}")
    
    for i in range(teste['repeticoes']):
        inicio = time.time()
        cursor.execute(teste['query'])
        resultados = cursor.fetchall()
        fim = time.time()
        
        tempo_ms = (fim - inicio) * 1000
        tempos.append(tempo_ms)
        
        print(f"  Execução {i+1}: {tempo_ms:.2f}ms ({len(resultados) if resultados else 0} resultados)")
    
    tempo_medio = sum(tempos) / len(tempos)
    print(f"  Tempo médio: {tempo_medio:.2f}ms\n")
    return tempo_medio

def verificar_indices(conn):
    """Verifica os índices existentes no banco de dados"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indices = cursor.fetchall()
    
    print("Índices encontrados no banco de dados:")
    if indices:
        for idx in indices:
            print(f"  - {idx[0]}")
    else:
        print("  Nenhum índice encontrado!")
    print()

def contar_registros(conn):
    """Conta o número de registros nas tabelas principais"""
    cursor = conn.cursor()
    
    print("Contagem de registros:")
    
    tabelas = ['produtos', 'movimentacoes', 'usuarios', 'solicitacoes']
    for tabela in tabelas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            print(f"  - {tabela}: {count:,} registros")
        except sqlite3.OperationalError:
            print(f"  - {tabela}: Tabela não encontrada")
    
    print()

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
        
        print("=" * 60)
        print("TESTE DE PERFORMANCE - SISTEMA DE CONTROLE DE ESTOQUE")
        print("=" * 60)
        print(f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Banco de dados: {os.path.abspath(DB_PATH)}")
        print("=" * 60)
        print()
        
        # Contar registros
        contar_registros(conn)
        
        # Verificar índices
        verificar_indices(conn)
        
        # Executar testes
        resultados = []
        for teste in TESTES:
            tempo_medio = executar_teste(conn, teste)
            resultados.append({
                'nome': teste['nome'],
                'tempo_medio': tempo_medio
            })
        
        # Resumo
        print("=" * 60)
        print("RESUMO DOS TESTES")
        print("=" * 60)
        
        for resultado in resultados:
            print(f"{resultado['nome']}: {resultado['tempo_medio']:.2f}ms")
        
        # Análise final
        tempos = [r['tempo_medio'] for r in resultados]
        tempo_medio_total = sum(tempos) / len(tempos)
        
        print("\nTempo médio geral: {:.2f}ms".format(tempo_medio_total))
        
        if tempo_medio_total < 50:
            print("\nANÁLISE: Performance excelente! O sistema está otimizado para grandes volumes de dados.")
        elif tempo_medio_total < 200:
            print("\nANÁLISE: Boa performance. O sistema deve funcionar bem com 20.000 itens.")
        elif tempo_medio_total < 500:
            print("\nANÁLISE: Performance aceitável, mas pode haver lentidão em algumas operações com grandes volumes.")
        else:
            print("\nANÁLISE: Performance abaixo do ideal. Recomenda-se revisar as otimizações.")
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
