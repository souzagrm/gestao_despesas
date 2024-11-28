import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
from views.tela_cadastro import abrir_tela_cadastro
from controllers.graficos import gerar_grafico_pizza
from controllers.relatorios import exportar_pdf, consultar_despesas_por_ano, consultar_despesas_por_mes, atualizar_despesa, consultar_db
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

# Função para mostrar despesas por ano
# def mostrar_despesas_por_ano():
#     ano = simpledialog.askinteger("Consultar Despesas por Ano", "Digite o ano:")
#     if ano is None:  # Cancelar entrada
#         return

#     try:
#         despesas = consultar_despesas_por_ano(int(ano))
#         if despesas:
#             exibir_tabela(despesas)
#         else:
#             messagebox.showinfo("Consulta de Despesas por Ano", f"Nenhuma despesa encontrada para o ano {ano}.")
#     except ValueError:
#         messagebox.showerror("Erro", "Ano inválido. Por favor, insira um ano válido.")

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

# # Função para mostrar despesas por mês
# def mostrar_despesas_por_mes():
#     ano = simpledialog.askinteger("Consultar Despesas por Mês", "Digite o ano:")
#     mes = simpledialog.askinteger("Consultar Despesas por Mês", "Digite o mês (1-12):")
#     if ano is None or mes is None:
#         return

#     try:
#         despesas = consultar_despesas_por_mes(int(ano), int(mes))
#         if despesas:
#             exibir_tabela(despesas)
#         else:
#             messagebox.showinfo("Consulta de Despesas por Mês", f"Nenhuma despesa encontrada para {mes}/{ano}.")
#     except ValueError:
#         messagebox.showerror("Erro", "Dados inválidos. Por favor, insira ano e mês válidos.")

def mostrar_despesas_por_mes():

    try:
        # Consulta os anos e meses disponíveis no banco de dados
        resultado_consulta = consultar_db("SELECT DISTINCT ano, mes FROM transacao")
        anos_disponiveis = sorted(list(set([int(row[0]) for row in resultado_consulta])))
        meses_disponiveis = sorted(list(set([int(row[1]) for row in resultado_consulta])))

        if not anos_disponiveis or not meses_disponiveis:
            messagebox.showinfo("Consulta de Despesas por ano e mês", "Nenhum dado encontrado no banco de dados.")
            return

        # Cria a janela de diálogo para seleção de ano e mês
        janela_selecao = tk.Toplevel()
        janela_selecao.title("Selecione Ano e Mês")

        # Dropdown para seleção do ano
        label_ano = tk.Label(janela_selecao, text="Ano:")
        label_ano.grid(row=0, column=0, padx=5, pady=5)

        ano_selecionado = tk.IntVar(value=anos_disponiveis[0] if anos_disponiveis else None) # Valor padrão ou None se não houver anos
        dropdown_ano = ttk.Combobox(janela_selecao, textvariable=ano_selecionado, values=anos_disponiveis, state="readonly")
        dropdown_ano.grid(row=0, column=1, padx=5, pady=5)

        # Dropdown para seleção do mês
        label_mes = tk.Label(janela_selecao, text="Mês:")
        label_mes.grid(row=1, column=0, padx=5, pady=5)
        
        mes_selecionado = tk.IntVar(value=meses_disponiveis[0] if meses_disponiveis else None) # Valor padrão ou None se não houver meses
        dropdown_mes = ttk.Combobox(janela_selecao, textvariable=mes_selecionado, values=meses_disponiveis, state="readonly")
        dropdown_mes.grid(row=1, column=1, padx=5, pady=5)

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

# Função para iniciar a interface
def iniciar_interface():
    root = tk.Tk()

    root.geometry('458x337')
    root.title('Gestão Financeira')

    tk.Button(root, text='Cadastrar Transação', command=abrir_tela_cadastro).pack(pady=10)
    tk.Button(root, text='Gerar Gráfico de Pizza', command=gerar_grafico_pizza).pack(pady=10)
    tk.Button(root, text='Consultar Despesas por Ano', command=mostrar_despesas_por_ano).pack(pady=10)
    tk.Button(root, text='Consultar Despesas por Mês', command=mostrar_despesas_por_mes).pack(pady=10)
    tk.Button(root, text='Exportar Relatório PDF', command=exportar_pdf).pack(pady=10)
    tk.Button(root, text='Sair', command=root.quit).pack(pady=10)

    root.mainloop()


