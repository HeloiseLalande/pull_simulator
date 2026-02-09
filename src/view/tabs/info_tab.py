import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys
from pathlib import Path


def create_info_tab(gui_instance, notebook):
    """Premier onglet : Informations et accès aux données"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text="Informations")
    
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
        command=lambda: gui_instance.open_data_folder()
    )
    data_button.pack()
