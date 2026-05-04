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

Lors de la réunion du 11 février 2026, les STEP ont autorisé la mise en commun de leurs données
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

# ----------------------
# SECTION 2 — QU'EST-CE QUE LA WBE ?
# ----------------------
st.header("2. Qu'est-ce que la WBE ?")

st.markdown(
    """
L'épidémiologie par les eaux usées (en anglais *wastewater based epidemiology* = WBE) est une
approche permettant d'estimer la consommation de substances au sein d'une population de manière
non invasive, en analysant des composés dans les eaux usées (Baz-Lomba et al., 2025).

Cette approche se base sur le principe suivant : tous les produits ingérés par un être humain
sont excrétés via les selles et/ou les urines. Ces résidus peuvent être identiques au produit
consommé (= substance parent) ou alors ils ont été transformés par le corps (= métabolite). Ces
résidus sont alors présents dans les eaux usées.

Afin d'effectuer les analyses, des prélèvements sont effectués à l'entrée des STEP. Ces
échantillons sont ensuite préparés en laboratoire puis sont analysés par LC-MS/MS, afin de
détecter et de quantifier les substances ciblées. Ainsi, il est possible de déterminer la
concentration des substances d'intérêt (de l'ordre du ng/L).

Cette concentration dépend de la quantité totale de substance excrétée par la population, mais
aussi du volume d'eaux usées qui arrive à la STEP. Une concentration mesurée en ng/L n'est donc
pas directement comparable entre STEPs de tailles différentes. C'est pourquoi, à partir de la
concentration mesurée, du débit journalier de la STEP, et de la population desservie, on calcule
la **charge journalière normalisée** (mg/jour/1000 habitants), qui est l'indicateur principal
utilisé dans ce dashboard.

Cette valeur sert alors d'indicateur de consommation **collective** : elle reflète la consommation
totale de la population desservie par la STEP, sans permettre l'identification de consommateurs
individuels. Cette charge normalisée peut être exploitée de plusieurs manières en recherche :

- **Suivi temporel** : il s'agit d'étudier l'évolution des charges en fonction du temps. Ainsi,
  il est possible de détecter la présence de schémas de consommation (ex : semaine vs week-end).
"""
)

# Placeholder pour la première image
st.info("🖼️ *Image à insérer : exemple de suivi temporel*")

st.markdown(
    """
- **Évaluation géographique** : lorsque des données de plusieurs régions sont disponibles, il est
  possible d'étudier des tendances géographiques (ex : Suisse romande vs. Suisse alémanique).
  Cette comparaison demande toutefois des précautions méthodologiques importantes : elle ne doit
  pas être utilisée comme un « classement » entre villes, mais pour identifier des tendances
  régionales. Les facteurs qui rendent les comparaisons délicates sont détaillés en **section 4**.
"""
)

# Placeholder pour la deuxième image
st.info("🖼️ *Image à insérer : exemple d'évaluation géographique*")

st.markdown(
    """
- **Croisement avec d'autres sources de données** : il existe plusieurs indicateurs permettant
  d'évaluer la consommation de stupéfiants (saisies policières, drug checking, questionnaires…).
  Le fait de croiser ces différentes sources permet de construire une image objective du marché
  des stupéfiants.

Dans le cadre de ce tableau de bord, l'usage privilégié est le **suivi des tendances temporelles
au sein d'une même STEP**, qui constitue le terrain méthodologique le plus solide.

Toutefois, l'interprétation des résultats demande de comprendre comment lire les charges
journalières et quelles sont les limites méthodologiques. C'est l'objet des sections suivantes.
"""
)

st.markdown("---")