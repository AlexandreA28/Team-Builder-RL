# Rocket League – Team Builder

Une application de bureau développée en Python (Tkinter) pour générer automatiquement des équipes équilibrées sur Rocket League. Idéal pour organiser des tournois entre amis ou des sessions privées sans prises de tête !

---

## Fonctionnalités

* **Gestion des joueurs :** Ajout, modification (double-clic ou touche Entrée) et suppression de joueurs avec leur MMR.
* **Sauvegarde automatique :** Les joueurs inscrits sont automatiquement sauvegardés localement dans un fichier `joueurs.json`.
* **Génération équilibrée :** Création d'équipes en 2 VS 2 ou 3 VS 3 basées sur un algorithme minimisant l'écart de MMR entre les équipes.
* **Paramètres ajustables :** Possibilité de définir l'écart de MMR maximum toléré pour forcer un matchmaking équitable.
* **Export Discord :** Un bouton dédié permet de copier instantanément le résultat du tirage au sort (avec un formatage propre en bloc de code) pour le coller directement sur Discord.

## Utilisation

### Option 1 : Utilisation de l'exécutable (.exe)
Si vous disposez de la version compilée (fichier `.exe`) :
1. Double-cliquez sur l'application.
2. Saisissez le Pseudo et MMR de vos joueurs.
3. Cliquez sur "Générer les équipes" et voilà !

### Option 2 : Lancement depuis le code source (Python)
Si vous souhaitez exécuter ou modifier le code source, vous aurez besoin de Python installé sur votre machine.

1. **Prérequis :** L'application utilise la bibliothèque externe `Pillow`. Installez-la via votre terminal :
   ```bash
   pip install -r requirements.txt
   ```
2. **Exécution :** Lancez l'interface graphique avec la commande :
   ```bash
   python app.py
   ```

### Création de l'exécutable (.exe)
Si vous souhaitez compiler l'exécutable vous-même à partir du code source (par exemple après l'avoir modifié), suivez ces étapes :

1. **Prérequis :** La compilation utilise la bibliothèque externe `pyinstaller`. Installez-la via votre terminal :
   ```bash
   pip install pyinstaller
   ```
2. **Exécution :** Placez-vous dans le dossier du projet avec votre terminal et lancez la commande de compilation :
   ```bash
   pyinstaller --noconsole --icon=icone_team_builder.ico --add-data "ranks;ranks" --add-data "icone_team_builder.ico;." --name "rl_team_builder" app.py
   ```
Note : L'exécutable final sera généré dans le sous-dossier `dist/`.


## Structure du projet

* **app.py** : Le code source de l'interface de l'application Tkinter.
* **tournoi_logic.py** Le code source de la logique d'équilibrage.

* **ranks/** : Dossier contenant les images PNG/JPG des différents rangs de Rocket League.

* **joueurs.json** : Fichier généré automatiquement pour sauvegarder la liste des joueurs.

* **icone_team_builder.ico** : L'icône de l'application.

## Technologies utilisées
* **Python 3**
* **Tkinter** (Interface graphique native de Python)
* **Pillow** (Gestion des images de ranks)