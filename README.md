# Monitoring Inscription ABB

Ce projet surveille une page web pour détecter tout changement et envoie une alerte sonore (bip) ainsi qu'un e-mail.

## Structure

- `monitor.py` : Script principal de surveillance.
- `requirements.txt` : Dépendances Python.
- `Dockerfile` : Configuration de l'image Docker.
- `docker-compose.yml` : Configuration du conteneur pour le redémarrage automatique.
- `.env` : Variables d'environnement (URL, Email, SMTP). À remplir en suivant l'exemple `.env.example`.

## Installation et Utilisation

1. Copier le fichier `.env.example` vers `.env` et le remplir avec vos propres informations :
   ```bash
   cp .env.example .env
   ```
2. Lancer le conteneur en mode détaché (ou avec la tâche VS code associée) :
   ```bash
   docker-compose up -d --build
   ```
3. Pour voir les logs de surveillance :
   ```bash
   docker logs -f surveillance_abb
   ```

## Persistance

Le paramètre `restart: always` dans `docker-compose.yml` garantit que le conteneur redémarrera dès que Docker Desktop sera lancé sur votre machine. Assurez-vous que Docker Desktop est configuré pour se lancer au démarrage de l'ordinateur dans ses préférences sous :

- **Settings** > **General** > **Start Docker Desktop when you log in**.
