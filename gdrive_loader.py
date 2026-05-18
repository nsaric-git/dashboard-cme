"""
Module de téléchargement de fichiers Excel depuis Google Drive.

Utilise un Service Account pour s'authentifier (sans interaction utilisateur).
Le fichier de credentials est lu depuis :
  - En local : .streamlit/gdrive_credentials.json
  - Sur Streamlit Cloud : st.secrets["gdrive_credentials"]
"""

import io
import json
from pathlib import Path
from typing import Optional

import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Scope minimal : lecture seule sur Drive
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Chemin local du fichier de credentials (utilisé si pas sur Streamlit Cloud)
LOCAL_CREDS_PATH = Path(".streamlit") / "gdrive_credentials.json"


def _get_credentials() -> Credentials:
    """
    Récupère les credentials du Service Account.
    Priorité : Streamlit Secrets (cloud) > fichier local.
    Lève une erreur explicite si rien n'est trouvé.
    """
    # Essai 1 : Streamlit Secrets (déploiement cloud)
    try:
        if "gdrive_credentials" in st.secrets:
            creds_dict = dict(st.secrets["gdrive_credentials"])
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        # secrets.toml absent en local → on continue vers le fichier JSON
        pass

    # Essai 2 : fichier JSON local
    if LOCAL_CREDS_PATH.exists():
        return Credentials.from_service_account_file(str(LOCAL_CREDS_PATH), scopes=SCOPES)

    raise FileNotFoundError(
        f"Credentials Google introuvables. Attendu soit :\n"
        f"  - st.secrets['gdrive_credentials'] (sur Streamlit Cloud)\n"
        f"  - {LOCAL_CREDS_PATH.resolve()} (en local)"
    )


@st.cache_data(ttl=3600, show_spinner="Téléchargement des données depuis le serveur...")
def download_file_from_drive(file_id: str) -> bytes:
    """
    Télécharge un fichier depuis Google Drive et renvoie ses bytes bruts.
    Mise en cache pendant 1h pour éviter de retélécharger à chaque interaction.

    Args:
        file_id: ID Google Drive du fichier (la partie entre /d/ et /view dans l'URL)

    Returns:
        bytes : contenu binaire du fichier

    Raises:
        FileNotFoundError : si les credentials sont introuvables
        googleapiclient.errors.HttpError : si le téléchargement échoue
    """
    credentials = _get_credentials()
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    return buffer.read()


def load_excel_from_drive(file_id: str) -> bytes:
    """
    Helper qui télécharge un fichier Excel depuis Drive.
    Wrapper léger autour de download_file_from_drive() pour la lisibilité.
    """
    return download_file_from_drive(file_id)