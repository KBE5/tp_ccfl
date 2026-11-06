# Rapport de Qualité des Données — CCFL

## 1. Tableau récapitulatif des anomalies

| Anomalie | Fichier | Colonne | Description | Lignes concernées | Part (%) | Traitement retenu |
|---|---|---|---|---|---|---|
| a | `materiel.csv` | Toutes | Doublons stricts de lignes | 14 | 3.82% | Suppression des doublons (1 occurrence conservée) |
| b | `materiel.csv` | `annee_achat` | Valeurs d'année d'achat vides | 9 | 2.45% | Conservation de la valeur manquante (non inventée) |
| c | `materiel.csv` | `annee_achat` | Année d'achat postérieure à 2026 | 5 | 1.36% | Conversion en valeur manquante (aberration temporelle) |
| d | `materiel.csv` | `valeur_achat` | Valeurs d'achat vides | 11 | 3.00% | Conservation de la valeur manquante |
| e | `materiel.csv` | `categorie` | Catégories en majuscules intégrales | 6 | 1.63% | Normalisation automatique (capitalisation) |
| f | `materiel.csv` | `categorie` | Espaces parasites en début/fin | 5 | 1.36% | Normalisation automatique (`strip()`) |
| g | `materiel.csv` | `valeur_achat` | Virgule décimale au lieu du point | 5 | 1.36% | Remplacement automatique `,` par `.` |
| h | `associations.csv` | `code_postal` | Codes postaux vides | 9 | 4.29% | Conservation de la valeur manquante |
| i | `associations.csv` | `type_association` | Type valant 'inconnu' | 7 | 3.33% | Conservation (donnée brute non corrigée par devinette) |
| j | `associations.csv` | `date_convention` | Dates au format obsolète `JJ/MM/AAAA` | 6 | 2.86% | Harmonisation automatique au format ISO `AAAA-MM-JJ` |
| k | `reservations.csv` | Toutes | Doublons stricts de réservations | 36 | 0.78% | Suppression des doublons stricts |
| l | `reservations.csv` | `id_materiel` | Référence vers un matériel inexistant (orphelins) | 21 | 0.45% | Suppression des lignes (rupture d'intégrité FK) |
| m | `reservations.csv` | `date_retour_reelle` | Date de retour antérieure au début du prêt | 15 | 0.32% | Suppression des lignes (aberration chronologique) |
| n | `reservations.csv` | `quantite` | Quantité réservée égale à zéro | 6 | 0.13% | Suppression des lignes (prêt vide aberrant) |

*Note : Les prêts en cours (`date_retour_reelle` vide, 72 cas initiaux) constituent un cas métier normal et ne sont pas comptés comme des anomalies.*

## 2. Synthèse par fichier

| Fichier | Lignes avant nettoyage | Lignes après nettoyage | Delta / Écart |
|---|---|---|---|
| `materiel.csv` | 367 | 360 | -7 |
| `associations.csv` | 210 | 210 | 0 |
| `reservations.csv` | 4618 | 4560 | -80 |

## 3. Analyse des prêts en cours

- **Prêts en cours avant nettoyage :** 72
- **Prêts en cours après nettoyage :** 71
- **Explication de l'écart :** L'écart d'une unité (72 -> 71) s'explique par le fait qu'un prêt en cours présentait également un identifiant de matériel orphelin (`id_materiel` inexistant), ce qui a conduit à son exclusion légitime pour préserver l'intégrité référentielle.

## 4. Points d'attention pour la direction

1. **Harmonisation de la saisie :** L'hétérogénéité sur les catégories montre l'absence de listes déroulantes dans l'ancien logiciel. Une standardisation s'impose.
2. **Contrôles de cohérence :** Des anomalies chronologiques et quantités nulles ont été enregistrées. Des règles de validation bloquantes dans le futur outil éviteront ces erreurs.
3. **Suivi des inventaires :** Fiabilisation physique des fiches de matériel conseillée dans les 5 pôles.
4. **Intégrité référentielle :** Le nettoyage des réservations orphelines prépare sereinement la modélisation relationnelle de l'Étape 4.
