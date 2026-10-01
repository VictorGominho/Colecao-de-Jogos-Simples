import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Iniciar o banco de dados
def iniciar_db():
    conexao = sqlite3.connect("jogos.db")
    cursor = conexao.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ano INTEGER NOT NULL,
            concluido BOOLEAN NOT NULL
        )
    """ 
    )
    conexao.commit()
    conexao.close()

# Função de manipulação de dados
def inserir_dados():
    # Valores obtidos com tk.Entry
    nome = entrada_nome.get()
    ano = entrada_ano.get()
    # Valor do checkbutton (True/False)
    concluido = entrada_concluido.get()

    # Verifica se um dos campos (ou ambos) estão vazios
    if nome == "" or ano == "":
        messagebox.showwarning("Atenção", "Por favor, preencha ambos os campos.")
        return

    # Checa para saber se "ano" é um número
    if not ano.isdigit():
        messagebox.showerror("Erro", "Preencha o ano apenas com números.")
        return

    # Inserindo valores
    conexao = sqlite3.connect("jogos.db")
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO jogos (nome, ano, concluido) VALUES (?,?,?)",
        (nome, int(ano), concluido)
    )
    conexao.commit()
    conexao.close()

    # Limpando os campos
    entrada_nome.delete(0, tk.END)
    entrada_ano.delete(0, tk.END)
    entrada_concluido.set(False)

    messagebox.showinfo("Sucesso", "Dados salvos com sucesso.")
    atualizar_db()

# Função para remover dados da tabela
def remover_dados():
    item_escolhido = tabela.selection()
    # Verifica se um item foi selecionado
    if not item_escolhido:
        messagebox.showwarning("Atenção", "Por favor, selecione um item para remover.")
        return

    # Obtém o ID do item selecionado
    valores = tabela.item(item_escolhido, "values")
    id_jogo = valores[0]

    # Confirmação para remover o item
    if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o jogo '{valores[1]}'?"):
        conexao = sqlite3.connect("jogos.db")
        cursor = conexao.cursor()
        cursor.execute(
            "DELETE FROM jogos WHERE id = ?", (id_jogo)
        )
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Jogo removido com sucesso.")
        atualizar_db()

# Função para alternar o estado de 'concluído'
def alterna_concluido():
    item_escolhido = tabela.selection()
    # Verifica se um item foi selecionado
    if not item_escolhido:
        messagebox.showwarning("Atenção", "Por favor, selecione um item para remover.")
        return
    # Obtém o ID do item selecionado
    valores = tabela.item(item_escolhido, "values")
    id_jogo = valores[0]
    status_atual = valores[3]

    # Inverte o estado
    novo_status = False if status_atual == "Sim" else True

    conexao = sqlite3.connect("jogos.db")
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE jogos SET concluido = ? WHERE id = ?", (novo_status, id_jogo)
    )
    conexao.commit()
    conexao.close()

    atualizar_db()
    

# Função para mostrar a tabela
def atualizar_db():
    for linha in tabela.get_children():
        tabela.delete(linha)

    filtro = combo_filtro.get()
    conexao = sqlite3.connect("jogos.db")
    cursor = conexao.cursor()

    # Modifica a query SQL dependendo do filtro selecionado
    if filtro == "Concluídos":
        cursor.execute(
            "SELECT * FROM jogos WHERE concluido = 1"
        )
    elif filtro == "Não Concluídos":
        cursor.execute(
            "SELECT * FROM jogos WHERE concluido = 0"
        )
    else:
        cursor.execute(
            "SELECT * FROM jogos"
        )

    dados = cursor.fetchall()
    conexao.close()

    for linha in dados:
        #Transformando o tipo Booleano do banco em texto para a interface
        id, nome, ano, comp = linha
        status_text = "Sim" if comp == 1 else "Não"

        tabela.insert("", tk.END, values=(id, nome, ano, status_text))

# Abrindo a janela da aplicação
iniciar_db()

janela = tk.Tk()
janela.title("Coleção de Jogos")
janela.geometry("550x550")

# Campo: Nome
lbl_nome = tk.Label(janela, text="Nome:")
lbl_nome.pack(pady=2)
entrada_nome = tk.Entry(janela, width=40)
entrada_nome.pack()

# Campo: Ano
lbl_ano = tk.Label(janela, text="Ano:")
lbl_ano.pack(pady=2)
entrada_ano = tk.Entry(janela, width=15)
entrada_ano.pack()

# Campo: Concluído (Checkbutton)
entrada_concluido = tk.BooleanVar()
chk_concluido = tk.Checkbutton(
    janela, text="Concluído", variable=entrada_concluido
)
chk_concluido.pack(pady=5)

# Botão: Salvar
btn_salvar = tk.Button(janela, text="Salvar na lista", command=inserir_dados)
btn_salvar.pack(pady=5)

# Frame: Filtros e seleção
frame_opcoes = tk.Frame(janela)
frame_opcoes.pack(pady=5, fill=tk.X, padx=10)

lbl_filtrar = tk.Label(frame_opcoes, text="Filtrar por:")
lbl_filtrar.pack(side=tk.LEFT, padx=5)

# Combobox: Filtro
combo_filtro = ttk.Combobox(frame_opcoes, values=["Todos", "Concluídos", "Não Concluídos"], state="readonly", width=15)
combo_filtro.set("Todos") # Escolha padrão
combo_filtro.bind("<<ComboboxSelected>>", lambda e: atualizar_db()) # Atualiza a tabela se o filtro mudar
combo_filtro.pack(side=tk.LEFT, padx=5)

# Botão: Remover
btn_remover = tk.Button(frame_opcoes, text="Remover", command=remover_dados, fg="red")
btn_remover.pack(side=tk.RIGHT, padx=5)

# Botão: Alternar Status
btn_alternar = tk.Button(frame_opcoes, text="Alternar Status", command=alterna_concluido)
btn_alternar.pack(side=tk.RIGHT, padx=5)

# Tabela
colunas = ("ID", "Nome", "Ano", "Concluído")
tabela = ttk.Treeview(janela, columns=colunas, show="headings")

# Cabeçalho e Dimensões da Tabela
tabela.heading("ID", text="ID")
tabela.column("ID", width=50, anchor=tk.CENTER)

tabela.heading("Nome", text="Nome")
tabela.column("Nome", width=200)

tabela.heading("Ano", text="Ano")
tabela.column("Ano", width=100, anchor=tk.CENTER)

tabela.heading("Concluído", text="Concluído")
tabela.column("Concluído", width=100, anchor=tk.CENTER)

tabela.pack(pady=10, fill=tk.BOTH, expand=True)

# Carrega os dados ao iniciar o app
atualizar_db()

janela.mainloop()