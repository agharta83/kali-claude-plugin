---
title: Integration PRD et Ralph Loop
created: 2026-01-30
status: draft
---

# Integration PRD et Ralph Loop

## Objectif

Etendre le plugin obat-tools avec la generation de `prd.json` pour alimenter le pattern Ralph Loop (Ralph Wiggum). Permet d'automatiser l'implementation iterative des user stories.

## Declenchement

### Proposition contextuelle (apres brainstorming)

A la fin d'un brainstorming sur un ticket **Story**, **Task** ou **Subtask** (pas Epic), proposer :

> "Ce ticket contient des criteres d'acceptation et/ou des sous-taches. Voulez-vous generer un `prd.json` pour lancer une boucle Ralph ?"

### Commandes manuelles

| Commande | Description |
|----------|-------------|
| `/prd create OBAT-123` | Genere prd.json depuis un ticket Jira |
| `/prd status` | Affiche l'etat des stories (passes: true/false) |

## Sources du PRD

Le `prd.json` est alimente par trois sources (fusionnees) :

1. **Acceptance criteria** du ticket Jira principal
2. **Sous-tickets existants** (tasks/subtasks lies)
3. **Suggestions du brainstorming** (section "Nouveaux tickets a creer")

## Priorisation

Claude analyse les dependances entre les user stories et les ordonne logiquement :
- Stories sans dependance en premier
- Stories dependantes ordonnees selon leurs pre-requis

## Format prd.json

Emplacement : `docs/plans/OBAT-123-prd.json`

```json
{
  "ticketId": "OBAT-123",
  "branchName": "feature/OBAT-123-titre",
  "designDoc": "docs/plans/OBAT-123-design.md",
  "userStories": [
    {
      "id": "US-001",
      "source": "jira-ac",
      "title": "Titre de la story",
      "acceptanceCriteria": [
        "Critere verifiable 1",
        "Critere verifiable 2"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "source": "jira-subtask",
      "jiraId": "OBAT-124",
      "title": "Sous-tache existante",
      "acceptanceCriteria": [
        "Critere depuis Jira"
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "source": "brainstorm",
      "title": "Story suggeree par brainstorming",
      "acceptanceCriteria": [
        "Critere du design doc"
      ],
      "priority": 3,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Champs source

| Source | Description |
|--------|-------------|
| `jira-ac` | Acceptance criteria du ticket principal |
| `jira-subtask` | Sous-ticket Jira existant |
| `brainstorm` | Suggestion du design doc |

## Configuration par defaut

Dans `config/plugin-config.yaml` :

```yaml
ralph:
  max_iterations: 20
  completion_promise: "ALL_STORIES_PASS"
```

## Flux d'utilisation

### Via brainstorming

```
/brainstorm --jira OBAT-123 (Story/Task/Subtask)
       |
       v
Design doc + ADR (si pertinent)
       |
       v
"Voulez-vous generer un prd.json pour Ralph Loop ?"
       |
       v
Genere docs/plans/OBAT-123-prd.json
       |
       v
/ralph-loop "Implementer OBAT-123 selon prd.json" --max-iterations 20 --completion-promise "ALL_STORIES_PASS"
```

### Via commande manuelle

```
/prd create OBAT-123
       |
       v
Genere docs/plans/OBAT-123-prd.json
       |
       v
/prd status  (pour verifier)
       |
       v
/ralph-loop "..." --max-iterations 20 --completion-promise "ALL_STORIES_PASS"
```

### Arret de la boucle

```
/cancel-ralph    # Annule la boucle active
```

## Composants a implementer

| Composant | Description |
|-----------|-------------|
| `skills/prd-generator/SKILL.md` | Skill de generation du prd.json |
| `skills/prd-status/SKILL.md` | Skill d'affichage du statut |
| `commands/prd.md` | Commande /prd avec sous-commandes |
| Mise a jour `jira-brainstorming` | Ajout Phase 7 (proposition PRD) |
| Mise a jour `plugin-config.yaml` | Ajout section ralph |
| Mise a jour `README.md` | Documentation PRD/Ralph |

## Dependances

- Plugin `ralph-loop` (installe) - pour le skill ralph-loop existant
- MCP Jira - pour recuperer les tickets
