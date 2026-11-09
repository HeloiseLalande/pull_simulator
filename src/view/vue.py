import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import json
import os
import subprocess
import sys
import threading
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
            results_str = format_results(results, num_pulls, config['title'])
            
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results_str)
            self.results_text.config(state=tk.DISABLED)
            
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Le fichier JSON n'est pas valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
    
    def run_statistics(self):
        """Lancer 1000 simulations pour générer des statistiques"""
        try:
            # Obtenir le chemin du fichier JSON
            json_file = self.stats_json_path.get()
            
            # Si c'est un chemin relatif, le rendre absolu
            if not Path(json_file).is_absolute():
                json_file = str(Path(__file__).parent.parent.parent / json_file)
            
            # Vérifier que le fichier existe
            if not Path(json_file).exists():
                messagebox.showerror("Erreur", f"Le fichier {json_file} n'existe pas")
                return
            
            # Charger la configuration
            config = load_gacha_config(json_file)
            
            # Récupérer les paramètres
            num_pulls = self.stats_num_pulls.get()
            banner_type = self.stats_banner_type.get()
            use_starlight = self.stats_use_starlight.get()
            initial_pity = self.stats_initial_pity.get()
            five_star_guaranteed = self.stats_five_star_guaranteed.get()
            
            # Valider les paramètres
            if num_pulls < 1:
                messagebox.showerror("Erreur", "Le nombre de pulls doit être au moins 1")
                return
            
            if not (0 <= initial_pity <= 90):
                messagebox.showerror("Erreur", "Le pity initial doit être entre 0 et 90")
                return
            
            # Désactiver le bouton et afficher le statut
            self.stats_run_button.config(state=tk.DISABLED)
            self.stats_status_label.config(text="Simulations en cours...")
            
            # Lancer les simulations dans un thread séparé
            thread = threading.Thread(
                target=self._run_statistics_thread,
                args=(
                    num_pulls, config, banner_type, use_starlight,
                    initial_pity, five_star_guaranteed
                )
            )
            thread.daemon = True
            thread.start()
            
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Le fichier JSON n'est pas valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
    
    def _run_statistics_thread(self, num_pulls, config, banner_type, use_starlight, initial_pity, five_star_guaranteed):
        """Exécute les 1000 simulations dans un thread séparé"""
        try:
            num_simulations = 1000
            five_star_desired_counts = []
            five_star_undesired_counts = []
            four_star_counts = []
            four_star_weapon_counts = []
            
            for i in range(num_simulations):
                # Mettre à jour la barre de progression
                self.stats_progress['value'] = ((i + 1) / num_simulations) * 100
                self.stats_status_label.config(text=f"Simulation {i + 1}/{num_simulations}")
                self.root.update_idletasks()
                
                # Lancer une simulation
                results = simulate_pulls(
                    num_pulls,
                    config,
                    banner_type=banner_type,
                    use_starlight=use_starlight,
                    initial_pity_five_star=initial_pity,
                    five_star_guaranteed=five_star_guaranteed
                )
                
                # Enregistrer les résultats
                five_star_desired_counts.append(results['five_star_desired'])
                five_star_undesired_counts.append(results['five_star_undesired'])
                four_star_counts.append(results['four_star_characters'])
                four_star_weapon_counts.append(results['four_star_weapons'])
            
            # Créer les graphiques
            self._create_statistics_graphs(
                five_star_desired_counts,
                five_star_undesired_counts,
                four_star_counts,
                four_star_weapon_counts
            )
            
            self.stats_status_label.config(text="Simulations terminées !")
            
        except Exception as e:
            self.stats_status_label.config(text=f"Erreur : {e}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
        finally:
            self.stats_run_button.config(state=tk.NORMAL)
    
    def _create_statistics_graphs(self, five_star_desired, five_star_undesired, four_star_char, four_star_weap):
        """Crée les graphiques de distribution"""
        # Nettoyer les graphiques précédents
        for widget in self.stats_canvas_frame.winfo_children():
            widget.destroy()
        
        # Créer une figure avec 2 sous-graphiques
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Graphique 1 : Personnages 5*
        ax1 = fig.add_subplot(121)
        desired_counter = Counter(five_star_desired)
        undesired_counter = Counter(five_star_undesired)
        
        # Préparer les données pour le graphique groupé
        max_desired = max(desired_counter.keys()) if desired_counter else 0
        max_undesired = max(undesired_counter.keys()) if undesired_counter else 0
        max_val = max(max_desired, max_undesired) + 1
        
        x_vals = list(range(0, max_val))
        desired_vals = [desired_counter.get(x, 0) for x in x_vals]
        undesired_vals = [undesired_counter.get(x, 0) for x in x_vals]
        
        width = 0.35
        ax1.bar([x - width/2 for x in x_vals], desired_vals, width, label='Désiré', alpha=0.8)
        ax1.bar([x + width/2 for x in x_vals], undesired_vals, width, label='Non désiré', alpha=0.8)
        
        ax1.set_xlabel('Nombre d\'obtentions')
        ax1.set_ylabel('Fréquence (sur 1000 simulations)')
        ax1.set_title('Distribution - Personnages 5*')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(x_vals)
        
        # Graphique 2 : Armes 4*
        ax2 = fig.add_subplot(122)
        char_counter = Counter(four_star_char)
        weap_counter = Counter(four_star_weap)
        
        max_char = max(char_counter.keys()) if char_counter else 0
        max_weap = max(weap_counter.keys()) if weap_counter else 0
        max_val2 = max(max_char, max_weap) + 1
        
        x_vals2 = list(range(0, max_val2))
        char_vals = [char_counter.get(x, 0) for x in x_vals2]
        weap_vals = [weap_counter.get(x, 0) for x in x_vals2]
        
        width = 0.35
        ax2.bar([x - width/2 for x in x_vals2], char_vals, width, label='Personnages', alpha=0.8)
        ax2.bar([x + width/2 for x in x_vals2], weap_vals, width, label='Armes', alpha=0.8)
        
        ax2.set_xlabel('Nombre d\'obtentions')
        ax2.set_ylabel('Fréquence (sur 1000 simulations)')
        ax2.set_title('Distribution - Objets 4*')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(x_vals2)
        
        fig.tight_layout()
        
        # Afficher le graphique dans le canvas Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.stats_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def start_gui():
    root = tk.Tk()
    app = GachaSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
if __name__ == "__main__":
    start_gui()