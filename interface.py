import tkinter as tk
from tkinter import ttk, messagebox
import aurion
from datetime import datetime

def iniciar_sistema():
    aurion.inicializar_banco()

    janela = tk.Tk()
    janela.title("AURION - Sistema de Gestão")
    janela.geometry("1200x700")
    janela.configure(bg="#f4f4f4")

    # === Título ===
    titulo = tk.Label(
        janela,
        text="AURION - Sistema de Gestão",
        font=("Segoe UI", 18, "bold"),
        bg="#222",
        fg="white",
        pady=10
    )
    titulo.pack(fill="x")

    # === Estrutura base ===
    menu = tk.Frame(janela, bg="#333", width=200)
    menu.pack(side="left", fill="y")

    conteudo = tk.Frame(janela, bg="#f4f4f4")
    conteudo.pack(side="right", fill="both", expand=True)

    # Função para limpar o conteúdo da área principal
    def limpar_conteudo():
        for w in conteudo.winfo_children():
            w.destroy()

    # ======================
    # PRODUTOS
    # ======================
    def mostrar_produtos():
        limpar_conteudo()
        tk.Label(conteudo, text="📦 Lista de Produtos", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        frame_botoes = tk.Frame(conteudo, bg="#f4f4f4")
        frame_botoes.pack(pady=5)

        # Frame para pesquisa
        frame_pesquisa = tk.Frame(conteudo, bg="#f4f4f4")
        frame_pesquisa.pack(pady=5)
        
        tk.Label(frame_pesquisa, text="Pesquisar:", bg="#f4f4f4").pack(side="left", padx=5)
        entrada_pesquisa = tk.Entry(frame_pesquisa, width=30)
        entrada_pesquisa.pack(side="left", padx=5)

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
                produto_formatado = (
                    p[0],
                    p[1],
                    p[2],
                    p[3],
                    f"R$ {p[4]:.2f}",
                    p[5]
                )
                tabela.insert("", "end", values=produto_formatado)

        def pesquisar_produtos():
            termo = entrada_pesquisa.get().strip().lower()
            for row in tabela.get_children():
                tabela.delete(row)
            for p in aurion.listar_produtos():
                if any(termo in str(campo).lower() for campo in p):
                    produto_formatado = (
                        p[0],
                        p[1],
                        p[2],
                        p[3],
                        f"R$ {p[4]:.2f}",
                        p[5]
                    )
                    tabela.insert("", "end", values=produto_formatado)

        def adicionar_produto():
            win = tk.Toplevel(janela)
            win.title("Adicionar Produto")
            win.geometry("380x260")
            win.resizable(False, False)

            campos = ["Marca", "Modelo", "Quantidade", "Valor"]
            entradas = {}
            for i, campo in enumerate(campos):
                tk.Label(win, text=campo, font=("Arial", 9)).grid(row=i, column=0, padx=10, pady=8, sticky="w")
                ent = tk.Entry(win, font=("Arial", 9))
                ent.grid(row=i, column=1, padx=10, pady=8, sticky="we")
                entradas[campo] = ent

            def salvar():
                try:
                    marca = entradas["Marca"].get().strip()
                    modelo = entradas["Modelo"].get().strip()
                    qtd = int(entradas["Quantidade"].get())
                    valor = float(entradas["Valor"].get())
                    
                    if not marca or not modelo:
                        messagebox.showwarning("Aviso", "⚠️ Marca e Modelo são obrigatórios.")
                        return
                    
                    if qtd < 0:
                        messagebox.showwarning("Aviso", "⚠️ Quantidade não pode ser negativa.")
                        return
                    
                    if valor < 0:
                        messagebox.showwarning("Aviso", "⚠️ Valor não pode ser negativo.")
                        return

                    aurion.adicionar_produto(marca, modelo, qtd, valor)
                    messagebox.showinfo("Sucesso", "✅ Produto adicionado com sucesso!")
                    win.destroy()
                    atualizar_tabela()
                except ValueError:
                    messagebox.showerror("Erro", "❌ Quantidade e Valor devem ser números válidos.")
                except Exception as e:
                    messagebox.showerror("Erro", f"❌ Erro ao salvar: {e}")

            btn_frame = tk.Frame(win)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
            
            tk.Button(btn_frame, text="Salvar", command=salvar, bg="#4CAF50", fg="white", 
                     font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancelar", command=win.destroy, bg="#f44336", fg="white",
                     font=("Arial", 10), width=10).pack(side="left", padx=5)

            win.columnconfigure(1, weight=1)

        def editar_produto():
            selecionado = tabela.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "⚠️ Selecione um produto para editar.")
                return
            
            item = tabela.item(selecionado[0])
            valores = item['values']
            produto_id = valores[0]

            win = tk.Toplevel(janela)
            win.title("Editar Produto")
            win.geometry("380x280")
            win.resizable(False, False)

            campos = ["Marca", "Modelo", "Quantidade", "Valor"]
            entradas = {}
            for i, campo in enumerate(campos):
                tk.Label(win, text=campo, font=("Arial", 9)).grid(row=i, column=0, padx=10, pady=8, sticky="w")
                ent = tk.Entry(win, font=("Arial", 9))
                ent.grid(row=i, column=1, padx=10, pady=8, sticky="we")
                entradas[campo] = ent

            # Preencher com dados atuais
            entradas["Marca"].insert(0, valores[1])
            entradas["Modelo"].insert(0, valores[2])
            entradas["Quantidade"].insert(0, valores[3])
            # Remover "R$ " do valor
            valor_limpo = valores[4].replace("R$ ", "").strip()
            entradas["Valor"].insert(0, valor_limpo)

            def salvar_edicao():
                try:
                    marca = entradas["Marca"].get().strip()
                    modelo = entradas["Modelo"].get().strip()
                    qtd = int(entradas["Quantidade"].get())
                    valor = float(entradas["Valor"].get())
                    
                    if not marca or not modelo:
                        messagebox.showwarning("Aviso", "⚠️ Marca e Modelo são obrigatórios.")
                        return
                    
                    if qtd < 0:
                        messagebox.showwarning("Aviso", "⚠️ Quantidade não pode ser negativa.")
                        return
                    
                    if valor < 0:
                        messagebox.showwarning("Aviso", "⚠️ Valor não pode ser negativo.")
                        return

                    sucesso = aurion.atualizar_produto(produto_id, marca, modelo, qtd, valor)
                    if sucesso:
                        messagebox.showinfo("Sucesso", "✅ Produto atualizado com sucesso!")
                        win.destroy()
                        atualizar_tabela()
                    else:
                        messagebox.showerror("Erro", "❌ Produto não encontrado.")
                except ValueError:
                    messagebox.showerror("Erro", "❌ Quantidade e Valor devem ser números válidos.")
                except Exception as e:
                    messagebox.showerror("Erro", f"❌ Erro ao atualizar: {e}")

            btn_frame = tk.Frame(win)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
            
            tk.Button(btn_frame, text="Salvar", command=salvar_edicao, bg="#4CAF50", fg="white", 
                     font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancelar", command=win.destroy, bg="#f44336", fg="white",
                     font=("Arial", 10), width=10).pack(side="left", padx=5)

            win.columnconfigure(1, weight=1)

        def excluir_produto():
            selecionado = tabela.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "⚠️ Selecione um produto para excluir.")
                return
            
            item = tabela.item(selecionado[0])
            valores = item['values']
            
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o produto?\n\n"
                f"Marca: {valores[1]}\n"
                f"Modelo: {valores[2]}"
            )
            
            if resposta:
                sucesso = aurion.excluir_produto(valores[0])
                if sucesso:
                    messagebox.showinfo("Sucesso", "✅ Produto excluído com sucesso!")
                    atualizar_tabela()
                else:
                    messagebox.showerror("Erro", "❌ Erro ao excluir produto.")

        # Botões
        tk.Button(frame_botoes, text="➕ Adicionar", command=adicionar_produto, 
                 bg="#4CAF50", fg="white", font=("Arial", 9)).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="✏️ Editar", command=editar_produto,
                 bg="#2196F3", fg="white", font=("Arial", 9)).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="🗑️ Excluir", command=excluir_produto,
                 bg="#f44336", fg="white", font=("Arial", 9)).pack(side="left", padx=2)
        
        # Botões de pesquisa
        tk.Button(frame_pesquisa, text="🔍 Pesquisar", command=pesquisar_produtos, 
                 bg="#2196F3", fg="white", font=("Arial", 9)).pack(side="left", padx=2)
        tk.Button(frame_pesquisa, text="🔄 Limpar", command=atualizar_tabela,
                 bg="#FF9800", fg="white", font=("Arial", 9)).pack(side="left", padx=2)

        atualizar_tabela()

    # ======================
    # CLIENTES
    # ======================
    def mostrar_clientes():
        limpar_conteudo()
        tk.Label(conteudo, text="👥 Lista de Clientes", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        frame_botoes = tk.Frame(conteudo, bg="#f4f4f4")
        frame_botoes.pack(pady=5)

        tabela = ttk.Treeview(
            conteudo,
            columns=("ID", "Nome", "Email", "Telefone", "Estado", "Cidade"),
            show="headings",
            height=15
        )
        for col in ("ID", "Nome", "Email", "Telefone", "Estado", "Cidade"):
            tabela.heading(col, text=col)
            tabela.column(col, anchor="center", width=140)
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        # Função para atualizar tabela
        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            for c in aurion.listar_clientes():
                tabela.insert("", "end", values=c)

        # Campo de pesquisa
        frame_pesquisa = tk.Frame(conteudo, bg="#f4f4f4")
        frame_pesquisa.pack(pady=5)
        tk.Label(frame_pesquisa, text="Pesquisar:", bg="#f4f4f4").pack(side="left", padx=5)
        entrada_pesquisa = tk.Entry(frame_pesquisa, width=30)
        entrada_pesquisa.pack(side="left", padx=5)

        def pesquisar_clientes():
            termo = entrada_pesquisa.get().strip().lower()
            for row in tabela.get_children():
                tabela.delete(row)
            for c in aurion.listar_clientes():
                if any(termo in str(campo).lower() for campo in c):
                    tabela.insert("", "end", values=c)

        def adicionar_cliente():
            win = tk.Toplevel(janela)
            win.title("Adicionar Cliente")
            win.geometry("400x330")
            win.resizable(False, False)

            campos = ["Nome", "Email", "Telefone", "Estado", "Cidade"]
            entradas = {}
            for i, campo in enumerate(campos):
                tk.Label(win, text=campo, font=("Arial", 9)).grid(row=i, column=0, padx=10, pady=6, sticky="w")
                ent = tk.Entry(win, font=("Arial", 9))
                ent.grid(row=i, column=1, padx=10, pady=6, sticky="we")
                entradas[campo] = ent

            def salvar():
                try:
                    nome = entradas["Nome"].get().strip()
                    email = entradas["Email"].get().strip()
                    telefone = entradas["Telefone"].get().strip()
                    estado = entradas["Estado"].get().strip()
                    cidade = entradas["Cidade"].get().strip()

                    if not nome:
                        messagebox.showwarning("Aviso", "⚠️ O campo Nome é obrigatório.")
                        return

                    aurion.adicionar_cliente(nome, email, telefone, estado, cidade)
                    messagebox.showinfo("Sucesso", "✅ Cliente adicionado com sucesso!")
                    win.destroy()
                    atualizar_tabela()
                except Exception as e:
                    messagebox.showerror("Erro", f"❌ Erro ao salvar: {e}")

            btn_frame = tk.Frame(win)
            btn_frame.grid(row=6, column=0, columnspan=2, pady=12)
            
            tk.Button(btn_frame, text="Salvar", command=salvar, bg="#4CAF50", fg="white",
                     font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancelar", command=win.destroy, bg="#f44336", fg="white",
                     font=("Arial", 10), width=10).pack(side="left", padx=5)

            win.columnconfigure(1, weight=1)

        tk.Button(frame_botoes, text="➕ Adicionar", command=adicionar_cliente, 
                 bg="#4CAF50", fg="white", font=("Arial", 9)).pack(side="left", padx=5)
        
        tk.Button(frame_pesquisa, text="🔍 Pesquisar", command=pesquisar_clientes, 
                 bg="#2196F3", fg="white", font=("Arial", 9)).pack(side="left", padx=5)
        tk.Button(frame_pesquisa, text="🔄 Limpar", command=atualizar_tabela, 
                 bg="#FF9800", fg="white", font=("Arial", 9)).pack(side="left", padx=5)
        
        atualizar_tabela()

    # ======================
    # VENDAS
    # ======================
    def mostrar_vendas():
        limpar_conteudo()
        tk.Label(conteudo, text="💰 Gestão de Vendas", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        frame_botoes = tk.Frame(conteudo, bg="#f4f4f4")
        frame_botoes.pack(pady=5)

        # Tabela de vendas
        tabela_vendas = ttk.Treeview(
            conteudo,
            columns=("ID", "Cliente", "Produto", "Quantidade", "Valor Total", "Vendedor", "Data"),
            show="headings",
            height=15
        )
        colunas_vendas = {
            "ID": 60,
            "Cliente": 150,
            "Produto": 150,
            "Quantidade": 100,
            "Valor Total": 120,
            "Vendedor": 120,
            "Data": 150
        }
        
        for col, width in colunas_vendas.items():
            tabela_vendas.heading(col, text=col)
            tabela_vendas.column(col, anchor="center", width=width)
        tabela_vendas.pack(fill="both", expand=True, padx=10, pady=10)

        def atualizar_tabela_vendas():
            for row in tabela_vendas.get_children():
                tabela_vendas.delete(row)
            for venda in aurion.listar_vendas():
                venda_formatada = (
                    venda[0],  # ID
                    venda[1],  # Cliente
                    venda[2],  # Produto
                    venda[3],  # Quantidade
                    f"R$ {venda[4]:.2f}",  # Valor Total
                    venda[5],  # Vendedor
                    venda[6]   # Data
                )
                tabela_vendas.insert("", "end", values=venda_formatada)

        def registrar_venda():
            win = tk.Toplevel(janela)
            win.title("Registrar Venda")
            win.geometry("500x450")
            win.resizable(False, False)

            # Combobox para selecionar produto
            tk.Label(win, text="Produto:*", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10, pady=6, sticky="w")
            combo_produto = ttk.Combobox(win, state="readonly", width=30, font=("Arial", 9))
            combo_produto.grid(row=0, column=1, padx=10, pady=6, sticky="we")

            # Combobox para selecionar cliente
            tk.Label(win, text="Cliente:*", font=("Arial", 9, "bold")).grid(row=1, column=0, padx=10, pady=6, sticky="w")
            combo_cliente = ttk.Combobox(win, state="readonly", width=30, font=("Arial", 9))
            combo_cliente.grid(row=1, column=1, padx=10, pady=6, sticky="we")

            # Campo quantidade
            tk.Label(win, text="Quantidade:*", font=("Arial", 9, "bold")).grid(row=2, column=0, padx=10, pady=6, sticky="w")
            entrada_quantidade = tk.Entry(win, font=("Arial", 9))
            entrada_quantidade.grid(row=2, column=1, padx=10, pady=6, sticky="we")

            # Campo vendedor
            tk.Label(win, text="Vendedor:*", font=("Arial", 9, "bold")).grid(row=3, column=0, padx=10, pady=6, sticky="w")
            entrada_vendedor = tk.Entry(win, font=("Arial", 9))
            entrada_vendedor.grid(row=3, column=1, padx=10, pady=6, sticky="we")

            # Informações do produto selecionado
            info_frame = tk.LabelFrame(win, text="Informações do Produto", padx=10, pady=10, font=("Arial", 9))
            info_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="we")
            
            lbl_estoque = tk.Label(info_frame, text="Estoque disponível: -", font=("Arial", 9))
            lbl_estoque.pack(anchor="w")
            lbl_valor = tk.Label(info_frame, text="Valor unitário: R$ 0.00", font=("Arial", 9))
            lbl_valor.pack(anchor="w")
            lbl_total = tk.Label(info_frame, text="Valor total: R$ 0.00", font=("Arial", 10, "bold"))
            lbl_total.pack(anchor="w")

            def carregar_produtos():
                produtos = aurion.listar_produtos()
                combo_produto['values'] = [f"{p[0]} - {p[1]} {p[2]}" for p in produtos]

            def carregar_clientes():
                clientes = aurion.listar_clientes()
                combo_cliente['values'] = [f"{c[0]} - {c[1]}" for c in clientes]

            def atualizar_info_produto(event=None):
                try:
                    produto_selecionado = combo_produto.get()
                    if produto_selecionado:
                        produto_id = int(produto_selecionado.split(" - ")[0])
                        produto = aurion.buscar_produto(produto_id)
                        if produto:
                            lbl_estoque.config(text=f"Estoque disponível: {produto[3]}")
                            lbl_valor.config(text=f"Valor unitário: R$ {produto[4]:.2f}")
                            
                            # Calcular valor total
                            try:
                                qtd = int(entrada_quantidade.get() or 0)
                                total = qtd * produto[4]
                                lbl_total.config(text=f"Valor total: R$ {total:.2f}")
                            except:
                                lbl_total.config(text=f"Valor total: R$ 0.00")
                except:
                    pass

            def calcular_total(event=None):
                atualizar_info_produto()

            # Carregar dados
            carregar_produtos()
            carregar_clientes()

            # Vincular eventos
            combo_produto.bind("<<ComboboxSelected>>", atualizar_info_produto)
            entrada_quantidade.bind("<KeyRelease>", calcular_total)

            def salvar_venda():
                try:
                    # Validar dados
                    if not combo_produto.get():
                        messagebox.showwarning("Aviso", "⚠️ Selecione um produto.")
                        return
                    if not combo_cliente.get():
                        messagebox.showwarning("Aviso", "⚠️ Selecione um cliente.")
                        return
                    
                    quantidade = int(entrada_quantidade.get())
                    if quantidade <= 0:
                        messagebox.showwarning("Aviso", "⚠️ Quantidade deve ser maior que zero.")
                        return

                    vendedor = entrada_vendedor.get().strip()
                    if not vendedor:
                        messagebox.showwarning("Aviso", "⚠️ Informe o nome do vendedor.")
                        return

                    # Obter IDs
                    produto_id = int(combo_produto.get().split(" - ")[0])
                    cliente_id = int(combo_cliente.get().split(" - ")[0])

                    # Validar estoque
                    if not aurion.validar_venda(produto_id, quantidade):
                        produto = aurion.buscar_produto(produto_id)
                        messagebox.showerror("Erro", f"❌ Estoque insuficiente! Disponível: {produto[3]}")
                        return

                    # Registrar venda
                    sucesso, mensagem = aurion.registrar_venda(produto_id, cliente_id, quantidade, vendedor)
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", f"✅ {mensagem}")
                        win.destroy()
                        atualizar_tabela_vendas()
                    else:
                        messagebox.showerror("Erro", f"❌ {mensagem}")
                        
                except ValueError:
                    messagebox.showerror("Erro", "❌ Quantidade deve ser um número válido.")
                except Exception as e:
                    messagebox.showerror("Erro", f"❌ Erro ao registrar venda: {e}")

            btn_frame = tk.Frame(win)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
            
            tk.Button(btn_frame, text="Registrar Venda", command=salvar_venda, bg="#4CAF50", fg="white", 
                     font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancelar", command=win.destroy, bg="#f44336", fg="white",
                     font=("Arial", 10), width=10).pack(side="left", padx=5)

            win.columnconfigure(1, weight=1)

        tk.Button(frame_botoes, text="➕ Nova Venda", command=registrar_venda, 
                 bg="#4CAF50", fg="white", font=("Arial", 9)).pack(side="left", padx=5)
        atualizar_tabela_vendas()

    # ======================
    # RELATÓRIOS
    # ======================
    def mostrar_relatorios():
        limpar_conteudo()
        tk.Label(conteudo, text="📊 Relatórios e Estatísticas", font=("Segoe UI", 14, "bold"), bg="#f4f4f4").pack(pady=10)

        # Frame para controles de relatório
        frame_controles = tk.Frame(conteudo, bg="#f4f4f4")
        frame_controles.pack(pady=10, fill="x")

        # Frame para métricas
        frame_metricas = tk.Frame(conteudo, bg="#f4f4f4")
        frame_metricas.pack(pady=10, fill="x")

        # Cards de métricas - CORREÇÃO: Usar aurion.total_vendas() diretamente
        total_vendas_valor = aurion.total_vendas()
        metricas_data = [
            ("💰 Total Vendido", f"R$ {total_vendas_valor:.2f}", "#4CAF50"),
            ("📦 Produtos Cadastrados", str(len(aurion.listar_produtos())), "#2196F3"),
            ("👥 Clientes Cadastrados", str(len(aurion.listar_clientes())), "#FF9800"),
            ("🛒 Vendas Realizadas", str(len(aurion.listar_vendas())), "#9C27B0")
        ]

        cards = []
        for i, (titulo, valor, cor) in enumerate(metricas_data):
            card = tk.Frame(frame_metricas, bg=cor, relief="raised", bd=1)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            lbl_titulo = tk.Label(card, text=titulo, bg=cor, fg="white", font=("Arial", 10, "bold"))
            lbl_titulo.pack(pady=(10, 5))
            
            lbl_valor = tk.Label(card, text=valor, bg=cor, fg="white", font=("Arial", 12, "bold"))
            lbl_valor.pack(pady=(0, 10))
            
            cards.append(card)
            
            # Configurar peso das colunas
            frame_metricas.columnconfigure(i, weight=1)

        # Tabela de relatórios detalhados
        notebook = ttk.Notebook(conteudo)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba: Produtos Mais Vendidos
        frame_produtos_vendidos = ttk.Frame(notebook)
        notebook.add(frame_produtos_vendidos, text="🏆 Produtos Mais Vendidos")

        tabela_produtos = ttk.Treeview(
            frame_produtos_vendidos,
            columns=("Produto", "Vendas", "Estoque", "Valor Unitário"),
            show="headings"
        )
        for col in ("Produto", "Vendas", "Estoque", "Valor Unitário"):
            tabela_produtos.heading(col, text=col)
            tabela_produtos.column(col, anchor="center", width=180)
        tabela_produtos.pack(fill="both", expand=True, padx=5, pady=5)

        # Aba: Clientes Frequentes
        frame_clientes_frequentes = ttk.Frame(notebook)
        notebook.add(frame_clientes_frequentes, text="👥 Clientes Frequentes")

        tabela_clientes = ttk.Treeview(
            frame_clientes_frequentes,
            columns=("Cliente", "Compras", "Total Gasto"),
            show="headings"
        )
        for col in ("Cliente", "Compras", "Total Gasto"):
            tabela_clientes.heading(col, text=col)
            tabela_clientes.column(col, anchor="center", width=200)
        tabela_clientes.pack(fill="both", expand=True, padx=5, pady=5)

        # Aba: Últimas Vendas
        frame_ultimas_vendas = ttk.Frame(notebook)
        notebook.add(frame_ultimas_vendas, text="📈 Últimas Vendas")

        tabela_ultimas_vendas = ttk.Treeview(
            frame_ultimas_vendas,
            columns=("Data", "Cliente", "Produto", "Quantidade", "Valor", "Vendedor"),
            show="headings"
        )
        for col in ("Data", "Cliente", "Produto", "Quantidade", "Valor", "Vendedor"):
            tabela_ultimas_vendas.heading(col, text=col)
            tabela_ultimas_vendas.column(col, anchor="center", width=130)
        tabela_ultimas_vendas.pack(fill="both", expand=True, padx=5, pady=5)

        def atualizar_relatorios():
            # Atualizar produtos mais vendidos
            for row in tabela_produtos.get_children():
                tabela_produtos.delete(row)
            produtos = aurion.listar_produtos()
            produtos_ordenados = sorted(produtos, key=lambda x: x[5], reverse=True)  # Ordenar por vendas
            for produto in produtos_ordenados[:10]:  # Top 10
                tabela_produtos.insert("", "end", values=(
                    f"{produto[1]} {produto[2]}",
                    produto[5],  # Vendas
                    produto[3],  # Estoque
                    f"R$ {produto[4]:.2f}"  # Valor Unitário
                ))

            # Atualizar clientes frequentes
            for row in tabela_clientes.get_children():
                tabela_clientes.delete(row)
            clientes_frequentes = aurion.clientes_frequentes(10)  # Top 10
            for cliente in clientes_frequentes:
                # Calcular total gasto pelo cliente
                total_gasto = 0
                vendas_cliente = [v for v in aurion.listar_vendas() if v[1] == cliente[0]]
                for venda in vendas_cliente:
                    total_gasto += venda[4]
                
                tabela_clientes.insert("", "end", values=(
                    cliente[0],  # Nome
                    cliente[1],  # Compras
                    f"R$ {total_gasto:.2f}"  # Total Gasto
                ))

            # Atualizar últimas vendas
            for row in tabela_ultimas_vendas.get_children():
                tabela_ultimas_vendas.delete(row)
            vendas = aurion.listar_vendas()[:15]  # Últimas 15 vendas
            for venda in vendas:
                tabela_ultimas_vendas.insert("", "end", values=(
                    venda[6],  # Data
                    venda[1],  # Cliente
                    venda[2],  # Produto
                    venda[3],  # Quantidade
                    f"R$ {venda[4]:.2f}",  # Valor
                    venda[5]   # Vendedor
                ))

            # Atualizar métricas - CORREÇÃO: Recalcular o total de vendas
            total_vendas_atualizado = aurion.total_vendas()
            for i, card in enumerate(cards):
                if i == 0:
                    card.winfo_children()[1].config(text=f"R$ {total_vendas_atualizado:.2f}")
                elif i == 1:
                    card.winfo_children()[1].config(text=str(len(aurion.listar_produtos())))
                elif i == 2:
                    card.winfo_children()[1].config(text=str(len(aurion.listar_clientes())))
                elif i == 3:
                    card.winfo_children()[1].config(text=str(len(aurion.listar_vendas())))

        # Botão para atualizar relatórios
        tk.Button(frame_controles, text="🔄 Atualizar Relatórios", command=atualizar_relatorios, 
                 bg="#2196F3", fg="white", font=("Arial", 10)).pack(pady=5)

        # Atualizar relatórios inicialmente
        atualizar_relatorios()

    # ======================
    # MENU PRINCIPAL
    # ======================
    botoes_menu = [
        ("📦 Produtos", mostrar_produtos),
        ("👥 Clientes", mostrar_clientes),
        ("💰 Vendas", mostrar_vendas),
        ("📊 Relatórios", mostrar_relatorios),
        ("💾 Backup", lambda: (aurion.backup_automatico(), messagebox.showinfo("Backup", "💾 Backup criado com sucesso!"))),
        ("⏻ Sair", janela.quit)
    ]

    for txt, cmd in botoes_menu:
        tk.Button(
            menu,
            text=txt,
            command=cmd,
            bg="#444",
            fg="white",
            font=("Segoe UI", 11),
            relief="flat",
            anchor="w",
            padx=20
        ).pack(fill="x", pady=2, padx=5)

    # Abre com tela de produtos
    mostrar_produtos()
    janela.mainloop()

# Para executar diretamente este arquivo
if __name__ == "__main__":
    iniciar_sistema()