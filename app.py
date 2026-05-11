# -*- coding: utf-8 -*-
# =========================================================
# app.py - Point d'entrée multi-pages
# Router pour les pages: Accueil + Dashboard
# =========================================================
import streamlit as st

# Configuration globale (s'applique à toutes les pages)
st.set_page_config(
    page_title="WBE — Dashboard CME",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Définition des pages
home_page = st.Page(
    "pages/home.py",
    title="Accueil",
    icon="🏠",
    #default=True
)

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊"
)

# Configuration de la navigation
pg = st.navigation([home_page, dashboard_page])
pg.run()