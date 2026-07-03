# RGESN — skills Claude Code

Skills Claude Code pour appliquer le **Référentiel Général d'Écoconception des Services Numériques** ([RGESN 2024, Arcep/Arcom](https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/)) sur vos projets.

L'objectif : **évaluer un service numérique** face aux 78 critères, **rédiger la déclaration d'écoconception publique (docx)** et **remplir le tableur officiel (xlsx)** — directement depuis Claude Code, sur n'importe quel projet, sans quitter votre IDE.

## Installation

> Le dépôt est **privé** : l'installation se fait via SSH (le `curl … | bash` public ne peut pas fonctionner). Assurez-vous d'avoir une [clé SSH configurée sur GitHub](https://docs.github.com/authentication/connecting-to-github-with-ssh) avec accès à l'organisation `Theodo-GovTech`.

```bash
git clone git@github.com:Theodo-GovTech/RGESN.git ~/.claude/rgesn-toolkit
~/.claude/rgesn-toolkit/install.sh
```

Le script :
1. clone (ou met à jour) le toolkit dans `~/.claude/rgesn-toolkit/` ;
2. installe les trois skills dans `~/.claude/skills/` (liens symboliques vers le toolkit — `git pull` suffit pour mettre à jour) ;
3. installe les prompts d'audit thématiques dans `~/.claude/commands/` (accessibles via `/rgesn-audit-…`) ;
4. crée un venv Python dans le toolkit et installe `openpyxl` et `python-docx` (nécessaires pour remplir le tableur et le document).

Variables d'environnement utiles :

| Variable | Défaut | Effet |
|---|---|---|
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Répertoire Claude Code cible |
| `RGESN_TOOLKIT_DIR` | `$CLAUDE_CONFIG_DIR/rgesn-toolkit` | Emplacement du clone |
| `RGESN_BRANCH` | `main` | Branche à utiliser |
| `RGESN_NO_PYTHON=1` | — | Ne pas installer le venv Python |

Désinstallation :

```bash
rm -rf ~/.claude/rgesn-toolkit ~/.claude/skills/rgesn-* ~/.claude/commands/rgesn-*
```

## Utilisation

### Dans Claude Code, depuis n'importe quel projet

| Demande à Claude | Skill/commande déclenché |
|---|---|
| « évalue ce projet avec le RGESN » | `rgesn-assess` |
| « rédige la déclaration d'écoconception » | `rgesn-assess` |
| « remplis le tableur RGESN » | `rgesn-fill-xlsx` |
| « génère la déclaration publique » / « produis le docx » | `rgesn-fill-docx` |
| `/rgesn-audit-frontend`, `/rgesn-audit-backend`, `/rgesn-audit-infra`, `/rgesn-audit-ia`, `/rgesn-audit-contenus`, `/rgesn-audit-rgesn` | audits thématiques ciblés |
| `/rgesn-generate-declaration` | variante courte de génération |
| `/rgesn-review-pr-ecoconception` | revue d'une PR sous l'angle RGESN |

### Parcours type

1. **Évaluation** — sur votre projet : demandez à Claude d'évaluer le service avec le RGESN. Le skill `rgesn-assess` lit le code, pose des questions ciblées, et produit `out/declaration.json`.
2. **Relecture** — ouvrez `out/declaration.json` et corrigez les critères marqués `Non conforme` ou `À évaluer`.
3. **Tableur d'audit** — demandez à Claude de générer le tableur. Le skill `rgesn-fill-xlsx` écrit `out/<service>_<date>.xlsx` en respectant le template officiel (usage interne : scores et conformité détaillée).
4. **Déclaration publique** — demandez à Claude de générer la déclaration. Le skill `rgesn-fill-docx` écrit `out/<service>_<date>.docx`, document narratif structuré comme l'exemple officiel et destiné à être publié sur le site du service.
5. **Export PDF** — ouvrez le `.xlsx` dans Excel (instructions d'export en `E5` de la feuille *Score d'avancement*) ou exportez le `.docx` depuis Word.

## Architecture

Trois skills complémentaires reliés par un JSON pivot :

```
                                                          ┌───────────────────┐   xlsx rempli (audit)
                                                      ┌─▶ │   rgesn-fill-xlsx │   ─────────────────▶
projet analysé     ┌────────────────┐  declaration    │   └───────────────────┘
 ───────────────▶  │  rgesn-assess  │  .json          │
                   │ (expert contenu)│ ──────────────▶│   ┌───────────────────┐   docx rempli (public)
                   └────────────────┘                 └─▶ │   rgesn-fill-docx │   ─────────────────▶
                                                          └───────────────────┘
```

- **`rgesn-assess`** — lit `data/criteres_rgesn.json`, évalue les 78 critères (Conforme / Non conforme / Non applicable / À évaluer) et rédige le texte de déclaration. Sortie : `declaration.json` conforme à `schemas/declaration.schema.json`.
- **`rgesn-fill-xlsx`** — remplit une copie de `docs/rgesn_2024_outil_declaration.xlsx` (tableur d'audit interne, scores et conformité).
- **`rgesn-fill-docx`** — génère un document Word narratif structuré comme `docs/rgesn_2024_exemple_declaration.docx` (déclaration publique à publier sur le site du service).

Cette séparation permet de relire / éditer le JSON avant remplissage, et d'isoler la complexité Office dans deux scripts uniques (`scripts/fill_xlsx.py`, `scripts/fill_docx.py`).

## Contenu du repo

```
├── install.sh                      # installation des skills dans ~/.claude/
├── data/
│   └── criteres_rgesn.json         # 78 critères structurés (source de vérité)
├── docs/                           # documents officiels RGESN 2024
│   ├── referentiel_rgesn_2024.pdf
│   ├── rgesn_2024_outil_declaration.xlsx
│   └── rgesn_2024_exemple_declaration.docx
├── schemas/
│   └── declaration.schema.json     # format pivot entre les deux skills
├── scripts/
│   ├── extract_criteres.py         # régénère data/criteres_rgesn.json depuis le xlsx
│   ├── fill_xlsx.py                # remplit le template xlsx depuis un declaration.json
│   └── fill_docx.py                # génère la déclaration docx depuis un declaration.json
├── examples/
│   └── declaration.minimal.json    # exemple conforme au schéma
├── .claude/skills/                 # skills Claude Code (installés via install.sh)
│   ├── rgesn-assess/SKILL.md
│   ├── rgesn-fill-xlsx/SKILL.md
│   └── rgesn-fill-docx/SKILL.md
├── skills/                         # prompts d'audit thématiques (slash commands)
│   ├── audit-rgesn.md
│   ├── audit-frontend.md
│   ├── audit-backend.md
│   ├── audit-infra.md
│   ├── audit-contenus.md
│   ├── audit-ia.md
│   ├── generate-declaration.md
│   └── review-pr-ecoconception.md
└── CLAUDE.md                       # règles d'écoconception applicables à ce repo
```

## Développement local

Pour hacker sur les skills sans passer par l'installation globale :

```bash
git clone git@github.com:Theodo-GovTech/RGESN.git
cd RGESN
python3 -m venv .venv && .venv/bin/pip install openpyxl python-docx

# Tests rapides des scripts de remplissage
.venv/bin/python scripts/fill_xlsx.py examples/declaration.minimal.json
.venv/bin/python scripts/fill_docx.py examples/declaration.minimal.json
```

Les skills s'autodétectent dans le repo courant (`.claude/skills/`) quand vous lancez Claude Code depuis ce dossier, sans besoin d'installation.

## Sources officielles

Tous les documents proviennent de [ecoresponsable.numerique.gouv.fr](https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/) (version mai 2024).
