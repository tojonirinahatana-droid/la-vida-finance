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
        # Demander la permission de stockage pour Android
        page.permissions_request(ft.PermissionType.STORAGE)
        
        page.title = "LA VIDA - GESTION FINANCIÈRE"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 10
        
        # Création automatique du fichier Excel
        if not EXCEL_FILE.exists():
            pd.DataFrame(columns=["DATE", "CATEGORIE", "ENTREE", "SORTIE", "MOTIF"]).to_excel(EXCEL_FILE, index=False)
        
        etat = {"nom": "VUE GÉNÉRALE"}
        
        # --- COMPOSANTS ---
        lbl_init = ft.Text("0 Ar", size=16, weight="bold", color="white")
        lbl_sortie = ft.Text("0 Ar", size=16, weight="bold", color="white")
        lbl_entree = ft.Text("0 Ar", size=16, weight="bold", color="white")
        lbl_reste = ft.Text("0 Ar", size=16, weight="bold", color="white")
        
        lbl_bni_retrait = ft.Text("0 Ar", size=24, weight="bold", color="#d84315")
        lbl_bni_reste = ft.Text("0 Ar", size=24, weight="bold", color="#2e7d32")
        input_bni_montant = ft.TextField(label="Montant (Ar)", width=200)
        input_bni_motif = ft.TextField(label="Motif", width=200)
        
        input_date = ft.TextField(label="Date (JJ/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y"), width=250)
        input_cat = ft.Dropdown(label="Choisir Catégorie", options=[ft.dropdown.Option(c) for c in CATEGORIES_LIST[1:]], width=250)
        input_montant = ft.TextField(label="Montant (Ar)", width=250)
        input_motif = ft.TextField(label="Motif", width=250)

        data_table = ft.DataTable(columns=[ft.DataColumn(ft.Text("DATE")), ft.DataColumn(ft.Text("CAT.")), ft.DataColumn(ft.Text("SORTIE")), ft.DataColumn(ft.Text("ENTRÉE")), ft.DataColumn(ft.Text("MOTIF"))], rows=[])
        bni_history_table = ft.DataTable(columns=[ft.DataColumn(ft.Text("DATE")), ft.DataColumn(ft.Text("SORTIE")), ft.DataColumn(ft.Text("ENTRÉE")), ft.DataColumn(ft.Text("RESTE")), ft.DataColumn(ft.Text("MOTIF"))], rows=[])

        # --- FONCTIONS ---
        def enregistrer_bni(is_entree):
            if not input_bni_montant.value: return
            montant = float(input_bni_montant.value)
            df = pd.read_excel(EXCEL_FILE)
            nouveau = pd.DataFrame([{"DATE": datetime.now().strftime("%d/%m/%Y"), "CATEGORIE": "BANQUE BNI",
                                    "ENTREE": montant if is_entree else 0,
                                    "SORTIE": 0 if is_entree else montant, 
                                    "MOTIF": input_bni_motif.value}])
            pd.concat([df, nouveau], ignore_index=True).to_excel(EXCEL_FILE, index=False)
            input_bni_montant.value = ""
            input_bni_motif.value = ""
            rafraichir()

        def rafraichir(e=None):
            initiale = get_initiale()
            df = pd.read_excel(EXCEL_FILE)
            e_v = df['ENTREE'].sum() if 'ENTREE' in df.columns else 0
            s_v = df['SORTIE'].sum() if 'SORTIE' in df.columns else 0
            
            bni_df = df[df['CATEGORIE'] == "BANQUE BNI"].copy()
            bni_df['SOLDE_BNI'] = (bni_df['ENTREE'] - bni_df['SORTIE']).cumsum()
            
            lbl_init.value = f"{initiale:,.0f} Ar"
            lbl_entree.value = f"{e_v:,.0f} Ar"
            lbl_sortie.value = f"{s_v:,.0f} Ar"
            lbl_reste.value = f"{(initiale - s_v + e_v):,.0f} Ar"
            lbl_bni_retrait.value = f"{bni_df['SORTIE'].sum():,.0f} Ar"
            lbl_bni_reste.value = f"{bni_df['SOLDE_BNI'].iloc[-1] if not bni_df.empty else 0:,.0f} Ar"
            
            bni_history_table.rows.clear()
            for _, r in bni_df.tail(20).iloc[::-1].iterrows():
                bni_history_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get('DATE', '')))),
                    ft.DataCell(ft.Text(f"{r.get('SORTIE', 0):,.0f}")),
                    ft.DataCell(ft.Text(f"{r.get('ENTREE', 0):,.0f}")),
                    ft.DataCell(ft.Text(f"{r.get('SOLDE_BNI', 0):,.0f}")),
                    ft.DataCell(ft.Text(str(r.get('MOTIF', '')))),
                ]))
            
            data_table.rows.clear()
            temp_df = df if etat["nom"] == "VUE GÉNÉRALE" else df[df['CATEGORIE'] == etat["nom"]]
            for _, r in temp_df.tail(50).iloc[::-1].iterrows():
                data_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get('DATE', '')))),
                    ft.DataCell(ft.Text(str(r.get('CATEGORIE', '')))),
                    ft.DataCell(ft.Text(f"{r.get('SORTIE', 0):,.0f}")),
                    ft.DataCell(ft.Text(f"{r.get('ENTREE', 0):,.0f}")),
                    ft.DataCell(ft.Text(str(r.get('MOTIF', '')))),
                ]))

            is_bni = (etat["nom"] == "BANQUE BNI")
            bni_view.visible = is_bni
            data_table.visible = not is_bni
            page.update()

        def valider(is_entree):
            if not input_montant.value or not input_cat.value: return
            df = pd.read_excel(EXCEL_FILE)
            nouveau = pd.DataFrame([{"DATE": input_date.value, "CATEGORIE": input_cat.value,
                                    "ENTREE": float(input_montant.value) if is_entree else 0,
                                    "SORTIE": float(input_montant.value) if not is_entree else 0, 
                                    "MOTIF": input_motif.value}])
            pd.concat([df, nouveau], ignore_index=True).to_excel(EXCEL_FILE, index=False)
            rafraichir()

        bni_view = ft.Column([
            ft.Text("BANQUE BNI - GESTION ET HISTORIQUE", size=20, weight="bold"),
            ft.Row([
                ft.Container(ft.Column([ft.Text("RETRAIT BNI", size=10), lbl_bni_retrait]), bgcolor="#262626", padding=20, border_radius=10, expand=True),
                ft.Container(ft.Column([ft.Text("RESTE BNI", size=10), lbl_bni_reste]), bgcolor="#262626", padding=20, border_radius=10, expand=True),
            ]),
            ft.Row([input_bni_montant, input_bni_motif]),
            ft.Row([ft.ElevatedButton("ENREGISTRER RETRAIT", bgcolor="red", on_click=lambda e: enregistrer_bni(False)), 
                    ft.ElevatedButton("ENREGISTRER DÉPÔT", bgcolor="green", on_click=lambda e: enregistrer_bni(True))]),
            ft.Container(content=ft.Column([bni_history_table], scroll="auto"), height=200, bgcolor="#1e1e1e", border_radius=5)
        ], visible=False)

        page.add(
            ft.Text("LA VIDA - GESTION FINANCIÈRE", size=22, weight="bold", color="red"),
            ft.Row([ft.Container(ft.Column([ft.Text("INITIALE", size=10), lbl_init], horizontal_alignment="center"), bgcolor="#424242", padding=10, width=170),
                    ft.Container(ft.Column([ft.Text("SORTIE", size=10), lbl_sortie], horizontal_alignment="center"), bgcolor="#b71c1c", padding=10, width=170),
                    ft.Container(ft.Column([ft.Text("ENTREE", size=10), lbl_entree], horizontal_alignment="center"), bgcolor="#1b5e20", padding=10, width=170),
                    ft.Container(ft.Column([ft.Text("RESTE", size=10), lbl_reste], horizontal_alignment="center"), bgcolor="#0d47a1", padding=10, width=170)]),
            ft.Row([
                ft.Container(ft.Column([input_date, input_cat, input_montant, input_motif, ft.ElevatedButton("ENREGISTRER", on_click=lambda e: valider(False))]), width=300),
                ft.Column([
                    ft.Row([ft.Container(ft.Text(c), bgcolor="#333333", padding=10, on_click=lambda e, c=c: (etat.update({"nom": c}), rafraichir())) for c in CATEGORIES_LIST], scroll="always"), 
                    bni_view, 
                    ft.Container(content=ft.Column([data_table], scroll="auto"), height=350)
                ], expand=True)
            ])
        )
        rafraichir()
        
    except Exception as e:
        # Affiche l'erreur en rouge si ça crash au démarrage
        page.add(ft.Text(f"ERREUR FATALE : {str(e)}", size=20, color="red"))
        page.update()

ft.app(target=main)
