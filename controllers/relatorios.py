from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3

def exportar_pdf():
    c = canvas.Canvas('relatorio_financeiro.pdf', pagesize=letter)
    c.drawString(100, 750, "Relatório Financeiro - Resumo")

    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT tipo, SUM(valor) FROM transacao GROUP BY tipo')
    dados = cursor.fetchall()
    conexao.close()

    y = 700
    for tipo, valor in dados:
        c.drawString(100, y, f"{tipo}: R$ {valor:.2f}")
        y -= 20

    c.save()

# Função para consultar despesas por ano
def consultar_despesas_por_ano(ano):
    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT categoria, valor, data
        FROM transacao
        WHERE tipo = 'Despesa' AND ano = ?
    ''', (ano,))
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def consultar_despesas_por_mes(ano, mes=None):
    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()

    if mes is None:
        cursor.execute('''
            SELECT DISTINCT mes
            FROM transacao
            WHERE tipo = 'Despesa' AND ano = ?
        ''', (ano,))
        meses_disponiveis = [row[0] for row in cursor.fetchall()]

        resultados = []
        if meses_disponiveis: # Verifica se há meses disponíveis
          for mes_disponivel in meses_disponiveis:
              cursor.execute('''
                  SELECT categoria, valor, data
                  FROM transacao
                  WHERE tipo = 'Despesa' AND ano = ? AND mes = ?
              ''', (ano, mes_disponivel))
              resultados_mes = cursor.fetchall() #Resultados da consulta do mês em questão
              if resultados_mes: # Verifica se há resultados para o mês.
                  resultados.extend(resultados_mes) # Adiciona apenas se houver resultados

    else:  # Se um mês específico for fornecido
        cursor.execute('''
            SELECT categoria, valor, data
            FROM transacao
            WHERE tipo = 'Despesa' AND ano = ? AND mes = ?
        ''', (ano, mes))
        resultados = cursor.fetchall()

    conexao.close()
    return resultados

def atualizar_despesa(categoria, novo_valor, data, tipo_dado, valor_antigo):
    conexao = sqlite3.connect('banco/financeiro.db')
    cursor = conexao.cursor()
    try:
        if tipo_dado == "valor":
            cursor.execute('''
                UPDATE transacao
                SET valor = ?
                WHERE categoria = ? AND data = ?
            ''', (novo_valor, categoria, data))
        elif tipo_dado == "categoria":
            cursor.execute('''
                UPDATE transacao
                SET categoria = ?
                WHERE categoria = ? AND data = ?
            ''', (categoria, valor_antigo, data))
        conexao.commit()
    except sqlite3.Error as e:
        conexao.rollback()
        raise Exception(f"Erro ao atualizar despesa: {e}")
    finally:
        conexao.close()

def consultar_db(sql, parametros=None):
    try:
        conexao = sqlite3.connect('banco/financeiro.db')
        cursor = conexao.cursor()
        if parametros:
            cursor.execute(sql, parametros)
        else:
            cursor.execute(sql)
        resultado = cursor.fetchall()
        conexao.close()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None