import sqlite3
import os

# Verifica se a pasta banco/ existe, se não, cria
if not os.path.exists('banco'):
    os.makedirs('banco')

# Define o caminho absoluto para o banco de dados
#caminho_banco = os.path.join(os.path.dirname(__file__), 'banco', 'financeiro.db')
caminho_banco = os.path.join('banco', 'financeiro.db')

def criar_banco():
    conexao = sqlite3.connect(caminho_banco)
    try:
        cursor = conexao.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                categoria TEXT,
                valor REAL,
                data TEXT
            )
        ''')
        conexao.commit()
        print("Banco de dados criado com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"Erro ao criar banco: {e}")
    finally:
        conexao.close()


def coluna_existe(nome_coluna):
    """Verifica se uma coluna já existe na tabela transacao"""
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA table_info(transacao)")
    colunas = [info[1] for info in cursor.fetchall()]  # Posição 1 contém o nome das colunas
    conexao.close()
    return nome_coluna in colunas


def atualizar_banco():
    try:
        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        # Verifica e adiciona a coluna 'ano' se não existir
        if not coluna_existe('ano'):
            cursor.execute("ALTER TABLE transacao ADD COLUMN ano INTEGER")
            print("Coluna 'ano' adicionada com sucesso.")

        # Verifica e adiciona a coluna 'mes' se não existir
        if not coluna_existe('mes'):
            cursor.execute("ALTER TABLE transacao ADD COLUMN mes INTEGER")
            print("Coluna 'mes' adicionada com sucesso.")

        conexao.commit()
    except sqlite3.OperationalError as e:
        print(f"Erro ao atualizar banco: {e}")
    finally:
        conexao.close()


def criar_tabelas():
    if not os.path.exists(caminho_banco): # verifica se o banco existe. Se não existir, cria
        criar_banco()
    atualizar_banco()
