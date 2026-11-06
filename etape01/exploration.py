import csv
from collections import Counter
import os

PATH_SITES = "tp_ccfl/data/sites.csv"
PATH_MATERIEL = "tp_ccfl/data/materiel.csv"
PATH_ASSOCIATIONS = "tp_ccfl/data/associations.csv"
PATH_RESERVATIONS = "tp_ccfl/data/reservations.csv"

def lire_csv(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def compter_par(lignes, colonne):
    c = Counter()
    for ligne in lignes:
        val = ligne.get(colonne, "")
        c[val] += 1
    return dict(c)

def total_par(lignes, colonne_groupe, colonne_valeur):
    totaux = {}
    for ligne in lignes:
        groupe = ligne.get(colonne_groupe, "")
        try:
            val = float(ligne.get(colonne_valeur, 0))
        except ValueError:
            val = 0.0
        totaux[groupe] = totaux.get(groupe, 0.0) + val
    return totaux

class Site:
    def __init__(self, code_site, nom, commune, annee_ouverture, surface_m2):
        self.code_site = code_site
        self.nom = nom
        self.commune = commune
        self.annee_ouverture = int(annee_ouverture)
        self.surface_m2 = int(surface_m2)

    def anciennete(self, annee_reference):
        return annee_reference - self.annee_ouverture

    def __str__(self):
        return f"{self.code_site} - {self.nom} ({self.commune}), {self.surface_m2} m2"

def reservations_en_cours(reservations):
    en_cours = []
    for r in reservations:
        if not r.get("date_retour_reelle", "").strip():
            en_cours.append(r)
    return en_cours

def main():
    sites = lire_csv(PATH_SITES)
    materiel = lire_csv(PATH_MATERIEL)
    associations = lire_csv(PATH_ASSOCIATIONS)
    reservations = lire_csv(PATH_RESERVATIONS)

    print("1. Nombre de lignes par fichier :")
    print(f"   - sites: {len(sites)}")
    print(f"   - materiel: {len(materiel)}")
    print(f"   - associations: {len(associations)}")
    print(f"   - reservations: {len(reservations)}")

    print("\n2. Objets Site et ancienneté (référence 2026) :")
    obj_sites = []
    for s in sites:
        obj = Site(s["code_site"], s["nom"], s["commune"], s["annee_ouverture"], s["surface_m2"])
        obj_sites.append(obj)
        print(f"   - {obj} | Ancienneté : {obj.anciennete(2026)} ans")

    print("\n3. Nombre de réservations par code_site (trié) :")
    res_par_site = compter_par(reservations, "code_site")
    for site, count in sorted(res_par_site.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {site}: {count}")

    print("\n4. Quantité totale réservée par code_site (trié) :")
    qte_par_site = total_par(reservations, "code_site", "quantite")
    for site, qte in sorted(qte_par_site.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {site}: {qte}")

    print("\n5. Nombre de matériels par etat :")
    mat_etat = compter_par(materiel, "etat")
    for etat, count in mat_etat.items():
        print(f"   - {etat}: {count}")

    print("\n6. Nombre de valeurs distinctes de categorie dans materiel.csv :")
    categories = set(m["categorie"] for m in materiel)
    print(f"   - Nombre distinct de catégories : {len(categories)} ({categories})")

    print("\n7. Nombre de réservations en cours :")
    en_cours = reservations_en_cours(reservations)
    print(f"   - Réservations en cours : {len(en_cours)}")

if __name__ == "__main__":
    main()