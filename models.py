from db_config import DatabaseConfig

class User:
    def __init__(self):
        self.db = DatabaseConfig()

    def create(self, username, password, email=None):
        query = """INSERT INTO users (username, password, email)
                  VALUES (%s, %s, %s)"""
        return self.db.execute_query(query, (username, password, email))

    def get_by_username(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        result = self.db.execute_query(query, (username,))
        return result[0] if result else None

class Article:
    def __init__(self):
        self.db = DatabaseConfig()

    def create(self, nom, prix, categorie_id, description=None, stock=0):
        query = """INSERT INTO articles (nom, prix, categorie_id, description, stock)
                  VALUES (%s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (nom, prix, categorie_id, description, stock))

    def get_all(self):
        query = """SELECT a.*, c.nom as categorie_nom
                  FROM articles a
                  LEFT JOIN categories c ON a.categorie_id = c.id"""
        return self.db.execute_query(query)

    def get_by_id(self, article_id):
        query = """SELECT a.*, c.nom as categorie_nom
                  FROM articles a
                  LEFT JOIN categories c ON a.categorie_id = c.id
                  WHERE a.id = %s"""
        result = self.db.execute_query(query, (article_id,))
        return result[0] if result else None

class Client:
    def __init__(self):
        self.db = DatabaseConfig()

    def create(self, nom, prenom, societe=None, email=None, telephone=None, adresse=None):
        query = """INSERT INTO clients (nom, prenom, societe, email, telephone, adresse)
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (nom, prenom, societe, email, telephone, adresse))

    def get_by_id(self, client_id):
        query = "SELECT * FROM clients WHERE id = %s"
        result = self.db.execute_query(query, (client_id,))
        return result[0] if result else None

class Facture:
    def __init__(self):
        self.db = DatabaseConfig()

    def create(self, numero, client_id, montant_total, devise, date_echeance=None, notes=None):
        query = """INSERT INTO factures (numero, client_id, montant_total, devise, date_echeance, notes)
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (numero, client_id, montant_total, devise, date_echeance, notes))

    def add_ligne(self, facture_id, article_id, quantite, prix_unitaire):
        montant_total = quantite * prix_unitaire
        query = """INSERT INTO lignes_facture (facture_id, article_id, quantite, prix_unitaire, montant_total)
                  VALUES (%s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (facture_id, article_id, quantite, prix_unitaire, montant_total))

    def get_by_id(self, facture_id):
        query = """SELECT f.*, c.nom, c.prenom, c.societe
                  FROM factures f
                  JOIN clients c ON f.client_id = c.id
                  WHERE f.id = %s"""
        result = self.db.execute_query(query, (facture_id,))
        return result[0] if result else None

    def get_lignes(self, facture_id):
        query = """SELECT lf.*, a.nom as article_nom
                  FROM lignes_facture lf
                  JOIN articles a ON lf.article_id = a.id
                  WHERE lf.facture_id = %s"""
        return self.db.execute_query(query, (facture_id,))

class Parametre:
    def __init__(self):
        self.db = DatabaseConfig()

    def get_value(self, cle):
        query = "SELECT valeur FROM parametres WHERE cle = %s"
        result = self.db.execute_query(query, (cle,))
        return result[0]['valeur'] if result else None

    def set_value(self, cle, valeur):
        query = """INSERT INTO parametres (cle, valeur)
                  VALUES (%s, %s)
                  ON DUPLICATE KEY UPDATE valeur = %s"""
        return self.db.execute_query(query, (cle, valeur, valeur))
