---
name: rgesn-fill-xlsx
description: Remplit le tableur officiel RGESN 2024 (rgesn_2024_outil_declaration.xlsx) à partir d'un declaration.json conforme à schemas/declaration.schema.json. À utiliser après rgesn-assess, ou quand l'utilisateur demande "génère le xlsx", "remplis le tableur RGESN", "exporte la déclaration".
---

# rgesn-fill-xlsx — remplissage du tableur officiel

Ce skill est l'expert Excel : il prend un `declaration.json` (produit par `rgesn-assess` ou écrit à la main) et écrit ses valeurs aux bons endroits dans une copie du template officiel `docs/rgesn_2024_outil_declaration.xlsx`.

## Règle d'or

**Ne jamais réimplémenter le remplissage** : toute la logique de mapping cellule ↔ critère est dans `scripts/fill_xlsx.py`. Appeler ce script, pas d'autre chemin.

```bash
python scripts/fill_xlsx.py <declaration.json> [<output.xlsx>]
```

Si l'environnement virtuel `.venv` du repo existe, préférer :

```bash
.venv/bin/python scripts/fill_xlsx.py <declaration.json>
```

Si la dépendance `openpyxl` manque :

```bash
python -m venv .venv && .venv/bin/pip install openpyxl
```

## Entrée attendue

Un fichier JSON conforme à `schemas/declaration.schema.json`. Voir aussi `rgesn-assess` pour la production de ce fichier. La structure minimale :

```json
{
  "service": { "nom": "...", "date_evaluation": "YYYY-MM-DD" },
  "criteres": [ { "id": "1.1", "evaluation": "Conforme", "texte_declaration": "..." } ]
}
```

Les critères absents du JSON gardent la valeur par défaut du template (`À évaluer`, cellule déclaration vide).

## Sortie

Un `.xlsx` écrit par défaut dans `out/<slug-du-service>_<date>.xlsx`, copie du template avec :
- La feuille `Score d'avancement` complétée (nom, échantillons, entité, responsable, date).
- Pour chaque critère évalué : `E` (évaluation), `F` (date), et `C` de la ligne suivante (texte de déclaration, cellule fusionnée `C:G`).
- Si renseignés : `G` (évolutions), `I` (actions), `J` (qui), `K` (quand).

Les formules de score et la structure du template sont préservées — l'ouverture dans Excel recalcule automatiquement le score d'avancement.

## Vérifications à faire après exécution

1. Vérifier que le script a affiché `OK N critères écrits` sans avertissement `ids inconnus`.
2. Ouvrir brièvement le xlsx (ou le relire avec openpyxl) pour confirmer qu'au moins la feuille `Score d'avancement` a les métadonnées attendues.
3. Rappeler à l'utilisateur comment exporter en PDF (feuille `Score d'avancement` → cellule E5 contient le mode d'emploi officiel).

## Ce que ce skill ne fait pas

- Il n'évalue rien — c'est le rôle de `rgesn-assess`.
- Il ne modifie pas le template source, seulement une copie.
- Il n'inscrit pas de texte dans une cellule si le JSON ne le fournit pas (pas de contenu inventé).
