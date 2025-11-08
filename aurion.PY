# aurion.py
import sqlite3
import os
import shutil
from datetime import datetime
from typing import List, Tuple, Optional

DB_NAME = "aurion.DB"

# -------------------------
# Inicialização / util
# -------------------------
def get_conn():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PRODUTOS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MARCA TEXT,
            MODELO TEXT,
            QUANTIDADE INTEGER,
            VALOR REAL,
            VENDAS_FEITAS INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS CLIENTES(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOME TEXT,
            EMAIL TEXT,
            TELEFONE TEXT,
            ESTADO TEXT,
            CIDADE TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS VENDAS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_CLIENTE INTEGER,
            VALOR REAL,
            QUANTIDADE INTEGER,
            VENDEDOR TEXT,
            FOREIGN KEY(ID_CLIENTE) REFERENCES CLIENTES(ID)
        )
    ''')
    cnn.commit()
    cnn.close()

# -------------------------
# Backup
# -------------------------
def backup_automatico(dest_folder: str = "backups") -> str:
    os.makedirs(dest_folder, exist_ok=True)
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(dest_folder, f"aurion_backup_{data_atual}.DB")
    shutil.copy(DB_NAME, destino)
    return destino

# -------------------------
# Produtos
# -------------------------
def adicionar_produto(marca: str, modelo: str, quantidade: int, valor: float) -> None:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('''
        INSERT INTO PRODUTOS (MARCA, MODELO, QUANTIDADE, VALOR, VENDAS_FEITAS)
        VALUES (?, ?, ?, ?, 0)
    ''', (marca, modelo, quantidade, valor))
    cnn.commit()
    cnn.close()

def atualizar_produto(id_produto: int, marca: str, modelo: str, quantidade: int, valor: float) -> bool:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('UPDATE PRODUTOS SET MARCA=?, MODELO=?, QUANTIDADE=?, VALOR=? WHERE ID=?',
                (marca, modelo, quantidade, valor, id_produto))
    changed = cur.rowcount > 0
    cnn.commit()
    cnn.close()
    return changed

def excluir_produto(id_produto: int) -> bool:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('DELETE FROM PRODUTOS WHERE ID=?', (id_produto,))
    changed = cur.rowcount > 0
    cnn.commit()
    cnn.close()
    return changed

def listar_produtos() -> List[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT ID, MARCA, MODELO, QUANTIDADE, VALOR, VENDAS_FEITAS FROM PRODUTOS')
    rows = cur.fetchall()
    cnn.close()
    return rows

def buscar_produto(id_produto: int) -> Optional[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT ID, MARCA, MODELO, QUANTIDADE, VALOR, VENDAS_FEITAS FROM PRODUTOS WHERE ID=?', (id_produto,))
    row = cur.fetchone()
    cnn.close()
    return row

# -------------------------
# Clientes
# -------------------------
def adicionar_cliente(nome: str, email: str, telefone: str, estado: str, cidade: str) -> None:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('INSERT INTO CLIENTES (NOME, EMAIL, TELEFONE, ESTADO, CIDADE) VALUES (?, ?, ?, ?, ?)',
                (nome, email, telefone, estado, cidade))
    cnn.commit()
    cnn.close()

def listar_clientes() -> List[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT ID, NOME, EMAIL, TELEFONE, ESTADO, CIDADE FROM CLIENTES')
    rows = cur.fetchall()
    cnn.close()
    return rows

def buscar_cliente(id_cliente: int) -> Optional[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT ID, NOME, EMAIL, TELEFONE, ESTADO, CIDADE FROM CLIENTES WHERE ID=?', (id_cliente,))
    row = cur.fetchone()
    cnn.close()
    return row

# -------------------------
# Vendas (integração)
# -------------------------
def validar_venda(id_produto: int, quantidade_vendida: int) -> bool:
    produto = buscar_produto(id_produto)
    if not produto:
        return False
    estoque = produto[3]  # QUANTIDADE
    return estoque >= quantidade_vendida

def registrar_venda(id_produto: int, id_cliente: int, quantidade_vendida: int, vendedor: str) -> Tuple[bool, str]:
    # returns (ok, message)
    if not buscar_cliente(id_cliente):
        return False, "Cliente não encontrado."
    produto = buscar_produto(id_produto)
    if not produto:
        return False, "Produto não encontrado."
    estoque, valor_unitario, vendas_feitas = produto[3], produto[4], produto[5]
    if quantidade_vendida > estoque:
        return False, f"Estoque insuficiente. Disponível: {estoque}"

    novo_estoque = estoque - quantidade_vendida
    novas_vendas = vendas_feitas + quantidade_vendida
    valor_total = valor_unitario * quantidade_vendida

    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('UPDATE PRODUTOS SET QUANTIDADE=?, VENDAS_FEITAS=? WHERE ID=?',
                (novo_estoque, novas_vendas, id_produto))
    cur.execute('INSERT INTO VENDAS (ID_CLIENTE, VALOR, QUANTIDADE, VENDEDOR) VALUES (?, ?, ?, ?)',
                (id_cliente, valor_total, quantidade_vendida, vendedor))
    cnn.commit()
    cnn.close()
    return True, f"Venda registrada. Valor total: R${valor_total:.2f}"

def listar_vendas() -> List[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('''
        SELECT V.ID, V.ID_CLIENTE, C.NOME, V.VALOR, V.QUANTIDADE, V.VENDEDOR
        FROM VENDAS V
        LEFT JOIN CLIENTES C ON V.ID_CLIENTE = C.ID
        ORDER BY V.ID DESC
    ''')
    rows = cur.fetchall()
    cnn.close()
    return rows

# -------------------------
# Relatórios simples
# -------------------------
def total_vendas() -> float:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT SUM(VALOR) FROM VENDAS')
    total = cur.fetchone()[0] or 0.0
    cnn.close()
    return total

def produto_mais_vendido(limit: int = 3) -> List[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('SELECT MARCA, MODELO, VENDAS_FEITAS FROM PRODUTOS ORDER BY VENDAS_FEITAS DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    cnn.close()
    return rows

def clientes_frequentes(limit: int = 3) -> List[Tuple]:
    cnn = get_conn()
    cur = cnn.cursor()
    cur.execute('''
        SELECT C.NOME, COUNT(V.ID) AS compras
        FROM VENDAS V
        LEFT JOIN CLIENTES C ON V.ID_CLIENTE = C.ID
        GROUP BY C.NOME
        ORDER BY compras DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    cnn.close()
    return rows

# Note: no code that runs on import
