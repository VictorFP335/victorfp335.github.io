import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="SUA_SENHA",
        database="calorifit"
    )

    if conn.is_connected():
        print("Conectado com sucesso!")
    else:
        print("Não conectou!")
except mysql.connector.Error as e:
    print("Erro:", e)
