"""
Script de chargement des données nettoyées de sorties / vers la base CCFL.
Utilise SQLAlchemy 2 et psycopg, avec gestion des rejets, journalisation, 
insertion par lots (batch >= 500) et idempotence.
"""

import os
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Charger les variables du fichier .env
load_dotenv()

# Récupération de l'URL de connexion depuis le .env ou valeur par défaut
DB_NAME = "ccfl"

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/ccfl"
)

# Chemins des fichiers
PATH_SITES = "data/sites.csv"
PATH_MATERIEL = "sorties/materiel_propre.csv"
PATH_ASSOCIATIONS = "sorties/associations_propre.csv"
PATH_RESERVATIONS = "sorties/reservations_propre.csv"
PATH_REJETS = "sorties/rejets_chargement.csv"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def clean_nan(val):
    """Convertit les NaN/NaT pandas en None (NULL SQL)."""
    if pd.isna(val):
        return None
    if isinstance(val, (float, np.floating)) and np.isnan(val):
        return None
    if isinstance(val, str) and val.strip().lower() in ["nan", "nat", ""]:
        return None
    return val

def charger_sites(engine, batch_size: int = 500) -> tuple[int, int, list]:
    """Charge la table site depuis data/sites.csv."""
    table_name = "site"
    lues = 0
    inserees = 0
    rejets = []

    if not os.path.exists(PATH_SITES):
        logger.error(f"Fichier {PATH_SITES} introuvable.")
        return lues, inserees, rejets

    df = pd.read_csv(PATH_SITES)
    lues = len(df)

    records = []
    for _, row in df.iterrows():
        try:
            record = {
                "code_site": clean_nan(row.get("code_site")),
                "nom": clean_nan(row.get("nom")),
                "commune": clean_nan(row.get("commune")),
                "annee_ouverture": int(row["annee_ouverture"]) if clean_nan(row.get("annee_ouverture")) is not None else None,
                "surface_m2": int(row["surface_m2"]) if clean_nan(row.get("surface_m2")) is not None else None,
            }
            records.append(record)
        except Exception as e:
            rejets.append({
                "table": table_name,
                "donnees": str(row.to_dict()),
                "motif_rejet": f"Erreur de formatage : {e}"
            })

    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            if batch:
                stmt = text("""
                    INSERT INTO site (code_site, nom, commune, annee_ouverture, surface_m2)
                    VALUES (:code_site, :nom, :commune, :annee_ouverture, :surface_m2)
                    ON CONFLICT (code_site) DO UPDATE SET
                        nom = EXCLUDED.nom,
                        commune = EXCLUDED.commune,
                        annee_ouverture = EXCLUDED.annee_ouverture,
                        surface_m2 = EXCLUDED.surface_m2
                """)
                conn.execute(stmt, batch)
                inserees += len(batch)

    return lues, inserees, rejets

def charger_materiel(engine, batch_size: int = 500) -> tuple[int, int, list]:
    """Charge la table materiel depuis sorties/materiel_propre.csv."""
    table_name = "materiel"
    lues = 0
    inserees = 0
    rejets = []

    if not os.path.exists(PATH_MATERIEL):
        logger.error(f"Fichier {PATH_MATERIEL} introuvable.")
        return lues, inserees, rejets

    df = pd.read_csv(PATH_MATERIEL)
    lues = len(df)

    with engine.connect() as conn:
        valid_sites = set(row[0] for row in conn.execute(text("SELECT code_site FROM site")).fetchall())

    records = []
    for _, row in df.iterrows():
        try:
            code_site = clean_nan(row.get("code_site"))
            if code_site not in valid_sites:
                rejets.append({
                    "table": table_name,
                    "donnees": str(row.to_dict()),
                    "motif_rejet": f"Code site inconnu/orphelin : {code_site}"
                })
                continue

            annee_achat = clean_nan(row.get("annee_achat"))
            valeur_achat = clean_nan(row.get("valeur_achat"))

            record = {
                "id_materiel": clean_nan(row.get("id_materiel")),
                "reference": clean_nan(row.get("reference")),
                "designation": clean_nan(row.get("designation")),
                "categorie": clean_nan(row.get("categorie")),
                "etat": clean_nan(row.get("etat")),
                "annee_achat": int(float(annee_achat)) if annee_achat is not None else None,
                "valeur_achat": float(valeur_achat) if valeur_achat is not None else None,
                "code_site": code_site
            }
            records.append(record)
        except Exception as e:
            rejets.append({
                "table": table_name,
                "donnees": str(row.to_dict()),
                "motif_rejet": f"Erreur de formatage : {e}"
            })

    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            if batch:
                stmt = text("""
                    INSERT INTO materiel (id_materiel, reference, designation, categorie, etat, annee_achat, valeur_achat, code_site)
                    VALUES (:id_materiel, :reference, :designation, :categorie, :etat, :annee_achat, :valeur_achat, :code_site)
                    ON CONFLICT (id_materiel) DO UPDATE SET
                        reference = EXCLUDED.reference,
                        designation = EXCLUDED.designation,
                        categorie = EXCLUDED.categorie,
                        etat = EXCLUDED.etat,
                        annee_achat = EXCLUDED.annee_achat,
                        valeur_achat = EXCLUDED.valeur_achat,
                        code_site = EXCLUDED.code_site
                """)
                conn.execute(stmt, batch)
                inserees += len(batch)

    return lues, inserees, rejets

def charger_associations(engine, batch_size: int = 500) -> tuple[int, int, list]:
    """Charge la table association depuis sorties/associations_propre.csv."""
    table_name = "association"
    lues = 0
    inserees = 0
    rejets = []

    if not os.path.exists(PATH_ASSOCIATIONS):
        logger.error(f"Fichier {PATH_ASSOCIATIONS} introuvable.")
        return lues, inserees, rejets

    df = pd.read_csv(PATH_ASSOCIATIONS, dtype={"code_postal": str})
    lues = len(df)

    with engine.connect() as conn:
        valid_sites = set(row[0] for row in conn.execute(text("SELECT code_site FROM site")).fetchall())

    records = []
    for _, row in df.iterrows():
        try:
            code_site = clean_nan(row.get("code_site"))
            if code_site not in valid_sites:
                rejets.append({
                    "table": table_name,
                    "donnees": str(row.to_dict()),
                    "motif_rejet": f"Code site inconnu/orphelin : {code_site}"
                })
                continue

            conv_raw = clean_nan(row.get("convention_active"))
            if conv_raw is None:
                convention_active = None  # Devient NULL en base si manquant
            elif isinstance(conv_raw, str):
                val_lower = conv_raw.strip().lower()
                if val_lower in ["nan", "nat", ""]:
                    convention_active = None
                else:
                    convention_active = val_lower in ["oui", "true", "1", "yes"]
            else:
                convention_active = bool(conv_raw)

                
            code_postal = clean_nan(row.get("code_postal"))
            if code_postal is not None:
                code_postal = str(code_postal).strip()
                if len(code_postal) == 4:
                    code_postal = "0" + code_postal

            date_conv = clean_nan(row.get("date_convention"))

            record = {
                "id_association": clean_nan(row.get("id_association")),
                "nom": clean_nan(row.get("nom")),
                "type_association": clean_nan(row.get("type_association")),
                "commune": clean_nan(row.get("commune")),
                "code_postal": code_postal,
                "date_convention": date_conv,
                "convention_active": convention_active,
                "code_site": code_site
            }
            records.append(record)
        except Exception as e:
            rejets.append({
                "table": table_name,
                "donnees": str(row.to_dict()),
                "motif_rejet": f"Erreur de formatage : {e}"
            })

    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            if batch:
                stmt = text("""
                    INSERT INTO association (id_association, nom, type_association, commune, code_postal, date_convention, convention_active, code_site)
                    VALUES (:id_association, :nom, :type_association, :commune, :code_postal, :date_convention, :convention_active, :code_site)
                    ON CONFLICT (id_association) DO UPDATE SET
                        nom = EXCLUDED.nom,
                        type_association = EXCLUDED.type_association,
                        commune = EXCLUDED.commune,
                        code_postal = EXCLUDED.code_postal,
                        date_convention = EXCLUDED.date_convention,
                        convention_active = EXCLUDED.convention_active,
                        code_site = EXCLUDED.code_site
                """)
                conn.execute(stmt, batch)
                inserees += len(batch)

    return lues, inserees, rejets

def charger_reservations(engine, batch_size: int = 500) -> tuple[int, int, list]:
    """Charge la table reservation depuis sorties/reservations_propre.csv."""
    table_name = "reservation"
    lues = 0
    inserees = 0
    rejets = []

    if not os.path.exists(PATH_RESERVATIONS):
        logger.error(f"Fichier {PATH_RESERVATIONS} introuvable.")
        return lues, inserees, rejets

    df = pd.read_csv(PATH_RESERVATIONS, dtype={"id_reservation": str})
    lues = len(df)

    # Récupération des clés valides présentes en base
    with engine.connect() as conn:
        valid_materiel = set(int(row[0]) for row in conn.execute(text("SELECT id_materiel FROM materiel")).fetchall())
        valid_asso = set(int(row[0]) for row in conn.execute(text("SELECT id_association FROM association")).fetchall())
        valid_sites = set(str(row[0]).strip() for row in conn.execute(text("SELECT code_site FROM site")).fetchall())

    records = []
    for _, row in df.iterrows():
        try:
            # Conversion propre pour correspondre aux types des sets de validation
            raw_mat = clean_nan(row.get("id_materiel"))
            raw_asso = clean_nan(row.get("id_association"))
            raw_site = clean_nan(row.get("code_site"))

            id_mat = int(raw_mat) if raw_mat is not None else None
            id_asso = int(raw_asso) if raw_asso is not None else None
            code_site = str(raw_site).strip() if raw_site is not None else None

            if id_mat not in valid_materiel:
                rejets.append({
                    "table": table_name,
                    "donnees": str(row.to_dict()),
                    "motif_rejet": f"id_materiel inexistant en base : {id_mat}"
                })
                continue
            if id_asso not in valid_asso:
                rejets.append({
                    "table": table_name,
                    "donnees": str(row.to_dict()),
                    "motif_rejet": f"id_association inexistant en base : {id_asso}"
                })
                continue
            if code_site not in valid_sites:
                rejets.append({
                    "table": table_name,
                    "donnees": str(row.to_dict()),
                    "motif_rejet": f"code_site inexistant en base : {code_site}"
                })
                continue

            record = {
                "id_reservation": clean_nan(row.get("id_reservation")),
                "id_materiel": id_mat,
                "id_association": id_asso,
                "code_site": code_site,
                "quantite": int(row["quantite"]),
                "date_debut": clean_nan(row.get("date_debut")),
                "date_fin_prevue": clean_nan(row.get("date_fin_prevue")),
                "date_retour_reelle": clean_nan(row.get("date_retour_reelle"))
            }
            records.append(record)
        except Exception as e:
            rejets.append({
                "table": table_name,
                "donnees": str(row.to_dict()),
                "motif_rejet": f"Erreur de formatage : {e}"
            })

    # Insertion par lots (batch) avec SQLAlchemy 2.0
    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            if batch:
                stmt = text("""
                    INSERT INTO reservation (id_reservation, id_materiel, id_association, code_site, quantite, date_debut, date_fin_prevue, date_retour_reelle)
                    VALUES (:id_reservation, :id_materiel, :id_association, :code_site, :quantite, :date_debut, :date_fin_prevue, :date_retour_reelle)
                    ON CONFLICT (id_reservation) DO UPDATE SET
                        id_materiel = EXCLUDED.id_materiel,
                        id_association = EXCLUDED.id_association,
                        code_site = EXCLUDED.code_site,
                        quantite = EXCLUDED.quantite,
                        date_debut = EXCLUDED.date_debut,
                        date_fin_prevue = EXCLUDED.date_fin_prevue,
                        date_retour_reelle = EXCLUDED.date_retour_reelle
                """)
                conn.execute(stmt, batch)
                inserees += len(batch)

    return lues, inserees, rejets

def main():
    logger.info("=== DÉBUT DU CHARGEMENT EN BASE POSTGRESQL (CCFL) ===")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connexion réussie à la base de données : {DB_NAME}")
    except Exception as e:
        logger.error(f"Échec de la connexion à la base de données : {e}")
        return

    tous_les_rejets = []

    # 1. Chargement des sites
    logger.info("Chargement de la table 'site'...")
    lues_s, ins_s, rej_s = charger_sites(engine)
    tous_les_rejets.extend(rej_s)
    logger.info(f" -> Site : {lues_s} lues, {ins_s} insérées, {len(rej_s)} rejetées.")

    # 2. Chargement du matériel
    logger.info("Chargement de la table 'materiel'...")
    lues_m, ins_m, rej_m = charger_materiel(engine)
    tous_les_rejets.extend(rej_m)
    logger.info(f" -> Materiel : {lues_m} lues, {ins_m} insérées, {len(rej_m)} rejetées.")

    # 3. Chargement des associations
    logger.info("Chargement de la table 'association'...")
    lues_a, ins_a, rej_a = charger_associations(engine)
    tous_les_rejets.extend(rej_a)
    logger.info(f" -> Association : {lues_a} lues, {ins_a} insérées, {len(rej_a)} rejetées.")

    # 4. Chargement des réservations
    logger.info("Chargement de la table 'reservation'...")
    lues_r, ins_r, rej_r = charger_reservations(engine)
    tous_les_rejets.extend(rej_r)
    logger.info(f" -> Reservation : {lues_r} lues, {ins_r} insérées, {len(rej_r)} rejetées.")

    # Export des rejets éventuels dans sorties/rejets_chargement.csv
    os.makedirs(os.path.dirname(PATH_REJETS), exist_ok=True)
    if tous_les_rejets:
        df_rejets = pd.DataFrame(tous_les_rejets)
        df_rejets.to_csv(PATH_REJETS, index=False, encoding="utf-8")
        logger.warning(f"Total de {len(tous_les_rejets)} lignes rejetées exportées dans {PATH_REJETS}")
    else:
        pd.DataFrame(columns=["table", "donnees", "motif_rejet"]).to_csv(PATH_REJETS, index=False, encoding="utf-8")
        logger.info("Aucun rejet enregistré lors du chargement.")

    logger.info("=== CHARGEMENT TERMINÉ AVEC SUCCÈS ===")

if __name__ == "__main__":
    main()