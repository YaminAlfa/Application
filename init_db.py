import mysql.connector
from config import DB_CONFIG

def create_database():
    # Connexion sans sélectionner de base de données
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()

    # Créer la base de données si elle n'existe pas
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")

    # Créer la table enf
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enf(
        idenf bigint unsigned primary key auto_increment,
        nomenf varchar(20),
        prenomenf varchar(20),
        adressenf varchar(50),
        agenf int,
        fk_emp_enf_bigint unsigned
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()
