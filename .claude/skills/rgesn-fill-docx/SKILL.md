---
name: rgesn-fill-docx
description: Génère la déclaration d'écoconception publique (format docx) à partir d'un declaration.json conforme à schemas/declaration.schema.json. À utiliser après rgesn-assess, ou quand l'utilisateur demande "génère le docx", "produis la déclaration publique", "rédige la déclaration d'écoconception".
---

# rgesn-fill-docx — déclaration d'écoconception publique (docx)

Ce skill est l'expert Word : il prend un `declaration.json` (produit par `rgesn-assess` ou écrit à la main) et produit un document `.docx` structuré comme `docs/rgesn_2024_exemple_declaration.docx`, prêt à être publié sur le site du service.

## À quoi sert ce docx par rapport au xlsx

- **`rgesn-fill-xlsx`** produit le **tableur d'audit** (scores, conformité critère par critère, usage interne).
- **`rgesn-fill-docx`** produit la **déclaration publique** (document Word narratif, destiné aux utilisateurs du service).

Les deux livrables cohabitent dans le RGESN 2024 et sont générés depuis le même `declaration.json` pivot.

## Règle d'or

**Ne jamais réimplémenter le remplissage** : toute la logique est dans `scripts/fill_docx.py`. Appeler ce script, pas d'autre chemin.

Ce script et ses ressources (`data/criteres_rgesn.json`, schéma) font partie du **toolkit RGESN**. Emplacements possibles, dans cet ordre :
1. le répertoire courant (si l'utilisateur travaille dans le repo RGESN lui-même),
2. sinon `~/.claude/rgesn-toolkit/` (emplacement installé par `install.sh`).

Commande recommandée, en utilisant le venv du toolkit quand il existe :

```bash
# Depuis n'importe quel projet, avec le toolkit installé globalement :
~/.claude/rgesn-toolkit/.venv/bin/python \
  ~/.claude/rgesn-toolkit/scripts/fill_docx.py \
  <declaration.json> [<output.docx>]
```

Ou, depuis une copie locale du repo :

```bash
.venv/bin/python scripts/fill_docx.py <declaration.json>
```

Si la dépendance `python-docx` manque :

```bash
python3 -m venv ~/.claude/rgesn-toolkit/.venv \
  && ~/.claude/rgesn-toolkit/.venv/bin/pip install python-docx
```

## Entrée attendue

Un fichier JSON conforme à `schemas/declaration.schema.json`. Voir aussi `rgesn-assess` pour la production de ce fichier. La structure minimale :

```json
{
  "service": { "nom": "...", "date_evaluation": "YYYY-MM-DD" },
  "criteres": [ { "id": "1.1", "evaluation": "Conforme", "texte_declaration": "..." } ]
}
```

Les critères absents du JSON n'apparaissent pas dans le document. Pour un critère sans `texte_declaration`, le script insère l'`exemple_declaration` officiel à la place — à relire et à personnaliser avant publication.

## Sortie

Un `.docx` écrit par défaut dans `out/<slug-du-service>_<date>.docx`. Structure :

- **Titre** : « Déclaration d'écoconception de <service> »
- **Résumé** : objectif, échantillons, entité, responsable, et les listes d'IDs par statut (validés / non validés / non applicables / à évaluer).
- **Détails du diagnostic** : critères regroupés par thème RGESN (1 Stratégie → 9 Algorithmie). Chaque critère comporte son libellé (Heading 3), une ligne « Critère X.Y — évaluation (date) », puis le texte de déclaration, puis les évolutions potentielles s'il y en a.

## Vérifications à faire après exécution

1. Vérifier que le script a affiché `OK N critères écrits` sans avertissement `ids inconnus`.
2. Ouvrir le docx (Word / LibreOffice / Pages) pour contrôler la mise en forme et la lisibilité.
3. Rappeler à l'utilisateur que les textes des critères `À évaluer` ou sans `texte_declaration` ont été remplis avec l'exemple officiel et doivent être personnalisés avant publication.

## Ce que ce skill ne fait pas

- Il n'évalue rien — c'est le rôle de `rgesn-assess`.
- Il n'invente pas de contenu : si le JSON ne fournit pas de texte, le template officiel est utilisé comme base, sans modification.
- Il ne gère pas l'export PDF — c'est à l'utilisateur de l'effectuer depuis Word une fois le docx relu.
