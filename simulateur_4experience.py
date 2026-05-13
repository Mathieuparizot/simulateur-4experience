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
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import interpolate
import pandas as pd
import streamlit as st
import io
from datetime import date
from matplotlib.backends.backend_pdf import PdfPages
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

# ── Couleurs PDF rapport (orange 4 Experience) ───────────────────
PDF_ORANGE_F = "#C14B00"   # orange foncé — bandeau, titres
PDF_ORANGE_M = "#F97316"   # orange moyen — accents, traits
PDF_ORANGE_C = "#FFEDD5"   # orange très clair — fonds
PDF_ORANGE_T = "#FED7AA"   # orange clair — en-têtes tableaux

# ── Logo 4 Experience (PNG embarqué en base64) ──────────────────
LOGO_B64 = "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"

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
# GÉNÉRATION PDF
# ════════════════════════════════════════════════════════════════
def _get_logo_rgb_on_orange():
    """Retourne le logo blanc composité sur fond orange — sans déformation."""
    import base64 as _b64, io as _io
    from PIL import Image as _PIL
    raw      = _b64.b64decode(LOGO_B64)
    img_rgba = _PIL.open(_io.BytesIO(raw)).convert("RGBA")
    arr      = np.array(img_rgba).astype(float)
    alpha_n  = arr[:, :, 3] / 255.0            # 0 = fond, 1 = logo
    orange   = np.array([193, 75, 0], dtype=float)   # PDF_ORANGE_F #C14B00
    out      = np.zeros((*arr.shape[:2], 3), dtype=np.uint8)
    for c in range(3):
        out[:, :, c] = (alpha_n * 255 + (1 - alpha_n) * orange[c]).clip(0, 255)
    return out


def _rect(fig, left, bottom, width, height, color):
    """Dessine un rectangle coloré directement sur la figure."""
    import matplotlib.patches as _mp
    fig.add_artist(_mp.FancyBboxPatch(
        (left, bottom), width, height,
        boxstyle="square,pad=0", transform=fig.transFigure,
        facecolor=color, edgecolor="none", zorder=0, clip_on=False
    ))


def fig_cover(projet, reference, date_str, notes, params_piste, params_air):
    """Page de garde A4 Portrait — orange 4 Experience + logo."""
    fig = plt.figure(figsize=(A4W, A4H))
    fig.patch.set_facecolor("white")

    # Bandeau haut 20%
    _rect(fig, 0, 0.80, 1.0, 0.20, PDF_ORANGE_F)
    _rect(fig, 0, 0.792, 1.0, 0.010, PDF_ORANGE_M)

    # Logo — ratio 4:1 adapté portrait, -25%
    _lw = 0.50 * 0.75; _lh = _lw * A4W / (4.0 * A4H)
    _lb = 0.80 + (0.20 - _lh) / 2.0
    try:
        _logo = _get_logo_rgb_on_orange()
        ax_l  = fig.add_axes([0.04, _lb, _lw, _lh])
        ax_l.axis("off"); ax_l.set_zorder(5)
        ax_l.imshow(_logo, aspect="auto",
                    interpolation="lanczos", zorder=5)
    except Exception:
        pass

    # Titre à droite dans le bandeau
    ax_t = fig.add_axes([0.04, 0.80, 0.92, 0.195])
    ax_t.set_facecolor(PDF_ORANGE_F); ax_t.set_zorder(2)
    ax_t.axis("off"); ax_t.patch.set_visible(True)
    ax_t.text(0.98, 0.72, "Rapport de simulation",
              fontsize=16, fontweight="bold", color="white",
              va="center", ha="right", transform=ax_t.transAxes)
    ax_t.text(0.98, 0.30, "Piste de glisse  &  Trajectoire Airbag",
              fontsize=10, color="#ffe0c0",
              va="center", ha="right", transform=ax_t.transAxes)

    # Infos projet
    ax_i = fig.add_axes([0.07, 0.57, 0.86, 0.21])
    ax_i.axis("off")
    infos = [("Projet",    projet    or "—"),
             ("Référence", reference or "—"),
             ("Date",      date_str),
             ("Notes",     notes     or "—")]
    for k, (lbl, val) in enumerate(infos):
        y = 0.93 - k * 0.25
        ax_i.text(0.00, y, lbl + " :", fontsize=11, fontweight="bold",
                  color=PDF_ORANGE_F, va="center")
        ax_i.text(0.25, y, str(val), fontsize=11,
                  color="#1e293b", va="center")
        ax_i.axhline(y - 0.10, color="#e2e8f0", lw=0.7)

    # Tableaux paramètres
    def _tbl(ax_pos, title, rows_dict):
        ax = fig.add_axes(ax_pos); ax.axis("off")
        ax.text(0, 1.04, title, fontsize=10, fontweight="bold",
                color=PDF_ORANGE_F, transform=ax.transAxes)
        rows = [[k, v] for k, v in rows_dict.items()]
        t = ax.table(cellText=rows, colLabels=["Paramètre", "Valeur"],
                     cellLoc="left", loc="upper left",
                     colWidths=[0.60, 0.40])
        t.auto_set_font_size(False); t.set_fontsize(8)
        for (r, c), cell in t.get_celld().items():
            cell.set_edgecolor("#e2e8f0")
            if r == 0:
                cell.set_facecolor(PDF_ORANGE_T)
                cell.set_text_props(fontweight="bold", color=PDF_ORANGE_F)
            else:
                cell.set_facecolor("white" if r % 2 else "#fff8f5")

    if params_piste and params_air:
        _tbl([0.07, 0.28, 0.42, 0.27], "Paramètres piste",  params_piste)
        _tbl([0.53, 0.28, 0.40, 0.27], "Paramètres airbag", params_air)
    elif params_piste:
        _tbl([0.07, 0.28, 0.86, 0.27], "Paramètres piste",  params_piste)
    elif params_air:
        _tbl([0.07, 0.28, 0.86, 0.27], "Paramètres airbag", params_air)

    # Pied de page
    _rect(fig, 0, 0, 1.0, 0.055, "#fff8f5")
    _rect(fig, 0, 0.053, 1.0, 0.003, PDF_ORANGE_M)
    ax_f = fig.add_axes([0, 0, 1, 0.053])
    ax_f.set_facecolor("#fff8f5"); ax_f.axis("off")
    ax_f.text(0.5, 0.45,
              "4 Experience  |  Document généré automatiquement  |  " + date_str,
              fontsize=8, color="#92400e", ha="center", va="center")
    return fig


def fig_sections_table(sections):
    """Tableau récapitulatif des sections de piste."""
    fig, ax = plt.subplots(figsize=(13, max(3.5, 1 + len(sections) * 0.45)))
    fig.patch.set_facecolor("white"); ax.axis("off")
    ax.set_title("Sections de piste", fontsize=12, fontweight="bold",
                 color=BLEU_F, pad=12, fontfamily="Arial")
    headers = ["#", "Nom", "Angle (°)", "Longueur (m)", "Surface", "Condition", "μ"]
    rows = [[str(i+1), s["nom"], f"{s['angle']:.1f}°",
             f"{s['longueur']:.1f} m", s["cat"].replace("❄️","").replace("🟩","").replace("🛝","").replace("⛷️","").strip(),
             "Sec ☀️" if s["cond"]=="sec" else "Humide 🌧️",
             f"{s['frottement']:.3f}"] for i, s in enumerate(sections)]
    tbl = ax.table(cellText=rows, colLabels=headers,
                   cellLoc="center", loc="upper center",
                   colWidths=[0.04,0.18,0.10,0.12,0.25,0.12,0.08])
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#e2e8f0")
        if r == 0:
            cell.set_facecolor(BLEU_C)
            cell.set_text_props(fontweight="bold", color=BLEU_F)
        else:
            cell.set_facecolor("white" if r % 2 else "#f8fafc")
    plt.tight_layout(); return fig



# ── Format A4 Portrait ────────────────────────────────────────────
A4W, A4H = 8.27, 11.69   # pouces, Portrait A4


def fig_page_portrait(chart_fig, titre_page, date_str, page_num):
    """Page A4 portrait avec en-tête/pied orange et graphique adapté."""
    fig = plt.figure(figsize=(A4W, A4H))
    fig.patch.set_facecolor("white")

    # En-tête orange
    _rect(fig, 0, 0.925, 1.0, 0.075, PDF_ORANGE_F)
    _rect(fig, 0, 0.917, 1.0, 0.008, PDF_ORANGE_M)

    # Logo dans en-tête
    _lw2 = 0.22; _lh2 = _lw2 * A4W / (4.0 * A4H)
    _lb2 = 0.925 + (0.075 - _lh2) / 2.0
    try:
        _logo2 = _get_logo_rgb_on_orange()
        ax_l2  = fig.add_axes([0.04, _lb2, _lw2, _lh2])
        ax_l2.axis("off"); ax_l2.set_zorder(5)
        ax_l2.imshow(_logo2, aspect="auto",
                     interpolation="lanczos", zorder=5)
    except Exception:
        pass

    ax_h = fig.add_axes([0.04, 0.925, 0.92, 0.072])
    ax_h.set_facecolor(PDF_ORANGE_F); ax_h.axis("off")
    ax_h.patch.set_visible(True)
    ax_h.text(0.98, 0.58, titre_page, fontsize=11, fontweight="bold",
              color="white", va="center", ha="right",
              transform=ax_h.transAxes)
    ax_h.text(0.98, 0.18, date_str, fontsize=8, color="#ffe0c0",
              va="center", ha="right", transform=ax_h.transAxes)

    # Redimensionner le graphique pour ratio portrait-friendly (1.5:1)
    try:
        chart_fig.set_size_inches(7.5, 5.0, forward=True)
        chart_fig.tight_layout()
    except Exception:
        pass

    # Rendre le graphique en PNG haute résolution
    from PIL import Image as _PILi
    buf_c = io.BytesIO()
    chart_fig.savefig(buf_c, format="png", dpi=200,
                       bbox_inches="tight", facecolor="white",
                       pad_inches=0.2)
    buf_c.seek(0)
    chart_img = np.array(_PILi.open(buf_c))
    img_h_px, img_w_px = chart_img.shape[:2]
    img_aspect = img_w_px / img_h_px

    # Zone disponible (entre en-tête à 0.92 et pied à 0.07)
    avail_top   = 0.91
    avail_bot   = 0.10
    avail_left  = 0.04
    avail_right = 0.96
    avail_h_in  = (avail_top - avail_bot) * A4H   # ≈ 9.5 in
    avail_w_in  = (avail_right - avail_left) * A4W  # ≈ 7.6 in

    # Ajuster aux dimensions du graphique en préservant l'aspect
    if avail_w_in / avail_h_in > img_aspect:
        # Hauteur limitante
        h_in = avail_h_in
        w_in = h_in * img_aspect
    else:
        # Largeur limitante
        w_in = avail_w_in
        h_in = w_in / img_aspect

    h_frac = h_in / A4H
    w_frac = w_in / A4W
    left   = (1.0 - w_frac) / 2.0
    bot    = avail_bot + (avail_top - avail_bot - h_frac) / 2.0

    ax_chart = fig.add_axes([left, bot, w_frac, h_frac])
    ax_chart.axis("off")
    ax_chart.imshow(chart_img, aspect="auto", interpolation="lanczos")

    # Pied de page
    _rect(fig, 0, 0, 1.0, 0.055, "#fff8f5")
    _rect(fig, 0, 0.053, 1.0, 0.003, PDF_ORANGE_M)
    ax_f = fig.add_axes([0, 0, 1, 0.053])
    ax_f.set_facecolor("#fff8f5"); ax_f.axis("off")
    ax_f.text(0.05, 0.45, "4 Experience  |  Simulateur piste & airbag",
              fontsize=8, color="#92400e", va="center")
    ax_f.text(0.95, 0.45, f"Page {page_num}",
              fontsize=8, color="#92400e", va="center", ha="right")
    return fig

def generate_pdf(config, state):
    """Génère le PDF A4 Portrait complet et retourne les bytes."""
    buf      = io.BytesIO()
    date_str = date.today().strftime("%d/%m/%Y")
    page_num = [2]   # compteur de pages (couverture = 1)

    def _add_chart(pdf, chart_fig, titre):
        pg = fig_page_portrait(chart_fig, titre, date_str, page_num[0])
        pdf.savefig(pg, bbox_inches="tight")
        plt.close(pg); page_num[0] += 1

    # Paramètres à afficher en couverture
    params_piste = None; params_air = None
    if state.get("piste_res") and config.get("inc_params"):
        r = state["piste_res"]
        params_piste = {
            "Masse":         f"{state['masse']} kg",
            "V₀ initiale":   f"{state['V0']} km/h",
            "Vitesse max":   f"{r['Vmax']:.1f} km/h",
            "Vitesse finale":f"{r['Vfin']:.1f} km/h",
            "Durée totale":  f"{r['duree']:.1f} s",
            "Dénivelé":      f"{abs(r['denivele']):.1f} m",
            "Distance":      f"{r['distance']:.0f} m",
        }
    if state.get("airbag_res") and config.get("inc_params"):
        r = state["airbag_res"]
        params_air = {
            "α sortie tremplin": f"{ALPHA_EXIT_DEG:.0f}°",
            "H tremplin":        f"{TREMPLIN_H:.2f} m",
            "Portée X":          f"{r['X']:.2f} m",
            "Temps en l'air":    f"{r['T']:.2f} s",
            "Hauteur max":       f"{r['ymax']:.2f} m",
        }
        if "V0_kmh" in r:
            params_air["V₀ nécessaire"] = f"{r['V0_kmh']:.1f} km/h"

    with PdfPages(buf) as pdf:
        d = pdf.infodict()
        d["Title"]   = f"4 Experience — {config['projet'] or 'Rapport de simulation'}"
        d["Author"]  = "4 Experience"
        d["Subject"] = "Simulation piste & airbag"

        # Page de couverture
        fig = fig_cover(config["projet"], config["reference"],
                        date_str, config["notes"], params_piste, params_air)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

        # Tableau sections
        if config.get("inc_sections") and state.get("sections"):
            fig = fig_sections_table(state["sections"])
            pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

        # Graphiques piste
        if state.get("piste_res"):
            r = state["piste_res"]
            pm = state.get("pas_m", 5)
            if config.get("inc_profil"):
                f = fig_profil(r, pm)
                _add_chart(pdf, f, "Profil de piste"); plt.close(f)
            if config.get("inc_vitesse"):
                f = fig_vitesse(r)
                _add_chart(pdf, f, "Vitesse en fonction de la distance"); plt.close(f)
            if config.get("inc_temps"):
                f = fig_temps(r)
                _add_chart(pdf, f, "Temps écoulé / distance"); plt.close(f)

        # Graphique airbag
        if config.get("inc_airbag") and state.get("airbag_res"):
            r   = state["airbag_res"]
            a   = state.get("airbag_alpha", ALPHA_EXIT_DEG)
            H   = state.get("airbag_H",     TREMPLIN_H)
            h   = state.get("airbag_hair",  None)
            m2  = state.get("airbag_mode2", False)
            f = fig_airbag(r, a, H, h, m2)
            _add_chart(pdf, f, "Trajectoire airbag"); plt.close(f)

        # Graphique comparatif
        if config.get("inc_cmp") and state.get("cmp_res"):
            f = fig_comparatif(state["cmp_res"][0], state["cmp_res"][1])
            _add_chart(pdf, f, "Profil comparatif"); plt.close(f)

        # Pied de page numérotation
        for i, fig_n in enumerate(pdf._file._pages):
            pass   # numérotation gérée par matplotlib

    buf.seek(0)
    return buf.read()

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
tab1, tab2, tab3, tab4 = st.tabs([
    "🏔️  Simulateur de piste",
    "🪂  Trajectoire Airbag",
    "📐  Profil comparatif",
    "📄  Rapport PDF",
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
                st.session_state["rpt_piste_res"]    = res
                st.session_state["rpt_piste_secs"]   = secs_new
                st.session_state["rpt_piste_params"] = {
                    "masse": masse, "V0": V0, "S": S, "Cx": Cx,
                    "rho": rho, "pas_m": pas_m,
                }

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
            st.session_state["rpt_airbag_res"]    = res
            st.session_state["rpt_airbag_alpha"]  = alpha_deg
            st.session_state["rpt_airbag_hair"]   = None
            st.session_state["rpt_airbag_mode"]   = "Vitesse connue"
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
                st.session_state["rpt_airbag_res"]    = res
                st.session_state["rpt_airbag_alpha"]  = alpha_deg
                st.session_state["rpt_airbag_hair"]   = h_airbag
                st.session_state["rpt_airbag_mode"]   = "Longueur souhaitée"
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
                st.session_state["cmp_res"] = (proj_xy, terr_xy)
                Nmin    = min(len(proj_xy[0]), len(terr_xy[0]))
                diff    = proj_xy[1][:Nmin] - terr_xy[1][:Nmin]
                remblai   = float(np.sum(diff[diff > 0]))
                deblai    = float(np.sum(np.abs(diff[diff < 0])))
                ecart_max = float(np.max(np.abs(diff)))
                st.session_state["rpt_cmp_proj"]  = proj_xy
                st.session_state["rpt_cmp_terr"]  = terr_xy
                st.session_state["rpt_cmp_stats"] = {
                    "ecart_max": ecart_max,
                    "remblai": remblai,
                    "deblai": deblai,
                }

                c1, c2, c3 = st.columns(3)
                c1.metric("📏 Écart max",      f"{ecart_max:.2f} m")
                c2.metric("⬆️ Remblai cumulé", f"{remblai:.1f} m·pts")
                c3.metric("⬇️ Déblai cumulé",  f"{deblai:.1f} m·pts")

                f = fig_comparatif(proj_xy, terr_xy)
                st.pyplot(f, use_container_width=True)
                plt.close(f)
            except Exception as e:
                st.error(f"Erreur : {e}")

# ════════════════════════════════════════════════════════════════
# ONGLET 4 — RAPPORT PDF
# ════════════════════════════════════════════════════════════════
with tab4:

    # ── Fonctions PDF ─────────────────────────────────────────────
    def pdf_page_garde(titre, projet, site, date_str, operateur, notes):
        """Délègue à fig_cover — couleurs orange 4 Experience + logo."""
        params_info = {}
        if projet:    params_info["Projet"]    = projet
        if site:      params_info["Site/Lieu"] = site
        if operateur: params_info["Opérateur"] = operateur
        return fig_cover(
            projet   = titre or "RAPPORT DE SIMULATION",
            reference= projet or "",
            date_str = date_str,
            notes    = notes,
            params_piste = params_info if params_info else None,
            params_air   = None,
        )

    def pdf_page_params(secs, params):
        """Page paramètres + sections en A4 portrait natif."""
        fig = plt.figure(figsize=(A4W, A4H))
        fig.patch.set_facecolor("white")

        # En-tête orange
        _rect(fig, 0, 0.925, 1.0, 0.075, PDF_ORANGE_F)
        _rect(fig, 0, 0.917, 1.0, 0.008, PDF_ORANGE_M)

        # Logo
        _lw3 = 0.22; _lh3 = _lw3 * A4W / (4.0 * A4H)
        _lb3 = 0.925 + (0.075 - _lh3) / 2.0
        try:
            _logo3 = _get_logo_rgb_on_orange()
            ax_l3 = fig.add_axes([0.04, _lb3, _lw3, _lh3])
            ax_l3.axis("off"); ax_l3.set_zorder(5)
            ax_l3.imshow(_logo3, aspect="auto",
                          interpolation="lanczos", zorder=5)
        except Exception:
            pass

        ax_h = fig.add_axes([0.04, 0.925, 0.92, 0.072])
        ax_h.set_facecolor(PDF_ORANGE_F); ax_h.axis("off")
        ax_h.patch.set_visible(True)
        ax_h.text(0.98, 0.55, "Paramètres & sections de piste",
                  fontsize=11, fontweight="bold", color="white",
                  va="center", ha="right", transform=ax_h.transAxes)

        # Bloc paramètres globaux
        ax_g = fig.add_axes([0.07, 0.74, 0.86, 0.15])
        ax_g.axis("off")
        ax_g.text(0, 1.0, "Paramètres globaux", fontsize=11,
                  fontweight="bold", color=PDF_ORANGE_F,
                  transform=ax_g.transAxes)
        p = params
        rows_g = [
            ["Masse",                 f"{p['masse']} kg"],
            ["Vitesse initiale V₀",   f"{p['V0']} km/h"],
            ["Cx",                    f"{p['Cx']:.2f}"],
            ["Surface frontale S",    f"{p['S']:.2f} m²"],
            ["Masse vol. air ρ",      f"{p['rho']:.3f} kg/m³"],
        ]
        tbl_g = ax_g.table(cellText=rows_g, colLabels=["Paramètre","Valeur"],
                           cellLoc="left", loc="upper left",
                           colWidths=[0.55, 0.45])
        tbl_g.auto_set_font_size(False); tbl_g.set_fontsize(9)
        tbl_g.scale(1, 1.3)
        for (r, c), cell in tbl_g.get_celld().items():
            cell.set_edgecolor("#e2e8f0")
            if r == 0:
                cell.set_facecolor(PDF_ORANGE_T)
                cell.set_text_props(fontweight="bold", color=PDF_ORANGE_F)
            else:
                cell.set_facecolor("white" if r % 2 else "#fff8f5")

        # Tableau sections
        ax_s = fig.add_axes([0.07, 0.10, 0.86, 0.58])
        ax_s.axis("off")
        ax_s.text(0, 1.0, "Sections de piste", fontsize=11,
                  fontweight="bold", color=PDF_ORANGE_F,
                  transform=ax_s.transAxes)
        rows_s = [[str(i+1), s["nom"], f"{s['angle']:.1f}°",
                    f"{s['longueur']:.1f} m",
                    s["cat"].replace("❄️ ","").replace("🟩 ","")
                            .replace("🛝 ","").replace("⛷️ ","").strip(),
                    "Sec" if s["cond"]=="sec" else "Humide",
                    f"{s['frottement']:.3f}"]
                   for i, s in enumerate(secs)]
        tbl_s = ax_s.table(cellText=rows_s,
                           colLabels=["#","Nom","Angle","Longueur",
                                       "Surface","Cond.","μ"],
                           cellLoc="center", loc="upper left",
                           colWidths=[0.05,0.20,0.10,0.13,0.27,0.13,0.10])
        tbl_s.auto_set_font_size(False); tbl_s.set_fontsize(9)
        tbl_s.scale(1, 1.4)
        for (r, c), cell in tbl_s.get_celld().items():
            cell.set_edgecolor("#e2e8f0")
            if r == 0:
                cell.set_facecolor(PDF_ORANGE_T)
                cell.set_text_props(fontweight="bold", color=PDF_ORANGE_F)
            else:
                cell.set_facecolor("white" if r % 2 else "#fff8f5")

        # Pied de page
        _rect(fig, 0, 0, 1.0, 0.055, "#fff8f5")
        _rect(fig, 0, 0.053, 1.0, 0.003, PDF_ORANGE_M)
        ax_f = fig.add_axes([0, 0, 1, 0.053])
        ax_f.set_facecolor("#fff8f5"); ax_f.axis("off")
        ax_f.text(0.5, 0.45, "4 Experience  |  Paramètres",
                  fontsize=8, color="#92400e", ha="center", va="center")
        return fig


    def add_footer(fig, txt="4 Experience — Rapport de simulation"):
        fig.text(0.5, 0.01, txt, ha="center", va="bottom",
                 fontsize=7, color="#94A3B8", fontfamily="Arial")

    def generer_pdf(titre, projet, site, date_str, operateur, notes,
                    incl_garde, incl_params, incl_profil, incl_vitesse,
                    incl_temps, incl_airbag, incl_cmp):
        """Génère le PDF entièrement en A4 Portrait."""
        buf      = io.BytesIO()
        page_num = [2]

        def _add(pdf, chart_fig, titre_pg):
            pg = fig_page_portrait(chart_fig, titre_pg, date_str, page_num[0])
            pdf.savefig(pg, bbox_inches="tight")
            plt.close(pg); page_num[0] += 1

        with PdfPages(buf) as pdf:

            # Page de garde
            if incl_garde:
                fig = pdf_page_garde(titre, projet, site, date_str, operateur, notes)
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

            # Page paramètres + sections
            piste_res    = st.session_state.get("rpt_piste_res")
            piste_secs   = st.session_state.get("rpt_piste_secs")
            piste_params = st.session_state.get("rpt_piste_params", {})

            if incl_params and piste_secs and piste_params:
                fig = pdf_page_params(piste_secs, piste_params)
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig); page_num[0] += 1

            # Graphiques piste
            if piste_res:
                pm = piste_params.get("pas_m", 5)
                if incl_profil:
                    fig = fig_profil(piste_res, pm)
                    _add(pdf, fig, "Profil de piste")
                    plt.close(fig)
                if incl_vitesse:
                    fig = fig_vitesse(piste_res)
                    _add(pdf, fig, "Vitesse en fonction de la distance")
                    plt.close(fig)
                if incl_temps:
                    fig = fig_temps(piste_res)
                    _add(pdf, fig, "Temps écoulé / distance")
                    plt.close(fig)

            # Trajectoire airbag
            if incl_airbag:
                ab_res   = st.session_state.get("rpt_airbag_res")
                ab_alpha = st.session_state.get("rpt_airbag_alpha", 45)
                ab_hair  = st.session_state.get("rpt_airbag_hair")
                if ab_res:
                    fig = fig_airbag(ab_res, ab_alpha, TREMPLIN_H, ab_hair,
                                     mode2=(ab_hair is not None))
                    _add(pdf, fig, "Trajectoire airbag")
                    plt.close(fig)

            # Profil comparatif
            if incl_cmp:
                cmp_proj = st.session_state.get("rpt_cmp_proj")
                cmp_terr = st.session_state.get("rpt_cmp_terr")
                if cmp_proj and cmp_terr:
                    fig = fig_comparatif(cmp_proj, cmp_terr)
                    _add(pdf, fig, "Profil comparatif")
                    plt.close(fig)

            d = pdf.infodict()
            d["Title"]   = titre or "Rapport 4 Experience"
            d["Author"]  = "4 Experience Simulateur"
            d["Subject"] = "Simulation de piste & trajectoire airbag"

        return buf.getvalue()

    # ── UI du rapport ──────────────────────────────────────────────
    st.markdown("""
    <div style='font-size:13px;color:#475569;margin-bottom:14px;line-height:1.7'>
    Configurez le contenu du rapport puis cliquez sur <b>Générer</b>.<br>
    <b>Important :</b> lancez d'abord les simulations souhaitées dans les onglets correspondants —
    les résultats sont mémorisés automatiquement.
    </div>""", unsafe_allow_html=True)

    # Sauvegarder l'état piste pour le rapport quand on arrive sur l'onglet
    if st.session_state.get("piste_res"):
        st.session_state["rpt_piste_res"]  = st.session_state["piste_res"]
        st.session_state["rpt_piste_secs"] = st.session_state.get("piste_secs", [])
        st.session_state["rpt_piste_params"] = {
            "masse": st.session_state.get("piste_masse", masse),
            "V0":    st.session_state.get("piste_V0", V0),
            "Cx":    Cx, "S": S, "rho": rho,
            "pas_m": st.session_state.get("piste_pas_m", pas_m),
        }
    if st.session_state.get("airbag_res"):
        st.session_state["rpt_airbag_res"]   = st.session_state["airbag_res"]
        st.session_state["rpt_airbag_alpha"] = st.session_state.get("airbag_alpha", ALPHA_EXIT_DEG)
        st.session_state["rpt_airbag_hair"]  = st.session_state.get("airbag_hair")
    if st.session_state.get("cmp_res"):
        st.session_state["rpt_cmp_proj"] = st.session_state["cmp_res"][0]
        st.session_state["rpt_cmp_terr"] = st.session_state["cmp_res"][1]

    # Informations projet
    st.markdown("<div class='section-title'>📋 Informations du projet</div>",
                unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        rpt_titre  = st.text_input("Titre du rapport",
                                    value="RAPPORT DE SIMULATION", key="rpt_titre")
        rpt_projet = st.text_input("Projet", placeholder="Ex: Piste tubing Alpe d'Huez",
                                    key="rpt_projet")
        rpt_site   = st.text_input("Site / Lieu", placeholder="Ex: Station des 2 Alpes",
                                    key="rpt_site")
    with col_b:
        rpt_operateur = st.text_input("Opérateur", placeholder="Nom de l'opérateur",
                                       key="rpt_operateur")
        rpt_notes     = st.text_area("Notes / Observations",
                                      placeholder="Conditions, remarques...",
                                      height=95, key="rpt_notes")

    # Sélection du contenu
    st.markdown("<div class='section-title'>📊 Contenu du rapport</div>",
                unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🏔️ Simulateur de piste**")
        inc_garde   = st.checkbox("Page de garde",          value=True, key="rpt_garde")
        inc_params  = st.checkbox("Paramètres & sections",  value=True, key="rpt_params")
        inc_profil  = st.checkbox("Profil de piste",        value=True, key="rpt_profil")
        inc_vitesse = st.checkbox("Vitesse / distance",     value=True, key="rpt_vitesse")
        inc_temps   = st.checkbox("Temps écoulé / distance",value=True, key="rpt_temps")
        if st.session_state.get("piste_res"):
            st.success("✅ Simulation piste disponible")
        else:
            st.warning("⚠️ Lancez la simulation piste")
    with col2:
        st.markdown("**🪂 Trajectoire Airbag**")
        inc_airbag = st.checkbox("Trajectoire du saut", value=True, key="rpt_airbag")
        if st.session_state.get("airbag_res"):
            st.success("✅ Trajectoire disponible")
        else:
            st.warning("⚠️ Lancez la simulation airbag")
    with col3:
        st.markdown("**📐 Profil comparatif**")
        inc_cmp = st.checkbox("Superposition + écart", value=True, key="rpt_cmp")
        if st.session_state.get("cmp_res"):
            st.success("✅ Comparatif disponible")
        else:
            st.warning("⚠️ Lancez le comparatif")

    st.markdown("---")

    # Génération
    if st.button("▶  Générer le rapport PDF", type="primary",
                 use_container_width=True, key="rpt_btn"):
        has_content = any([
            inc_garde,
            inc_profil  and st.session_state.get("piste_res"),
            inc_vitesse and st.session_state.get("piste_res"),
            inc_temps   and st.session_state.get("piste_res"),
            inc_airbag  and st.session_state.get("airbag_res"),
            inc_cmp     and st.session_state.get("cmp_res"),
        ])
        if not has_content:
            st.error("Aucun contenu — lancez au moins une simulation.")
        else:
            with st.spinner("Génération du rapport en cours..."):
                try:
                    date_str = date.today().strftime("%d/%m/%Y")
                    pdf_bytes = generer_pdf(
                        rpt_titre, rpt_projet, rpt_site, date_str,
                        rpt_operateur, rpt_notes,
                        inc_garde, inc_params, inc_profil, inc_vitesse,
                        inc_temps, inc_airbag, inc_cmp,
                    )
                    nom_fichier = (
                        f"rapport_4experience_"
                        f"{(rpt_projet or 'simulation').replace(' ','_')}"
                        f"_{date.today().strftime('%Y%m%d')}.pdf"
                    )
                    st.success(f"✅ Rapport généré — {len(pdf_bytes)//1024} Ko")
                    st.download_button(
                        "📥  Télécharger le rapport PDF",
                        data=pdf_bytes,
                        file_name=nom_fichier,
                        mime="application/pdf",
                        use_container_width=True,
                        key="rpt_dl",
                    )
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
                    import traceback
                    st.code(traceback.format_exc())

