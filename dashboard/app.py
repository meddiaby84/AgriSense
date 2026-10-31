import os
from datetime import datetime, timezone
import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

COLLECTION_SERVICE_URL = os.getenv(
    "COLLECTION_SERVICE_URL", "http://collection-service:8000"
)
PROCESSING_SERVICE_URL = os.getenv(
    "PROCESSING_SERVICE_URL", "http://processing-service:8000"
)
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))

st.set_page_config(
    page_title="AgriSense - Supervision IoT Agricole",
    page_icon="🌱",
    layout="wide",
)


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


# En-tête et bandeau de simulation (Règle métier n°9 & Section 16.2)
st.title("🌱 AgriSense — Plateforme distribuée de supervision IoT agricole")
st.info(
    "**Mode Simulation IoT Actif** : Toutes les mesures affichées dans ce tableau de bord "
    "proviennent de capteurs agricoles logiciels simulés (aucun capteur physique connecté)."
)

# Navigation latérale (4 pages du TRD Section 16.1 + Outil de test interactif)
st.sidebar.header("Navigation AgriSense")
page = st.sidebar.radio(
    "Aller vers :",
    [
        "1. Vue générale",
        "2. Supervision des parcelles",
        "3. Analyse des mesures",
        "4. Alertes",
    ],
)

period_options = {
    "Dernières 15 minutes": "last_15_minutes",
    "Dernière heure": "last_1_hour",
    "Dernières 6 heures": "last_6_hours",
    "Dernières 24 heures": "last_24_hours",
    "7 derniers jours": "last_7_days",
    "Toutes les mesures": "all",
}
selected_period_label = st.sidebar.selectbox(
    "Période d'analyse :",
    list(period_options.keys()),
    index=3,
)
selected_period = period_options[selected_period_label]

if st.sidebar.button("🔄 Actualiser les données"):
    st.rerun()

# Vérification de l'état des services
col_health, col_err = api_get(COLLECTION_SERVICE_URL, "/api/v1/health")
proc_health, proc_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/health")

st.sidebar.markdown("---")
st.sidebar.subheader("État des microservices")
st.sidebar.write(
    f"**Collecte (8001)** : {'🟢 En ligne' if col_health and col_health.get('status') == 'healthy' else '🔴 Indisponible'}"
)
st.sidebar.write(
    f"**Traitement (8002)** : {'🟢 En ligne' if proc_health and proc_health.get('status') == 'healthy' else '🔴 Indisponible'}"
)

# Chargement des données communes via l'API de traitement
parcels, parcels_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/parcels")
sensors, sensors_err = api_get(PROCESSING_SERVICE_URL, "/api/v1/sensors")
global_stats, stats_err = api_get(
    PROCESSING_SERVICE_URL, "/api/v1/statistics", {"period": selected_period}
)

if proc_err or parcels_err:
    st.error(
        f"⚠️ Impossible de récupérer les données depuis `processing-service` ({PROCESSING_SERVICE_URL}). "
        f"Détail : {proc_err or parcels_err}"
    )

# ============================================================================
# PAGE 1 : VUE GÉNÉRALE
# ============================================================================
if page == "1. Vue générale":
    st.subheader("📊 Vue générale de la plateforme")

    total_parcels = len(parcels) if parcels else 0
    active_sensors = (
        sum(1 for s in sensors if s.get("actif")) if sensors else 0
    )
    total_sensors = len(sensors) if sensors else 0
    total_measurements = (
        global_stats.get("measurements_count", 0) if global_stats else 0
    )
    total_alerts = global_stats.get("alerts_count", 0) if global_stats else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Parcelles supervisées", total_parcels)
    k2.metric("Capteurs actifs", f"{active_sensors} / {total_sensors}")
    k3.metric(f"Mesures ({selected_period_label})", total_measurements)
    k4.metric(f"Alertes déclenchées ({selected_period_label})", total_alerts)

    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("#### 🕒 Dernières mesures reçues")
        recent_measurements, m_err = api_get(
            PROCESSING_SERVICE_URL,
            "/api/v1/measurements",
            {"period": selected_period, "limit": 15},
        )
        if m_err:
            st.warning(m_err)
        elif recent_measurements:
            df_rec = pd.DataFrame(recent_measurements)
            df_display = df_rec[
                [
                    "id",
                    "parcel_name",
                    "sensor_id",
                    "temperature",
                    "soil_humidity",
                    "air_humidity",
                    "measured_at",
                ]
            ].rename(
                columns={
                    "id": "ID",
                    "parcel_name": "Parcelle",
                    "sensor_id": "Capteur",
                    "temperature": "Température (°C)",
                    "soil_humidity": "Humidité Sol (%)",
                    "air_humidity": "Humidité Air (%)",
                    "measured_at": "Date/Heure Mesure",
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune mesure enregistrée sur cette période.")

    with c2:
        st.markdown("#### 🩺 État détaillé de l'architecture")
        st.json(
            {
                "collection_service": col_health or {"status": "offline", "error": col_err},
                "processing_service": proc_health or {"status": "offline", "error": proc_err},
            }
        )

        with st.expander("🧪 Envoyer une mesure de test manuelle"):
            with st.form("manual_measurement_form"):
                sensor_choice = st.selectbox(
                    "Capteur",
                    [s["id"] for s in sensors] if sensors else ["sensor-001", "sensor-unknown"],
                )
                t_val = st.number_input("Température (°C)", value=37.5, step=0.5)
                s_val = st.number_input("Humidité du sol (%)", value=21.0, step=1.0)
                a_val = st.number_input("Humidité de l'air (%)", value=45.0, step=1.0)
                submitted = st.form_submit_button("Envoyer à collection-service")
                if submitted:
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

# ============================================================================
# PAGE 2 : SUPERVISION DES PARCELLES
# ============================================================================
elif page == "2. Supervision des parcelles":
    st.subheader("🌾 Supervision par parcelle agricole")

    if parcels:
        df_parcels = pd.DataFrame(parcels).rename(
            columns={
                "id": "ID Parcelle",
                "nom": "Nom de la parcelle",
                "localisation": "Localisation",
                "active_sensors": "Capteurs Actifs",
                "total_sensors": "Total Capteurs",
            }
        )
        st.dataframe(
            df_parcels[
                [
                    "ID Parcelle",
                    "Nom de la parcelle",
                    "Localisation",
                    "Capteurs Actifs",
                    "Total Capteurs",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        parcel_map = {f"{p['id']} — {p['nom']}": p["id"] for p in parcels}
        chosen_label = st.selectbox("Sélectionner une parcelle :", list(parcel_map.keys()))
        chosen_parcel_id = parcel_map[chosen_label]

        p_stats, _ = api_get(
            PROCESSING_SERVICE_URL,
            "/api/v1/statistics",
            {"parcel_id": chosen_parcel_id, "period": selected_period},
        )
        p_meas, _ = api_get(
            PROCESSING_SERVICE_URL,
            f"/api/v1/parcels/{chosen_parcel_id}/measurements",
            {"period": selected_period, "limit": 50},
        )

        if p_stats:
            st.markdown(f"#### Indicateurs statistiques — `{chosen_parcel_id}` ({selected_period_label})")
            c1, c2, c3 = st.columns(3)
            t_stat = p_stats.get("temperature", {})
            s_stat = p_stats.get("soil_humidity", {})
            a_stat = p_stats.get("air_humidity", {})

            c1.metric(
                "🌡️ Température moyenne (°C)",
                f"{t_stat.get('average') or '-'} °C",
                f"Min: {t_stat.get('min') or '-'} °C | Max: {t_stat.get('max') or '-'} °C",
            )
            c2.metric(
                "💧 Humidité du sol moyenne (%)",
                f"{s_stat.get('average') or '-'} %",
                f"Min: {s_stat.get('min') or '-'} % | Max: {s_stat.get('max') or '-'} %",
            )
            c3.metric(
                "🌬️ Humidité de l'air moyenne (%)",
                f"{a_stat.get('average') or '-'} %",
                f"Min: {a_stat.get('min') or '-'} % | Max: {a_stat.get('max') or '-'} %",
            )

        st.markdown("#### Dernières mesures de la parcelle")
        if p_meas:
            st.dataframe(pd.DataFrame(p_meas), use_container_width=True, hide_index=True)
        else:
            st.info("Aucune mesure disponible pour cette parcelle sur la période sélectionnée.")

# ============================================================================
# PAGE 3 : ANALYSE DES MESURES
# ============================================================================
elif page == "3. Analyse des mesures":
    st.subheader("📈 Analyse temporelle et évolution des mesures")

    col_f1, col_f2 = st.columns(2)
    parcel_options = {"Toutes les parcelles": None}
    if parcels:
        for p in parcels:
            parcel_options[f"{p['id']} — {p['nom']}"] = p["id"]
    selected_parcel_filter = col_f1.selectbox("Filtrer par parcelle :", list(parcel_options.keys()))
    parcel_id_filter = parcel_options[selected_parcel_filter]

    sensor_options = {"Tous les capteurs": None}
    if sensors:
        for s in sensors:
            if not parcel_id_filter or s["parcelle_id"] == parcel_id_filter:
                sensor_options[f"{s['id']} ({s['nom']})"] = s["id"]
    selected_sensor_filter = col_f2.selectbox("Filtrer par capteur :", list(sensor_options.keys()))
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

        thresholds = (
            global_stats.get("thresholds", {})
            if global_stats
            else {"temperature_max": 35.0, "soil_humidity_min": 25.0, "air_humidity_min": 30.0}
        )

        # Graphique 1 : Température
        fig_temp = px.line(
            df,
            x="measured_at",
            y="temperature",
            color="sensor_id",
            markers=True,
            title="Évolution de la Température (°C)",
            labels={"measured_at": "Date et heure", "temperature": "Température (°C)", "sensor_id": "Capteur"},
        )
        fig_temp.add_hline(
            y=thresholds.get("temperature_max", 35.0),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Seuil max ({thresholds.get('temperature_max', 35.0)} °C)",
        )
        st.plotly_chart(fig_temp, use_container_width=True)

        # Graphique 2 : Humidité du sol
        fig_soil = px.line(
            df,
            x="measured_at",
            y="soil_humidity",
            color="sensor_id",
            markers=True,
            title="Évolution de l'Humidité du Sol (%)",
            labels={"measured_at": "Date et heure", "soil_humidity": "Humidité du sol (%)", "sensor_id": "Capteur"},
        )
        fig_soil.add_hline(
            y=thresholds.get("soil_humidity_min", 25.0),
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Seuil min ({thresholds.get('soil_humidity_min', 25.0)} %)",
        )
        st.plotly_chart(fig_soil, use_container_width=True)

        # Graphique 3 : Humidité de l'air
        fig_air = px.line(
            df,
            x="measured_at",
            y="air_humidity",
            color="sensor_id",
            markers=True,
            title="Évolution de l'Humidité de l'Air (%)",
            labels={"measured_at": "Date et heure", "air_humidity": "Humidité de l'air (%)", "sensor_id": "Capteur"},
        )
        fig_air.add_hline(
            y=thresholds.get("air_humidity_min", 30.0),
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Seuil min ({thresholds.get('air_humidity_min', 30.0)} %)",
        )
        st.plotly_chart(fig_air, use_container_width=True)

        # Export CSV optionnel (Section 3.2)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Télécharger les mesures filtrées (CSV)",
            data=csv_bytes,
            file_name="agrisense_mesures.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucune mesure disponible pour ces critères de filtrage.")

# ============================================================================
# PAGE 4 : ALERTES
# ============================================================================
elif page == "4. Alertes":
    st.subheader("🚨 Journal des alertes et dépassements de seuils")

    parcel_options = {"Toutes les parcelles": None}
    if parcels:
        for p in parcels:
            parcel_options[f"{p['id']} — {p['nom']}"] = p["id"]
    selected_parcel_alert = st.selectbox("Filtrer les alertes par parcelle :", list(parcel_options.keys()))

    alerts, alert_err = api_get(
        PROCESSING_SERVICE_URL,
        "/api/v1/alerts",
        {
            "parcel_id": parcel_options[selected_parcel_alert],
            "period": selected_period,
            "limit": 200,
        },
    )

    if alert_err:
        st.error(alert_err)
    elif alerts:
        df_alerts = pd.DataFrame(alerts)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Alertes affichées", len(df_alerts))
        c2.metric(
            "Alertes Température (> 35°C)",
            int((df_alerts["indicateur"] == "temperature").sum()),
        )
        c3.metric(
            "Alertes Hydriques (Sol < 25% ou Air < 30%)",
            int((df_alerts["indicateur"].isin(["soil_humidity", "air_humidity"])).sum()),
        )

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
                    "id": "ID Alerte",
                    "parcel_name": "Parcelle",
                    "sensor_id": "Capteur",
                    "indicateur": "Indicateur",
                    "valeur": "Valeur observée",
                    "seuil": "Seuil configuré",
                    "message": "Description",
                    "measured_at": "Date/Heure Mesure",
                    "statut": "Statut",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("Aucune alerte détectée sur la période sélectionnée.")

