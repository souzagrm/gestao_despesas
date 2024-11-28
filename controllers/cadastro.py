import sqlite3
from datetime import datetime
import tkinter as tk

def salvar_transacao(tipo, categoria, valor, data):
    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()

    # Extraindo ano e mês da data fornecida
    try:
        data_formatada = datetime.strptime(data, '%d/%m/%Y')  # Converte a string para um objeto datetime
        ano = data_formatada.year
        mes = data_formatada.month
    except ValueError:
        tk.messagebox.showerror("Erro de Formato", "A data deve estar no formato DD/MM/YYYY.")
        conexao.close()
        return
    # Inserindo a transação com tipo, categoria, valor, data, ano e mês
    cursor.execute('''
        INSERT INTO transacao (tipo, categoria, valor, data, ano, mes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tipo, categoria, valor, data, ano, mes))

    conexao.commit()
    conexao.close()