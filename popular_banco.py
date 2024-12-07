import sqlite3

# Reabrindo a conexão com o banco de dados
conn = sqlite3.connect('instance/pedidos.db')
cursor = conn.cursor()

# Inserindo alguns pedidos na tabela
pedidos = [
    (3, 666, 'preparando'),
    (2, 22, 'preparando'),
    (1, 11, 'preparando')
]

# Inserindo os dados na tabela
cursor.executemany('''
INSERT INTO pedidos (opcao, codigo, status) 
VALUES (?, ?, ?)
''', pedidos)

# Comitando as mudanças e fechando a conexão
conn.commit()
conn.close()