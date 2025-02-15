import sqlite3

class FakeData:
    def __init__(self, db_path="dados_api.db"):
        self.db_path = db_path

    def conectar_banco(self):
        """Cria e retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)

    def limpar_dados_mockados(self):
        """Remove dados anteriores da tabela controle_downloads para evitar duplicação"""
        conn = self.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM controle_downloads")
        conn.commit()
        conn.close()
        print("🔹 Dados anteriores removidos.")

    def inserir_dados_mockados(self):
        """Insere dados de teste no banco de dados"""
        conn = self.conectar_banco()
        cursor = conn.cursor()

        # Inserir um único endpoint "viagens" com última data baixada em 12/02/2025
        cursor.execute("""
            INSERT INTO controle_downloads (endpoint, ultima_data)
            VALUES ('viagens', '2025-02-12')
        """)

        conn.commit()
        conn.close()
        print("🔹 Dados mockados inseridos com sucesso!")

# Executar para limpar e popular o banco de dados com dados de teste
if __name__ == "__main__":
    fake_data = FakeData()
    fake_data.limpar_dados_mockados()
    fake_data.inserir_dados_mockados()
