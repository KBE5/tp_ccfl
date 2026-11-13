# Modélisation des Données — CCFL (Étape 4)

## 1. Modèle Conceptuel de Données (MCD)

Le système gère quatre entités principales dans le cadre du prêt de matériel intercommunal, basées strictement sur les structures des fichiers sources (`sites.csv`, `materiel.csv`, `associations.csv`, `reservations.csv`) :

### Entités et Propriétés :
* **SITE** (`code_site`, `nom`, `commune`, `annee_ouverture`, `surface_m2`)
* **MATERIEL** (`id_materiel`, `reference`, `designation`, `categorie`, `etat`, `annee_achat`, `valeur_achat`)
* **ASSOCIATION** (`id_association`, `nom`, `type_association`, `commune`, `code_postal`, `date_convention`, `convention_active`)
* **RESERVATION** (`id_reservation`, `quantite`, `date_debut`, `date_fin_prevue`, `date_retour_reelle`)

*(Note : Dans le MCD pur, les clés étrangères pour relier deux entités comme `code_site`, `id_materiel` et `id_association` sont portées par les associations et matérialisées lors du passage au MLD).*

### Associations et Cardinalités :
* **SITE — MATERIEL** (*stocker*) : Un site stocke 1 ou plusieurs matériels (`1,N`), un matériel est stocké dans 1 et 1 seul site (`1,1`).
* **SITE — ASSOCIATION** (*rattacher*) : Un site rattache 1 ou plusieurs associations (`1,N`), une association est rattachée à 1 et 1 seul site (`1,1`).
* **SITE — RESERVATION** (*enregistrer*) : Un site enregistre 0 ou plusieurs réservations (`0,N`), une réservation est effectuée auprès d'1 et 1 seul site (`1,1`).
* **ASSOCIATION — RESERVATION** (*effectuer*) : Une association effectue 0 ou plusieurs réservations (`0,N`), une réservation est effectuée par 1 et 1 seule association (`1,1`).
* **MATERIEL — RESERVATION** (*concerner*) : Un matériel fait l'objet de 0 ou plusieurs réservations (`0,N`), une réservation concerne 1 et 1 seul matériel (`1,1`).

### Schéma Mermaid du MCD
```mermaid
erDiagram
    SITE ||--|{ MATERIEL : "stocke (1,1 / 1,N)"
    SITE ||--|{ ASSOCIATION : "rattache (1,1 / 1,N)"
    SITE ||--o{ RESERVATION : "enregistre (1,1 / 0,N)"
    ASSOCIATION ||--o{ RESERVATION : "effectue (1,1 / 0,N)"
    MATERIEL ||--o{ RESERVATION : "concerne (1,1 / 0,N)"

    SITE {
        string code_site PK
        string nom
        string commune
        int annee_ouverture
        int surface_m2
    }
    MATERIEL {
        string id_materiel PK
        string reference
        string designation
        string categorie
        string etat
        int annee_achat
        decimal valeur_achat
    }
    ASSOCIATION {
        string id_association PK
        string nom
        string type_association
        string commune
        string code_postal
        date date_convention
        boolean convention_active
    }
    RESERVATION {
        string id_reservation PK
        int quantite
        date date_debut
        date date_fin_prevue
        date date_retour_reelle
    }



## 2. Modèle Logique de Données (MLD)

Lors de la dérivation du Modèle Conceptuel de Données (MCD) vers le Modèle Logique de Données (MLD), les associations de cardinalité `(1,1)` du côté de l'entité fille se traduisent par l'intégration explicite des clés étrangères (FK) et la définition précise du type de chaque attribut pour PostgreSQL :

### 1. `site`

* `code_site` : `VARCHAR(10)` — Clé Primaire (**PK**)
* `nom` : `VARCHAR(100)` (**NON NULL**)
* `commune` : `VARCHAR(100)` (**NON NULL**)
* `annee_ouverture` : `INT` (**NON NULL**)
* `surface_m2` : `INT` (**NON NULL**)

### 2. `materiel`

* `id_materiel` : `VARCHAR(20)` — Clé Primaire (**PK**)
* `reference` : `VARCHAR(50)` (**NON NULL**)
* `designation` : `VARCHAR(150)` (**NON NULL**)
* `categorie` : `VARCHAR(50)` (**NON NULL**)
* `etat` : `VARCHAR(50)` (**NON NULL**)
* `annee_achat` : `INT` (NULL autorisé)
* `valeur_achat` : `DECIMAL(8,2)` ou `NUMERIC(8,2)` (NULL autorisé)
* `code_site` : `VARCHAR(10)` — Clé Étrangère (**FK**) faisant référence à `site(code_site)` (**NON NULL**)

### 3. `association`

* `id_association` : `VARCHAR(20)` — Clé Primaire (**PK**)
* `nom` : `VARCHAR(150)` (**NON NULL**)
* `type_association` : `VARCHAR(50)` (**NON NULL**)
* `commune` : `VARCHAR(100)` (**NON NULL**)
* `code_postal` : `VARCHAR(10)` (NULL autorisé)
* `date_convention` : `DATE` (NULL autorisé)
* `convention_active` : `BOOLEAN` (**NON NULL**)
* `code_site` : `VARCHAR(10)` — Clé Étrangère (**FK**) faisant référence à `site(code_site)` (**NON NULL**)

### 4. `reservation`

* `id_reservation` : `CHAR(7)` — Clé Primaire (**PK**)
* `id_materiel` : `VARCHAR(20)` — Clé Étrangère (**FK**) faisant référence à `materiel(id_materiel)` (**NON NULL**)
* `id_association` : `VARCHAR(20)` — Clé Étrangère (**FK**) faisant référence à `association(id_association)` (**NON NULL**)
* `code_site` : `VARCHAR(10)` — Clé Étrangère (**FK**) faisant référence à `site(code_site)` (**NON NULL**)
* `quantite` : `INT` (**NON NULL**, `CHECK (quantite > 0)`)
* `date_debut` : `DATE` (**NON NULL**)
* `date_fin_prevue` : `DATE` (**NON NULL**, `CHECK (date_fin_prevue >= date_debut)`)
* `date_retour_reelle` : `DATE` (NULL autorisé)


## 3. Justifications techniques

* **Type de la clé primaire de `reservation` (`id_reservation`) :** Les identifiants sources étant strictement formatés sur le modèle `R250000` (1 lettre suivie de 6 chiffres), le type `CHAR(7)` est choisi. Ce type de chaîne à longueur fixe évite le surcoût de gestion de taille variable, garantit le format métier et optimise l'indexation de la clé primaire.
* **Type de `valeur_achat` (`DECIMAL(8,2)` / `NUMERIC(8,2)`) :** Le type `DECIMAL` (strict synonyme de `NUMERIC` dans PostgreSQL) est retenu au détriment d'un type flottant (`FLOAT` ou `REAL`). Les types à virgule flottante stockent les valeurs en binaire et génèrent des erreurs d'arrondi incompatibles avec les calculs comptables et financiers. `DECIMAL(8,2)` assure une précision exacte au centime près.
* **Représentation de `convention_active` :** Codée sous forme de chaîne (`oui` / `non`) dans le fichier CSV source, cette donnée est convertie en type natif `BOOLEAN` (`TRUE` / `FALSE`) en base. Ce typage réduit l'espace de stockage, élimine les risques d'erreurs de casse ou de frappe, et accélère les requêtes de filtrage.
* **Gestion de `date_retour_reelle` (valeur nulle autorisée) :** Selon les règles de gestion de la CCFL, l'absence de date de retour réelle ne constitue pas une donnée manquante erronée, mais caractérise un **prêt en cours** . La colonne doit donc impérativement accepter la valeur `NULL` pour refléter l'état réel du stock disponible.
* **Présence de `code_site` sur `materiel`, `association` et `reservation` :** Il ne s'agit pas d'une redondance inutile à supprimer, mais de trois informations métier distinctes :
  1. Sur `materiel` : définit le pôle de stockage physique où l'équipement est rattaché et inventorié.
  2. Sur `association` : désigne le pôle administratif de référence auprès duquel l'association a signé sa convention.
  3. Sur `reservation` : trace le pôle effectif de retrait et de retour du matériel lors du prêt (une association pouvant ponctuellement réserver un équipement disponible dans un autre pôle que son pôle d'origine).