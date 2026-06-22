import flet as ft
import pandas as pd
import os
import pathlib
from datetime import datetime

# --- CONFIGURATION CHEMINS ---
APP_DIR = pathlib.Path(__file__).parent.absolute()
EXCEL_FILE = APP_DIR / "finance_data_essai.xlsx"
CONFIG_FILE = APP_DIR / "config.txt"
CATEGORIES_LIST = ["VUE GÉNÉRALE", "CREDIT", "FRAIS", "GOUTTER", "DEVOIR SABATH", "SANTE", "RIZ", "PLUS", "ENTRÉES", "BANQUE BNI"]

def get_initiale():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return float(f.read().strip())
        except: return 400000.0
    return 400000.0

def main(page: ft.Page):
    try:
        page.title = "LA VIDA - GESTION FINANCIÈRE"
        page.theme_mode = ft.ThemeMode.DARK
        
        # Vérification du fichier Excel sans bloquer le lancement
        if not EXCEL_FILE.exists():
            df_init = pd.DataFrame(columns=["DATE", "CATEGORIE", "ENTREE", "SORTIE", "MOTIF"])
            df_init.to_excel(EXCEL_FILE, index=False)
        
        # --- UI SIMPLIFIÉE POUR TESTER ---
        page.add(ft.Text("LA VIDA - OK", size=20, color="green"))
        
        def rafraichir(e=None):
            try:
                df = pd.read_excel(EXCEL_FILE)
                # Juste un test pour voir si pandas lit bien
                page.add(ft.Text(f"Lignes trouvées: {len(df)}"))
                page.update()
            except Exception as e_read:
                page.add(ft.Text(f"Erreur lecture: {e_read}", color="red"))
                page.update()

        page.add(ft.ElevatedButton("Tester Chargement", on_click=rafraichir))
        
    except Exception as e:
        page.add(ft.Text(f"ERREUR FATALE: {str(e)}", size=20, color="red"))
    
    page.update()

ft.app(target=main)
