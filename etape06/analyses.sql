-- Question 1. Par site (code_site, nom) : nombre de réservations, quantité totale réservée
-- et nombre d'associations distinctes, trié par nombre de réservations décroissant.
-- Les sites sans réservation doivent apparaître avec 0.
SELECT
    s.code_site,
    s.nom,
    COUNT(r.id_reservation) AS nb_reservations,
    COALESCE(SUM(r.quantite), 0) AS quantite_totale_reservee,
    COUNT(DISTINCT r.id_association) AS nb_associations_distinctes
FROM site s
LEFT JOIN reservation r ON s.code_site = r.code_site
GROUP BY s.code_site, s.nom
ORDER BY nb_reservations DESC, s.code_site ASC;
-- Nombre de lignes obtenues : 5 lignes 
-- "POL-HAZ"	"Pole technique d'Hazebrouck"	1840	5698
-- "POL-MER"	"Depot intercommunal de Merville"	927	2810
-- "POL-BAI"	"Atelier municipal de Bailleul"	887	2795
-- "POL-EST"	"Reserve d'Estaires"	531	1739
-- "POL-NIE"	"Magasin de Nieppe"	375	1161


-- Question 2. Nombre de réservations par mois de date_debut, au format AAAA-MM, trié chronologiquement.
SELECT
    TO_CHAR(date_debut, 'YYYY-MM') AS mois_reservation,
    COUNT(id_reservation) AS nb_reservations
FROM reservation
GROUP BY TO_CHAR(date_debut, 'YYYY-MM')
ORDER BY mois_reservation ASC;
-- Nombre de lignes obtenues : 13 lignes
-- "2025-10"	46
-- "2025-11"	63
-- "2025-12"	119
-- "2026-01"	160
-- "2026-02"	192
-- "2026-03"	513
-- "2026-04"	642
-- "2026-05"	727
-- "2026-06"	792
-- "2026-07"	594
-- "2026-08"	432
-- "2026-09"	202
-- "2026-10"	78

-- Question 3. Les 10 matériels les plus réservés (id_materiel, designation, categorie, nombre de réservations).
SELECT
    m.id_materiel,
    m.designation,
    m.categorie,
    COUNT(r.id_reservation) AS nb_reservations
FROM materiel m
INNER JOIN reservation r ON m.id_materiel = r.id_materiel
GROUP BY m.id_materiel, m.designation, m.categorie
ORDER BY nb_reservations DESC, m.id_materiel ASC
LIMIT 10;
-- Nombre de lignes obtenues : 10 lignes 
-- "43"	"Table de mixage 8 voies"	"Sonorisation"	48
-- "204"	"Barnum 3x3 m"	"Tente et barnum"	47
-- "254"	"Guirlande guinguette 20 m"	"Eclairage"	45
-- "290"	"Panneau de deviation"	"Securite"	45
-- "130"	"Chaise pliante"	"Mobilier"	43
-- "116"	"Table pliante 180 cm"	"Mobilier"	42
-- "333"	"Four a raclette 8 personnes"	"Cuisine"	42
-- "21"	"Enceinte amplifiee 12 pouces"	"Sonorisation"	41
-- "211"	"Mat d'eclairage"	"Eclairage"	41
-- "341"	"Friteuse 2 bacs"	"Cuisine"	41


-- Question 4. Taux de retard en pourcentage, arrondi à deux décimales, globalement puis par site,
-- calculé sur les seules réservations closes : un retard est un retour réel postérieur à la date de fin prévue.
-- 4a. Taux de retard global :
SELECT
    ROUND(
        100.0 * COUNT(CASE WHEN date_retour_reelle > date_fin_prevue THEN 1 END) / NULLIF(COUNT(id_reservation), 0),
        2
    ) AS taux_retard_global_pct
FROM reservation
WHERE date_retour_reelle IS NOT NULL;
-- Nombre de lignes obtenues (4a) : 1 ligne.
-- Taux global obtenu 32.41%

-- 4b. Taux de retard par site :
SELECT
    s.code_site,
    s.nom,
    ROUND(
        100.0 * COUNT(CASE WHEN r.date_retour_reelle > r.date_fin_prevue THEN 1 END) / NULLIF(COUNT(r.id_reservation), 0),
        2
    ) AS taux_retard_pct
FROM site s
INNER JOIN reservation r ON s.code_site = r.code_site
WHERE r.date_retour_reelle IS NOT NULL
GROUP BY s.code_site, s.nom
ORDER BY taux_retard_pct DESC, s.code_site ASC;
-- Nombre de lignes obtenues (4b) : 5 lignes (1 ligne par site ayant au moins une réservation close.
-- "POL-HAZ"	"Pole technique d'Hazebrouck"	33.90%
-- "POL-BAI"	"Atelier municipal de Bailleul"	32.30%
-- "POL-EST"	"Reserve d'Estaires"	31.56%
-- "POL-MER"	"Depot intercommunal de Merville"	31.28%
-- "POL-NIE"	"Magasin de Nieppe"	29.35%

-- Question 5. Les catégories dont le nombre de réservations est supérieur à la moyenne des catégories, avec ce nombre.
WITH reservations_par_categorie AS (
    SELECT
        m.categorie,
        COUNT(r.id_reservation) AS nb_reservations
    FROM materiel m
    INNER JOIN reservation r ON m.id_materiel = r.id_materiel
    GROUP BY m.categorie
)
SELECT
    categorie,
    nb_reservations
FROM reservations_par_categorie
WHERE nb_reservations > (
    SELECT AVG(nb_reservations)
    FROM reservations_par_categorie
)
ORDER BY nb_reservations DESC, categorie ASC;
-- Nombre de lignes obtenues : 2
-- Mobilier (1321 reservations) et Securite (892 reservations)


-- Question 6. Pour chaque site, le matériel le plus réservé avec son nombre de réservations :
-- une ligne par site, en utilisant une fonction fenêtre dans une expression de table commune WITH.
WITH classement_materiel_site AS (
    SELECT
        s.code_site,
        s.nom AS nom_site,
        m.id_materiel,
        m.designation,
        COUNT(r.id_reservation) AS nb_reservations,
        ROW_NUMBER() OVER (
            PARTITION BY s.code_site
            ORDER BY COUNT(r.id_reservation) DESC, m.id_materiel ASC
        ) AS rang
    FROM site s
    INNER JOIN reservation r ON s.code_site = r.code_site
    INNER JOIN materiel m ON r.id_materiel = m.id_materiel
    GROUP BY s.code_site, s.nom, m.id_materiel, m.designation
)
SELECT
    code_site,
    nom_site,
    id_materiel,
    designation,
    nb_reservations
FROM classement_materiel_site
WHERE rang = 1
ORDER BY code_site ASC;
-- Nombre de lignes obtenues : 5 lignes (1 par site ayant au moins une réservation.
-- "POL-BAI"	"Atelier municipal de Bailleul"	"250"	"Projecteur LED 100 W"
-- "POL-EST"	"Reserve d'Estaires"	"121"	"Estrade 2x1 m"
-- "POL-HAZ"	"Pole technique d'Hazebrouck"	"204"	"Barnum 3x3 m"
-- "POL-MER"	"Depot intercommunal de Merville"	"211"	"Mat d'eclairage"
-- "POL-NIE"	"Magasin de Nieppe"	"211"	"Mat d'eclairage"

-- Question 7. La durée réelle moyenne de prêt en jours (retour réel moins début), globalement puis par catégorie,
-- sur les réservations closes, arrondie à une décimale, triée par durée décroissante.
-- 7a. Durée réelle moyenne globale :
SELECT
    ROUND(AVG(date_retour_reelle - date_debut)::NUMERIC, 1) AS duree_moyenne_globale_jours
FROM reservation
WHERE date_retour_reelle IS NOT NULL;
-- Nombre de lignes obtenues (7a) : 1 ligne.
-- Duree globale = 5.7

-- 7b. Durée réelle moyenne par catégorie :
SELECT
    m.categorie,
    ROUND(AVG(r.date_retour_reelle - r.date_debut)::NUMERIC, 1) AS duree_moyenne_jours
FROM reservation r
INNER JOIN materiel m ON r.id_materiel = m.id_materiel
WHERE r.date_retour_reelle IS NOT NULL
GROUP BY m.categorie
ORDER BY duree_moyenne_jours DESC, m.categorie ASC;
-- Nombre de lignes obtenues (7b) : 6 lignes (1 ligne par catégorie ayant au moins une réservation close).
-- "Tente et barnum"	5.9
-- "Cuisine"	5.8
-- "Securite"	5.8
-- "Mobilier"	5.7
-- "Eclairage"	5.6
-- "Sonorisation"	5.4


/*
Analyse du coût des requêtes :
1. Les requêtes 1 et 6 sont les plus coûteuses en ressources (CPU et mémoire / I/O).
2. La requête 1 nécessite un LEFT JOIN suivi d'un COUNT(DISTINCT r.id_association), ce qui oblige PostgreSQL à trier ou hacher l'ensemble des réservations pour dédupliquer les associations par site.
3. La requête 6 combine une double jointure (site, reservation, materiel), une agrégation GROUP BY sur 4 colonnes, puis un tri partitionné (WindowAgg avec PARTITION BY et ORDER BY) pour le ROW_NUMBER().
4. La requête 5 engendre également un surcoût modéré car la CTE agrège les réservations par catégorie avant de la relire une seconde fois pour calculer la moyenne globale (AVG).
5. À l'inverse, les requêtes 2, 4a et 7a ne balayent que la table reservation sans jointure, et les index sur les clés étrangères (code_site, id_materiel) accélèrent fortement les requêtes 3, 4b et 7b.
*/
