import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # À modifier selon votre configuration
            'database': 'factures_db'
        }

    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Erreur lors de la connexion à MySQL: {e}")
            return None

    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    connection.commit()
                    return cursor.lastrowid
                else:
                    return cursor.fetchall()
            except Error as e:
                print(f"Erreur lors de l'exécution de la requête: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return None
