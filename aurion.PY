import sqlite3
from datetime import datetime
import os
import shutil

DB = "aurion.db"

# ==========================
# BANCO DE DADOS
# ==========================
def conectar():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB)

def inicializar_banco():
    """Cria o banco e as tabelas se não existirem."""
    conn = conectar()
    cur = conn.cursor()

    # Tabela de produtos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor REAL NOT NULL,
            vendas INTEGER DEFAULT 0
        )
    """)

    # Tabela de clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            estado TEXT,
            cidade TEXT
        )
    """)

    # Tabela de vendas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            valor_total REAL,
            vendedor TEXT,
            data TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conn.commit()
    conn.close()

# ==========================
# PRODUTOS
# ==========================
def listar_produtos():
    """Retorna todos os produtos cadastrados."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos ORDER BY id DESC")
    dados = cur.fetchall()
    conn.close()
    return dados

def adicionar_produto(marca, modelo, quantidade, valor):
    """Adiciona um novo produto ao banco."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO produtos (marca, modelo, quantidade, valor) VALUES (?, ?, ?, ?)",
        (marca, modelo, quantidade, valor)
    )
    conn.commit()
    conn.close()

def buscar_produto(produto_id):
    """Busca um produto pelo ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE id=?", (produto_id,))
    produto = cur.fetchone()
    conn.close()
    return produto

def atualizar_produto(produto_id, marca, modelo, quantidade, valor):
    """Atualiza informações de um produto."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE produtos
        SET marca=?, modelo=?, quantidade=?, valor=?
        WHERE id=?
    """, (marca, modelo, quantidade, valor, produto_id))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

def excluir_produto(produto_id):
    """Exclui um produto pelo ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

# ==========================
# CLIENTES
# ==========================
def listar_clientes():
    """Lista todos os clientes cadastrados."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY id DESC")
    dados = cur.fetchall()
    conn.close()
    return dados

def adicionar_cliente(nome, email, telefone, estado, cidade):
    """Adiciona um novo cliente."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (nome, email, telefone, estado, cidade)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, email, telefone, estado, cidade))
    conn.commit()
    conn.close()

def buscar_cliente(cliente_id):
    """Busca um cliente pelo ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
    cliente = cur.fetchone()
    conn.close()
    return cliente

def atualizar_cliente(cliente_id, nome, email, telefone, estado, cidade):
    """Atualiza informações de um cliente."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clientes
        SET nome=?, email=?, telefone=?, estado=?, cidade=?
        WHERE id=?
    """, (nome, email, telefone, estado, cidade, cliente_id))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

def excluir_cliente(cliente_id):
    """Exclui um cliente pelo ID."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

# ==========================
# VENDAS
# ==========================
def listar_vendas():
    """Lista todas as vendas com informações de cliente e produto."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, c.nome, p.marca || ' ' || p.modelo as produto, 
               v.quantidade, v.valor_total, v.vendedor, v.data
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.data DESC
    """)
    dados = cur.fetchall()
    conn.close()
    return dados

def validar_venda(produto_id, quantidade):
    """Valida se há estoque suficiente para uma venda."""
    produto = buscar_produto(produto_id)
    return produto and produto[3] >= quantidade

def registrar_venda(produto_id, cliente_id, quantidade, vendedor):
    """Registra uma nova venda e atualiza o estoque."""
    conn = conectar()
    cur = conn.cursor()

    try:
        # Verificar se produto existe
        produto = buscar_produto(produto_id)
        if not produto:
            return False, "Produto não encontrado."

        # Verificar se cliente existe
        cliente = buscar_cliente(cliente_id)
        if not cliente:
            return False, "Cliente não encontrado."

        estoque_atual = produto[3]
        if estoque_atual < quantidade:
            return False, f"Estoque insuficiente ({estoque_atual} disponíveis)."

        valor_total = produto[4] * quantidade
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar venda
        cur.execute("""
            INSERT INTO vendas (cliente_id, produto_id, quantidade, valor_total, vendedor, data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cliente_id, produto_id, quantidade, valor_total, vendedor, data))

        # Atualiza estoque e contador de vendas
        cur.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?, vendas = vendas + ?
            WHERE id = ?
        """, (quantidade, quantidade, produto_id))

        conn.commit()
        return True, f"Venda registrada com sucesso! Total: R$ {valor_total:.2f}"
    
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao registrar venda: {str(e)}"
    
    finally:
        conn.close()

# ==========================
# RELATÓRIOS
# ==========================
def total_vendas():
    """Retorna o valor total de todas as vendas."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT SUM(valor_total) FROM vendas")
    resultado = cur.fetchone()[0]
    conn.close()
    
    # CORREÇÃO: Garantir que retorna 0.0 quando não há vendas (resultado é None)
    if resultado is None:
        return 0.0
    return float(resultado)

def clientes_frequentes(limite=10):
    """Retorna os clientes com mais compras."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.nome, COUNT(v.id) AS compras
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        GROUP BY c.id, c.nome
        ORDER BY compras DESC
        LIMIT ?
    """, (limite,))
    dados = cur.fetchall()
    conn.close()
    return dados

def produtos_mais_vendidos(limite=10):
    """Retorna os produtos mais vendidos."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.marca || ' ' || p.modelo as produto, 
               SUM(v.quantidade) AS total_vendido,
               SUM(v.valor_total) as total_arrecadado
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.id, p.marca, p.modelo
        ORDER BY total_vendido DESC
        LIMIT ?
    """, (limite,))
    dados = cur.fetchall()
    conn.close()
    return dados

def obter_estatisticas_vendas():
    """Retorna estatísticas completas para relatórios."""
    conn = conectar()
    cur = conn.cursor()
    
    # Total de vendas e valor total - CORREÇÃO: Usar COALESCE para evitar None
    cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM vendas")
    total_vendas, total_arrecadado = cur.fetchone()
    
    # Total de produtos
    cur.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cur.fetchone()[0]
    
    # Total de clientes
    cur.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cur.fetchone()[0]
    
    # Clientes ativos (que fizeram pelo menos uma compra)
    cur.execute("SELECT COUNT(DISTINCT cliente_id) FROM vendas")
    clientes_ativos_result = cur.fetchone()[0]
    clientes_ativos = clientes_ativos_result if clientes_ativos_result is not None else 0
    
    # Produto mais vendido
    cur.execute("""
        SELECT p.marca || ' ' || p.modelo, SUM(v.quantidade)
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.id
        ORDER BY SUM(v.quantidade) DESC
        LIMIT 1
    """)
    produto_mais_vendido = cur.fetchone()
    
    conn.close()
    
    return {
        'total_vendas': total_vendas or 0,
        'total_arrecadado': total_arrecadado or 0,
        'total_produtos': total_produtos,
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'produto_mais_vendido': produto_mais_vendido[0] if produto_mais_vendido else "Nenhum"
    }

# ==========================
# BACKUP
# ==========================
def backup_automatico():
    """Cria uma cópia de segurança do banco de dados."""
    if not os.path.exists(DB):
        raise FileNotFoundError("Banco de dados não encontrado.")

    pasta_backup = "backups"
    os.makedirs(pasta_backup, exist_ok=True)

    data = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(pasta_backup, f"aurion_backup_{data}.db")
    shutil.copy(DB, destino)
    return destino

# ==========================
# DADOS DE EXEMPLO (para desenvolvimento)
# ==========================
def criar_dados_exemplo():
    """Cria dados de exemplo para testes."""
    conn = conectar()
    cur = conn.cursor()
    
    # Limpar tabelas
    cur.execute("DELETE FROM vendas")
    cur.execute("DELETE FROM produtos")
    cur.execute("DELETE FROM clientes")
    
    # Inserir produtos de exemplo
    produtos_exemplo = [
        ('Samsung', 'Galaxy S23', 50, 2999.99),
        ('Apple', 'iPhone 15', 30, 5999.99),
        ('Xiaomi', 'Redmi Note 12', 100, 1299.99),
        ('Motorola', 'Moto G84', 75, 1499.99),
        ('Samsung', 'Galaxy A54', 60, 1899.99)
    ]
    
    cur.executemany("""
        INSERT INTO produtos (marca, modelo, quantidade, valor)
        VALUES (?, ?, ?, ?)
    """, produtos_exemplo)
    
    # Inserir clientes de exemplo
    clientes_exemplo = [
        ('João Silva', 'joao@email.com', '(11) 9999-8888', 'SP', 'São Paulo'),
        ('Maria Santos', 'maria@email.com', '(21) 7777-6666', 'RJ', 'Rio de Janeiro'),
        ('Pedro Oliveira', 'pedro@email.com', '(31) 5555-4444', 'MG', 'Belo Horizonte'),
        ('Ana Costa', 'ana@email.com', '(41) 3333-2222', 'PR', 'Curitiba'),
        ('Carlos Lima', 'carlos@email.com', '(51) 1111-0000', 'RS', 'Porto Alegre')
    ]
    
    cur.executemany("""
        INSERT INTO clientes (nome, email, telefone, estado, cidade)
        VALUES (?, ?, ?, ?, ?)
    """, clientes_exemplo)
    
    conn.commit()
    conn.close()

# ==========================
# INICIALIZAÇÃO
# ==========================
if __name__ == "__main__":
    inicializar_banco()
    print("✅ Banco de dados inicializado com sucesso!")
    print("✅ Tabelas criadas/verificadas: produtos, clientes, vendas")