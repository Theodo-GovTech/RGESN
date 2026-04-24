# Génération de la Déclaration d'Écoconception — RGESN 2024

Tu génères la déclaration d'écoconception du service numérique de ce projet, conformément au modèle officiel du RGESN 2024 (Arcep/Arcom).

## Méthodologie

### Phase 1 — Collecte d'informations automatique

Scanne le projet pour extraire :

1. **Identité du projet** : `package.json` (name, description), `README.md`, `pyproject.toml`, `Cargo.toml`, etc.
2. **Stack technique** : frameworks, langages, dépendances principales
3. **Infrastructure** : `Dockerfile`, `docker-compose.yml`, `terraform/`, `vercel.json`, `.github/workflows/`, config serveur
4. **Hébergeur** : identifié via la config de déploiement
5. **Résultats d'audits RGESN** : si des rapports d'audit précédents existent dans le projet (`.claude/` ou docs), les intégrer
6. **Services tiers** : trackers, APIs externes, CDN, etc.
7. **Contenus** : types de médias utilisés, formats, pipelines d'optimisation

### Phase 2 — Informations manquantes

Pour les critères qui ne peuvent pas être évalués automatiquement, pose des **questions ciblées** à l'utilisateur. Regroupe-les pour minimiser les allers-retours :

```
Pour compléter la déclaration, j'ai besoin des informations suivantes :

**Stratégie (section 1)**
1. Dans quel(s) ODD s'inscrit le service ? (critère 1.1)
2. Qui est le référent écoconception ? Nom et titre (critère 1.3)
3. Fréquence des revues écoconception prévue ? (critère 1.4)
4. Des objectifs de réduction d'impact ont-ils été fixés ? Lesquels ? (critère 1.5)

**Hébergement (section 8)**
5. Nom de l'hébergeur et localisation des serveurs ? (critères 8.1, 8.6)
6. PUE de l'hébergeur ? (critère 8.3)
7. WUE de l'hébergeur ? (critère 8.4)
8. Mix énergétique / part d'énergie renouvelable ? (critère 8.5)

**Spécifications (section 2)**
9. Quels sont les terminaux les plus anciens supportés ? (critère 2.1, 2.2)
10. Des exigences écoconception sont-elles imposées aux fournisseurs ? (critère 2.8)
```

### Phase 3 — Génération du document

Génère la déclaration en Markdown en suivant **exactement** la structure du modèle officiel RGESN 2024.

## Structure de la déclaration

```markdown
# Déclaration d'écoconception de [NOM DU SERVICE]

**Date de réalisation** : [date]
**Version** : 1.0

---

## Résumé

### Objectif

Le service [NOM] s'inscrit dans une démarche d'écoconception visant à réduire
les impacts environnementaux. Cette déclaration a été rédigée le [date], dans
le cadre de la mise en œuvre du référentiel général de l'écoconception des
services numériques (version 2024).

Le référentiel, réalisé par l'Arcep et l'Arcom en collaboration avec l'ADEME,
la DINUM, la CNIL et l'Inria, est disponible sur le
[site web de l'Arcep](https://www.arcep.fr/demarches-et-services/professionnels/referentiel-general-ecoconception-services-numeriques.html).

### Critères validés par le service numérique

[LISTE DES NUMÉROS : 1.1, 1.2, 1.3, ...]

### Critères non validés par le service numérique

[LISTE DES NUMÉROS]

### Critères non applicables

[LISTE DES NUMÉROS + justification pour chaque N/A]

### Score d'avancement

**Score d'avancement au [date]** : [XX]%

Formule :
(Σ critères validés × poids) / (Σ critères applicables × poids) × 100
- Prioritaire : ×1.5
- Recommandé : ×1.25
- Modéré : ×1.0

Score d'avancement précédent : [si disponible]
Objectif à [date + 2 ans] : [XX]%

### Plan d'avancement

Les pistes d'actions suivantes sont ou seront mises en place :
[LISTE DES ACTIONS PRIORITAIRES issues des audits]

Des revues et audits sont réalisés tous les [fréquence].

### Chemins critiques et unités fonctionnelles évalués

Le diagnostic d'écoconception a été mené le [date] sur les échantillons suivants :
[DÉTAIL : pages/fonctionnalités principales évaluées]

### Référent en écoconception numérique (critère 1.3)

- Nom : [NOM]
- Titre : [TITRE]

---

## Détails du diagnostic

### 1 Stratégie

#### Critère 1.1 — Utilité du service
[ÉVALUATION + JUSTIFICATION]

#### Critère 1.2 — Cibles utilisatrices
[DÉTAIL]

[... continuer pour CHAQUE critère applicable, en suivant l'ordre 1.1 → 9.7 ...]

### 2 Spécifications
[...]

### 3 Architecture
[...]

### 4 Expérience et interface utilisateur
[...]

### 5 Contenus
[...]

### 6 Frontend
[...]

### 7 Backend
[...]

### 8 Hébergement
[...]

### 9 Algorithmie
[Si applicable, sinon indiquer N/A avec justification]
```

## Calcul du score

Implémente le calcul exact du score RGESN 2024 :

```
Score = (Σ critères validés pondérés) / (Σ critères applicables pondérés) × 100

Où la pondération est :
- Critères "Prioritaire" (30 critères) : × 1.5
- Critères "Recommandé" (28 critères) : × 1.25
- Critères "Modéré" (20 critères) : × 1.0

Les critères N/A sont EXCLUS du dénominateur.
Les critères "Partiel" ne sont PAS validés (comptent comme non validés).
```

Détaille le calcul dans le rapport :

```
| Priorité | Validés | Applicables | Points validés | Points possibles |
|----------|---------|-------------|----------------|-----------------|
| Prioritaire (×1.5) | X | Y | X × 1.5 | Y × 1.5 |
| Recommandé (×1.25) | X | Y | X × 1.25 | Y × 1.25 |
| Modéré (×1.0) | X | Y | X × 1.0 | Y × 1.0 |
| **Total** | | | **XX** | **YY** |

**Score** = XX / YY × 100 = **ZZ%**
```

## Instructions importantes

- **Remplis tout ce qui est extractible** du code et des configurations.
- Pour ce qui manque, indique clairement `[À COMPLÉTER — critère X.X]`.
- **Ne fabrique pas** d'informations : si tu ne trouves pas l'info, mets le placeholder.
- Le document doit être **publiable en l'état** (aux placeholders près).
- Inclus les **liens vers les fichiers source** pertinents du projet quand tu cites un constat.
- Le fichier généré sera sauvegardé dans `docs/declaration-ecoconception.md`.
