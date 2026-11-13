# Auto-évaluation — NOM Prénom

## Étapes

| Étape | État (terminée / partielle / non abordée) | Points de vérification obtenus | Ce qui a bloqué | Temps réel passé par étape |
|---|---|---|---|---|
| 1 | terminée | 4 / 4 | Manipulation des fichiers CSV en Python brut et compréhension des structures d'origine. | ~1 h 15|
| 2 | terminée | 4 / 4 | Gestion des conversions de types (`errors="coerce"`), gestion des virgules décimales et repérage des orphelins. | ~1 h |
| 3 | terminée | 7 / 7 | Application combinée de 14 anomalies, calcul exact des métriques de suppression et gestion du piège des prêts en cours. | ~55 mn |
| 4 | terminée | 3 / 3 | Traduction rigoureuse du modèle conceptuel vers le script DDL PostgreSQL (contraintes de clés étrangères et CHECK). | ~1 h 05 |
| 5 | terminée | 5 / 5 | Gestion des transactions par lots avec SQLAlchemy et remplacement des NaN de pandas par des `None` SQL. | ~1 h 17 |
| 6 | terminée | 7 / 7 | Écriture des jointures complexes, de la CTE avec fonction fenêtre (`ROW_NUMBER`) et gestion des agrégats conditionnels. | ~58 mn |
| 7 | non abordée | | | |

## Ce que je sais faire mieux qu'en septembre
- Charger, manipuler et nettoyer des jeux de données avec **Pandas** (filtrage, typage des colonnes, traitement des `NaN` et des dates).
- Réaliser un audit assez complet en identifiant, quantifiant et justifiant les corrections pour chaque catégorie d'anomalie.
- Distinguer les anomalies techniques des règles métier (comme les prêts en cours) et garantir l'intégrité référentielle entre tables.


- Modéliser une base de données relationnelle et écrire des scripts DDL propres sous PostgreSQL avec des contraintes d'intégrité strictes (`FOREIGN KEY`, `CHECK`).
- Écrire des requêtes SQL combinant des expressions de table communes (`WITH`), et des jointures explicites.


## Ce qui me résiste encore
- L'écriture de scripts de nettoyage complexes combinant plusieurs filtres logiques simultanés sans décomposer pas à pas.
- L'interprétation rapide de certains messages d'erreur de Python/Pandas lorsqu me confronte à des types de données inattendus.

- L'optimisation des requêtes complexes 
- La maîtrise des fonctions fenêtres (ROW_NUMBER())

- L'articulation fluide entre les scripts d'insertion SQLAlchemy et les types de données spécifiques en base.