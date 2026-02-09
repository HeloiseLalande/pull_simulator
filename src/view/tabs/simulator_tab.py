import tkinter as tk
from tkinter import ttk, scrolledtext


def create_simulator_tab(gui_instance, notebook):
    """Deuxième onglet : Simulateur de pulls"""
    frame = ttk.Frame(notebook, padding=15)
    notebook.add(frame, text="Simulateur")
    
    # Partie gauche - Paramètres
    left_frame = ttk.LabelFrame(frame, text="Paramètres", padding=10)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
    
    # --- Sélection du fichier JSON ---
    ttk.Label(left_frame, text="Fichier de configuration :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
    
    json_frame = ttk.Frame(left_frame)
    json_frame.pack(fill=tk.X, pady=5)
    
    gui_instance.json_path = tk.StringVar(value="data/honkai.json")
    ttk.Entry(json_frame, textvariable=gui_instance.json_path, width=25).pack(side=tk.LEFT, padx=5)
    ttk.Button(json_frame, text="Parcourir", command=lambda: gui_instance.select_json_file()).pack(side=tk.LEFT)
    
    # --- Type de bannière ---
    ttk.Label(left_frame, text="Type de bannière :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    
    gui_instance.banner_type = tk.StringVar(value="character")
    ttk.Radiobutton(left_frame, text="Personnage", variable=gui_instance.banner_type, value="character").pack(anchor=tk.W, padx=20)
    ttk.Radiobutton(left_frame, text="Arme", variable=gui_instance.banner_type, value="weapon").pack(anchor=tk.W, padx=20)
    
    # --- Nombre de pulls ---
    ttk.Label(left_frame, text="Nombre de pulls :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    gui_instance.num_pulls = tk.IntVar(value=90)
    ttk.Spinbox(left_frame, from_=1, to=1000, textvariable=gui_instance.num_pulls, width=10).pack(anchor=tk.W, padx=20, pady=5)
    
    # --- Utiliser starlight ---
    gui_instance.use_starlight = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        left_frame,
        text="Consommer les starlight pour bonus pulls",
        variable=gui_instance.use_starlight
    ).pack(anchor=tk.W, pady=(15, 5), padx=20)
    
    # --- Pity initial ---
    ttk.Label(left_frame, text="Pity 5* initial (0-90) :", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
    gui_instance.initial_pity = tk.IntVar(value=0)
    ttk.Spinbox(left_frame, from_=0, to=90, textvariable=gui_instance.initial_pity, width=10).pack(anchor=tk.W, padx=20, pady=5)
    
    # --- Garantie 5* ---
    gui_instance.five_star_guaranteed = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        left_frame,
        text="Garantie 5* active",
        variable=gui_instance.five_star_guaranteed
    ).pack(anchor=tk.W, pady=(15, 5), padx=20)
    
    # Bouton de lancement
    ttk.Button(
        left_frame,
        text="🎲 LANCER LA SIMULATION",
        command=lambda: gui_instance.run_simulation()
    ).pack(fill=tk.X, pady=(20, 10), padx=5)
    
    # Partie droite - Résultats
    right_frame = ttk.LabelFrame(frame, text="Résultats", padding=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
    
    gui_instance.results_text = scrolledtext.ScrolledText(
        right_frame,
        width=60,
        height=30,
        font=("Courier", 9),
        bg="#f0f0f0"
    )
    gui_instance.results_text.pack(fill=tk.BOTH, expand=True)
    gui_instance.results_text.insert(tk.END, "Les résultats apparaîtront ici...\n")
    gui_instance.results_text.config(state=tk.DISABLED)
