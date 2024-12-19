# Générateur de Factures

Une application de bureau simple pour générer des factures automatiquement après l'achat d'articles.

## Fonctionnalités

- Interface graphique conviviale
- Ajout d'articles avec nom, prix et quantité
- Calcul automatique des totaux
- Génération de factures en PDF
- Sauvegarde des factures avec horodatage

## Installation

1. Assurez-vous d'avoir Python installé sur votre système
2. Installez les dépendances requises :
   ```
   pip install -r requirements.txt
   ```

## Utilisation

1. Lancez l'application :
   ```
   python main.py
   ```
2. Ajoutez des articles en remplissant les champs :
   - Nom de l'article
   - Prix unitaire
   - Quantité
3. Cliquez sur "Ajouter" pour chaque article
4. Une fois tous les articles ajoutés, cliquez sur "Générer la facture"
5. Les factures sont sauvegardées dans le dossier "factures" au format PDF

## Structure du projet

- `main.py` : Programme principal avec l'interface graphique
- `requirements.txt` : Liste des dépendances
- `factures/` : Dossier où sont sauvegardées les factures générées
# Goodfacture
