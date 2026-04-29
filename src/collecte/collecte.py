# src/collecte/collecte.py
"""
Phase 1 — Collecte des données
Responsabilité : lire et valider les données sources
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import DATA_CONFIG
from datetime import datetime

def lire_source(chemin: str, sheet: str = "all companies") -> pd.DataFrame:
    """Lit le fichier source Excel et retourne un DataFrame."""
    print(f"📥 Lecture du fichier source : {chemin}")
    try:
        df = pd.read_excel(chemin, sheet_name=sheet, dtype=str)
        df.columns = [c.strip() for c in df.columns]
        print(f"✅ {len(df)} lignes lues | {len(df.columns)} colonnes")
        return df
    except Exception as e:
        print(f"❌ Erreur lecture : {e}")
        raise

def valider_source(df: pd.DataFrame) -> dict:
    """Valide la qualité de la source et retourne un rapport."""
    rapport = {
        "date_validation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nb_lignes":       len(df),
        "nb_colonnes":     len(df.columns),
        "colonnes":        list(df.columns),
        "taux_remplissage": {},
        "alertes":         []
    }

    # Calcul taux remplissage
    for col in df.columns:
        filled = df[col].notna().sum()
        pct    = filled / len(df) * 100
        rapport["taux_remplissage"][col] = round(pct, 1)
        if pct == 0:
            rapport["alertes"].append(f"⚠️ Colonne '{col}' entièrement vide !")
        elif pct < 50:
            rapport["alertes"].append(f"⚠️ Colonne '{col}' remplie à {pct:.1f}%")

    return rapport

def afficher_rapport_collecte(rapport: dict) -> None:
    """Affiche le rapport de collecte."""
    print("\n" + "="*60)
    print("       RAPPORT PHASE 1 — COLLECTE")
    print("="*60)
    print(f"📅 Date          : {rapport['date_validation']}")
    print(f"📊 Lignes lues   : {rapport['nb_lignes']:,}")
    print(f"📋 Colonnes      : {rapport['nb_colonnes']}")
    print(f"\n📈 TAUX DE REMPLISSAGE :")
    print("-"*40)
    for col, pct in rapport["taux_remplissage"].items():
        statut = "✅" if pct > 80 else "⚠️" if pct > 20 else "🔴"
        print(f"  {statut} {col:25s} : {pct:5.1f}%")
    if rapport["alertes"]:
        print(f"\n🚨 ALERTES ({len(rapport['alertes'])}) :")
        for alerte in rapport["alertes"]:
            print(f"  {alerte}")
    print("="*60)

def run_collecte() -> pd.DataFrame:
    """Point d'entrée principal de la phase collecte."""
    print("\n🚀 DÉMARRAGE PHASE 1 — COLLECTE")
    print("="*60)

    # Lire la source
    chemin = DATA_CONFIG["raw_file"]
    df = lire_source(chemin)

    # Valider
    rapport = valider_source(df)
    afficher_rapport_collecte(rapport)

    return df

if __name__ == "__main__":
    df = run_collecte()