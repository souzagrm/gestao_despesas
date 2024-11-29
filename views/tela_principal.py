import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
from views.tela_cadastro import abrir_tela_cadastro
from controllers.graficos import gerar_grafico_pizza
from controllers.relatorios import exportar_pdf, consultar_despesas_por_ano, consultar_despesas_por_mes, atualizar_despesa, consultar_db
from tkinter import filedialog
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sqlite3

# Variáveis globais para a janela, a Treeview e o Label do total
janela_tabela = None
tree = None
total_label = None

# Função para exportar para Excel
def exportar_para_excel(dados, nome_arquivo):
    df = pd.DataFrame(dados, columns=["Categoria", "Valor", "Data"])
    df.to_excel(nome_arquivo, index=False)
    messagebox.showinfo("Exportação Concluída", f"Dados exportados para {nome_arquivo}")

def exibir_tabela(dados):
    global janela_tabela, tree, total_label

    try:
        if janela_tabela.winfo_exists():
            for i in tree.get_children():
                tree.delete(i)
            for item in dados:
                tree.insert("", tk.END, values=item)
            janela_tabela.deiconify()
            total_label.config(text=f"Total: R$ {calcular_total(dados):.2f}")
            return
    except (NameError, AttributeError):
        pass

    janela_tabela = tk.Toplevel()
    janela_tabela.title("Resultado da Consulta")
    janela_tabela.protocol("WM_DELETE_WINDOW", lambda: janela_tabela.withdraw())

    tree = ttk.Treeview(janela_tabela, columns=("Categoria", "Valor", "Data"), show="headings")
    tree.heading("Categoria", text="Categoria")
    tree.heading("Valor", text="Valor") # Sem "R$" no cabeçalho
    tree.heading("Data", text="Data")
    tree.pack(fill=tk.BOTH, expand=True)

    for item in dados:
        tree.insert("", tk.END, values=item)

    tree.column("Valor", width=100)
    tree.bind("<Double-1>", lambda event: editar_celula(tree, event))

    botao_exportar = tk.Button(janela_tabela, text="Exportar para Excel",
                               command=lambda: exportar_para_excel(dados, "resultado_consulta.xlsx"))
    botao_exportar.pack(pady=10)

    total_label = tk.Label(janela_tabela, text=f"Total: R$ {calcular_total(dados):.2f}")
    total_label.pack()

def calcular_total(dados):
    total = 0
    for _, valor, _ in dados:
        try:
            total += float(valor)
        except ValueError as e:
            print(f"Erro ao converter '{valor}' para float: {e}")
            pass
    return total

def editar_celula(tree, event):
    region = tree.identify("region", event.x, event.y)
    if region == "cell":
        column = tree.identify_column(event.x)
        rowid = tree.identify_row(event.y)
        item = tree.item(rowid)

        if column == "#1":  # Coluna "Categoria"
            valor_antigo = item['values'][0]
            novo_valor = simpledialog.askstring("Editar Categoria", "Nova Categoria:", initialvalue=valor_antigo)
            tipo_dado = "categoria"

        elif column == "#2":  # Coluna "Valor"
            valor_antigo = item['values'][1].replace("R$ ", "")
            novo_valor = simpledialog.askfloat("Editar Valor", "Novo Valor:", initialvalue=float(valor_antigo))
            tipo_dado = "valor"
        else:
            return
        
    if novo_valor is not None:
        try:
            if column == "#2":
                nova_categoria = item['values'][0]
                novo_valor_float = float(novo_valor)
                valor_antigo_correto = None
                tipo_dado = "valor"
            elif column == "#1":
                nova_categoria = novo_valor
                novo_valor_float = float(item['values'][1]) # Converta para float aqui se necessário
                valor_antigo_correto = item['values'][0]
                tipo_dado = "categoria"
            else:
                return  # Ignora cliques em outras colunas

            nova_data = item['values'][2]

            atualizar_despesa(nova_categoria, novo_valor_float, nova_data, tipo_dado, valor_antigo_correto)
            tree.item(rowid, values=(nova_categoria, novo_valor_float, nova_data))

            dados_atualizados = get_dados_tabela(tree)
            total_label.config(text=f"Total: R$ {calcular_total(dados_atualizados):.2f}")

            #messagebox.showinfo("Sucesso", f"{tipo_dado.capitalize()} atualizado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar {tipo_dado}: {str(e)}")

def get_dados_tabela(tree):
    dados = []
    for item in tree.get_children():
        dados.append(tree.item(item)['values'])
    return dados

def mostrar_despesas_por_ano():
    try:
        # Consulta os anos disponíveis no banco de dados
        resultado_consulta = consultar_db("SELECT DISTINCT ano FROM transacao")
        anos_disponiveis = sorted(list(set([int(row[0]) for row in resultado_consulta])))
        
        if not anos_disponiveis:
            messagebox.showinfo("Consulta de Despesas por Ano", "Nenhum dado encontrado no banco de dados.")
            return

        # Cria a janela de diálogo para seleção do ano
        janela_selecao = tk.Toplevel()
        janela_selecao.title("Selecione o Ano")

        # Dropdown para seleção do ano
        label_ano = tk.Label(janela_selecao, text="Ano:")
        label_ano.grid(row=0, column=0, padx=5, pady=5)

        ano_selecionado = tk.IntVar(value=anos_disponiveis[0])
        dropdown_ano = ttk.Combobox(janela_selecao, textvariable=ano_selecionado, values=anos_disponiveis, state="readonly")
        dropdown_ano.grid(row=0, column=1, padx=5, pady=5)

        # Botão para confirmar a seleção
        def confirmar_selecao():
            ano = ano_selecionado.get()
            janela_selecao.destroy()

            try:
                despesas = consultar_despesas_por_ano(ano)
                if despesas:
                    exibir_tabela(despesas)
                else:
                    messagebox.showinfo("Consulta de Despesas por Ano", f"Nenhuma despesa encontrada para o ano {ano}.")
            except ValueError:
                messagebox.showerror("Erro", "Ano inválido.")

        botao_confirmar = tk.Button(janela_selecao, text="Confirmar", command=confirmar_selecao)
        botao_confirmar.grid(row=1, column=0, columnspan=2, pady=10)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao consultar o banco de dados: {str(e)}")


def mostrar_despesas_por_mes():
    try:
        # Consulta os anos disponíveis no banco de dados (apenas os anos)
        resultado_consulta_anos = consultar_db("SELECT DISTINCT ano FROM transacao")
        anos_disponiveis = sorted(list(set([int(row[0]) for row in resultado_consulta_anos])))

        if not anos_disponiveis:
            messagebox.showinfo("Consulta de Despesas por Mês", "Nenhum dado encontrado no banco de dados.")
            return

        janela_selecao = tk.Toplevel()
        janela_selecao.title("Selecione Ano e Mês")

        label_ano = tk.Label(janela_selecao, text="Ano:")
        label_ano.grid(row=0, column=0, padx=5, pady=5)

        ano_selecionado = tk.IntVar(value=anos_disponiveis[0] if anos_disponiveis else None)
        dropdown_ano = ttk.Combobox(janela_selecao, textvariable=ano_selecionado, values=anos_disponiveis, state="readonly")
        dropdown_ano.grid(row=0, column=1, padx=5, pady=5)

        label_mes = tk.Label(janela_selecao, text="Mês:")
        label_mes.grid(row=1, column=0, padx=5, pady=5)

        mes_selecionado = tk.IntVar()  # Inicializa sem valor
        dropdown_mes = ttk.Combobox(janela_selecao, textvariable=mes_selecionado, state="readonly")
        dropdown_mes.grid(row=1, column=1, padx=5, pady=5)

        def atualizar_meses_disponiveis(event=None):
            ano = ano_selecionado.get()
            meses_do_ano = consultar_db("SELECT DISTINCT mes FROM transacao WHERE ano = ?", (ano,))
            meses_disponiveis_para_o_ano = [row[0] for row in meses_do_ano]
            dropdown_mes['values'] = meses_disponiveis_para_o_ano
            if meses_disponiveis_para_o_ano:
                mes_selecionado.set(meses_disponiveis_para_o_ano[0])
            else:
                mes_selecionado.set(None)

        atualizar_meses_disponiveis()  # Chama inicialmente para preencher os meses
        dropdown_ano.bind("<<ComboboxSelected>>", atualizar_meses_disponiveis)

        # Botão para confirmar a seleção
        def confirmar_selecao():
            ano = ano_selecionado.get()
            mes = mes_selecionado.get()
            janela_selecao.destroy()

            try:
                despesas = consultar_despesas_por_mes(ano, mes)
                if despesas:
                    exibir_tabela(despesas)
                else:
                    messagebox.showinfo("Consulta de Despesas por Mês", f"Nenhuma despesa encontrada para {mes}/{ano}.")
            except ValueError:
                messagebox.showerror("Erro", "Dados inválidos.")
        
        botao_confirmar = tk.Button(janela_selecao, text="Confirmar", command=confirmar_selecao)
        botao_confirmar.grid(row=2, column=0, columnspan=2, pady=10)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao consultar o banco de dados: {str(e)}")

def gerar_relatorio_pdf():
    try:
        # Janela para seleção de opções do relatório
        janela_opcoes = tk.Toplevel()
        janela_opcoes.title("Opções do Relatório PDF")

        # Variável para armazenar o tipo de relatório (ano ou mês)
        tipo_relatorio = tk.StringVar(value="ano")

        # Frame para as opções de ano
        frame_ano = tk.Frame(janela_opcoes)
        frame_ano.pack(pady=10)

        tk.Label(frame_ano, text="Ano:").pack(side=tk.LEFT)
        ano_selecionado = tk.IntVar()
        resultado_consulta_anos = consultar_db("SELECT DISTINCT ano FROM transacao")
        anos_disponiveis = sorted(list(set([int(row[0]) for row in resultado_consulta_anos])))

        dropdown_ano = ttk.Combobox(frame_ano, textvariable=ano_selecionado, values=anos_disponiveis, state="readonly")
        dropdown_ano.pack(side=tk.LEFT, padx=5)

        if anos_disponiveis: # define um ano como padrão se houver
            ano_selecionado.set(anos_disponiveis[0])
        
        # Frame para as opções de mês (inicialmente oculto)
        frame_mes = tk.Frame(janela_opcoes)
        #frame_mes.pack(pady=10)  # Oculto inicialmente

        tk.Label(frame_mes, text="Mês:").pack(side=tk.LEFT)
        mes_selecionado = tk.IntVar()
        dropdown_mes = ttk.Combobox(frame_mes, textvariable=mes_selecionado, state="readonly")
        dropdown_mes.pack(side=tk.LEFT, padx=5)

        def escolher_pasta():
            pasta = filedialog.askdirectory()
            if pasta:
                gerar_pdf(pasta)

        # def gerar_pdf(pasta_destino):
        #     if tipo_relatorio.get() == "ano":
        #         ano = ano_selecionado.get()
        #         conexao = sqlite3.connect('banco/financeiro.db')
        #         cursor = conexao.cursor()
        #         cursor.execute('SELECT tipo, SUM(valor) FROM transacao GROUP BY tipo')
        #         dados = cursor.fetchall()
        #         conexao.close()
        #         nome_arquivo = os.path.join(pasta_destino, f"relatorio_ano_{ano}.pdf")
            
        #     c = canvas.Canvas(nome_arquivo, pagesize=letter)
        #     c.drawString(100, 750, "Relatório Financeiro - Resumo")
        #     y = 700
        #     for tipo, valor in dados:
        #         c.drawString(100, y, f"{tipo}: R$ {valor:.2f}")
        #         y -= 20

        #     c.save()
        #     janela_opcoes.destroy()
        def gerar_pdf(pasta_destino):
            if tipo_relatorio.get() == "ano":
                ano = ano_selecionado.get()
                conexao = sqlite3.connect('banco/financeiro.db')
                cursor = conexao.cursor()

                # Consulta modificada para retornar todas as linhas do ano
                cursor.execute(f'SELECT tipo, categoria, valor, data FROM transacao WHERE ano = ?', (ano,))  # Filtra pelo ano

                dados = cursor.fetchall()
                conexao.close()
                nome_arquivo = os.path.join(pasta_destino, f"relatorio_ano_{ano}.pdf")

            c = canvas.Canvas(nome_arquivo, pagesize=letter)
            c.drawString(100, 750, "Relatório Financeiro - Detalhado") # Título mais apropriado
            y = 700

            # Cabeçalho da tabela
            c.drawString(100, y, "Data")
            c.drawString(200, y, "Tipo")
            c.drawString(300, y, "Categoria")
            c.drawString(450, y, "Valor")
            y -= 20

            # Imprime cada linha da tabela
            for data, tipo, categoria, valor in dados:
                c.drawString(100, y, str(data))
                c.drawString(200, y, str(tipo))
                c.drawString(300, y, str(categoria))
                c.drawString(450, y, str(valor))
                y -= 20

            c.save()
            janela_opcoes.destroy()

        tk.Button(janela_opcoes, text="Escolher Pasta e Gerar PDF", command=escolher_pasta).pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")

# Função para iniciar a interface
def iniciar_interface():
    root = tk.Tk()

    root.geometry('458x337')
    root.title('Gestão Financeira')

    tk.Button(root, text='Cadastrar Transação', command=abrir_tela_cadastro).pack(pady=10)
    tk.Button(root, text='Gerar Gráfico de Pizza', command=gerar_grafico_pizza).pack(pady=10)
    tk.Button(root, text='Consultar Despesas por Ano', command=mostrar_despesas_por_ano).pack(pady=10)
    tk.Button(root, text='Consultar Despesas por Mês', command=mostrar_despesas_por_mes).pack(pady=10)
    tk.Button(root, text='Exportar Relatório PDF', command=gerar_relatorio_pdf).pack(pady=10)
    tk.Button(root, text='Sair', command=root.quit).pack(pady=10)

    root.mainloop()


