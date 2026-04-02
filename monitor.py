import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cloudscraper
from dotenv import load_dotenv

# Configuration
load_dotenv()
TARGET_URL = os.getenv("TARGET_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAILS = [e.strip() for e in os.getenv("RECEIVER_EMAILS", "").split(",") if e.strip()]
DATA_DIR = os.getenv("DATA_DIR", "data")

os.makedirs(DATA_DIR, exist_ok=True)


def get_latest_html():
    """Récupère le contenu du dernier fichier HTML sauvegardé."""
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("page_") and f.endswith(".html")]
    if not files:
        return None
    latest_file = os.path.join(DATA_DIR, sorted(files)[-1])
    with open(latest_file, "r", encoding="utf-8") as f:
        return f.read()


def save_html(content):
    """Sauvegarde le HTML avec un timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(DATA_DIR, f"page_{timestamp}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def get_page_content():
    """Récupère le HTML de la page via cloudscraper."""
    try:
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'linux', 'desktop': True})
        response = scraper.get(TARGET_URL, timeout=30)
        if response.status_code == 200:
            return response.text
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erreur HTTP : {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erreur lors de la récupération : {e}")
    return None


def send_notification(new_html, old_html=None):
    """Envoie un mail avec les changements."""
    msg = MIMEMultipart()
    msg['Subject'] = f"Changement détecté : Anglet Beach Bask"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAILS)

    body = f"Un changement a été détecté sur {TARGET_URL} à {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.\n\n"
    msg.attach(MIMEText(body, 'plain'))

    # Sauvegarde des versions pour archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file = os.path.join(DATA_DIR, f"page_{timestamp}.html")
    with open(new_file, "w", encoding="utf-8") as f:
        f.write(new_html)

    # Ajout des pièces jointes
    for content, name in [(new_html, "nouvelle_version.html"), (old_html, "ancienne_version.html")]:
        if content:
            part = MIMEText(content, "html", "utf-8")
            part.add_header("Content-Disposition", f"attachment; filename={name}")
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Notification envoyée à {', '.join(RECEIVER_EMAILS)}")
    except Exception as e:
        print(f"Erreur envoi mail : {e}")


def main():
    print(f"Surveillance de {TARGET_URL} lancée...")

    # Chargement état initial depuis le dernier fichier timestampé
    last_html = get_latest_html()

    while True:
        current_html = get_page_content()

        if current_html:
            if last_html and current_html != last_html:
                print("Changement détecté !")
                save_html(current_html)
                send_notification(current_html, last_html)
                last_html = current_html
            elif not last_html:
                print("Initialisation du contenu.")
                save_html(current_html)
                last_html = current_html
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Pas de changement.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
