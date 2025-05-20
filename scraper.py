import time
from datetime import datetime
from selenium.webdriver.common.by import By
from log import logger

class Scraper:
    def check_global_update(self):
        """Verifica se há atualização global no site"""
        try:
            # Acessa a página inicial
            self.driver.get(self.base_url)
            time.sleep(2)  # Aguarda carregamento
            
            # Obtém a data da última atualização do elemento last_update
            last_update_element = self.driver.find_element(By.ID, "last_update")
            last_update_str = last_update_element.text
            
            # Converte a string da data para datetime
            last_update = datetime.strptime(last_update_str, "%a %b %d %H:%M:%S UTC %Y")
            
            # Verifica se já temos essa atualização no banco
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT last_update FROM cursos 
                        ORDER BY last_update DESC 
                        LIMIT 1
                    """)
                    result = cur.fetchone()
                    
                    if result and result[0] >= last_update:
                        logger.info(f"Banco de dados já está atualizado. Última atualização: {result[0]}")
                        return False
                    
                    logger.info(f"Nova atualização disponível: {last_update}")
                    return True
                    
        except Exception as e:
            logger.error(f"Erro ao verificar atualização global: {str(e)}")
            return True  # Em caso de erro, assume que precisa atualizar 