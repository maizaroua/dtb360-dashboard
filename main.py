# main.py
"""
Pipeline BI DTB360 — Orchestrateur Principal
Lance toutes les phases dans l'ordre automatiquement
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

print("="*60)
print("   PIPELINE BI DTB360 — DÉMARRAGE AUTOMATIQUE")
print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

debut_total = time.time()

# ── PHASE 1 — COLLECTE ────────────────────────────────────────
print("\n📥 PHASE 1 — COLLECTE")
debut = time.time()
from src.collecte.collecte import run_collecte
df_source = run_collecte()
print(f"⏱️  Durée : {round(time.time()-debut, 2)}s")

# ── PHASE 2 — PRÉTRAITEMENT ───────────────────────────────────
print("\n🔧 PHASE 2 — PRÉTRAITEMENT")
debut = time.time()
from src.pretraitement.pretraitement import run_pretraitement
df_propre = run_pretraitement(df_source)
print(f"⏱️  Durée : {round(time.time()-debut, 2)}s")

# ── PHASE 3 — STOCKAGE ────────────────────────────────────────
print("\n🗄️  PHASE 3 — STOCKAGE MySQL")
debut = time.time()
from src.stockage.stockage import run_stockage
import pandas as pd
df_final = pd.read_excel("data/processed/base_finale.xlsx")
df_final = df_final.drop_duplicates(
    subset=["Company name", "ZIP CODE"], keep="first")
run_stockage(df_final)
print(f"⏱️  Durée : {round(time.time()-debut, 2)}s")

# ── PHASE 4 — KPIs ────────────────────────────────────────────
print("\n📊 PHASE 4 — MODÉLISATION KPIs")
debut = time.time()
from src.modelisation.kpis import run_kpis
kpis = run_kpis(df_final)
print(f"⏱️  Durée : {round(time.time()-debut, 2)}s")

# ── RÉSUMÉ FINAL ──────────────────────────────────────────────
duree_totale = round(time.time() - debut_total, 2)
print("\n" + "="*60)
print("   PIPELINE TERMINÉ AVEC SUCCÈS ✅")
print("="*60)
print(f"📊 Sociétés traitées : {len(df_final):,}")
print(f"📈 KPIs calculés     : {len(kpis)}")
print(f"⏱️  Durée totale      : {duree_totale}s")
print(f"\n🚀 Lancez le dashboard :")
print(f"   streamlit run src/dashboard/dashboard.py")
print("="*60)