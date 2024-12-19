import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='database/factures.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    # Opérations sur les clients
    def ajouter_client(self, nom, adresse, telephone, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO clients (nom, adresse, telephone, email)
            VALUES (?, ?, ?, ?)
            ''', (nom, adresse, telephone, email))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_client(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    # Opérations sur les articles
    def ajouter_article(self, nom, description, prix_ht, tva=20.0, stock=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO articles (nom, description, prix_ht, tva, stock)
            VALUES (?, ?, ?, ?, ?)
            ''', (nom, description, prix_ht, tva, stock))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_article(self, article_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def update_stock(self, article_id, quantite):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE articles 
            SET stock = stock + ? 
            WHERE id = ?
            ''', (quantite, article_id))
            conn.commit()
        finally:
            conn.close()
    
    # Opérations sur les factures
    def creer_facture(self, client_id, articles, devise='€'):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Calcul des totaux
            total_ht = sum(art['prix_ht'] * art['quantite'] for art in articles)
            tva = total_ht * 0.20  # TVA à 20%
            total_ttc = total_ht + tva
            
            # Création du numéro de facture (YYYYMMDD-XXXX)
            numero = datetime.now().strftime('%Y%m%d-') + str(int(datetime.now().timestamp()))[-4:]
            
            # Insertion de la facture
            cursor.execute('''
            INSERT INTO factures (numero, client_id, total_ht, tva, total_ttc, devise)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (numero, client_id, total_ht, tva, total_ttc, devise))
            
            facture_id = cursor.lastrowid
            
            # Insertion des détails de la facture
            for article in articles:
                cursor.execute('''
                INSERT INTO details_facture 
                (facture_id, article_id, quantite, prix_unitaire, total_ligne)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    facture_id,
                    article['id'],
                    article['quantite'],
                    article['prix_ht'],
                    article['prix_ht'] * article['quantite']
                ))
                
                # Mise à jour du stock
                self.update_stock(article['id'], -article['quantite'])
            
            conn.commit()
            return facture_id
        finally:
            conn.close()
    
    def get_facture(self, facture_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Récupération des informations de la facture
            cursor.execute('''
            SELECT f.*, c.nom, c.adresse, c.telephone, c.email
            FROM factures f
            JOIN clients c ON f.client_id = c.id
            WHERE f.id = ?
            ''', (facture_id,))
            facture = cursor.fetchone()
            
            if not facture:
                return None
            
            # Récupération des détails de la facture
            cursor.execute('''
            SELECT df.*, a.nom, a.description
            FROM details_facture df
            JOIN articles a ON df.article_id = a.id
            WHERE df.facture_id = ?
            ''', (facture_id,))
            details = cursor.fetchall()
            
            return {'facture': facture, 'details': details}
        finally:
            conn.close()
    
    # Opérations sur les paramètres
    def get_parametre(self, nom):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT valeur FROM parametres WHERE nom = ?', (nom,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def set_parametre(self, nom, valeur):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO parametres (nom, valeur)
            VALUES (?, ?)
            ''', (nom, valeur))
            conn.commit()
        finally:
            conn.close()
