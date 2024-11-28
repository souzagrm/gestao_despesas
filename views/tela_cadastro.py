# import tkinter as tk
# from tkinter import ttk
# from controllers.cadastro import salvar_transacao


# def abrir_tela_cadastro():

#     cadastro = tk.Toplevel()
#     cadastro.title('Cadastro de Transações')

#     tk.Label(cadastro, text='Tipo').grid(row=0, column=0, padx=5, pady=5)
#     tipo = ttk.Combobox(cadastro, values=['Despesa', 'Receita'])
#     tipo.grid(row=0, column=1, padx=5, pady=5)

#     tk.Label(cadastro, text='Categoria').grid(row=1, column=0, padx=5, pady=5)
#     categoria = tk.Entry(cadastro)
#     categoria.grid(row=1, column=1, padx=5, pady=5)

#     tk.Label(cadastro, text='Valor').grid(row=2, column=0, padx=5, pady=5)
#     valor = tk.Entry(cadastro)
#     valor.grid(row=2, column=1, padx=5, pady=5)

#     tk.Label(cadastro, text='Data (DD/MM/AAAA)').grid(row=3, column=0, padx=5, pady=5)
#     data = tk.Entry(cadastro)
#     data.grid(row=3, column=1, padx=5, pady=5)

#     tk.Button(cadastro, text='Salvar', command=lambda: salvar_transacao(
#         tipo.get(), categoria.get(), float(valor.get().replace(',', '.')), data.get()
#     )).grid(row=4, columnspan=2, pady=10)

import tkinter as tk
from tkinter import ttk
from controllers.cadastro import salvar_transacao


def abrir_tela_cadastro():

    def on_data_key(event):
        texto = data_entry.get()
        if len(texto) == 2 or len(texto) == 5:
            if texto[-1] != "/":
                data_entry.insert(tk.END, "/")

    # Função para salvar a transação e atualizar a interface
    def salvar_e_exibir_mensagem():
        try:
            # Valida se os campos estão preenchidos corretamente
            if not tipo.get() or not categoria.get() or not valor.get() or not data_entry.get():
                mensagem.config(text="Por favor, preencha todos os campos.", fg="red")
                return

            # Converte o valor para float e chama a função salvar_transacao
            salvar_transacao(
                tipo.get(),
                categoria.get(),
                float(valor.get().replace(',', '.')),
                data_entry.get()
            )

            # Exibe a mensagem de sucesso
            mensagem.config(text="Despesa cadastrada com sucesso!", fg="green")

            # Limpa os campos
            tipo.set('')
            categoria.delete(0, tk.END)
            valor.delete(0, tk.END)
            data_entry.delete(0, tk.END)

        except ValueError:
            # Trata erro de conversão do valor
            mensagem.config(text="Erro: Verifique se o valor está correto (use números).", fg="red")

        except Exception as e:
            # Trata outros erros e exibe a mensagem correspondente
            mensagem.config(text=f"Erro ao cadastrar: {str(e)}", fg="red")

    # Criação da janela
    cadastro = tk.Toplevel()
    cadastro.title('Cadastro de Transações')

    # Campos da interface
    tk.Label(cadastro, text='Tipo').grid(row=0, column=0, padx=5, pady=5)
    tipo = ttk.Combobox(cadastro, values=['Despesa', 'Receita'])
    tipo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(cadastro, text='Categoria').grid(row=1, column=0, padx=5, pady=5)
    categoria = tk.Entry(cadastro)
    categoria.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(cadastro, text='Valor').grid(row=2, column=0, padx=5, pady=5)
    valor = tk.Entry(cadastro)
    valor.grid(row=2, column=1, padx=5, pady=5)

    data_label = ttk.Label(cadastro, text="Data (DD/MM/YYYY):")
    data_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

    data_entry = ttk.Entry(cadastro)
    data_entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
    data_entry.bind("<KeyRelease>", on_data_key)

    # Botão Salvar
    tk.Button(cadastro, text='Salvar', command=salvar_e_exibir_mensagem).grid(row=4, columnspan=2, pady=10)

    # Label para exibir mensagens de sucesso ou erro
    mensagem = tk.Label(cadastro, text='', fg='green')
    mensagem.grid(row=5, columnspan=2, pady=5)

