# src/dashboard/dashboard.py
"""
Phase 5 — Dashboard Décisionnel DTB360
Connecté à MySQL — Visualisation professionnelle
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import DB_CONFIG

# ── CONFIGURATION PAGE ────────────────────────────────────────
st.set_page_config(
    page_title="DTB360 — Intelligence Commerciale Suisse",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLE CSS PROFESSIONNEL ───────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1F4E79, #2E75B6);
        padding: 20px 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2E75B6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .section-title {
        color: #1F4E79;
        font-size: 20px;
        font-weight: bold;
        border-bottom: 2px solid #2E75B6;
        padding-bottom: 5px;
        margin: 20px 0 15px 0;
    }
    .metric-good  { color: #2ECC71; font-weight: bold; }
    .metric-warn  { color: #F39C12; font-weight: bold; }
    .metric-bad   { color: #E74C3C; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── CONNEXION MYSQL ───────────────────────────────────────────
@st.cache_resource
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except:
        return None

@st.cache_data(ttl=300)
def charger_societes():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM fact_societes", conn)
        conn.close()
        return df
    except:
        return pd.read_excel("data/processed/base_finale.xlsx")

@st.cache_data(ttl=300)
def charger_kpis():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(
            "SELECT * FROM fact_kpis ORDER BY date_calcul DESC",
            conn
        )
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def charger_cantons():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM dim_canton", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ── CHARGEMENT ────────────────────────────────────────────────
df_all    = charger_societes()
df_kpis   = charger_kpis()
df_canton = charger_cantons()

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0">🇨🇭 DIGITECHBRIDGE360</h1>
    <p style="margin:5px 0 0 0; opacity:0.9">
        Plateforme d'Intelligence Commerciale — Base Sociétés Suisses
    </p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/switzerland.png", width=60)
st.sidebar.title("🔍 Filtres")

cantons_list = ["Tous"] + sorted(df_all["canton"].dropna().unique().tolist())
domaines_list = ["Tous"] + sorted(
    df_all["priority_domain_dtb360"].dropna().unique().tolist())
priorites_list = ["Tous", "P1", "P2", "P3"]
statuts_list = ["Tous"] + sorted(
    df_all["company_status_operational"].dropna().unique().tolist()) \
    if "company_status_operational" in df_all.columns else \
    ["Tous"] + sorted(
    df_all["company_status"].dropna().unique().tolist()) \
    if "company_status" in df_all.columns else ["Tous"]

canton_sel   = st.sidebar.selectbox("📍 Canton", cantons_list)
domaine_sel  = st.sidebar.selectbox("🏭 Domaine DTB360", domaines_list)
priorite_sel = st.sidebar.selectbox("🎯 Priorité", priorites_list)
statut_sel   = st.sidebar.selectbox("✅ Statut", statuts_list)

# Appliquer filtres
df = df_all.copy()
if canton_sel   != "Tous": df = df[df["canton"] == canton_sel]
if domaine_sel  != "Tous": df = df[df["priority_domain_dtb360"] == domaine_sel]
if priorite_sel != "Tous": df = df[df["prospection_priority"] == priorite_sel]
col_statut = "company_status" if "company_status" in df.columns \
             else "company_status_operational"
if statut_sel != "Tous": df = df[df[col_statut] == statut_sel]

st.sidebar.markdown("---")
st.sidebar.metric("Sociétés sélectionnées", f"{len(df):,}")
st.sidebar.metric("Sur total", f"{len(df_all):,}")

# ── NAVIGATION ────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Tableau de Bord",
    "🏭 Analyse Sectorielle",
    "🗺️ Analyse Géographique",
    "📋 Qualité des Données",
    "🚀 Pilotage Commercial",
    "💼 Opportunités Recrutement",
    "📈 Suivi des KPIs"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-title">Vue d\'ensemble — Indicateurs Clés</div>',
                unsafe_allow_html=True)

    # KPIs principaux
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏢 Total Sociétés",     f"{len(df):,}")
    c2.metric("✅ Sites Accessibles",
             f"{(df.get('company_status', df.get('company_status_operational', pd.Series()))=='Probably Open').sum():,}")
    c3.metric("📞 Téléphones",         f"{df['phone'].notna().sum():,}")
    c4.metric("📧 Emails",             f"{df['email'].notna().sum():,}")
    c5.metric("⭐ Score Qualité Moy.", f"{df['data_quality_score'].mean():.1f}/100"
              if 'data_quality_score' in df.columns else "N/A")

    st.markdown("---")

    c6, c7, c8, c9 = st.columns(4)
    c6.metric("🟢 Priorité P1",
              f"{(df['prospection_priority']=='P1').sum():,}")
    c7.metric("🟡 Priorité P2",
              f"{(df['prospection_priority']=='P2').sum():,}")
    c8.metric("🔵 Priorité P3",
              f"{(df['prospection_priority']=='P3').sum():,}")
    c9.metric("🇨🇭 Certifiées ZEFIX",
              f"{(df['zefix_status']=='Active').sum():,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Jauge score qualité
        score_moy = df["data_quality_score"].mean() \
                    if "data_quality_score" in df.columns else 0
        fig_jauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score_moy,
            title={"text": "Score Qualité Moyen", "font": {"size": 16}},
            delta={"reference": 70, "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1F4E79"},
                "steps": [
                    {"range": [0, 40],  "color": "#FADBD8"},
                    {"range": [40, 70], "color": "#FEF9E7"},
                    {"range": [70, 100],"color": "#D5F5E3"},
                ],
                "threshold": {
                    "line": {"color": "green", "width": 4},
                    "thickness": 0.75,
                    "value": 70
                }
            }
        ))
        fig_jauge.update_layout(height=280)
        st.plotly_chart(fig_jauge, use_container_width=True)

    with col2:
        # Statut opérationnel
        statut_counts = df["company_status"].value_counts()
        fig_statut = px.pie(
            values=statut_counts.values,
            names=statut_counts.index,
            title="Statut Opérationnel des Sociétés",
            color_discrete_map={
                "Probably Open":   "#2ECC71",
                "Active":          "#27AE60",
                "Unknown":         "#95A5A6",
                "To Verify":       "#F39C12",
                "Probably Closed": "#E74C3C",
            },
            hole=0.4
        )
        fig_statut.update_layout(height=280)
        st.plotly_chart(fig_statut, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — ANALYSE SECTORIELLE
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-title">Répartition par Secteur d\'Activité</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        domaine_counts = df["priority_domain_dtb360"].value_counts()
        fig_dom = px.bar(
            x=domaine_counts.values,
            y=domaine_counts.index,
            orientation="h",
            title="Sociétés par Domaine Prioritaire DTB360",
            color=domaine_counts.values,
            color_continuous_scale="Blues",
            labels={"x": "Nombre de sociétés", "y": "Domaine"}
        )
        fig_dom.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_dom, use_container_width=True)

    with col2:
        macro_counts = df["macro_sector"].value_counts() \
                       if "macro_sector" in df.columns else pd.Series()
        if not macro_counts.empty:
            fig_macro = px.pie(
                values=macro_counts.values,
                names=macro_counts.index,
                title="Répartition par Macro-Secteur",
                hole=0.4
            )
            fig_macro.update_layout(height=400)
            st.plotly_chart(fig_macro, use_container_width=True)

    # Score alignement
    if "domain_fit_score" in df.columns:
        fig_fit = px.histogram(
            df, x="domain_fit_score",
            title="Distribution du Score d'Alignement DTB360 (1 à 5)",
            color="dtb360_priority_level",
            color_discrete_map={
                "High": "#2ECC71", "Medium": "#F39C12", "Low": "#E74C3C"
            },
            labels={"domain_fit_score": "Score d'alignement",
                    "count": "Nombre de sociétés"}
        )
        st.plotly_chart(fig_fit, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — ANALYSE GÉOGRAPHIQUE
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-title">Répartition Géographique en Suisse</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        canton_counts = df["canton"].value_counts().head(15)
        fig_canton = px.bar(
            x=canton_counts.index,
            y=canton_counts.values,
            title="Top 15 Cantons — Nombre de Sociétés",
            color=canton_counts.values,
            color_continuous_scale="Blues",
            labels={"x": "Canton", "y": "Nombre de sociétés"}
        )
        fig_canton.update_layout(showlegend=False)
        st.plotly_chart(fig_canton, use_container_width=True)

    with col2:
        langue_counts = df["language_region"].value_counts() \
                        if "language_region" in df.columns else pd.Series()
        lang_labels = {
            "DE": "🇩🇪 Suisse Allemande",
            "FR": "🇫🇷 Suisse Romande",
            "IT": "🇮🇹 Suisse Italienne"
        }
        if not langue_counts.empty:
            langue_counts.index = [
                lang_labels.get(l, l) for l in langue_counts.index]
            fig_langue = px.pie(
                values=langue_counts.values,
                names=langue_counts.index,
                title="Répartition par Région Linguistique",
                color_discrete_sequence=["#1F4E79", "#E74C3C", "#2ECC71"]
            )
            st.plotly_chart(fig_langue, use_container_width=True)

    # Top villes
    if "city" in df.columns:
        ville_counts = df["city"].value_counts().head(15)
        fig_ville = px.bar(
            x=ville_counts.index,
            y=ville_counts.values,
            title="Top 15 Villes — Concentration de Sociétés",
            color=ville_counts.values,
            color_continuous_scale="Oranges",
            labels={"x": "Ville", "y": "Nombre de sociétés"}
        )
        fig_ville.update_layout(showlegend=False)
        st.plotly_chart(fig_ville, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-title">Audit Qualité des Données</div>',
                unsafe_allow_html=True)

    # Taux de remplissage
    champs = {
        "company_name":           "Nom Société",
        "website":                "Site Web",
        "phone":                  "Téléphone",
        "email":                  "Email",
        "address":                "Adresse",
        "canton":                 "Canton",
        "company_type":           "Type Juridique",
        "macro_sector":           "Macro Secteur",
        "priority_domain_dtb360": "Domaine DTB360",
        "zefix_status":           "Statut ZEFIX",
        "linkedin_url":           "LinkedIn",
    }

    taux = {}
    for col, label in champs.items():
        if col in df.columns:
            taux[label] = df[col].notna().sum() / len(df) * 100

    fig_qual = px.bar(
        x=list(taux.values()),
        y=list(taux.keys()),
        orientation="h",
        title="Taux de Remplissage par Champ (%)",
        color=list(taux.values()),
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        labels={"x": "Taux de remplissage (%)", "y": "Champ"}
    )
    fig_qual.add_vline(x=80, line_dash="dash", line_color="green",
                       annotation_text="Seuil cible 80%")
    fig_qual.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_qual, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        fig_score = px.histogram(
            df, x="data_quality_score", nbins=20,
            title="Distribution Score Qualité",
            color_discrete_sequence=["#1F4E79"],
            labels={"data_quality_score": "Score Qualité",
                    "count": "Nombre"}
        ) if "data_quality_score" in df.columns else None
        if fig_score:
            st.plotly_chart(fig_score, use_container_width=True)

    with col2:
        if "record_status" in df.columns:
            rec_counts = df["record_status"].value_counts()
            fig_rec = px.pie(
                values=rec_counts.values,
                names=rec_counts.index,
                title="Statut des Fiches",
                color_discrete_map={
                    "Valid":      "#2ECC71",
                    "Incomplete": "#F39C12",
                    "To Review":  "#E74C3C"
                }
            )
            st.plotly_chart(fig_rec, use_container_width=True)

    with col3:
        # Certification ZEFIX
        if "zefix_status" in df.columns:
            zefix_counts = df["zefix_status"].value_counts()
            fig_zefix = px.pie(
                values=zefix_counts.values,
                names=zefix_counts.index,
                title="Statuts Officiels ZEFIX 🇨🇭",
                color_discrete_map={
                    "Active":      "#2ECC71",
                    "Non trouvé":  "#95A5A6",
                    "Inconnu":     "#F39C12"
                },
                hole=0.4
            )
            st.plotly_chart(fig_zefix, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — PILOTAGE COMMERCIAL
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-title">Pilotage Commercial DTB360</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        prosp_counts = df["prospection_priority"].value_counts()
        fig_prosp = px.bar(
            x=prosp_counts.index,
            y=prosp_counts.values,
            title="Répartition par Priorité de Prospection",
            color=prosp_counts.index,
            color_discrete_map={
                "P1": "#2ECC71",
                "P2": "#F39C12",
                "P3": "#E74C3C"
            },
            labels={"x": "Priorité", "y": "Nombre de sociétés"}
        )
        st.plotly_chart(fig_prosp, use_container_width=True)

    with col2:
        if "partnership_potential" in df.columns:
            partner_counts = df["partnership_potential"].value_counts()
            fig_partner = px.pie(
                values=partner_counts.values,
                names=partner_counts.index,
                title="Potentiel de Partenariat Commercial",
                color_discrete_map={
                    "High":   "#2ECC71",
                    "Medium": "#F39C12",
                    "Low":    "#E74C3C"
                }
            )
            st.plotly_chart(fig_partner, use_container_width=True)

    # Tableau P1
    st.markdown("#### 🎯 Sociétés Prioritaires P1 — Prêtes pour Prospection")
    df_p1 = df[df["prospection_priority"] == "P1"][[
        "company_name", "canton", "priority_domain_dtb360",
        "phone", "email", "website",
        "data_quality_score", "contactability_score",
        "zefix_status", "partnership_potential"
    ]].sort_values("data_quality_score", ascending=False) \
      if "prospection_priority" in df.columns else pd.DataFrame()

    st.dataframe(df_p1, use_container_width=True, height=400)

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.success(f"✅ {len(df_p1):,} sociétés P1 identifiées")
    col_s2.info(f"📞 {df_p1['phone'].notna().sum():,} avec téléphone")
    col_s3.info(f"📧 {df_p1['email'].notna().sum():,} avec email")

# ══════════════════════════════════════════════════════════════
# TAB 6 — OPPORTUNITÉS RECRUTEMENT
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-title">Analyse des Opportunités de Recrutement</div>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    total = len(df)

    avec_carriere  = (df["has_careers_page"] == "Yes").sum() \
                     if "has_careers_page" in df.columns else 0
    contactables   = (df["contactability_score"] >= 50).sum() \
                     if "contactability_score" in df.columns else 0
    score_contact  = df["contactability_score"].mean() \
                     if "contactability_score" in df.columns else 0

    col1.metric("📄 Avec Page Carrière",
                f"{avec_carriere:,}",
                f"{avec_carriere/total*100:.1f}%")
    col2.metric("📞 Facilement Contactables",
                f"{contactables:,}",
                f"{contactables/total*100:.1f}%")
    col3.metric("⭐ Score Contact Moyen",
                f"{score_contact:.1f}/100")
    col4.metric("🔗 Profils LinkedIn",
                f"{df['linkedin_url'].notna().sum():,}"
                if "linkedin_url" in df.columns else "0")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        df_recr = df[df["has_careers_page"] == "Yes"] \
                  if "has_careers_page" in df.columns else pd.DataFrame()
        if not df_recr.empty:
            recr_sec = df_recr["priority_domain_dtb360"].value_counts()
            fig_recr = px.bar(
                x=recr_sec.values,
                y=recr_sec.index,
                orientation="h",
                title="Secteurs qui Recrutent le Plus",
                color=recr_sec.values,
                color_continuous_scale="Greens",
                labels={"x": "Nombre", "y": "Secteur"}
            )
            fig_recr.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_recr, use_container_width=True)

    with col2:
        if not df_recr.empty:
            canton_recr = df_recr["canton"].value_counts().head(10)
            fig_cr = px.bar(
                x=canton_recr.index,
                y=canton_recr.values,
                title="Top 10 Cantons — Sociétés qui Recrutent",
                color=canton_recr.values,
                color_continuous_scale="Blues",
                labels={"x": "Canton", "y": "Nombre"}
            )
            fig_cr.update_layout(showlegend=False)
            st.plotly_chart(fig_cr, use_container_width=True)

    # Top opportunités
    st.markdown("#### 🎯 Meilleures Opportunités — Recrutement + Contactables")
    df_opp = df[
        (df.get("has_careers_page", pd.Series()) == "Yes") &
        (df["prospection_priority"].isin(["P1", "P2"]))
    ][[
        "company_name", "canton", "priority_domain_dtb360",
        "phone", "email", "job_portal_url",
        "contactability_score", "prospection_priority"
    ]].sort_values("contactability_score", ascending=False) \
      if "has_careers_page" in df.columns else pd.DataFrame()

    st.dataframe(df_opp, use_container_width=True, height=350)

# ══════════════════════════════════════════════════════════════
# TAB 7 — SUIVI DES KPIs
# ══════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="section-title">Tableau de Bord des KPIs — Suivi des Objectifs</div>',
                unsafe_allow_html=True)

    if not df_kpis.empty:
        # Tableau KPIs
        df_kpis_display = df_kpis[[
            "kpi_nom", "kpi_valeur", "kpi_objectif",
            "kpi_unite", "kpi_statut", "kpi_description"
        ]].rename(columns={
            "kpi_nom":         "Indicateur",
            "kpi_valeur":      "Valeur",
            "kpi_objectif":    "Objectif",
            "kpi_unite":       "Unité",
            "kpi_statut":      "Statut",
            "kpi_description": "Description"
        })
        st.dataframe(df_kpis_display, use_container_width=True, height=400)

        # Graphique KPIs vs Objectifs
        fig_kpi = go.Figure()
        fig_kpi.add_trace(go.Bar(
            name="Valeur actuelle",
            x=df_kpis["kpi_nom"],
            y=df_kpis["kpi_valeur"],
            marker_color="#1F4E79"
        ))
        fig_kpi.add_trace(go.Scatter(
            name="Objectif",
            x=df_kpis["kpi_nom"],
            y=df_kpis["kpi_objectif"],
            mode="lines+markers",
            line=dict(color="#E74C3C", dash="dash", width=2),
            marker=dict(size=8)
        ))
        fig_kpi.update_layout(
            title="KPIs vs Objectifs DTB360",
            xaxis_tickangle=-45,
            height=450,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_kpi, use_container_width=True)

    else:
        st.warning("⚠️ Aucun KPI trouvé — Lancez d'abord la Phase 4 !")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"**DIGITECHBRIDGE360** — Plateforme Intelligence Commerciale | "
    f"Base : {len(df_all):,} sociétés suisses | "
    f"Développé par Maiza Roua | "
    f"Source : MySQL `dtb360_bi`"
)