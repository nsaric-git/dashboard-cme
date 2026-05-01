# -*- coding: utf-8 -*-
# =========================================================
# pages/home.py - Page d'accueil
# Présentation du projet et limites d'interprétation des données WBE
# =========================================================
import streamlit as st

# ----------------------
# TITRE PRINCIPAL
# ----------------------
st.title("🧪 ChaMalEaux — Présentation et limites d'interprétation")

# ----------------------
# SOMMAIRE (placeholder — sera complété au fur et à mesure)
# ----------------------
st.info("📑 **Sommaire** — sera complété au fur et à mesure que les sections sont ajoutées.")

st.markdown("---")

# ----------------------
# SECTION 1 — BIENVENUE / INTRODUCTION
# ----------------------
st.header("1. Bienvenue")

st.markdown(
    """
**Bienvenue sur le dashboard des résultats du projet ChaMalEaux !**

Le projet ChaMalEaux a pour but de monitorer la consommation de divers stupéfiants par le biais
d'analyse des eaux usées. Il s'agit d'un projet supervisé par l'École des Sciences Criminelles,
à l'Université de Lausanne.

Ce tableau de bord est destiné aux personnels des STEP partenaires du projet, ainsi qu'aux autres
partenaires en fonction des accords qui ont été signés.

Lors de la réunion du 11 février 2026, les STEP ont autorisées la mise en commun de leurs données
afin de permettre une meilleure appréciation des résultats. Ainsi, ce tableau de bord est un outil
scientifique et collaboratif. **En aucun cas, les données présentes ne peuvent être communiquées
au public sans que les autres partenaires n'aient été avertis et sans qu'ils aient donné leur
autorisation.**

De plus, les données présentes sur ce site demandent une lecture éclairée en ce qui concerne leur
interprétation, ainsi qu'une bonne compréhension des limites inhérentes aux analyses des eaux
usées. C'est pourquoi cette page d'accueil rassemble les informations nécessaires à
l'interprétation des résultats. La lecture des sections suivantes est vivement conseillée avant
toute consultation du dashboard.
"""
)

st.markdown("---")