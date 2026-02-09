import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import json
import os
import subprocess
import sys

# Ajouter le répertoire parent (src) au sys.path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Ajouter aussi le répertoire view pour les imports des tabs
sys.path.insert(0, str(Path(__file__).parent))

# Importer les fonctions du controller
from controller.simulate_pulls import load_gacha_config, simulate_pulls, format_results

# Importer les onglets
from tabs.info_tab import create_info_tab
from tabs.simulator_tab import create_simulator_tab
from tabs.stats_tab import create_stats_tab


class GachaSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Honkai Star Rail - Gacha Simulator")
        self.root.geometry("1000x800")
        
        # Configuration des styles
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Créer le notebook (conteneur d'onglets)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer les 3 onglets via les modules séparés
        create_info_tab(self, self.notebook)
        create_simulator_tab(self, self.notebook)
        create_stats_tab(self, self.notebook)
    
    def select_json_file(self):
        """Ouvrir un dialogue pour sélectionner le fichier JSON"""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier de configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).parent.parent.parent / "data")
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
                json_file = str(Path(__file__).parent.parent.parent / json_file)
            
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
if __name__ == "__main__":
    start_gui()