## Écoconception — RGESN 2024

Ce projet applique le Référentiel Général d'Écoconception des Services Numériques (RGESN 2024).
Réf: https://www.arcep.fr/demarches-et-services/professionnels/referentiel-general-ecoconception-services-numeriques.html

### Principes directeurs

Toute modification de code DOIT respecter les principes suivants, par ordre de priorité :

1. **Sobriété fonctionnelle** : ne pas ajouter de fonctionnalité sans besoin utilisateur avéré (1.1, 1.2)
2. **Compatibilité terminaux anciens** : le service doit tourner sur du matériel d'au moins 7 ans (natif) ou 10 ans (web) (2.2)
3. **Compatibilité logicielle** : supporter les OS de 5 ans et navigateurs de 2 ans (2.4)
4. **Performance réseau** : le service doit rester utilisable en 3G / 512 Kbit/s (2.3)
5. **Poids minimal** : chaque écran a un budget poids et un budget requêtes (6.1)

### Règles frontend obligatoires

- **Pas d'autoplay** sur les vidéos, audios et animations (4.1)
- **Pas de défilement infini** : utiliser la pagination (4.2)
- **Composants natifs en priorité** : préférer `<select>`, `<dialog>`, `<details>` aux composants custom (4.5)
- **Maximum 2 polices** téléchargées, préférer les system fonts (4.8)
- **Debounce obligatoire** sur toute requête serveur liée à une saisie utilisateur — minimum 300ms (4.9)
- **Validation côté client** avant toute soumission de formulaire (4.10)
- **Informer du poids/format** attendu avant tout upload de fichier (4.11)
- **Images en WebP ou AVIF** sauf contrainte de compatibilité documentée (5.1)
- **Images < 200 KB** sauf justification. Utiliser `srcset` + `sizes` pour le responsive (5.2, 6.4)
- **Lazy loading** sur toutes les images et iframes hors viewport initial (6.5)
- **Pas de ressources inutilisées** : activer le tree-shaking, purger le CSS mort (6.5)
- **Compression Brotli/Gzip** sur tous les assets transférés (6.3)
- **Mise en cache agressive** : Cache-Control avec max-age approprié, immutable sur les assets hashés (6.2)
- **Héberger les assets statiques sur le même domaine** quand c'est possible (6.7)
- **Limiter l'usage des capteurs** (géoloc, caméra, micro) au strict nécessaire avec permission explicite (6.6)
- **Pas de contenu vidéo/audio purement décoratif** (4.6). Préférer texte > image > audio > vidéo (4.7)

### Règles backend obligatoires

- **Cache serveur** sur les données fréquemment accédées (Redis, HTTP cache) (7.1)
- **TTL et politique de purge** sur toutes les données stockées (7.2)
- **Feedback sur les traitements longs** : informer l'utilisateur qu'un traitement est en cours (7.3)
- **Pas de Proof-of-Work** si blockchain utilisée : préférer PoS ou autre consensus sobre (7.4)
- **Collecte de données minimale** : chaque champ en base doit être justifié par un besoin utilisateur (1.6)
- **Pas de tracking/profilage** sans consentement explicite, et uniquement si essentiel au service (1.6)
- **Chiffrement proportionné** : documenter le choix d'algorithme vs le besoin de sécurité (1.7)

### Règles architecture

- **Technologies standard et interopérables** : préférer le web aux apps natives quand c'est possible (1.9)
- **Autoscaling** : l'infra doit s'adapter à la charge, pas tourner à plein régime 24/7 (3.2)
- **Protocoles pérennes** : IPv6, TLS 1.3, HTTP/2+ (3.3)
- **Mises à jour incrémentielles** : pas de full-rebuild quand un diff suffit (3.6)
- **Éteindre les envs inutilisés** : les envs de dev/test/staging doivent être stoppés hors heures ouvrées (3.7)
- **Séparer données chaudes et froides** : archiver ce qui est rarement accédé (8.8)
- **Limiter la duplication** : chaque réplica de données doit être justifié (8.9)

### Règles contenus multimédias

- **Vidéo** : définition adaptée au contexte (pas de 4K sur mobile), codec efficace (AV1 > H.265 > H.264), mode écoute seule proposé si pertinent (5.3, 5.4, 5.5)
- **Audio** : codec Opus ou AAC, bitrate adapté au contexte (5.6)
- **Documents** : format compressé, poids optimisé (5.7)
- **Archivage** : supprimer ou archiver les contenus obsolètes (5.8)

### Règles IA / Algorithmie (si applicable)

- **Justifier le recours à l'entraînement** : un modèle pré-entraîné ou une recherche classique suffit-il ? (9.1)
- **Complexité minimale** : choisir le modèle le plus simple qui satisfait le besoin (9.2)
- **Privilégier le fine-tuning** sur un modèle pré-entraîné plutôt que l'entraînement from-scratch (9.3)
- **Données d'entraînement minimales** : ne pas stocker/collecter plus que nécessaire (9.4)
- **Réentraînement raisonné** : définir des seuils de déclenchement, pas de schedule arbitraire (9.5)
- **Compression de modèle** : quantization, pruning, distillation quand c'est applicable (9.6)
- **Inférence optimisée** : cache de résultats, batch, edge computing quand c'est pertinent (9.7)

### UX / Dark patterns interdits

- **Pas de dark patterns** : pas de pre-checked options, confirmshaming, roach motel, forced continuity (4.14)
- **Notifications limitées par défaut**, désactivables par l'utilisateur (4.13)
- **Informer l'utilisateur** de l'impact environnemental des fonctionnalités lourdes (4.12)
- **Proposer un mode sobriété** / économie de données si pertinent (4.15)
- **Laisser l'utilisateur contrôler l'activation des services tiers** (4.4)

### Hébergement (à documenter dans la déclaration)

Pour l'hébergeur choisi, documenter :
- PUE réel (cible < 1.4, idéal < 1.2) (8.3)
- WUE réel (8.4)
- Origine de l'électricité et part renouvelable (8.5)
- Localisation géographique et cohérence avec les utilisateurs (8.6)
- Politique de gestion durable des équipements (8.2)
- Traitement de la chaleur fatale si PUE > 1.2 (8.7)
- Possibilité de décaler les calculs asynchrones selon la carbonation du réseau (8.10)

### Processus

- **Référent écoconception** identifié dans l'équipe (1.3)
- **Revue de conception** incluant l'impact environnemental avant chaque sprint/feature (2.6)
- **Revue de code** avec critères RGESN dans la checklist de PR review (2.6)
- **Audit régulier** avec le référentiel (au minimum tous les 6 mois) (1.4)
- **Déclaration d'écoconception** publiée et mise à jour (1.4)
- **Open source** : publier le code quand c'est possible (1.8)
- **Stratégie de maintenance et décommissionnement** documentée (2.7)
- **Impact des services tiers** évalué avant intégration (2.10)
- **Impact des composants UI tiers** évalué avant adoption (2.9)
- **Exigences écoconception** imposées aux fournisseurs (2.8)