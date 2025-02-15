import sqlite3

class DatabaseManager:
    def __init__(self, db_name="dados_api.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabela para rastrear downloads
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS controle_downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL UNIQUE,
                ultima_data TEXT NOT NULL
            )
            """
        )
        
        # Tabela para rastrear processamento de arquivos
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS controle_processamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT NOT NULL UNIQUE,
                processado BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        
        self.conn.commit()
    
    def registrar_download(self, endpoint, ultima_data):
        self.cursor.execute(
            """
            INSERT INTO controle_downloads (endpoint, ultima_data)
            VALUES (?, ?)
            ON CONFLICT(endpoint) DO UPDATE SET ultima_data=excluded.ultima_data
            """,
            (endpoint, ultima_data)
        )
        self.conn.commit()
    
    def registrar_processamento(self, nome_arquivo):
        self.cursor.execute(
            """
            INSERT INTO controle_processamento (nome_arquivo, processado)
            VALUES (?, 1)
            ON CONFLICT(nome_arquivo) DO UPDATE SET processado=1
            """,
            (nome_arquivo,)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_tables()
    db.close()
