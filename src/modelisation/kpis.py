# src/modelisation/kpis.py
"""
Phase 4 — Modélisation des KPIs
Responsabilité : calculer et stocker les KPIs dans MySQL
"""

import mysql.connector
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import DB_CONFIG, KPI_OBJECTIFS
from datetime import datetime, date

# ── CONNEXION ─────────────────────────────────────────────────
def connecter():
    return mysql.connector.connect(**DB_CONFIG)

# ── CALCUL DES KPIs ───────────────────────────────────────────
def calculer_kpis(df: pd.DataFrame) -> list:
    """Calcule tous les KPIs et retourne une liste de dictionnaires."""
    today = date.today()
    kpis  = []
    total = len(df)

    def ajouter_kpi(code, nom, valeur, objectif, unite, description):
        statut = "✅ Atteint" if valeur >= objectif else "⚠️ En cours" \
                 if valeur >= objectif * 0.8 else "🔴 À améliorer"
        kpis.append({
            "date_calcul":   today,
            "kpi_code":      code,
            "kpi_nom":       nom,
            "kpi_valeur":    round(valeur, 2),
            "kpi_objectif":  objectif,
            "kpi_unite":     unite,
            "kpi_statut":    statut,
            "kpi_description": description
        })

    # ── KPI 1 : Taux de complétude global
    champs_cles = ["phone", "email", "web site", "adress", "canton"]
    taux_list = []
    for col in champs_cles:
        if col in df.columns:
            taux_list.append(df[col].notna().sum() / total * 100)
    taux_completude = sum(taux_list) / len(taux_list) if taux_list else 0
    ajouter_kpi(
        "COMPLETUDE_GLOBALE",
        "Taux de Complétude Global",
        taux_completude,
        KPI_OBJECTIFS["taux_completude"],
        "%",
        "Moyenne du taux de remplissage des champs essentiels"
    )

    # ── KPI 2 : Taux d'enrichissement téléphone
    taux_tel = df["phone"].notna().sum() / total * 100 \
               if "phone" in df.columns else 0
    ajouter_kpi(
        "TAUX_TELEPHONE",
        "Taux d'Enrichissement Téléphone",
        taux_tel,
        KPI_OBJECTIFS["taux_telephone"],
        "%",
        "Pourcentage de sociétés avec numéro de téléphone"
    )

    # ── KPI 3 : Taux d'enrichissement email
    taux_email = df["email"].notna().sum() / total * 100 \
                 if "email" in df.columns else 0
    ajouter_kpi(
        "TAUX_EMAIL",
        "Taux d'Enrichissement Email",
        taux_email,
        KPI_OBJECTIFS["taux_email"],
        "%",
        "Pourcentage de sociétés avec adresse email"
    )

    # ── KPI 4 : Score qualité moyen
    score_moyen = df["data_quality_score"].mean() \
                  if "data_quality_score" in df.columns else 0
    ajouter_kpi(
        "SCORE_QUALITE",
        "Score Qualité Moyen",
        score_moyen,
        KPI_OBJECTIFS["score_qualite_moyen"],
        "/100",
        "Score moyen de qualité des fiches sociétés"
    )

    # ── KPI 5 : Taux certification ZEFIX
    if "zefix_status" in df.columns:
        p1_total  = (df["prospection_priority"] == "P1").sum()
        p1_actives = (
            (df["prospection_priority"] == "P1") &
            (df["zefix_status"] == "Active")
        ).sum()
        taux_zefix = p1_actives / p1_total * 100 if p1_total > 0 else 0
    else:
        taux_zefix = 0
    ajouter_kpi(
        "TAUX_CERTIFICATION_ZEFIX",
        "Taux de Certification ZEFIX",
        taux_zefix,
        KPI_OBJECTIFS["taux_certification_zefix"],
        "%",
        "Pourcentage de sociétés P1 certifiées actives par ZEFIX"
    )

    # ── KPI 6 : Taux de classification sectorielle
    if "priority_domain_dtb360" in df.columns:
        classes = (df["priority_domain_dtb360"] != "Hors périmètre").sum()
        taux_classif = classes / total * 100
    else:
        taux_classif = 0
    ajouter_kpi(
        "TAUX_CLASSIFICATION",
        "Taux de Classification Sectorielle",
        taux_classif,
        KPI_OBJECTIFS["taux_classification"],
        "%",
        "Pourcentage de sociétés classifiées dans un domaine DTB360"
    )

    # ── KPI 7 : Nombre de sociétés P1
    nb_p1 = int((df["prospection_priority"] == "P1").sum()) \
            if "prospection_priority" in df.columns else 0
    ajouter_kpi(
        "NB_SOCIETES_P1",
        "Nombre de Sociétés Prioritaires P1",
        nb_p1,
        KPI_OBJECTIFS["nb_societes_p1_min"],
        "sociétés",
        "Sociétés prioritaires hautement alignées avec DTB360"
    )

    # ── KPI 8 : Sociétés P1 contactables
    if "prospection_priority" in df.columns:
        p1_contactables = (
            (df["prospection_priority"] == "P1") &
            (df["phone"].notna() | df["email"].notna())
        ).sum()
    else:
        p1_contactables = 0
    ajouter_kpi(
        "P1_CONTACTABLES",
        "Sociétés P1 Contactables",
        int(p1_contactables),
        800,
        "sociétés",
        "Sociétés P1 avec téléphone ou email disponible"
    )

    # ── KPI 9 : Score contactabilité moyen
    score_contact = df["contactability_score"].mean() \
                    if "contactability_score" in df.columns else 0
    ajouter_kpi(
        "SCORE_CONTACTABILITE",
        "Score de Contactabilité Moyen",
        score_contact,
        50,
        "/100",
        "Score moyen de contactabilité commerciale"
    )

    # ── KPI 10 : Index de prospection DTB360
    if "prospection_priority" in df.columns:
        nb_p2 = (df["prospection_priority"] == "P2").sum()
        nb_p3 = (df["prospection_priority"] == "P3").sum()
        index_prosp = (nb_p1 * 3 + nb_p2 * 2 + nb_p3 * 1) / total
    else:
        index_prosp = 0
    ajouter_kpi(
        "INDEX_PROSPECTION",
        "Index de Prospection DTB360",
        index_prosp,
        1.5,
        "score",
        "Score global de valeur commerciale de la base"
    )

    return kpis

# ── STOCKAGE KPIs ─────────────────────────────────────────────
def stocker_kpis(conn, kpis: list) -> None:
    """Stocke les KPIs dans la table fact_kpis."""
    cursor = conn.cursor()

    # Supprimer les KPIs du jour
    cursor.execute("DELETE FROM fact_kpis WHERE date_calcul = %s",
                   (date.today(),))

    sql = """
        INSERT INTO fact_kpis
        (date_calcul, kpi_code, kpi_nom, kpi_valeur,
         kpi_objectif, kpi_unite, kpi_statut, kpi_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for kpi in kpis:
        cursor.execute(sql, (
            kpi["date_calcul"],
            kpi["kpi_code"],
            kpi["kpi_nom"],
            kpi["kpi_valeur"],
            kpi["kpi_objectif"],
            kpi["kpi_unite"],
            kpi["kpi_statut"],
            kpi["kpi_description"]
        ))

    conn.commit()
    cursor.close()

# ── PIPELINE KPIs ─────────────────────────────────────────────
def run_kpis(df: pd.DataFrame) -> list:
    print("\n🚀 DÉMARRAGE PHASE 4 — MODÉLISATION KPIs")
    print("="*60)

    # Calculer
    print("📊 Calcul des KPIs...")
    kpis = calculer_kpis(df)

    # Stocker dans MySQL
    conn = connecter()
    stocker_kpis(conn, kpis)
    conn.close()

    # Rapport
    print("\n" + "="*60)
    print("       RAPPORT PHASE 4 — KPIs DTB360")
    print("="*60)
    print(f"{'KPI':<35} {'Valeur':>10} {'Objectif':>10} {'Statut'}")
    print("-"*70)
    for kpi in kpis:
        print(f"{kpi['kpi_nom']:<35} "
              f"{kpi['kpi_valeur']:>8.1f}{kpi['kpi_unite']:>4} "
              f"{kpi['kpi_objectif']:>8.1f}     "
              f"{kpi['kpi_statut']}")
    print("="*60)
    print(f"✅ {len(kpis)} KPIs calculés et stockés dans MySQL !")

    return kpis

if __name__ == "__main__":
    df = pd.read_excel("data/processed/base_finale.xlsx")
    df = df.drop_duplicates(subset=["Company name", "ZIP CODE"], keep="first")
    print(f"📂 {len(df)} sociétés chargées")
    kpis = run_kpis(df)