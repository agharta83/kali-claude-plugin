---
title: Extension Brainstorming avec intégration Jira
created: 2026-01-30
status: draft
---

# Extension Brainstorming avec intégration Jira

## Objectif

Créer un plugin `obat-tools` qui étend la commande `/brainstorm` de superpowers avec une intégration Jira intelligente. Le plugin permet de brainstormer avec le contexte complet d'un ticket Jira existant et de générer des suggestions de nouveaux tickets.

## Commandes

| Commande | Rôle |
|----------|------|
| `/brainstorm` (étendu) | Brainstorming enrichi par contexte Jira avec flag `--jira` ou détection auto |
| `/jira-sync` | Synchronise les suggestions du design doc vers Jira |

## Flux principal

```
Utilisateur lance /brainstorm --jira OBAT-123
         ↓
Claude récupère le ticket + toute sa hiérarchie via MCP Jira
         ↓
Claude analyse et propose le type (epic/story/task/subtask)
         ↓
Brainstorming structuré avec connaissance du contexte existant
         ↓
Génère: docs/plans/OBAT-123-design.md
        + Section "Suggestions Jira" (nouveaux tickets, modifications)
         ↓
Utilisateur lance /jira-sync (optionnel)
         ↓
Création/modification des tickets dans Jira
```

## Structure du plugin

```
obat-claude-plugins/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── commands/
│   ├── brainstorm.md        # Surcharge la commande superpowers
│   └── jira-sync.md         # Nouvelle commande
├── skills/
│   ├── jira-brainstorming/
│   │   └── SKILL.md
│   └── jira-sync/
│       └── SKILL.md
├── config/
│   └── plugin-config.yaml   # Config équipe
└── README.md
```

## Skill jira-brainstorming

### Déclenchement

Trois façons d'activer le mode Jira :

1. **Flag explicite** : `/brainstorm --jira OBAT-123`
2. **Flag sans ID** : `/brainstorm --jira` (Claude demande l'ID)
3. **Détection auto** : `/brainstorm "améliorer OBAT-123"` (Claude propose)

### Phase 1 : Récupération du contexte Jira

Claude utilise les outils MCP Jira pour récupérer :

- Le ticket cible + ses parents (jusqu'à l'epic)
- Tous les enfants (stories → tasks → subtasks)
- Pour chaque ticket :
  - Titre, description, statut, type
  - Acceptance criteria
  - Commentaires récents
  - Historique des changements
  - Pièces jointes
  - Story points, sprint, labels
  - Assignee, priorité

### Phase 2 : Analyse et confirmation

Claude analyse la hiérarchie et propose :

> "J'ai récupéré l'epic OBAT-100 avec 5 stories, 12 tasks et 8 subtasks.
> Le ticket OBAT-123 que vous avez mentionné est une **Story**.
> Souhaitez-vous brainstormer au niveau de cette story, ou remonter à l'epic ?"

### Phase 3 : Brainstorming structuré

Le brainstorming suit le processus standard superpowers :

- Questions une par une
- Exploration des approches (2-3 options)
- Validation incrémentale du design

Avec la connaissance du contexte Jira existant pour éviter les doublons et s'aligner sur l'existant.

## Format du document de design

### Nommage du fichier

| Contexte | Format |
|----------|--------|
| Avec Jira | `docs/plans/OBAT-123-design.md` |
| Sans Jira | `docs/plans/YYYY-MM-DD-<topic>-design.md` |

### Structure du document

```yaml
---
# Métadonnées Jira
jira:
  source_ticket: OBAT-123
  project: OBAT
  component: backend
  labels: [feature, api]
  priority: Medium
  default_assignee: null
  sprint: Sprint 42

# Contexte récupéré (lecture seule)
context:
  epic: OBAT-100
  total_tickets_analyzed: 26
  retrieved_at: 2026-01-29T14:30:00Z
---

# Design : Titre du brainstorming

## Contexte Jira

Résumé de la hiérarchie analysée et des éléments clés découverts.

## Design

### Architecture
[Contenu du brainstorming validé...]

### Composants
[...]

## Suggestions Jira

### Nouveaux tickets à créer

- **[Story]** Implémenter l'authentification OAuth
  - Parent: OBAT-123
  - Description: ...
  - Acceptance criteria: ...

- **[Task]** Configurer le provider OAuth
  - Parent: (story ci-dessus)
  - Description: ...

### Modifications suggérées

- **OBAT-124** : Mettre à jour l'acceptance criteria
  - Ajouter: "Doit supporter le refresh token"
```

## Commande /jira-sync

### Usage

```bash
/jira-sync                    # Sync le dernier design doc Jira trouvé
/jira-sync OBAT-123          # Sync le design doc pour ce ticket spécifique
/jira-sync --dry-run         # Prévisualise sans créer/modifier
```

### Processus de synchronisation

1. **Lecture** : Parse le design doc et extrait les suggestions Jira
2. **Validation** : Vérifie que les tickets parents existent toujours
3. **Prévisualisation** : Affiche un résumé des actions prévues

```
Actions prévues :
   ├── Créer 2 stories sous OBAT-123
   ├── Créer 3 tasks
   ├── Créer 1 subtask
   └── Modifier 1 ticket existant (OBAT-124)

Confirmer ? [o/N]
```

4. **Exécution** : Crée/modifie les tickets via MCP Jira
5. **Mise à jour du doc** : Ajoute les IDs Jira créés dans le design doc

### Après synchronisation

Le document est mis à jour avec les IDs créés :

```markdown
## Suggestions Jira

### Nouveaux tickets à créer

- **[Story]** Implémenter l'authentification OAuth
  - ✅ Créé: OBAT-150
```

## Configuration

### Configuration équipe (plugin)

Fichier : `config/plugin-config.yaml`

```yaml
# Configuration partagée équipe Obat
jira:
  # Composants disponibles
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
```

### Configuration utilisateur

Fichier : `~/.claude/config/obat-jira.yaml`

```yaml
# Configuration personnelle (chaque développeur)
jira:
  default_project: OBAT        # Requis
  board_id: 42                  # Requis
  default_assignee: ""          # Vide par défaut
  default_priority: Medium      # Optionnel
```

Au premier lancement avec `--jira`, si la config utilisateur n'existe pas, Claude guide le développeur pour la créer.

## Dépendances

- **Plugin superpowers** : Pour le skill brainstorming de base
- **MCP Jira** (`mcp__atlassian__jira_*`) : Pour l'interaction avec Jira

## Limites

Ce que le plugin NE fait PAS :

- Pas de modification automatique sans confirmation
- Pas de suppression de tickets
- Pas de changement de statut (transitions Jira)

## Composants à implémenter

| Composant | Description |
|-----------|-------------|
| `commands/brainstorm.md` | Surcharge la commande, détecte le contexte Jira |
| `commands/jira-sync.md` | Commande de synchronisation vers Jira |
| `skills/jira-brainstorming/SKILL.md` | Logique de brainstorming enrichi Jira |
| `skills/jira-sync/SKILL.md` | Logique de création/modification tickets |
| `config/plugin-config.yaml` | Configuration par défaut équipe |
