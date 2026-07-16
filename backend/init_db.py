# backend/init_db.py
import sqlite3

def criar_banco():
    conn = sqlite3.connect("loja.db")
    cursor = conn.cursor()

    # 1. Criar tabela de Categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    );
    """)

    # 2. Criar tabela de Produtos (Relacional)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        estoque INTEGER NOT NULL,
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );
    """)

    # 3. Inserir dados fictícios para teste se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM categorias;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO categorias (nome) VALUES ('Eletrônicos');")
        cursor.execute("INSERT INTO categorias (nome) VALUES ('Vestuário');")
        
        cursor.execute("INSERT INTO produtos (nome, preco, estoque, categoria_id) VALUES ('Smartphone X', 1999.90, 15, 1);")
        cursor.execute("INSERT INTO produtos (nome, preco, estoque, categoria_id) VALUES ('Fone de Ouvido Bluetooth', 299.00, 40, 1);")
        cursor.execute("INSERT INTO produtos (nome, preco, estoque, categoria_id) VALUES ('Camiseta Algodão', 79.90, 100, 2);")

    conn.commit()
    conn.close()
    print("Banco de dados 'loja.db' inicializado com sucesso!")

if __name__ == "__main__":
    criar_banco()