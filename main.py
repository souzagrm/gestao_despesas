import os
from views.tela_principal import iniciar_interface
from executar_banco import criar_tabelas # Importa a nova função

def main():
    #Cria o banco de dados se ele não existir (first run)
    caminho_banco = os.path.join('banco', 'financeiro.db')
    if not os.path.exists(caminho_banco):
        criar_tabelas()

    iniciar_interface()

from views.tela_principal import iniciar_interface

if __name__ == "__main__":
    main()
