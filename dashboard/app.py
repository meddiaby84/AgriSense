import os
from datetime import datetime, timezone
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

COLLECTION_SERVICE_URL = os.getenv(
    "COLLECTION_SERVICE_URL", "http://collection-service:8000"
)
PROCESSING_SERVICE_URL = os.getenv(
    "PROCESSING_SERVICE_URL", "http://processing-service:8000"
)
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))

st.set_page_config(
    page_title="AgriSense | Supervision IoT Agricole Distribuée",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# DESIGN SYSTEM & CUSTOM CSS (Modern Agritech SaaS UI)
# ============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1440px;
    }

    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #064e3b 0%, #047857 55%, #0f766e 100%);
        border-radius: 18px;
        padding: 1.6rem 2rem;
        color: #ffffff;
        box-shadow: 0 12px 30px rgba(4, 120, 87, 0.18);
        margin-bottom: 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 0.92rem;
        color: #d1fae5;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }
    .hero-badges {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        align-items: center;
    }
    .badge-pill {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: #ecfdf5;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* KPI Cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.55rem;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
    }
    .kpi-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #475569;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    /* Parcel Cards */
    .parcel-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #10b981;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.8rem;
    }
    .parcel-card.alert {
        border-left-color: #ef4444;
    }
    .parcel-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .parcel-loc {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 0.85rem;
    }
    .parcel-metrics {
        display: flex;
        justify-content: space-between;
        background: #f8fafc;
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        font-size: 0.84rem;
        color: #1e293b;
    }

    /* Alert Item Card */
    .alert-item {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 4px solid #e11d48;
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.65rem;
    }
    .alert-item-title {
        font-weight: 700;
        color: #881337;
        font-size: 0.92rem;
    }
    .alert-item-meta {
        font-size: 0.78rem;
        color: #9f1239;
        margin-top: 0.25rem;
    }

    /* Section Header */
    .section-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.5rem;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Service Health Pill in Sidebar */
    .srv-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.55rem;
        font-size: 0.84rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# CLIENT API REST (Zéro accès direct DB - Respect strict du TRD Section 10.3)
# ============================================================================
def api_get(base_url: str, path: str, params: dict = None):
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(f"{base_url}{path}", params=params)
            resp.raise_for_status()
            return resp.json(), None
    except httpx.TimeoutException:
        return None, f"Délai d'attente dépassé (Timeout) sur {base_url}{path}"
    except httpx.RequestError as exc:
        return None, f"Service injoignable ({base_url}) : {exc}"
    except httpx.HTTPStatusError as exc:
        return None, f"Erreur HTTP {exc.response.status_code} : {exc.response.text}"


def api_post(base_url: str, path: str, payload: dict):
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.post(f"{base_url}{path}", json=payload)
            return resp.status_code, resp.json()
    except Exception as exc:
        return 503, {"detail": f"Service indisponible : {exc}"}


def render_kpi_card(label: str, value: str, sub: str, icon: str, bg_color: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">{label}</span>
                <div class="kpi-icon" style="background: {bg_color};">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_gauge(title: str, value: float, min_v: float, max_v: float, threshold: float, unit: str, invert_alert: bool = False):
    if value is None:
        value = 0.0
    if not invert_alert:
        # Alerte si supérieur au seuil (ex: Température > 35°C)
        steps = [
            {"range": [min_v, threshold * 0.85], "color": "#d1fae5"},
            {"range": [threshold * 0.85, threshold], "color": "#fef3c7"},
            {"range": [threshold, max_v], "color": "#fee2e2"},
        ]
        bar_color = "#ef4444" if value > threshold else "#059669"
    else:
        # Alerte si inférieur au seuil (ex: Humidité < 25%)
        steps = [
            {"range": [min_v, threshold], "color": "#fee2e2"},
            {"range": [threshold, threshold * 1.3], "color": "#fef3c7"},
            {"range": [threshold * 1.3, max_v], "color": "#d1fae5"},
        ]
        bar_color = "#ef4444" if value < threshold else "#0284c7"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": f" {unit}", "font": {"size": 26, "weight": 700}},
            title={"text": title, "font": {"size": 14, "color": "#334155"}},
            gauge={
                "axis": {"range": [min_v, max_v]},
                "bar": {"color": bar_color, "thickness": 0.65},
                "steps": steps,
                "threshold": {
                    "line": {"color": "#dc2626", "width": 3},
                    "thickness": 0.8,
                    "value": threshold,
                },
            },
        )
    )
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=40, b=15), paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ============================================================================
# SIDEBAR : NAVIGATION, FILTRES GLOBAUX & SANTÉ DES SERVICES
# ============================================================================
with st.sidebar:
    st.markdown("## 🌱 **AgriSense IoT**")
    st.caption("Plateforme Distribuée • Master ADIA")

    page = st.radio(
        "Navigation principale",
        [
            "🏠 1. Cockpit & Vue Générale",
            "🌾 2. Supervision des Parcelles",
            "📈 3. Laboratoire d'Analyse",
            "🚨 4. Centre d'Alertes & Test IoT",
        ],
    )

    st.markdown("---")
    st.markdown("### ⏱️ Fenêtre Temporelle")
    period_options = {
        "Dernières 15 minutes": "last_15_minutes",
        "Dernière heure": "last_1_hour",
        "Dernières 6 heures": "last_6_hours",
        "Dernières 24 heures": "last_24_hours",
        "7 derniers jours": "last_7_days",
        "Historique complet": "all",
    }
    selected_period_label = st.selectbox(
        "Période d'analyse",
        list(period_options.keys()),
        index=3,
        label_visibility="collapsed",
    )
    selected_period = period_options[selected_period_label]

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("🔄 Actualiser", use_container_width=True, type="primary"):
        st.rerun()
    auto_refresh = col_btn2.toggle("Auto (5s)", value=False)

    # Santé des microservices
    col_health, col_err = api_get(COLLECTION_SERVICE_URL, "/api/v1/health")
    proc_health, proc_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/health")

    col_ok = bool(col_health and col_health.get("status") == "healthy")
    proc_ok = bool(proc_health and proc_health.get("status") == "healthy")
    db_ok = bool(
        (col_health and col_health.get("database") == "connected")
        or (proc_health and proc_health.get("database") == "connected")
    )

    st.markdown("---")
    st.markdown("### 🖧 État de l'Architecture")
    st.markdown(
        f"""
        <div class="srv-card">
            <div><b>API Collecte (:8001)</b> : {'🟢 Opérationnel' if col_ok else '🔴 Indisponible'}</div>
            <div style="margin-top:4px;"><b>API Traitement (:8002)</b> : {'🟢 Opérationnel' if proc_ok else '🔴 Indisponible'}</div>
            <div style="margin-top:4px;"><b>PostgreSQL (:5432)</b> : {'🟢 Connecté' if db_ok else '🔴 Déconnecté'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# CHARGEMENT DES DONNÉES VIA API REST
# ============================================================================
parcels, parcels_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/parcels")
sensors, sensors_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/sensors")
global_stats, stats_err = api_get(
    PROCESSING_SERVICE_URL, "/api/v1/statistics", {"period": selected_period}
)
recent_alerts, alerts_err = api_get(
    PROCESSING_SERVICE_URL, "/api/v1/alerts", {"period": selected_period, "limit": 100}
)

thresholds = (
    global_stats.get("thresholds", {})
    if global_stats
    else {"temperature_max": 35.0, "soil_humidity_min": 25.0, "air_humidity_min": 30.0}
)

# ============================================================================
# HERO BANNER (Règle métier n°9 : Identification explicite des données simulées)
# ============================================================================
now_str = datetime.now().strftime("%H:%M:%S")
sys_badge = "🟢 Tous les services actifs" if (col_ok and proc_ok) else "🟠 Mode Dégradé Détecté"

st.markdown(
    f"""
    <div class="hero-banner">
        <div>
            <h1 class="hero-title">🌱 AgriSense — Supervision & Analyse IoT Agricole</h1>
            <p class="hero-subtitle">
                Architecture microservices distribuée (FastAPI • PostgreSQL • Streamlit) — Fenêtre : <b>{selected_period_label}</b>
            </p>
        </div>
        <div class="hero-badges">
            <span class="badge-pill">🤖 Mode Simulation IoT Actif</span>
            <span class="badge-pill">{sys_badge}</span>
            <span class="badge-pill">🕒 Maj : {now_str}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if proc_err or parcels_err:
    st.error(
        f"🚨 **Alerte Résilience** : Le service de traitement (`{PROCESSING_SERVICE_URL}`) ne répond pas. "
        f"Le tableau de bord fonctionne en mode tolérant aux pannes. Détail : `{proc_err or parcels_err}`"
    )

# ============================================================================
# PAGE 1 : COCKPIT & VUE GÉNÉRALE
# ============================================================================
if page.startswith("🏠"):
    total_parcels = len(parcels) if parcels else 0
    active_sensors = sum(1 for s in sensors if s.get("actif")) if sensors else 0
    total_sensors = len(sensors) if sensors else 0
    total_measurements = global_stats.get("measurements_count", 0) if global_stats else 0
    total_alerts = global_stats.get("alerts_count", 0) if global_stats else 0

    t_avg = (global_stats or {}).get("temperature", {}).get("average")
    s_avg = (global_stats or {}).get("soil_humidity", {}).get("average")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            "Parcelles Agricoles",
            str(total_parcels),
            "Zones géographiques suivies",
            "🗺️",
            "#ecfdf5",
        )
    with k2:
        render_kpi_card(
            "Capteurs IoT Actifs",
            f"{active_sensors} / {total_sensors}",
            f"{total_sensors - active_sensors} capteur(s) en maintenance",
            "📡",
            "#eff6ff",
        )
    with k3:
        render_kpi_card(
            "Mesures Collectées",
            f"{total_measurements:,}".replace(",", " "),
            f"Moy. Globale : {t_avg or '-'}°C | Sol {s_avg or '-'}%",
            "📊",
            "#f5f3ff",
        )
    with k4:
        render_kpi_card(
            "Alertes sur Seuils",
            str(total_alerts),
            f"Seuils : T>{thresholds.get('temperature_max')}°C | Sol<{thresholds.get('soil_humidity_min')}%",
            "🚨",
            "#fff1f2" if total_alerts > 0 else "#f0fdf4",
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Synthèse visuelle par parcelle
    st.markdown('<div class="section-title">🌾 État de Santé en Direct par Parcelle</div>', unsafe_allow_html=True)
    if parcels:
        p_cols = st.columns(len(parcels))
        for idx, p in enumerate(parcels):
            p_stat, _ = api_get(
                PROCESSING_SERVICE_URL,
                "/api/v1/statistics",
                {"parcel_id": p["id"], "period": selected_period},
            )
            p_alerts = (p_stat or {}).get("alerts_count", 0)
            p_temp = (p_stat or {}).get("temperature", {}).get("average")
            p_soil = (p_stat or {}).get("soil_humidity", {}).get("average")
            p_air = (p_stat or {}).get("air_humidity", {}).get("average")
            p_count = (p_stat or {}).get("measurements_count", 0)

            status_badge = (
                f"<span style='color:#dc2626;font-weight:700;'>🔴 {p_alerts} alerte(s)</span>"
                if p_alerts > 0
                else "<span style='color:#059669;font-weight:700;'>🟢 Conditions normales</span>"
            )
            card_cls = "parcel-card alert" if p_alerts > 0 else "parcel-card"

            with p_cols[idx]:
                st.markdown(
                    f"""
                    <div class="{card_cls}">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:0.75rem;font-weight:700;color:#047857;background:#ecfdf5;padding:2px 8px;border-radius:6px;">{p['id']}</span>
                            {status_badge}
                        </div>
                        <div class="parcel-title" style="margin-top:0.4rem;">{p['nom']}</div>
                        <div class="parcel-loc">📍 {p.get('localisation') or 'Non spécifiée'} • 📡 {p.get('active_sensors', 0)}/{p.get('total_sensors', 0)} capteurs actifs</div>
                        <div class="parcel-metrics">
                            <div>🌡️ <b>{p_temp if p_temp is not None else '-'} °C</b><br/><span style="font-size:0.72rem;color:#64748b;">Temp. moy</span></div>
                            <div>💧 <b>{p_soil if p_soil is not None else '-'} %</b><br/><span style="font-size:0.72rem;color:#64748b;">Hum. Sol</span></div>
                            <div>🌬️ <b>{p_air if p_air is not None else '-'} %</b><br/><span style="font-size:0.72rem;color:#64748b;">Hum. Air</span></div>
                            <div>📥 <b>{p_count}</b><br/><span style="font-size:0.72rem;color:#64748b;">Mesures</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    col_left, col_right = st.columns([1.65, 1.05])

    with col_left:
        st.markdown('<div class="section-title">🕒 Flux Temps Réel des Dernières Mesures</div>', unsafe_allow_html=True)
        recent_measurements, m_err = api_get(
            PROCESSING_SERVICE_URL,
            "/api/v1/measurements",
            {"period": selected_period, "limit": 20},
        )
        if m_err:
            st.warning(m_err)
        elif recent_measurements:
            df_rec = pd.DataFrame(recent_measurements)

            def _status_label(row):
                reasons = []
                if row["temperature"] > thresholds.get("temperature_max", 35.0):
                    reasons.append("🔥 T° Haute")
                if row["soil_humidity"] < thresholds.get("soil_humidity_min", 25.0):
                    reasons.append("🏜️ Sol Sec")
                if row["air_humidity"] < thresholds.get("air_humidity_min", 30.0):
                    reasons.append("🌬️ Air Sec")
                return " | ".join(reasons) if reasons else "✅ Normal"

            df_rec["Diagnostic"] = df_rec.apply(_status_label, axis=1)
            df_display = df_rec[
                [
                    "id",
                    "parcel_name",
                    "sensor_id",
                    "temperature",
                    "soil_humidity",
                    "air_humidity",
                    "Diagnostic",
                    "measured_at",
                ]
            ].rename(
                columns={
                    "id": "ID",
                    "parcel_name": "Parcelle",
                    "sensor_id": "Capteur",
                    "temperature": "Temp. (°C)",
                    "soil_humidity": "Sol (%)",
                    "air_humidity": "Air (%)",
                    "measured_at": "Horodatage UTC",
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=360)
        else:
            st.info("Aucune mesure reçue sur la période sélectionnée.")

    with col_right:
        st.markdown('<div class="section-title">🔔 Dernières Alertes Déclenchées</div>', unsafe_allow_html=True)
        if recent_alerts:
            for al in recent_alerts[:5]:
                st.markdown(
                    f"""
                    <div class="alert-item">
                        <div class="alert-item-title">⚠️ {al['message']}</div>
                        <div class="alert-item-meta">
                            🌾 <b>{al['parcel_name']}</b> • 📡 <code>{al['sensor_id']}</code> • 🕒 {str(al['measured_at'])[:19].replace('T', ' ')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ Aucun dépassement de seuil sur cette période.")

# ============================================================================
# PAGE 2 : SUPERVISION DÉTAILLÉE DES PARCELLES
# ============================================================================
elif page.startswith("🌾"):
    st.markdown('<div class="section-title">🌾 Supervision Agronomique par Parcelle</div>', unsafe_allow_html=True)

    if parcels:
        parcel_map = {f"{p['id']} — {p['nom']} ({p.get('localisation', '')})": p for p in parcels}
        chosen_label = st.selectbox("Choisir la parcelle à inspecter :", list(parcel_map.keys()))
        chosen_parcel = parcel_map[chosen_label]
        chosen_parcel_id = chosen_parcel["id"]

        p_stats, _ = api_get(
            PROCESSING_SERVICE_URL,
            "/api/v1/statistics",
            {"parcel_id": chosen_parcel_id, "period": selected_period},
        )
        p_meas, _ = api_get(
            PROCESSING_SERVICE_URL,
            f"/api/v1/parcels/{chosen_parcel_id}/measurements",
            {"period": selected_period, "limit": 100},
        )
        p_sensors = [s for s in (sensors or []) if s["parcelle_id"] == chosen_parcel_id]

        if p_stats:
            t_stat = p_stats.get("temperature", {})
            s_stat = p_stats.get("soil_humidity", {})
            a_stat = p_stats.get("air_humidity", {})

            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(
                    create_gauge(
                        f"Température Moyenne (Min {t_stat.get('min') or '-'}° / Max {t_stat.get('max') or '-'}°)",
                        t_stat.get("average") or 0.0,
                        0.0,
                        50.0,
                        thresholds.get("temperature_max", 35.0),
                        "°C",
                        invert_alert=False,
                    ),
                    use_container_width=True,
                )
            with g2:
                st.plotly_chart(
                    create_gauge(
                        f"Humidité du Sol Moyenne (Min {s_stat.get('min') or '-'}% / Max {s_stat.get('max') or '-'}%)",
                        s_stat.get("average") or 0.0,
                        0.0,
                        100.0,
                        thresholds.get("soil_humidity_min", 25.0),
                        "%",
                        invert_alert=True,
                    ),
                    use_container_width=True,
                )
            with g3:
                st.plotly_chart(
                    create_gauge(
                        f"Humidité de l'Air Moyenne (Min {a_stat.get('min') or '-'}% / Max {a_stat.get('max') or '-'}%)",
                        a_stat.get("average") or 0.0,
                        0.0,
                        100.0,
                        thresholds.get("air_humidity_min", 30.0),
                        "%",
                        invert_alert=True,
                    ),
                    use_container_width=True,
                )

        c_sens, c_hist = st.columns([1, 2])
        with c_sens:
            st.markdown("#### 📡 Capteurs rattachés à la parcelle")
            for s in p_sensors:
                etat = "🟢 Actif" if s.get("actif") else "🟠 Maintenance (Inactif)"
                st.markdown(
                    f"""
                    <div class="srv-card">
                        <b>{s['id']}</b> — {s['nom']}<br/>
                        <span style="color:#64748b;font-size:0.78rem;">Type : {s['type']}</span> • <b>{etat}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with c_hist:
            st.markdown("#### 📋 Historique des mesures de la parcelle")
            if p_meas:
                st.dataframe(pd.DataFrame(p_meas), use_container_width=True, hide_index=True, height=280)
            else:
                st.info("Aucune mesure disponible pour cette parcelle.")

# ============================================================================
# PAGE 3 : LABORATOIRE D'ANALYSE & SÉRIES TEMPORELLES
# ============================================================================
elif page.startswith("📈"):
    st.markdown('<div class="section-title">📈 Analyse Temporelle & Visualisation Interactive</div>', unsafe_allow_html=True)

    f_col1, f_col2 = st.columns(2)
    parcel_options = {"Toutes les parcelles": None}
    if parcels:
        for p in parcels:
            parcel_options[f"{p['id']} — {p['nom']}"] = p["id"]
    selected_parcel_filter = f_col1.selectbox("Filtrer par parcelle :", list(parcel_options.keys()))
    parcel_id_filter = parcel_options[selected_parcel_filter]

    sensor_options = {"Tous les capteurs": None}
    if sensors:
        for s in sensors:
            if not parcel_id_filter or s["parcelle_id"] == parcel_id_filter:
                sensor_options[f"{s['id']} ({s['nom']})"] = s["id"]
    selected_sensor_filter = f_col2.selectbox("Filtrer par capteur :", list(sensor_options.keys()))
    sensor_id_filter = sensor_options[selected_sensor_filter]

    measurements, err = api_get(
        PROCESSING_SERVICE_URL,
        "/api/v1/measurements",
        {
            "parcel_id": parcel_id_filter,
            "sensor_id": sensor_id_filter,
            "period": selected_period,
            "limit": 500,
        },
    )

    if err:
        st.error(err)
    elif measurements:
        df = pd.DataFrame(measurements)
        df["measured_at"] = pd.to_datetime(df["measured_at"])
        df = df.sort_values("measured_at")

        tab_temp, tab_soil, tab_air, tab_corr = st.tabs(
            [
                "🌡️ Température (°C)",
                "💧 Humidité du Sol (%)",
                "🌬️ Humidité de l'Air (%)",
                "🔬 Corrélation Température / Sol",
            ]
        )

        with tab_temp:
            fig_temp = px.line(
                df,
                x="measured_at",
                y="temperature",
                color="sensor_id",
                line_shape="spline",
                markers=True,
                title="Évolution de la Température par Capteur (°C)",
                labels={"measured_at": "Horodatage", "temperature": "Température (°C)", "sensor_id": "Capteur"},
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            t_max = thresholds.get("temperature_max", 35.0)
            fig_temp.add_hline(
                y=t_max,
                line_dash="dash",
                line_color="#ef4444",
                annotation_text=f"⚠️ Seuil critique max ({t_max} °C)",
                annotation_position="top left",
            )
            fig_temp.update_layout(height=420, hovermode="x unified", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_temp, use_container_width=True)

        with tab_soil:
            fig_soil = px.line(
                df,
                x="measured_at",
                y="soil_humidity",
                color="sensor_id",
                line_shape="spline",
                markers=True,
                title="Évolution de l'Humidité du Sol par Capteur (%)",
                labels={"measured_at": "Horodatage", "soil_humidity": "Humidité du sol (%)", "sensor_id": "Capteur"},
                color_discrete_sequence=px.colors.qualitative.Vivid,
            )
            s_min = thresholds.get("soil_humidity_min", 25.0)
            fig_soil.add_hline(
                y=s_min,
                line_dash="dash",
                line_color="#f97316",
                annotation_text=f"⚠️ Seuil stress hydrique ({s_min} %)",
                annotation_position="bottom left",
            )
            fig_soil.update_layout(height=420, hovermode="x unified", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_soil, use_container_width=True)

        with tab_air:
            fig_air = px.line(
                df,
                x="measured_at",
                y="air_humidity",
                color="sensor_id",
                line_shape="spline",
                markers=True,
                title="Évolution de l'Humidité de l'Air par Capteur (%)",
                labels={"measured_at": "Horodatage", "air_humidity": "Humidité de l'air (%)", "sensor_id": "Capteur"},
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            a_min = thresholds.get("air_humidity_min", 30.0)
            fig_air.add_hline(
                y=a_min,
                line_dash="dash",
                line_color="#0284c7",
                annotation_text=f"⚠️ Seuil air sec ({a_min} %)",
                annotation_position="bottom left",
            )
            fig_air.update_layout(height=420, hovermode="x unified", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_air, use_container_width=True)

        with tab_corr:
            fig_scatter = px.scatter(
                df,
                x="temperature",
                y="soil_humidity",
                color="parcel_name",
                size="air_humidity",
                hover_data=["sensor_id", "measured_at"],
                title="Croisement Température (°C) vs Humidité du Sol (%) — Taille = Humidité de l'Air",
                labels={
                    "temperature": "Température (°C)",
                    "soil_humidity": "Humidité du Sol (%)",
                    "parcel_name": "Parcelle",
                },
            )
            fig_scatter.add_vline(x=thresholds.get("temperature_max", 35.0), line_dash="dot", line_color="red")
            fig_scatter.add_hline(y=thresholds.get("soil_humidity_min", 25.0), line_dash="dot", line_color="orange")
            fig_scatter.update_layout(height=420, plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_scatter, use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exporter les données filtrées au format CSV",
            data=csv_bytes,
            file_name=f"agrisense_mesures_{selected_period}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucune mesure disponible pour ces critères.")

# ============================================================================
# PAGE 4 : CENTRE D'ALERTES & CONSOLE DE TEST IOT
# ============================================================================
elif page.startswith("🚨"):
    tab_alerts, tab_sim = st.tabs(
        ["🚨 Journal & Analytique des Alertes", "🧪 Console d'Injection IoT (Démo Soutenance)"]
    )

    with tab_alerts:
        parcel_options = {"Toutes les parcelles": None}
        if parcels:
            for p in parcels:
                parcel_options[f"{p['id']} — {p['nom']}"] = p["id"]
        selected_parcel_alert = st.selectbox(
            "Filtrer les alertes par parcelle :", list(parcel_options.keys())
        )

        alerts, alert_err = api_get(
            PROCESSING_SERVICE_URL,
            "/api/v1/alerts",
            {
                "parcel_id": parcel_options[selected_parcel_alert],
                "period": selected_period,
                "limit": 300,
            },
        )

        if alert_err:
            st.error(alert_err)
        elif alerts:
            df_alerts = pd.DataFrame(alerts)
            n_temp = int((df_alerts["indicateur"] == "temperature").sum())
            n_soil = int((df_alerts["indicateur"] == "soil_humidity").sum())
            n_air = int((df_alerts["indicateur"] == "air_humidity").sum())

            a1, a2, a3, a4 = st.columns(4)
            with a1:
                render_kpi_card("Total Alertes", str(len(df_alerts)), "Sur la période filtrée", "🚨", "#fff1f2")
            with a2:
                render_kpi_card("Excès Thermique", str(n_temp), f"Température > {thresholds.get('temperature_max')} °C", "🔥", "#fef2f2")
            with a3:
                render_kpi_card("Stress Hydrique Sol", str(n_soil), f"Humidité sol < {thresholds.get('soil_humidity_min')} %", "🏜️", "#fff7ed")
            with a4:
                render_kpi_card("Sécheresse de l'Air", str(n_air), f"Humidité air < {thresholds.get('air_humidity_min')} %", "🌬️", "#f0f9ff")

            st.markdown("<br/>", unsafe_allow_html=True)
            ch1, ch2 = st.columns(2)
            with ch1:
                fig_pie = px.pie(
                    df_alerts,
                    names="indicateur",
                    hole=0.45,
                    title="Répartition par Type d'Alerte",
                    color="indicateur",
                    color_discrete_map={
                        "temperature": "#ef4444",
                        "soil_humidity": "#f97316",
                        "air_humidity": "#0284c7",
                    },
                )
                fig_pie.update_layout(height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            with ch2:
                by_parcel = df_alerts.groupby("parcel_name").size().reset_index(name="Nombre d'alertes")
                fig_bar = px.bar(
                    by_parcel,
                    x="parcel_name",
                    y="Nombre d'alertes",
                    color="parcel_name",
                    title="Alertes par Parcelle Agricole",
                )
                fig_bar.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("#### 📋 Registre détaillé des alertes")
            st.dataframe(
                df_alerts[
                    [
                        "id",
                        "parcel_name",
                        "sensor_id",
                        "indicateur",
                        "valeur",
                        "seuil",
                        "message",
                        "measured_at",
                        "statut",
                    ]
                ].rename(
                    columns={
                        "id": "ID",
                        "parcel_name": "Parcelle",
                        "sensor_id": "Capteur",
                        "indicateur": "Indicateur",
                        "valeur": "Valeur mesurée",
                        "seuil": "Seuil critique",
                        "message": "Diagnostic",
                        "measured_at": "Date/Heure Mesure",
                        "statut": "Statut",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("✅ Aucune alerte détectée sur cette période.")

    with tab_sim:
        st.markdown("#### 🧪 Console d'Injection de Scénarios IoT (Idéal pour la démonstration)")
        st.write(
            "Testez en direct la chaîne complète **`Dashboard -> Collection Service (8001) -> Validation Pydantic -> PostgreSQL -> Processing Service (8002)`**."
        )

        preset_col1, preset_col2, preset_col3 = st.columns(3)
        if preset_col1.button("🔥 Simuler Canicule + Sécheresse (Alerte Double)", use_container_width=True):
            code, resp = api_post(
                COLLECTION_SERVICE_URL,
                "/api/v1/measurements",
                {
                    "sensor_id": "sensor-001",
                    "temperature": 39.8,
                    "soil_humidity": 17.5,
                    "air_humidity": 24.0,
                    "measured_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            st.success(f"Réponse HTTP {code} : {resp}")

        if preset_col2.button("❌ Simuler Valeur Aberrante (Test Rejet HTTP 422)", use_container_width=True):
            code, resp = api_post(
                COLLECTION_SERVICE_URL,
                "/api/v1/measurements",
                {
                    "sensor_id": "sensor-001",
                    "temperature": 145.0,
                    "soil_humidity": -12.0,
                    "air_humidity": 50.0,
                    "measured_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            st.warning(f"Rejet attendu validé (HTTP {code}) : {resp}")

        if preset_col3.button("🚫 Simuler Capteur en Maintenance (sensor-006)", use_container_width=True):
            code, resp = api_post(
                COLLECTION_SERVICE_URL,
                "/api/v1/measurements",
                {
                    "sensor_id": "sensor-006",
                    "temperature": 25.0,
                    "soil_humidity": 40.0,
                    "air_humidity": 50.0,
                    "measured_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            st.warning(f"Rejet capteur inactif validé (HTTP {code}) : {resp}")

        st.markdown("---")
        with st.form("custom_iot_form"):
            st.markdown("##### 🎛️ Envoyer une mesure personnalisée")
            fc1, fc2, fc3, fc4 = st.columns(4)
            sensor_choice = fc1.selectbox(
                "Capteur cible",
                [s["id"] for s in sensors] if sensors else ["sensor-001", "sensor-006"],
            )
            t_val = fc2.number_input("Température (°C)", value=36.5, step=0.5)
            s_val = fc3.number_input("Humidité du sol (%)", value=22.0, step=1.0)
            a_val = fc4.number_input("Humidité de l'air (%)", value=45.0, step=1.0)
            if st.form_submit_button("🚀 Transmettre au Service de Collecte", type="primary"):
                code, resp = api_post(
                    COLLECTION_SERVICE_URL,
                    "/api/v1/measurements",
                    {
                        "sensor_id": sensor_choice,
                        "temperature": t_val,
                        "soil_humidity": s_val,
                        "air_humidity": a_val,
                        "measured_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                if code in (200, 201):
                    st.success(f"Mesure acceptée (HTTP {code}) : {resp}")
                else:
                    st.error(f"Mesure rejetée (HTTP {code}) : {resp}")

if auto_refresh:
    import time as _time

    _time.sleep(5)
    st.rerun()
