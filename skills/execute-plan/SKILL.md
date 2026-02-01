---
name: execute-plan
description: "Exécution de plans d'implémentation. Mode standard (batches), --subagent (agent frais par tâche + code review), --loop (Ralph Loop)."
---

# Exécution de plans d'implémentation

## Routage

Analyser la requête utilisateur pour déterminer le mode :

- `/execute-plan` ou `/execute-plan <fichier>` → Mode standard (exécution par batches)
- `/execute-plan --subagent [fichier]` → Mode subagent (agent frais par tâche + code review)
- `/execute-plan --loop [TICKET-ID]` → Mode Ralph Loop (prd.json)
- `/execute-plan --worktree` → Combinable avec standard ou subagent (pas avec --loop)

**Flags mutuellement exclusifs :** `--subagent` et `--loop` ne peuvent pas être combinés.

**Exemples :**
```bash
/execute-plan                           # Standard : batches de 3 tâches
/execute-plan --subagent                # Subagent : 1 agent/tâche + review
/execute-plan --subagent --worktree     # Subagent dans un worktree isolé
/execute-plan --loop OBAT-123           # Ralph Loop autonome
```

---

# Flag --worktree : Création d'un worktree isolé

Si le flag `--worktree` est présent, **avant** d'exécuter le plan :

1. Invoquer le skill `/setup-worktree`
2. Demander l'ID Jira et le type de branche
3. Créer le worktree avec le format Obat : `type/PROJET-ID[-description]`
4. Installer les dépendances et vérifier les tests
5. Continuer avec l'exécution du plan dans ce worktree

**Combinaisons valides :**
```bash
/execute-plan --worktree                    # Standard + worktree
/execute-plan --worktree mon-plan.md        # Standard + worktree + fichier spécifique
/execute-plan --subagent --worktree         # Subagent + worktree
```

**Note :** `--worktree` n'est pas compatible avec `--loop` (Ralph Loop gère son propre contexte).

**Convention de nommage branche/worktree :**
```
feat/DEL-123[-description]
tech/DEL-456[-description]
fix/DEL-789[-description]
hotfix/OBAT-101[-description]
```

---

# Mode Standard : Exécution de plans markdown

## Overview

Charger un plan, le revoir de manière critique, exécuter les tâches par batches, faire un rapport entre chaque batch pour revue.

**Principe clé :** Exécution par batches avec checkpoints pour revue.

**Annoncer au début :** "J'exécute le plan d'implémentation."

## Le processus

### Étape 1 : Charger et revoir le plan

1. Si un fichier est spécifié : le charger
2. Sinon : trouver le plan le plus récent dans `docs/plans/*.md` (exclure les `-design.md`)
3. Si aucun trouvé :
   > "Aucun plan trouvé. Utilisez `/plan` pour en créer un."

4. Revoir le plan de manière critique - identifier les questions ou préoccupations
5. Si préoccupations : Les soulever avec l'utilisateur avant de commencer
6. Si pas de préoccupations : Créer les TodoWrite et procéder

### Étape 2 : Exécuter un batch

**Par défaut : les 3 premières tâches**

Pour chaque tâche :
1. La marquer comme in_progress
2. Suivre chaque étape exactement (le plan a des étapes de petite taille)
3. Exécuter les vérifications comme spécifié
4. La marquer comme completed

### Étape 3 : Rapport

Quand le batch est terminé :
- Montrer ce qui a été implémenté
- Montrer la sortie des vérifications
- Dire : "Prêt pour les retours."

### Étape 4 : Continuer

Selon les retours :
- Appliquer les changements si nécessaire
- Exécuter le batch suivant
- Répéter jusqu'à complétion

### Étape 5 : Terminer le développement

Après que toutes les tâches sont terminées et vérifiées :
- Annoncer : "Toutes les tâches du plan sont terminées."
- Proposer de commiter les changements (voir "Convention de commits" ci-dessous)
- Résumer ce qui a été implémenté
- Proposer d'utiliser `/finish-branch` pour créer la MR

## Quand s'arrêter et demander de l'aide

**S'ARRÊTER immédiatement quand :**
- Un bloqueur apparaît en milieu de batch (dépendance manquante, test échoue, instruction peu claire)
- Le plan a des lacunes critiques empêchant de commencer
- Une instruction n'est pas comprise
- Une vérification échoue de manière répétée

**Demander des clarifications plutôt que deviner.**

## Quand revisiter les étapes précédentes

**Retourner à la revue (Étape 1) quand :**
- L'utilisateur met à jour le plan suite aux retours
- L'approche fondamentale nécessite une révision

**Ne pas forcer à travers les bloqueurs** - s'arrêter et demander.

## Règles

- Revoir le plan de manière critique d'abord
- Suivre les étapes du plan exactement
- Ne pas sauter les vérifications
- Entre les batches : juste rapporter et attendre
- S'arrêter quand bloqué, ne pas deviner

## Convention de commits Obat

**Format obligatoire :**
```
^(fixup! )?(?:tech|feat|doc|fix|hotfix|chore):\s#(?:[A-Z]+-)?\d+\s.*
```

**Types autorisés :** `tech`, `feat`, `doc`, `fix`, `hotfix`, `chore`

**Exemples valides :**
```
feat: #DEL-123 Add user authentication
fix: #OBAT-456 Fix login redirect bug
tech: #DEL-789 Refactor database connection pool
doc: #DEL-123 Update API documentation
chore: #DEL-456 Update dependencies
fixup! feat: #DEL-123 Add user authentication
```

**Extraire l'ID Jira depuis la branche :**
```
feat/DEL-123-description → DEL-123
```

**Si l'ID n'est pas dans la branche :** Demander à l'utilisateur.

---

# Mode Subagent : Exécution avec agents frais

## Overview

Exécute un plan en dispatchant un **subagent frais par tâche**, avec **code review automatique** après chaque tâche. Élimine la pollution de contexte sur les plans longs.

**Principe clé :** Agent frais par tâche + review entre les tâches = haute qualité, itération rapide.

**Annoncer au début :** "J'exécute le plan en mode subagent (un agent par tâche + code review)."

## Quand utiliser ce mode

- Plans avec 5+ tâches (évite l'accumulation de contexte)
- Tâches complexes nécessitant un focus isolé
- Besoin de review systématique entre les tâches

## Phase 1 : Chargement et validation

1. Charger le plan markdown (même logique que mode standard)
2. Créer TodoWrite avec toutes les tâches
3. Sauvegarder le SHA git actuel (`base_sha_initial`)
4. Afficher le résumé :

```
Mode Subagent activé
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Plan : docs/plans/2026-01-30-feature.md
Tâches : 7
Mode : 1 subagent/tâche + code review

Lancer l'exécution ? [o/N]
```

## Phase 2 : Boucle d'exécution

Pour chaque tâche du plan :

### 2.1 Préparer

```
1. Marquer la tâche comme in_progress dans TodoWrite
2. Sauvegarder le SHA git actuel (base_sha)
```

### 2.2 Dispatcher le subagent d'implémentation

```
Task tool (general-purpose):
  description: "Implémenter Tâche N: [nom court]"
  prompt: |
    Tu implémentes la Tâche N du plan [chemin/vers/plan.md].

    Instructions :
    1. Lis la tâche dans le plan (section "Tâche N")
    2. Suis chaque étape exactement (TDD : test → implémentation → vérification)
    3. Commite ton travail après chaque étape logique
    4. Rapporte : ce que tu as fait, fichiers modifiés, résultat des tests

    Répertoire de travail : [directory]

    Convention commits Obat :
    Format : type: #PROJET-XXX description
    Types autorisés : tech, feat, doc, fix, hotfix, chore

    IMPORTANT : Ne modifie QUE ce qui est spécifié dans la tâche.
```

Attendre le rapport du subagent.

### 2.3 Dispatcher le subagent code-reviewer

```
Task tool (superpowers:code-reviewer):
  description: "Review Tâche N"
  prompt: |
    Review les changements de la Tâche N.

    Commits à reviewer : de [base_sha] à HEAD
    Plan de référence : [chemin/vers/plan.md], section "Tâche N"

    Vérifie :
    - [ ] La tâche est implémentée selon le plan
    - [ ] Tests présents et passants
    - [ ] Pas de code mort, console.log, ou debug oublié
    - [ ] Conventions Obat respectées (commits, nommage)
    - [ ] Pas de régressions introduites

    Retourne :
    - Strengths : Points positifs
    - Issues : Liste avec sévérité (Critical/Important/Minor)
    - Assessment : "Ready" ou "Needs Work"
```

### 2.4 Traiter le résultat du code review

**Si Assessment = "Ready" :**
```
→ Marquer la tâche comme completed
→ Passer à la tâche suivante
```

**Si Assessment = "Needs Work" avec issues Critical :**
```
→ Dispatcher un subagent de fix (voir 2.5)
→ Re-run le code-reviewer
→ Si toujours "Needs Work" après 1 retry : STOPPER et rapporter
```

**Si Assessment = "Needs Work" avec seulement Important/Minor :**
```
→ Dispatcher un subagent de fix
→ Marquer comme completed (pas de re-review pour issues mineures)
→ Passer à la tâche suivante
```

### 2.5 Dispatcher le subagent de fix (si nécessaire)

```
Task tool (general-purpose):
  description: "Fix issues Tâche N"
  prompt: |
    Corrige les problèmes identifiés par le code review pour la Tâche N.

    Issues à corriger :
    [Liste des issues du code-reviewer]

    Instructions :
    1. Corrige chaque issue listée
    2. Commite tes corrections (format: fixup! type: #ID description)
    3. Rapporte ce que tu as corrigé

    IMPORTANT : Ne corrige QUE les issues listées, rien d'autre.
```

## Phase 3 : Finalisation

Après toutes les tâches complétées :

1. Afficher le résumé :
```
Exécution terminée
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tâches : 7/7 complétées
Commits : 12
Reviews : 7 (tous "Ready")

Prochaine étape : /finish-branch
```

2. Proposer d'utiliser `/finish-branch` pour créer la MR

## Gestion des erreurs

### Échec d'un subagent d'implémentation

Si le subagent rapporte un échec (tests qui ne passent pas, erreur bloquante) :

```
1. Dispatcher un nouveau subagent avec le contexte d'erreur :
   "La tentative précédente a échoué avec : [erreur]. Analyse et corrige."

2. Si échec après ce retry :
   → STOPPER l'exécution
   → Afficher : "Tâche N bloquée après 1 retry. Erreur : [détails]"
   → Attendre l'intervention utilisateur
```

### Échec persistant au code review

Si une tâche reste "Needs Work" après le fix :

```
→ STOPPER l'exécution
→ Afficher les issues non résolues
→ Attendre l'intervention utilisateur
```

## Red Flags

**Ne jamais :**
- Sauter le code review entre les tâches
- Continuer avec des issues Critical non corrigées
- Essayer de corriger manuellement (pollution de contexte)
- Dispatcher plusieurs subagents d'implémentation en parallèle (conflits git)

**Si bloqué :** Stopper et demander, ne pas deviner.

---

# Mode Ralph Loop : Exécution avec prd.json

## Overview

Lance une boucle Ralph Loop autonome. Détecte automatiquement le fichier prd.json et applique les paramètres par défaut de la config équipe.

## Usage

```
/execute-plan --loop              # Détecte le dernier prd.json
/execute-plan --loop OBAT-123     # Utilise docs/plans/OBAT-123-prd.json
```

## Phase 1 : Détection du PRD

1. Si un ID est fourni : chercher `docs/plans/<ID>-prd.json`
2. Sinon : trouver le prd.json le plus récent dans `docs/plans/`
3. Si aucun trouvé :
   > "Aucun prd.json trouvé. Utilisez `/plan --prd OBAT-123` pour en générer un, ou `/brainstorm --jira OBAT-123` pour démarrer un brainstorming."

## Phase 2 : Lecture de la config

Lire les paramètres depuis `config/plugin-config.yaml` :
- `ralph.max_iterations` (défaut: 20)
- `ralph.completion_promise` (défaut: "ALL_STORIES_PASS")

## Phase 3 : Affichage du résumé

Avant de lancer, afficher :

```
Ralph Loop : OBAT-123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRD : docs/plans/OBAT-123-prd.json
Stories : 5 (0 complétées)
Max iterations : 20
Completion promise : ALL_STORIES_PASS

Lancer la boucle ? [o/N]
```

## Phase 4 : Lancement

Si l'utilisateur confirme, invoquer le skill `ralph-loop:ralph-loop` avec :

```
Implémenter les user stories définies dans docs/plans/OBAT-123-prd.json

Règles :
1. Lire le prd.json pour identifier la prochaine story (passes: false, priorité la plus basse)
2. Implémenter la story
3. Vérifier les critères d'acceptation (tests, typecheck, lint)
4. Si OK : mettre passes: true, commiter (format: `type: #ID description`), logger dans progress.txt
5. Si TOUTES les stories ont passes: true : output <promise>ALL_STORIES_PASS</promise>

Format commit obligatoire : `type: #PROJET-XXX description`
Types : tech, feat, doc, fix, hotfix, chore

--max-iterations 20 --completion-promise "ALL_STORIES_PASS"
```

## Arrêt

Rappeler à l'utilisateur :
> "Pour arrêter la boucle : `/cancel-ralph`"
