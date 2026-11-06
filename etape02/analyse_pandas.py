import pandas as pd
import os

PATH_SITES = "data/sites.csv"
PATH_MATERIEL = "data/materiel.csv"
PATH_ASSOCIATIONS = "data/associations.csv"
PATH_RESERVATIONS = "data/reservations.csv"
PATH_SORTIE_TOP10 = "sorties/top10_materiel.csv"

def main():
    # 1. Chargement des CSV
    df_sites = pd.read_csv(PATH_SITES)
    df_materiel = pd.read_csv(PATH_MATERIEL)
    df_associations = pd.read_csv(PATH_ASSOCIATIONS)
    df_reservations = pd.read_csv(PATH_RESERVATIONS, dtype={"id_reservation": str})

    # 2. Conversion des dates en datetime
    df_reservations["date_debut"] = pd.to_datetime(df_reservations["date_debut"], errors="coerce")
    df_reservations["date_fin_prevue"] = pd.to_datetime(df_reservations["date_fin_prevue"], errors="coerce")
    df_reservations["date_retour_reelle"] = pd.to_datetime(df_reservations["date_retour_reelle"], errors="coerce")

    # 3. Forme, info et valeurs manquantes
    print("--- df_materiel ---")
    print("Shape:", df_materiel.shape)
    print(df_materiel.info())
    print("Valeurs manquantes:\n", df_materiel.isna().sum())

    print("\n--- df_reservations ---")
    print("Shape:", df_reservations.shape)
    print(df_reservations.info())
    print("Valeurs manquantes:\n", df_reservations.isna().sum())

    # 4. Traitement de la colonne valeur_achat
    # Cause : Présence de virgules décimales européennes (ex: '1484,04') qu'il faut convertir en points.
    df_materiel["valeur_achat"] = pd.to_numeric(
        df_materiel["valeur_achat"].astype(str).str.replace(",", "."),
        errors="coerce"
    )

    print("\n--- 10 matériels les plus chers ---")
    top_chers = df_materiel.sort_values(by="valeur_achat", ascending=False).head(10)
    print(top_chers[["reference", "designation", "categorie", "valeur_achat"]])

    print("\n--- Nombre de matériels par catégorie ---")
    print(df_materiel["categorie"].value_counts())

    print("\n--- Nombre de réservations et quantité totale par code_site ---")
    stats_site = df_reservations.groupby("code_site").agg(
        nb_reservations=("id_reservation", "size"),
        quantite_totale=("quantite", "sum")
    ).sort_values(by="nb_reservations", ascending=False)
    print(stats_site)

    # 6. Fusion des DataFrames (avec suppression préalable des doublons de clés si existants)
    df_materiel_unique = df_materiel.drop_duplicates(subset=["id_materiel"])
    df_associations_unique = df_associations.drop_duplicates(subset=["id_association"])

    df_complet = df_reservations.merge(
        df_materiel_unique, on="id_materiel", how="left", suffixes=("_res", "_mat")
    ).merge(
        df_associations_unique, on="id_association", how="left", suffixes=("_mat", "_asso")
    )

    print(f"\nNombre de lignes de df_complet : {len(df_complet)}")
    nb_sans_mat = df_complet["designation"].isna().sum()
    print(f"Nombre de lignes sans matériel correspondant : {nb_sans_mat}")

    # 7. Top 10 des matériels les plus réservés
    top_materiel_reserves = df_complet.groupby(["id_materiel", "designation"]).size().reset_index(name="nb_reservations")
    top_10_res = top_materiel_reserves.sort_values(by="nb_reservations", ascending=False).head(10)
    print("\n--- Top 10 des matériels les plus réservés ---")
    print(top_10_res)

    # Export en CSV dans sorties/
    os.makedirs(os.path.dirname(PATH_SORTIE_TOP10), exist_ok=True)
    top_10_res[["id_materiel", "designation", "nb_reservations"]].to_csv(PATH_SORTIE_TOP10, index=False, encoding="utf-8")
    print(f"Exporté avec succès dans {PATH_SORTIE_TOP10}")

if __name__ == "__main__":
    main()