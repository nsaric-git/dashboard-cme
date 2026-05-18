# -*- coding: utf-8 -*-
# =========================================================
# app.py - Point d'entrée multi-pages avec authentification
# =========================================================
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Configuration globale (s'applique à toutes les pages)
st.set_page_config(
    page_title="WBE — Dashboard ChaMalEaux",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# AUTHENTIFICATION
# ----------------------

CONFIG_PATH = Path("auth_config.yaml")


def _load_auth_config() -> dict:
    """
    Charge la configuration d'authentification.
    Priorité : Streamlit Secrets (cloud) > fichier YAML local.
    """
    # Essai 1 : Streamlit Secrets (déploiement cloud)
    try:
        if "auth_config" in st.secrets:
            return dict(st.secrets["auth_config"])
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        pass

    # Essai 2 : fichier YAML local
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=SafeLoader)

    st.error(
        "Configuration d'authentification introuvable. "
        "Attendu : auth_config.yaml en local OU st.secrets['auth_config'] sur Cloud."
    )
    st.stop()


config = _load_auth_config()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Affichage du formulaire de login
authenticator.login(location="main")

# Gestion des 3 états : connecté, échec, pas encore tenté
auth_status = st.session_state.get("authentication_status")

if auth_status is False:
    st.error("❌ Identifiants incorrects.")
    st.stop()
elif auth_status is None:
    st.info("👉 Veuillez vous identifier pour accéder au dashboard.")
    st.stop()

# === À partir d'ici, l'utilisateur est authentifié ===

# Récupérer les infos utilisateur dans la config pour les passer aux pages
username = st.session_state.get("username")
user_info = config["credentials"]["usernames"].get(username, {})
user_roles = user_info.get("roles", [])
user_city = user_info.get("city", None)

# Stocker dans session_state pour que dashboard.py y accède
st.session_state["user_username"] = username
st.session_state["user_roles"] = user_roles
st.session_state["user_city"] = user_city
st.session_state["is_admin"] = "admin" in user_roles

# Sidebar : nom de l'utilisateur + bouton logout
with st.sidebar:
    st.markdown(f"👤 **{user_info.get('first_name', '')} {user_info.get('last_name', '')}**")
    st.caption(f"Connecté en tant que `{username}`")
    authenticator.logout(location="sidebar", button_name="🚪 Se déconnecter")
    st.divider()

# Définition des pages
home_page = st.Page(
    "pages/home.py",
    title="Accueil",
    icon="🏠",
)

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊"
)

pg = st.navigation([home_page, dashboard_page])
pg.run()