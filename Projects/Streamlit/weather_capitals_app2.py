# app_etape_2.py

# --- Imports ---
import streamlit as st                # interface web
import pandas as pd                   # manipulation de données tabulaires
import requests                       # requêtes HTTP vers des APIs

# --- Page config ---
st.set_page_config(page_title="🌍 Météo des capitales — Étape 2", layout="wide")

st.title("🌍 Météo des capitales")
st.caption("Étape 2 : charger les capitales depuis restcountries et afficher le tableau")

# --- Fonction de chargement des capitales avec cache ---
@st.cache_data(show_spinner=True)     # mémorise le résultat pour éviter de re-télécharger à chaque interaction
def load_capitals():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,latlng"  # endpoint restcountries (champs limités)
    r = requests.get(url, timeout=30)  # envoi de la requête HTTP avec un timeout
    r.raise_for_status()               # lève une exception si le serveur renvoie une erreur
    data = r.json()                    # parse la réponse JSON en objet Python (liste de dicts)

    rows = []                          # liste qui accueillera les lignes valides
    for country in data:               # boucle sur chaque pays
        name = country.get("name", {}).get("common")  # récupère le nom courant du pays
        if not name:                   # si pas de nom, on saute
            continue

        # Exclure certains pays selon ton choix initial
        if name in ["Israel", "South Africa"]:  # filtre d’exclusion
            continue

        capitals = country.get("capital") or []  # la valeur "capital" peut être absente ou vide
        latlng = country.get("latlng")           # coordonnées (lat, lng)
        if not latlng or len(latlng) < 2:        # si pas de coordonnée exploitable, on saute
            continue

        for cap in capitals:                     # certains pays ont plusieurs capitales
            rows.append({
                "country": name,                 # nom du pays
                "capital": cap,                  # nom de la capitale
                "lat": latlng[0],                # latitude
                "lng": latlng[1]                 # longitude
            })

    return pd.DataFrame(rows)                    # conversion en DataFrame pandas

# --- Appel du chargement + affichage ---
with st.spinner("Chargement des capitales…"):    # montre un spinner pendant le chargement
    capitals_df = load_capitals()                # DataFrame des capitales filtrées

st.subheader("Capitales (source: restcountries)")
st.dataframe(capitals_df, use_container_width=True)  # affiche le tableau dans Streamlit
st.info(f"{len(capitals_df)} capitales chargées (pays exclus : Israel, South Africa).")  # petit résumé
