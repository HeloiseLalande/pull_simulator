import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import json
import os
import subprocess
import sys

# Ajouter le répertoire parent (src) au sys.path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer la fonction simulate_pulls
from controller.simulate_pulls import load_gacha_config, simulate_pulls, format_results


class GachaSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Honkai Star Rail - Gacha Simulator")
        self.root.geometry("1000x800")
        
        # Configuration des styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Créer le notebook (conteneur d'onglets)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer les 3 onglets
        self.create_info_tab()
        self.create_simulator_tab()
        self.create_stats_tab()
    

    def create_info_tab(self):
        """Premier onglet : Informations et accès aux données"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Informations")
        
        # Titre
        title = ttk.Label(frame, text="Fonctionnement du Simulateur", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Texte d'explication
        info_text = """
            GUIDE D'UTILISATION

            1. PARAMÈTRES DE SIMULATION :

            • Fichier de configuration : Chemin vers le fichier JSON contenant les probabilités
            • Type de bannière : Choisir entre personnage limité ou arme
            • Nombre de pulls : Quantité de pulls à simuler
            • Consommer starlight : Automatiquement convertir les starlight en pulls bonus
            • Pity initial : Nombre de pulls déjà effectués (ex: 40/90)
            • Garantie 5* : Si le prochain 5* est garanti

            2. INTERPRÉTATION DES RÉSULTATS :

            Les résultats affichent :
            • Nombre de 5* obtenus (désiré vs non-désiré)
            • Nombre de 4* obtenus (personnages vs armes)
            • Nombre de 3* obtenus
            • Starlight restant
            • État de la garantie à la fin

            3.  CONSEILS :

            • Testez avec différents paramètres pour voir les statistiques
            • Activez "Consommer starlight" pour voir l'impact des bonus pulls
            • Les résultats sont aléatoires : relancez la simulation pour voir des variations

            4. FICHIER DE CONFIGURATION :

            Accédez au dossier DATA depuis l'onglet "Informations" pour modifier les probabilités
            et adapter le simulateur à votre jeu.

            Cliquez sur le bouton ci-dessous pour accéder aux fichiers de configuration :
        """
        
        text_widget = tk.Label(frame, text=info_text, justify=tk.LEFT, wraplength=800)
        text_widget.pack(pady=20)
        
        # Bouton pour accéder au dossier data
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        data_button = ttk.Button(
            button_frame,
            text="📁 Ouvrir le dossier DATA",
            command=self.open_data_folder
        )
        data_button.pack()
    
    def create_simulator_tab(self):
        """Deuxième onglet : Simulateur de pulls"""
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="Simulateur")
        
        # Partie gauche - Paramètres
        left_frame = ttk.LabelFrame(frame, text="Paramètres", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        # --- Sélection du fichier JSON ---
        ttk.Label(left_frame, text="Fichier de configuration :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        json_frame = ttk.Frame(left_frame)
        json_frame.pack(fill=tk.X, pady=5)
        
        self.json_path = tk.StringVar(value="data/honkai.json")
        ttk.Entry(json_frame, textvariable=self.json_path, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(json_frame, text="Parcourir", command=self.select_json_file).pack(side=tk.LEFT)
        
        # --- Type de bannière ---
        ttk.Label(left_frame, text="Type de bannière :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        self.banner_type = tk.StringVar(value="character")
        ttk.Radiobutton(left_frame, text="Personnage", variable=self.banner_type, value="character").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(left_frame, text="Arme", variable=self.banner_type, value="weapon").pack(anchor=tk.W, padx=20)
        
        # --- Nombre de pulls ---
        ttk.Label(left_frame, text="Nombre de pulls :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        self.num_pulls = tk.IntVar(value=90)
        ttk.Spinbox(left_frame, from_=1, to=1000, textvariable=self.num_pulls, width=10).pack(anchor=tk.W, padx=20, pady=5)
        
        # --- Utiliser starlight ---
        self.use_starlight = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            left_frame,
            text="Consommer les starlight pour bonus pulls",
            variable=self.use_starlight
        ).pack(anchor=tk.W, pady=(15, 5), padx=20)
        
        # --- Pity initial ---
        ttk.Label(left_frame, text="Pity 5* initial (0-90) :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        self.initial_pity = tk.IntVar(value=0)
        ttk.Spinbox(left_frame, from_=0, to=90, textvariable=self.initial_pity, width=10).pack(anchor=tk.W, padx=20, pady=5)
        
        # --- Garantie 5* ---
        self.five_star_guaranteed = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            left_frame,
            text="Garantie 5* active",
            variable=self.five_star_guaranteed
        ).pack(anchor=tk.W, pady=(15, 5), padx=20)
        
        # Bouton de lancement
        ttk.Button(
            left_frame,
            text="🎲 LANCER LA SIMULATION",
            command=self.run_simulation
        ).pack(fill=tk.X, pady=(20, 10), padx=5)
        
        # Partie droite - Résultats
        right_frame = ttk.LabelFrame(frame, text="Résultats", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.results_text = scrolledtext.ScrolledText(
            right_frame,
            width=60,
            height=30,
            font=("Courier", 9),
            bg="#f0f0f0"
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert(tk.END, "Les résultats apparaîtront ici...\n")
        self.results_text.config(state=tk.DISABLED)
    
    def create_stats_tab(self):
        """Troisième onglet : Probabilités"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Probabilités")
        
        # Titre
        title = ttk.Label(frame, text="Informations Supplémentaires", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Texte d'aide
        help_text = """
        """
        
        text_widget = tk.Label(frame, text=help_text, justify=tk.LEFT, wraplength=900)
        text_widget.pack(pady=20)
    
    def select_json_file(self):
        """Ouvrir un dialogue pour sélectionner le fichier JSON"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier de configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).parent.parent / "data")
        )
        if filename:
            self.json_path.set(filename)
    
    def open_data_folder(self):
        """Ouvrir le dossier data dans l'explorateur"""
        data_folder = Path(__file__).parent.parent.parent / "data"
        
        if not data_folder.exists():
            messagebox.showerror("Erreur", f"Le dossier {data_folder} n'existe pas")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(str(data_folder))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(data_folder)])
            else:
                subprocess.Popen(['xdg-open', str(data_folder)])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier : {e}")
    
    def run_simulation(self):
        """Lancer la simulation avec les paramètres sélectionnés"""
        try:
            # Obtenir le chemin du fichier JSON
            json_file = self.json_path.get()
            
            # Si c'est un chemin relatif, le rendre absolu par rapport au répertoire racine
            if not Path(json_file).is_absolute():
                json_file = str(Path(__file__).parent.parent / json_file)
            
            # Vérifier que le fichier existe
            if not Path(json_file).exists():
                messagebox.showerror("Erreur", f"Le fichier {json_file} n'existe pas")
                return
            
            # Charger la configuration
            config = load_gacha_config(json_file)
            
            # Récupérer les paramètres
            num_pulls = self.num_pulls.get()
            banner_type = self.banner_type.get()
            use_starlight = self.use_starlight.get()
            initial_pity = self.initial_pity.get()
            five_star_guaranteed = self.five_star_guaranteed.get()
            
            # Valider les paramètres
            if num_pulls < 1:
                messagebox.showerror("Erreur", "Le nombre de pulls doit être au moins 1")
                return
            
            if not (0 <= initial_pity <= 90):
                messagebox.showerror("Erreur", "Le pity initial doit être entre 0 et 90")
                return
            
            # Lancer la simulation
            results = simulate_pulls(
                num_pulls,
                config,
                banner_type=banner_type,
                use_starlight=use_starlight,
                initial_pity_five_star=initial_pity,
                five_star_guaranteed=five_star_guaranteed
            )
            
            # Formater et afficher les résultats
            results_str = format_results(results, num_pulls)
            
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results_str)
            self.results_text.config(state=tk.DISABLED)
            
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Le fichier JSON n'est pas valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")


def start_gui():
    root = tk.Tk()
    app = GachaSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    start_gui()