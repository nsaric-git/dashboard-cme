# Dashboard CME — WBE Streamlit

Application Streamlit pour la visualisation des données de **Wastewater-Based Epidemiology (WBE)** dans le cadre du projet de thèse de Nikola Saric à l'École des Sciences Criminelles, Université de Lausanne.

L'app permet aux STEPs partenaires de consulter les tendances temporelles des concentrations de stupéfiants et de leurs métabolites dans les eaux usées, mesurées par LC-MS/MS.

## Contexte scientifique

Le dashboard affiche les **charges journalières normalisées** (mg/jour/1000 habitants) calculées à partir des concentrations mesurées (ng/L), des volumes journaliers d'eaux usées et de la population desservie par chaque STEP.

⚠️ **Limites d'interprétation** : les comparaisons strictes entre STEPs sont à éviter. La variabilité de la collecte (type de réseau, dégradation in-sewer, événements météo, flux pendulaires) impacte les charges mesurées. L'outil est conçu pour suivre les **tendances temporelles au sein d'une même STEP** plutôt que pour comparer des valeurs absolues entre sites.

## Prérequis

- Python 3.11 ou supérieur
- Les fichiers de données Excel (`260205_WW_AllData_LA_v2.xlsx` et `251113_Data.xlsx`) à la racine du projet

## Installation

```bash
# Cloner le repo
git clone https://github.com/nsaric-git/dashboard-cme.git
cd dashboard-cme

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'app s'ouvre par défaut sur http://localhost:8501

## Structure du projet
dashboard-cme/
├── app.py                              # Application Streamlit principale
├── requirements.txt                    # Dépendances Python
├── 260205_WW_AllData_LA_v2.xlsx        # Données WBE
├── 251113_Data.xlsx                    # Données de pureté (saisies)
├── .gitignore                          # Fichiers ignorés par Git
└── README.md                           # Ce fichier

## Méthodologie

- **`<LOD`** : valeurs sous la limite de détection → remplacées par 0 ng/L
- **`<LOQ`** : valeurs sous la limite de quantification → remplacées par LOQ/2 = 5 ng/L (pratique standard pour les données gauche-censurées)
- **Outliers** : exclus des statistiques mais affichés visuellement
- **Pureté** : les charges peuvent être normalisées par la pureté trimestrielle estimée à partir des données de saisies

## Auteur

Nikola Saric — Assistant-doctorant
École des Sciences Criminelles, Université de Lausanne
nikola.saric@unil.ch

## Statut

🚧 En développement — déploiement prévu sur Streamlit Community Cloud.