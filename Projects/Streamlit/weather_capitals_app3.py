# app_etape_3.py

# --- Imports ---
import streamlit as st                       # interface web
import pandas as pd                          # tableaux
import requests                              # requêtes HTTP
                                             # plotly non utilisé ici (graphique à l’étape 4)

# --- Page config ---
st.set_page_config(page_title="🌍 Météo des capitales — Étape 3", layout="wide")

st.title("🌍 Météo des capitales")
st.caption("Étape 3 : interroger Open-Meteo et construire df2 (température & humidité)")

# --- 1) Charger capitales (réutilisation de l’étape 2) ---
@st.cache_data(show_spinner=True)            # cache pour éviter de recharger à chaque interaction
def load_capitals():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,latlng"  # endpoint restcountries
    r = requests.get(url, timeout=30)        # requête HTTP
    r.raise_for_status()                     # vérifie le statut HTTP
    data = r.json()                          # parse JSON

    rows = []                                # contiendra les lignes valides
    for country in data:                     # boucle pays
        name = country.get("name", {}).get("common")  # nom du pays
        if not name:
            continue
        if name in ["Israel", "South Africa"]:        # exclusions
            continue

        capitals = country.get("capital") or []       # capitales éventuelles
        latlng = country.get("latlng")                # lat/lng
        if not latlng or len(latlng) < 2:
            continue

        for cap in capitals:                          # ajout d'une ligne par capitale
            rows.append({
                "country": name,
                "capital": cap,
                "lat": latlng[0],
                "lng": latlng[1]
            })

    return pd.DataFrame(rows)                         # DataFrame des capitales

# --- 2) Fonction pour interroger Open-Meteo sur N capitales ---
@st.cache_data(show_spinner=True)            # cache pour limiter les appels API
def fetch_weather_for_capitals(capitals_df: pd.DataFrame, limit: int = 30):
    sample = capitals_df.iloc[:limit].copy() # prend les 'limit' premières capitales pour éviter de spammer l’API
    records = []                              # accumulera les réponses formatées

    for _, row in sample.iterrows():          # boucle ligne par ligne sur l’échantillon
        url2 = (                              # construit l’URL de l’API Open-Meteo
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={row['lat']}&longitude={row['lng']}"
            "&current=temperature_2m,relative_humidity_2m"
        )
        try:
            r2 = requests.get(url2, timeout=20)  # appel Open-Meteo
            r2.raise_for_status()                # lève en cas d’erreur HTTP
            data2 = r2.json()                    # parse JSON

            # extrait les champs utiles (avec get pour éviter KeyError)
            records.append({
                "country": row["country"],                               # pays
                "name": row["capital"],                                  # alias pour le graphe
                "capital": row["capital"],                               # capitale
                "elevation": data2.get("elevation"),                     # altitude de la grille
                "timezone": data2.get("timezone"),                       # fuseau horaire
                "temperature_metric": data2.get("current_units", {}).get("temperature_2m"),  # unité de T°
                "temperature": data2.get("current", {}).get("temperature_2m"),               # T° actuelle
                "humidity_metric": data2.get("current_units", {}).get("relative_humidity_2m"),# unité humidité
                "humidity": data2.get("current", {}).get("relative_humidity_2m"),            # humidité actuelle
            })
        except requests.RequestException:
            # si une ville échoue (réseau, quota…), on la saute pour ne pas bloquer l’app
            continue

    return pd.DataFrame(records)               # DataFrame final df2

# --- 3) UI : choisir le nombre de capitales à interroger ---
with st.sidebar:                               # barre latérale pour les contrôles
    st.header("Options")
    limit = st.number_input(                   # champ numérique pour limiter l’échantillon API
        "Nombre max de capitales (API Open-Meteo)", 
        min_value=1, max_value=30, value=5, step=1
    )

# --- 4) Exécution : charger capitales + météo ---
with st.spinner("Chargement des capitales…"):  # spinner de progression
    capitals_df = load_capitals()              # DataFrame des capitales

with st.spinner("Interrogation Open-Meteo…"):  # spinner pendant les appels API
    df2 = fetch_weather_for_capitals(capitals_df, limit=int(limit))  # DataFrame météo

# --- 5) Affichage du DataFrame df2 ---
st.subheader("Données météo (df2)")
st.dataframe(df2, use_container_width=True)    # affiche df2
st.success(f"{len(df2)} enregistrements météo récupérés.")  # petit récap
