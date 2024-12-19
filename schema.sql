-- Création de la base de données
CREATE DATABASE IF NOT EXISTS factures_db;
USE factures_db;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des clients
CREATE TABLE IF NOT EXISTS clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    societe VARCHAR(100),
    email VARCHAR(100),
    telephone VARCHAR(20),
    adresse TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des catégories
CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Table des articles
CREATE TABLE IF NOT EXISTS articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    categorie_id INT,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categorie_id) REFERENCES categories(id)
);

-- Table des factures
CREATE TABLE IF NOT EXISTS factures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    numero VARCHAR(20) UNIQUE NOT NULL,
    client_id INT NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_echeance DATE,
    montant_total DECIMAL(10, 2) NOT NULL,
    devise VARCHAR(10) NOT NULL,
    statut ENUM('en_attente', 'payee', 'annulee') DEFAULT 'en_attente',
    notes TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Table des lignes de facture
CREATE TABLE IF NOT EXISTS lignes_facture (
    id INT PRIMARY KEY AUTO_INCREMENT,
    facture_id INT NOT NULL,
    article_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10, 2) NOT NULL,
    montant_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (facture_id) REFERENCES factures(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Table des paramètres
CREATE TABLE IF NOT EXISTS parametres (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cle VARCHAR(50) UNIQUE NOT NULL,
    valeur TEXT NOT NULL,
    description TEXT
);

-- Insertion des données de base pour les catégories
INSERT INTO categories (nom, description) VALUES
('Informatique', 'Matériel informatique et accessoires'),
('Téléphonie', 'Smartphones et accessoires'),
('Bureautique', 'Fournitures de bureau');

-- Insertion des paramètres par défaut
INSERT INTO parametres (cle, valeur, description) VALUES
('devise_defaut', 'FCFA', 'Devise par défaut'),
('theme', 'light', 'Thème de l''interface');
