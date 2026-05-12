#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║   4 EXPERIENCE — Simulateur de piste & Airbag        ║
║   Lancement : streamlit run simulateur_4experience.py ║
║   Dépendances : pip install streamlit numpy scipy     ║
║                 matplotlib pandas                     ║
╚══════════════════════════════════════════════════════╝
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import interpolate
import pandas as pd
import streamlit as st
import io
import hashlib

# ════════════════════════════════════════════════════════════════
# PROTECTION MOT DE PASSE
# ════════════════════════════════════════════════════════════════
MOT_DE_PASSE = "4experience2025"   # <-- Changez ce mot de passe ici

def check_password():
    """Affiche un écran de connexion et bloque l'accès si le mot de passe est incorrect."""

    def verifier():
        mdp_saisi = st.session_state.get("mdp_input", "")
        if hashlib.sha256(mdp_saisi.encode()).hexdigest() == \
           hashlib.sha256(MOT_DE_PASSE.encode()).hexdigest():
            st.session_state["authentifie"] = True
        else:
            st.session_state["authentifie"] = False
            st.session_state["mdp_erreur"] = True

    if st.session_state.get("authentifie"):
        return True

    # Page de connexion
    st.set_page_config(
        page_title="4 Experience – Connexion",
        page_icon="🔒",
        layout="centered",
    )
    st.markdown("""
    <style>
    .login-box {
        max-width: 400px; margin: 80px auto 0 auto;
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 16px; padding: 2.5rem 2rem; text-align: center;
    }
    .login-box h2 { color: #1e3a5f; font-size: 1.3rem; margin-bottom: .4rem; }
    .login-box p  { color: #64748b; font-size: .9rem; margin-bottom: 1.5rem; }
    </style>
    <div class="login-box">
      <div style="font-size:3rem">🏔️</div>
      <h2>4 Experience — Simulateur</h2>
      <p>Entrez le mot de passe pour accéder à l'application</p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        st.text_input("Mot de passe", type="password",
                      key="mdp_input", on_change=verifier,
                      placeholder="••••••••••••••")
        if st.session_state.get("mdp_erreur"):
            st.error("Mot de passe incorrect.")
        st.caption("Appuyez sur Entrée pour valider")

    return False

if not check_password():
    st.stop()

# ── Config page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="4 Experience – Simulateur",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Style global ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1a2744 0%, #0d1b35 100%);
    border-radius: 12px; padding: 1.2rem 1.8rem; margin-bottom: 1.4rem;
    display: flex; align-items: center; gap: 1rem; border-left: 4px solid #3b82f6;
}
.main-header h1 { color: #f1f5f9; font-size: 1.4rem; font-weight: 600; margin: 0; }
.main-header p  { color: #94a3b8; font-size: 0.85rem; margin: 0; }

.section-title {
    font-size: 13px; font-weight: 600; color: #1e3a5f;
    border-bottom: 2px solid #dbeafe; padding-bottom: 4px;
    margin-bottom: 10px; margin-top: 4px;
}
.info-box {
    background: #eff6ff; border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0; padding: 10px 14px;
    font-size: 13px; color: #1e40af; margin-top: 10px;
}
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9; border-radius: 10px; padding: 4px; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; font-weight: 500; font-size: 14px; padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: white !important; box-shadow: 0 1px 4px rgba(0,0,0,.1);
}
div.stButton > button[kind="primary"] {
    background: #1e3a5f; color: white; border: none; border-radius: 8px;
    font-weight: 600; font-size: 14px; padding: 10px 0; transition: background .15s;
}
div.stButton > button[kind="primary"]:hover { background: #2563eb; }
section[data-testid="stSidebar"] { background: #0f1c30; }
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
section[data-testid="stSidebar"] .stNumberInput input {
    background: #1e3a5f; color: #f1f5f9; border-color: #334155;
}
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# BASE DE DONNÉES SURFACES
# ════════════════════════════════════════════════════════════════
g = 9.80665

# Neige naturelle : un seul μ (pas de distinction sec/humide car déjà intégré)
# Revêtements synthétiques : μ sec et μ humide distincts
SURFACES_DB = {
    "❄️ Neige glacée":   {"—": {"sec": 0.03, "humide": 0.03}},
    "❄️ Neige dure":     {"—": {"sec": 0.07, "humide": 0.07}},
    "❄️ Neige normale":  {"—": {"sec": 0.10, "humide": 0.10}},
    "❄️ Neige humide":   {"—": {"sec": 0.18, "humide": 0.18}},
    "❄️ Neige fraîche":  {"—": {"sec": 0.12, "humide": 0.12}},
    "🟩 Neveplast":       {"—": {"sec": 0.12, "humide": 0.10}},
    "🟩 PearlSlide":      {"—": {"sec": 0.11, "humide": 0.10}},
    "🟩 PearlSnow":       {"—": {"sec": 0.11, "humide": 0.10}},
    "🟩 DreamSlide":      {"—": {"sec": 0.12, "humide": 0.10}},
    "🟩 DreamSnow":       {"—": {"sec": 0.15, "humide": 0.14}},
    "🛝 Caoutchouc":      {"—": {"sec": 0.25, "humide": 0.20}},
    "⛷️ Personnalisé":    {"—": {"sec": 0.10, "humide": 0.10}},
}
CATS = list(SURFACES_DB.keys())

def get_mu(cat, var, cond):
    return SURFACES_DB.get(cat, {}).get(var, {}).get(cond, 0.10)

# ════════════════════════════════════════════════════════════════
# PHYSIQUE — PISTE
# ════════════════════════════════════════════════════════════════
def simuler_piste(sections, masse, V0_kmh, S, Cx, rho, Npoints=2000):
    n      = len(sections)
    angles = np.array([s["angle"]      for s in sections])
    longu  = np.array([s["longueur"]   for s in sections])
    frott  = np.array([s["frottement"] for s in sections])

    s_pts = np.zeros(n+1); x_pts = np.zeros(n+1); y_pts = np.zeros(n+1)
    for i in range(1, n+1):
        s_pts[i] = s_pts[i-1] + longu[i-1]
        x_pts[i] = x_pts[i-1] + longu[i-1] * np.cos(np.radians(angles[i-1]))
        y_pts[i] = y_pts[i-1] - longu[i-1] * np.sin(np.radians(angles[i-1]))

    snew  = np.linspace(0, s_pts[-1], Npoints)
    tck_x = interpolate.splrep(s_pts, x_pts, k=1, s=0)
    tck_y = interpolate.splrep(s_pts, y_pts, k=1, s=0)
    xnew  = interpolate.splev(snew, tck_x)
    ynew  = interpolate.splev(snew, tck_y)
    alpha = np.arctan2(interpolate.splev(snew, tck_y, der=1),
                       interpolate.splev(snew, tck_x, der=1))

    knew = np.zeros(Npoints)
    for i in range(Npoints):
        j = 0
        while j < n-1 and x_pts[j+1] < xnew[i]: j += 1
        knew[i] = frott[j]

    u = np.zeros(Npoints); v = np.zeros(Npoints)
    u[0] = (V0_kmh / 3.6) ** 2
    for i in range(Npoints-1):
        ds     = snew[i+1] - snew[i]
        u[i+1] = u[i] + ds * (2*g*(np.sin(-alpha[i]) - knew[i]*np.cos(-alpha[i]))
                               - (rho*S*Cx/masse)*u[i])
        v[i+1] = np.sqrt(max(u[i+1], 0))

    tnew = np.zeros(Npoints)
    for i in range(1, Npoints-1):
        if v[i] > 0 and v[i+1] > 0:
            tnew[i+1] = tnew[i] + 0.5*(snew[i+1]-snew[i])*(1/v[i+1]+1/v[i])
        else:
            tnew[i+1] = tnew[i]

    return {
        "snew": snew, "xnew": xnew, "ynew": ynew,
        "x_pts": x_pts, "y_pts": y_pts,
        "v": v*3.6, "tnew": tnew,
        "Vmax":     float(max(v)*3.6),
        "Vfin":     float(v[-2]*3.6),
        "duree":    float(max(tnew)),
        "denivele": float(y_pts[-1]),
        "distance": float(s_pts[-1]),
    }

# ════════════════════════════════════════════════════════════════
# PHYSIQUE — AIRBAG
# ════════════════════════════════════════════════════════════════
def traj_vitesse_connue(alpha_deg, V0_kmh, h0=0.0):
    a = np.radians(alpha_deg); V0 = V0_kmh / 3.6
    vx, vy = V0*np.cos(a), V0*np.sin(a)
    T = 2*vy/g; X = vx*T
    t = np.linspace(0, T, 400)
    return {"X": X, "T": T, "t": t,
            "xt": vx*t, "yt": h0 + vy*t - 0.5*g*t**2,
            "ymax": h0 + vy**2/(2*g)}

def traj_longueur_souhaitee(alpha_deg, H, X_cible, h_air=0.0):
    a = np.radians(alpha_deg)
    d = 2*np.cos(a)**2*(X_cible*np.tan(a) + H - h_air)
    if d <= 0: return None
    V0  = np.sqrt(g*X_cible**2/d)
    res = traj_vitesse_connue(alpha_deg, V0*3.6, H)
    res["V0_kmh"] = V0*3.6
    res["T"]      = X_cible / (V0*np.cos(a))
    return res

# ════════════════════════════════════════════════════════════════
# GRAPHIQUES
# ════════════════════════════════════════════════════════════════
BLEU_F  = "#1e3a5f"
BLEU_C  = "#3b82f6"
VERT    = "#166534"
MARRON  = "#92400e"
ROUGE   = "#dc2626"
ORANGE  = "#d97706"

def _style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_title(title, fontsize=12, fontweight="bold", color=BLEU_F, pad=10)
    ax.set_xlabel(xlabel, fontsize=10, color="#475569")
    ax.set_ylabel(ylabel, fontsize=10, color="#475569")
    ax.tick_params(labelsize=9, colors="#64748b")
    ax.grid(True, color="#e2e8f0", linewidth=0.6, linestyle="--", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.set_facecolor("#fafbfc")

def fig_profil(res, pas_m=5):
    fig, ax = plt.subplots(figsize=(13, 3.8)); fig.patch.set_facecolor("white")
    ax.plot(res["xnew"], res["ynew"], color=BLEU_C, lw=2.2, zorder=2, label="Piste")
    ax.fill_between(res["xnew"], res["ynew"], min(res["ynew"])-0.5,
                    alpha=0.08, color=BLEU_C, zorder=1)
    # Points tous les pas_m mètres (distance curviligne)
    snew = res["snew"]; Stot = snew[-1]; x5, y5 = [], []; s_c = 0.0
    while s_c <= Stot + 1e-6:
        idx = int(np.argmin(np.abs(snew - s_c)))
        x5.append(res["xnew"][idx]); y5.append(res["ynew"][idx]); s_c += pas_m
    ax.scatter(x5, y5, s=22, color=BLEU_C, edgecolors="white",
               linewidths=1.3, zorder=4, label=f"Point / {pas_m} m")
    ax.scatter(res["x_pts"], res["y_pts"], s=55, marker="^",
               color=ROUGE, zorder=5, label="Sections relevées")
    _style_ax(ax, "Profil de piste", "Distance horizontale (m)", "Altitude (m)")
    ax.legend(fontsize=9, framealpha=0.9, loc="upper right",
              facecolor="white", edgecolor="#e2e8f0")
    plt.tight_layout(); return fig

def fig_vitesse(res):
    fig, ax = plt.subplots(figsize=(13, 3.8)); fig.patch.set_facecolor("white")
    ax.plot(res["snew"], res["v"], color=VERT, lw=2.2, zorder=2)
    ax.fill_between(res["snew"], res["v"], alpha=0.08, color=VERT, zorder=1)
    ax.axhline(res["Vmax"], color=ROUGE,  lw=1.4, ls="--", alpha=0.85,
               label=f"Vmax = {res['Vmax']:.1f} km/h")
    ax.axhline(res["Vfin"], color=ORANGE, lw=1.4, ls=":",  alpha=0.85,
               label=f"Vfin = {res['Vfin']:.1f} km/h")
    _style_ax(ax, "Vitesse en fonction de la distance",
              "Distance curviligne (m)", "Vitesse (km/h)")
    ax.legend(fontsize=9, framealpha=0.9, facecolor="white", edgecolor="#e2e8f0")
    plt.tight_layout(); return fig

def fig_temps(res):
    mask = res["tnew"] > 0
    fig, ax = plt.subplots(figsize=(13, 3.8)); fig.patch.set_facecolor("white")
    ax.plot(res["snew"][mask], res["tnew"][mask], color=MARRON, lw=2.2, zorder=2)
    ax.fill_between(res["snew"][mask], res["tnew"][mask],
                    alpha=0.08, color=MARRON, zorder=1)
    ax.axhline(res["duree"], color=ROUGE, lw=1.4, ls="--", alpha=0.85,
               label=f"Durée totale = {res['duree']:.1f} s")
    _style_ax(ax, "Temps écoulé en fonction de la distance",
              "Distance curviligne (m)", "Temps (s)")
    ax.legend(fontsize=9, framealpha=0.9, facecolor="white", edgecolor="#e2e8f0")
    plt.tight_layout(); return fig

def fig_airbag(res, alpha_deg, h_air=None):
    fig, ax = plt.subplots(figsize=(13, 4.2)); fig.patch.set_facecolor("white")
    ax.plot(res["xt"], res["yt"], color=BLEU_C, lw=2.5, zorder=3,
            label=f"Trajectoire (α = {alpha_deg}°)")
    ax.fill_between(res["xt"], res["yt"], min(res["yt"])-0.2,
                    alpha=0.07, color=BLEU_C, zorder=1)
    i_max = int(np.argmax(res["yt"]))
    ax.scatter([res["xt"][i_max]], [res["yt"][i_max]], s=80, color=ORANGE, zorder=5,
               label=f"Hauteur max = {res['ymax']:.2f} m")
    ax.scatter([res["X"]], [res["yt"][-1]], s=80, color=ROUGE, marker="v", zorder=5,
               label=f"Portée X = {res['X']:.2f} m")
    if h_air and h_air > 0:
        rect = mpatches.FancyBboxPatch((res["X"]-0.5, 0), 1.5, h_air,
                                        boxstyle="round,pad=0.05", lw=1.5,
                                        edgecolor=VERT, facecolor="#dcfce7")
        ax.add_patch(rect)
        ax.text(res["X"]+0.3, h_air/2, "Airbag", color=VERT,
                fontsize=9, va="center", fontweight="600")
    ax.axhline(0, color="#94a3b8", lw=1)
    _style_ax(ax, "Trajectoire du saut", "Distance (m)", "Hauteur (m)")
    ax.set_xlim(-0.5, res["X"] * 1.18)
    ax.legend(fontsize=9, framealpha=0.9, facecolor="white", edgecolor="#e2e8f0")
    plt.tight_layout(); return fig

# ── Comparatif ───────────────────────────────────────────────────
def build_profile_xy(sections_cmp, N=600):
    n = len(sections_cmp)
    sP = np.zeros(n+1); xP = np.zeros(n+1); yP = np.zeros(n+1)
    for i in range(n):
        a = np.radians(sections_cmp[i]["angle"])
        l = sections_cmp[i]["longueur"]
        sP[i+1] = sP[i] + l
        xP[i+1] = xP[i] + l * np.cos(a)
        yP[i+1] = yP[i] - l * np.sin(a)
    s_new = np.linspace(0, sP[-1], N)
    tck_x = interpolate.splrep(sP, xP, k=1, s=0)
    tck_y = interpolate.splrep(sP, yP, k=1, s=0)
    return interpolate.splev(s_new, tck_x), interpolate.splev(s_new, tck_y)

def fig_comparatif(proj, terr):
    fig, axes = plt.subplots(2, 1, figsize=(13, 7.5))
    fig.patch.set_facecolor("white")
    Nmin = min(len(proj[0]), len(terr[0]))
    px, py = proj[0][:Nmin], proj[1][:Nmin]
    tx, ty = terr[0][:Nmin], terr[1][:Nmin]
    diff = py - ty

    ax = axes[0]
    ax.plot(px, py, color=BLEU_C, lw=2.5, label="Profil projet (souhaité)")
    ax.plot(tx, ty, color=VERT,   lw=2.5, ls="--", label="Relevé terrain (existant)")
    ax.fill_between(px, py, ty, where=(py >= ty),
                    alpha=0.15, color=BLEU_C, label="Remblai nécessaire")
    ax.fill_between(px, py, ty, where=(py < ty),
                    alpha=0.15, color=ROUGE,  label="Déblai nécessaire")
    _style_ax(ax, "Superposition des profils", "Distance horizontale (m)", "Altitude (m)")
    ax.legend(fontsize=9, framealpha=0.9, facecolor="white", edgecolor="#e2e8f0")

    ax = axes[1]
    ax.plot(px, diff, color=BLEU_C, lw=2)
    ax.fill_between(px, diff, 0, where=(diff >= 0),
                    alpha=0.20, color=BLEU_C, label="Remblai (+)")
    ax.fill_between(px, diff, 0, where=(diff < 0),
                    alpha=0.20, color=ROUGE,  label="Déblai (−)")
    ax.axhline(0, color="#94a3b8", lw=1, ls="--")
    _style_ax(ax, "Écart altimétrique projet − terrain",
           "Distance horizontale (m)", "Écart (m)")
    ax.legend(fontsize=9, framealpha=0.9, facecolor="white", edgecolor="#e2e8f0")
    plt.tight_layout()
    return fig

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Paramètres globaux")
    masse = st.slider("Masse (kg)", 40, 150, 80, 5,
                      help="Masse totale pratiquant + matériel")
    V0    = st.slider("V₀ initiale (km/h)", 0, 50, 0,
                      help="0 = départ arrêté")
    st.markdown("---")
    st.markdown("**Paramètres aérodynamiques**")
    Cx  = st.number_input("Cx", value=1.1, step=0.05, format="%.2f")
    S   = st.number_input("Surface frontale S (m²)", value=0.56, step=0.01, format="%.2f")
    rho = st.number_input("ρ air (kg/m³)", value=1.225, step=0.001, format="%.3f")
    st.markdown("---")
    pas_m = st.selectbox("Repères profil (m)", [1, 2, 5, 10, 20], index=2,
                         help="Espacement des points sur le graphique profil")
    st.markdown("---")

    # ── Convertisseur ° ↔ % ─────────────────────────────────────
    st.markdown("**🔄 Convertisseur pente**")
    conv_col1, conv_col2 = st.columns(2)
    with conv_col1:
        deg_in = st.number_input("Degrés (°)",
                                  value=0.0, step=0.1, format="%.1f",
                                  min_value=0.0, max_value=89.0,
                                  key="conv_deg",
                                  help="Saisissez un angle en degrés")
        if deg_in > 0:
            pct_out = np.tan(np.radians(deg_in)) * 100
            st.markdown(
                f"<div style='background:#dbeafe;border-radius:6px;padding:6px 10px;"
                f"text-align:center;font-size:13px;color:#1e3a5f;font-weight:600'>"
                f"→ {pct_out:.2f} %</div>",
                unsafe_allow_html=True)
    with conv_col2:
        pct_in = st.number_input("Pourcent (%)",
                                  value=0.0, step=0.5, format="%.1f",
                                  min_value=0.0, max_value=5000.0,
                                  key="conv_pct",
                                  help="Saisissez une pente en pourcentage")
        if pct_in > 0:
            deg_out = np.degrees(np.arctan(pct_in / 100))
            st.markdown(
                f"<div style='background:#dcfce7;border-radius:6px;padding:6px 10px;"
                f"text-align:center;font-size:13px;color:#166534;font-weight:600'>"
                f"→ {deg_out:.2f} °</div>",
                unsafe_allow_html=True)
    st.markdown("---")
    st.caption("**4 Experience** — Simulateur piste & airbag")

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
  <div>
    <h1>🏔️ Simulateur de piste &amp; Trajectoire Airbag</h1>
    <p>Calcul dynamique de vitesses, temps d'arrêt et trajectoires — 4 Experience</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# ONGLETS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "🏔️  Simulateur de piste",
    "🪂  Trajectoire Airbag",
    "📐  Profil comparatif",
])

# ────────────────────────────────────────────────────────────────
# ONGLET 1 — PISTE
# ────────────────────────────────────────────────────────────────
with tab1:

    DEFAULT = [
        {"nom":"Départ",     "angle":14.0,"longueur":5.35,  "cat":"❄️ Neige dure",   "var":"—","cond":"sec","mu_ovr":None},
        {"nom":"Schuss 1",   "angle":11.4,"longueur":56.68, "cat":"❄️ Neige normale", "var":"—","cond":"sec","mu_ovr":None},
        {"nom":"Transition", "angle":8.5, "longueur":5.22,  "cat":"❄️ Neige glacée",  "var":"—","cond":"sec","mu_ovr":None},
        {"nom":"Fin",        "angle":4.0, "longueur":7.17,  "cat":"🟩 Neveplast",     "var":"—","cond":"sec","mu_ovr":None},
    ]

    if "sections" not in st.session_state:
        st.session_state.sections = [s.copy() for s in DEFAULT]

    # Barre d'outils
    ca, cb, _ = st.columns([1, 1, 3])
    with ca:
        if st.button("➕ Ajouter section",
                     disabled=len(st.session_state.sections) >= 10,
                     use_container_width=True):
            c0 = CATS[0]; v0 = list(SURFACES_DB[c0].keys())[0]
            st.session_state.sections.append({
                "nom": f"Section {len(st.session_state.sections)+1}",
                "angle": 5.0, "longueur": 10.0,
                "cat": c0, "var": "—", "cond": "sec", "mu_ovr": None,
            })
            st.rerun()
    with cb:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.sections = [s.copy() for s in DEFAULT]
            st.rerun()

    st.caption(f"{len(st.session_state.sections)} section(s) — 10 max")

    # En-têtes
    hh = st.columns([0.22, 0.85, 0.6, 0.6, 1.6, 0.55, 0.7, 0.38])
    for col, txt in zip(hh, ["#","Nom","Angle °","Long. m",
                               "Surface","Cond.","μ final","×"]):
        col.markdown(
            f"<div style='font-size:10px;color:#94a3b8;text-transform:uppercase;"
            f"letter-spacing:.06em;padding-bottom:2px'>{txt}</div>",
            unsafe_allow_html=True)

    secs_new = []; del_idx = None

    for i, sec in enumerate(st.session_state.sections):
        cols = st.columns([0.22, 0.85, 0.6, 0.6, 1.6, 0.55, 0.7, 0.38])

        cols[0].markdown(
            f"<div style='text-align:center;padding-top:.45rem'>"
            f"<span style='background:#1e3a5f;color:white;border-radius:50%;"
            f"width:22px;height:22px;display:inline-flex;align-items:center;"
            f"justify-content:center;font-size:11px;font-weight:600'>{i+1}</span></div>",
            unsafe_allow_html=True)

        nom   = cols[1].text_input("n", value=sec["nom"], key=f"n{i}",
                                    label_visibility="collapsed")
        angle = cols[2].number_input("a", value=float(sec["angle"]), key=f"a{i}",
                                      label_visibility="collapsed",
                                      step=0.1, format="%.1f")
        longu = cols[3].number_input("l", value=float(sec["longueur"]), key=f"l{i}",
                                      label_visibility="collapsed",
                                      step=0.5, format="%.1f", min_value=0.1)

        cat_i = CATS.index(sec["cat"]) if sec["cat"] in CATS else 0
        cat   = cols[4].selectbox("c", CATS, index=cat_i, key=f"c{i}",
                                   label_visibility="collapsed")

        var = "—"

        cond  = cols[5].selectbox("cd", ["sec", "humide"],
                                   index=0 if sec["cond"] == "sec" else 1,
                                   key=f"cd{i}", label_visibility="collapsed",
                                   format_func=lambda x: "☀️ Sec" if x == "sec" else "🌧️ Hum.")

        mu_auto = get_mu(cat, var, cond)
        # La clé inclut cat+cond : quand la surface change, le widget
        # est recréé à neuf et s'initialise automatiquement à mu_auto.
        mu_key  = f"m{i}_{cat}_{cond}".replace(" ", "_").replace("️", "").replace("❄", "").replace("🟩", "").replace("🛝", "").replace("⛷", "")
        mu      = cols[6].number_input(
            "μ", value=float(mu_auto), key=mu_key,
            label_visibility="collapsed", step=0.001, format="%.3f",
            min_value=0.001, max_value=1.0,
            help=f"μ auto = {mu_auto:.3f} — modifiable librement")
        mu_ovr  = mu if abs(mu - mu_auto) > 1e-6 else None

        if cols[7].button("✕", key=f"d{i}",
                          disabled=len(st.session_state.sections) <= 1):
            del_idx = i

        secs_new.append({"nom": nom, "angle": angle, "longueur": longu,
                          "cat": cat, "var": var, "cond": cond,
                          "mu_ovr": mu_ovr, "frottement": mu})

    if del_idx is not None:
        st.session_state.sections.pop(del_idx); st.rerun()
    st.session_state.sections = secs_new

    # Récap μ
    recap = "  ·  ".join(
        f"**#{i+1} {s['nom']}** μ={s['frottement']:.3f}"
        + (" ✏️" if s["mu_ovr"] is not None else "")
        for i, s in enumerate(secs_new)
    )
    st.caption("Coefficients : " + recap)
    st.markdown("---")

    # Bouton simulation
    if st.button("▶  Lancer la simulation", type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            try:
                res = simuler_piste(secs_new, masse, V0, S, Cx, rho)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🚀 Vitesse max",    f"{res['Vmax']:.1f} km/h")
                c2.metric("🏁 Vitesse finale", f"{res['Vfin']:.1f} km/h")
                c3.metric("⏱ Durée totale",    f"{res['duree']:.1f} s")
                c4.metric("📐 Dénivelé",        f"{abs(res['denivele']):.1f} m")

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                for fn, lbl in [
                    (lambda r: fig_profil(r, pas_m), "📍 Profil de piste"),
                    (fig_vitesse, "📈 Vitesse / distance"),
                    (fig_temps,   "⏱ Temps écoulé / distance"),
                ]:
                    st.markdown(f"<div class='section-title'>{lbl}</div>",
                                unsafe_allow_html=True)
                    f = fn(res)
                    st.pyplot(f, use_container_width=True)
                    plt.close(f)

                st.markdown("---")
                df = pd.DataFrame({
                    "t (s)":    res["tnew"][1:-1],
                    "s (m)":    res["snew"][1:-1],
                    "v (km/h)": res["v"][1:-1],
                })
                buf = io.StringIO()
                df.to_csv(buf, index=False, sep=";", decimal=",")
                st.download_button(
                    "📥 Télécharger les résultats (CSV)",
                    buf.getvalue(),
                    file_name="simulation_piste_4experience.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Erreur de calcul : {e}")
                st.info("Vérifiez que les angles et longueurs de sections sont cohérents.")

# ────────────────────────────────────────────────────────────────
# ONGLET 2 — AIRBAG
# ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🪂 Calcul de trajectoire — Piste Airbag")

    mode = st.radio(
        "Mode de calcul",
        ["🎯  Vitesse connue → calcul du saut",
         "📏  Longueur souhaitée → vitesse nécessaire"],
        horizontal=True,
    )
    st.markdown("---")

    if "connue" in mode:
        c1, c2, c3 = st.columns(3)
        alpha_deg = c1.slider("Angle de sortie α (°)", 5, 85, 30)
        V0_air    = c2.slider("Vitesse V₀ (km/h)", 1, 120, 20)
        h_init    = c3.number_input("Hauteur initiale (m)", value=0.0,
                                     step=0.1, format="%.1f",
                                     help="Hauteur du point de départ par rapport à la réception")

        if st.button("▶  Calculer la trajectoire", type="primary",
                     use_container_width=True):
            res = traj_vitesse_connue(alpha_deg, V0_air, h_init)
            c1, c2, c3 = st.columns(3)
            c1.metric("📏 Portée X",       f"{res['X']:.2f} m")
            c2.metric("⏱ Temps en l'air",  f"{res['T']:.2f} s")
            c3.metric("🔝 Hauteur max",    f"{res['ymax']:.2f} m")
            f = fig_airbag(res, alpha_deg)
            st.pyplot(f, use_container_width=True); plt.close(f)

    else:
        c1, c2, c3, c4 = st.columns(4)
        H_tremplin = c1.number_input("Hauteur tremplin H (m)", value=2.0,
                                      step=0.1, format="%.1f")
        X_cible    = c2.number_input("Longueur souhaitée (m)", value=6.65,
                                      step=0.05, format="%.2f")
        alpha_deg  = c3.slider("Angle de sortie α (°)", 5, 85, 55)
        h_airbag   = c4.number_input("Hauteur airbag (m)", value=0.252,
                                      step=0.01, format="%.3f")

        if st.button("▶  Calculer la vitesse nécessaire", type="primary",
                     use_container_width=True):
            res = traj_longueur_souhaitee(alpha_deg, H_tremplin, X_cible, h_airbag)
            if res is None:
                st.error("Paramètres incohérents — vérifiez l'angle et les hauteurs.")
            else:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("⚡ V₀ nécessaire",  f"{res['V0_kmh']:.1f} km/h")
                c2.metric("📏 Portée X",        f"{res['X']:.2f} m")
                c3.metric("⏱ Temps en l'air",  f"{res['T']:.2f} s")
                c4.metric("🔝 Hauteur max",     f"{res['ymax']:.2f} m")
                f = fig_airbag(res, alpha_deg, h_airbag)
                st.pyplot(f, use_container_width=True); plt.close(f)
                st.markdown(
                    f"<div class='info-box'>💡 Pour atteindre <b>{res['V0_kmh']:.1f} km/h</b> "
                    f"en bout de piste, ajustez vos sections dans l'onglet "
                    f"<b>Simulateur de piste</b> jusqu'à obtenir cette vitesse finale.</div>",
                    unsafe_allow_html=True,
                )

# ════════════════════════════════════════════════════════════════
# ONGLET 3 — PROFIL COMPARATIF
# ════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div style='font-size:13px;color:#475569;margin-bottom:14px;line-height:1.7'>
    Saisissez le <b>profil projet</b> (ce que vous souhaitez construire) et le <b>relevé terrain</b>
    (mesures sur site). Le graphique superpose les deux profils et met en évidence les zones de
    <span style='color:#1e40af'>remblai</span> et de <span style='color:#dc2626'>déblai</span>.
    </div>""", unsafe_allow_html=True)

    DEFAULT_PROJ = [
        {"nom":"S1","angle":12.0,"longueur":30.0},
        {"nom":"S2","angle": 8.0,"longueur":40.0},
        {"nom":"S3","angle": 4.0,"longueur":20.0},
        {"nom":"S4","angle": 2.0,"longueur":10.0},
    ]
    DEFAULT_TERR = [
        {"nom":"T1","angle":14.0,"longueur":25.0},
        {"nom":"T2","angle": 6.0,"longueur":35.0},
        {"nom":"T3","angle": 5.5,"longueur":25.0},
        {"nom":"T4","angle": 1.0,"longueur":15.0},
    ]

    if "cmp_proj" not in st.session_state:
        st.session_state.cmp_proj = [s.copy() for s in DEFAULT_PROJ]
    if "cmp_terr" not in st.session_state:
        st.session_state.cmp_terr = [s.copy() for s in DEFAULT_TERR]

    def render_cmp_table(key, label, color):
        data = st.session_state[f"cmp_{key}"]
        st.markdown(f"<div style='font-size:12px;font-weight:600;color:{color};"
                    f"margin-bottom:6px'>{label}</div>", unsafe_allow_html=True)
        hh2 = st.columns([0.2, 0.8, 0.7, 0.7, 0.4])
        for col, txt in zip(hh2, ["#","Nom","Angle °","Long. m","×"]):
            col.markdown(f"<div style='font-size:10px;color:#94a3b8;"
                         f"text-transform:uppercase'>{txt}</div>",
                         unsafe_allow_html=True)
        del_i = None
        new_data = []
        for i, s in enumerate(data):
            c = st.columns([0.2, 0.8, 0.7, 0.7, 0.4])
            c[0].markdown(
                f"<div style='text-align:center;padding-top:.4rem;"
                f"font-size:11px;color:#94a3b8'>{i+1}</div>",
                unsafe_allow_html=True)
            nom = c[1].text_input("n", value=s["nom"],
                                   key=f"{key}_n{i}", label_visibility="collapsed")
            ang = c[2].number_input("a", value=float(s["angle"]),
                                     key=f"{key}_a{i}", label_visibility="collapsed",
                                     step=0.1, format="%.1f")
            lon = c[3].number_input("l", value=float(s["longueur"]),
                                     key=f"{key}_l{i}", label_visibility="collapsed",
                                     step=1.0, format="%.1f", min_value=0.1)
            if c[4].button("✕", key=f"{key}_d{i}", disabled=len(data) <= 1):
                del_i = i
            new_data.append({"nom": nom, "angle": ang, "longueur": lon})
        st.session_state[f"cmp_{key}"] = new_data
        if del_i is not None:
            st.session_state[f"cmp_{key}"].pop(del_i)
            st.rerun()
        ca2, cb2 = st.columns(2)
        with ca2:
            if st.button("➕ Ajouter", key=f"{key}_add", use_container_width=True):
                st.session_state[f"cmp_{key}"].append(
                    {"nom": f"S{len(st.session_state[f'cmp_{key}'])+1}",
                     "angle": 5.0, "longueur": 10.0})
                st.rerun()
        with cb2:
            if st.button("🔄 Exemple", key=f"{key}_rst", use_container_width=True):
                st.session_state[f"cmp_{key}"] = [
                    s.copy() for s in
                    (DEFAULT_PROJ if key == "proj" else DEFAULT_TERR)]
                st.rerun()
        return st.session_state[f"cmp_{key}"]

    col_p, col_t = st.columns(2)
    with col_p:
        proj_secs = render_cmp_table("proj", "🔵  Profil projet (souhaité)", "#1e40af")
    with col_t:
        terr_secs = render_cmp_table("terr", "🟢  Relevé terrain (existant)", "#166534")

    st.markdown("---")
    if st.button("▶  Générer le profil comparatif", type="primary",
                 use_container_width=True):
        with st.spinner("Calcul..."):
            try:
                proj_xy = build_profile_xy(proj_secs)
                terr_xy = build_profile_xy(terr_secs)
                Nmin    = min(len(proj_xy[0]), len(terr_xy[0]))
                diff    = proj_xy[1][:Nmin] - terr_xy[1][:Nmin]
                remblai   = float(np.sum(diff[diff > 0]))
                deblai    = float(np.sum(np.abs(diff[diff < 0])))
                ecart_max = float(np.max(np.abs(diff)))

                c1, c2, c3 = st.columns(3)
                c1.metric("📏 Écart max",      f"{ecart_max:.2f} m")
                c2.metric("⬆️ Remblai cumulé", f"{remblai:.1f} m·pts")
                c3.metric("⬇️ Déblai cumulé",  f"{deblai:.1f} m·pts")

                f = fig_comparatif(proj_xy, terr_xy)
                st.pyplot(f, use_container_width=True)
                plt.close(f)
            except Exception as e:
                st.error(f"Erreur : {e}")
