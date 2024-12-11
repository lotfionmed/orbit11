# Éditeur de Texte Libre

## Description
Une application web permettant d'écrire et de déplacer du texte librement sur une page blanche, avec sauvegarde dans une base de données.

## Prérequis
- Python 3.8+
- pip

## Installation
1. Clonez le dépôt
2. Créez un environnement virtuel:
   ```
   python -m venv venv
   venv\Scripts\activate  # Sur Windows
   ```
3. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

## Lancement de l'application
```
python app.py
```
Ouvrez un navigateur et accédez à `http://localhost:5000`

## Fonctionnalités
- Écrire du texte n'importe où sur la page
- Déplacer les textes par glisser-déposer
- Sauvegarde automatique dans une base de données SQLite
