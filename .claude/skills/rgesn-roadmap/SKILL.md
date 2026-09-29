---
name: rgesn-roadmap
description: Produit le plan d'avancement RGESN 2024 (roadmap des next steps, phasée et chiffrée en points de score) à partir d'un declaration.json conforme à schemas/declaration.schema.json. À utiliser après rgesn-assess, ou quand l'utilisateur demande "fais la roadmap", "plan d'avancement", "next steps RGESN", "par quoi on commence ?".
---

# rgesn-roadmap — plan d'avancement

Ce skill transforme les critères `Non conforme` et `À évaluer` d'un `declaration.json` en un plan d'actions phasé, avec le gain de score de chaque action et le score cumulé après chaque phase.

## Règle d'or

**Ne jamais réimplémenter le phasage ni le calcul du score** : toute la logique est dans `scripts/roadmap.py`. Ton rôle est d'enrichir le JSON (effort réel, dépendances), puis d'appeler le script.

Le script n'utilise que la bibliothèque standard Python : pas de venv ni de `pip install` nécessaires. Emplacements possibles, dans cet ordre :
1. le répertoire courant (si l'utilisateur travaille dans le repo RGESN lui-même),
2. sinon `~/.claude/rgesn-toolkit/` (emplacement installé par `install.sh`).

```bash
python3 ~/.claude/rgesn-toolkit/scripts/roadmap.py <declaration.json> [<output.md>]
```

## Comment le script phase les actions

| Phase | Contenu |
|---|---|
| 0 — Lever les inconnues | critères `À évaluer` |
| 1 — Quick wins | effort `Faible` |
| 2 — Chantiers | effort `Moyen` |
| 3 — Chantiers structurants | effort `Fort` |

- **Effort** : par défaut, la `difficulte` du référentiel (`data/criteres_rgesn.json`). Le champ optionnel `effort` d'un critère dans le JSON la remplace ; le rapport marque alors l'effort d'un astérisque.
- **Dépendances** : le champ optionnel `depend_de` (liste d'ids) repousse une action au moins dans la phase de ses dépendances, et la place après elles.
- **Ordre dans une phase** : pondération décroissante (gain de score), puis priorité, puis id.
- **Score** : même formule que le tableur officiel (Σ pondérations validées / Σ pondérations applicables ; N/A exclus ; `À évaluer` compte au dénominateur).
- **Action affichée** : `actions_a_mener`, sinon `evolutions_potentielles`, sinon `[À définir]`. Responsable : `qui`, sinon `[À attribuer]`. Échéance : `quand`.

## Déroulé attendu

1. **Lire** le `declaration.json` et `data/criteres_rgesn.json` (priorité, difficulté, pondération de chaque critère).
2. **Réestimer l'effort** de chaque critère non validé *pour ce service*. La difficulté du référentiel est générique : une action qui se résume à une ligne de config (en-tête Cache-Control, activation de gzip) ou à une question posée au DPO est `Faible` même si le référentiel dit `Moyen`. Ne renseigner `effort` que lorsque ton estimation diffère du référentiel, en t'appuyant sur le texte de `actions_a_mener` et `texte_declaration`.
3. **Identifier les dépendances** évidentes entre actions, en particulier quand le texte d'une action cite un autre critère (« Activer la compression (critère 6.3), puis… », « Une fois la mesure d'empreinte réalisée (critère 1.5)… »), ou quand une action suppose un rôle qui n'existe pas encore (revue RGESN après désignation du référent 1.3).
4. **Présenter à l'utilisateur** les efforts réestimés et les dépendances, sous forme de tableau court, puis les écrire dans le JSON (champs `effort` et `depend_de`) une fois validés. Si l'utilisateur fournit des responsables ou des échéances, les écrire dans `qui` et `quand`. Ces champs n'ont aucun effet sur `rgesn-fill-xlsx` et `rgesn-fill-docx`, sauf `qui` et `quand`, qui sont reportés dans les colonnes J et K du tableur.
5. **Lancer le script**, par défaut à côté du JSON : `<dossier du JSON>/roadmap_<service>_<date>.md`.
6. **Vérifier** que le script a affiché `OK N actions planifiées` sans avertissement `ids inconnus`, puis relire le Markdown produit.

## Restitution à l'utilisateur

Résumer en quelques lignes : le score actuel, le score après chaque phase, les 3 à 5 premières actions à lancer, et les trous du plan (section « Points à compléter » : responsables à attribuer, actions à définir, absence d'échéances). Si les critères `qui` ou `quand` ont été modifiés, proposer de régénérer le xlsx avec `rgesn-fill-xlsx`.

## Ce que ce skill ne fait pas

- Il ne réévalue pas les critères : c'est le rôle de `rgesn-assess`.
- Il n'invente ni responsable ni échéance : les manques restent visibles dans le rapport.
- Le score cumulé suppose que chaque action rend le critère conforme ; ce n'est pas une garantie.
