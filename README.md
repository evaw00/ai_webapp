# Bild Galerie Webapp

## Setup

1. Python 3.8+ installieren
2. Virtuelle Umgebung erstellen (optional aber empfohlen):
    ```
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```
3. Dependencies installieren:
    ```
    pip install -r requirements.txt
    ```
4. Datenbank initialisieren:
    ```python
    from app import db
    db.create_all()
    ```
5. GitHub OAuth App erstellen:  
   - Gehe zu https://github.com/settings/developers  
   - Neue OAuth App erstellen  
   - Callback URL: `http://localhost:5000/login/github/authorized`  
   - Client ID und Secret in `app.py` eintragen (ersetze die Platzhalter)

6. App starten:
    ```
    flask run
    ```
7. Öffne im Browser `http://localhost:5000`

---

## Features

- Login via GitHub OAuth2
- Bilder hochladen mit Beschreibung
- Bilder anschauen & kommentieren
- Eigene Bilder löschen

---

## GitHub Push Anleitung

- Git initialisieren, falls noch nicht geschehen:
  ```
  git init
  git add .
  git commit -m "Initial commit Bild Galerie Webapp"
  ```
- Remote Repository hinzufügen:
  ```
  git remote add origin https://github.com/DEIN_USERNAME/DEIN_REPO.git
  ```
- Pushen:
  ```
  git branch -M main
  git push -u origin main
  ```
---

Viel Erfolg!# ai_webapp
