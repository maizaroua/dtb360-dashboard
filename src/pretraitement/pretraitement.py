# src/pretraitement/pretraitement.py
"""
Phase 2 — Prétraitement des données
Responsabilité : nettoyage, normalisation, déduplication
"""

import pandas as pd
import re
import hashlib
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import DATA_CONFIG, QUALITE_CONFIG
from datetime import datetime

# ── NETTOYAGE ─────────────────────────────────────────────────

def nettoyer_nom(nom):
    if pd.isna(nom): return nom
    nom = str(nom).strip().strip('"').strip("'")
    return re.sub(r"\s+", " ", nom)

def normaliser_url(url):
    if pd.isna(url) or str(url).strip() == "": return None
    url = str(url).strip()
    if not url.startswith("http"): url = "https://" + url
    return url.rstrip("/")

def normaliser_npa(npa):
    if pd.isna(npa): return None
    npa_str = re.sub(r"\D", "", str(npa))
    if len(npa_str) == 4 and 1000 <= int(npa_str) <= 9999:
        return npa_str
    return None

def generer_id(nom, zip_code):
    cle = f"{str(nom).strip().lower()}|{str(zip_code).strip()}"
    return "DTB360-" + hashlib.md5(cle.encode()).hexdigest()[:8].upper()

def normaliser_nom_compare(nom):
    if pd.isna(nom): return ""
    nom = str(nom).lower().strip()
    for suffix in [" ag", " sa", " gmbh", " sàrl", " sarl", " ltd"]:
        nom = nom.replace(suffix, "")
    nom = re.sub(r"[^a-z0-9\s]", "", nom)
    return re.sub(r"\s+", " ", nom).strip()

# ── DÉDUPLICATION ─────────────────────────────────────────────

def dedupliquer(df):
    avant = len(df)
    df["_filled"] = df.notna().sum(axis=1)
    df = (df.sort_values("_filled", ascending=False)
            .drop_duplicates(subset=["Company name", "ZIP CODE"], keep="first")
            .drop(columns=["_filled"]))
    apres = len(df)
    print(f"  ✅ Doublons supprimés : {avant - apres}")
    return df

# ── CANTON ET LANGUE ──────────────────────────────────────────

def get_canton(zip_code):
    if pd.isna(zip_code): return None
    try:
        npa = int(str(zip_code).strip().split(".")[0])
        if 1000 <= npa <= 1209: return "VD"
        elif 1210 <= npa <= 1299: return "GE"
        elif 1300 <= npa <= 1999: return "VD"
        elif 2000 <= npa <= 2799: return "NE"
        elif 2800 <= npa <= 2999: return "JU"
        elif 3000 <= npa <= 3899: return "BE"
        elif 3900 <= npa <= 3999: return "VS"
        elif 4000 <= npa <= 4099: return "BS"
        elif 4100 <= npa <= 4499: return "BL"
        elif 4500 <= npa <= 4999: return "SO"
        elif 5000 <= npa <= 5999: return "AG"
        elif 6000 <= npa <= 6499: return "LU"
        elif 6500 <= npa <= 6999: return "TI"
        elif 7000 <= npa <= 7999: return "GR"
        elif 8000 <= npa <= 8499: return "ZH"
        elif 8500 <= npa <= 8599: return "TG"
        elif 8600 <= npa <= 8999: return "ZH"
        elif 9000 <= npa <= 9499: return "SG"
        elif 9500 <= npa <= 9999: return "AR"
    except: pass
    return None

def get_langue(canton):
    fr = ["GE", "VD", "NE", "JU", "VS", "FR"]
    it = ["TI"]
    if canton in fr: return "FR"
    if canton in it: return "IT"
    return "DE"

# ── PIPELINE PRÉTRAITEMENT ────────────────────────────────────

def run_pretraitement(df: pd.DataFrame) -> pd.DataFrame:
    print("\n🚀 DÉMARRAGE PHASE 2 — PRÉTRAITEMENT")
    print("="*60)

    # 1. Nettoyage
    print("🔧 Nettoyage des données...")
    df["Company name"] = df["Company name"].apply(nettoyer_nom)
    df["web site"]     = df["web site"].apply(normaliser_url)
    df["ZIP CODE"]     = df["ZIP CODE"].apply(normaliser_npa)
    print("  ✅ Noms, URLs et codes postaux normalisés")

    # 2. Déduplication
    print("🔍 Déduplication...")
    df = dedupliquer(df)

    # 3. Enrichissement de base
    print("➕ Ajout des champs de base...")
    df["company_id_internal"]     = df.apply(
        lambda r: generer_id(r["Company name"], r["ZIP CODE"]), axis=1)
    df["company_name_normalized"] = df["Company name"].apply(normaliser_nom_compare)
    df["canton"]          = df["ZIP CODE"].apply(get_canton)
    df["language_region"] = df["canton"].apply(get_langue)
    df["city"]            = df["Region"]
    df["country"]         = "Switzerland"
    df["duplicate_flag"]  = "No"
    df["record_created"]  = datetime.now().strftime("%Y-%m-%d")
    print("  ✅ Identifiants, cantons et langues ajoutés")

    # 4. Forme juridique
    print("⚖️  Extraction forme juridique...")
    formes = {
        "AG": r"\bAG\b", "SA": r"\bSA\b",
        "GmbH": r"\bGmbH\b", "Sàrl": r"\bS[aà]rl\b",
        "Sagl": r"\bSagl\b", "Ltd": r"\bLtd\.?\b"
    }
    def extraire_type(nom):
        if pd.isna(nom): return "Autre"
        for forme, pattern in formes.items():
            if re.search(pattern, str(nom), re.IGNORECASE):
                return forme
        return "Autre"
    df["type"] = df["Company name"].apply(extraire_type)
    print("  ✅ Formes juridiques extraites")

    # 5. Rapport
    print("\n" + "="*60)
    print("       RAPPORT PHASE 2 — PRÉTRAITEMENT")
    print("="*60)
    print(f"📊 Sociétés après nettoyage : {len(df):,}")
    print(f"\n⚖️  FORMES JURIDIQUES :")
    for forme, count in df["type"].value_counts().items():
        print(f"  {forme:10s} : {count:,}")
    print(f"\n🗺️  TOP 5 CANTONS :")
    for canton, count in df["canton"].value_counts().head(5).items():
        print(f"  {canton} : {count:,}")
    print(f"\n🌐 RÉGIONS LINGUISTIQUES :")
    for langue, count in df["language_region"].value_counts().items():
        print(f"  {langue} : {count:,}")
    print("="*60)

    # 6. Sauvegarde
    chemin_sortie = "data/processed/base_pretaitee.xlsx"
    df.to_excel(chemin_sortie, index=False)
    print(f"💾 Fichier sauvegardé : {chemin_sortie}")
    print("✅ Phase 2 terminée !")

    return df

if __name__ == "__main__":
    from src.collecte.collecte import run_collecte
    df_source = run_collecte()
    df_propre = run_pretraitement(df_source)