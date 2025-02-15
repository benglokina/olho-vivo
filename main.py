import sqlite3
from datetime import datetime, timedelta
from viagens import ViagensDownloader

class GerenciadorDeDownloads:
    def __init__(self, db_path="dados.db", api_key_path="gov_fed.api_key"):
        self.db_path = db_path
        self.chave_api = self.ler_chave_api(api_key_path)
        self.data_inicio = datetime.strptime("2025-01-01", "%Y-%m-%d")  # Data fixa de início
        self.viagens_downloader = ViagensDownloader(self.chave_api)

    def ler_chave_api(self, api_key_path):
        """Lê a chave da API do arquivo especificado"""
        try:
            with open(api_key_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print("Erro: Arquivo de chave API não encontrado!")
            return None

    def conectar_banco(self):
        """Cria e retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)

    def obter_endpoints_pendentes(self):
        """Consulta quais endpoints precisam ser chamados e executa as chamadas"""
        conn = self.conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT endpoint, ultima_data_baixada 
            FROM metadados
        """)
        
        metadados = cursor.fetchall()
        conn.close()

        # Calcular a data limite (ontem)
        data_limite = datetime.today() - timedelta(days=1)
        data_limite_str = data_limite.strftime("%Y-%m-%d")

        print("\n📌 Iniciando chamadas para os endpoints pendentes:")
        for endpoint, ultima_data_baixada in metadados:
            chamadas = []  # Lista para armazenar as chamadas pendentes

            # Se nunca foi baixado, começa de 01/01/2025
            if ultima_data_baixada is None:
                chamadas.append("2025-01-01")
            else:
                # Determina a data inicial a partir da última baixada +1 dia
                data_inicio = datetime.strptime(ultima_data_baixada, "%Y-%m-%d") + timedelta(days=1)

                # Se já está atualizado até ontem, não há nada a fazer
                if data_inicio > data_limite:
                    continue

                # Gerar chamadas para cada dia pendente até ontem
                while data_inicio <= data_limite:
                    chamadas.append(data_inicio.strftime("%Y-%m-%d"))
                    data_inicio += timedelta(days=1)

            # Executar chamadas para cada dia pendente
            for data in chamadas:
                print(f"🔹 Chamando {endpoint} | Data: {data}")
                if endpoint == "viagens":
                    pagina = 1
                    while True:
                        resultado = self.viagens_downloader.consultar_viagens(data, pagina)
                        if not resultado:
                            break  # Para se não houver mais páginas
                        pagina += 1

# Executar o gerenciador de downloads
if __name__ == "__main__":
    gerenciador = GerenciadorDeDownloads()
    gerenciador.obter_endpoints_pendentes()
