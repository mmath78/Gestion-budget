import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

def categorize_transaction(description):
    categories = {
        "loyer": "Logement",
        "supermarché": "Alimentation",
        "restaurant": "Loisirs",
        "essence": "Transport",
        "salaire": "Revenus"
    }
    for key, value in categories.items():
        if key in description.lower():
            return value
    return "Autre"

def load_data(file):
    df = pd.read_csv(file)
    df["Catégorie"] = df["Description"].apply(categorize_transaction)
    return df

def create_sankey(df):
    sources = list(df["Catégorie"].unique())
    sources.append("Budget")  # Source globale
    source_indices = {category: i for i, category in enumerate(sources)}
    
    source = [source_indices["Budget"]] * len(df)
    target = [source_indices[cat] for cat in df["Catégorie"]]
    value = list(df["Montant"].abs())
    
    fig = go.Figure(go.Sankey(
        node=dict(
            label=sources,
            pad=15,
            thickness=20
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    ))
    return fig

# Interface Streamlit
st.title("Gestionnaire de Budget Interactif")
if "CONDA_DEFAULT_ENV" in os.environ:
    st.success(f"Environnement Anaconda détecté: {os.environ['CONDA_DEFAULT_ENV']}")
else:
    st.warning("Vous n'êtes pas dans un environnement Anaconda. Pensez à l'utiliser pour une meilleure gestion des dépendances.")

# Paramétrage du fichier
st.sidebar.header("Paramètres du fichier")
default_filename = "budget.csv"
filename = st.sidebar.text_input("Nom du fichier CSV :", default_filename)

file = st.file_uploader("Importer un fichier bancaire (CSV)", type=["csv"])

if file:
    df = load_data(file)
    st.write(df)
    fig = create_sankey(df)
    st.plotly_chart(fig)
    
    # Ajout de nouvelles dépenses
    st.sidebar.subheader("Ajouter une dépense")
    new_date = st.sidebar.date_input("Date de la dépense")
    new_description = st.sidebar.text_input("Description")
    new_montant = st.sidebar.number_input("Montant", value=0.0, step=0.01)
    new_category = st.sidebar.text_input("Catégorie (optionnel)")
    
    if st.sidebar.button("Ajouter la dépense"):
        new_entry = pd.DataFrame({
            "Date": [new_date],
            "Description": [new_description],
            "Montant": [new_montant],
            "Catégorie": [new_category if new_category else categorize_transaction(new_description)]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        st.success("Dépense ajoutée avec succès !")
    
    # Enregistrement des modifications
    if st.sidebar.button("Enregistrer les modifications"):
        df.to_csv(filename, index=False, encoding="utf-8")
        st.sidebar.success(f"Fichier enregistré sous {filename}")
