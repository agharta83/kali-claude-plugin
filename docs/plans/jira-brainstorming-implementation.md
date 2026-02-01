# Extension Brainstorming Jira - Plan d'implémentation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Étendre le plugin obat-tools avec une intégration Jira pour la commande /brainstorm et une nouvelle commande /jira-sync.

**Architecture:** Le plugin surcharge la commande /brainstorm de superpowers. Quand un contexte Jira est détecté (flag --jira ou ID dans le texte), le skill jira-brainstorming prend le relais. Il récupère la hiérarchie complète du ticket via MCP Jira, puis guide le brainstorming avec ce contexte. Les suggestions sont sauvegardées dans un design doc que /jira-sync peut ensuite synchroniser vers Jira.

**Tech Stack:** Claude Code plugins (Markdown), MCP Jira tools, YAML config

---

## Task 1: Configuration équipe

**Files:**
- Create: `config/plugin-config.yaml`

**Step 1: Créer le dossier config**

```bash
mkdir -p config
```

**Step 2: Écrire la configuration équipe**

```yaml
# Configuration partagée équipe Obat
jira:
  # Composants disponibles (favoris)
  preferred_components:
    - backend
    - frontend
    - mobile
    - infrastructure

  # Labels fréquents
  common_labels:
    - feature
    - bugfix
    - tech-debt
    - security

# Comportement du brainstorming
brainstorming:
  # Proposer de récupérer le contexte Jira si un ID est détecté
  auto_detect_jira_ids: true

  # Profondeur de génération (epic → story → task → subtask)
  default_depth: full

# Template pour la config utilisateur (à copier dans ~/.claude/config/obat-jira.yaml)
user_config_template:
  jira:
    default_project: ""      # Requis - ex: OBAT
    board_id: null           # Requis - ex: 42
    default_assignee: ""     # Optionnel - vide par défaut
    default_priority: Medium # Optionnel
```

**Step 3: Vérifier que le fichier est valide**

```bash
cat config/plugin-config.yaml
```

---

## Task 2: Skill jira-brainstorming

**Files:**
- Create: `skills/jira-brainstorming/SKILL.md`

**Step 1: Créer le dossier du skill**

```bash
mkdir -p skills/jira-brainstorming
```

**Step 2: Écrire le skill SKILL.md**

```markdown
---
name: jira-brainstorming
description: "Use when brainstorming with Jira context - when --jira flag is present or a Jira ticket ID (like OBAT-123) is mentioned in the request"
---

# Brainstorming avec contexte Jira

## Overview

Étend le brainstorming standard avec la récupération et l'analyse du contexte Jira. Récupère la hiérarchie complète d'un ticket (epic → stories → tasks → subtasks) pour informer le design.

## Déclenchement

Ce skill s'active quand :
1. Flag explicite : `/brainstorm --jira OBAT-123`
2. Flag sans ID : `/brainstorm --jira` (demander l'ID)
3. Détection auto : Un ID Jira (pattern `[A-Z]+-\d+`) est mentionné

## Phase 1 : Vérification de la configuration utilisateur

Avant toute récupération Jira, vérifier que `~/.claude/config/obat-jira.yaml` existe.

Si absent, guider l'utilisateur :

> "Je n'ai pas trouvé votre configuration Jira personnelle.
> Créez le fichier `~/.claude/config/obat-jira.yaml` avec :
> ```yaml
> jira:
>   default_project: OBAT    # Votre projet par défaut
>   board_id: 42             # ID de votre board Jira
>   default_assignee: ""     # Votre email (optionnel)
>   default_priority: Medium
> ```
> Puis relancez la commande."

## Phase 2 : Récupération du contexte Jira

Utiliser les outils MCP Jira dans cet ordre :

1. **Récupérer le ticket source** avec `mcp__atlassian__jira_get_issue`
2. **Identifier le type** (Epic, Story, Task, Subtask)
3. **Remonter la hiérarchie** jusqu'à l'Epic parent
4. **Descendre la hiérarchie** pour récupérer tous les enfants

Pour chaque ticket, récupérer :
- Titre, description, statut, type
- Acceptance criteria (champ customfield si applicable)
- Commentaires récents
- Story points, sprint, labels
- Assignee, priorité
- Liens (blocks, is blocked by, relates to)

## Phase 3 : Analyse et confirmation

Présenter un résumé :

> "J'ai récupéré la hiérarchie Jira :
> - Epic : OBAT-100 - Refonte authentification
>   - Story : OBAT-123 - Implémenter OAuth (votre ticket)
>     - Task : OBAT-124 - Configurer provider
>     - Task : OBAT-125 - Créer middleware
>   - Story : OBAT-126 - Tests E2E
>
> Total : 1 epic, 2 stories, 2 tasks analysés.
>
> Souhaitez-vous brainstormer au niveau de la **Story OBAT-123**, ou remonter à l'**Epic OBAT-100** ?"

## Phase 4 : Brainstorming structuré

Suivre le processus standard de brainstorming (superpowers:brainstorming) :
- Questions une par une
- Proposer 2-3 approches
- Valider le design par sections

**Avec le contexte Jira en tête :**
- Éviter de proposer des éléments qui existent déjà
- S'aligner sur la terminologie et structure existante
- Référencer les tickets liés quand pertinent

## Phase 5 : Génération du document

Sauvegarder dans `docs/plans/<TICKET-ID>-design.md` avec :

1. **Frontmatter YAML** contenant les métadonnées Jira
2. **Section Contexte Jira** résumant la hiérarchie analysée
3. **Section Design** avec le résultat du brainstorming
4. **Section Suggestions Jira** avec :
   - Nouveaux tickets à créer (type, parent, description, acceptance criteria)
   - Modifications suggérées sur tickets existants

## Format des suggestions Jira

```markdown
## Suggestions Jira

### Nouveaux tickets à créer

#### [Story] Implémenter le refresh token
- **Parent:** OBAT-123
- **Description:** Ajouter le support du refresh token OAuth pour maintenir les sessions utilisateur.
- **Acceptance criteria:**
  - [ ] Le refresh token est stocké de façon sécurisée
  - [ ] Le token est renouvelé automatiquement avant expiration
  - [ ] En cas d'échec, l'utilisateur est redirigé vers login
- **Labels:** feature, security
- **Story points:** 3

#### [Task] Créer le service TokenRefreshService
- **Parent:** (story ci-dessus)
- **Description:** Service responsable du renouvellement automatique des tokens.

### Modifications suggérées

#### OBAT-124 - Configurer provider
- **Ajouter à la description:** Inclure la configuration du refresh token endpoint
- **Ajouter acceptance criteria:**
  - [ ] Le refresh endpoint est configuré
```

## Après le design

Proposer :
> "Design sauvegardé dans `docs/plans/OBAT-123-design.md`.
>
> Pour synchroniser les suggestions vers Jira, utilisez `/jira-sync OBAT-123`."
```

**Step 3: Vérifier la syntaxe du fichier**

```bash
head -5 skills/jira-brainstorming/SKILL.md
```

---

## Task 3: Skill jira-sync

**Files:**
- Create: `skills/jira-sync/SKILL.md`

**Step 1: Créer le dossier du skill**

```bash
mkdir -p skills/jira-sync
```

**Step 2: Écrire le skill SKILL.md**

```markdown
---
name: jira-sync
description: "Use when synchronizing a design document to Jira - creates new tickets and applies modifications from the Suggestions Jira section"
---

# Synchronisation vers Jira

## Overview

Lit un document de design généré par jira-brainstorming et synchronise les suggestions vers Jira : création de nouveaux tickets et modifications des tickets existants.

## Usage

```
/jira-sync                    # Sync le dernier design doc Jira trouvé
/jira-sync OBAT-123          # Sync le design doc docs/plans/OBAT-123-design.md
/jira-sync --dry-run         # Prévisualise sans créer/modifier
```

## Phase 1 : Localisation du document

1. Si un ID est fourni : chercher `docs/plans/<ID>-design.md`
2. Sinon : trouver le design doc Jira le plus récent dans `docs/plans/`
3. Si aucun trouvé : informer l'utilisateur

## Phase 2 : Parsing du document

Extraire du frontmatter YAML :
- `jira.source_ticket` : ticket de référence
- `jira.project` : projet cible
- `jira.default_assignee`, `jira.priority`, etc.

Parser la section `## Suggestions Jira` :
- Identifier les blocs `### Nouveaux tickets à créer`
- Identifier les blocs `### Modifications suggérées`

## Phase 3 : Validation

Vérifier via MCP Jira :
- Le projet existe et est accessible
- Les tickets parents référencés existent
- L'utilisateur a les permissions de création

## Phase 4 : Prévisualisation

Afficher un résumé des actions :

```
📋 Actions prévues pour OBAT-123-design.md :

CRÉATIONS :
  ├── [Story] Implémenter le refresh token
  │   └── Parent: OBAT-123
  │   └── Story points: 3
  ├── [Task] Créer le service TokenRefreshService
  │   └── Parent: (story ci-dessus)

MODIFICATIONS :
  └── OBAT-124 - Configurer provider
      └── Ajouter acceptance criteria (1 item)

Confirmer ? [o/N]
```

Si `--dry-run` : s'arrêter ici.

## Phase 5 : Exécution

Pour chaque nouveau ticket :
1. Utiliser `mcp__atlassian__jira_create_issue`
2. Stocker l'ID créé pour les références parent
3. Si le parent est "(story ci-dessus)", utiliser l'ID créé à l'étape précédente

Pour chaque modification :
1. Utiliser `mcp__atlassian__jira_get_issue` pour récupérer l'état actuel
2. Merger les modifications (append, pas replace)
3. Utiliser `mcp__atlassian__jira_update_issue`

## Phase 6 : Mise à jour du document

Après création réussie, mettre à jour le design doc :

```markdown
#### [Story] Implémenter le refresh token
- ✅ **Créé:** OBAT-150
- **Parent:** OBAT-123
...
```

Ajouter en bas du document :

```markdown
---
## Historique de synchronisation

- **2026-01-30 14:30** : Créé OBAT-150, OBAT-151. Modifié OBAT-124.
```

## Gestion des erreurs

- **Permission refusée** : Lister les tickets non créés, suggérer de contacter l'admin
- **Ticket parent inexistant** : Proposer de créer sous un autre parent ou skip
- **Champ requis manquant** : Demander la valeur à l'utilisateur

## Rollback

Ce skill ne supprime jamais de tickets. En cas d'erreur partielle :
- Les tickets créés restent dans Jira
- Le document est mis à jour avec les IDs créés
- Les tickets non créés restent marqués sans checkmark
```

**Step 3: Vérifier la syntaxe du fichier**

```bash
head -5 skills/jira-sync/SKILL.md
```

---

## Task 4: Commande brainstorm (surcharge)

**Files:**
- Create: `commands/brainstorm.md`

**Step 1: Créer le dossier commands**

```bash
mkdir -p commands
```

**Step 2: Écrire la commande brainstorm.md**

```markdown
---
description: "Brainstorming avec support Jira optionnel. Utilisez --jira pour enrichir avec le contexte d'un ticket existant."
disable-model-invocation: true
---

# Instructions de routage

Analyser la requête utilisateur pour déterminer le mode :

## Mode Jira activé si :
1. Le flag `--jira` est présent (avec ou sans ID)
2. Un ID Jira est détecté dans le texte (pattern : lettres majuscules + tiret + chiffres, ex: OBAT-123, PROJ-42)

Si mode Jira → Invoquer le skill `jira-brainstorming` et le suivre exactement.

## Mode standard si :
Aucun flag --jira et aucun ID Jira détecté.

Si mode standard → Invoquer le skill `superpowers:brainstorming` et le suivre exactement.
```

**Step 3: Vérifier le fichier**

```bash
cat commands/brainstorm.md
```

---

## Task 5: Commande jira-sync

**Files:**
- Create: `commands/jira-sync.md`

**Step 1: Écrire la commande jira-sync.md**

```markdown
---
description: "Synchronise les suggestions d'un design doc vers Jira. Usage: /jira-sync [TICKET-ID] [--dry-run]"
disable-model-invocation: true
---

Invoke the jira-sync skill and follow it exactly as presented to you.
```

**Step 2: Vérifier le fichier**

```bash
cat commands/jira-sync.md
```

---

## Task 6: Mise à jour du plugin.json

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Step 1: Lire le fichier actuel**

```bash
cat .claude-plugin/plugin.json
```

**Step 2: Mettre à jour avec les métadonnées complètes**

```json
{
  "name": "obat-tools",
  "version": "1.0.0",
  "description": "Outils Claude Code pour l'équipe Obat - Extension brainstorming avec intégration Jira",
  "author": {
    "name": "Équipe Obat"
  },
  "keywords": ["jira", "brainstorming", "obat", "planning"]
}
```

**Step 3: Vérifier la syntaxe JSON**

```bash
cat .claude-plugin/plugin.json | python3 -m json.tool
```

---

## Task 7: Documentation README

**Files:**
- Modify: `README.md`

**Step 1: Lire le README actuel**

```bash
cat README.md
```

**Step 2: Réécrire avec la documentation complète**

```markdown
# obat-tools

Plugin Claude Code pour l'équipe Obat.

## Installation

```bash
/plugin marketplace add https://gitlab.obat.fr/tools/obat-claude-plugins
/plugin install obat-tools@obat-marketplace
```

## Commandes

### /brainstorm

Brainstorming avec support Jira optionnel.

```bash
# Mode standard (identique à superpowers)
/brainstorm créer une API de notifications

# Mode Jira - avec flag explicite
/brainstorm --jira OBAT-123

# Mode Jira - détection automatique
/brainstorm améliorer le ticket OBAT-123
```

En mode Jira, Claude :
1. Récupère le ticket et toute sa hiérarchie (epic → stories → tasks → subtasks)
2. Analyse le contexte existant
3. Guide le brainstorming avec cette connaissance
4. Génère un design doc avec suggestions Jira

### /jira-sync

Synchronise les suggestions d'un design doc vers Jira.

```bash
# Sync un design doc spécifique
/jira-sync OBAT-123

# Sync le dernier design doc Jira
/jira-sync

# Prévisualiser sans créer
/jira-sync --dry-run
```

## Configuration

### Configuration utilisateur (requise)

Créez `~/.claude/config/obat-jira.yaml` :

```yaml
jira:
  default_project: OBAT    # Votre projet Jira
  board_id: 42             # ID de votre board
  default_assignee: ""     # Votre email (optionnel)
  default_priority: Medium
```

### Configuration équipe

Les valeurs par défaut équipe sont dans `config/plugin-config.yaml`.
```

**Step 3: Vérifier le README**

```bash
cat README.md
```

---

## Task 8: Test manuel du plugin

**Step 1: Vérifier la structure complète**

```bash
find . -type f -name "*.md" -o -name "*.yaml" -o -name "*.json" | head -20
```

**Step 2: Vérifier que les skills sont détectables**

```bash
# Vérifier le frontmatter des skills
head -5 skills/jira-brainstorming/SKILL.md
head -5 skills/jira-sync/SKILL.md
```

**Step 3: Vérifier les commandes**

```bash
head -5 commands/brainstorm.md
head -5 commands/jira-sync.md
```

---

## Récapitulatif des fichiers créés

| Fichier | Rôle |
|---------|------|
| `config/plugin-config.yaml` | Configuration équipe |
| `skills/jira-brainstorming/SKILL.md` | Skill brainstorming Jira |
| `skills/jira-sync/SKILL.md` | Skill synchronisation Jira |
| `commands/brainstorm.md` | Commande /brainstorm (surcharge) |
| `commands/jira-sync.md` | Commande /jira-sync |
| `.claude-plugin/plugin.json` | Manifest mis à jour |
| `README.md` | Documentation |
