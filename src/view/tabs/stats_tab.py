import tkinter as tk
from tkinter import ttk


def create_stats_tab(gui_instance, notebook):
    """Troisième onglet : Statistiques"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text="Statistiques")
    
    # Titre
    title = ttk.Label(frame, text="Statistiques", font=("Arial", 16, "bold"))
    title.pack(pady=10)
    
    # Texte d'aide
    help_text = """

    """
    
    text_widget = tk.Label(frame, text=help_text, justify=tk.LEFT, wraplength=900)
    text_widget.pack(pady=20)
