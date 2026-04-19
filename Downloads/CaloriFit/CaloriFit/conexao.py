import mysql.connector

def conectar():
    try:
        conexao = mysql.connector.connect(
            host="127.0.0.1",    # endereço do MySQL
            user="root",         # seu usuário
            password="123",  # coloque sua senha
            database="BD1",  # coloque o nome do seu banco
            port=3306
        )

        if conexao.is_connected():
            print("✅ Conexão com MySQL bem-sucedida!")
            return conexao
        else:
            print("❌ Falha ao conectar.")
            return None

    except Exception as erro:
        print("❌ Erro ao conectar:", erro)
        return None


# Teste rápido (opcional)
if __name__ == "__main__":
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        print("Banco atual:", cursor.fetchone())
        conn.close()

