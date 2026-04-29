# src/stockage/stockage.py
"""
Phase 3 — Stockage dans MySQL
Responsabilité : charger les données dans la base dtb360_bi
"""

import mysql.connector
import pandas as pd
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import DB_CONFIG
from datetime import datetime

# ── CONNEXION ─────────────────────────────────────────────────

def connecter():
    """Établit la connexion à MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✅ Connexion MySQL établie → {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Erreur connexion MySQL : {e}")
        raise

# ── CHARGEMENT DIMENSIONS ─────────────────────────────────────

def charger_dim_canton(conn, df):
    """Charge la table dim_canton."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dim_canton")

    cantons_info = {
        "ZH": ("Zürich", "DE"),
        "BE": ("Bern", "DE"),
        "LU": ("Luzern", "DE"),
        "UR": ("Uri", "DE"),
        "SZ": ("Schwyz", "DE"),
        "OW": ("Obwalden", "DE"),
        "NW": ("Nidwalden", "DE"),
        "GL": ("Glarus", "DE"),
        "ZG": ("Zug", "DE"),
        "FR": ("Fribourg", "FR"),
        "SO": ("Solothurn", "DE"),
        "BS": ("Basel-Stadt", "DE"),
        "BL": ("Basel-Landschaft", "DE"),
        "SH": ("Schaffhausen", "DE"),
        "AR": ("Appenzell Ausserrhoden", "DE"),
        "AI": ("Appenzell Innerrhoden", "DE"),
        "SG": ("St. Gallen", "DE"),
        "GR": ("Graubünden", "DE"),
        "AG": ("Aargau", "DE"),
        "TG": ("Thurgau", "DE"),
        "TI": ("Ticino", "IT"),
        "VD": ("Vaud", "FR"),
        "VS": ("Valais", "FR"),
        "NE": ("Neuchâtel", "FR"),
        "GE": ("Genève", "FR"),
        "JU": ("Jura", "FR"),
    }

    canton_counts = df["canton"].value_counts().to_dict()

    for code, (nom, langue) in cantons_info.items():
        nb = canton_counts.get(code, 0)
        cursor.execute("""
            INSERT INTO dim_canton
            (code_canton, nom_canton, region_linguistique, nb_societes)
            VALUES (%s, %s, %s, %s)
        """, (code, nom, langue, nb))

    conn.commit()
    print(f"  ✅ dim_canton : {len(cantons_info)} cantons chargés")
    cursor.close()

def charger_dim_secteur(conn, df):
    """Charge la table dim_secteur."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dim_secteur")

    secteurs_info = {
        "IT / Logiciels / IA / Data":   ("ICT & Digital", "High"),
        "Ingénierie":                    ("Engineering & Industry", "High"),
        "H&T / Services":               ("Retail / Commerce", "Medium"),
        "Ventes / Communication":        ("Finance & Business Services", "Medium"),
        "Santé (Non Rég.)":             ("Healthcare & Pharma", "High"),
        "Énergies Renouvelables":        ("Energy & Environment", "High"),
        "Techniques Spécialisées":       ("Construction & Infrastructure", "Medium"),
        "Hors périmètre":               ("Other", "Low"),
    }

    domaine_counts = df["priority_domain_dtb360"].value_counts().to_dict() \
        if "priority_domain_dtb360" in df.columns else {}

    for domaine, (macro, priorite) in secteurs_info.items():
        nb = domaine_counts.get(domaine, 0)
        cursor.execute("""
            INSERT INTO dim_secteur
            (macro_secteur, domaine_dtb360, priorite_dtb360, nb_societes)
            VALUES (%s, %s, %s, %s)
        """, (macro, domaine, priorite, nb))

    conn.commit()
    print(f"  ✅ dim_secteur : {len(secteurs_info)} secteurs chargés")
    cursor.close()

# ── CHARGEMENT SOCIÉTÉS ───────────────────────────────────────

def charger_fact_societes(conn, df):
    """Charge la table fact_societes."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fact_societes")

    def safe(val):
        if pd.isna(val) if not isinstance(val, str) else False:
            return None
        return str(val)[:500] if val else None

    def safe_int(val):
        try:
            return int(float(val)) if not pd.isna(val) else None
        except: return None

    def safe_date(val):
        if pd.isna(val) if not isinstance(val, str) else False:
            return None
        try:
            return str(val)[:10]
        except: return None

    sql = """
        INSERT INTO fact_societes (
            company_id_internal, company_name, company_name_normalized,
            company_type, phone, email, website, address,
            zip_code, city, canton, country, language_region,
            macro_sector, priority_domain_dtb360, domain_fit_score,
            dtb360_priority_level, company_status, zefix_status,
            zefix_uid, zefix_confidence, linkedin_url, job_portal_url,
            has_careers_page, data_quality_score, contactability_score,
            missing_fields_count, prospection_priority,
            partnership_potential, duplicate_flag, record_status,
            verification_source, verification_confidence,
            last_verified_date
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s
        )
    """

    batch = []
    total = len(df)
    inserted = 0

    for _, row in df.iterrows():
        batch.append((
            safe(row.get("company_id_internal")),
            safe(row.get("Company name")),
            safe(row.get("company_name_normalized")),
            safe(row.get("type")),
            safe(row.get("phone")),
            safe(row.get("email")),
            safe(row.get("web site")),
            safe(row.get("adress")),
            safe(row.get("ZIP CODE")),
            safe(row.get("city")),
            safe(row.get("canton")),
            safe(row.get("country")),
            safe(row.get("language_region")),
            safe(row.get("macro_sector")),
            safe(row.get("priority_domain_dtb360")),
            safe_int(row.get("domain_fit_score")),
            safe(row.get("dtb360_priority_level")),
            safe(row.get("company_status_operational")),
            safe(row.get("zefix_status")),
            safe(row.get("zefix_uid")),
            safe(row.get("zefix_confidence")),
            safe(row.get("linkedin_company_url")),
            safe(row.get("job portal url")),
            safe(row.get("has_careers_page")),
            safe_int(row.get("data_quality_score")),
            safe_int(row.get("contactability_score")),
            safe_int(row.get("missing_fields_count")),
            safe(row.get("prospection_priority")),
            safe(row.get("partnership_potential")),
            safe(row.get("duplicate_flag")),
            safe(row.get("record_status")),
            safe(row.get("verification_source")),
            safe(row.get("verification_confidence")),
            safe_date(row.get("last_verified_date")),
        ))

        # Insérer par batch de 500
        if len(batch) == 500:
            cursor.executemany(sql, batch)
            conn.commit()
            inserted += len(batch)
            print(f"  ⏳ {inserted}/{total} sociétés insérées...", end="\r")
            batch = []

    # Insérer le reste
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
        inserted += len(batch)

    print(f"  ✅ fact_societes : {inserted} sociétés chargées")
    cursor.close()

# ── LOG ETL ───────────────────────────────────────────────────

def log_etl(conn, phase, nb_entree, nb_sortie, statut, message, duree):
    """Enregistre un log ETL dans la base."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs_etl
        (phase, nb_lignes_entree, nb_lignes_sortie, statut, message, duree_secondes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (phase, nb_entree, nb_sortie, statut, message, duree))
    conn.commit()
    cursor.close()

# ── PIPELINE STOCKAGE ─────────────────────────────────────────

def run_stockage(df: pd.DataFrame) -> None:
    print("\n🚀 DÉMARRAGE PHASE 3 — STOCKAGE MySQL")
    print("="*60)
    debut = time.time()

    conn = connecter()

    try:
        print("\n📥 Chargement des dimensions...")
        charger_dim_canton(conn, df)
        charger_dim_secteur(conn, df)

        print("\n📥 Chargement des sociétés...")
        charger_fact_societes(conn, df)

        duree = round(time.time() - debut, 2)

        # Log ETL
        log_etl(conn, "stockage_complet",
                len(df), len(df), "SUCCESS",
                f"Chargement complet : {len(df)} sociétés",
                duree)

        print("\n" + "="*60)
        print("       RAPPORT PHASE 3 — STOCKAGE")
        print("="*60)
        print(f"✅ fact_societes : {len(df):,} lignes")
        print(f"✅ dim_canton    : 26 cantons")
        print(f"✅ dim_secteur   : 8 secteurs")
        print(f"✅ logs_etl      : 1 log enregistré")
        print(f"⏱️  Durée         : {duree} secondes")
        print("="*60)
        print("✅ Phase 3 terminée !")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        log_etl(conn, "stockage_complet", len(df), 0, "ERROR", str(e), 0)
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    df = pd.read_excel("data/processed/base_finale.xlsx")
    df = df.drop_duplicates(subset=["Company name", "ZIP CODE"], keep="first")
    print(f"📂 {len(df)} sociétés chargées depuis base_finale.xlsx")
    run_stockage(df)