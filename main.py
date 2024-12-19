import tkinter as tk
from tkinter import ttk, messagebox
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import time
import sqlite3
from database.db_operations import DatabaseManager

class FactureApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.articles_panier = []
        self.total = 0
        
        # Initialisation de la base de données
        self.db = DatabaseManager()
        
        # Configuration de la fenêtre principale
        self.root.title("Générateur de Factures")
        
        # Variables pour les paramètres
        self.devise = tk.StringVar(value='€')
        self.theme = tk.StringVar(value='clair')
        
        # Charger les paramètres depuis la base de données
        devise_db = self.db.get_parametre('devise_default')
        if devise_db:
            self.devise.set(devise_db)
        
        theme_db = self.db.get_parametre('theme_default')
        if theme_db:
            self.theme.set(theme_db)
        
        # Charger le catalogue
        self.catalogue = self.charger_catalogue()
        
        # Création du menu hamburger
        self.create_hamburger_menu()
        
        # Création de l'interface principale avec trois colonnes
        self.create_main_layout()
        
    def create_hamburger_menu(self):
        # Menu hamburger
        menu_button = ttk.Button(self.root, text="☰", width=3)
        menu_button.place(x=5, y=5)
        
        # Création du menu popup
        self.popup_menu = tk.Menu(self.root, tearoff=0)
        
        # Options directes (sans sous-menus)
        self.popup_menu.add_command(label="Devise: Euro (€)", command=lambda: self.change_devise("€"))
        self.popup_menu.add_command(label="Devise: Dollar ($)", command=lambda: self.change_devise("$"))
        self.popup_menu.add_command(label="Devise: Livre (£)", command=lambda: self.change_devise("£"))
        self.popup_menu.add_command(label="Devise: Yen (¥)", command=lambda: self.change_devise("¥"))
        self.popup_menu.add_command(label="Devise: FCFA", command=lambda: self.change_devise("FCFA"))
        
        self.popup_menu.add_separator()
        
        self.popup_menu.add_command(label="Thème: Clair", command=lambda: self.change_theme("clair"))
        self.popup_menu.add_command(label="Thème: Sombre", command=lambda: self.change_theme("sombre"))
        self.popup_menu.add_command(label="Thème: Système", command=lambda: self.change_theme("système"))
        
        self.popup_menu.add_separator()
        
        self.popup_menu.add_command(label="Se déconnecter", command=self.deconnecter)
        
        # Lier le clic du bouton au menu
        menu_button.bind('<Button-1>', self.show_menu)
        
    def change_devise(self, nouvelle_devise):
        self.devise.set(nouvelle_devise)
        self.update_devise()
        
    def change_theme(self, nouveau_theme):
        self.theme.set(nouveau_theme)
        self.update_theme()
        
    def show_menu(self, event):
        # Afficher le menu sous le bouton
        self.popup_menu.post(event.widget.winfo_rootx(),
                           event.widget.winfo_rooty() + event.widget.winfo_height())
        
    def update_devise(self):
        # Mettre à jour tous les prix avec la nouvelle devise
        for item in self.panier_tree.get_children():
            values = self.panier_tree.item(item)['values']
            prix = values[1].rstrip('€$£¥FCFA')
            values = (values[0], f"{prix}{self.devise.get()}", values[2], f"{values[3].rstrip('€$£¥FCFA')}{self.devise.get()}")
            self.panier_tree.item(item, values=values)
            
    def update_theme(self):
        if self.theme.get() == "sombre":
            # Configuration du thème sombre
            self.root.configure(bg='#2b2b2b')
            style = ttk.Style()
            
            # Configuration générale
            style.configure(".", background='#2b2b2b', foreground='white')
            style.configure("TLabel", background='#2b2b2b', foreground='white')
            style.configure("TFrame", background='#2b2b2b')
            style.configure("TLabelframe", background='#2b2b2b', foreground='white')
            style.configure("TLabelframe.Label", background='#2b2b2b', foreground='white')
            style.configure("TButton", background='#3c3f41', foreground='white')
            style.configure("TEntry", fieldbackground='#3c3f41', foreground='white')
            style.configure("TSpinbox", fieldbackground='#3c3f41', foreground='white')
            style.configure("TCombobox", fieldbackground='#3c3f41', foreground='white')
            
            # Configuration améliorée pour le panier
            style.configure("Treeview", 
                background='#3c3f41',
                foreground='white',
                fieldbackground='#3c3f41',
                selectbackground='#0078d7',
                selectforeground='white'
            )
            style.configure("Treeview.Heading",
                background='#2b2b2b',
                foreground='white',
                relief='flat'
            )
            style.map("Treeview",
                background=[('selected', '#0078d7')],
                foreground=[('selected', 'white')]
            )
            style.map("Treeview.Heading",
                background=[('active', '#3c3f41')],
                foreground=[('active', 'white')]
            )
            
            if hasattr(self, 'panier_tree'):
                self.panier_tree.tag_configure('oddrow', background='#2d2d2d', foreground='white')
                self.panier_tree.tag_configure('evenrow', background='#3c3f41', foreground='white')
            
            # Configuration spéciale pour le bouton Générer facture
            style.configure("Generate.TButton",
                          background='#0078d7',
                          foreground='white',
                          font=('Helvetica', 10, 'bold'))
            
            if hasattr(self, 'total_label'):
                self.total_label.configure(foreground='white', background='#2b2b2b')
            
        elif self.theme.get() == "clair":
            # Réinitialisation au thème clair
            self.root.configure(bg='white')
            style = ttk.Style()
            style.configure(".", background='white', foreground='black')
            style.configure("TLabel", background='white', foreground='black')
            style.configure("TFrame", background='white')
            style.configure("TLabelframe", background='white', foreground='black')
            style.configure("TLabelframe.Label", background='white', foreground='black')
            style.configure("TButton", background='white', foreground='black')
            style.configure("Treeview", background='white', foreground='black', fieldbackground='white')
            style.configure("TEntry", fieldbackground='white', foreground='black')
            style.configure("TSpinbox", fieldbackground='white', foreground='black')
            style.configure("TCombobox", fieldbackground='white', foreground='black')
            
            # Configuration spécifique pour le panier
            style.configure("Treeview.Heading", background='white', foreground='black')
            style.map("Treeview",
                background=[('selected', '#0078d7')],
                foreground=[('selected', 'white')])
            
            # Configuration des listbox et autres widgets
            if hasattr(self, 'articles_list'):
                self.articles_list.configure(bg='white', fg='black', selectbackground='#0078d7', selectforeground='white')
            
            if hasattr(self, 'panier_tree'):
                self.panier_tree.configure(style="Treeview")
                self.panier_tree.tag_configure('oddrow', background='#f5f5f5')
                self.panier_tree.tag_configure('evenrow', background='white')
            
            # Configuration des boutons spécifiques
            style.configure("Add.TButton", background='white', foreground='black')
            
            # Réinitialisation du bouton Générer facture
            style.configure("Generate.TButton",
                          background='white',
                          foreground='black',
                          font=('Helvetica', 10, 'bold'))
            
            if hasattr(self, 'total_label'):
                self.total_label.configure(foreground='black', background='white')
            
    def show_hamburger_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        
        # Sous-menu Devise
        devise_menu = tk.Menu(menu, tearoff=0)
        for devise in ["€", "$", "£", "¥", "FCFA"]:
            devise_menu.add_command(label=f"Devise: {devise}", command=lambda d=devise: self.change_devise(d))
        menu.add_cascade(label="Devise", menu=devise_menu)
        
        # Sous-menu Thème
        theme_menu = tk.Menu(menu, tearoff=0)
        for theme in ["Clair", "Sombre", "Système"]:
            theme_menu.add_command(label=f"Thème: {theme}", command=lambda t=theme.lower(): self.change_theme(t))
        menu.add_cascade(label="Thème", menu=theme_menu)
        
        # Séparateur
        menu.add_separator()
        
        # Option Déconnexion
        menu.add_command(label="Se déconnecter", command=self.deconnecter)
        
        # Afficher le menu sous le bouton
        menu.post(event.widget.winfo_rootx(),
                 event.widget.winfo_rooty() + event.widget.winfo_height())
        
    def deconnecter(self):
        # Fermer la fenêtre actuelle
        self.root.destroy()
        # Vous pouvez ajouter ici le code pour revenir à l'écran de connexion
        messagebox.showinfo("Déconnexion", "Vous avez été déconnecté avec succès")
        
    def create_nav_menu(self):
        nav_frame = ttk.Frame(self.root, padding="10")
        nav_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Style pour les boutons de navigation
        style = ttk.Style()
        style.configure("Nav.TButton", padding=10, width=15)
        
        # Boutons de navigation horizontaux
        ttk.Button(nav_frame, text="Accueil", style="Nav.TButton", 
                  command=self.show_home).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="Articles", style="Nav.TButton",
                  command=self.show_articles).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="Factures", style="Nav.TButton",
                  command=self.show_invoices).pack(side="left", padx=2)

        # Bouton menu hamburger
        menu_btn = ttk.Button(nav_frame, text="☰", width=3)
        menu_btn.pack(side="left", padx=10)
        menu_btn.bind('<Button-1>', self.show_hamburger_menu)
        
        # Nom d'utilisateur à droite
        ttk.Label(nav_frame, text=self.username,
                 font=('Helvetica', 10)).pack(side="right", padx=10)

    def create_main_layout(self):
        # Configuration des colonnes principales
        self.root.grid_columnconfigure(1, weight=3)  # Articles (plus large)
        self.root.grid_columnconfigure(2, weight=2)  # Infos client
        
        # 1. Menu de navigation (colonne 0)
        self.create_nav_menu()
        
        # 2. Liste des articles (colonne 1)
        self.create_articles_section()
        
        # 3. Informations client et panier (colonne 2)
        self.create_client_section()
        
    def create_articles_section(self):
        # Frame principal pour les articles
        articles_frame = ttk.LabelFrame(self.root, text="Articles Disponibles", padding="10")
        articles_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Frame pour les paramètres en haut
        params_frame = ttk.LabelFrame(articles_frame, text="Paramètres", padding="5")
        params_frame.pack(fill="x", padx=5, pady=5)

        # Grille pour les paramètres
        params = [
            ("TVA (%)", "20"),
            ("Remise (%)", "0"),
            ("Mode de paiement", "Espèces"),
            ("Délai de paiement", "30 jours")
        ]

        for i, (label, default) in enumerate(params):
            ttk.Label(params_frame, text=label).grid(row=i//2, column=i%2*2, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(params_frame, width=15)
            entry.insert(0, default)
            entry.grid(row=i//2, column=i%2*2+1, padx=5, pady=2, sticky="w")
            setattr(self, f"{label.lower().replace(' ', '_')}_entry", entry)

        # Frame pour les filtres
        filter_frame = ttk.Frame(articles_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)

        # Liste déroulante pour les catégories
        ttk.Label(filter_frame, text="Filtrer par catégorie:").pack(side="left", padx=5)
        categories = list(set(article['categorie'] for article in self.catalogue['articles']))
        self.categorie_var = tk.StringVar()
        categorie_combo = ttk.Combobox(filter_frame, textvariable=self.categorie_var, values=['Tous'] + categories)
        categorie_combo.pack(side="left", padx=5)
        categorie_combo.set('Tous')
        categorie_combo.bind('<<ComboboxSelected>>', self.filter_articles)

        # Frame pour la liste des articles
        list_frame = ttk.Frame(articles_frame)
        list_frame.pack(fill="both", expand=True)

        # Création de la liste des articles avec Listbox
        self.articles_list = tk.Listbox(list_frame, selectmode="single", height=10)
        self.articles_list.pack(side="left", fill="both", expand=True)

        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.articles_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.articles_list.config(yscrollcommand=scrollbar.set)

        # Frame pour les détails de l'article
        self.details_frame = ttk.LabelFrame(articles_frame, text="Détails de l'article", padding="10")
        self.details_frame.pack(fill="x", padx=5, pady=5)

        # Labels pour les détails
        self.nom_label = ttk.Label(self.details_frame, text="")
        self.nom_label.pack(fill="x")
        self.prix_label = ttk.Label(self.details_frame, text="")
        self.prix_label.pack(fill="x")
        self.categorie_label = ttk.Label(self.details_frame, text="")
        self.categorie_label.pack(fill="x")
        self.description_label = ttk.Label(self.details_frame, text="", wraplength=300)
        self.description_label.pack(fill="x")

        # Frame pour quantité et bouton
        quantity_frame = ttk.Frame(self.details_frame)
        quantity_frame.pack(fill="x", pady=5)

        # Spinbox pour la quantité
        ttk.Label(quantity_frame, text="Quantité:").pack(side="left", padx=5)
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spinbox = ttk.Spinbox(
            quantity_frame,
            from_=1,
            to=100,
            width=5,
            textvariable=self.quantity_var
        )
        self.quantity_spinbox.pack(side="left", padx=5)

        # Bouton Ajouter
        self.add_button = ttk.Button(quantity_frame, text="Ajouter au panier", command=self.ajouter_au_panier)
        self.add_button.pack(side="left", padx=5)
        self.add_button.config(state="disabled")

        # Remplir la liste
        self.update_articles_list()

        # Binding pour la sélection
        self.articles_list.bind('<<ListboxSelect>>', self.on_select)
        
    def update_articles_list(self, filter_cat=None):
        self.articles_list.delete(0, tk.END)
        for article in self.catalogue['articles']:
            if filter_cat is None or filter_cat == 'Tous' or article['categorie'] == filter_cat:
                self.articles_list.insert(tk.END, article['nom'])
                
    def filter_articles(self, event=None):
        self.update_articles_list(self.categorie_var.get())
        
    def on_select(self, event=None):
        if not self.articles_list.curselection():
            return
        
        # Récupérer l'article sélectionné
        selected_name = self.articles_list.get(self.articles_list.curselection())
        selected_article = None
        for article in self.catalogue['articles']:
            if article['nom'] == selected_name:
                selected_article = article
                break
                
        if selected_article:
            # Mettre à jour les détails
            self.nom_label.config(text=f"Nom: {selected_article['nom']}")
            self.prix_label.config(text=f"Prix: {selected_article['prix']}€")
            self.categorie_label.config(text=f"Catégorie: {selected_article['categorie']}")
            self.description_label.config(text=f"Description: {selected_article.get('description', 'Pas de description')}")
            
            # Réinitialiser la quantité à 1
            self.quantity_var.set("1")
            
            # Activer le bouton et configurer la commande
            self.add_button.config(
                state="normal",
                command=lambda: self.ajouter_au_panier(selected_article)
            )
            
    def create_client_section(self):
        client_frame = ttk.LabelFrame(self.root, text="Informations Client", padding="10")
        client_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)
        
        # Champs pour les informations client
        fields = [
            ("Nom", "nom"),
            ("Adresse", "adresse"),
            ("Téléphone", "telephone"),
            ("Email", "email")
        ]
        
        for i, (label, attr) in enumerate(fields):
            ttk.Label(client_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = ttk.Entry(client_frame, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            setattr(self, f"{attr}_entry", entry)
        
        # Frame pour le panier
        panier_frame = ttk.LabelFrame(client_frame, text="Panier", padding="10")
        panier_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Création du tableau pour le panier
        columns = ('Article', 'Prix', 'Quantité', 'Total')
        self.panier_tree = ttk.Treeview(panier_frame, columns=columns, show='headings', height=10)
        
        # Configuration des colonnes
        for col in columns:
            self.panier_tree.heading(col, text=col)
            self.panier_tree.column(col, width=100)
        
        # Ajout d'une scrollbar
        scrollbar = ttk.Scrollbar(panier_frame, orient="vertical", command=self.panier_tree.yview)
        self.panier_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement des éléments
        self.panier_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Total et bouton générer facture
        total_frame = ttk.Frame(client_frame)
        total_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.total_label = ttk.Label(total_frame, text="Total: 0.00€", font=('Helvetica', 12, 'bold'))
        self.total_label.pack(side="left", padx=5)
        
        # Style spécial pour le bouton générer facture
        style = ttk.Style()
        style.configure("Generate.TButton", font=('Helvetica', 10, 'bold'))
        
        generer_btn = ttk.Button(total_frame, text="Générer une facture",
                               command=self.generer_facture, style="Generate.TButton")
        generer_btn.pack(side="right", padx=5)

    def ajouter_au_panier(self, article):
        try:
            quantite = int(self.quantity_var.get())
            if quantite <= 0:
                messagebox.showwarning("Erreur", "La quantité doit être supérieure à 0")
                return
            
            # Récupérer les informations de l'article
            prix = float(article['prix'])
            total_ligne = prix * quantite
            
            # Ajouter au panier (interface)
            values = (article['nom'], prix, quantite, total_ligne)
            self.panier_tree.insert('', 'end', values=values)
            
            # Mettre à jour le total
            self.total += total_ligne
            self.total_label.config(text=f"Total: {self.total:.2f}{self.devise.get()}")
            
        except ValueError:
            messagebox.showwarning("Erreur", "Veuillez entrer une quantité valide")
            
    def generer_facture(self):
        if not self.panier_tree.get_children():
            messagebox.showwarning("Panier vide", "Veuillez ajouter des articles au panier avant de générer une facture.")
            return
        
        # Récupérer les informations client
        client_info = {
            'nom': self.nom_entry.get(),
            'adresse': self.adresse_entry.get(),
            'telephone': self.telephone_entry.get(),
            'email': self.email_entry.get()
        }
        
        if not all(client_info.values()):
            messagebox.showwarning("Informations manquantes", 
                                 "Veuillez remplir toutes les informations client avant de générer une facture.")
            return
        
        try:
            # Sauvegarder le client dans la base de données
            client_id = self.db.ajouter_client(**client_info)
            
            # Préparer les articles pour la facture
            articles = []
            for item in self.panier_tree.get_children():
                values = self.panier_tree.item(item)['values']
                article_nom, prix, quantite, total = values
                
                # Créer ou récupérer l'article dans la base
                article = {
                    'nom': article_nom,
                    'description': '',
                    'prix_ht': float(prix),
                    'quantite': int(quantite)
                }
                article['id'] = self.db.ajouter_article(
                    article['nom'], 
                    article['description'], 
                    article['prix_ht']
                )
                articles.append(article)
            
            # Créer la facture dans la base de données
            facture_id = self.db.creer_facture(client_id, articles, self.devise.get())
            
            # Générer le PDF comme avant
            if not os.path.exists('factures'):
                os.makedirs('factures')
            
            filename = f'factures/facture_{facture_id}.pdf'
            self.generer_pdf_facture(filename, client_info, articles)
            
            # Ouvrir le PDF
            os.startfile(os.path.abspath(filename))
            
            # Vider le panier
            self.panier_tree.delete(*self.panier_tree.get_children())
            self.total = 0
            self.total_label.config(text=f"Total: 0.00{self.devise.get()}")
            
            messagebox.showinfo("Succès", "La facture a été générée avec succès !")
            
        except Exception as e:
            print(f"Erreur détaillée: {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la génération de la facture : {str(e)}")
            
    def charger_catalogue(self):
        try:
            with open('catalogue.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'articles': [
                    {
                        'nom': 'Ordinateur Portable HP',
                        'prix': 699.99,
                        'categorie': 'Informatique',
                        'description': 'Processeur Intel i5, 8GB RAM, 512GB SSD, Windows 10'
                    },
                    {
                        'nom': 'Smartphone Samsung Galaxy',
                        'prix': 499.99,
                        'categorie': 'Téléphonie',
                        'description': 'Écran 6.5", 128GB, Android 12, Double SIM'
                    },
                    {
                        'nom': 'Imprimante Canon',
                        'prix': 149.99,
                        'categorie': 'Informatique',
                        'description': 'Imprimante multifonction, WiFi, Recto-verso automatique'
                    },
                    {
                        'nom': 'Écran 27" Dell',
                        'prix': 249.99,
                        'categorie': 'Informatique',
                        'description': 'Résolution 2K, 144Hz, 1ms, FreeSync'
                    },
                    {
                        'nom': 'Clavier Mécanique',
                        'prix': 79.99,
                        'categorie': 'Accessoires',
                        'description': 'Switches Cherry MX Blue, RGB, AZERTY'
                    },
                    {
                        'nom': 'Souris Gaming',
                        'prix': 49.99,
                        'categorie': 'Accessoires',
                        'description': '16000 DPI, RGB, 8 boutons programmables'
                    },
                    {
                        'nom': 'Casque Bluetooth',
                        'prix': 89.99,
                        'categorie': 'Audio',
                        'description': 'Réduction de bruit active, 30h d\'autonomie'
                    },
                    {
                        'nom': 'Webcam HD',
                        'prix': 59.99,
                        'categorie': 'Accessoires',
                        'description': '1080p, Micro intégré, Auto-focus'
                    },
                    {
                        'nom': 'Disque Dur 1To',
                        'prix': 69.99,
                        'categorie': 'Stockage',
                        'description': 'USB 3.0, Compatible PC/Mac, Compact'
                    }
                ]
            }
            
    def generer_pdf_facture(self, filename, client_info, articles):
        # Créer le PDF
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        
        # Style pour le document
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(name='Right', alignment=2))
        styles.add(ParagraphStyle(name='Left', alignment=0))
        
        # En-tête
        elements.append(Paragraph("FACTURE", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Informations de la facture
        current_date = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(f"Facture N° : {filename.split('_')[-1].split('.')[0]}", styles['Normal']))
        elements.append(Paragraph(f"Date : {current_date}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Informations client
        elements.append(Paragraph("Informations Client:", styles['Heading2']))
        for key, value in client_info.items():
            elements.append(Paragraph(f"{key.capitalize()}: {value}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tableau des articles
        data = [['Article', 'Prix unitaire', 'Quantité', 'Total HT']]
        total_ht = 0
        
        # Récupérer les articles du panier
        for article in articles:
            # Convertir le prix en nombre
            try:
                total = article['prix_ht'] * article['quantite']
                data.append([article['nom'], f"{article['prix_ht']}", article['quantite'], f"{total:.2f}"])
                total_ht += total
            except ValueError as e:
                print(f"Erreur de conversion: {e}")
                total_ht += 0
        
        # Créer le tableau
        table = Table(data, colWidths=[200, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Calcul des totaux
        tva = total_ht * 0.20  # TVA à 20%
        total_ttc = total_ht + tva
        
        # Affichage des totaux
        elements.append(Paragraph(f"Total HT: {total_ht:.2f} {self.devise.get()}", styles['Right']))
        elements.append(Paragraph(f"TVA (20%): {tva:.2f} {self.devise.get()}", styles['Right']))
        elements.append(Paragraph(f"Total TTC: {total_ttc:.2f} {self.devise.get()}", styles['Right']))
        
        # Pied de page
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Merci de votre confiance !", styles['Center']))
        
        # Générer le PDF
        doc.build(elements)
        
    def show_home(self):
        # Nettoyer et recréer l'interface principale
        self.create_main_layout()
        
    def show_articles(self):
        # Afficher uniquement la section articles
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Recréer le menu de navigation
        self.create_nav_menu()
        
        # Créer un grand frame pour les articles
        articles_frame = ttk.LabelFrame(self.root, text="Articles Disponibles", padding="10")
        articles_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Frame pour les paramètres en haut
        params_frame = ttk.LabelFrame(articles_frame, text="Paramètres", padding="5")
        params_frame.pack(fill="x", padx=5, pady=5)

        # Grille pour les paramètres
        for i, param in enumerate([
            ("TVA (%)", "20"),
            ("Remise (%)", "0"),
            ("Mode de paiement", "Espèces"),
            ("Délai de paiement", "30 jours")
        ]):
            label, default = param
            ttk.Label(params_frame, text=label).grid(row=i//2, column=i%2*2, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(params_frame, width=15)
            entry.insert(0, default)
            entry.grid(row=i//2, column=i%2*2+1, padx=5, pady=2, sticky="w")
            setattr(self, f"{label.lower().replace(' ', '_')}_entry", entry)

        # Frame pour les filtres
        filter_frame = ttk.Frame(articles_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Liste déroulante pour les catégories
        ttk.Label(filter_frame, text="Filtrer par catégorie:").pack(side="left", padx=5)
        categories = list(set(article['categorie'] for article in self.charger_catalogue()['articles']))
        self.categorie_var = tk.StringVar()
        categorie_combo = ttk.Combobox(filter_frame, textvariable=self.categorie_var, values=['Tous'] + categories)
        categorie_combo.pack(side="left", padx=5)
        categorie_combo.set('Tous')
        categorie_combo.bind('<<ComboboxSelected>>', self.filter_articles)
        
        # Frame pour la liste des articles
        list_frame = ttk.Frame(articles_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Création de la liste des articles avec Listbox
        self.articles_list = tk.Listbox(list_frame, selectmode="single", height=10)
        self.articles_list.pack(side="left", fill="both", expand=True)
        
        # Frame pour les détails de l'article
        self.details_frame = ttk.LabelFrame(articles_frame, text="Détails de l'article", padding="10")
        self.details_frame.pack(fill="x", padx=5, pady=5)
        
        # Labels pour les détails
        self.nom_label = ttk.Label(self.details_frame, text="")
        self.nom_label.pack(fill="x")
        self.prix_label = ttk.Label(self.details_frame, text="")
        self.prix_label.pack(fill="x")
        self.categorie_label = ttk.Label(self.details_frame, text="")
        self.categorie_label.pack(fill="x")
        self.description_label = ttk.Label(self.details_frame, text="", wraplength=300)
        self.description_label.pack(fill="x")
        
        # Frame pour quantité et bouton
        quantity_frame = ttk.Frame(self.details_frame)
        quantity_frame.pack(fill="x", pady=5)
        
        # Spinbox pour la quantité
        ttk.Label(quantity_frame, text="Quantité:").pack(side="left", padx=5)
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spinbox = ttk.Spinbox(
            quantity_frame,
            from_=1,
            to=100,
            width=5,
            textvariable=self.quantity_var
        )
        self.quantity_spinbox.pack(side="left", padx=5)
        
        # Bouton Ajouter
        self.add_button = ttk.Button(quantity_frame, text="Ajouter au panier")
        self.add_button.pack(side="left", padx=5)
        self.add_button.config(state="disabled")
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.articles_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.articles_list.config(yscrollcommand=scrollbar.set)
        
        # Remplir la liste
        self.update_articles_list()
        
        # Binding pour la sélection
        self.articles_list.bind('<<ListboxSelect>>', self.on_select)
        
    def show_invoices(self):
        # Nettoyer l'interface
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Recréer le menu de navigation
        self.create_nav_menu()
        
        # Créer le frame principal pour les factures
        factures_frame = ttk.LabelFrame(self.root, text="Historique des Factures", padding="10")
        factures_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configuration des colonnes
        self.root.grid_columnconfigure(1, weight=1)
        
        # Création du tableau des factures
        columns = ('Date', 'Client', 'Total', 'Statut')
        tree = ttk.Treeview(factures_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Vérifier si le dossier factures existe
        if not os.path.exists('factures'):
            os.makedirs('factures')
        
        # Lister les factures existantes
        for file in os.listdir('factures'):
            if file.endswith('.pdf'):
                date = datetime.fromtimestamp(os.path.getctime(f'factures/{file}'))
                tree.insert('', 'end', values=(
                    date.strftime('%d/%m/%Y %H:%M'),
                    file.split('_')[0],
                    'N/A',
                    'Généré'
                ))
        
        # Ajout d'une scrollbar
        scrollbar = ttk.Scrollbar(factures_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement des éléments
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
class NumericKeypad(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Quantité")
        self.geometry("200x300")
        
        # Affichage
        self.display_var = tk.StringVar(value="0")
        display = ttk.Entry(self, textvariable=self.display_var, justify="right")
        display.pack(fill="x", padx=10, pady=10)
        
        # Boutons
        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            'C', '0', 'OK'
        ]
        
        button_frame = ttk.Frame(self)
        button_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        row = 0
        col = 0
        for button in buttons:
            cmd = lambda x=button: self.click(x)
            btn = ttk.Button(button_frame, text=button, command=cmd)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        # Configuration de la grille
        for i in range(4):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)
            
    def click(self, key):
        if key == 'C':
            self.display_var.set('0')
        elif key == 'OK':
            try:
                quantity = int(self.display_var.get())
                if quantity > 0:
                    self.callback(quantity)
                    self.destroy()
                else:
                    messagebox.showwarning("Attention", "La quantité doit être supérieure à 0")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer un nombre valide")
        else:
            current = self.display_var.get()
            if current == '0':
                self.display_var.set(key)
            else:
                self.display_var.set(current + key)

if __name__ == "__main__":
    root = tk.Tk()
    app = FactureApp(root, "justin")
    root.mainloop()
