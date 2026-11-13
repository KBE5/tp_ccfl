
-- ============================================
-- CCFL - Schéma SQL du la gestion du prêt de matériel
-- ============================================
-- 0. Supprimer les tables existantes dans l'ordre inverse des dépendances

DROP TABLE IF EXISTS reservation CASCADE;
DROP TABLE IF EXISTS materiel CASCADE;
DROP TABLE IF EXISTS association CASCADE;
DROP TABLE IF EXISTS site CASCADE;

-- 1. TABLE SITE
CREATE TABLE site (
    code_site VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    commune VARCHAR(100) NOT NULL,
    annee_ouverture INT NOT NULL,
    surface_m2 INT NOT NULL
);

-- 2. TABLE MATERIEL
CREATE TABLE materiel (
    id_materiel VARCHAR(20) PRIMARY KEY,
    reference VARCHAR(50) NOT NULL,
    designation VARCHAR(150) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    etat VARCHAR(50) NOT NULL,
    annee_achat INT,
    valeur_achat NUMERIC(8,2),
    code_site VARCHAR(10) NOT NULL,

    CONSTRAINT fk_materiel_site
        FOREIGN KEY (code_site)
        REFERENCES site(code_site)
);

-- 3. TABLE ASSOCIATION
CREATE TABLE association (
    id_association VARCHAR(20) PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    type_association VARCHAR(50) NOT NULL,
    commune VARCHAR(100) NOT NULL,
    code_postal VARCHAR(10),
    date_convention DATE,
    convention_active BOOLEAN NOT NULL,
    code_site VARCHAR(10) NOT NULL,

    CONSTRAINT fk_association_site
        FOREIGN KEY (code_site)
        REFERENCES site(code_site)
);

-- 4. TABLE RESERVATION
CREATE TABLE reservation (
    id_reservation CHAR(7) PRIMARY KEY,
    id_materiel VARCHAR(20) NOT NULL,
    id_association VARCHAR(20) NOT NULL,
    code_site VARCHAR(10) NOT NULL,
    quantite INT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin_prevue DATE NOT NULL,
    date_retour_reelle DATE,

    CONSTRAINT fk_reservation_materiel
        FOREIGN KEY (id_materiel)
        REFERENCES materiel(id_materiel),

    CONSTRAINT fk_reservation_association
        FOREIGN KEY (id_association)
        REFERENCES association(id_association),

    CONSTRAINT fk_reservation_site
        FOREIGN KEY (code_site)
        REFERENCES site(code_site),

    CONSTRAINT chk_quantite
        CHECK (quantite > 0),

    CONSTRAINT chk_dates_reservation
        CHECK (date_fin_prevue >= date_debut),

    CONSTRAINT chk_id_reservation
        CHECK (id_reservation ~ '^R[0-9]{6}$')
);


