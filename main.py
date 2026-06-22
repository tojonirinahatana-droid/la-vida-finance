import flet as ft

def main(page: ft.Page):
    # Ce code simple vérifie si l'application peut au moins s'afficher
    page.title = "Test LA VIDA"
    page.add(ft.Text("Test de démarrage réussi !", size=25, color="green"))
    page.add(ft.Text("Si vous voyez ce texte,", size=15))
    page.add(ft.Text("l'APK fonctionne.", size=15))
    page.update()

ft.app(target=main)
