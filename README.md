
# TP CCFL — Pilotage du prêt de matériel aux associations

## 1. Prérequis et base de données
Assurez-vous d'avoir installé **Python 3.12** (`pandas`, `sqlalchemy`, `psycopg`, `streamlit`) et **PostgreSQL 14+**, puis créez la base dédiée  sur `PostgreSQL`:
```bash
createdb ccfl
```

## 2. Variables d'environnement
Aucun mot de passe en dur n'est présent dans le code. Définissez les variables de connexion à la base avant d'exécuter les étapes 5 et 7 :
```bash
DATABASE_URL=postgresql+psycopg://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/ccfl
```

## 3. Ordre d'exécution des scripts (depuis la racine `tp-ccfl/`)
1. **Étape 1 (Exploration Python) :** `python etape01/exploration.py`
2. **Étape 2 (Analyse Pandas) :** `python etape02/analyse_pandas.py` (génère `sorties/top10_materiel.csv`)
3. **Étape 3 (Qualité & nettoyage) :** `python etape03/qualite.py` (génère les CSV propres et `sorties/rapport_qualite.md`)
4. **Étape 4 (Création du schéma SQL) :** `psql -d ccfl -f etape04/schema.sql` ou copier le script SQL et exécuez le ds le SQL Query de PostgresSQL
5. **Étape 5 (Chargement en base) :** `python etape05/chargement.py` >> charge la bdd `ccfl` avec les fichiers CSV néttoyés
6. **Étape 6 (Requêtes d'analyse) :** `psql -d ccfl -f etape06/analyses.sql`
ou copier le script SQL et exécuez le ds le SQL Query de PostgresSQL
7. **Étape 7 (Bonus — Catalogue Streamlit) :** `streamlit run etape07/app.py` >> Non effectué par manque de temps 