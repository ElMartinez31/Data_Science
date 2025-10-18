# app_etape_4.py

# --- Imports ---
import streamlit as st                     # interface
import pandas as pd                        # dataframes
import requests                            # HTTP
import plotly.express as px                # graphes interactifs
import random

# --- Page config ---
st.set_page_config(page_title="🌍 Météo des capitales — Étape 4", layout="wide")

st.title("🌍 Météo des capitales")
st.caption("Étape 4 : filtre par pays + graphe Plotly")

# --- 1) Fonctions utilitaires (identiques aux étapes précédentes) ---
@st.cache_data(show_spinner=True)
def load_capitals():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,latlng"  # API restcountries
    r = requests.get(url, timeout=30)       # requête HTTP
    r.raise_for_status()                    # vérifie le statut
    data = r.json()                         # parse JSON
    rows = []                               # contiendra les lignes

    for country in data:                    # boucle pays
        name = country.get("name", {}).get("common")  # nom
        if not name:
            continue
        if name in ["Israel", "South Africa"]:        # exclusions
            continue
        capitals = country.get("capital") or []       # liste des capitales
        latlng = country.get("latlng")                # coordonnées
        if not latlng or len(latlng) < 2:             # saute si coordonnées manquantes
            continue
        for cap in capitals:                          # une ligne par capitale
            rows.append({
                "country": name,
                "capital": cap,
                "lat": latlng[0],
                "lng": latlng[1]
            })
    shuffled = pd.DataFrame(rows).sample(frac=1, random_state = None).reset_index(drop = True) # shuffle capitals
    return  shuffled                         # DataFrame capitales

@st.cache_data(show_spinner=True)
def fetch_weather_for_capitals(capitals_df: pd.DataFrame, limit: int = 30):
    sample = capitals_df.iloc[:limit].copy()          # échantillon limité
    records = []                                      # accumule les réponses formatées
    for _, row in sample.iterrows():                  # boucle sur l’échantillon
        url2 = (                                      # URL Open-Meteo
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={row['lat']}&longitude={row['lng']}"
            "&current=temperature_2m,relative_humidity_2m"
        )
        try:
            r2 = requests.get(url2, timeout=20)       # appel API
            r2.raise_for_status()                     # vérifie le statut
            data2 = r2.json()                         # parse JSON

            records.append({                          # ajoute un enregistrement formaté
                "country": row["country"],
                "name": row["capital"],
                "capital": row["capital"],
                "elevation": data2.get("elevation"),
                "timezone": data2.get("timezone"),
                "temperature_metric": data2.get("current_units", {}).get("temperature_2m"),
                "temperature": data2.get("current", {}).get("temperature_2m"),
                "humidity_metric": data2.get("current_units", {}).get("relative_humidity_2m"),
                "humidity": data2.get("current", {}).get("relative_humidity_2m"),
            })
        except requests.RequestException:             # en cas d’échec, on ignore cette capitale
            continue
    return pd.DataFrame(records)                      # df2

@st.cache_data(show_spinner=True)
def fetch_history_weather_capital(lat : float, lng : float, start_date: str = "2024-05-01", end_date : str = "2024-10-01"):    
    url3 = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={lat}&longitude={lng}"
    f"&start_date={start_date}&end_date={end_date}"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    f"&timezone=Europe%2FParis"
)
    try :
        r3 = requests.get(url3, timeout=30)
        r3.raise_for_status()
        data3 = r3.json()
        hist_dict = {
                    "days" : data3["daily"]["time"],
                    "temp_unit" : data3["daily_units"]["temperature_2m_max"],
                    "precipitation_unit" : data3["daily_units"]["precipitation_sum"],
                    "max_temp_daily" : data3["daily"]["temperature_2m_max"],
                    "min_temp_daily" : data3["daily"]["temperature_2m_min"],
                    "sum_precipitation" : data3["daily"]["precipitation_sum"]
                    }
        
        return pd.DataFrame(hist_dict)

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erreur HTTP {r3.status_code} : {e}")
    except requests.exceptions.Timeout:
        raise RuntimeError("La requête a expiré (timeout).")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Erreur de connexion au serveur Open-Meteo.")
    except Exception as e:
        raise RuntimeError(f"Erreur inattendue : {e}")


# --- 2) Widgets : contrôle du volume + filtre par pays ---
with st.sidebar:                                      # barre latérale
    st.header("Options")
    limit = st.number_input(                          # limite d’interrogation API
        "Nombre max de capitales (API Open-Meteo)",
        min_value=1, max_value=30, value=5, step=1
    )

# --- 3) Charger données + météo ---
with st.spinner("Chargement des capitales…"):
    capitals_df = load_capitals()                     # DataFrame capitales

with st.spinner("Interrogation Open-Meteo…"):
    df2 = fetch_weather_for_capitals(capitals_df, limit=int(limit))  # DataFrame météo



# --- 4) Sélecteur de pays (multiselect) ---
all_countries = sorted(df2["country"].dropna().unique().tolist())   # liste de pays présents
default_countries = all_countries[:10]                               # sélection par défaut
selected_countries = st.multiselect(                                 # widget multi-sélection
    "Sélectionnez un ou plusieurs pays à afficher",
    options=all_countries,
    default=default_countries,
)

# --- 5) Filtrage des données selon les pays choisis ---
if selected_countries:                                               # si l’utilisateur a choisi des pays
    df2_filtered = df2[df2["country"].isin(selected_countries)].copy() # on filtre
else:
    df2_filtered = df2.copy()                                        # sinon, on prend tout

# --- 6) Affichage du DataFrame df2 complet + résumé ---
st.subheader("Données météo (df2)")
st.dataframe(df2, use_container_width=True)                          # montre l’ensemble des données
st.caption(f"Affichage du graphe filtré sur : {len(df2_filtered)} points.")


# --- 7) Graphe Plotly (température vs humidité) ---
st.subheader("Température vs. humidité (par capitale)")
if df2_filtered.empty:                                               # si rien après filtre, message d’info
    st.info("Aucune donnée à afficher avec le filtre actuel.")
else:
    fig = px.scatter(                                                # scatter plot interactif
        df2_filtered,                                                # DataFrame filtré
        x="temperature",                                             # axe X = température
        y="humidity",                                                # axe Y = humidité
        text="name",                                                 # nom de la capitale à côté du point
        hover_name="name",                                           # nom au survol
        hover_data={                                                 # infos supplémentaires dans le tooltip
            "temperature": True,
            "humidity": True,
            "elevation": True,
            "timezone": True,
            "country": True,
        },
        title="Température et humidité dans différentes capitales",  # titre du graphique
    )
    fig.update_traces(                                               # options de style des points/labels
        textposition="top center",                                   # position du label
        marker=dict(size=10)                                         # taille des points
    )
    fig.update_layout(                                               # titres des axes + thème + marges
        xaxis_title="Température (°C)",
        yaxis_title="Humidité (%)",
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)                   # rendu du graphe dans Streamlit

# ---Petits indicateurs de synthèse ---
col1, col2, col3 = st.columns(3)                                     # 3 colonnes responsives
with col1:
    st.metric("Capitales interrogées", len(df2))                     # nombre total de points
with col2:
    st.metric("Affichées sur le graphe", len(df2_filtered))          # nombre après filtre
with col3:
    # calcule une moyenne si au moins une température non nulle/non NaN est présente
    if not df2_filtered.empty and pd.notna(df2_filtered["temperature"]).any():
        st.metric("Température moyenne", f"{df2_filtered['temperature'].mean():.1f} °C")



# capital selector for history data
with st.sidebar:
    st.header("Historique")
    # Liste des pays / capitales à partir du DataFrame des capitales
    capital_all = sorted(capitals_df["capital"].dropna().unique().tolist())
    # Valeurs par défaut: premier pays et sa première capitale
    default_capital = capital_all[0] if capital_all else None

    capital_sel = st.selectbox("Capitale", capital_all, index=0 if capital_all else None)

    # Période de l'historique (optionnelle)
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("Début", pd.to_datetime("2024-05-01"))
    with col_b:
        end_date = st.date_input("Fin", pd.to_datetime("2024-10-01"))

with st.spinner("Interrogation des archives pour la méteo historique…"):
    selected_row = capitals_df[capitals_df["capital"] == capital_sel].iloc[0]
    country_name = selected_row["country"]
    df3 = fetch_history_weather_capital(lat = selected_row["lat"], lng = selected_row["lng"], start_date=start_date.strftime("%Y-%m-%d"), end_date = end_date.strftime("%Y-%m-%d"))
    # df3 = fetch_history_weather_capital(capitals_df)


# ---affichage df3---
st.subheader("Données historiques (df3)")
st.dataframe(df3, use_container_width=True)

# données historiques temp
st.subheader(f"Temperatures historiques {capital_sel}, {country_name}")
if df3.empty:                                               # si rien après filtre, message d’info
    st.info("Aucune donnée à afficher avec le filtre actuel.")
else:
    fig2 = px.line(                                                # scatter plot interactif
        df3,                                                # DataFrame filtré
        x="days",                                             # axe X = température
        y=["max_temp_daily", "min_temp_daily"],                                                # axe Y = humidité
        title="Max Temp Daily",
        color_discrete_sequence=["red", "blue"],                                           # nom au survol
    )
    fig2.update_layout(                                               # titres des axes + thème + marges
    yaxis_title="Température (°C)",
    xaxis_title="Days",
    template="plotly_white",
    margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

# donn"es historiques précipitations
st.subheader(f"Precipitations historiques {capital_sel}, {country_name}")
if df3.empty:                                               # si rien après filtre, message d’info
    st.info("Aucune donnée à afficher avec le filtre actuel.")
else:
    fig3 = px.line(                                                # scatter plot interactif
        df3,                                                # DataFrame filtré
        x="days",                                             # axe X = température
        y=["sum_precipitation"],                                                # axe Y = humidité
        title="Precipitations (mm)",
        color_discrete_sequence=["purple"],                                           # nom au survol
    )
    fig3.update_layout(                                               # titres des axes + thème + marges
    yaxis_title="Precipitations (mm)",
    xaxis_title="Days",
    template="plotly_white",
    margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

