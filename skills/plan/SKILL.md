---
name: plan
description: "Création de plans d'implémentation. Utilisez --prd pour générer un format Ralph Loop."
---

# Création de plans d'implémentation

## Routage

Analyser la requête utilisateur pour déterminer le mode :

- `/plan` ou `/plan <description>` → Mode standard (plan markdown)
- `/plan --prd [TICKET-ID]` → Mode PRD (prd.json pour Ralph Loop)
- `/plan status [TICKET-ID]` → Affiche le statut d'un PRD existant

---

# Mode Standard : Plan Markdown

## Overview

Écrire des plans d'implémentation complets en supposant que l'ingénieur n'a aucun contexte sur le codebase. Documenter tout ce qu'il doit savoir : quels fichiers toucher pour chaque tâche, code, tests, docs à vérifier, comment tester. Donner le plan complet en tâches de petite taille. DRY. YAGNI. TDD. Commits fréquents.

Supposer que c'est un développeur compétent, mais qui ne connaît presque rien de nos outils ou du domaine. Supposer qu'il ne connaît pas bien le design de tests.

**Annoncer au début :** "Je crée un plan d'implémentation détaillé."

**Sauvegarder dans :** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Granularité des tâches

**Chaque étape est une action (2-5 minutes) :**
- "Écrire le test qui échoue" - étape
- "L'exécuter pour vérifier qu'il échoue" - étape
- "Implémenter le code minimal pour faire passer le test" - étape
- "Exécuter les tests et vérifier qu'ils passent" - étape
- "Commiter" - étape

## En-tête du document

**Chaque plan DOIT commencer par cet en-tête :**

```markdown
# [Nom de la Feature] - Plan d'implémentation

**Objectif :** [Une phrase décrivant ce qu'on construit]

**Architecture :** [2-3 phrases sur l'approche]

**Stack technique :** [Technologies/librairies clés]

---
```

## Structure des tâches

```markdown
### Tâche N : [Nom du composant]

**Fichiers :**
- Créer : `exact/path/to/file.py`
- Modifier : `exact/path/to/existing.py:123-145`
- Test : `tests/exact/path/to/test.py`

**Étape 1 : Écrire le test qui échoue**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Étape 2 : Exécuter le test pour vérifier qu'il échoue**

Exécuter : `pytest tests/path/test.py::test_name -v`
Attendu : FAIL avec "function not defined"

**Étape 3 : Écrire l'implémentation minimale**

```python
def function(input):
    return expected
```

**Étape 4 : Exécuter le test pour vérifier qu'il passe**

Exécuter : `pytest tests/path/test.py::test_name -v`
Attendu : PASS

**Étape 5 : Commiter**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Règles

- Chemins de fichiers exacts toujours
- Code complet dans le plan (pas "ajouter la validation")
- Commandes exactes avec sortie attendue
- DRY, YAGNI, TDD, commits fréquents

## Après le plan

Proposer le choix d'exécution :

> "Plan terminé et sauvegardé dans `docs/plans/<filename>.md`.
>
> **Options d'exécution :**
> 1. **Subagent-Driven (cette session)** - Un subagent frais par tâche, revue entre les tâches
> 2. **Session parallèle (séparée)** - Nouvelle session dédiée à l'exécution
>
> **Quelle approche ?"**

---

# Mode PRD : Format Ralph Loop

## Overview

Génère un fichier `prd.json` pour alimenter une boucle Ralph Loop. Extrait les user stories depuis les acceptance criteria Jira, les sous-tickets existants, et les suggestions du brainstorming.

## Déclenchement

- `/plan --prd OBAT-123`
- `/plan --prd` (demander l'ID du ticket)
- Proposition automatique après brainstorming (si ticket = Story/Task/Subtask)

## Étape 1 : Collecte des sources

### Source 1 : Acceptance criteria du ticket principal

Récupérer via `mcp__atlassian__jira_get_issue` :
- Champ description (chercher les critères d'acceptation)
- Champs custom (acceptance criteria si présent)

Transformer chaque critère en user story :
```json
{
  "id": "US-001",
  "source": "jira-ac",
  "title": "Critère d'acceptation",
  "acceptanceCriteria": ["Le critère original"],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

### Source 2 : Sous-tickets Jira

Récupérer les tasks/subtasks liés au ticket principal.

Pour chaque sous-ticket :
```json
{
  "id": "US-002",
  "source": "jira-subtask",
  "jiraId": "OBAT-124",
  "title": "Titre du sous-ticket",
  "acceptanceCriteria": ["Critères du sous-ticket"],
  "priority": 2,
  "passes": false,
  "notes": ""
}
```

### Source 3 : Suggestions du brainstorming

Si un design doc existe (`docs/plans/<TICKET-ID>-design.md`), extraire la section "Nouveaux tickets à créer".

Pour chaque suggestion :
```json
{
  "id": "US-003",
  "source": "brainstorm",
  "title": "Titre de la suggestion",
  "acceptanceCriteria": ["Critères du design doc"],
  "priority": 3,
  "passes": false,
  "notes": ""
}
```

## Étape 2 : Analyse des dépendances

Analyser les user stories collectées pour détecter les dépendances :
- Références entre stories ("après US-001", "dépend de...")
- Ordre logique d'implémentation (setup avant utilisation)

Réordonner les stories par priorité basée sur les dépendances.

## Étape 3 : Génération du fichier

Générer `docs/plans/<TICKET-ID>-prd.json` :

```json
{
  "ticketId": "OBAT-123",
  "branchName": "feature/OBAT-123-titre-kebab",
  "designDoc": "docs/plans/OBAT-123-design.md",
  "createdAt": "2026-01-30T14:30:00Z",
  "userStories": [
    // Stories ordonnées par priorité
  ]
}
```

## Étape 4 : Affichage du résumé

Afficher :

```
PRD généré : docs/plans/OBAT-123-prd.json

User stories (5) :
  1. [jira-ac] Critère d'acceptation 1
  2. [jira-ac] Critère d'acceptation 2
  3. [jira-subtask] OBAT-124 - Sous-tâche
  4. [brainstorm] Suggestion 1
  5. [brainstorm] Suggestion 2

Pour lancer Ralph Loop :
/ralph OBAT-123
```

---

# Mode Status : Statut du PRD

## Overview

Affiche l'état d'avancement des user stories dans un fichier prd.json. Montre quelles stories sont complétées (passes: true) et lesquelles sont en attente.

## Déclenchement

- `/plan status [TICKET-ID]`

## Étape 1 : Localisation du fichier

1. Si un ID est fourni : chercher `docs/plans/<ID>-prd.json`
2. Sinon : trouver le prd.json le plus récent dans `docs/plans/`
3. Si aucun trouvé : informer l'utilisateur

## Étape 2 : Lecture et analyse

Lire le fichier JSON et calculer :
- Nombre total de stories
- Nombre de stories complétées (passes: true)
- Nombre de stories en attente (passes: false)
- Pourcentage de complétion

## Étape 3 : Affichage

Format d'affichage :

```
PRD Status : OBAT-123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Progress : 2/5 (40%)
[██████████░░░░░░░░░░░░░░░]

Stories :
  ✅ US-001 [jira-ac] Critère d'acceptation 1
  ✅ US-002 [jira-ac] Critère d'acceptation 2
  ⏳ US-003 [jira-subtask] OBAT-124 - Sous-tâche
  ⏳ US-004 [brainstorm] Suggestion 1
  ⏳ US-005 [brainstorm] Suggestion 2

Prochaine story : US-003 - OBAT-124 - Sous-tâche

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fichier : docs/plans/OBAT-123-prd.json
```

## Notes sur les stories

Si une story a des notes (champ `notes`), les afficher :

```
  ⏳ US-003 [jira-subtask] OBAT-124 - Sous-tâche
     Note: "Bloqué par problème de permissions"
```
