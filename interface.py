# interface.py
import tkinter as tk
from tkinter import ttk, messagebox
import aurion


# ---------- Interface principal ----------
def iniciar_sistema():
    aurion.inicializar_banco()  # garante que o banco existe

    janela = tk.Tk()
    janela.title("AURION - Sistema de Gestão")
    janela.geometry("1000x650")
    janela.configure(bg="#f4f4f4")

    # === TÍTULO SUPERIOR ===
    titulo = tk.Label(
        janela,
        text="AURION - Sistema de Gestão",
        font=("Segoe UI", 18, "bold"),
        bg="#222",
        fg="white",
        pady=10
    )
    titulo.pack(fill="x")

    # === FRAMES ===
    menu = tk.Frame(janela, bg="#333", width=200)
    menu.pack(side="left", fill="y")
    conteudo = tk.Frame(janela, bg="#f4f4f4")
    conteudo.pack(side="right", fill="both", expand=True)

    # ---------- Funções auxiliares ----------
    def limpar_conteudo():
        for w in conteudo.winfo_children():
            w.destroy()

    # ---------- TELA DE PRODUTOS ----------
    def mostrar_produtos():
        limpar_conteudo()
        tk.Label(
            conteudo,
            text="📦 Lista de Produtos",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f4f4"
        ).pack(pady=10)

        frame_botoes = tk.Frame(conteudo, bg="#f4f4f4")
        frame_botoes.pack(pady=5)

        tabela = ttk.Treeview(
            conteudo,
            columns=("ID", "Marca", "Modelo", "Quantidade", "Valor", "Vendas"),
            show="headings",
            height=18
        )
        for col in ("ID", "Marca", "Modelo", "Quantidade", "Valor", "Vendas"):
            tabela.heading(col, text=col)
            tabela.column(col, anchor="center", width=140)
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            for p in aurion.listar_produtos():
                tabela.insert("", "end", values=p)

        def adicionar_produto_janela():
            win = tk.Toplevel(janela)
            win.title("Adicionar Produto")
            win.geometry("380x260")
            campos = ["Marca", "Modelo", "Quantidade", "Valor"]
            entradas = {}
            for i, campo in enumerate(campos):
                tk.Label(win, text=campo).grid(row=i, column=0, padx=10, pady=6, sticky="w")
                ent = tk.Entry(win)
                ent.grid(row=i, column=1, padx=10, pady=6)
                entradas[campo] = ent

            def salvar():
                try:
                    marca = entradas["Marca"].get().strip()
                    modelo = entradas["Modelo"].get().strip()
                    qtd = int(entradas["Quantidade"].get())
                    valor = float(entradas["Valor"].get())

                    # ✅ Correção aqui: função correta do módulo aurion
                    aurion.adicionar_produto(marca, modelo, qtd, valor)

                    messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
                    win.destroy()
                    atualizar_tabela()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar: {e}")

            tk.Button(
                win,
                text="Salvar",
                command=salvar,
                bg="#4CAF50",
                fg="white"
            ).grid(row=5, column=0, columnspan=2, pady=12)

        def excluir_produto():
            sel = tabela.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
                return
            values = tabela.item(sel, "values")
            id_prod = int(values[0])
            if messagebox.askyesno("Confirmar", f"Excluir produto ID {id_prod}?"):
                if aurion.excluir_produto(id_prod):
                    messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                    atualizar_tabela()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir o produto.")

        # Botões
        tk.Button(
            frame_botoes,
            text="➕ Adicionar",
            command=adicionar_produto_janela,
            bg="#4CAF50",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            frame_botoes,
            text="🗑️ Excluir",
            command=excluir_produto,
            bg="#F44336",
            fg="white"
        ).pack(side="left", padx=5)

        atualizar_tabela()

    # ---------- CLIENTES ----------
    def mostrar_clientes():
        limpar_conteudo()
        tk.Label(conteudo, text="👥 Lista de Clientes", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        cols = ("ID", "Nome", "Email", "Telefone", "Estado", "Cidade")
        tree = ttk.Treeview(conteudo, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for c in aurion.listar_clientes():
            tree.insert("", "end", values=c)

    # ---------- VENDAS ----------
    def mostrar_vendas():
        limpar_conteudo()
        tk.Label(conteudo, text="💰 Lista de Vendas", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        cols = ("ID", "ID_CLIENTE", "Valor", "Quantidade", "Vendedor")
        tree = ttk.Treeview(conteudo, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for v in aurion.listar_vendas():
            tree.insert("", "end", values=v)

    # ---------- RELATÓRIOS ----------
    def mostrar_relatorios():
        limpar_conteudo()
        tk.Label(conteudo, text="📊 Relatórios", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        def exibir_total_vendas():
            total = aurion.total_vendas()
            messagebox.showinfo("Total de Vendas", f"R$ {total:.2f}")

        def exibir_produtos_mais_vendidos():
            dados = aurion.produto_mais_vendido()
            texto = "\n".join([f"{m} {mod} - {v} vendas" for m, mod, v in dados])
            messagebox.showinfo("Mais Vendidos", texto or "Nenhum dado disponível.")

        def exibir_clientes_frequentes():
            dados = aurion.clientes_frequentes()
            texto = "\n".join([f"{n} - {c} compras" for n, c in dados])
            messagebox.showinfo("Clientes Frequentes", texto or "Nenhum dado disponível.")

        tk.Button(conteudo, text="Total de Vendas", command=exibir_total_vendas).pack(pady=6)
        tk.Button(conteudo, text="Produtos Mais Vendidos", command=exibir_produtos_mais_vendidos).pack(pady=6)
        tk.Button(conteudo, text="Clientes Frequentes", command=exibir_clientes_frequentes).pack(pady=6)
        
            # ---------- CLIENTES ----------
    def mostrar_clientes():
        limpar_conteudo()
        tk.Label(conteudo, text="👥 Lista de Clientes", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        frame_botoes = tk.Frame(conteudo, bg="#f4f4f4")
        frame_botoes.pack(pady=5)

        tabela = ttk.Treeview(conteudo, columns=("ID", "Nome", "Email", "Telefone", "Estado", "Cidade"), show="headings", height=18)
        for col in ("ID", "Nome", "Email", "Telefone", "Estado", "Cidade"):
            tabela.heading(col, text=col)
            tabela.column(col, anchor="center", width=140)
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            cnn = aurion.sqlite3.connect(aurion.DB_NAME)
            cur = cnn.cursor()
            cur.execute("SELECT * FROM CLIENTES")
            for c in cur.fetchall():
                tabela.insert("", "end", values=c)
            cnn.close()

        def adicionar_cliente_janela():
            win = tk.Toplevel(janela)
            win.title("Adicionar Cliente")
            win.geometry("400x330")
            campos = ["Nome", "Email", "Telefone", "Estado", "Cidade"]
            entradas = {}
            for i, campo in enumerate(campos):
                tk.Label(win, text=campo).grid(row=i, column=0, padx=10, pady=6, sticky="w")
                ent = tk.Entry(win)
                ent.grid(row=i, column=1, padx=10, pady=6)
                entradas[campo] = ent

            def salvar():
                try:
                    nome = entradas["Nome"].get().strip()
                    email = entradas["Email"].get().strip()
                    telefone = entradas["Telefone"].get().strip()
                    estado = entradas["Estado"].get().strip()
                    cidade = entradas["Cidade"].get().strip()

                    if not nome:
                        messagebox.showwarning("Aviso", "O campo Nome é obrigatório.")
                        return

                    cnn = aurion.sqlite3.connect(aurion.DB_NAME)
                    cur = cnn.cursor()
                    cur.execute(
                        "INSERT INTO CLIENTES (NOME, EMAIL, TELEFONE, ESTADO, CIDADE) VALUES (?, ?, ?, ?, ?)",
                        (nome, email, telefone, estado, cidade)
                    )
                    cnn.commit()
                    cnn.close()

                    messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
                    win.destroy()
                    atualizar_tabela()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar: {e}")

            tk.Button(win, text="Salvar", command=salvar, bg="#4CAF50", fg="white").grid(row=6, column=0, columnspan=2, pady=12)

        def excluir_cliente():
            sel = tabela.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
                return
            values = tabela.item(sel, "values")
            id_cliente = int(values[0])
            if messagebox.askyesno("Confirmar", f"Excluir cliente ID {id_cliente}?"):
                cnn = aurion.sqlite3.connect(aurion.DB_NAME)
                cur = cnn.cursor()
                cur.execute("DELETE FROM CLIENTES WHERE ID=?", (id_cliente,))
                cnn.commit()
                cnn.close()
                atualizar_tabela()

        # Botões
        tk.Button(frame_botoes, text="➕ Adicionar", command=adicionar_cliente_janela, bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botoes, text="🗑️ Excluir", command=excluir_cliente, bg="#F44336", fg="white").pack(side="left", padx=5)

        atualizar_tabela()


    # ---------- MENU ----------
    botoes = [
        ("📦 Produtos", mostrar_produtos),
        ("👥 Clientes", mostrar_clientes),
        ("💰 Vendas", mostrar_vendas),
        ("📊 Relatórios", mostrar_relatorios),
        ("💾 Backup", lambda: (aurion.backup_automatico(), messagebox.showinfo("Backup", "Backup criado com sucesso!"))),
        ("⏻ Sair", janela.quit)
    ]
    for txt, cmd in botoes:
        tk.Button(
            menu,
            text=txt,
            command=cmd,
            bg="#444",
            fg="white",
            font=("Segoe UI", 11),
            relief="flat"
        ).pack(fill="x", pady=4, padx=6)

    # Tela inicial
    mostrar_produtos()
    janela.mainloop()
