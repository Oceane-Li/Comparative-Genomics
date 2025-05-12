# PROJET PYTHON AVANCE - MU4BM748 : COMPARAISON DE PAIRES DE GENOMES BACTERIENS PAR DOTPLOT


# Etudiant : Océane Li (n_etudiant : 28602519)


import tkinter as tk
from tkinter import filedialog
from tkinter import Menu
from tkinter import ttk
import tkinter.messagebox as messagebox
import psycopg2 as pg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import time
import gzip
import os
import copy
import sys


# Autocomplete Combobox class
class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
        # Cette méthode définit la liste des options pour l'autocomplétion.
        """
        Input:
        - completion_list : la liste des chaînes de caractères à partir desquelles l'autocomplétion sera effectuée.
        """

        # La liste est triée de manière insensible à la casse
        self._completion_list = sorted(completion_list, key=str.lower)

        # Initialisation des variables de contrôle
        self._hits = []  # list : résultats d'autocomplétion
        self._hit_index = 0  # index de l'élément actuellement sélectionné
        self.position = 0  # position du curseur dans le texte du combobox

        # à chaque fois qu'une touche est relâchée dans le combobox, handle_keyrelease est appelée pour gérer l'autocomplétion
        self.bind("<KeyRelease>", self.handle_keyrelease)
        self["values"] = self._completion_list

    def autocomplete(self, delta=0):
        # Autocomplétion en fonction du texte saisi dans le comboboc.
        """
        Input:
        - delta : int indiquant la direction de l'autocomplétion (vers le haut ou le bas).
        - si delta != 0 : la partie du texte après la position actuelle du curseur est supprimée (garantit que l'autocomplétion n'écrase pas le texte déjà saisi).
        - si delta = 0 : aucun ajustement supplémentaire n'est nécessaire.
        """

        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())

        _hits = []  # Stocke les correspondances trouvées
        # On vérifie si l'élément commence par le texte actuellement saisi dans le combobox
        for item in self._completion_list:
            if item.lower().startswith(self.get().lower()):
                _hits.append(item)

        # Mise à jour des correspondances
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        # Si des correspondances sont disponibles dans _hits
        if _hits:
            self._hit_index = (self._hit_index + delta) % len(_hits)
            self.delete(0, tk.END)
            self.insert(0, _hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        # Gestion des évènements de relâchement de touches.

        # L'utilisateur a supprimé du texte
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        # Déplacement du curseur vers la gauche
        elif event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.position = self.index(tk.END)
        # Déplacement du curseur vers la droite
        elif event.keysym == "Right":
            self.position = self.index(tk.END)
        # Déplacement vers le haut ou le bas pour sélectionner dans la liste d'autocomplétion
        elif event.keysym == "Down":
            self.autocomplete(1)
        elif event.keysym == "Up":
            self.autocomplete(-1)
        elif len(event.keysym) == 1:
            self.autocomplete()


class OrganismComparisonApp:

    # Initialisation de l'interface graphique
    def __init__(self, root):

        # Fenêtre principale
        self.root = root
        self.root.title("Comparaison de paires de génomes bactériens par dotplot")
        self.root.geometry("1550x800")  # Taille de la fenêtre

        # Création de la barre de menu
        menubar = Menu(self.root)

        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Enregistrer", command=self.save_dotplot)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.confirm_quit)
        menubar.add_cascade(label="Menu", menu=file_menu)

        # Configuration de la barre de menu
        self.root.config(menu=menubar)

        # Couleur de fond de la fenetre principale
        self.root.configure(bg="light blue")

        # Frames
        # frame1 : éléments de contrôle (labels, listes, boutons)
        self.frame1 = tk.Frame(self.root, bg="light blue")
        self.frame1.pack(side="left")  # Panneau de commande à gauche
        # frame2 : affichage du dotplot à droite de frame1
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(side="right")  # Canevas du dotplot

        # Labels (étiquettes) : sélectionner les organismes pour faire la comparaison
        label1 = tk.Label(
            self.frame1,
            text="Sélectionner un 1er organisme :",
            font=("Arial", 16, "bold"),
            bg="light blue",
            fg="black",
        )
        label1.grid(row=0, column=0, sticky="ns", columnspan=3, pady=(1, 10))
        label2 = tk.Label(
            self.frame1,
            text="Sélectionner un 2nd organisme :",
            font=("Arial", 16, "bold"),
            bg="light blue",
            fg="black",
        )
        label2.grid(row=2, column=0, sticky="ns", columnspan=3, pady=(20, 10))

        # Comboboxes d'autocomplétion
        self.org1_combobox = AutocompleteCombobox(
            self.frame1, width=50, font=("Arial", 16)
        )
        self.org1_combobox.grid(
            row=1, column=0, sticky="ns", columnspan=3, pady=(10, 5)
        )
        self.org2_combobox = AutocompleteCombobox(
            self.frame1, width=50, font=("Arial", 16)
        )
        self.org2_combobox.grid(row=3, column=0, sticky="ns", columnspan=3)

        # Load organism names and links
        self.load_organism_data()

        # Bouton BLASTP
        self.blastp_button = tk.Button(
            self.frame1,
            text="Lancer BLASTP",
            command=self.launch_blastp,
            font=("Arial", 16, "bold"),
        )
        self.blastp_button.grid(row=4, column=0, columnspan=3, pady=(20, 10))
        # Case à cocher : "Filtrer le dotplot" (BLASTP)
        self.filter_var = tk.BooleanVar()
        self.filter_checkbox = tk.Checkbutton(
            self.frame1,
            text="Filtrer le dotplot    ",
            font=("Arial", 12, "bold"),
            bg="light blue",
            fg="black",
            variable=self.filter_var,
            command=self.update_filter_status,
        )
        self.filter_checkbox.grid(
            row=4, column=2, sticky="e", columnspan=1, pady=(20, 10)
        )

        # Bouton CDSearch
        self.cdsearch_button = tk.Button(
            self.frame1,
            text="Lancer CD Search",
            command=self.launch_cdsearch,
            font=("Arial", 16, "bold"),
        )  # Texte en gras
        self.cdsearch_button.grid(row=5, column=0, columnspan=3, pady=(10, 20))
        # Case à cocher : "Filtrer le dotplot" (CDSearch)
        self.filter_var2 = tk.BooleanVar()
        self.filter_checkbox2 = tk.Checkbutton(
            self.frame1,
            text="Filtrer le dotplot    ",
            font=("Arial", 12, "bold"),
            bg="light blue",
            fg="black",
            variable=self.filter_var2,
            command=self.update_filter_status2,
        )
        self.filter_checkbox2.grid(
            row=5, column=2, sticky="e", columnspan=1, pady=(10, 20)
        )

        # Espace entre les boutons
        self.frame1.rowconfigure(6, minsize=20)

        # Label et Entry pour la valeur de e-value (blastp)
        tk.Label(
            self.frame1,
            text="E-Value (BLASTP):",
            font=("Arial", 15, "bold"),
            bg="light blue",
            fg="black",
        ).grid(row=7, column=0, sticky="w")
        # Case d'entrée pour la e-value de BLASTP
        self.evalue_entry = tk.Entry(self.frame1, width=15, font=("Arial", 15))
        self.evalue_entry.grid(row=7, column=1)
        # Valeur par défaut de la e-value (blastp)
        self.evalue_entry.insert(tk.END, "1e-6")

        # Espace entre les e-value
        self.frame1.rowconfigure(8, minsize=20)

        # Label et Entry pour la valeur de e-value (CDSearch)
        tk.Label(
            self.frame1,
            text="E-Value (CD Search):",
            font=("Arial", 15, "bold"),
            bg="light blue",
            fg="black",
        ).grid(row=9, column=0, sticky="w", pady=(1, 30))
        # Case d'entrée pour la e-value de CDSearch
        self.evalue_entry_cdsearch = tk.Entry(self.frame1, width=15, font=("Arial", 15))
        self.evalue_entry_cdsearch.grid(row=9, column=1, pady=(1, 30))
        # Valeur par défaut de la e-value de CDSearch
        self.evalue_entry_cdsearch.insert(tk.END, "1e-4")

        # Espacement
        self.frame1.rowconfigure(10, minsize=20)

        # Canevas du dotplot
        self.fig, self.ax = plt.subplots(figsize=(20, 20))  # Carré
        self.ax.invert_yaxis()
        self.canvas = FigureCanvasTkAgg(
            self.fig, master=self.frame2
        )  # Frame 2 pour le dotplot
        self.canvas.get_tk_widget().pack(
            side="right"
        )  # Affichage du dotplot à droite de frame 1

        # Gestionnaire d'événements pour le clic de souris
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Initialiser le dotplot dans le Canvas
        self.dotplot = None

        # Charger les données initiales dans les Comboboxes
        self.update_org1_combobox()
        self.update_org2_combobox()

        # Variables pour stocker les limites des axes avant zoom
        self.prev_xlim = None
        self.prev_ylim = None

        # Bouton pour zoomer sur le dotplot
        self.zoom_button = tk.Button(
            self.frame1, text="Zoomer", command=self.zoom_dotplot, font=("Arial", 14)
        )
        self.zoom_button.grid(row=11, padx=2, pady=5, sticky="we")

        # Bouton pour dézoomer sur le dotplot
        self.dezoom_button = tk.Button(
            self.frame1,
            text="Dézoomer",
            command=self.dezoom_dotplot,
            font=("Arial", 14),
        )
        self.dezoom_button.grid(row=11, column=1, padx=2, pady=5, sticky="we")

        # Bouton pour revenir au dotplot initial
        self.dezoom_complet_button = tk.Button(
            self.frame1,
            text="Dézoome total",
            command=self.dezoom_complet,
            font=("Arial", 14),
        )
        self.dezoom_complet_button.grid(row=11, column=2, padx=2, pady=5, sticky="we")

        # Bouton pour enregistrer le dotplot
        self.save_button = tk.Button(
            self.frame1,
            text="Enregistrer Dotplot",
            command=self.save_dotplot,
            font=("Arial", 15, "bold"),
        )
        self.save_button.grid(
            row=12, column=0, columnspan=3, padx=2, pady=10, sticky="we"
        )

        # Quitter l'interface
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_quit)
        quit_button = tk.Button(
            self.frame1,
            text="Quitter",
            command=self.confirm_quit,
            font=("Arial", 15, "bold"),
        )
        quit_button.grid(row=13, column=0, columnspan=3, padx=2, pady=5, sticky="we")

    # Clic de la souris souris sur le dotplot
    def on_click(self, event):
        if event.inaxes is not None:  # si le clic a été effectué dans le dotplot
            # Capture les coordonnées du clic
            x, y = event.xdata, event.ydata
            print(f"Coordonnées du clic de souris : x = {x}, y = {y}")
            # (x, y) serviront de point de départ pour le zoom
            self.zoom_start = (x, y)

    # Fonction pour zoomer sur le dotplot
    def zoom_dotplot(self):
        # On vérifie si les coordonnées de départ du zoom on été enregistrées
        if hasattr(self, "zoom_start"):
            x, y = self.zoom_start
            zoom_factor = 2  # Facteur de zoom

            # Limites actuelles des axes
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()

            # Calcul des nouvelles limites des axes
            new_xlim = (x - (x - x_min) / zoom_factor, x + (x_max - x) / zoom_factor)
            new_ylim = (y - (y - y_min) / zoom_factor, y + (y_max - y) / zoom_factor)

            # Mise à jour des limites des axes + redessin du dotplot
            self.prev_xlim = (x_min, x_max)
            self.prev_ylim = (y_min, y_max)
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.canvas.draw()

    # Fonction pour dézoomer le dotplot
    def dezoom_dotplot(self):
        # Rétablit les limites des axes pour dézoomer
        if self.prev_xlim is not None and self.prev_ylim is not None:
            self.ax.set_xlim(self.prev_xlim)
            self.ax.set_ylim(self.prev_ylim)
            self.canvas.draw()

    # Fonction pour revenir aux échelles initiales du dotplot
    def dezoom_complet(self):
        # Réinitialiser les limites des axes
        self.ax.autoscale()
        self.canvas.draw()

    # Fonction pour enregistrer le dotplot
    def save_dotplot(self):
        # Ouvrir une boîte de dialogue pour choisir le répertoire et le format d'enregistrement
        file_path = filedialog.asksaveasfile(
            filetypes=[
                ("PDF files", "*.pdf"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
            ]
        )
        if file_path:
            # On récupère le nom du fichier choisi
            file_name = file_path.name
            # On sauvegarde le dotplot dans le format choisi en utilisant le nom de fichier
            self.fig.savefig(file_name)

    # Fonction pour quitter l'application
    def quit_application(self):
        root.destroy()  # Ferme l'interface
        sys.exit()  # Arrête le programme Python

    # Boite de confirmation pour quitter
    def confirm_quit(self):
        # Affiche une boîte de dialogue de confirmation
        response = messagebox.askyesno(
            "Confirmation", "Voulez-vous vraiment quitter l'application ?"
        )
        if response:
            self.quit_application()  # Ferme l'interface si l'utilisateur clique sur "Oui"

    # Chargement des données des organismes (fichier.csv)
    def load_organism_data(self):
        print("Loading organism data...")

        # Read organism names and links from CSV file, skipping the first row
        df = pd.read_csv("prokaryotes_complete-genomes.csv", header=None, skiprows=1)
        organism_data = df[
            [0, 14, 5]
        ].values.tolist()  # Organism name, Protome link, Reference name

        organism_names = [data[0] for data in organism_data]

        # Remplir les comboboxes avec les noms des organismes
        self.org1_combobox.insert(0, organism_names[0])
        self.org2_combobox.insert(0, organism_names[1])

        # Extraire les FTP links des protéomes
        self.ftp_links = [data[1] for data in organism_data]
        self.organism_data = organism_data

        return [self.org1_combobox.get(), self.org2_combobox.get()]

    # Mise à jour de la liste de l'organisme 1 dans la Combobox
    def update_org1_combobox(self):
        self.org1_combobox.set_completion_list([org[0] for org in self.organism_data])

    # Mise à jour de la liste de l'organisme 2 dans la Combobox
    def update_org2_combobox(self):
        self.org2_combobox.set_completion_list([org[0] for org in self.organism_data])

    # Mise à jour du statut de filtrage (BLASTP)
    def update_filter_status(self):
        self.filter_etat = self.filter_var.get()  # Récupérer l'état de la case à cocher

    # Mise à jour du statut de filtrage (CDSearch)
    def update_filter_status2(self):
        self.filter_etat2 = (
            self.filter_var2.get()
        )  # Récupérer l'état de la case à cocher

    # Fonction pour récupérer le nom du fichier.faa (GCA)
    def get_protome_filename(self, proteome_link):
        # Remplacer "ftp" par "https" dans le lien du protéome
        ncbi_link = proteome_link.replace("ftp://", "https://")

        # Extraire le nom du fichier .faa
        slash_index = ncbi_link.rfind("/")
        filename = ncbi_link[slash_index + 1 :]
        faa_filename = filename + "_translated_cds.faa"
        print("GET PROTOME FILENAME :", faa_filename)

        return faa_filename, ncbi_link

    # Télécharger les protéomes depuis NCBI
    def download_protome(self, proteome_link):
        # Remplacer "ftp" par "https" dans le lien du protéome
        ncbi_link = proteome_link.replace("ftp://", "https://")
        slash = ncbi_link[:]
        last_slash_index = slash.rfind("/")
        filename_parts = slash[last_slash_index + 1 :]

        # Extraire le nom du fichier .faa.gz
        faa_gz_filename = filename_parts + "_translated_cds.faa.gz"

        # Construire le lien complet du fichier .faa.gz
        proteome_url = ncbi_link + "/" + faa_gz_filename

        # Déterminer le chemin complet de destination dans le dossier FASTAFILE
        fastafile_path = os.path.join("FASTAFILE", faa_gz_filename)

        # Télécharger le fichier .faa.gz
        os.system(f"wget -P FASTAFILE {proteome_url}")

        # Décompresser le fichier .faa.gz
        os.system(f"gunzip {fastafile_path}")

        return ncbi_link

    # Extraire les noms des gènes à partir d'un fichier FASTA
    def read_fasta(self, fasta_file):
        gene_names = []
        with open(os.path.join("FASTAFILE", fasta_file), "r") as file:
            for line in file:
                if line.startswith(">"):
                    gene_names.append(line[1:].split()[0])
        return gene_names

    # Dotplot (BLASTP)
    def create_dotplot(self, blastp_file, protome1_faa, protome2_faa):
        # Lire les noms de gènes à partir des fichiers faa
        org1_genes = self.read_fasta(protome1_faa)
        org2_genes = self.read_fasta(protome2_faa)

        # Initialiser la matrice dotplot à 0
        dotplot_matrix = np.zeros((len(org1_genes), len(org2_genes)))
        print(f"Taille protéome 1 : {len(org1_genes)}")
        print(f"Taille protéome 2 : {len(org2_genes)}")
        print()

        # Lire la valeur de la e-value depuis l'Entry
        e_value = float(self.evalue_entry.get())

        # Parcourir le fichier blastp et mettre à 1 les coordonnées correspondantes dans la matrice dotplot
        with open(os.path.join("BLASTPFILE", blastp_file), "r") as file:
            for line in file:
                fields = line.split("\t")
                gene1, gene2, evalue = fields[0], fields[1], float(fields[-2])
                if evalue < e_value:
                    index1 = org1_genes.index(gene1)
                    index2 = org2_genes.index(gene2)
                    dotplot_matrix[index1, index2] = 1

        # Filtrer la matrice pour éliminer les points dispersés
        if self.filter_var.get():
            new_dotplot = self.filter_dotplot(dotplot_matrix)
        else:
            new_dotplot = dotplot_matrix  # Utiliser la matrice originale si la case de filtre n'est pas cochée

        # Afficher le dotplot
        dot = np.where(new_dotplot == 1)
        self.ax.clear()
        self.ax.scatter(dot[0], dot[1], s=1, cmap="Blues")
        self.ax.grid(True)
        self.ax.set_xlabel(f"{self.org1_combobox.get()}")
        self.ax.set_ylabel(f"{self.org2_combobox.get()}")
        self.ax.set_title("Dotplot BLASTP")
        self.canvas.draw()

    # Filtrer le dotplot (BLASTP)
    def filter_dotplot(self, dotplot_matrix):
        # Initialiser la matrice filtrée
        filtered_dotmat = np.zeros_like(dotplot_matrix)

        # Parcourir la matrice brute avec une mini matrice de taille 3*3 pour filtrer les points en diagonale
        for i in range(1, dotplot_matrix.shape[0] - 1):
            for j in range(1, dotplot_matrix.shape[1] - 1):
                # Vérifier si les 3 points en diagonale (quel que soit le sens) sont présents
                if (
                    dotplot_matrix[i - 1, j - 1]
                    == dotplot_matrix[i, j]
                    == dotplot_matrix[i + 1, j + 1]
                    == 1
                ):
                    # Conserver les 3 points en diagonale dans la matrice filtrée
                    filtered_dotmat[i - 1, j - 1] = 1
                    filtered_dotmat[i, j] = 1
                    filtered_dotmat[i + 1, j + 1] = 1
                if (
                    dotplot_matrix[i - 1, j + 1]
                    == dotplot_matrix[i, j]
                    == dotplot_matrix[i + 1, j - 1]
                    == 1
                ):
                    # Conserver les 3 points sur l'anti-diagonale dans la matrice filtrée
                    filtered_dotmat[i - 1, j + 1] = 1
                    filtered_dotmat[i, j] = 1
                    filtered_dotmat[i + 1, j - 1] = 1

        return filtered_dotmat

    # Abreviation des noms d'espèces
    def abrev_name(self, org):
        first = org[:5].replace(" ", "_")  # on remplace les espaces par des underscores
        last = org[-5:].replace(" ", "_")
        name = first + last
        return name

    # Lancer le BLASTP
    def launch_blastp(self):

        # Noms des 2 organismes sélectionnés par l'utilisateur
        org1 = self.org1_combobox.get()
        org2 = self.org2_combobox.get()

        # Abréviation des noms des 2 organismes
        name1 = self.abrev_name(org1)
        name2 = self.abrev_name(org2)

        # FTP links
        protome1_link = self.ftp_links[
            [data[0] for data in self.organism_data].index(org1)
        ]
        protome2_link = self.ftp_links[
            [data[0] for data in self.organism_data].index(org2)
        ]
        # Noms des fichiers.faa (GCA)
        protome1_filename, _ = self.get_protome_filename(protome1_link)
        protome2_filename, _ = self.get_protome_filename(protome2_link)

        FASTAFILE = "FASTAFILE"
        BLASTPFILE = "BLASTPFILE"

        # On vérifie si le fichier blastp existe déjà dans la Database pour ces 2 organismes
        blastp_filename = f"blastp_{name1}_{name2}.out"
        conn, cur = self.connect_database()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM blastp WHERE nom_fichier = %s)",
            (blastp_filename,),
        )
        blastp_exists = cur.fetchone()[0]
        cur.close()

        if blastp_exists:
            print(f"Le fichier {blastp_filename} existe déjà dans BLASTPFILE.\n")
            # Si le fichier existe dans la base de données, on va le chercher dans le dossier BLASTPFILE
            blastp_path = os.path.join(BLASTPFILE, blastp_filename)
        else:
            # On vérifie si les fichiers .faa existe déjà dans la database, sinon les télécharger (ncbi)
            conn, cur = self.connect_database()
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM fasta WHERE nom_fichier = %s)",
                (protome1_filename,),
            )
            existing_data1 = cur.fetchone()[0]
            cur.close()
            if not existing_data1:
                self.download_protome(protome1_link)
                protome1_filename, _ = self.get_protome_filename(protome1_link)
                print(f"Téléchargement du fichier fasta {protome1_filename} réussi.\n")
                fasta_path1 = os.path.join(FASTAFILE, protome1_filename)
            else:
                # Si le fichier .faa existe dans la base de données, on va le chercher dans le dossier FASTAFILE
                fasta_path1 = os.path.join(FASTAFILE, protome1_filename)
                if not os.path.exists(fasta_path1):
                    print(
                        f"Le fichier {protome1_filename} n'existe pas dans le dossier FASTAFILE.\n"
                    )
                else:
                    print(
                        f"Le fichier {protome1_filename} a été trouvé dans le dossier FASTAFILE.\n"
                    )

            # La même procédure pour le 2nd organisme sélectionné
            conn, cur = self.connect_database()
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM fasta WHERE nom_fichier = %s)",
                (protome2_filename,),
            )
            existing_data2 = cur.fetchone()[0]
            cur.close()
            if not existing_data2:
                self.download_protome(protome2_link)
                protome2_filename, _ = self.get_protome_filename(protome2_link)
                print(f"Téléchargement du fichier fasta {protome2_filename} réussi.\n")
                fasta_path2 = os.path.join(FASTAFILE, protome2_filename)
            else:
                fasta_path2 = os.path.join(FASTAFILE, protome2_filename)
                if not os.path.exists(fasta_path2):
                    print(
                        f"Le fichier {protome2_filename} n'existe pas dans le dossier FASTAFILE.\n"
                    )
                else:
                    print(
                        f"Le fichier {protome2_filename} a été trouvé dans le dossier FASTAFILE.\n"
                    )

            # Lancer le BLASTP entre les 2 organismes dans obiwan
            print(f"Début du blastp entre {org1} et {org2}...")
            os.system(
                f"blastp -query {fasta_path1} -subject {fasta_path2} -out BLASTPFILE/blastp_{name1}_{name2}.out -outfmt 6"
            )
            print()
            print("Fin du BLASTP.\n")

        # On crée le dotplot à partir du fichier de sortie du blastp
        self.create_dotplot(blastp_filename, protome1_filename, protome2_filename)

        # On complète notre database avec les nouveaux fichiers formés
        self.complete_fasta_table(FASTAFILE)
        self.complete_blastp_table(blastp_filename, BLASTPFILE)

        return blastp_filename

    # Chargement des données du fichier blastp.out
    def load_blastp_data(self):
        blastp_data = []  # Liste de tuples
        blastp_filename = self.launch_blastp()
        with open(os.path.join("BLASTPFILE", blastp_filename), "r") as file:
            for line in file:
                fields = line.split("\t")
                gene1, gene2, _ = fields[0], fields[1], float(fields[-2])
                blastp_data.append((gene1, gene2))
        return blastp_data

    # Dotplot (CDSEARCH)
    def plot_cdsearch(
        self, gene_couples, protome1_faa, protome2_faa, functional_similarity
    ):

        # Lire les noms de gènes à partir des fichiers faa
        org1_genes = self.read_fasta(protome1_faa)
        org2_genes = self.read_fasta(protome2_faa)

        # Initialiser la matrice dotplot à 0
        cdd_matrix = np.zeros((len(org1_genes), len(org2_genes)))

        # Parcourir la liste des couples de gènes qui ont des CDD < e-value définie par l'utilisateur
        for gene1, gene2 in gene_couples:
            index1 = org1_genes.index(gene1)
            index2 = org2_genes.index(gene2)

            # On détermine la couleur des points en fonction de la similarité fonctionnelle
            similarity = functional_similarity[(gene1, gene2)]
            if similarity > 0.9:
                cdd_matrix[index1, index2] = 1
            elif similarity > 0.5:
                cdd_matrix[index1, index2] = 2
            else:
                cdd_matrix[index1, index2] = 3

        # Filtrer la matrice pour éliminer les points dispersés
        if self.filter_var2.get():
            new_cdd = self.filter_cdsearch(cdd_matrix)
        else:
            new_cdd = cdd_matrix  # Utiliser la matrice originale si la case de filtre n'est pas cochée

        # Afficher le dotplot
        dot1 = np.where(new_cdd == 1)
        dot2 = np.where(new_cdd == 2)
        dot3 = np.where(new_cdd == 3)
        self.ax.clear()
        self.ax.scatter(dot1[0], dot1[1], s=1, color="red")
        self.ax.scatter(dot2[0], dot2[1], s=1, color="green")
        self.ax.scatter(dot3[0], dot3[1], s=1, color="blue")
        self.ax.grid(True)
        self.ax.set_xlabel(f"{self.org1_combobox.get()}")
        self.ax.set_ylabel(f"{self.org2_combobox.get()}")
        self.ax.set_title("CD Search")

        # Légendes
        legend_elements = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="red",
                markersize=10,
                label=">80%",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="green",
                markersize=10,
                label=">50%",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="blue",
                markersize=10,
                label="<50%",
            ),
        ]
        self.ax.legend(
            handles=legend_elements,
            loc="upper right",
            bbox_to_anchor=(1.0, 1.0),
            ncol=1,
            title="Similarité fonctionnelle",
        )

        self.canvas.draw()

    # Filtrer le dotplot (CDSEARCH)
    def filter_cdsearch(self, dotplot_matrix):
        # Initialiser la matrice filtrée
        filtered_dotmat = np.zeros_like(dotplot_matrix)

        # Parcourir la matrice brute avec une mini matrice de taille 3*3 pour filtrer les points en diagonale
        for i in range(1, dotplot_matrix.shape[0] - 1):
            for j in range(1, dotplot_matrix.shape[1] - 1):
                # Vérifier si les 3 points en diagonale (quel que soit le sens) sont présents
                if (
                    dotplot_matrix[i - 1, j - 1] != 0
                    and dotplot_matrix[i, j] != 0
                    and dotplot_matrix[i + 1, j + 1] != 0
                ):
                    # Conserver les 3 points en diagonale dans la matrice filtrée
                    filtered_dotmat[i - 1, j - 1] = dotplot_matrix[i - 1, j - 1]
                    filtered_dotmat[i, j] = dotplot_matrix[i, j]
                    filtered_dotmat[i + 1, j + 1] = dotplot_matrix[i + 1, j + 1]
                if (
                    dotplot_matrix[i - 1, j + 1] != 0
                    and dotplot_matrix[i, j] != 0
                    and dotplot_matrix[i + 1, j - 1] != 0
                ):
                    # Conserver les 3 points sur l'anti-diagonale dans la matrice filtrée
                    filtered_dotmat[i - 1, j + 1] = dotplot_matrix[i - 1, j + 1]
                    filtered_dotmat[i, j] = dotplot_matrix[i, j]
                    filtered_dotmat[i + 1, j - 1] = dotplot_matrix[i + 1, j - 1]

        return filtered_dotmat

    # Lancer le CDSEARCH
    def launch_cdsearch(self):

        # Noms des 2 organismes sélectionnés par l'utilisateur
        org1 = self.org1_combobox.get()
        org2 = self.org2_combobox.get()

        # Abréviation des noms des 2 organismes
        name1 = self.abrev_name(org1)
        name2 = self.abrev_name(org2)

        # Path
        FASTAFILE = "FASTAFILE"
        CDSFILE = "CDSFILE"

        # Noms des fichiers.faa (GCA)
        protome1_filename, _ = self.get_protome_filename(
            self.ftp_links[[data[0] for data in self.organism_data].index(org1)]
        )
        protome2_filename, _ = self.get_protome_filename(
            self.ftp_links[[data[0] for data in self.organism_data].index(org2)]
        )
        # Path vers les fichiers.faa
        fasta_path1 = os.path.join(FASTAFILE, protome1_filename)
        fasta_path2 = os.path.join(FASTAFILE, protome2_filename)

        # On vérifie si le fichier CDsearch existe déjà dans la database, sinon le lancer
        cds1_filename = f"CDS_{name1}.out"
        conn, cur = self.connect_database()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM cdsearch WHERE nom_fichier = %s)",
            (cds1_filename,),
        )
        cds1_exists = cur.fetchone()[0]
        cur.close()

        if cds1_exists:
            print(f"Le fichier {cds1_filename} existe déjà dans CDSFILE.\n")
            cds_path1 = os.path.join(CDSFILE, cds1_filename)
        else:  # Lancer CD Search (prot1)
            print(f"Début du CD Search pour {org1}...\n")
            os.system(
                f"rpsblast+ -db /usr/share/cdd/Cdd_NCBI -query {fasta_path1} -out CDSFILE/CDS_{name1}.out -outfmt 6"
            )
            print()
            print(f"Fin du CD Search pour {org1}.\n")
            # Compléter la table cdsearch
            self.complete_cdsearch_table(cds1_filename, CDSFILE)

        # La même procédure pour le 2nd organisme sélectionné
        cds2_filename = f"CDS_{name2}.out"
        conn, cur = self.connect_database()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM cdsearch WHERE nom_fichier = %s)",
            (cds2_filename,),
        )
        cds2_exists = cur.fetchone()[0]
        cur.close()

        if cds2_exists:
            print(f"Le fichier {cds2_filename} existe déjà dans CDSFILE.\n")
            cds_path2 = os.path.join(CDSFILE, cds2_filename)
        else:  # Lancer CD Search (prot2)
            print(f"Début du CD Search pour {org2}...\n")
            os.system(
                f"rpsblast+ -db /usr/share/cdd/Cdd_NCBI -query {fasta_path2} -out CDSFILE/CDS_{name2}.out -outfmt 6"
            )
            print()
            print(f"Fin du CD Search pour {org2}.\n")
            # Compléter la table cdsearch
            self.complete_cdsearch_table(cds2_filename, CDSFILE)

        # Lire la valeur de la e-value depuis l'Entry
        e_value_cd = float(self.evalue_entry_cdsearch.get())

        # On stocke les CDD du protéome 1 et du protéome 2 avec une e-value inférieure au seuil
        cdd_prot1 = {}
        cdd_prot2 = {}

        # On analyse le fichier de sortie CD Search pour le protéome 1
        with open(os.path.join(CDSFILE, f"CDS_{name1}.out"), "r") as file:
            for line in file:
                fields = line.split("\t")
                gene, CDD, evalue = fields[0], fields[1], float(fields[-2])

                # Si le CDD a une e-value inférieure au seuil pour le protéome 1, on le stocke
                if evalue < e_value_cd:
                    if gene not in cdd_prot1:
                        cdd_prot1[gene] = [CDD]
                    else:
                        cdd_prot1[gene].append(CDD)

        # On analyse le fichier de sortie CD Search pour le protéome 2
        with open(os.path.join(CDSFILE, f"CDS_{name2}.out"), "r") as file:
            for line in file:
                fields = line.split("\t")
                gene, CDD, evalue = fields[0], fields[1], float(fields[-2])

                # Si le CDD a une e-value inférieure au seuil pour le protéome 2, on le stocke
                if evalue < e_value_cd:
                    if gene not in cdd_prot2:
                        cdd_prot2[gene] = [CDD]
                    else:
                        cdd_prot2[gene].append(CDD)

        # Charger les données depuis le fichier blastp
        blastp_data = self.load_blastp_data()

        # On filtre les couples de gènes qui ont des CDD en commun
        gene_couples = []
        for gene1, gene2 in blastp_data:
            if gene1 in cdd_prot1 and gene2 in cdd_prot2:
                gene_couples.append((gene1, gene2))

        # Calcul de la similarité fonctionnelle pour chaque couple de gènes
        functional_similarity = {}
        for gene1, gene2 in gene_couples:
            # Nombre de CDD en commun entre les 2 gènes
            common_cdd = len(set(cdd_prot1[gene1]) & set(cdd_prot2[gene2]))

            # Nombre total de CDD dans les 2 gènes sans redondance
            total_cdd = len(set(cdd_prot1[gene1] + cdd_prot2[gene2]))

            # Calcul du pourcentage de similarité fonctionnelle
            similarity = common_cdd / total_cdd if total_cdd else 0.0
            functional_similarity[(gene1, gene2)] = similarity
        print("Calcul du pourcentage de similarité fonctionnelle terminé.\n")

        # Affichage du dotplot
        self.plot_cdsearch(
            gene_couples, protome1_filename, protome2_filename, functional_similarity
        )
        print("Dotplot CDSearch end.\n")

    # # Connexion à la base de données Projet748
    def connect_database(self):
        conn = pg.connect("dbname=Projet748")
        cur = conn.cursor()
        return conn, cur

    # Fermeture de la connexion à la base de données
    def close_connection(self, conn, cur):
        cur.close()
        conn.close()

    # Table fasta
    def complete_fasta_table(self, path):
        # Connection à la base de données
        conn, cur = self.connect_database()

        # Obtention des valeurs à insérer dans la table fasta pour le 1er organisme
        nom_organisme1 = self.org1_combobox.get()
        prot_link1 = self.ftp_links[
            [data[0] for data in self.organism_data].index(nom_organisme1)
        ]
        nom_fichier1, ftplink1 = self.get_protome_filename(prot_link1)
        abreviation1 = self.abrev_name(nom_organisme1)

        # Vérifier si les données existent déjà dans la table fasta pour org1
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM fasta WHERE nom_fichier = %s)",
            (nom_fichier1,),
        )
        existing_data1 = cur.fetchone()[0]  # Récupérer le résultat de la requête

        # Si les données n'existent pas déjà pour org1, les ajouter à la table fasta
        if not existing_data1:
            # Insertion des valeurs dans la table fasta pour org1
            sql_insert1 = """
            INSERT INTO fasta(nom_fichier, nom_organisme, abreviation, ftplink, repertoire)
            VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(
                sql_insert1,
                (nom_fichier1, nom_organisme1, abreviation1, ftplink1, path),
            )
            print("Données pour org1 insérées dans la table fasta avec succès.\n")
        else:
            print("Les données pour org1 existent déjà dans la table fasta.\n")

        # Obtention des valeurs à insérer dans la table fasta pour le 2nd organisme
        nom_organisme2 = self.org2_combobox.get()
        prot_link2 = self.ftp_links[
            [data[0] for data in self.organism_data].index(nom_organisme2)
        ]
        nom_fichier2, ftplink2 = self.get_protome_filename(prot_link2)
        abreviation2 = self.abrev_name(nom_organisme2)

        # Vérifier si les données existent déjà dans la table fasta pour org2
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM fasta WHERE nom_fichier = %s)",
            (nom_fichier2,),
        )
        existing_data2 = cur.fetchone()[0]  # Récupérer le résultat de la requête

        # Si les données n'existent pas déjà pour org2, les ajouter à la table fasta
        if not existing_data2:
            # Insertion des valeurs dans la table fasta pour org2
            sql_insert2 = """
            INSERT INTO fasta(nom_fichier, nom_organisme, abreviation, ftplink, repertoire)
            VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(
                sql_insert2,
                (nom_fichier2, nom_organisme2, abreviation2, ftplink2, path),
            )
            print("Données pour org2 insérées dans la table fasta avec succès.\n")
        else:
            print("Les données pour org2 existent déjà dans la table fasta.\n")

        # On valide les modifications dans la database
        conn.commit()

        # Fermeture de la connexion à la database
        self.close_connection(conn, cur)

    # Table blastp
    def complete_blastp_table(self, blastp_filename, path):
        # Connection à la base de données
        conn, cur = self.connect_database()

        # Obtention des valeurs à insérer dans la table blastp
        nom_fichier = blastp_filename

        # Vérifier si les données existent déjà dans la table blastp
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM blastp WHERE nom_fichier = %s)",
            (nom_fichier,),
        )
        existing_data = cur.fetchone()[0]

        # Si les données n'existent pas déjà, les ajouter à la table blastp
        if not existing_data:
            # Insertion des valeurs dans la table blastp
            sql_insert = """
            INSERT INTO blastp(nom_fichier, repertoire)
            VALUES (%s, %s);
            """
            cur.execute(sql_insert, (nom_fichier, path))
            print("Données insérées dans la table blastp avec succès.\n")
        else:
            print("Les données existent déjà dans la table blastp.\n")

        # On valide les modifications dans la base de données
        conn.commit()

        # Fermeture de la connexion à la base de données
        self.close_connection(conn, cur)

    # Table cdsearch
    def complete_cdsearch_table(self, cdsearch_filename, path):
        conn, cur = self.connect_database()

        # Vérifier si le fichier existe déjà dans la table cdsearch
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM cdsearch WHERE nom_fichier = %s)",
            (cdsearch_filename,),
        )
        cdsearch_exists = cur.fetchone()[0]

        if not cdsearch_exists:
            # Insérer les valeurs dans la table cdsearch
            sql_insert = """
            INSERT INTO cdsearch(nom_fichier, repertoire)
            VALUES (%s, %s)
            """
            cur.execute(sql_insert, (cdsearch_filename, path))
            print(
                f"Données pour {cdsearch_filename} insérées dans la table cdsearch avec succès.\n"
            )
        else:
            print(
                f"Les données pour {cdsearch_filename} existent déjà dans la table cdsearch.\n"
            )

        # Valider les modifications dans la base de données
        conn.commit()

        # Fermer la connexion à la base de données
        self.close_connection(conn, cur)


if __name__ == "__main__":
    root = tk.Tk()
    app = OrganismComparisonApp(root)
    root.mainloop()


# QUE DOIT ON FAIRE AVEC LE FICHIER CD SEARCH ?
# Si les couples de gènes du fichier blastp ont au moins un CDD en commun avec une e-value < seuil, on plot le point.
# 2 CHOIX :
# - Hyp 1 : si un couple de gène n'est pas présent dans le fichier blastp, alors il y a peu de chance qu'il ont un CDD en commun (seuil de e-value = 10 dans blastp)
#           Plus la e-value est élevé, plus les gènes sont différents/éloignés, donc cette hypothèse peut être valable.
#           PB : on néglige la convergence des fonctions de 2 gènes non homologues.
# - Hyp 2 : on crée un fichier où on va faire les couples nous-mêmes (all genes prot1 * all genes prot2)
#           PB : prend bcp de temps et bcp de mémoire
#           Avantage : on prend toutes les possibilités en considération.
# ATTENTION : l'hyp2 ne donne pas forcément de meilleurs résultats
