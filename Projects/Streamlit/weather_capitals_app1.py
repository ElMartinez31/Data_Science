# weather_capitals_app1.py

# --- Import des librairies nécessaires ---
import streamlit as st  # bibliothèque pour créer l'interface web simplement

# --- Configuration de la page ---
st.set_page_config(               # configure l'onglet et la mise en page
    page_title="🌍 Météo des capitales",  # titre de l'onglet du navigateur
    layout="wide"                 # mise en page large
)

# --- Contenu minimal (app vide) ---
st.title("🌍 Météo des capitales")      # titre principal visible dans la page
st.caption("Étape 1 : squelette de l’application")  # petite légende explicative
st.write("L’app est bien lancée.")
