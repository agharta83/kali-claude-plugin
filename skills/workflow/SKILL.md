---
name: workflow
description: "Orchestration automatique du cycle de développement. Enchaîne brainstorm → plan → execute → review → finish avec détection intelligente des transitions."
---

# Workflow - Orchestration automatique

## Overview

Orchestre automatiquement le cycle complet de développement en enchaînant les skills appropriés. Détecte les transitions naturelles et propose la prochaine étape.

**Principe :** Guider l'utilisateur à travers le workflow complet, du brainstorming à la MR, sans qu'il ait à connaître chaque skill.

**Annonce au démarrage :** "J'utilise le skill workflow pour orchestrer le développement."

## Routage

Analyser la requête utilisateur pour déterminer le mode :

- `/workflow "description"` → Mode guidé (cycle complet avec checkpoints)
- `/workflow --from <phase> --to <phase>` → Mode partiel (phases spécifiques)
- `/workflow --autopilot "description"` → Mode autopilot (minimal interaction, tâches simples)
- `/workflow --status` → Afficher l'état du workflow en cours
- `/workflow --resume` → Reprendre un workflow interrompu

## Phases du workflow

```
┌─────────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────────┐
│ brainstorm  │────▶│  plan   │────▶│ execute-plan│────▶│ code-review │────▶│ finish-branch │
└─────────────┘     └─────────┘     └─────────────┘     └─────────────┘     └───────────────┘
      │                  │                  │                  │
      │ --sdd            │ --prd            │ --subagent       │
      ▼                  ▼                  │ --loop           │
┌─────────────┐     ┌─────────┐            ▼                  │
│ sdd/specify │     │ PRD.json│     ┌─────────────┐           │
│ sdd/plan    │     └─────────┘     │ Ralph Loop  │           │
│ sdd/tasks   │                     └─────────────┘           │
│ sdd/impl    │                                               │
└─────────────┘                                               │
                                                              ▼
                                                        ┌───────────┐
                                                        │ notify-cr │
                                                        └───────────┘
```

## Mapping des phases vers les skills

| Phase | Skill invoqué | Condition de sortie |
|-------|---------------|---------------------|
| `brainstorm` | `/brainstorm` | Design document sauvegardé |
| `plan` | `/plan` | Plan markdown ou PRD généré |
| `execute-plan` | `/execute-plan` | Toutes les tâches complétées |
| `code-review` | `/code-review` | Review terminée, issues traitées |
| `finish-branch` | `/finish-branch` | MR créée |

---

# Mode guidé (par défaut)

## Phase 0 : Initialisation

1. **Créer le fichier de suivi** `.claude/workflow-state.json` :

```json
{
  "id": "workflow-<timestamp>",
  "description": "<description utilisateur>",
  "started_at": "<ISO timestamp>",
  "current_phase": "brainstorm",
  "completed_phases": [],
  "context": {
    "design_doc": null,
    "plan_file": null,
    "jira_id": null,
    "branch": null,
    "mr_url": null
  },
  "mode": "guided",
  "checkpoints": ["plan", "code-review"]
}
```

2. **Afficher le résumé** :

```
Workflow démarré
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Description : <description>
Mode : Guidé (checkpoints après plan et review)

Phases :
  ○ brainstorm
  ○ plan
  ○ execute-plan
  ○ code-review
  ○ finish-branch

Démarrer le brainstorming ? [O/n]
```

## Phase 1 : Brainstorming

1. **Invoquer** `/brainstorm` avec la description
2. **Attendre** la complétion (design document sauvegardé)
3. **Mettre à jour l'état** :
   - `context.design_doc` = chemin du design
   - `context.jira_id` = ID extrait si mode Jira
   - `completed_phases.push("brainstorm")`
   - `current_phase = "plan"`

4. **Proposer la transition** :

```
✓ Brainstorming terminé
  Design : docs/plans/2026-02-01-feature-design.md

Prochaine phase : Plan d'implémentation

Options :
1. Continuer vers /plan (recommandé)
2. Continuer vers /plan --prd (Ralph Loop)
3. Activer SDD complet (/sdd/specify)
4. Arrêter ici (reprendre plus tard avec /workflow --resume)
```

## Phase 2 : Planning

1. **Invoquer** `/plan` (ou `/plan --prd` si choisi)
2. **Attendre** la complétion
3. **Mettre à jour l'état** :
   - `context.plan_file` = chemin du plan
   - `completed_phases.push("plan")`
   - `current_phase = "execute-plan"`

4. **CHECKPOINT - Validation utilisateur** :

```
✓ Plan créé
  Fichier : docs/plans/2026-02-01-feature-plan.md
  Tâches : 5

━━━ CHECKPOINT ━━━

Relisez le plan avant de continuer. Questions :
- Le scope est-il correct ?
- Les tâches sont-elles bien découpées ?
- Manque-t-il quelque chose ?

Options :
1. Approuver et continuer vers l'exécution
2. Modifier le plan (je révise et on reprend)
3. Arrêter ici
```

## Phase 3 : Exécution

1. **Vérifier si worktree nécessaire** :
   - Si pas sur une branche feature → Proposer `/setup-worktree`
   - Si sur une branche feature → Continuer

2. **Demander le mode d'exécution** :

```
Mode d'exécution :
1. Standard (batches de 3, checkpoints) - recommandé
2. Subagent (agent frais par tâche + review)
3. Ralph Loop (autonome, si PRD disponible)
```

3. **Invoquer** `/execute-plan` avec le mode choisi
4. **Attendre** la complétion
5. **Mettre à jour l'état** :
   - `context.branch` = branche courante
   - `completed_phases.push("execute-plan")`
   - `current_phase = "code-review"`

6. **Proposer la transition** :

```
✓ Exécution terminée
  Tâches : 5/5 complétées
  Commits : 8

Prochaine phase : Code review

Lancer le code review ? [O/n]
```

## Phase 4 : Code Review

1. **Invoquer** `/code-review`
2. **Attendre** la complétion
3. **Mettre à jour l'état** :
   - `completed_phases.push("code-review")`
   - `current_phase = "finish-branch"`

4. **CHECKPOINT - Validation du review** :

```
✓ Code review terminé

━━━ CHECKPOINT ━━━

Résumé :
- Critical : 0
- Important : 2
- Minor : 5

Les issues Important ont été corrigées.

Options :
1. Approuver et créer la MR
2. Revoir les issues restantes
3. Arrêter ici
```

## Phase 5 : Finalisation

1. **Invoquer** `/finish-branch`
2. **Attendre** la complétion (MR créée)
3. **Mettre à jour l'état** :
   - `context.mr_url` = URL de la MR
   - `completed_phases.push("finish-branch")`
   - `current_phase = "completed"`

4. **Afficher le résumé final** :

```
✓ Workflow terminé
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Description : <description>
Durée : <durée>

Artifacts :
  - Design : docs/plans/2026-02-01-feature-design.md
  - Plan : docs/plans/2026-02-01-feature-plan.md
  - MR : https://gitlab.com/...

Prochaines étapes suggérées :
  - Attendre le pipeline
  - /notify-cr pour demander une review
  - /check-pipeline pour suivre le CI
```

5. **Nettoyer** : Supprimer `.claude/workflow-state.json`

---

# Mode partiel (--from / --to)

## Usage

```bash
/workflow --from plan --to code-review
/workflow --from execute-plan --to finish-branch
```

## Comportement

1. **Valider les phases** :
   - `--from` doit être avant `--to` dans la séquence
   - Phases valides : `brainstorm`, `plan`, `execute-plan`, `code-review`, `finish-branch`

2. **Vérifier les prérequis** :
   - Si `--from plan` : Vérifier qu'un design existe
   - Si `--from execute-plan` : Vérifier qu'un plan existe
   - Si `--from code-review` : Vérifier qu'on est sur une branche avec des commits
   - Si `--from finish-branch` : Vérifier qu'on est sur une branche feature

3. **Exécuter** les phases de `--from` à `--to` (inclus)

4. **Checkpoints** : Mêmes checkpoints que le mode guidé

---

# Mode autopilot

## Usage

```bash
/workflow --autopilot "fix typo in README"
/workflow --autopilot "add console.log to debug"
```

## Conditions d'activation

Le mode autopilot est autorisé **uniquement** si :
- Score de complexité < seuil configuré (défaut: 3)
- Pas d'ID Jira détecté (tâche ad-hoc)
- Description courte (<100 caractères)

Si ces conditions ne sont pas remplies :
```
Cette tâche semble trop complexe pour le mode autopilot.
Score de complexité : 5/10

Basculer vers le mode guidé ? [O/n]
```

## Comportement autopilot

1. **Analyse rapide** de la description
2. **Créer une branche** si nécessaire : `fix/adhoc-<timestamp>`
3. **Exécuter directement** sans brainstorming ni plan formel
4. **Commiter** les changements
5. **Proposer** : "Créer une MR ou garder local ?"

**Pas de checkpoints** - exécution fluide.

---

# Mode status

## Usage

```bash
/workflow --status
```

## Comportement

1. **Lire** `.claude/workflow-state.json`
2. **Afficher** l'état :

```
Workflow en cours
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID : workflow-1706745600
Description : Implémenter l'authentification OAuth
Démarré : 2026-02-01 10:00
Mode : Guidé

Progression :
  ✓ brainstorm (docs/plans/2026-02-01-oauth-design.md)
  ✓ plan (docs/plans/2026-02-01-oauth-plan.md)
  ● execute-plan (3/5 tâches)
  ○ code-review
  ○ finish-branch

Contexte :
  - Jira : OBAT-123
  - Branche : feat/OBAT-123-oauth

Reprendre avec /workflow --resume
```

Si aucun workflow en cours :
```
Aucun workflow en cours.

Démarrer avec : /workflow "description"
```

---

# Mode resume

## Usage

```bash
/workflow --resume
```

## Comportement

1. **Lire** `.claude/workflow-state.json`
2. **Vérifier** la cohérence (branche, fichiers)
3. **Reprendre** à `current_phase`

```
Reprise du workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Description : Implémenter l'authentification OAuth
Phase actuelle : execute-plan

Reprendre l'exécution ? [O/n]
```

---

# Configuration

Lire depuis `config/plugin-config.yaml` :

```yaml
workflow:
  # Phases par défaut
  default-flow:
    - brainstorm
    - plan
    - execute-plan
    - code-review
    - finish-branch

  # Phases nécessitant validation utilisateur
  checkpoints:
    - plan
    - code-review

  # Seuil de complexité pour mode autopilot
  autopilot-threshold: 3

  # Mode d'exécution par défaut (standard, subagent)
  default-execution-mode: standard

  # Proposer worktree automatiquement
  auto-suggest-worktree: true
```

---

# Gestion des erreurs

## Erreur dans une phase

Si un skill échoue (ex: tests qui ne passent pas) :

```
✗ Phase execute-plan échouée

Erreur : Tests PHPUnit en échec (3 erreurs)

Options :
1. Corriger et réessayer cette phase
2. Revenir à la phase précédente (plan)
3. Arrêter le workflow (reprendre avec --resume)
```

L'état est préservé - l'utilisateur peut reprendre.

## Interruption utilisateur

Si l'utilisateur quitte (Ctrl+C, ferme le terminal) :

- L'état est sauvegardé dans `.claude/workflow-state.json`
- Message au prochain démarrage :
  ```
  Un workflow interrompu a été détecté.
  Reprendre avec /workflow --resume
  ```

## Incohérence détectée

Si l'état ne correspond plus à la réalité (branche supprimée, fichiers manquants) :

```
Incohérence détectée dans le workflow

Problèmes :
- Le fichier de plan n'existe plus
- La branche feat/OBAT-123 n'existe plus

Options :
1. Réinitialiser et recommencer
2. Ignorer et forcer la reprise (risqué)
```

---

# Intégration avec les autres skills

## Skills invoqués

| Skill | Invoqué quand | Paramètres passés |
|-------|---------------|-------------------|
| `/brainstorm` | Phase brainstorm | Description, `--jira` si ID détecté |
| `/plan` | Phase plan | Chemin du design doc |
| `/setup-worktree` | Avant execute si pas de branche | Type, ID Jira |
| `/execute-plan` | Phase execute | Mode (standard/subagent/loop) |
| `/code-review` | Phase review | - |
| `/finish-branch` | Phase finish | - |

## Détection automatique

Le workflow détecte automatiquement :
- **ID Jira** dans la description → Active mode Jira pour brainstorm
- **Complexité élevée** → Suggère SDD
- **PRD existant** → Propose Ralph Loop pour execute
- **Pas de branche feature** → Suggère worktree

---

# Exemples d'utilisation

## Cycle complet simple

```bash
/workflow "ajouter un bouton de déconnexion"

# → brainstorm (design en 5 min)
# → plan (5 tâches)
# → CHECKPOINT : validation du plan
# → execute-plan standard
# → code-review
# → CHECKPOINT : validation review
# → finish-branch
# → MR créée !
```

## Avec contexte Jira

```bash
/workflow "OBAT-123 implémenter OAuth"

# Détecte OBAT-123 → active mode Jira
# → brainstorm --jira OBAT-123
# → plan
# → ...
```

## Reprise après interruption

```bash
# Session 1
/workflow "gros refactoring"
# → brainstorm OK
# → plan OK
# (utilisateur ferme le terminal)

# Session 2
/workflow --status
# Affiche : execute-plan en cours

/workflow --resume
# Reprend à execute-plan
```

## Mode autopilot pour tâche simple

```bash
/workflow --autopilot "fix typo dans README"

# Pas de brainstorm
# Pas de plan
# → Correction directe
# → Commit
# → "Créer une MR ?" [o/N]
```

---

# Red Flags

**Ne jamais :**
- Sauter les checkpoints configurés
- Continuer après une erreur critique sans validation
- Perdre l'état du workflow (toujours sauvegarder)
- Forcer le mode autopilot sur une tâche complexe

**Si bloqué :** Sauvegarder l'état et demander à l'utilisateur.
