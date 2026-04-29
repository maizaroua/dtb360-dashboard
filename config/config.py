
"""Configuration globale de la solution BI DTB360."""

# ── BASE DE DONNÉES MYSQL ─────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",          # Mot de passe XAMPP (vide par défaut)
    "database": "dtb360_bi",
    "port":     3306
}

# ── FICHIERS DE DONNÉES ───────────────────────────────────────
DATA_CONFIG = {
  "raw_file": "data/raw/all company suisse.xlsx",
    "processed_file": "data/processed/base_finale.xlsx",
    "output_dir":     "data/output/"
}

# ── PARAMÈTRES SCRAPING ───────────────────────────────────────
SCRAPING_CONFIG = {
    "pause_entre_sites": 1,
    "timeout":           8,
    "sauvegarde_chaque": 100,
    "pages_contact": [
        "/contact", "/kontakt",
        "/contacts", "/nous-contacter"
    ]
}

# ── PARAMÈTRES QUALITÉ ────────────────────────────────────────
QUALITE_CONFIG = {
    "score_minimum_valid":    70,
    "score_minimum_review":   40,
    "confidence_accept":      0.85,
    "confidence_review":      0.60,
}

# ── KPIs — OBJECTIFS DTB360 ───────────────────────────────────
KPI_OBJECTIFS = {
    "taux_completude":        70.0,   # % minimum acceptable
    "taux_telephone":         60.0,   # % téléphones remplis
    "taux_email":             60.0,   # % emails remplis
    "score_qualite_moyen":    70.0,   # score /100
    "taux_certification_zefix": 80.0, # % sociétés P1 certifiées
    "taux_classification":    50.0,   # % sociétés classifiées
    "nb_societes_p1_min":     800,    # nombre minimum P1
}

# ── CLASSIFICATION DTB360 ─────────────────────────────────────
DOMAINES_DTB360 = [
    "IT / Logiciels / IA / Data",
    "Ingénierie",
    "H&T / Services",
    "Ventes / Communication",
    "Santé (Non Rég.)",
    "Énergies Renouvelables",
    "Techniques Spécialisées",
    "Hors périmètre"
]

STATUTS_OPERATIONNELS = [
    "Active",
    "Probably Open",
    "Probably Closed",
    "To Verify",
    "Unknown"
]