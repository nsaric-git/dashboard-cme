# -*- coding: utf-8 -*-
# =========================================================
# WW_Option_A_with_bubble_map_3.py - Version corrigée
# - Carte avec couleur proportionnelle à la concentration
# - Boxplot avec couleur fixe par ville
# - Légende population améliorée
# - Plus de villes dans CITY_COORDS
# =========================================================
import numpy as np
import pandas as pd
import datetime as _dt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
import unicodedata
import re
import requests
from datetime import date
from typing import Optional
import streamlit.components.v1 as components

# ----------------------
# FICHIERS DE DONNÉES
# ----------------------
WBE_PATH = "260205_WW_AllData_LA_v2.xlsx" #"250430_WW_AllData_LA_v2.xlsx"
SEIZURE_PATH = "251113_Data.xlsx"

# ----------------------
# COULEURS - Palette étendue pour les villes
# ----------------------
COLOR_SEQ = [
    "#0f4c81", "#e63946", "#2a9d8f", "#e9c46a", "#f4a261",
    "#264653", "#a8dadc", "#457b9d", "#1d3557", "#ff6b6b",
    "#6a4c93", "#1982c4", "#8ac926", "#ffca3a", "#ff595e",
    "#90be6d", "#43aa8b", "#577590", "#f9844a", "#9b5de5",
]

# Échelle de couleur pour la concentration (du bleu clair au rouge foncé)
CONCENTRATION_COLORSCALE = [
    [0.0, "#F7E425"],
    [0.25, "#F58C46"],
    [0.5, "#CB4679"],
    [0.75, "#8707A6"],
    [1.0, "#41049D"],
]

# ----------------------
# DICTIONNAIRE DE COULEURS PAR VILLE (GLOBAL)
# ----------------------
CITY_COLOR_MAP = {}

# ----------------------
# COORDONNÉES DES VILLES (WGS84) - Liste étendue
# Clés en minuscules sans accents (via _norm).
# ----------------------
CITY_COORDS = {
    # Grandes villes suisses
    "geneve": (46.2044, 6.1432),
    "geneva": (46.2044, 6.1432),
    "lausanne": (46.5197, 6.6323),
    "zurich": (47.3769, 8.5417),
    "zuerich": (47.3769, 8.5417),
    "bale": (47.5596, 7.5886),
    "basel": (47.5596, 7.5886),
    "bern": (46.9480, 7.4474),
    "berne": (46.9480, 7.4474),
    "neuchatel": (46.9896, 6.9293),
    "lugano": (46.0037, 8.9511),
    "coire": (46.8523, 9.5300),
    "chur": (46.8523, 9.5300),

    # Villes moyennes
    "zuchwil": (47.2049, 7.5638),
    "schwyz": (47.0207, 8.6525),
    "lucerne": (47.0502, 8.3093),
    "luzern": (47.0502, 8.3093),
    "st gallen": (47.4245, 9.3767),
    "saint gallen": (47.4245, 9.3767),
    "winterthur": (47.4988, 8.7236),
    "thun": (46.7580, 7.6280),
    "fribourg": (46.8065, 7.1619),
    "freiburg": (46.8065, 7.1619),
    "sion": (46.2269, 7.3586),
    "sitten": (46.2269, 7.3586),
    "bienne": (47.1368, 7.2467),
    "biel": (47.1368, 7.2467),
    "yverdon": (46.7785, 6.6412),
    "yverdon les bains": (46.7785, 6.6412),
    "montreux": (46.4312, 6.9107),
    "vevey": (46.4628, 6.8432),
    "nyon": (46.3833, 6.2398),
    "morges": (46.5110, 6.4984),
    "renens": (46.5354, 6.5879),
    "ecublens": (46.5275, 6.5602),

    # Autres villes
    "aarau": (47.3925, 8.0444),
    "baden": (47.4733, 8.3066),
    "bellinzona": (46.1952, 9.0287),
    "locarno": (46.1708, 8.7994),
    "olten": (47.3520, 7.9079),
    "solothurn": (47.2088, 7.5323),
    "soleure": (47.2088, 7.5323),
    "schaffhausen": (47.6959, 8.6377),
    "schaffhouse": (47.6959, 8.6377),
    "zug": (47.1724, 8.5177),
    "zoug": (47.1724, 8.5177),
    "uster": (47.3472, 8.7207),
    "dietikon": (47.4038, 8.4008),
    "wetzikon": (47.3167, 8.8000),
    "rapperswil": (47.2264, 8.8267),
    "emmen": (47.0846, 8.3053),
    "kriens": (47.0351, 8.2740),
    "frauenfeld": (47.5585, 8.8988),
    "vernier": (46.2172, 6.0833),
    "meyrin": (46.2344, 6.0800),
    "carouge": (46.1833, 6.1394),
    "lancy": (46.1833, 6.1181),
    "onex": (46.1833, 6.1000),
    "payerne": (46.822011, 6.936081),
    "bulle": (46.619500, 7.056739),

    # Villes génériques (pour les données anonymisées)
    "ville 1": (46.5197, 6.6323),  # Position par défaut Lausanne
    "ville 2": (46.9480, 7.4474),  # Bern
    "ville 3": (47.3769, 8.5417),  # Zurich
    "ville 4": (46.2044, 6.1432),  # Genève
    "ville 5": (47.5596, 7.5886),  # Bâle
    "ville 6": (46.9896, 6.9293),  # Neuchâtel
    "ville 7": (46.0037, 8.9511),  # Lugano
    "ville 8": (47.0502, 8.3093),  # Lucerne
    "ville 9": (47.4245, 9.3767),  # St-Gallen
    "ville 10": (46.7580, 7.6280),  # Thun
    "city 1": (46.5197, 6.6323),
    "city 2": (46.9480, 7.4474),
    "city 3": (47.3769, 8.5417),
    "city 4": (46.2044, 6.1432),
    "city 5": (47.5596, 7.5886),
}

# ----------------------
# CLASSIFICATION LINGUISTIQUE DES VILLES (pour cadrage automatique de la carte)
# ----------------------
# Clés normalisées (minuscules sans accents) — passées par _norm()
ROMANDE_CITIES = {
    "geneve", "geneva", "lausanne", "morges", "neuchatel", "vevey",
    "yverdon", "yverdon les bains", "payerne", "bulle", "sion", "sitten",
    "nyon", "renens", "ecublens", "vernier", "meyrin", "carouge", "lancy",
    "onex", "bienne", "biel", "fribourg", "freiburg", "montreux",
}
# Villes "frontière" : leur présence ne déclenche pas le cadrage Suisse entière.
# Berne est officiellement bilingue et géographiquement à la limite romande.
NEUTRAL_CITIES = {"bern", "berne"}

def build_city_color_map(df: pd.DataFrame, color_palette: list) -> dict:
    """
    Construit un dictionnaire ville → couleur fixe.
    Les couleurs sont attribuées de manière déterministe (ordre alphabétique).
    """
    if "ville" not in df.columns:
        return {}

    cities = sorted(df["ville"].dropna().unique())
    return {city: color_palette[i % len(color_palette)] for i, city in enumerate(cities)}


# ----------------------
# MAPPING STUPÉFIANTS → ANALYTES
# ----------------------
RELATED_ANALYTES = {
    "Amphétamine": ["AMPH.2"],
    "Anabasine": ["ANBS.2"],
    "Cocaïne HCL": ["BE.1", "COC.1", "COE.1"],
    "Crack": ["BE.1", "COC.1", "AEME.2"],
    "Héroïne": ["6MAM.1", "HER.1", "MOR.1"],
    "Kétamine": ["KET.1"],
    "Méthadone": ["Methadone.1", "EDDP.1"],
    "Méthamphétamine": ["Methamphetamine.1"],
    "MDMA": ["MDMA.1", "HMMA.1"],
    "THC": ["THCCOOH.2"],
}

# ----------------------
# DESCRIPTIONS DES STUPÉFIANTS
# ----------------------
STUP_DESCRIPTIONS = {
    "Amphétamine": {
        "description": "Stimulant du système nerveux central. L'amphétamine est souvent consommée sous forme de sulfate d'amphétamine.",
        "parent": "Amphétamine (AMPH)",
        "metabolites": "AMPH.2 (amphétamine urinaire)",
        "note": "L'amphétamine peut aussi être un métabolite de la méthamphétamine."
    },
    "Anabasine": {
        "description": "Alcaloïde présent dans le tabac. Marqueur de consommation de tabac non transformé.",
        "parent": "Anabasine (ANBS)",
        "metabolites": "ANBS.2",
        "note": "Utilisé comme biomarqueur de consommation de tabac."
    },
    "Cocaïne HCL": {
        "description": "Forme chlorhydrate de la cocaïne, consommée par voie nasale ou injectable.",
        "parent": "Cocaïne (COC.1)",
        "metabolites": "Benzoylecgonine (BE.1), Cocaéthylène (COE.1 - co-consommation avec alcool)",
        "note": "Le ratio BE/COC peut indiquer le mode de consommation."
    },
    "Crack": {
        "description": "Forme base libre de la cocaïne, consommée par inhalation/fumée.",
        "parent": "Cocaïne (COC.1)",
        "metabolites": "Benzoylecgonine (BE.1), Anhydroecgonine méthyl ester (AEME.2 - marqueur spécifique de pyrolyse)",
        "note": "L'AEME est un marqueur spécifique de la consommation par fumée (crack)."
    },
    "Héroïne": {
        "description": "Opiacé semi-synthétique dérivé de la morphine. Forte dépendance physique.",
        "parent": "Héroïne (HER.1, diacétylmorphine)",
        "metabolites": "6-Monoacétylmorphine (6MAM.1 - marqueur spécifique), Morphine (MOR.1)",
        "note": "Le 6-MAM est le marqueur le plus spécifique de la consommation d'héroïne."
    },
    "Kétamine": {
        "description": "Anesthésique dissociatif utilisé de manière récréative pour ses effets hallucinogènes.",
        "parent": "Kétamine (KET.1)",
        "metabolites": "Norkétamine (non mesuré dans ce dataset)",
        "note": "Tendance à la hausse dans plusieurs pays européens."
    },
    "Méthadone": {
        "description": "Opioïde synthétique utilisé en traitement de substitution aux opiacés (TSO).",
        "parent": "Méthadone (Methadone.1)",
        "metabolites": "EDDP (EDDP.1 - métabolite principal)",
        "note": "Indicateur de traitements de substitution plutôt que d'usage récréatif."
    },
    "Méthamphétamine": {
        "description": "Stimulant puissant du système nerveux central, très addictif.",
        "parent": "Méthamphétamine (Methamphetamine.1)",
        "metabolites": "Amphétamine (métabolite, ~10-20% de la dose)",
        "note": "Prévalence variable selon les régions (plus élevée en Europe de l'Est et Asie)."
    },
    "MDMA": {
        "description": "Ecstasy/MDMA - Entactogène-stimulant, consommé principalement en contexte festif.",
        "parent": "MDMA (MDMA.1)",
        "metabolites": "HMMA (HMMA.1 - 4-hydroxy-3-méthoxyméthamphétamine)",
        "note": "Pics de consommation souvent observés les week-ends et lors d'événements festifs."
    },
    "THC": {
        "description": "Principal composé psychoactif du cannabis (tétrahydrocannabinol).",
        "parent": "THC",
        "metabolites": "THC-COOH (THCCOOH.2 - métabolite urinaire principal)",
        "note": "Substance illicite la plus consommée. Le THC-COOH est le seul marqueur fiable dans les eaux usées."
    },
}

# ----------------------
# CLASSIFICATION ANALYTES
# ----------------------
ANALYTE_OVERRIDES = {
    "COC.1": "parent", "BE.1": "metabolite", "COE.1": "metabolite", "AEME.2": "metabolite",
    "MDMA.1": "parent", "HMMA.1": "metabolite", "KET.1": "parent",
    "6MAM.1": "metabolite", "HER.1": "parent", "MOR.1": "metabolite",
    "Methadone.1": "parent", "EDDP.1": "metabolite", "THCCOOH.2": "metabolite",
    "Methamphetamine.1": "parent", "AMPH.2": "metabolite", "ANBS.2": "parent"
}

ANALYTE_CLASS = {
    "Cocaine": "parent", "Cocaïne": "parent", "Cocaïne HCL": "parent",
    "Benzoylecgonine": "metabolite", "BE": "metabolite",
    "MDMA": "parent", "MDA": "metabolite", "HMMA": "metabolite",
    "Amphetamine": "parent", "Methamphetamine": "parent",
    "Ketamine": "parent", "Norketamine": "metabolite",
    "THCCOOH": "metabolite", "Morphine": "metabolite", "6-MAM": "metabolite",
}

_META_REGEX = re.compile(
    r"(?:\b(?:nor|dehydro|hydroxy|oxo)\b|cooh\b|gluc(?:uronide)?\b|sulf(?:ate|o)\b|\b(?:hm?ma|be|eme|aeme|6 ?mam)\b)",
    re.I
)

# ----------------------
# CONSTANTES POUR LE TRAITEMENT DES DONNÉES
# ----------------------
LOQ_REPLACEMENT_VALUE = 5.0  # ng/L - valeur utilisée quand inf_LOQ = TRUE
LOD_REPLACEMENT_VALUE = 0.0  # ng/L - valeur utilisée quand inf_LOD = TRUE

# ----------------------
# STYLE CSS
# ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #0f4c81 0%, #1a6bb5 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.main-header h1 { margin: 0; font-size: 1.8rem; font-weight: 700; }
.main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #e8eef4;
    padding: 6px;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    padding: 10px 20px;
    color: #0f4c81;
    font-weight: 500;
    font-size: 0.95rem;
    border: none;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(15, 76, 129, 0.1); }
.stTabs [aria-selected="true"] {
    background: #0f4c81 !important;
    color: white !important;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(15, 76, 129, 0.3);
}

/* Stup Panel */
.stup-panel {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}
.stup-panel-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}
.stup-panel-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f4c81;
}
.stup-panel-badge {
    background: #0f4c81;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}
.stup-description {
    font-size: 0.85rem;
    color: #495057;
    line-height: 1.5;
    margin-bottom: 0.5rem;
}
.stup-analytes {
    font-size: 0.8rem;
    color: #6c757d;
    background: white;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    border-left: 3px solid #0f4c81;
}

/* KPI Cards */
.kpi-container {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.kpi-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    flex: 1;
    min-width: 150px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.kpi-label {
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f4c81;
}

/* City badge */
.city-badge {
    display: inline-block;
    background: linear-gradient(135deg, #0f4c81, #1a6bb5);
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Section headers */
.section-header {
    background: #f8f9fa;
    border-left: 4px solid #0f4c81;
    padding: 0.75rem 1rem;
    margin: 1.5rem 0 1rem 0;
    border-radius: 0 8px 8px 0;
    font-weight: 600;
    color: #333;
}

/* Comparison banner */
.comparison-banner {
    background: linear-gradient(90deg, #e8f4fd, #d1e9fc);
    border: 1px solid #b3d7f5;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}

/* Chart footnote */
.chart-footnote {
    font-size: 0.8rem;
    color: #666;
    padding: 0.5rem 0;
    border-top: 1px solid #eee;
    margin-top: 0.5rem;
}

/* Data info box */
.data-info-box {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
}

/* Legend for data flags */
.flag-legend {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
}
.flag-legend span {
    margin-right: 1rem;
}
.flag-lod { color: #dc3545; }
.flag-loq { color: #fd7e14; }
.flag-outlier { color: #6c757d; text-decoration: line-through; }

/* Population legend box */
.pop-legend-box {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 0.75rem;
    margin-top: 0.5rem;
}
.pop-legend-title {
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
    color: #333;
}
.pop-legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
    font-size: 0.8rem;
}
.pop-circle {
    border-radius: 50%;
    background: rgba(15, 76, 129, 0.3);
    border: 2px solid #333;
    display: inline-block;
}

/* Légende population superposée sur la carte */
.map-wrapper {
    position: relative;
}
.map-pop-legend {
    position: absolute;
    bottom: 30px;
    right: -10px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 11px;
    color: #333;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
    pointer-events: none;
}
.map-pop-legend-title {
    font-weight: 600;
    margin-bottom: 6px;
    text-align: center;
}
.map-pop-legend-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 3px 0;
}
.map-pop-circle {
    display: inline-block;
    border-radius: 50%;
    background: rgba(120, 120, 120, 0.4);
    border: 1.5px solid #555;
    flex-shrink: 0;
}
/* Tailles cohérentes avec SIZE_MIN_PX=14 / SIZE_MAX_PX=52, courbe √population */
.map-pop-circle.s-500k { width: 52px; height: 52px; }
.map-pop-circle.s-250k { width: 41px; height: 41px; }
.map-pop-circle.s-100k { width: 31px; height: 31px; }
.map-pop-circle.s-50k  { width: 24px; height: 24px; }
.map-pop-circle.s-10k  { width: 14px; height: 14px; }
</style>
""", unsafe_allow_html=True)


# ----------------------
# HELPER FUNCTIONS
# ----------------------
def _norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def classify_analyte(name: str, selected_stup: str = "") -> str:
    key_exact = str(name).strip()
    if key_exact in ANALYTE_OVERRIDES:
        return ANALYTE_OVERRIDES[key_exact]
    n = _norm(name)
    if n in {"mda", "aeme", "anhydroecgonine methyl ester", "coe", "cocaethylene"}:
        return "metabolite"
    if name in ANALYTE_CLASS:
        return ANALYTE_CLASS[name]
    if _META_REGEX.search(name):
        return "metabolite"
    return "parent"


def _fmt_d(d) -> str:
    if pd.isna(d):
        return "—"
    return pd.to_datetime(d).strftime("%d.%m.%Y")


def style_legend(fig, size=14):
    fig.update_layout(
        legend=dict(
            font=dict(size=size),
            x=1.02, xanchor="left",
            y=1, yanchor="top",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
        margin=dict(l=20, r=150, t=40, b=40)
    )


def figure_footnote(df_plot: pd.DataFrame, y_col: str) -> str:
    if df_plot.empty or y_col not in df_plot.columns:
        return "Aucune donnée utilisable."
    d2 = df_plot.dropna(subset=[y_col, "date"]).copy()
    if d2.empty:
        return "Aucune donnée utilisable."
    dmin, dmax = _fmt_d(d2["date"].min()), _fmt_d(d2["date"].max())
    n_total = len(d2)

    info_parts = [f"Points : **{n_total}**", f"Période : **{dmin} → {dmax}**"]

    if "flag_status" in d2.columns:
        n_lod = (d2["flag_status"] == "LOD").sum()
        n_loq = (d2["flag_status"] == "LOQ").sum()
        n_normal = (d2["flag_status"] == "Normal").sum()
        if n_lod > 0 or n_loq > 0:
            info_parts.append(f"(Normal: {n_normal}, <LOQ: {n_loq}, <LOD: {n_lod})")

    return " • ".join(info_parts)


def is_true_value(val) -> bool:
    """Vérifie si une valeur représente TRUE (bool, string, int)"""
    if pd.isna(val):
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val == 1
    s = str(val).strip().lower()
    return s in ("true", "1", "yes", "oui", "vrai")


# ----------------------
# DATA LOADERS
# ----------------------
@st.cache_data
def load_wbe(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except FileNotFoundError:
        return pd.DataFrame()
    df.columns = [c.strip().lower() for c in df.columns]
    if "date" not in df.columns:
        return pd.DataFrame()
    if np.issubdtype(df["date"].dtype, np.number):
        df["date"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df["date"], unit="D")
    else:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

    # Normaliser les colonnes flag (mélange TRUE/VRAI/Yes/No/FAUX dans Excel)
    # → force en string pour éviter le crash Arrow lors de st.dataframe
    for c in ["outlier", "inf_lod", "inf_loq"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df.dropna(subset=["date"]).copy()

@st.cache_data
def load_market(path: str) -> pd.DataFrame:
    try:
        dm = pd.read_excel(path)
    except Exception:
        return pd.DataFrame()
    dm.columns = [c.strip().lower() for c in dm.columns]
    if "date" in dm.columns:
        if np.issubdtype(dm["date"].dtype, np.number):
            dm["date"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(dm["date"], unit="D")
        else:
            dm["date"] = pd.to_datetime(dm["date"], errors="coerce", dayfirst=True)
    if "pureté" in dm.columns:
        dm["pureté"] = pd.to_numeric(dm["pureté"], errors="coerce")
    if "stup" in dm.columns:
        STUP_ALIASES = {
            "cocaine sel": "Cocaïne (Sel)", "cocaïne sel": "Cocaïne (Sel)",
            "cocaine base": "Cocaïne (Base)", "cocaïne base": "Cocaïne (Base)",
            "mdma pilule": "MDMA (pilule)", "mdma pillule": "MDMA (pilule)",
            "mdma cristal": "MDMA (cristaux)", "mdma cristaux": "MDMA (cristaux)",
        }

        def normalize_stup_label(x):
            if pd.isna(x):
                return x
            key = str(x).strip().lower()
            return STUP_ALIASES.get(key, x)

        dm["stup"] = dm["stup"].apply(normalize_stup_label)
    return dm.dropna(subset=["date"]).copy() if "date" in dm.columns else dm


# ----------------------
# TRAITEMENT DES DONNÉES WBE
# ----------------------
@st.cache_data
def process_wbe_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for c in ["rep_1", "rep_2", "rep_3", "vol_jour", "pop"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    rep_cols = [c for c in ["rep_1", "rep_2", "rep_3"] if c in df.columns]
    if rep_cols:
        df["conc_raw_ng_l"] = df[rep_cols].mean(axis=1, skipna=True)
    elif "conc_ng_l" in df.columns:
        df["conc_raw_ng_l"] = pd.to_numeric(df["conc_ng_l"], errors="coerce")
    else:
        df["conc_raw_ng_l"] = np.nan

    df["flag_status"] = "Normal"
    df["conc_final_ng_l"] = df["conc_raw_ng_l"].copy()

    if "inf_lod" in df.columns:
        mask_lod = df["inf_lod"].apply(is_true_value)
        df.loc[mask_lod, "conc_final_ng_l"] = LOD_REPLACEMENT_VALUE
        df.loc[mask_lod, "flag_status"] = "LOD"

    if "inf_loq" in df.columns:
        mask_loq = df["inf_loq"].apply(is_true_value) & (df["flag_status"] != "LOD")
        df.loc[mask_loq, "conc_final_ng_l"] = LOQ_REPLACEMENT_VALUE
        df.loc[mask_loq, "flag_status"] = "LOQ"

    df["is_outlier"] = False
    if "outlier" in df.columns:
        df["is_outlier"] = df["outlier"].apply(lambda x: is_true_value(x) or str(x).strip().lower() == "yes")

    df["charge_calc"] = np.nan
    if {"vol_jour", "pop"}.issubset(df.columns):
        df["charge_calc"] = df["conc_final_ng_l"] * df["vol_jour"] / df["pop"]

    df["y"] = df["charge_calc"].copy()
    df.loc[df["is_outlier"], "y"] = np.nan
    df["y_display"] = df["charge_calc"].copy()

    return df


# ----------------------
# PURETÉ TRIMESTRIELLE
# ----------------------
@st.cache_data
def build_quarterly_purity(df_mkt: pd.DataFrame,
                           selected_stup: str,
                           start_d: date,
                           end_d: date) -> pd.DataFrame:
    out_cols = ["quarter", "pur_median_q"]

    if df_mkt.empty or not {"date", "pureté", "stup"}.issubset(df_mkt.columns):
        return pd.DataFrame(columns=out_cols)

    dm = df_mkt.loc[
        (df_mkt["date"].dt.date >= start_d) & (df_mkt["date"].dt.date <= end_d),
        ["date", "pureté", "stup"]
    ].copy()

    if dm.empty:
        return pd.DataFrame(columns=out_cols)

    dm["quarter"] = dm["date"].dt.to_period("Q")
    dm["pureté"] = pd.to_numeric(dm["pureté"], errors="coerce").clip(0, 100)

    COC_BASE = "Cocaïne (Base)"
    COC_SEL = "Cocaïne (Sel)"
    MDMA_P = "MDMA (pilule)"
    MDMA_C = "MDMA (cristaux)"
    THC_CANN = "THC (Cannabis)"
    THC_RES = "THC (Résine)"
    HER_BASE = "Héroïne (Base)"

    ui = str(selected_stup).strip()
    if ui == "Cocaïne HCL":
        target = COC_SEL
    elif ui == "Crack":
        target = COC_BASE
    elif ui == "Héroïne":
        target = HER_BASE
    else:
        target = ui

    if target in {COC_BASE, COC_SEL}:
        MW_BASE = 303.35
        MW_HCL = 339.82
        SEL_TO_BASE = MW_BASE / MW_HCL
        BASE_TO_SEL = MW_HCL / MW_BASE

        sub = dm[dm["stup"].isin([COC_BASE, COC_SEL])].copy()
        if sub.empty:
            return pd.DataFrame(columns=out_cols)

        if target == COC_BASE:
            sub["purete_equiv"] = np.where(
                sub["stup"].eq(COC_SEL),
                sub["pureté"] * SEL_TO_BASE,
                sub["pureté"]
            )
        else:
            sub["purete_equiv"] = np.where(
                sub["stup"].eq(COC_BASE),
                sub["pureté"] * BASE_TO_SEL,
                sub["pureté"]
            )

        pur_q = (sub.groupby("quarter", as_index=False)["purete_equiv"]
                 .median()
                 .rename(columns={"purete_equiv": "pur_median_q"}))
        pur_q["pur_median_q"] = pur_q["pur_median_q"].clip(0, 100)
        return pur_q[out_cols]

    if target in {"MDMA", MDMA_P, MDMA_C}:
        sub = dm[dm["stup"].isin([MDMA_P, MDMA_C])].copy()
        if sub.empty:
            return pd.DataFrame(columns=out_cols)

        stats = (sub.groupby(["quarter", "stup"])["pureté"]
                 .agg(median="median", n="count").reset_index())
        pill = stats[stats["stup"].eq(MDMA_P)].rename(
            columns={"median": "median_pill", "n": "n_pill"}).drop(columns=["stup"])
        cryst = stats[stats["stup"].eq(MDMA_C)].rename(
            columns={"median": "median_cryst", "n": "n_cryst"}).drop(columns=["stup"])
        pur = pd.merge(pill, cryst, on="quarter", how="outer")
        pur["n_pill"] = pur["n_pill"].fillna(0)
        pur["n_cryst"] = pur["n_cryst"].fillna(0)

        def _weighted(row):
            n1, n2 = row.get("n_pill", 0), row.get("n_cryst", 0)
            m1, m2 = row.get("median_pill", np.nan), row.get("median_cryst", np.nan)
            if n1 > 0 and n2 > 0:
                return (n1 * m1 + n2 * m2) / (n1 + n2)
            if n1 > 0:
                return m1
            if n2 > 0:
                return m2
            return np.nan

        pur["pur_median_q"] = pur.apply(_weighted, axis=1).clip(0, 100)
        return pur[out_cols].dropna(subset=["pur_median_q"])

    if target in {"THC", THC_CANN, THC_RES}:
        sub = dm[dm["stup"].isin([THC_CANN, THC_RES])].copy()
        if sub.empty:
            return pd.DataFrame(columns=out_cols)

        stats = (sub.groupby(["quarter", "stup"])["pureté"]
                 .agg(median="median", n="count").reset_index())
        cann = stats[stats["stup"].eq(THC_CANN)].rename(
            columns={"median": "median_cann", "n": "n_cann"}).drop(columns=["stup"])
        resin = stats[stats["stup"].eq(THC_RES)].rename(
            columns={"median": "median_res", "n": "n_res"}).drop(columns=["stup"])
        pur = pd.merge(cann, resin, on="quarter", how="outer")
        pur["n_cann"] = pur["n_cann"].fillna(0)
        pur["n_res"] = pur["n_res"].fillna(0)

        def _weighted_thc(row):
            n1, n2 = row.get("n_cann", 0), row.get("n_res", 0)
            m1, m2 = row.get("median_cann", np.nan), row.get("median_res", np.nan)
            if n1 > 0 and n2 > 0:
                return (n1 * m1 + n2 * m2) / (n1 + n2)
            if n1 > 0:
                return m1
            if n2 > 0:
                return m2
            return np.nan

        pur["pur_median_q"] = pur.apply(_weighted_thc, axis=1).clip(0, 100)
        return pur[out_cols].dropna(subset=["pur_median_q"])

    sub = dm[dm["stup"].eq(target)].copy()
    if sub.empty:
        return pd.DataFrame(columns=out_cols)
    pur_q = (sub.groupby("quarter", as_index=False)["pureté"]
             .median()
             .rename(columns={"pureté": "pur_median_q"}))
    pur_q["pur_median_q"] = pur_q["pur_median_q"].clip(0, 100)
    return pur_q[out_cols]


# ----------------------
# GEO / MAP FUNCTIONS
# ----------------------
def _pick_geo_columns(df: pd.DataFrame):
    """Détecte des colonnes lat/lon si elles existent dans les données."""
    if df is None or df.empty:
        return None, None
    cols = [c.lower() for c in df.columns]
    lat_candidates = ["lat", "latitude", "y_lat", "lat_wgs84"]
    lon_candidates = ["lon", "lng", "long", "longitude", "x_lon", "lon_wgs84"]
    lat_col = next((c for c in lat_candidates if c in cols), None)
    lon_col = next((c for c in lon_candidates if c in cols), None)
    return lat_col, lon_col


def _city_latlon_from_dict(city: str):
    """Retourne (lat, lon) depuis CITY_COORDS.

    Tolère des variantes de nom (parenthèses, tirets, suffixes).
    Ex: "Zurich - Werdhölzli" -> "Zurich".
    """
    if city is None:
        return None

    city_raw = str(city)
    city_clean = re.sub(r"\(.*?\)|\[.*?\]", "", city_raw).strip()
    city_clean = re.split(r"\s*[-–—/,|]\s*", city_clean)[0].strip()

    key = _norm(city_clean)
    if not key:
        return None

    if key in CITY_COORDS:
        return CITY_COORDS[key]

    first = key.split()[0]
    if first in CITY_COORDS:
        return CITY_COORDS[first]

    best_ll = None
    best_len = 0
    for k, ll in CITY_COORDS.items():
        if k and (k in key or key in k):
            if len(k) > best_len:
                best_ll = ll
                best_len = len(k)
    return best_ll


@st.cache_data
def build_city_bubble_df(df_sub: pd.DataFrame, value_col: str = "y") -> pd.DataFrame:
    """Agrège par ville: médiane(value), médiane(pop), n_points + coords."""
    if df_sub.empty or "ville" not in df_sub.columns:
        return pd.DataFrame()

    d = df_sub.copy()
    d[value_col] = pd.to_numeric(d.get(value_col), errors="coerce")

    agg = (d.dropna(subset=[value_col, "ville"])
    .groupby("ville", as_index=False)
    .agg(
        value_median=(value_col, "median"),
        pop_median=("pop", "median"),
        n_points=(value_col, "count")
    ))

    agg["pop_median"] = pd.to_numeric(agg.get("pop_median"), errors="coerce").fillna(50000.0)

    if agg.empty:
        return pd.DataFrame()

    lat_col, lon_col = _pick_geo_columns(d)
    if lat_col and lon_col:
        geo = (d.dropna(subset=[lat_col, lon_col, "ville"])
               .groupby("ville", as_index=False)
               .agg(lat=(lat_col, "median"), lon=(lon_col, "median")))
        agg = agg.merge(geo, on="ville", how="left")

        agg["lat"] = pd.to_numeric(agg.get("lat"), errors="coerce")
        agg["lon"] = pd.to_numeric(agg.get("lon"), errors="coerce")

        bad_wgs84 = (agg["lat"].abs() > 90) | (agg["lon"].abs() > 180)
        agg.loc[bad_wgs84, ["lat", "lon"]] = np.nan

        bad_ch = (agg["lat"] < 44.5) | (agg["lat"] > 48.9) | (agg["lon"] < 5.0) | (agg["lon"] > 11.9)
        agg.loc[bad_ch, ["lat", "lon"]] = np.nan
    else:
        agg["lat"] = np.nan
        agg["lon"] = np.nan

    # Fallback vers dictionnaire de coordonnées
    for i, row in agg.iterrows():
        if pd.isna(row["lat"]) or pd.isna(row["lon"]):
            ll = _city_latlon_from_dict(row["ville"])
            if ll:
                agg.at[i, "lat"] = ll[0]
                agg.at[i, "lon"] = ll[1]

    agg["lat"] = pd.to_numeric(agg.get("lat"), errors="coerce")
    agg["lon"] = pd.to_numeric(agg.get("lon"), errors="coerce")

    # Retirer les villes sans coords
    agg = agg.dropna(subset=["lat", "lon"]).copy()

    return agg


@st.cache_data(ttl=3600)
def _fetch_cantons_geojson():
    """Télécharge et cache le GeoJSON des cantons suisses."""
    CANTONS_GEOJSON_URL = "https://raw.githubusercontent.com/greymass/countrydata/master/data/switzerland/cantons.geojson"
    CANTONS_GEOJSON_URL_ALT = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/switzerland-cantons.geojson"
    try:
        response = requests.get(CANTONS_GEOJSON_URL, timeout=5)
        if response.status_code != 200:
            response = requests.get(CANTONS_GEOJSON_URL_ALT, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def render_city_bubble_map_concentration(df_sub: pd.DataFrame,
                                         value_col: str = "y",
                                         title: str = "Carte — charges médianes",
                                         units: str = "mg/j/1000 hab.",
                                         key: Optional[str] = None,
                                         basemap_style: str = "carto-positron",
                                         zoom: float = 7.2,
                                         height: int = 520) -> None:
    """
    Carte des villes avec Plotly Maplibre (rapide, sans st_folium).
    - Taille des cercles ∝ population (racine carrée pour perception aire)
    - Couleur des cercles = concentration médiane
    - Frontières cantonales suisses superposées (GeoJSON)
    """
    city_df = build_city_bubble_df(df_sub, value_col=value_col)

    if city_df.empty:
        if "ville" in df_sub.columns:
            missing = df_sub["ville"].dropna().unique().tolist()
            st.warning(f"⚠️ Pas de coordonnées géographiques pour : {', '.join(missing)}")
        else:
            st.info("Pas assez d'informations géographiques pour afficher la carte.")
        return

    city_df["value_median"] = pd.to_numeric(city_df["value_median"], errors="coerce")
    city_df = city_df.dropna(subset=["value_median"])
    if city_df.empty:
        st.warning("⚠️ Aucune valeur médiane valide pour afficher la carte.")
        return

    # Échelle de couleur (concentration)
    val_min = float(city_df["value_median"].min())
    val_max = float(city_df["value_median"].max())
    if val_min == val_max:
        margin = max(abs(val_min) * 0.1, 1.0)
        val_min -= margin
        val_max += margin

    # Taille des cercles ∝ √population, sur une échelle ABSOLUE 10k → 500k habitants
    # (cohérence visuelle d'une vue à l'autre : Bulle a toujours la même taille
    #  qu'on la regarde seule ou avec Genève)
    POP_MIN_REF = 10_000
    POP_MAX_REF = 500_000
    SIZE_MIN_PX = 14
    SIZE_MAX_PX = 52

    pop_clipped = pd.to_numeric(city_df["pop_median"], errors="coerce").fillna(POP_MIN_REF)
    pop_clipped = pop_clipped.clip(lower=POP_MIN_REF, upper=POP_MAX_REF)
    normalized = (pop_clipped - POP_MIN_REF) / (POP_MAX_REF - POP_MIN_REF)
    city_df["marker_size"] = SIZE_MIN_PX + (normalized ** 0.5) * (SIZE_MAX_PX - SIZE_MIN_PX)

    # Couches custom : frontières cantonales
    cantons_geojson = _fetch_cantons_geojson()
    map_layers = []
    if cantons_geojson:
        map_layers.append({
            "sourcetype": "geojson",
            "source": cantons_geojson,
            "type": "line",
            "color": "rgba(85, 85, 85, 0.55)",
            "line": {"width": 1.0},
            "below": "traces",
        })

    # Auto-zoom selon la composition des villes affichées :
    # - 1 seule ville → zoom serré
    # - toutes romandes ou neutres (Bern) → cadrage Romandie élargie
    # - au moins une alémanique → cadrage Suisse entière
    lats = city_df["lat"].tolist()
    lons = city_df["lon"].tolist()

    if len(city_df) == 1:
        center_lat = lats[0]
        center_lon = lons[0]
        auto_zoom = 9.0
    else:
        villes_norm = {_norm(v) for v in city_df["ville"]}
        only_romande_or_neutral = villes_norm.issubset(ROMANDE_CITIES | NEUTRAL_CITIES)

        if only_romande_or_neutral:
            # Cadrage Romandie élargie (Jura au nord + Berne à l'est visibles)
            center_lat = 46.85
            center_lon = 6.8
            auto_zoom = 7.1
        else:
            # Au moins une ville alémanique → cadrage Suisse entière
            center_lat = 46.8
            center_lon = 8.2
            auto_zoom = 6.2

    fig = go.Figure(go.Scattermapbox(
        lat=city_df["lat"].tolist(),
        lon=city_df["lon"].tolist(),
        mode="markers+text",
        marker=dict(
            size=city_df["marker_size"].tolist(),
            color=city_df["value_median"].tolist(),
            colorscale=CONCENTRATION_COLORSCALE,
            cmin=val_min,
            cmax=val_max,
            opacity=0.88,
            colorbar=dict(
                title=dict(text=f"Charge<br>({units})", font=dict(size=11)),
                thickness=14,
                len=0.45,  # raccourcie (avant : 0.65)
                x=1.02,
                y=0.78,  # ancrée vers le haut de la carte
                yanchor="middle",
                tickfont=dict(size=10),
            ),
        ),
        text=city_df["ville"].tolist(),
        textposition="bottom right",
        textfont=dict(size=11, color="#1a1a1a"),
        customdata=city_df[["pop_median", "n_points"]].values,
        hovertemplate=(
            "<b>%{text}</b><br>"
            f"Charge médiane : %{{marker.color:.1f}} {units}<br>"
            "Population : %{customdata[0]:,.0f} hab.<br>"
            "Points : %{customdata[1]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        height=height,
        margin=dict(l=0, r=10, t=40, b=0),
        mapbox=dict(
            style=basemap_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=auto_zoom,
            layers=map_layers,
        ),
    )

    # Wrapper relatif + carte, pour permettre le positionnement absolu de la légende
    st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
    st.plotly_chart(fig, width="stretch", key=key)

    # Légende des tailles de population, superposée en bas à droite
    # (échelle absolue 10k → 500k, indépendante de la sélection courante)
    legend_html = """
        <div class="map-pop-legend">
            <div class="map-pop-legend-title">Population (hab.)</div>
            <div class="map-pop-legend-row"><span class="map-pop-circle s-500k"></span><span>500 000</span></div>
            <div class="map-pop-legend-row"><span class="map-pop-circle s-250k"></span><span>250 000</span></div>
            <div class="map-pop-legend-row"><span class="map-pop-circle s-100k"></span><span>100 000</span></div>
            <div class="map-pop-legend-row"><span class="map-pop-circle s-50k"></span><span>50 000</span></div>
            <div class="map-pop-legend-row"><span class="map-pop-circle s-10k"></span><span>10 000</span></div>
        </div>
        </div>
        """
    st.markdown(legend_html, unsafe_allow_html=True)
# ----------------------
# CHART FUNCTIONS
# ----------------------
def _figure_color_map(fig) -> dict:
    cmap = {}
    for tr in fig.data:
        lg = getattr(tr, "legendgroup", None)
        col = tr.line.color if hasattr(tr, "line") and tr.line and tr.line.color else None
        if lg and col and lg not in cmap:
            cmap[lg] = col
    return cmap


def _add_trendlines(fig, data, y_col, color_col, dash_col=None):
    if data.empty or y_col not in data.columns:
        return pd.DataFrame()
    color_map = _figure_color_map(fig)
    group_cols = [color_col] if color_col else []
    if dash_col:
        group_cols.append(dash_col)
    rows = []
    for keys, dsub in data.dropna(subset=[y_col, "date"]).groupby(group_cols):
        if len(dsub) < 2:
            continue
        xnum = dsub["date"].dt.date.map(_dt.date.toordinal).astype(float).to_numpy()
        ynum = pd.to_numeric(dsub[y_col], errors="coerce").to_numpy()
        mask = np.isfinite(xnum) & np.isfinite(ynum)
        xnum, ynum = xnum[mask], ynum[mask]
        if xnum.size < 2:
            continue
        slope, intercept = np.polyfit(xnum, ynum, 1)
        x0, x1 = xnum.min(), xnum.max()
        y0, y1 = slope * x0 + intercept, slope * x1 + intercept
        d0 = pd.to_datetime([_dt.date.fromordinal(int(x0))])[0]
        d1 = pd.to_datetime([_dt.date.fromordinal(int(x1))])[0]
        main_key = keys[0] if isinstance(keys, tuple) else keys
        slope_per_year = slope * 365.25
        name = f"{main_key} — tendance ({slope_per_year:+.1f}/an)"
        line_color = color_map.get(str(main_key))
        fig.add_trace(go.Scatter(
            x=[d0, d1], y=[y0, y1],
            mode="lines",
            name=name, legendgroup=str(main_key),
            line=dict(width=2.5, dash="dash", color=line_color),
            hoverinfo="skip", showlegend=True,
        ))
        med = float(np.nanmedian(ynum)) if np.isfinite(ynum).any() else np.nan
        rel_pct = (slope_per_year / med * 100.0) if med and np.isfinite(med) else np.nan
        rows.append({color_col: main_key, "pente_an": slope_per_year, "pente_rel_%/an": rel_pct, "n_points": len(dsub)})
    return pd.DataFrame(rows)


def _adapt_xaxis(fig, series_dates):
    if series_dates.notna().any():
        xmin, xmax = pd.to_datetime(series_dates.min()), pd.to_datetime(series_dates.max())
        if pd.notna(xmin) and pd.notna(xmax) and xmin < xmax:
            fig.update_xaxes(type="date", range=[xmin, xmax])


# ----------------------
# RENDER FUNCTIONS
# ----------------------
def render_stup_panel_header(stup_name: str, n_points: int):
    desc = STUP_DESCRIPTIONS.get(stup_name, {})
    description = desc.get("description", "Aucune description disponible.")
    parent = desc.get("parent", "Non spécifié")
    metabolites = desc.get("metabolites", "Non spécifié")
    note = desc.get("note", "")

    st.markdown(f"""
    <div class="stup-panel">
        <div class="stup-panel-header">
            <span class="stup-panel-title">🧪 {stup_name}</span>
            <span class="stup-panel-badge">{n_points} points</span>
        </div>
        <div class="stup-description">{description}</div>
        <div class="stup-analytes">
            <strong>Parent :</strong> {parent}<br>
            <strong>Métabolites :</strong> {metabolites}
            {f'<br><em>💡 {note}</em>' if note else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_analyte_checkboxes(parents, metabs, key_prefix=""):
    selected_parents = []
    selected_metabs = []

    col1, col2 = st.columns(2)

    with col1:
        if parents:
            st.markdown("**Parents**")
            for a in parents:
                k = f"{key_prefix}par_{a}"
                if k not in st.session_state:
                    st.session_state[k] = True
                if st.checkbox(a, key=k):
                    selected_parents.append(a)

    with col2:
        if metabs:
            st.markdown("**Métabolites**")
            for a in metabs:
                k = f"{key_prefix}met_{a}"
                if k not in st.session_state:
                    st.session_state[k] = True
                if st.checkbox(a, key=k):
                    selected_metabs.append(a)

    return selected_parents, selected_metabs


def render_data_legend():
    st.markdown("""
    <div class="flag-legend">
        <strong>Légende des données :</strong>
        <span>🟢 Normal</span>
        <span class="flag-loq">🟠 <LOQ (5 ng/L)</span>
        <span class="flag-lod">🔴 <LOD (0 ng/L)</span>
        <span class="flag-outlier">⚫ Outlier (exclu)</span>
    </div>
    """, unsafe_allow_html=True)


def render_detailed_data_table(df_view: pd.DataFrame, key_prefix: str = ""):
    if df_view.empty:
        st.info("Aucune donnée à afficher.")
        return

    display_cols = []

    base_cols = ["date", "ville", "composes"]
    for c in base_cols:
        if c in df_view.columns:
            display_cols.append(c)

    rep_cols = [c for c in ["rep_1", "rep_2", "rep_3"] if c in df_view.columns]
    display_cols.extend(rep_cols)

    flag_cols = ["inf_lod", "inf_loq", "outlier"]
    for c in flag_cols:
        if c in df_view.columns:
            display_cols.append(c)

    calc_cols = ["conc_raw_ng_l", "flag_status", "conc_final_ng_l", "vol_jour", "pop", "charge_calc", "y", "is_outlier"]
    for c in calc_cols:
        if c in df_view.columns:
            display_cols.append(c)

    norm_cols = ["quarter", "pur_median_q", "y_norm"]
    for c in norm_cols:
        if c in df_view.columns:
            display_cols.append(c)

    display_cols = list(dict.fromkeys(display_cols))
    display_cols = [c for c in display_cols if c in df_view.columns]

    df_display = df_view[display_cols].copy()

    if "date" in df_display.columns:
        df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%Y-%m-%d")

    numeric_cols = df_display.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col in ["pop", "vol_jour"]:
            df_display[col] = df_display[col].round(0)
        else:
            df_display[col] = df_display[col].round(3)

    col_rename = {
        "conc_raw_ng_l": "Conc. brute (ng/L)",
        "conc_final_ng_l": "Conc. finale (ng/L)",
        "charge_calc": "Charge calc (mg/j/1000)",
        "y": "Y (stats)",
        "flag_status": "Flag",
        "is_outlier": "Outlier?",
        "vol_jour": "Vol. jour (m³)",
        "pop": "Population",
        "inf_lod": "<LOD",
        "inf_loq": "<LOQ",
        "pur_median_q": "Pureté Q (%)",
        "y_norm": "Y normalisé"
    }
    df_display = df_display.rename(columns={k: v for k, v in col_rename.items() if k in df_display.columns})

    st.dataframe(
        df_display.sort_values(by=[c for c in ["ville", "composes", "date"] if c in df_display.columns]),
        width='stretch',
        hide_index=True
    )


def render_timeseries_chart(df_view, show_trend, normalize, df_mkt, start_d, end_d,
                            stup_name, key_prefix="", is_comparison=False):
    if df_view.empty:
        st.info("Aucune donnée à afficher pour ce stupéfiant.")
        return

    global CITY_COLOR_MAP

    n_cities = df_view["ville"].nunique() if "ville" in df_view.columns else 0
    n_analytes = df_view["composes"].nunique()

    if is_comparison and n_cities > 1:
        color_col = "ville"
        dash_col = "composes" if n_analytes >= 2 else None
        COLOR_MAP = CITY_COLOR_MAP
    else:
        color_col = "composes"
        dash_col = None
        cats_all = sorted(df_view[color_col].dropna().unique()) if color_col in df_view.columns else []
        COLOR_MAP = {cat: COLOR_SEQ[i % len(COLOR_SEQ)] for i, cat in enumerate(cats_all)}

    cats_all = sorted(df_view[color_col].dropna().unique()) if color_col in df_view.columns else []
    CATEGORY_ORDERS = {color_col: cats_all}

    render_data_legend()

    fig1 = px.line(
        df_view.sort_values("date"),
        x="date", y="y",
        color=color_col, line_dash=dash_col, markers=True,
        color_discrete_map=COLOR_MAP, category_orders=CATEGORY_ORDERS,
        labels={"y": "Charge (mg/j/1000 hab.)", "composes": "Analyte", "ville": "Ville", "date": "Date"},
    )
    for tr in fig1.data:
        tr.line.width = 2
        tr.marker.size = 6
    fig1.update_traces(connectgaps=True)
    _adapt_xaxis(fig1, df_view["date"])
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"),
        hovermode="x unified",
        height=400,
    )
    style_legend(fig1)

    if show_trend:
        _add_trendlines(fig1, df_view, y_col="y", color_col=color_col, dash_col=dash_col)

    st.plotly_chart(fig1, width='stretch', key=f"{key_prefix}chart_raw")
    st.markdown(f'<div class="chart-footnote">{figure_footnote(df_view, "y")}</div>', unsafe_allow_html=True)

    if normalize:
        df_norm = df_view.copy()
        df_norm["quarter"] = df_norm["date"].dt.to_period("Q")
        pur_q = build_quarterly_purity(df_mkt, stup_name, start_d, end_d)

        if pur_q.empty:
            st.warning("⚠️ Aucune donnée de pureté disponible pour ce stupéfiant.")
        else:
            df_norm = df_norm.merge(pur_q, on="quarter", how="left")
            df_norm["y_norm"] = np.where(
                df_norm["pur_median_q"].notna() & (df_norm["pur_median_q"] > 0),
                df_norm["y"] / (df_norm["pur_median_q"] / 100.0),
                np.nan
            )

            df_norm_plot = df_norm.dropna(subset=["y_norm"]).copy()

            if df_norm_plot.empty:
                st.warning("⚠️ Pas de données après normalisation (pureté manquante pour ces trimestres).")
            else:
                col1, col2 = st.columns([2.5, 1.5])

                with col1:
                    st.markdown("**⚖️ Charges normalisées par la pureté**")
                    fig2 = px.line(
                        df_norm_plot.sort_values("date"),
                        x="date", y="y_norm",
                        color=color_col, line_dash=dash_col, markers=True,
                        color_discrete_map=COLOR_MAP, category_orders=CATEGORY_ORDERS,
                    )
                    for tr in fig2.data:
                        tr.line.width = 2
                        tr.marker.size = 6
                    fig2.update_traces(connectgaps=True)
                    _adapt_xaxis(fig2, df_norm_plot["date"])
                    fig2.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        height=350,
                    )
                    style_legend(fig2)

                    if show_trend and not df_norm_plot.empty:
                        _add_trendlines(fig2, df_norm_plot, y_col="y_norm", color_col=color_col, dash_col=dash_col)

                    st.plotly_chart(fig2, width='stretch', key=f"{key_prefix}chart_norm")

                with col2:
                    st.markdown("**📉 Pureté trimestrielle utilisée**")
                    pur_q_plot = pur_q.sort_values("quarter").copy()
                    pur_q_plot["date_mid"] = pur_q_plot["quarter"].dt.to_timestamp(how="end") - pd.offsets.Day(45)

                    fig3 = px.line(pur_q_plot, x="date_mid", y="pur_median_q", markers=True)
                    fig3.update_traces(line_color="#e63946", line_width=2, marker_size=8)
                    fig3.update_yaxes(range=[0, 100])
                    fig3.update_layout(
                        plot_bgcolor="white", height=300,
                        margin=dict(l=20, r=20, t=20, b=40)
                    )
                    st.plotly_chart(fig3, width='stretch', key=f"{key_prefix}chart_purity")

                    if stup_name in {"MDMA", "THC"}:
                        st.caption(
                            f"ℹ️ La pureté trimestrielle pour {stup_name} est une moyenne pondérée "
                            "des différentes formes disponibles sur le marché."
                        )

                with st.expander("📋 Données détaillées (avec normalisation)"):
                    render_detailed_data_table(df_norm, key_prefix=f"{key_prefix}norm_")
                return

    with st.expander("📋 Données détaillées"):
        render_detailed_data_table(df_view, key_prefix=key_prefix)


def render_comparison_with_map(df_view, stup_name, key_prefix=""):
    """
    Affiche la comparaison avec CARTE (couleur = concentration) côte à côte avec boxplot.
    """
    if df_view.empty:
        st.info("Aucune donnée à afficher.")
        return

    if "ville" not in df_view.columns or df_view["ville"].nunique() < 2:
        st.info("Au moins 2 villes sont nécessaires pour la comparaison.")
        return

    global CITY_COLOR_MAP

    render_data_legend()

    analytes = sorted(df_view["composes"].dropna().unique())

    def _compute_zoom_ymax(yvals: pd.Series) -> float:
        y = pd.to_numeric(yvals, errors="coerce").dropna()
        if y.empty:
            return 1.0
        y_np = y.to_numpy()
        q1, q3 = np.percentile(y_np, [25, 75])
        iqr = q3 - q1
        if iqr == 0:
            ymax = float(y.max())
            return ymax * 1.15 if ymax > 0 else 1.0
        upper_fence = q3 + 1.5 * iqr
        non_out = y[y <= upper_fence]
        whisker_max = float(non_out.max()) if not non_out.empty else float(y.max())
        outlier_max = float(y.max())
        if outlier_max > 1.8 * whisker_max and whisker_max > 0:
            ymax = whisker_max * 1.15
        else:
            ymax = outlier_max * 1.08
        return max(ymax, 1.0)

    for analyte in analytes:
        sub = df_view[df_view["composes"] == analyte].copy()
        sub["y"] = pd.to_numeric(sub["y"], errors="coerce")
        sub = sub.dropna(subset=["y", "ville"])
        if sub.empty:
            continue

        medians = sub.groupby("ville")["y"].median().sort_values(ascending=False)
        ville_order = list(medians.index)
        y_max_zoom = _compute_zoom_ymax(sub["y"])

        st.markdown(f"##### Analyte : {analyte}")

        col_map, col_box = st.columns([1, 1.3], gap="large")

        with col_map:
            st.markdown("**🗺️ Carte — couleur = concentration médiane**")
            render_city_bubble_map_concentration(
                sub,
                value_col="y",
                title=f"Charges médianes — {analyte}",
                units="mg/j/1000 hab.",
                basemap_style="carto-positron",
                zoom=6.2,
                height=480,
                key=f"{key_prefix}map_{analyte}",
            )

        with col_box:
            st.markdown("**📊 Boxplots — couleur = charge (médiane par ville)**")

            vmin = float(medians.min())
            vmax = float(medians.max())
            if vmax == vmin:
                vmax = vmin + 1e-9

            def _rgba_from_scale(v: float, alpha: float) -> str:
                if pd.isna(v):
                    return f"rgba(160,160,160,{alpha})"
                t = (float(v) - vmin) / (vmax - vmin)
                t = max(0.0, min(1.0, t))
                c = pc.sample_colorscale(CONCENTRATION_COLORSCALE, [t])[0]
                if isinstance(c, str) and c.startswith('#'):
                    hx = c.lstrip('#')
                    r = int(hx[0:2], 16);
                    g = int(hx[2:4], 16);
                    b = int(hx[4:6], 16)
                    return f"rgba({r},{g},{b},{alpha})"
                nums = str(c).strip('rgb()').split(',')
                r, g, b = [int(float(x)) for x in nums]
                return f"rgba({r},{g},{b},{alpha})"

            fig = go.Figure()

            for ville in ville_order:
                sub_ville = sub[sub['ville'] == ville]
                v_med = float(medians.loc[ville])
                fill = _rgba_from_scale(v_med, alpha=0.28)
                line = _rgba_from_scale(v_med, alpha=1.0)
                pts = _rgba_from_scale(v_med, alpha=0.55)

                fig.add_trace(go.Box(
                    x=[ville] * len(sub_ville),
                    y=sub_ville['y'],
                    name=ville,
                    fillcolor=fill,
                    line=dict(color=line, width=1.8),
                    marker=dict(color=pts),
                    boxmean=False,
                    showlegend=False,
                    boxpoints='outliers'
                ))

                fig.add_trace(go.Scatter(
                    x=[ville] * len(sub_ville),
                    y=sub_ville['y'],
                    mode='markers',
                    marker=dict(color=pts, size=5, opacity=0.35),
                    hovertemplate=(
                        'Ville: %{x}<br>'
                        'Charge: %{y:.2f} mg/j/1000 hab<br>'
                        '<extra></extra>'
                    ),
                    showlegend=False
                ))

            fig.update_layout(
                title=f"Comparaison — {analyte}",
                xaxis_title="Ville",
                yaxis_title="Charge (mg/jour/1000 habitants)",
                xaxis=dict(categoryorder="array", categoryarray=ville_order, tickangle=-45),
                height=480,
                plot_bgcolor="white",
                margin=dict(l=60, r=30, t=60, b=80),
            )
            fig.update_yaxes(range=[0, y_max_zoom], gridcolor="#f0f0f0", zerolinecolor="#e0e0e0")

            st.plotly_chart(fig, width='stretch', key=f"{key_prefix}boxplot_{analyte}")

        st.markdown("---")

    with st.expander("📋 Données détaillées"):
        render_detailed_data_table(df_view, key_prefix=f"{key_prefix}map_")


def render_comparison_boxplot_only(df_view, stup_name, key_prefix=""):
    """
    Affiche UNIQUEMENT les boxplots avec couleur fixe par ville (sans carte).
    """
    if df_view.empty:
        st.info("Aucune donnée à afficher.")
        return

    if "ville" not in df_view.columns or df_view["ville"].nunique() < 2:
        st.info("Au moins 2 villes sont nécessaires pour la comparaison.")
        return

    global CITY_COLOR_MAP

    render_data_legend()

    analytes = sorted(df_view["composes"].dropna().unique())

    def _compute_zoom_ymax(yvals: pd.Series) -> float:
        y = pd.to_numeric(yvals, errors="coerce").dropna()
        if y.empty:
            return 1.0
        y_np = y.to_numpy()
        q1, q3 = np.percentile(y_np, [25, 75])
        iqr = q3 - q1
        if iqr == 0:
            ymax = float(y.max())
            return ymax * 1.15 if ymax > 0 else 1.0
        upper_fence = q3 + 1.5 * iqr
        non_out = y[y <= upper_fence]
        whisker_max = float(non_out.max()) if not non_out.empty else float(y.max())
        outlier_max = float(y.max())
        if outlier_max > 1.8 * whisker_max and whisker_max > 0:
            ymax = whisker_max * 1.15
        else:
            ymax = outlier_max * 1.08
        return max(ymax, 1.0)

    for analyte in analytes:
        sub = df_view[df_view["composes"] == analyte].copy()
        sub["y"] = pd.to_numeric(sub["y"], errors="coerce")
        sub = sub.dropna(subset=["y", "ville"])
        if sub.empty:
            continue

        medians = sub.groupby("ville")["y"].median().sort_values(ascending=False)
        ville_order = list(medians.index)
        y_max_zoom = _compute_zoom_ymax(sub["y"])

        fig = go.Figure()

        for ville in ville_order:
            sub_ville = sub[sub["ville"] == ville]
            ville_color = CITY_COLOR_MAP.get(ville, COLOR_SEQ[0])

            fig.add_trace(go.Box(
                x=[ville] * len(sub_ville),
                y=sub_ville["y"],
                name=ville,
                marker_color=ville_color,
                boxmean=False,
                showlegend=False,
                boxpoints="outliers"
            ))

            fig.add_trace(go.Scatter(
                x=[ville] * len(sub_ville),
                y=sub_ville["y"],
                mode="markers",
                name=f"Points {ville}",
                marker=dict(
                    color=ville_color,
                    size=5,
                    opacity=0.5
                ),
                hovertemplate=(
                    "Ville: %{x}<br>"
                    "Charge: %{y:.2f} mg/j/1000 hab<br>"
                    "<extra></extra>"
                ),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Comparaison par ville — {analyte}",
            xaxis_title="Ville",
            yaxis_title="Charge (mg/jour/1000 habitants)",
            xaxis=dict(categoryorder="array", categoryarray=ville_order, tickangle=-45),
            height=650,
            plot_bgcolor="white",
            margin=dict(l=60, r=30, t=60, b=80),
        )
        fig.update_yaxes(range=[0, y_max_zoom], gridcolor="#f0f0f0", zerolinecolor="#e0e0e0")

        st.plotly_chart(fig, width='stretch', key=f"{key_prefix}boxplot_{analyte}")

    with st.expander("📋 Données détaillées"):
        render_detailed_data_table(df_view, key_prefix=f"{key_prefix}boxplot_")


# ----------------------
# LOAD DATA
# ----------------------
df_wbe = load_wbe(WBE_PATH)
df_mkt = load_market(SEIZURE_PATH)

if df_wbe.empty:
    st.error("⚠️ Aucune donnée WBE chargée. Vérifiez le fichier.")
    st.stop()

if "ville" in df_wbe.columns:
    CITY_COLOR_MAP = build_city_color_map(df_wbe, COLOR_SEQ)

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.markdown("## ⚙️ Filtres")

    with st.expander("📁 **Projets**", expanded=True):
        if "projet" in df_wbe.columns:
            all_projects = sorted([p for p in df_wbe["projet"].dropna().astype(str).unique() if p.upper() != "SCORE"])
            selected_projects = []
            for p in all_projects:
                k = f"proj_{p}"
                if k not in st.session_state:
                    st.session_state[k] = True
                if st.checkbox(p, key=k):
                    selected_projects.append(p)
            if not selected_projects:
                st.warning("Sélectionnez au moins un projet")
                st.stop()
        else:
            selected_projects = []

    st.markdown("### 📅 Période")
    min_d, max_d = df_wbe["date"].min().date(), df_wbe["date"].max().date()
    period = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")
    start_d, end_d = period if isinstance(period, tuple) and len(period) == 2 else (min_d, max_d)

    st.markdown("---")

    st.markdown("### 🔧 Options d'affichage")
    show_trend = st.checkbox("📈 Afficher tendances", key="show_trend")
    normalize = st.checkbox("⚖️ Normaliser par pureté", key="normalize")

    st.markdown("---")

    st.markdown("### ℹ️ Traitement des données")
    st.markdown(f"""
    - **<LOD** : remplacé par {LOD_REPLACEMENT_VALUE} ng/L
    - **<LOQ** : remplacé par {LOQ_REPLACEMENT_VALUE} ng/L
    - **Outliers** : exclus des statistiques
    """)

# ----------------------
# DATA PREPARATION (CACHED)
# ----------------------
@st.cache_data
def prepare_filtered_data(df_input: pd.DataFrame, start_d, end_d) -> pd.DataFrame:
    """Traite et filtre les données WBE - résultat mis en cache."""
    df_proc = process_wbe_data(df_input)
    mask = (df_proc["date"].dt.date >= start_d) & (df_proc["date"].dt.date <= end_d)
    df_out = df_proc.loc[mask].copy()
    df_out["date_day"] = df_out["date"].dt.floor("D")
    df_out["_is_spe"] = df_out["technique"].astype(str).str.upper().str.contains("SPE", na=False).astype(
        int) if "technique" in df_out.columns else 0
    df_out["composes"] = df_out["composes"].astype(str)
    grp_cols = ["date_day", "composes"] + (["ville"] if "ville" in df_out.columns else [])
    df_out = df_out.sort_values(["_is_spe", "y"], ascending=[False, False]).groupby(grp_cols, as_index=False).first()
    df_out["date"] = df_out["date_day"]
    df_out.drop(columns=["date_day", "_is_spe"], inplace=True, errors="ignore")
    return df_out

df_proj = df_wbe.copy()
if selected_projects:
    df_proj = df_proj[df_proj["projet"].astype(str).isin(selected_projects)]
if "pays" not in df_proj.columns:
    df_proj["pays"] = "\u2014"

df_base = prepare_filtered_data(df_proj, start_d, end_d)

all_available_cities = sorted(df_base["ville"].dropna().unique()) if "ville" in df_base.columns else []

if not all_available_cities:
    st.warning("Aucune ville disponible dans les données filtrées.")
    st.stop()


def get_available_stups(df):
    available_composes = set(df["composes"].dropna().unique())
    available_stups = []
    for stup, analytes in RELATED_ANALYTES.items():
        if any(a in available_composes for a in analytes):
            available_stups.append(stup)
    return sorted(available_stups)


# ----------------------
# HEADER
# ----------------------
st.markdown("""
<div class="main-header">
    <h1>🧪 WBE — Analyse des tendances temporelles</h1>
    <p>Wastewater-Based Epidemiology • Suivi des charges journalières normalisées</p>
</div>
""", unsafe_allow_html=True)

with st.expander("🎨 Couleurs attribuées aux villes"):
    cols = st.columns(min(len(CITY_COLOR_MAP), 5))
    for i, (city, color) in enumerate(CITY_COLOR_MAP.items()):
        with cols[i % len(cols)]:
            st.markdown(f'<span style="color:{color}; font-weight:bold;">● {city}</span>', unsafe_allow_html=True)

# ----------------------
# TABS - Villes
# ----------------------
tab_names = ["🌍 Toutes les villes"] + [f"📍 {city}" for city in all_available_cities]
tabs = st.tabs(tab_names)

# ----------------------
# TAB: Toutes les villes (Comparaison)
# ----------------------
with tabs[0]:
    st.markdown("""
    <div class="comparison-banner">
        <span>📊</span>
        <strong>Mode comparaison — Vue multi-villes</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🏙️ Sélectionner les villes à comparer")
    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("✓ Toutes", key="select_all_cities"):
            for city in all_available_cities:
                st.session_state[f"compare_city_{city}"] = True
    with col_btn2:
        if st.button("✗ Aucune", key="deselect_all_cities"):
            for city in all_available_cities:
                st.session_state[f"compare_city_{city}"] = False

    n_cols_cities = min(len(all_available_cities), 5)
    city_cols = st.columns(n_cols_cities)
    cities_to_compare = []
    for i, city in enumerate(all_available_cities):
        key = f"compare_city_{city}"
        if key not in st.session_state:
            st.session_state[key] = True
        with city_cols[i % n_cols_cities]:
            if st.checkbox(city, key=key):
                cities_to_compare.append(city)

    st.markdown("---")

    if not cities_to_compare:
        st.warning("Sélectionnez au moins une ville.")
    else:
        df_comparison = df_base[df_base["ville"].isin(cities_to_compare)].copy()
        available_stups = get_available_stups(df_comparison)

        if not available_stups:
            st.warning("Aucun stupéfiant disponible pour ces villes.")
        else:
            # Mode de comparaison avec 3 options
            st.markdown("#### 📊 Mode de visualisation")
            comparison_mode = st.radio(
                "",
                options=[
                    "📈 Tendances temporelles",
                    "🗺️ Carte + Boxplots (couleur carte = concentration)",
                    "📦 Boxplots uniquement (couleur = ville)"
                ],
                horizontal=True,
                key="comparison_mode",
                label_visibility="collapsed"
            )

            st.markdown("---")

        if "Carte" in comparison_mode:
            # Mode Carte : un seul stup affiché à la fois (via selectbox)
            # → max 3 cartes WebGL en parallèle (parent + métabolites du stup choisi),
            #   bien sous la limite navigateur
            selected_stup = st.selectbox(
                "🧪 Choisir le stupéfiant à visualiser",
                options=available_stups,
                key="all_carte_selected_stup",
            )

            wanted_analytes = RELATED_ANALYTES.get(selected_stup, [])
            df_stup = df_comparison[df_comparison["composes"].isin(wanted_analytes)].copy()

            if df_stup.empty:
                st.info(f"Aucune donnée disponible pour {selected_stup}.")
            else:
                n_points = len(df_stup.dropna(subset=["y"]))

                render_stup_panel_header(selected_stup, n_points)

                available = sorted(df_stup["composes"].dropna().unique())
                parents = [a for a in available if classify_analyte(a, selected_stup) == "parent"]
                metabs = [a for a in available if classify_analyte(a, selected_stup) == "metabolite"]

                selected_parents, selected_metabs = render_analyte_checkboxes(
                    parents, metabs, key_prefix=f"all_carte_{selected_stup}_"
                )
                selected_all = selected_parents + selected_metabs

                if not selected_all:
                    st.info("Sélectionnez au moins un analyte.")
                else:
                    df_filtered = df_stup[df_stup["composes"].isin(selected_all)]
                    render_comparison_with_map(
                        df_filtered, selected_stup,
                        key_prefix=f"all_carte_{selected_stup}_"
                    )

        else:
            # Modes Tendances / Boxplots uniquement : boucle classique sur tous les stups
            for stup in available_stups:
                wanted_analytes = RELATED_ANALYTES.get(stup, [])
                df_stup = df_comparison[df_comparison["composes"].isin(wanted_analytes)].copy()

                if df_stup.empty:
                    continue

                n_points = len(df_stup.dropna(subset=["y"]))

                with st.expander(f"🧪 **{stup}** ({n_points} points)", expanded=False):
                    render_stup_panel_header(stup, n_points)

                    available = sorted(df_stup["composes"].dropna().unique())
                    parents = [a for a in available if classify_analyte(a, stup) == "parent"]
                    metabs = [a for a in available if classify_analyte(a, stup) == "metabolite"]

                    selected_parents, selected_metabs = render_analyte_checkboxes(
                        parents, metabs, key_prefix=f"all_{stup}_"
                    )
                    selected_all = selected_parents + selected_metabs

                    if not selected_all:
                        st.info("Sélectionnez au moins un analyte.")
                    else:
                        df_filtered = df_stup[df_stup["composes"].isin(selected_all)]

                        if "Tendances" in comparison_mode:
                            render_timeseries_chart(
                                df_filtered, show_trend, normalize, df_mkt, start_d, end_d,
                                stup, key_prefix=f"all_{stup}_", is_comparison=True
                            )
                        else:  # Boxplots uniquement
                            render_comparison_boxplot_only(
                                df_filtered, stup, key_prefix=f"all_{stup}_"
                            )



# ----------------------
# TABS: Par ville
# ----------------------
for i, city in enumerate(all_available_cities):
    with tabs[i + 1]:
        df_city = df_base[df_base["ville"] == city].copy()

        if df_city.empty:
            st.warning(f"Aucune donnée pour **{city}**.")
        else:
            city_color = CITY_COLOR_MAP.get(city, "#0f4c81")
            st.markdown(f'<span class="city-badge" style="background: {city_color};">📍 {city}</span>',
                        unsafe_allow_html=True)

            n_points_total = len(df_city.dropna(subset=["y"]))
            n_outliers = df_city["is_outlier"].sum() if "is_outlier" in df_city.columns else 0
            n_lod = (df_city["flag_status"] == "LOD").sum() if "flag_status" in df_city.columns else 0
            n_loq = (df_city["flag_status"] == "LOQ").sum() if "flag_status" in df_city.columns else 0
            date_range = f"{_fmt_d(df_city['date'].min())} — {_fmt_d(df_city['date'].max())}"

            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-card">
                    <div class="kpi-label">📊 Points de données</div>
                    <div class="kpi-value">{n_points_total:,}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">📅 Période</div>
                    <div class="kpi-value" style="font-size: 1rem;">{date_range}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">🔴 <LOD / 🟠 <LOQ</div>
                    <div class="kpi-value" style="font-size: 1rem;">{n_lod} / {n_loq}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">⚫ Outliers</div>
                    <div class="kpi-value">{n_outliers}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            available_stups = get_available_stups(df_city)

            if not available_stups:
                st.info("Aucun stupéfiant détecté pour cette ville.")
            else:
                for stup in available_stups:
                    wanted_analytes = RELATED_ANALYTES.get(stup, [])
                    df_stup = df_city[df_city["composes"].isin(wanted_analytes)].copy()

                    if df_stup.empty:
                        continue

                    n_points = len(df_stup.dropna(subset=["y"]))

                    with st.expander(f"🧪 **{stup}** ({n_points} points)", expanded=False):
                        render_stup_panel_header(stup, n_points)

                        available = sorted(df_stup["composes"].dropna().unique())
                        parents = [a for a in available if classify_analyte(a, stup) == "parent"]
                        metabs = [a for a in available if classify_analyte(a, stup) == "metabolite"]

                        selected_parents, selected_metabs = render_analyte_checkboxes(
                            parents, metabs, key_prefix=f"{city}_{stup}_"
                        )
                        selected_all = selected_parents + selected_metabs

                        if not selected_all:
                            st.info("Sélectionnez au moins un analyte.")
                        else:
                            df_filtered = df_stup[df_stup["composes"].isin(selected_all)]

                            render_timeseries_chart(
                                df_filtered, show_trend, normalize, df_mkt, start_d, end_d,
                                stup, key_prefix=f"{city}_{stup}_", is_comparison=False
                            )

# ----------------------
# FOOTER
# ----------------------
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #888; font-size: 0.8rem;'>"
    f"WBE Dashboard • {_dt.date.today().strftime('%d.%m.%Y')} • "
    f"<LOD={LOD_REPLACEMENT_VALUE} ng/L, <LOQ={LOQ_REPLACEMENT_VALUE} ng/L</div>",
    unsafe_allow_html=True
)