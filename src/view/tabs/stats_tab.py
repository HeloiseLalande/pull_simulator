import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import threading
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def get_json_configs():
    """Charge les fichiers JSON du dossier data et retourne un dictionnaire titre -> chemin"""
    data_folder = Path(__file__).parent.parent.parent.parent / "data"
    configs = {}
    
    if data_folder.exists():
        for json_file in sorted(data_folder.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    title = data.get("title", json_file.stem)
                    relative_path = f"data/{json_file.name}"
                    configs[title] = relative_path
            except (json.JSONDecodeError, IOError):
                pass
    
    return configs


def create_stats_tab(gui_instance, notebook):
    """Onglet : Statistiques avec graphiques"""
    frame = ttk.Frame(notebook, padding=15)
    notebook.add(frame, text="Statistiques")
    
    # Partie gauche - Paramètres
    left_frame = ttk.LabelFrame(frame, text="Paramètres", padding=10)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
    
    # --- Sélection du fichier JSON ---
    ttk.Label(left_frame, text="Fichier de configuration :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
    
    configs = get_json_configs()
    config_titles = list(configs.keys())
    
    gui_instance.stats_json_configs = configs
    
    gui_instance.stats_json_title = tk.StringVar(value=config_titles[0] if config_titles else "")
    config_combobox = ttk.Combobox(
        left_frame,
        textvariable=gui_instance.stats_json_title,
        values=config_titles,
        state="readonly",
        width=22
    )
    config_combobox.pack(anchor=tk.W, pady=5, padx=5)
    
    if config_titles:
        gui_instance.stats_json_path = tk.StringVar(value=configs[config_titles[0]])
        def on_config_change(*args):
            selected_title = gui_instance.stats_json_title.get()
            if selected_title in configs:
                gui_instance.stats_json_path.set(configs[selected_title])
        gui_instance.stats_json_title.trace('w', on_config_change)
    else:
        gui_instance.stats_json_path = tk.StringVar(value="data/honkai.json")
    
    # --- Type de bannière ---
    ttk.Label(left_frame, text="Type de bannière :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    
    gui_instance.stats_banner_type = tk.StringVar(value="character")
    ttk.Radiobutton(left_frame, text="Personnage", variable=gui_instance.stats_banner_type, value="character").pack(anchor=tk.W, padx=20)
    ttk.Radiobutton(left_frame, text="Arme", variable=gui_instance.stats_banner_type, value="weapon").pack(anchor=tk.W, padx=20)
    
    # --- Nombre de pulls ---
    ttk.Label(left_frame, text="Nombre de pulls :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    gui_instance.stats_num_pulls = tk.IntVar(value=90)
    ttk.Spinbox(left_frame, from_=1, to=1000, textvariable=gui_instance.stats_num_pulls, width=10).pack(anchor=tk.W, padx=20, pady=5)
    
    # --- Utiliser starlight ---
    gui_instance.stats_use_starlight = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        left_frame,
        text="Consommer les starlight",
        variable=gui_instance.stats_use_starlight
    ).pack(anchor=tk.W, pady=(15, 5), padx=20)
    
    # --- Pity initial ---
    ttk.Label(left_frame, text="Pity 5* initial (0-90) :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    gui_instance.stats_initial_pity = tk.IntVar(value=0)
    ttk.Spinbox(left_frame, from_=0, to=90, textvariable=gui_instance.stats_initial_pity, width=10).pack(anchor=tk.W, padx=20, pady=5)
    
    # --- Garantie 5* ---
    gui_instance.stats_five_star_guaranteed = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        left_frame,
        text="Garantie 5* active",
        variable=gui_instance.stats_five_star_guaranteed
    ).pack(anchor=tk.W, pady=(15, 5), padx=20)
    
    # Bouton de lancement
    gui_instance.stats_run_button = ttk.Button(
        left_frame,
        text="🎲 LANCER (1000 SIMULATIONS)",
        command=lambda: gui_instance.run_statistics()
    )
    gui_instance.stats_run_button.pack(fill=tk.X, pady=(20, 10), padx=5)
    
    # Barre de progression
    gui_instance.stats_progress = ttk.Progressbar(
        left_frame,
        mode='determinate',
        length=200
    )
    gui_instance.stats_progress.pack(fill=tk.X, pady=5, padx=5)
    gui_instance.stats_progress['value'] = 0
    
    # Étiquette de statut
    gui_instance.stats_status_label = ttk.Label(left_frame, text="", font=("Arial", 9))
    gui_instance.stats_status_label.pack(anchor=tk.W, pady=(5, 0), padx=5)
    
    # Partie droite - Graphiques
    right_frame = ttk.LabelFrame(frame, text="Résultats", padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
    
    # Canvas pour les graphiques
    gui_instance.stats_canvas_frame = right_frame
    gui_instance.stats_figures = []

