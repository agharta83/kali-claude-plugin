---
name: skill-creator
description: "Guide pour créer des skills efficaces. Utiliser quand l'utilisateur veut créer un nouveau skill (ou mettre à jour un skill existant) qui étend les capacités de Claude avec des connaissances spécialisées, workflows ou intégrations d'outils."
license: Termes complets dans LICENSE.txt
---

# Créateur de Skills

Ce skill fournit des conseils pour créer des skills efficaces.

## À propos des Skills

Les skills sont des packages modulaires et autonomes qui étendent les capacités de Claude en fournissant des connaissances spécialisées, des workflows et des outils. Ils transforment Claude d'un agent généraliste en un agent spécialisé équipé de connaissances procédurales qu'aucun modèle ne peut posséder entièrement.

### Ce que les Skills apportent

1. Workflows spécialisés - Procédures multi-étapes pour des domaines spécifiques
2. Intégrations d'outils - Instructions pour travailler avec des formats de fichiers ou APIs spécifiques
3. Expertise domaine - Connaissances spécifiques à l'entreprise, schémas, logique métier
4. Ressources embarquées - Scripts, références et assets pour des tâches complexes et répétitives

### Anatomie d'un Skill

Chaque skill consiste en un fichier SKILL.md requis et des ressources optionnelles :

```
nom-du-skill/
├── SKILL.md (requis)
│   ├── Métadonnées YAML frontmatter (requis)
│   │   ├── name: (requis)
│   │   └── description: (requis)
│   └── Instructions Markdown (requis)
└── Ressources embarquées (optionnel)
    ├── scripts/          - Code exécutable (Python/Bash/etc.)
    ├── references/       - Documentation à charger en contexte au besoin
    └── assets/           - Fichiers utilisés en sortie (templates, icônes, polices, etc.)
```

#### SKILL.md (requis)

**Qualité des métadonnées :** Le `name` et la `description` dans le frontmatter YAML déterminent quand Claude utilisera le skill. Être spécifique sur ce que fait le skill et quand l'utiliser. Utiliser la troisième personne (ex: "Ce skill doit être utilisé quand..." plutôt que "Utilise ce skill quand...").

#### Ressources embarquées (optionnel)

##### Scripts (`scripts/`)

Code exécutable (Python/Bash/etc.) pour les tâches qui nécessitent une fiabilité déterministe ou sont réécrites de manière répétée.

- **Quand inclure** : Quand le même code est réécrit de manière répétée ou qu'une fiabilité déterministe est nécessaire
- **Exemple** : `scripts/rotate_pdf.py` pour les tâches de rotation PDF
- **Avantages** : Efficace en tokens, déterministe, peut être exécuté sans charger en contexte
- **Note** : Les scripts peuvent encore devoir être lus par Claude pour des ajustements ou adaptations à l'environnement

##### Références (`references/`)

Documentation et matériel de référence destiné à être chargé au besoin en contexte pour informer le processus et la réflexion de Claude.

- **Quand inclure** : Pour la documentation que Claude devrait référencer pendant le travail
- **Exemples** : `references/finance.md` pour les schémas financiers, `references/mnda.md` pour le template NDA de l'entreprise, `references/policies.md` pour les politiques de l'entreprise, `references/api_docs.md` pour les spécifications API
- **Cas d'usage** : Schémas de base de données, documentation API, connaissances domaine, politiques d'entreprise, guides de workflow détaillés
- **Avantages** : Garde SKILL.md léger, chargé seulement quand Claude détermine que c'est nécessaire
- **Bonne pratique** : Si les fichiers sont volumineux (>10k mots), inclure des patterns de recherche grep dans SKILL.md
- **Éviter la duplication** : L'information doit vivre soit dans SKILL.md soit dans les fichiers de références, pas les deux. Préférer les fichiers de références pour l'information détaillée sauf si c'est vraiment central au skill.

##### Assets (`assets/`)

Fichiers non destinés à être chargés en contexte, mais plutôt utilisés dans la sortie que Claude produit.

- **Quand inclure** : Quand le skill a besoin de fichiers qui seront utilisés dans la sortie finale
- **Exemples** : `assets/logo.png` pour les assets de marque, `assets/slides.pptx` pour les templates PowerPoint, `assets/frontend-template/` pour le boilerplate HTML/React, `assets/font.ttf` pour la typographie
- **Cas d'usage** : Templates, images, icônes, code boilerplate, polices, documents exemples à copier ou modifier
- **Avantages** : Sépare les ressources de sortie de la documentation, permet à Claude d'utiliser les fichiers sans les charger en contexte

### Principe de conception : Divulgation progressive

Les skills utilisent un système de chargement à trois niveaux pour gérer efficacement le contexte :

1. **Métadonnées (name + description)** - Toujours en contexte (~100 mots)
2. **Corps de SKILL.md** - Quand le skill se déclenche (<5k mots)
3. **Ressources embarquées** - Au besoin par Claude (Illimité*)

*Illimité car les scripts peuvent être exécutés sans être lus dans la fenêtre de contexte.

## Processus de création de Skill

Pour créer un skill, suivre le "Processus de création de Skill" dans l'ordre, en sautant les étapes seulement s'il y a une raison claire pour laquelle elles ne s'appliquent pas.

### Étape 1 : Comprendre le Skill avec des exemples concrets

Sauter cette étape seulement quand les patterns d'utilisation du skill sont déjà clairement compris. Elle reste utile même en travaillant avec un skill existant.

Pour créer un skill efficace, comprendre clairement des exemples concrets de comment le skill sera utilisé. Cette compréhension peut venir soit d'exemples directs de l'utilisateur soit d'exemples générés validés avec les retours de l'utilisateur.

Par exemple, pour construire un skill image-editor, les questions pertinentes incluent :

- "Quelles fonctionnalités le skill image-editor devrait-il supporter ? Édition, rotation, autre chose ?"
- "Pouvez-vous donner des exemples de comment ce skill serait utilisé ?"
- "J'imagine que les utilisateurs pourraient demander des choses comme 'Enlève les yeux rouges de cette image' ou 'Fais pivoter cette image'. Y a-t-il d'autres façons dont vous imaginez ce skill utilisé ?"
- "Que dirait un utilisateur qui devrait déclencher ce skill ?"

Pour éviter de submerger les utilisateurs, éviter de poser trop de questions dans un seul message. Commencer avec les questions les plus importantes et faire un suivi au besoin.

Conclure cette étape quand il y a une compréhension claire des fonctionnalités que le skill devrait supporter.

### Étape 2 : Planifier le contenu réutilisable du Skill

Pour transformer les exemples concrets en skill efficace, analyser chaque exemple en :

1. Considérant comment exécuter l'exemple à partir de zéro
2. Identifiant quels scripts, références et assets seraient utiles pour exécuter ces workflows de manière répétée

Exemple : Pour construire un skill `pdf-editor` pour gérer des requêtes comme "Aide-moi à faire pivoter ce PDF", l'analyse montre :

1. Faire pivoter un PDF nécessite de réécrire le même code à chaque fois
2. Un script `scripts/rotate_pdf.py` serait utile à stocker dans le skill

Exemple : Pour concevoir un skill `frontend-webapp-builder` pour des requêtes comme "Construis-moi une app todo" ou "Construis-moi un dashboard pour suivre mes pas", l'analyse montre :

1. Écrire une webapp frontend nécessite le même boilerplate HTML/React à chaque fois
2. Un template `assets/hello-world/` contenant les fichiers de projet boilerplate HTML/React serait utile à stocker dans le skill

Exemple : Pour construire un skill `big-query` pour gérer des requêtes comme "Combien d'utilisateurs se sont connectés aujourd'hui ?", l'analyse montre :

1. Interroger BigQuery nécessite de redécouvrir les schémas de tables et relations à chaque fois
2. Un fichier `references/schema.md` documentant les schémas de tables serait utile à stocker dans le skill

Pour établir le contenu du skill, analyser chaque exemple concret pour créer une liste des ressources réutilisables à inclure : scripts, références et assets.

### Étape 3 : Initialiser le Skill

À ce stade, il est temps de créer effectivement le skill.

Sauter cette étape seulement si le skill en développement existe déjà et qu'une itération ou un packaging est nécessaire. Dans ce cas, continuer à l'étape suivante.

Pour créer un nouveau skill à partir de zéro, toujours exécuter le script `init_skill.py`. Le script génère commodément un nouveau répertoire de skill template qui inclut automatiquement tout ce qu'un skill requiert.

Usage :

```bash
scripts/init_skill.py <nom-du-skill> --path <répertoire-de-sortie>
```

Le script :

- Crée le répertoire du skill au chemin spécifié
- Génère un template SKILL.md avec le frontmatter approprié et des placeholders TODO
- Crée des répertoires de ressources exemples : `scripts/`, `references/` et `assets/`
- Ajoute des fichiers exemples dans chaque répertoire qui peuvent être personnalisés ou supprimés

Après initialisation, personnaliser ou supprimer le SKILL.md généré et les fichiers exemples selon les besoins.

### Étape 4 : Éditer le Skill

Pour éditer le skill (nouvellement généré ou existant), se rappeler que le skill est créé pour qu'une autre instance de Claude l'utilise. Se concentrer sur l'inclusion d'informations qui seraient bénéfiques et non évidentes pour Claude. Considérer quelles connaissances procédurales, détails spécifiques au domaine ou assets réutilisables aideraient une autre instance de Claude à exécuter ces tâches plus efficacement.

#### Commencer avec le contenu réutilisable du Skill

Pour commencer l'implémentation, commencer avec les ressources réutilisables identifiées ci-dessus : fichiers `scripts/`, `references/` et `assets/`. Noter que cette étape peut nécessiter une entrée utilisateur. Par exemple, pour implémenter un skill `brand-guidelines`, l'utilisateur peut avoir besoin de fournir des assets de marque ou templates à stocker dans `assets/`, ou de la documentation à stocker dans `references/`.

Aussi, supprimer tous les fichiers et répertoires exemples non nécessaires pour le skill. Le script d'initialisation crée des fichiers exemples dans `scripts/`, `references/` et `assets/` pour démontrer la structure, mais la plupart des skills n'auront pas besoin de tous.

#### Mettre à jour SKILL.md

**Style d'écriture :** Écrire tout le skill en utilisant la **forme impérative/infinitive** (instructions commençant par un verbe), pas la deuxième personne. Utiliser un langage objectif et instructionnel (ex: "Pour accomplir X, faire Y" plutôt que "Tu devrais faire X" ou "Si tu as besoin de faire X"). Cela maintient la cohérence et la clarté pour la consommation par l'IA.

Pour compléter SKILL.md, répondre aux questions suivantes :

1. Quel est le but du skill, en quelques phrases ?
2. Quand le skill devrait-il être utilisé ?
3. En pratique, comment Claude devrait-il utiliser le skill ? Tout le contenu réutilisable du skill développé ci-dessus devrait être référencé pour que Claude sache comment l'utiliser.

### Étape 5 : Packager un Skill

Une fois le skill prêt, il devrait être packagé dans un fichier zip distribuable qui est partagé avec l'utilisateur. Le processus de packaging valide automatiquement le skill d'abord pour s'assurer qu'il répond à toutes les exigences :

```bash
scripts/package_skill.py <chemin/vers/dossier-skill>
```

Spécification optionnelle du répertoire de sortie :

```bash
scripts/package_skill.py <chemin/vers/dossier-skill> ./dist
```

Le script de packaging va :

1. **Valider** le skill automatiquement, en vérifiant :
   - Format du frontmatter YAML et champs requis
   - Conventions de nommage du skill et structure du répertoire
   - Complétude et qualité de la description
   - Organisation des fichiers et références des ressources

2. **Packager** le skill si la validation passe, créant un fichier zip nommé d'après le skill (ex: `mon-skill.zip`) qui inclut tous les fichiers et maintient la structure de répertoire appropriée pour la distribution.

Si la validation échoue, le script rapportera les erreurs et sortira sans créer de package. Corriger les erreurs de validation et relancer la commande de packaging.

### Étape 6 : Itérer

Après avoir testé le skill, les utilisateurs peuvent demander des améliorations. Souvent cela arrive juste après avoir utilisé le skill, avec un contexte frais de comment le skill a performé.

**Workflow d'itération :**
1. Utiliser le skill sur des tâches réelles
2. Noter les difficultés ou inefficacités
3. Identifier comment SKILL.md ou les ressources embarquées devraient être mises à jour
4. Implémenter les changements et tester à nouveau
