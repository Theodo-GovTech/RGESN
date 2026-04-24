---
name: rgesn-assess
description: Évalue un service numérique face aux 78 critères du RGESN 2024 (Arcep/Arcom) et produit un declaration.json prêt à être converti en déclaration d'écoconception. À utiliser pour "faire l'audit RGESN", "évaluer mon service avec le RGESN", "rédiger la déclaration d'écoconception", etc.
---

# rgesn-assess — évaluation RGESN d'un service numérique

Ce skill transforme un projet (code + contexte) en un `declaration.json` conforme au schéma `schemas/declaration.schema.json`. Le JSON produit est la sortie pivot consommée par le skill `rgesn-fill-xlsx` qui le matérialise dans le tableur officiel.

## Sources à connaître

Ces fichiers appartiennent au **toolkit RGESN**. Chercher dans cet ordre :
1. le répertoire courant (si l'utilisateur travaille dans le repo RGESN lui-même),
2. sinon `~/.claude/rgesn-toolkit/` (emplacement par défaut de `install.sh`).

- `data/criteres_rgesn.json` — les 78 critères structurés (id, libellé, priorité, difficulté, pondération, cible, moyen de test, exemple de texte de déclaration). **Lis ce fichier en premier**, c'est la source de vérité.
- `docs/referentiel_rgesn_2024.pdf` — le référentiel officiel complet. À consulter quand le `moyen_test` d'un critère est ambigu ou quand l'utilisateur demande le détail d'un critère.
- `schemas/declaration.schema.json` — le format de sortie à respecter.

## Déroulé attendu

1. **Collecter les métadonnées du service** auprès de l'utilisateur (ou les inférer du projet courant) :
   - Nom du service
   - Échantillons évalués (chemins critiques / unités fonctionnelles)
   - Entité qui évalue, responsable, date

2. **Première passe automatique — examen direct** : parcourir les 78 critères et évaluer tout ce qui est directement observable dans le code, la config, les manifests, le CI, la documentation du projet (architecture, frontend, backend, hébergement, algorithmie sont largement auditables ainsi). Pour chaque critère, déterminer :
   - `evaluation` ∈ { `Conforme`, `Non conforme`, `Non applicable`, `À évaluer` }
     - `Non applicable` uniquement si le champ `cible` du critère le permet (ex: "N/A si le service n'utilise pas d'IA"). Sinon c'est `Conforme` ou `Non conforme`.
     - `À évaluer` (état temporaire) si l'information manque — **ne jamais inventer**, le critère passera à l'étape 3.
   - `texte_declaration` — rédaction publiable. S'inspirer du template dans `exemple_declaration` quand il existe, mais le personnaliser avec les éléments réels du service. Ne **jamais** laisser `[à compléter]` dans la sortie finale.
   - `evolutions_potentielles`, `actions_a_mener`, `qui`, `quand` — optionnels, à renseigner quand utile.

3. **Seconde passe — mode interactif question / réponse** pour tous les critères encore `À évaluer` après la première passe :
   - Utiliser le tool **`AskUserQuestion`** pour transformer chaque lacune en question à choix multiples (le même style d'interaction que le plan mode).
   - **Regrouper les critères par thème** (stratégie, UX/UI, contenus, organisationnel, hébergement…) et traiter un thème à la fois. À chaque tour, envoyer jusqu'à **4 questions en parallèle** dans un seul appel `AskUserQuestion` pour limiter les allers-retours.
   - Pour chaque question, proposer **2 à 4 options concrètes et mutuellement exclusives** qui couvrent les cas typiques du critère (ex : « Oui, documenté », « Oui, mais non documenté », « Non »). Ne pas ajouter d'option « Autre » : le tool la fournit automatiquement.
   - Dans `header` (≤ 12 car.), mettre l'**id du critère** (ex : `1.3`, `4.14`) pour que l'utilisateur voie à quel critère la question se rapporte.
   - Dans `question`, reformuler le `moyen_test` du critère en langage naturel.
   - Exploiter chaque réponse pour compléter immédiatement `evaluation` + `texte_declaration` + éventuellement `actions_a_mener`. Citer la réponse utilisateur dans le texte de déclaration plutôt que de la paraphraser vaguement.
   - Si l'utilisateur choisit « Autre » avec une note libre, en tenir compte littéralement.
   - Si l'utilisateur demande explicitement à sauter une question (réponse « Je ne sais pas », « Passer », etc.), alors — et seulement alors — laisser `evaluation: "À évaluer"` avec une note dans `actions_a_mener` indiquant qui doit trancher.

4. **Écrire le résultat** dans `out/declaration.json` du **projet courant** (créer `out/` si besoin) en suivant strictement `schemas/declaration.schema.json`. Avant d'écrire, vérifier qu'aucun critère ne reste en `À évaluer` sans action associée.

## Règles de rédaction du `texte_declaration`

- Style factuel, au présent, à la 3ᵉ personne (« Le service X … »).
- Justifier la conformité en s'appuyant explicitement sur le `moyen_test` du critère.
- Citer les preuves concrètes (fichiers, outils, méthodologies, dates, métriques) plutôt que des formules génériques.
- Pour un critère `Non conforme`, décrire honnêtement l'écart plutôt que le masquer — la transparence est un objectif du RGESN.
- Pour `Non applicable`, reformuler la raison de non-applicabilité en citant la cible du critère.

## Exemple d'appel `AskUserQuestion` en seconde passe

```jsonc
{
  "questions": [
    {
      "header": "1.3",
      "question": "Un référent écoconception est-il identifié dans l'équipe ?",
      "multiSelect": false,
      "options": [
        { "label": "Oui, nommé et documenté", "description": "Une personne est désignée et c'est écrit quelque part (charte, README, fiche de poste)." },
        { "label": "Oui, mais informel",       "description": "Une personne joue ce rôle de fait, sans désignation écrite." },
        { "label": "Non",                       "description": "Aucune personne n'a cette responsabilité aujourd'hui." }
      ]
    },
    {
      "header": "4.13",
      "question": "Les notifications sont-elles désactivées par défaut et paramétrables par l'utilisateur ?",
      "multiSelect": false,
      "options": [
        { "label": "Oui aux deux",        "description": "Désactivées par défaut ET paramétrables." },
        { "label": "Paramétrables seulement", "description": "Paramétrables mais activées par défaut." },
        { "label": "Non",                 "description": "Activées par défaut et non configurables." },
        { "label": "Pas de notifications", "description": "Le service n'envoie aucune notification — critère non applicable." }
      ]
    }
  ]
}
```

## Quand s'arrêter

Ne pas invoquer `rgesn-fill-xlsx` automatiquement. Proposer à l'utilisateur de :
1. Relire le `declaration.json` produit (surtout les critères marqués `Non conforme` ou `À évaluer`).
2. Puis lancer `rgesn-fill-xlsx` pour générer le tableur officiel.

## Format de sortie minimal

```json
{
  "service": {
    "nom": "...",
    "echantillons": "...",
    "entite_evaluation": "...",
    "responsable_evaluation": "...",
    "date_evaluation": "YYYY-MM-DD"
  },
  "criteres": [
    { "id": "1.1", "evaluation": "Conforme", "texte_declaration": "..." },
    { "id": "1.2", "evaluation": "À évaluer" }
  ]
}
```

Les critères omis seront traités comme `À évaluer` par le skill de remplissage — mais viser l'exhaustivité reste préférable.
