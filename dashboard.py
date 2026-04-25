import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIGURATION PAGE ────────────────────────────────────────
st.set_page_config(
    page_title="DTB360 — Dashboard Sociétés Suisses",
    page_icon="🇨🇭",
    layout="wide"
)

# ── CHARGEMENT DONNÉES ─────────────────────────────────────
@st.cache_data
def charger_données():
    return pd.read_excel("base_finale.xlsx")

df = charger_données()

# ── HEADER ────────────────────────────────────────────────────
st.title("🇨🇭 DIGITECHBRIDGE360 — Dashboard Sociétés Suisses")
st.markdown("---")

# ── SIDEBAR FILTRES ───────────────────────────────────────────
st.sidebar.title("🔍 Filtres")

# Filtre canton
cantons = ["Tous"] + sorted(df["canton"].dropna().unique().tolist())
canton_selec = st.sidebar.selectbox("Canton", cantons)

# Filtre domaine DTB360
domaines = ["Tous"] + sorted(df["priority_domain_dtb360"].dropna().unique().tolist())
domaine_selec = st.sidebar.selectbox("Domaine DTB360", domaines)

# Filtre priorité prospection
priorites = ["Tous", "P1", "P2", "P3"]
priorite_selec = st.sidebar.selectbox("Priorité prospection", priorites)

# Filtre statut
statuts = ["Tous"] + sorted(df["company_status_operational"].dropna().unique().tolist())
statut_selec = st.sidebar.selectbox("Statut société", statuts)

# Appliquer les filtres
df_filtre = df.copy()
if canton_selec != "Tous":
    df_filtre = df_filtre[df_filtre["canton"] == canton_selec]
if domaine_selec != "Tous":
    df_filtre = df_filtre[df_filtre["priority_domain_dtb360"] == domaine_selec]
if priorite_selec != "Tous":
    df_filtre = df_filtre[df_filtre["prospection_priority"] == priorite_selec]
if statut_selec != "Tous":
    df_filtre = df_filtre[df_filtre["company_status_operational"] == statut_selec]

st.sidebar.markdown("---")
st.sidebar.metric("Sociétés filtrées", len(df_filtre))

# ══════════════════════════════════════════════════════════════
# VUE 1 — KPIs GLOBAUX
# ══════════════════════════════════════════════════════════════
st.header("📊 Vue 1 — KPIs Globaux")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🏢 Total Sociétés",    f"{len(df_filtre):,}")
col2.metric("✅ Sites Accessibles", f"{(df_filtre['website accessible']=='Accessible').sum():,}")
col3.metric("📞 Téléphones",        f"{df_filtre['phone'].notna().sum():,}")
col4.metric("📧 Emails",            f"{df_filtre['email'].notna().sum():,}")
col5.metric("⭐ Score Qualité Moy", f"{df_filtre['data_quality_score'].mean():.1f}/100")

st.markdown("---")

col6, col7, col8, col9 = st.columns(4)
col6.metric("🚀 Priorité P1",       f"{(df_filtre['prospection_priority']=='P1').sum():,}")
col7.metric("🟡 Priorité P2",       f"{(df_filtre['prospection_priority']=='P2').sum():,}")
col8.metric("🔵 Priorité P3",       f"{(df_filtre['prospection_priority']=='P3').sum():,}")
col9.metric("🤝 Partenariat High",  f"{(df_filtre['partnership_potential']=='High').sum():,}")

st.markdown("---")

# Jauge score qualité
fig_jauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=df_filtre["data_quality_score"].mean(),
    title={"text": "Score Qualité Moyen"},
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
fig_jauge.update_layout(height=300)

col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(fig_jauge, use_container_width=True)

with col_g2:
    # Répartition statut opérationnel
    statut_counts = df_filtre["company_status_operational"].value_counts()
    fig_statut = px.pie(
        values=statut_counts.values,
        names=statut_counts.index,
        title="Statut Opérationnel des Sociétés",
        color_discrete_map={
            "Probably Open":   "#2ECC71",
            "Unknown":         "#95A5A6",
            "To Verify":       "#F39C12",
            "Probably Closed": "#E74C3C",
        }
    )
    st.plotly_chart(fig_statut, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# VUE 2 — RÉPARTITION SECTORIELLE
# ══════════════════════════════════════════════════════════════
st.header("🏭 Vue 2 — Répartition Sectorielle")

col_s1, col_s2 = st.columns(2)

with col_s1:
    # Domaines DTB360
    domaine_counts = df_filtre["priority_domain_dtb360"].value_counts()
    fig_domaine = px.bar(
        x=domaine_counts.values,
        y=domaine_counts.index,
        orientation="h",
        title="Sociétés par Domaine DTB360",
        color=domaine_counts.values,
        color_continuous_scale="Blues",
        labels={"x": "Nombre", "y": "Domaine"}
    )
    fig_domaine.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_domaine, use_container_width=True)

with col_s2:
    # Macro secteurs
    macro_counts = df_filtre["macro_sector"].value_counts()
    fig_macro = px.pie(
        values=macro_counts.values,
        names=macro_counts.index,
        title="Répartition par Macro-Secteur",
        hole=0.4
    )
    fig_macro.update_layout(height=400)
    st.plotly_chart(fig_macro, use_container_width=True)

# Domain fit score
fig_fit = px.histogram(
    df_filtre,
    x="domain_fit_score",
    title="Distribution du Score d'Alignement DTB360 (1-5)",
    color="dtb360_priority_level",
    color_discrete_map={
        "High":   "#2ECC71",
        "Medium": "#F39C12",
        "Low":    "#E74C3C"
    },
    labels={"domain_fit_score": "Score Alignement", "count": "Nombre"}
)
st.plotly_chart(fig_fit, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# VUE 3 — RÉPARTITION GÉOGRAPHIQUE
# ══════════════════════════════════════════════════════════════
st.header("🗺️ Vue 3 — Répartition Géographique")

col_g1, col_g2 = st.columns(2)

with col_g1:
    # Top 15 cantons
    canton_counts = df_filtre["canton"].value_counts().head(15)
    fig_canton = px.bar(
        x=canton_counts.index,
        y=canton_counts.values,
        title="Top 15 Cantons",
        color=canton_counts.values,
        color_continuous_scale="Blues",
        labels={"x": "Canton", "y": "Nombre de sociétés"}
    )
    fig_canton.update_layout(showlegend=False)
    st.plotly_chart(fig_canton, use_container_width=True)

with col_g2:
    # Répartition par langue
    langue_counts = df_filtre["language_region"].value_counts()
    lang_labels = {"DE": "🇩🇪 Allemand", "FR": "🇫🇷 Français", "IT": "🇮🇹 Italien"}
    langue_counts.index = [lang_labels.get(l, l) for l in langue_counts.index]
    fig_langue = px.pie(
        values=langue_counts.values,
        names=langue_counts.index,
        title="Répartition par Région Linguistique",
        color_discrete_sequence=["#1F4E79", "#E74C3C", "#2ECC71"]
    )
    st.plotly_chart(fig_langue, use_container_width=True)

# Top 15 villes
ville_counts = df_filtre["city"].value_counts().head(15)
fig_ville = px.bar(
    x=ville_counts.index,
    y=ville_counts.values,
    title="Top 15 Villes",
    color=ville_counts.values,
    color_continuous_scale="Oranges",
    labels={"x": "Ville", "y": "Nombre"}
)
fig_ville.update_layout(showlegend=False)
st.plotly_chart(fig_ville, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# VUE 4 — QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════
st.header("📋 Vue 4 — Qualité des Données")

# Taux de remplissage par colonne
champs_cles = {
    "Company name":    "Nom société",
    "web site":        "Site web",
    "phone":           "Téléphone",
    "email":           "Email",
    "adress":          "Adresse",
    "canton":          "Canton",
    "type":            "Type juridique",
    "macro_sector":    "Macro secteur",
    "has_careers_page":"Page carrière",
}

taux = {}
for col, label in champs_cles.items():
    if col in df_filtre.columns:
        taux[label] = df_filtre[col].notna().sum() / len(df_filtre) * 100

fig_qualite = px.bar(
    x=list(taux.values()),
    y=list(taux.keys()),
    orientation="h",
    title="Taux de Remplissage par Champ (%)",
    color=list(taux.values()),
    color_continuous_scale="RdYlGn",
    range_color=[0, 100],
    labels={"x": "Taux (%)", "y": "Champ"}
)
fig_qualite.add_vline(x=80, line_dash="dash", line_color="green",
                       annotation_text="Seuil 80%")
fig_qualite.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_qualite, use_container_width=True)

col_q1, col_q2, col_q3 = st.columns(3)

# Distribution score qualité
fig_score = px.histogram(
    df_filtre,
    x="data_quality_score",
    nbins=20,
    title="Distribution Score Qualité",
    color_discrete_sequence=["#1F4E79"],
    labels={"data_quality_score": "Score", "count": "Nombre"}
)
col_q1.plotly_chart(fig_score, use_container_width=True)

# Record status
record_counts = df_filtre["record_status"].value_counts()
fig_record = px.pie(
    values=record_counts.values,
    names=record_counts.index,
    title="Statut des Fiches",
    color_discrete_map={
        "Valid":       "#2ECC71",
        "Incomplete":  "#F39C12",
        "To Review":   "#E74C3C",
        "Duplicate":   "#95A5A6"
    }
)
col_q2.plotly_chart(fig_record, use_container_width=True)

# Contactabilité
fig_contact = px.histogram(
    df_filtre,
    x="contactability_score",
    nbins=10,
    title="Score de Contactabilité",
    color_discrete_sequence=["#E74C3C"],
    labels={"contactability_score": "Score", "count": "Nombre"}
)
col_q3.plotly_chart(fig_contact, use_container_width=True)
# ── Bloc ZEFIX ──────────────────────────────────────────────
if "zefix_status" in df_filtre.columns:
    st.subheader("🏛️ Vérification ZEFIX — Registre Officiel Suisse")

    col_z1, col_z2, col_z3, col_z4 = st.columns(4)
    actives    = (df_filtre["zefix_status"] == "Active").sum()
    radiees    = (df_filtre["zefix_status"] == "Radiée").sum()
    verifiees  = df_filtre["zefix_status"].notna().sum()
    haut_conf  = (df_filtre["zefix_confidence"] == "High").sum()

    col_z1.metric("✅ Sociétés Actives",    f"{actives:,}")
    col_z2.metric("❌ Sociétés Radiées",    f"{radiees:,}")
    col_z3.metric("🔍 Vérifiées ZEFIX",    f"{verifiees:,}")
    col_z4.metric("⭐ Haute Confiance",     f"{haut_conf:,}")

    # Graphique statuts ZEFIX
    zefix_counts = df_filtre["zefix_status"].value_counts()
    fig_zefix = px.pie(
        values=zefix_counts.values,
        names=zefix_counts.index,
        title="🏛️ Statuts Officiels ZEFIX",
        color_discrete_map={
            "Active":       "#2ECC71",
            "Radiée":       "#E74C3C",
            "En liquidation":"#F39C12",
            "Non trouvé":   "#95A5A6",
            "Inconnu":      "#BDC3C7"
        },
        hole=0.4
    )
    st.plotly_chart(fig_zefix, use_container_width=True)

    # Tableau sociétés vérifiées P1
    st.subheader("🎯 Sociétés P1 Vérifiées ZEFIX")
    df_zefix_p1 = df_filtre[
        (df_filtre["zefix_status"] == "Active") &
        (df_filtre["prospection_priority"] == "P1")
    ][[
        "Company name", "canton", "priority_domain_dtb360",
        "uid_ide", "zefix_status", "zefix_confidence",
        "phone", "email", "zefix_source_url"
    ]].sort_values("Company name")

    st.dataframe(df_zefix_p1, use_container_width=True, height=400)
    st.success(f"✅ {len(df_zefix_p1)} sociétés P1 officiellement actives selon ZEFIX !")

# ══════════════════════════════════════════════════════════════
# VUE 5 — PILOTAGE COMMERCIAL DTB360
# ══════════════════════════════════════════════════════════════
st.header("🚀 Vue 5 — Pilotage Commercial DTB360")

col_p1, col_p2 = st.columns(2)

with col_p1:
    # Prospection priority
    prosp_counts = df_filtre["prospection_priority"].value_counts()
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
        labels={"x": "Priorité", "y": "Nombre"}
    )
    st.plotly_chart(fig_prosp, use_container_width=True)

with col_p2:
    # Partnership potential
    partner_counts = df_filtre["partnership_potential"].value_counts()
    fig_partner = px.pie(
        values=partner_counts.values,
        names=partner_counts.index,
        title="Potentiel de Partenariat",
        color_discrete_map={
            "High":   "#2ECC71",
            "Medium": "#F39C12",
            "Low":    "#E74C3C"
        }
    )
    st.plotly_chart(fig_partner, use_container_width=True)

# Tableau sociétés P1
st.subheader("🎯 Sociétés Prioritaires P1")
df_p1 = df_filtre[df_filtre["prospection_priority"] == "P1"][[
    "Company name", "canton", "priority_domain_dtb360",
    "phone", "email", "web site",
    "data_quality_score", "contactability_score",
    "partnership_potential"
]].sort_values("data_quality_score", ascending=False)

st.dataframe(df_p1, use_container_width=True, height=400)
st.caption(f"📊 {len(df_p1)} sociétés prioritaires P1")

# ══════════════════════════════════════════════════════════════
# VUE 6 — ANALYSE RECRUTEMENT & OPPORTUNITÉS
# ══════════════════════════════════════════════════════════════
st.header("💼 Vue 6 — Analyse Recrutement & Opportunités")
st.caption("Vue ajoutée pour répondre au cœur de métier de DTB360 : connecter les talents aux entreprises qui recrutent")

# ── KPIs Recrutement ─────────────────────────────────────────
col_r1, col_r2, col_r3, col_r4 = st.columns(4)

total = len(df_filtre)
avec_carriere = (df_filtre["has_careers_page"] == "Yes").sum()
avec_offres   = (df_filtre["job_postings_detected"] == "Yes").sum()
contactables  = (df_filtre["contactability_score"] >= 50).sum()

col_r1.metric("📄 Avec Page Carrière",   f"{avec_carriere:,}",
              f"{avec_carriere/total*100:.1f}%")
col_r2.metric("📢 Offres Détectées",     f"{avec_offres:,}",
              f"{avec_offres/total*100:.1f}%")
col_r3.metric("📞 Facilement Contactables", f"{contactables:,}",
              f"{contactables/total*100:.1f}%")
col_r4.metric("🎯 Score Contact Moyen",
              f"{df_filtre['contactability_score'].mean():.1f}/100")

st.markdown("---")

col_rv1, col_rv2 = st.columns(2)

with col_rv1:
    # Secteurs qui recrutent le plus
    df_recrutement = df_filtre[df_filtre["has_careers_page"] == "Yes"]
    if len(df_recrutement) > 0:
        recr_secteur = df_recrutement["priority_domain_dtb360"].value_counts()
        fig_recr = px.bar(
            x=recr_secteur.values,
            y=recr_secteur.index,
            orientation="h",
            title="🏭 Secteurs qui Recrutent le Plus",
            color=recr_secteur.values,
            color_continuous_scale="Greens",
            labels={"x": "Nombre de sociétés", "y": "Secteur"}
        )
        fig_recr.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_recr, use_container_width=True)

with col_rv2:
    # Niveau d'activité recrutement
    recr_niveau = df_filtre["recruitment_activity_level"].value_counts()
    fig_niveau = px.pie(
        values=recr_niveau.values,
        names=recr_niveau.index,
        title="📊 Niveau d'Activité Recrutement",
        color_discrete_map={
            "High":    "#2ECC71",
            "Medium":  "#F39C12",
            "Low":     "#E74C3C",
            "Unknown": "#95A5A6"
        },
        hole=0.4
    )
    fig_niveau.update_layout(height=400)
    st.plotly_chart(fig_niveau, use_container_width=True)

# Cantons qui recrutent le plus
col_rv3, col_rv4 = st.columns(2)

with col_rv3:
    canton_recr = df_recrutement["canton"].value_counts().head(10)
    fig_canton_recr = px.bar(
        x=canton_recr.index,
        y=canton_recr.values,
        title="🗺️ Top 10 Cantons — Sociétés qui Recrutent",
        color=canton_recr.values,
        color_continuous_scale="Blues",
        labels={"x": "Canton", "y": "Nombre"}
    )
    fig_canton_recr.update_layout(showlegend=False)
    st.plotly_chart(fig_canton_recr, use_container_width=True)

with col_rv4:
    # Score contactabilité par secteur
    contact_secteur = df_filtre.groupby("priority_domain_dtb360")[
        "contactability_score"].mean().sort_values(ascending=False)
    fig_contact_sec = px.bar(
        x=contact_secteur.values,
        y=contact_secteur.index,
        orientation="h",
        title="📞 Score Contactabilité Moyen par Secteur",
        color=contact_secteur.values,
        color_continuous_scale="RdYlGn",
        labels={"x": "Score moyen", "y": "Secteur"}
    )
    fig_contact_sec.update_layout(showlegend=False)
    st.plotly_chart(fig_contact_sec, use_container_width=True)

# ── Tableau Top Opportunités ──────────────────────────────────
st.subheader("🎯 Top Opportunités — Sociétés qui Recrutent et Contactables")
st.caption("Sociétés avec page carrière + email ou téléphone disponible + priorité P1 ou P2")

df_opportunites = df_filtre[
    (df_filtre["has_careers_page"] == "Yes") &
    (df_filtre["contactability_score"] >= 25) &
    (df_filtre["prospection_priority"].isin(["P1", "P2"]))
][[
    "Company name", "canton", "priority_domain_dtb360",
    "phone", "email", "web site", "job portal url",
    "contactability_score", "prospection_priority",
    "recruitment_activity_level", "partnership_potential"
]].sort_values("contactability_score", ascending=False)

st.dataframe(df_opportunites, use_container_width=True, height=400)

col_stat1, col_stat2, col_stat3 = st.columns(3)
col_stat1.success(f"✅ {len(df_opportunites)} opportunités identifiées")
col_stat2.info(f"📞 {df_opportunites['phone'].notna().sum()} avec téléphone")
col_stat3.info(f"📧 {df_opportunites['email'].notna().sum()} avec email")



# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "**DIGITECHBRIDGE360** — Dashboard Data Quality | "
    f"Base : {len(df):,} sociétés suisses | "
    "Développé par Maiza Roua"
)