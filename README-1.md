# Base de données MySQL pour le Générateur de Factures

## Structure de la Base de Données

### Tables

#### 1. utilisateurs
- `id`: Identifiant unique (auto-incrémenté)
- `username`: Nom d'utilisateur (unique)
- `password`: Mot de passe (hashé)
- `email`: Email (unique)
- `date_creation`: Date de création du compte

#### 2. clients
- `id`: Identifiant unique (auto-incrémenté)
- `nom`: Nom du client
- `adresse`: Adresse du client
- `telephone`: Numéro de téléphone
- `email`: Email
- `date_creation`: Date d'ajout du client

#### 3. articles
- `id`: Identifiant unique (auto-incrémenté)
- `nom`: Nom de l'article
- `description`: Description de l'article
- `prix_ht`: Prix hors taxes
- `tva`: Taux de TVA (par défaut 20%)
- `stock`: Quantité en stock
- `date_creation`: Date d'ajout de l'article

#### 4. factures
- `id`: Identifiant unique (auto-incrémenté)
- `numero`: Numéro unique de facture
- `date_creation`: Date de création de la facture
- `client_id`: ID du client (clé étrangère)
- `total_ht`: Total hors taxes
- `tva`: Montant de la TVA
- `total_ttc`: Total TTC
- `devise`: Devise utilisée
- `statut`: État de la facture

#### 5. details_facture
- `id`: Identifiant unique (auto-incrémenté)
- `facture_id`: ID de la facture (clé étrangère)
- `article_id`: ID de l'article (clé étrangère)
- `quantite`: Quantité commandée
- `prix_unitaire`: Prix unitaire au moment de la commande
- `total_ligne`: Total de la ligne

#### 6. parametres
- `id`: Identifiant unique (auto-incrémenté)
- `nom`: Nom du paramètre
- `valeur`: Valeur du paramètre

## Relations

1. `factures.client_id` → `clients.id`
2. `details_facture.facture_id` → `factures.id`
3. `details_facture.article_id` → `articles.id`

## Installation

1. Installer MySQL sur votre système
2. Créer une base de données nommée `factures_db`
3. Exécuter le script `schema.sql`
4. Configurer les accès dans `db_config.py`

## Configuration

Dans `db_config.py`, modifier les paramètres de connexion :
```python
self.config = {
    'host': 'localhost',
    'user': 'votre_utilisateur',
    'password': 'votre_mot_de_passe',
    'database': 'factures_db'
}
```

## Utilisation

1. Initialiser la base de données :
```python
from database.init_db import init_database
init_database()
```

2. Créer un utilisateur :
```python
from database.init_db import create_user
create_user('username', 'password', 'email@example.com')
```

3. Utiliser les opérations de base de données :
```python
from database.db_operations import DatabaseManager
db = DatabaseManager()

# Ajouter un client
client_id = db.ajouter_client('Nom', 'Adresse', 'Téléphone', 'email')

# Ajouter un article
article_id = db.ajouter_article('Article', 'Description', 99.99)

# Créer une facture
articles = [{'id': article_id, 'prix_ht': 99.99, 'quantite': 1}]
facture_id = db.creer_facture(client_id, articles)
```

## Sécurité

- Les mots de passe sont stockés de manière sécurisée (hachés)
- Utilisation de requêtes préparées pour éviter les injections SQL
- Validation des données avant insertion
