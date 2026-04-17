---
name: rgesn-assess
description: Évalue un service numérique face aux 78 critères du RGESN 2024 (Arcep/Arcom) et produit un declaration.json prêt à être converti en déclaration d'écoconception. À utiliser pour "faire l'audit RGESN", "évaluer mon service avec le RGESN", "rédiger la déclaration d'écoconception", etc.
---

# rgesn-assess — évaluation RGESN d'un service numérique

Ce skill transforme un projet (code + contexte) en un `declaration.json` conforme au schéma `schemas/declaration.schema.json`. Le JSON produit est la sortie pivot consommée par le skill `rgesn-fill-xlsx` qui le matérialise dans le tableur officiel.

## Sources à connaître

- `data/criteres_rgesn.json` — les 78 critères structurés (id, libellé, priorité, difficulté, pondération, cible, moyen de test, exemple de texte de déclaration). **Lis ce fichier en premier**, c'est la source de vérité.
- `docs/referentiel_rgesn_2024.pdf` — le référentiel officiel complet. À consulter quand le `moyen_test` d'un critère est ambigu ou quand l'utilisateur demande le détail d'un critère.
- `schemas/declaration.schema.json` — le format de sortie à respecter.

## Déroulé attendu

1. **Collecter les métadonnées du service** auprès de l'utilisateur (ou les inférer du projet courant) :
   - Nom du service
   - Échantillons évalués (chemins critiques / unités fonctionnelles)
   - Entité qui évalue, responsable, date

2. **Pour chaque critère**, déterminer :
   - `evaluation` ∈ { `Conforme`, `Non conforme`, `Non applicable`, `À évaluer` }
     - `Non applicable` uniquement si le champ `cible` du critère le permet (ex: "N/A si le service n'utilise pas d'IA"). Sinon c'est `Conforme` ou `Non conforme`.
     - `À évaluer` si l'information manque — préférer poser la question à l'utilisateur plutôt que d'inventer.
   - `texte_declaration` — rédaction publiable. S'inspirer du template dans `exemple_declaration` quand il existe, mais le personnaliser avec les éléments réels du service. Ne **jamais** laisser `[à compléter]` dans la sortie finale.
   - `evolutions_potentielles`, `actions_a_mener`, `qui`, `quand` — optionnels, à renseigner quand utile.

3. **Stratégie d'évaluation** — privilégier dans cet ordre :
   - Examen direct du code / de la config / de la documentation du projet (architecture, frontend, backend, hébergement, algorithmie sont largement auditables).
   - Questions ciblées à l'utilisateur pour les critères organisationnels (stratégie, UX/UI, contenus) — **grouper les questions par thème** pour limiter les allers-retours.
   - Marquer `À évaluer` en dernier recours, jamais par défaut.

4. **Écrire le résultat** dans `out/declaration.json` (créer `out/` si besoin) en suivant strictement `schemas/declaration.schema.json`.

## Règles de rédaction du `texte_declaration`

- Style factuel, au présent, à la 3ᵉ personne (« Le service X … »).
- Justifier la conformité en s'appuyant explicitement sur le `moyen_test` du critère.
- Citer les preuves concrètes (fichiers, outils, méthodologies, dates, métriques) plutôt que des formules génériques.
- Pour un critère `Non conforme`, décrire honnêtement l'écart plutôt que le masquer — la transparence est un objectif du RGESN.
- Pour `Non applicable`, reformuler la raison de non-applicabilité en citant la cible du critère.

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
