---
name: subagent-driven-development
description: "Utiliser pour exécuter des plans d'implémentation avec des tâches indépendantes dans la session courante ou face à 3+ problèmes indépendants qui peuvent être investigués sans état partagé ou dépendances - dispatch un subagent frais pour chaque tâche avec code review entre les tâches, permettant une itération rapide avec des points de contrôle qualité"
---

# Développement piloté par Subagents

Créer et exécuter un plan en dispatchant un subagent frais par tâche ou problème, avec review du code et des résultats après chaque tâche ou batch de tâches.

**Principe fondamental :** Subagent frais par tâche + review entre ou après les tâches = haute qualité, itération rapide.

Exécuter des plans via des agents :

- Même session (pas de changement de contexte)
- Subagent frais par tâche (pas de pollution de contexte)
- Code review après chaque tâche ou batch (détecter les problèmes tôt)
- Itération plus rapide (pas d'humain dans la boucle entre les tâches)

## Types d'exécution supportés

### Exécution séquentielle

Quand les tâches ou problèmes sont liés entre eux et doivent être exécutés dans l'ordre, les investiguer ou modifier séquentiellement est la meilleure approche.

Dispatcher un agent par tâche ou problème. Le laisser travailler séquentiellement. Revoir le résultat et le code après chaque tâche ou problème.

**Quand utiliser :**

- Les tâches sont étroitement couplées
- Les tâches doivent être exécutées dans l'ordre

### Exécution parallèle

Quand il y a plusieurs tâches ou problèmes non liés (fichiers différents, sous-systèmes différents, bugs différents), les investiguer ou modifier séquentiellement fait perdre du temps. Chaque tâche ou investigation est indépendante et peut se faire en parallèle.

Dispatcher un agent par domaine de problème indépendant. Les laisser travailler en parallèle.

**Quand utiliser :**

- Les tâches sont principalement indépendantes
- La review globale peut être faite après que toutes les tâches sont complétées

## Processus d'exécution séquentielle

### 1. Charger le plan

Lire le fichier de plan, créer TodoWrite avec toutes les tâches.

### 2. Exécuter la tâche avec un Subagent

Pour chaque tâche :

**Dispatcher un subagent frais :**

```
Task tool (general-purpose):
  description: "Implémenter Tâche N: [nom de la tâche]"
  prompt: |
    Tu implémentes la Tâche N de [fichier-plan].

    Lis cette tâche attentivement. Ton travail est de :
    1. Implémenter exactement ce que la tâche spécifie
    2. Écrire les tests (suivant TDD si la tâche le dit)
    3. Vérifier que l'implémentation fonctionne
    4. Commiter ton travail
    5. Faire un rapport

    Travailler depuis : [répertoire]

    Rapport : Ce que tu as implémenté, ce que tu as testé, résultats des tests, fichiers modifiés, tout problème
```

**Le subagent fait un rapport** avec un résumé du travail.

### 3. Revoir le travail du Subagent

**Dispatcher un subagent code-reviewer :**

```
Task tool (superpowers:code-reviewer):
  Utiliser le template à requesting-code-review/code-reviewer.md

  CE_QUI_A_ÉTÉ_IMPLÉMENTÉ: [du rapport du subagent]
  PLAN_OU_EXIGENCES: Tâche N de [fichier-plan]
  BASE_SHA: [commit avant la tâche]
  HEAD_SHA: [commit actuel]
  DESCRIPTION: [résumé de la tâche]
```

**Le code reviewer retourne :** Points forts, Problèmes (Critique/Important/Mineur), Évaluation

### 4. Appliquer les retours de la Review

**Si des problèmes sont trouvés :**

- Corriger les problèmes Critiques immédiatement
- Corriger les problèmes Importants avant la prochaine tâche
- Noter les problèmes Mineurs

**Dispatcher un subagent de suivi si nécessaire :**

```
"Corriger les problèmes du code review : [liste des problèmes]"
```

### 5. Marquer comme complété, Tâche suivante

- Marquer la tâche comme complétée dans TodoWrite
- Passer à la tâche suivante
- Répéter les étapes 2-5

### 6. Review finale

Après que toutes les tâches sont complétées, dispatcher un code-reviewer final :

- Revoir l'implémentation entière
- Vérifier que toutes les exigences du plan sont satisfaites
- Valider l'architecture globale

### 7. Terminer le développement

Après que la review finale passe :

- Annoncer : "J'utilise le skill finishing-a-development-branch pour terminer ce travail."
- **SOUS-SKILL REQUIS :** Utiliser superpowers:finishing-a-development-branch
- Suivre ce skill pour vérifier les tests, présenter les options, exécuter le choix

### Exemple de Workflow

```
Toi : J'utilise le Développement piloté par Subagents pour exécuter ce plan.

[Charger le plan, créer TodoWrite]

Tâche 1 : Script d'installation du hook

[Dispatcher le subagent d'implémentation]
Subagent : Implémenté install-hook avec tests, 5/5 passent

[Récupérer les SHAs git, dispatcher le code-reviewer]
Reviewer : Points forts : Bonne couverture de tests. Problèmes : Aucun. Prêt.

[Marquer Tâche 1 comme complétée]

Tâche 2 : Modes de récupération

[Dispatcher le subagent d'implémentation]
Subagent : Ajouté verify/repair, 8/8 tests passent

[Dispatcher le code-reviewer]
Reviewer : Points forts : Solide. Problèmes (Important) : Manque le reporting de progression

[Dispatcher le subagent de fix]
Subagent fix : Ajouté progression toutes les 100 conversations

[Vérifier le fix, marquer Tâche 2 comme complétée]

...

[Après toutes les tâches]
[Dispatcher le code-reviewer final]
Reviewer final : Toutes les exigences satisfaites, prêt à merger

Terminé !
```

### Red Flags

**Jamais :**

- Sauter le code review entre les tâches
- Continuer avec des problèmes Critiques non corrigés
- Dispatcher plusieurs subagents d'implémentation en parallèle (conflits)
- Implémenter sans lire la tâche du plan

**Si un subagent échoue sur une tâche :**

- Dispatcher un subagent de fix avec des instructions spécifiques
- Ne pas essayer de corriger manuellement (pollution de contexte)

## Processus d'exécution parallèle

Charger le plan, le revoir de manière critique, exécuter les tâches par batches, faire un rapport pour review entre les batches.

**Principe fondamental :** Exécution par batch avec checkpoints pour review par l'architecte.

**Annoncer au début :** "J'utilise le skill executing-plans pour implémenter ce plan."

### Étape 1 : Charger et revoir le Plan

1. Lire le fichier de plan
2. Revoir de manière critique - identifier les questions ou préoccupations sur le plan
3. Si préoccupations : Les soulever avec votre partenaire humain avant de commencer
4. Si pas de préoccupations : Créer TodoWrite et procéder

### Étape 2 : Exécuter le Batch

**Par défaut : Les 3 premières tâches**

Pour chaque tâche :

1. Marquer comme in_progress
2. Suivre chaque étape exactement (le plan a des étapes de petite taille)
3. Exécuter les vérifications comme spécifié
4. Marquer comme completed

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

Après que toutes les tâches sont complétées et vérifiées :

- Annoncer : "J'utilise le skill finishing-a-development-branch pour terminer ce travail."
- **SOUS-SKILL REQUIS :** Utiliser superpowers:finishing-a-development-branch
- Suivre ce skill pour vérifier les tests, présenter les options, exécuter le choix

### Quand s'arrêter et demander de l'aide

**S'ARRÊTER immédiatement quand :**

- Un bloqueur apparaît en milieu de batch (dépendance manquante, test échoue, instruction pas claire)
- Le plan a des lacunes critiques empêchant de commencer
- Une instruction n'est pas comprise
- Une vérification échoue de manière répétée

**Demander des clarifications plutôt que deviner.**

### Quand revisiter les étapes précédentes

**Retourner à la Review (Étape 1) quand :**

- Le partenaire met à jour le plan suite aux retours
- L'approche fondamentale nécessite une révision

**Ne pas forcer à travers les bloqueurs** - s'arrêter et demander.

### À retenir

- Revoir le plan de manière critique d'abord
- Suivre les étapes du plan exactement
- Ne pas sauter les vérifications
- Référencer les skills quand le plan le dit
- Entre les batches : juste faire un rapport et attendre
- S'arrêter quand bloqué, ne pas deviner

## Processus d'investigation parallèle

Cas spécial d'exécution parallèle, quand il y a plusieurs échecs non liés qui peuvent être investigués sans état partagé ou dépendances.

### 1. Identifier les domaines indépendants

Grouper les échecs par ce qui est cassé :

- Tests fichier A : Flux d'approbation d'outil
- Tests fichier B : Comportement de complétion de batch
- Tests fichier C : Fonctionnalité d'abandon

Chaque domaine est indépendant - corriger l'approbation d'outil n'affecte pas les tests d'abandon.

### 2. Créer des tâches d'Agent focalisées

Chaque agent reçoit :

- **Périmètre spécifique :** Un fichier de test ou sous-système
- **Objectif clair :** Faire passer ces tests
- **Contraintes :** Ne pas changer d'autre code
- **Sortie attendue :** Résumé de ce qui a été trouvé et corrigé

### 3. Dispatcher en parallèle

```typescript
// Dans l'environnement Claude Code / AI
Task("Corriger les échecs de agent-tool-abort.test.ts")
Task("Corriger les échecs de batch-completion-behavior.test.ts")
Task("Corriger les échecs de tool-approval-race-conditions.test.ts")
// Les trois s'exécutent en parallèle
```

### 4. Revoir et intégrer

Quand les agents retournent :

- Lire chaque résumé
- Vérifier que les fixes ne sont pas en conflit
- Exécuter la suite de tests complète
- Intégrer tous les changements

### Structure de prompt d'Agent

Les bons prompts d'agent sont :

1. **Focalisés** - Un domaine de problème clair
2. **Autonomes** - Tout le contexte nécessaire pour comprendre le problème
3. **Spécifiques sur la sortie** - Que devrait retourner l'agent ?

```markdown
Corriger les 3 tests qui échouent dans src/agents/agent-tool-abort.test.ts :

1. "should abort tool with partial output capture" - attend 'interrupted at' dans le message
2. "should handle mixed completed and aborted tools" - outil rapide abandonné au lieu de complété
3. "should properly track pendingToolCount" - attend 3 résultats mais obtient 0

Ce sont des problèmes de timing/race condition. Ta tâche :

1. Lire le fichier de test et comprendre ce que chaque test vérifie
2. Identifier la cause racine - problèmes de timing ou vrais bugs ?
3. Corriger en :
   - Remplaçant les timeouts arbitraires par de l'attente basée sur les événements
   - Corrigeant les bugs dans l'implémentation d'abandon si trouvés
   - Ajustant les attentes des tests si le comportement testé a changé

NE PAS juste augmenter les timeouts - trouver le vrai problème.

Retour : Résumé de ce que tu as trouvé et ce que tu as corrigé.
```

### Erreurs courantes

**❌ Trop large :** "Corriger tous les tests" - l'agent se perd
**✅ Spécifique :** "Corriger agent-tool-abort.test.ts" - périmètre focalisé

**❌ Pas de contexte :** "Corriger la race condition" - l'agent ne sait pas où
**✅ Contexte :** Coller les messages d'erreur et noms des tests

**❌ Pas de contraintes :** L'agent pourrait tout refactorer
**✅ Contraintes :** "NE PAS changer le code de production" ou "Corriger les tests seulement"

**❌ Sortie vague :** "Corrige-le" - on ne sait pas ce qui a changé
**✅ Spécifique :** "Retourner un résumé de la cause racine et des changements"

### Quand NE PAS utiliser

**Échecs liés :** Corriger l'un pourrait corriger les autres - investiguer ensemble d'abord
**Besoin du contexte complet :** Comprendre nécessite de voir le système entier
**Debug exploratoire :** On ne sait pas encore ce qui est cassé
**État partagé :** Les agents interféreraient (éditant les mêmes fichiers, utilisant les mêmes ressources)

### Exemple réel d'une session

**Scénario :** 6 échecs de tests sur 3 fichiers après un refactoring majeur

**Échecs :**

- agent-tool-abort.test.ts : 3 échecs (problèmes de timing)
- batch-completion-behavior.test.ts : 2 échecs (outils non exécutés)
- tool-approval-race-conditions.test.ts : 1 échec (compteur d'exécutions = 0)

**Décision :** Domaines indépendants - logique d'abandon séparée de la complétion de batch séparée des race conditions

**Dispatch :**

```
Agent 1 → Corriger agent-tool-abort.test.ts
Agent 2 → Corriger batch-completion-behavior.test.ts
Agent 3 → Corriger tool-approval-race-conditions.test.ts
```

**Résultats :**

- Agent 1 : Remplacé les timeouts par de l'attente basée sur les événements
- Agent 2 : Corrigé un bug de structure d'événement (threadId au mauvais endroit)
- Agent 3 : Ajouté attente pour la complétion de l'exécution d'outil async

**Intégration :** Tous les fixes indépendants, pas de conflits, suite complète verte

**Temps économisé :** 3 problèmes résolus en parallèle vs séquentiellement

### Vérification

Après le retour des agents :

1. **Revoir chaque résumé** - Comprendre ce qui a changé
2. **Vérifier les conflits** - Les agents ont-ils édité le même code ?
3. **Exécuter la suite complète** - Vérifier que tous les fixes fonctionnent ensemble
4. **Vérification ponctuelle** - Les agents peuvent faire des erreurs systématiques
