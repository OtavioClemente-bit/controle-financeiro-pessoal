import sqlite3, locale
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # Configura o locale para formatação de moeda em REAL BRASILEIRO

categoria = ["Alimentação", "Medicamento", "Lazer", "Estudo"]

def criar_banco():
    conexao = sqlite3.connect("financeiro.db")
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        categoria TEXT,
        descricao TEXT,
        data TEXT NOT NULL
    )
    """)
    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    criar_banco()

janela_menu = tk.Tk()
janela_menu.title("Menu Principal")
janela_menu.geometry("700x600")
janela_menu.configure(bg="#f2f2f2")

def formatar_moeda(event, valor_var, valor_entry):
    texto = valor_var.get()
    texto = ''.join(filter(str.isdigit, texto))

    if texto:
        valor_float = int(texto) / 100
        formatado = locale.currency(valor_float, grouping=True)
        valor_var.set(formatado)
    else:
        valor_var.set(locale.currency(0, grouping=True))

    valor_entry.icursor(tk.END)

def adicionar_categoria(combo):
    janela_categoria = tk.Toplevel()
    janela_categoria.title("Adicionar Categoria")
    janela_categoria.geometry("250x150")
    janela_categoria.configure(bg="#f2f2f2")

    tk.Label(janela_categoria, text="Nome da categoria para adicionar:", font=("Arial", 12), bg="#f2f2f2").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    categoria_adicionar = tk.Entry(janela_categoria, font=("Arial", 12), width=22)
    categoria_adicionar.grid(padx=5, pady=5)

    def salvar_categoria():
        nova = categoria_adicionar.get().strip().title()

        if not nova:
            messagebox.showerror("Erro", "O nome da categoria não pode ser vazio.", parent=janela_categoria)
            return
        elif nova in categoria:
            messagebox.showerror("Erro", "Categoria já existe.", parent=janela_categoria)
            return
        else:
            try:
                conexao = sqlite3.connect("financeiro.db")
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nova,))
                conexao.commit()
                conexao.close()
                
                categoria.append(nova)
                nova_lista = carregar_categorias()
                combo.config(values=nova_lista)
                combo.set(nova)
                
                janela_categoria.destroy()

                messagebox.showinfo("Sucesso", "Categoria adicionada com sucesso!")

            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Categoria já existe.", parent=janela_categoria)

    tk.Button(janela_categoria, text="Adicionar", command=salvar_categoria, font=("Arial", 12), width=12).grid(row=3, column=0, padx=5, pady=5)

def carregar_categorias():
    conexao = sqlite3.connect("financeiro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT nome FROM categorias ORDER BY nome")
    categorias = [linha[0] for linha in cursor.fetchall()]
    conexao.close()

    if not categorias:
        categorias_padrao = ["Alimentação", "Medicamento", "Lazer", "Estudo"]
        conexao = sqlite3.connect("financeiro.db")
        cursor = conexao.cursor()
        for c in categorias_padrao:
            cursor.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (c,))
        conexao.commit()
        conexao.close()
        return categorias_padrao

    return categorias

categoria = carregar_categorias()

def cadastrar_entrada():
    
    janela_principal = tk.Toplevel()
    janela_principal.title("Controle Financeiro")
    janela_principal.geometry("500x400")
    janela_principal.configure(bg="#f2f2f2")  

    # Título
    tk.Label(janela_principal, text="Sistema de Controle Financeiro", font=("Arial", 16, "bold"), bg="#f2f2f2").pack(pady=20, anchor="center")

    formulario = tk.Frame(janela_principal, bg="#f2f2f2")
    formulario.pack()

    label_font = ("Arial", 12)
    entry_font = ("Arial", 12)

    # Tipo
    tk.Label(formulario, text="Tipo:", font=label_font, bg="#f2f2f2").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    valor_tipo = tk.StringVar()
    tipo_combo = ttk.Combobox(formulario, textvariable=valor_tipo, values=["Receita", "Despesa"], font=entry_font, width=20)
    tipo_combo.grid(row=0, column=1, padx=5, pady=5)
    tipo_combo.current(0)

    tk.Label(formulario, text="Categoria:", font=label_font, bg="#f2f2f2").grid(row=1, column=0, sticky="e", padx=5, pady=5)

    # Categoria
    frame_categoria = tk.Frame(formulario, bg="#f2f2f2")
    frame_categoria.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    valor_cat = tk.StringVar()
    categoria_escolha = ttk.Combobox(frame_categoria, textvariable=valor_cat, values=categoria, font=entry_font, width=15)
    categoria_escolha.grid(row=0, column=0)
    categoria_escolha.current(0)

    tk.Button(frame_categoria,text="+",command=lambda: adicionar_categoria(categoria_escolha),font=("Arial", 12),width=2).grid(row=0, column=1, padx=10)

    # Valor
    tk.Label(formulario, text="Valor:", font=label_font, bg="#f2f2f2").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    valor_var = tk.StringVar(value=locale.currency(0, grouping=True))
    valor_entry = tk.Entry(formulario, textvariable=valor_var, font=("Arial", 12), width=22)
    valor_entry.grid(row=2, column=1, padx=5, pady=5)
    janela_principal.update_idletasks() 

    valor_entry.bind("<KeyRelease>", lambda e: formatar_moeda(e, valor_var, valor_entry))

    # Descrição
    tk.Label(formulario, text="Descrição:", font=label_font, bg="#f2f2f2").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    valor_descricao = tk.Entry(formulario, font=entry_font, width=22)
    valor_descricao.grid(row=3, column=1, padx=5, pady=5)

    # Data
    tk.Label(formulario, text="Data:", font=label_font, bg="#f2f2f2").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    valor_data = DateEntry(formulario, font=entry_font, width=20, date_pattern="dd-mm-yyyy")
    valor_data.grid(row=4, column=1, padx=5, pady=5)

    def salvar_banco():
        tipo = valor_tipo.get()
        categoria = valor_cat.get()
        valor = valor_var.get().replace("R$", "").replace(".", "").replace(",", "").strip()
        descricao = valor_descricao.get()
        data = valor_data.get()

        if not valor.isdigit():
            messagebox.showerror("Erro", "Valor inválido.", parent=janela_principal)
            return
        valor = float(valor) / 100 
        
        conexao = sqlite3.connect("financeiro.db")
        cursor = conexao.cursor()
        cursor.execute("""
        INSERT INTO transacoes (tipo, valor, categoria, descricao, data)
        VALUES (?, ?, ?, ?, ?)
        """, (tipo, valor, categoria, descricao, data))

        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Transação salva com sucesso!", parent=janela_principal)

        valor_var.set(locale.currency(0, grouping=True)) 
        valor_descricao.delete(0, tk.END)

        atualizar_saldo_dashboard()
        
    tk.Button(janela_principal, text="Salvar", command=salvar_banco, font=label_font, width=12).pack(pady=20)

def listar_valores():
    
    janela_lista = tk.Toplevel(janela_menu)
    janela_lista.title("Lista")
    janela_lista.geometry("500x400")
    
    colunas = ("Tipo", "Categoria", "Valor", "Descrição", "Data")

    tree = ttk.Treeview(janela_lista, columns=colunas, show="headings")
    tree.pack(fill="both")

    conexao = sqlite3.connect("financeiro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, tipo, categoria, valor, descricao, data FROM transacoes")
    dados = cursor.fetchall()
    conexao.close()
    
    valor_receita = 0
    valor_despesa = 0
    
    for n in colunas:
        tree.heading(n, text=n)
        tree.column(n, width=70, anchor="center", stretch=True)
    
    for n in dados:
        if n[1] == "Receita":
            valor_receita += n[3]
        elif n[1] == "Despesa":
            valor_despesa += n[3]
        moeda_valor = locale.currency(float(n[3]), grouping=True)
        lista = (n[1], n[2], moeda_valor, n[4], n[5])  # Pulando o ID
        tree.insert("", tk.END, values=lista)
    
    saldo_final = valor_receita - valor_despesa
    cor_saldo = "green" if saldo_final >= 0 else "red"

    frame_saldos = tk.Frame(janela_lista, bg="#f2f2f2")
    frame_saldos.pack(pady=10, fill="x")
    
    ttk.Separator(janela_lista, orient="horizontal").pack(fill="x", pady=10)
    
    tk.Label(frame_saldos, text="Receita:", font=("Arial", 12, "bold"), bg="#f2f2f2", fg="green").grid(row=0, column=0, padx=10, sticky="e")
    tk.Label(frame_saldos, text=locale.currency(valor_receita, grouping=True), font=("Arial", 12), bg="#f2f2f2", fg="green").grid(row=0, column=1, sticky="w")

    tk.Label(frame_saldos, text="Despesa:", font=("Arial", 12, "bold"), bg="#f2f2f2", fg="red").grid(row=1, column=0, padx=10, sticky="e")
    tk.Label(frame_saldos, text=locale.currency(valor_despesa, grouping=True), font=("Arial", 12), bg="#f2f2f2", fg="red").grid(row=1, column=1, sticky="w")

    tk.Label(frame_saldos, text="Saldo Final:", font=("Arial", 12, "bold"), bg="#f2f2f2", fg=cor_saldo).grid(row=2, column=0, padx=10, sticky="e")
    tk.Label(frame_saldos, text=locale.currency(saldo_final, grouping=True), font=("Arial", 12, "bold"), bg="#f2f2f2", fg=cor_saldo).grid(row=2, column=1, sticky="w")

    def editar_transacao():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma transação para editar.", parent=janela_lista)
            return

        item = tree.item(selecionado)
        valores = item["values"]

        tipo_atual, categoria_atual, valor_formatado, descricao_atual, data_atual = valores

        janela_editar = tk.Toplevel(janela_lista)
        janela_editar.title("Editar Transação")
        janela_editar.geometry("400x400")
        janela_editar.configure(bg="#f2f2f2")

        # Tipo
        tk.Label(janela_editar, text="Tipo:", bg="#f2f2f2").pack()
        tipo_var = tk.StringVar(value=tipo_atual)
        tipo_combo = ttk.Combobox(janela_editar, textvariable=tipo_var, values=["Receita", "Despesa"])
        tipo_combo.pack()
        tipo_combo.set(tipo_atual)

        # Categoria
        tk.Label(janela_editar, text="Categoria:", bg="#f2f2f2").pack()
        cat_var = tk.StringVar(value=categoria_atual)
        cat_combo = ttk.Combobox(janela_editar, textvariable=cat_var, values=categoria)
        cat_combo.pack()
        cat_combo.set(categoria_atual)

        # Valor
        tk.Label(janela_editar, text="Valor:", bg="#f2f2f2").pack()
        valor_entry = tk.Entry(janela_editar, font=("Arial", 12))
        valor_entry.pack()
        valor_entry.insert(0, valor_formatado)
        valor_entry.icursor(tk.END)

        # Descrição
        tk.Label(janela_editar, text="Descrição:", bg="#f2f2f2").pack()
        desc_entry = tk.Entry(janela_editar)
        desc_entry.insert(0, descricao_atual)
        desc_entry.pack()

        # Data
        tk.Label(janela_editar, text="Data:", bg="#f2f2f2").pack()
        data_entry = DateEntry(janela_editar, date_pattern="dd-mm-yyyy")
        data_entry.set_date(data_atual)
        data_entry.pack()

        def salvar_edicao():
            novo_tipo = tipo_var.get()
            nova_categoria = cat_var.get()
            novo_valor_str = valor_entry.get()
            nova_desc = desc_entry.get()
            nova_data = data_entry.get()

            try:
                # Converter string "R$ 1.234,56" em float 1234.56
                novo_valor = novo_valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
                print("DEBUG - Valor digitado:", novo_valor)  # ✅ VERIFIQUE ISSO NO TERMINAL
                novo_valor = float(novo_valor)
            except Exception as e:
                messagebox.showerror("Erro", f"Valor inválido.\n{e}")
                return

            conexao = sqlite3.connect("financeiro.db")
            cursor = conexao.cursor()
            id_transacao = dados[tree.index(selecionado[0])][0]
            cursor.execute("""
                UPDATE transacoes
                SET tipo = ?, valor = ?, categoria = ?, descricao = ?, data = ?
                WHERE id = ?
            """, (novo_tipo, novo_valor, nova_categoria, nova_desc, nova_data, id_transacao))
            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", "Transação atualizada!")

            janela_editar.destroy()
            janela_lista.destroy()

            atualizar_saldo_dashboard()
            desenhar_grafico_pizza(globals()["painel_grafico"])
            listar_valores()

        tk.Button(janela_editar, text="Salvar", command=salvar_edicao).pack(pady=10)

    def excluir_transacao():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma transação para excluir.", parent=janela_lista)
            return

        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?", parent=janela_lista)

        if resposta:
            id_transacao = dados[tree.index(selecionado[0])][0]
            conexao = sqlite3.connect("financeiro.db")
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
            conexao.commit()
            conexao.close()

            tree.delete(selecionado[0])
            messagebox.showinfo("Sucesso", "Transação excluída!")
            janela_lista.destroy()
            atualizar_saldo_dashboard()
            desenhar_grafico_pizza(globals()["painel_grafico"])
            listar_valores()

    botoes_editar = tk.Frame(janela_lista, bg="#f2f2f2")
    botoes_editar.pack(pady=10)

    tk.Button(botoes_editar, text=" Editar", command=editar_transacao, width=12).grid(row=0, column=0, padx=10)
    tk.Button(botoes_editar, text=" Excluir", command=excluir_transacao, width=12).grid(row=0, column=1, padx=10)

def desenhar_grafico_pizza(painel):
    # Limpa o gráfico anterior, se existir
    if getattr(painel, "grafico_atual", None):
        painel.grafico_atual.get_tk_widget().destroy()

    conexao = sqlite3.connect("financeiro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT tipo, SUM(valor) FROM transacoes GROUP BY tipo")
    dados = cursor.fetchall()
    conexao.close()

    if not dados:
        return

    labels = []
    valores = []

    for tipo, soma in dados:
        labels.append(tipo)
        valores.append(soma)

    fig, ax = plt.subplots(figsize=(4, 4), dpi=90)
    ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    canvas = FigureCanvasTkAgg(fig, master=painel)
    canvas.draw()

    # Salva o novo gráfico
    painel.grafico_atual = canvas
    canvas.get_tk_widget().pack()

# Título 
tk.Label(janela_menu, text="💰 Controle Financeiro Pessoal", font=("Arial", 20, "bold"), bg="#f2f2f2").pack(pady=(20, 10))

# Painel principal h
painel_geral = tk.Frame(janela_menu, bg="#f2f2f2")
painel_geral.pack(pady=10, fill="both", expand=True)

# Painel de saldo 
painel = tk.Frame(painel_geral, bg="#f2f2f2")
painel.pack(side="left", padx=20, pady=10)

tk.Label(painel, text="Saldo atual:", font=("Arial", 13, "bold"), bg="#f2f2f2").grid(row=0, column=0, sticky="e", padx=10)
label_saldo_valor = tk.Label(painel, text="R$ 0,00", font=("Arial", 13, "bold"), fg="green", bg="#f2f2f2")
label_saldo_valor.grid(row=0, column=1, sticky="w")

tk.Label(painel, text="Receitas:", font=("Arial", 12), bg="#f2f2f2").grid(row=1, column=0, sticky="e", padx=10)
label_receita_valor = tk.Label(painel, text="R$ 0,00", font=("Arial", 12), fg="green", bg="#f2f2f2")
label_receita_valor.grid(row=1, column=1, sticky="w")

tk.Label(painel, text="Despesas:", font=("Arial", 12), bg="#f2f2f2").grid(row=2, column=0, sticky="e", padx=10)
label_despesa_valor = tk.Label(painel, text="R$ 0,00", font=("Arial", 12), fg="red", bg="#f2f2f2")
label_despesa_valor.grid(row=2, column=1, sticky="w")

# O gráfico será desenhado aqui
painel_grafico = tk.Frame(painel_geral, bg="#f2f2f2")
painel_grafico.pack(side="right", padx=20, pady=10)
painel_grafico.grafico_atual = None

def atualizar_saldo_dashboard():
    conexao = sqlite3.connect("financeiro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT tipo, valor FROM transacoes")
    dados = cursor.fetchall()
    conexao.close()

    receita = sum(v for t, v in dados if t == "Receita")
    despesa = sum(v for t, v in dados if t == "Despesa")
    saldo = receita - despesa

    label_receita_valor.config(text=locale.currency(receita, grouping=True))
    label_despesa_valor.config(text=locale.currency(despesa, grouping=True))
    label_saldo_valor.config(text=locale.currency(saldo, grouping=True), fg="green" if saldo >= 0 else "red")

    desenhar_grafico_pizza(painel_grafico)

globals()["painel_grafico"] = painel_grafico

# Botões
botoes = tk.Frame(janela_menu, bg="#f2f2f2")
botoes.pack(pady=30)

tk.Button(botoes, text="Nova Transação", command=cadastrar_entrada, font=("Arial", 12), width=20).grid(row=0, column=0, padx=10)
tk.Button(botoes, text="Ver Extrato", command=listar_valores, font=("Arial", 12), width=20).grid(row=0, column=1, padx=10)

# Atualiza tudo
atualizar_saldo_dashboard()

janela_menu.mainloop()
