# RGESN

Base de skills Claude Code dédiés au **Référentiel Général d'Écoconception de Services Numériques** (RGESN 2024, Arcep/Arcom).

L'objectif : rédiger automatiquement une déclaration d'écoconception conforme et remplir le tableur officiel, à partir d'une analyse du projet et d'échanges avec l'équipe.

## Architecture

Deux skills complémentaires, reliés par un JSON pivot :

```
projet analysé        ┌────────────────────┐   declaration.json   ┌───────────────────┐   xlsx rempli
   ───────────────▶   │   rgesn-assess     │   ─────────────────▶ │   rgesn-fill-xlsx │   ────────▶
                      │ (expert contenu)   │                      │ (expert Excel)    │
                      └────────────────────┘                      └───────────────────┘
```

- **`rgesn-assess`** — lit `data/criteres_rgesn.json`, évalue les 78 critères (Conforme / Non conforme / Non applicable / À évaluer) en auditant le projet et en questionnant l'utilisateur, puis rédige le texte de déclaration pour chacun. Sortie : un `declaration.json` conforme à `schemas/declaration.schema.json`.
- **`rgesn-fill-xlsx`** — prend ce JSON et écrit ses valeurs dans une copie de `docs/rgesn_2024_outil_declaration.xlsx`, en respectant les cellules fusionnées du template. Le tableur obtenu est prêt à exporter en PDF.

Cette séparation permet de relire / éditer le JSON avant le remplissage, et d'isoler la complexité Excel dans un script unique.

## Contenu du repo

```
├── data/
│   └── criteres_rgesn.json         # 78 critères structurés (source de vérité des skills)
├── docs/                           # documents officiels RGESN 2024
│   ├── referentiel_rgesn_2024.pdf
│   ├── rgesn_2024_outil_declaration.xlsx
│   └── rgesn_2024_exemple_declaration.docx
├── schemas/
│   └── declaration.schema.json     # format pivot entre les deux skills
├── scripts/
│   ├── extract_criteres.py         # régénère data/criteres_rgesn.json depuis le xlsx
│   └── fill_xlsx.py                # remplit le template xlsx depuis un declaration.json
├── examples/
│   └── declaration.minimal.json    # exemple minimal conforme au schéma
└── .claude/skills/
    ├── rgesn-assess/SKILL.md
    └── rgesn-fill-xlsx/SKILL.md
```

## Utilisation

```bash
python -m venv .venv && .venv/bin/pip install openpyxl
```

Dans Claude Code :

1. `/rgesn-assess` (ou simplement « évalue ce projet avec le RGESN ») → produit `out/declaration.json`.
2. Relire et corriger manuellement les critères `Non conforme` ou `À évaluer`.
3. `/rgesn-fill-xlsx out/declaration.json` → produit `out/<service>_<date>.xlsx`.
4. Ouvrir le xlsx dans Excel et exporter en PDF (instructions en E5 de la feuille *Score d'avancement*).

Pour tester le pipeline sans passer par Claude :

```bash
.venv/bin/python scripts/fill_xlsx.py examples/declaration.minimal.json
```

## Sources officielles

Tous les documents proviennent de [ecoresponsable.numerique.gouv.fr](https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/) (version mai 2024).
