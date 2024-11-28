import sqlite3
import matplotlib.pyplot as plt

def gerar_grafico_pizza():
    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT categoria, SUM(valor) FROM transacao 
        WHERE tipo="Despesa" GROUP BY categoria
    ''')
    dados = cursor.fetchall()
    conexao.close()

    categorias = [row[0] for row in dados]
    valores = [row[1] for row in dados]

    plt.pie(valores, labels=categorias, autopct='%1.1f%%')
    plt.title('Distribuição de Despesas por Categoria')
    plt.show()
