---
name: mr-feedback
description: Use when colleagues have left review comments on your GitLab Merge Request and you need to address their feedback systematically
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Task", "AskUserQuestion", "ToolSearch"]
argument-hint: "<mr-number> [--project <project-path>]"
---

# Traitement Interactif des Feedbacks de MR

## Overview

Workflow interactif pour traiter les retours de code review sur une MR GitLab : récupérer tous les feedbacks, les afficher par priorité, puis les traiter un par un avec analyse et choix d'action.

**Principe :** Voir tout d'abord, puis traiter granulairment avec contrôle total.

## Arguments

- `$ARGUMENTS` : Numéro de la MR (obligatoire)
- `--project` : Chemin du projet GitLab (optionnel, détecté via git remote)

---

## Phase 1 : Récupération et vue d'ensemble

### Étape 1.1 : Setup

1. Charger les outils GitLab :
   ```
   ToolSearch: "+gitlab merge_request"
   ToolSearch: "+gitlab discussions"
   ```

2. Identifier le projet :
   - Si `--project` fourni → utiliser
   - Sinon → `git remote get-url origin` et extraire le path

3. Identifier la branche de la MR et les commits concernés :
   ```bash
   git log --oneline origin/main..HEAD
   ```

### Étape 1.2 : Récupérer les feedbacks

1. `mcp__gitlab-enhanced__get_merge_request` → infos de la MR (titre, auteur, état)
2. `mcp__gitlab-enhanced__mr_discussions` → tous les threads de discussion
3. `mcp__gitlab-enhanced__get_merge_request_notes` → notes générales

### Étape 1.3 : Filtrer et enrichir

**Ignorer :**
- Commentaires système (CI/CD, bots)
- Threads déjà résolus
- Vos propres commentaires (sauf questions en attente)

**Pour chaque thread gardé, extraire :**
- `id` : ID du thread (pour résolution ultérieure)
- `author` : Qui a commenté
- `file` : Fichier concerné (si inline comment)
- `line` : Ligne(s) concernée(s)
- `content` : Texte du commentaire
- `has_suggestion` : Contient un bloc `suggestion` ?
- `replies` : Nombre de réponses dans le thread

### Étape 1.4 : Analyser et prioriser

Pour chaque feedback, déterminer :

**Priorité (basée sur le contenu) :**
| Priorité | Critères |
|----------|----------|
| 🔴 CRITICAL | Mots-clés : bug, crash, security, vulnerability, breaks, fails |
| 🟠 HIGH | Mots-clés : should, must, needs to, incorrect, wrong |
| 🟡 MEDIUM | Mots-clés : consider, might want, could be better |
| 🟢 LOW | Mots-clés : nit, minor, style, preference, optional |
| ⚪ QUESTION | Finit par `?` sans demande de changement |

**Pertinence (analyse rapide) :**
| Score | Signification |
|-------|---------------|
| ✅ PERTINENT | Le feedback pointe un vrai problème ou amélioration valide |
| ⚠️ À VÉRIFIER | Besoin de regarder le code pour confirmer |
| ❌ DISCUTABLE | Semble incorrect ou hors contexte |
| ❓ AMBIGU | Pas assez clair pour juger |

### Étape 1.5 : Afficher le tableau récapitulatif

```markdown
## 📋 Feedbacks MR !{number} - {title}

**Branche :** `{source_branch}` → `{target_branch}`
**Auteur MR :** @{author}
**Reviewers :** @{reviewer1}, @{reviewer2}
**Commits :** {n} commits depuis {base}

---

### Vue d'ensemble ({total} feedbacks non résolus)

| # | Pri | Pertinence | Reviewer | Fichier:Ligne | Résumé (30 chars) |
|---|-----|------------|----------|---------------|-------------------|
| 1 | 🔴 | ✅ | @alice | `api.ts:42` | NullPointer possible... |
| 2 | 🟠 | ⚠️ | @bob | `utils.ts:15-18` | Refacto suggéré... |
| 3 | 🟡 | ❌ | @alice | `config.ts:3` | Style preference... |
| 4 | ⚪ | ❓ | @bob | - | Pourquoi ce choix ?... |

---

### Répartition
- 🔴 Critical: {n}
- 🟠 High: {n}
- 🟡 Medium: {n}
- 🟢 Low: {n}
- ⚪ Questions: {n}

Prêt à traiter les feedbacks un par un ?
```

Attendre confirmation de l'utilisateur avant de passer à la Phase 2.

---

## Phase 2 : Traitement interactif (un par un)

### Boucle principale

Pour chaque feedback (dans l'ordre de priorité 🔴→🟠→🟡→🟢→⚪) :

#### Étape 2.1 : Afficher le détail

```markdown
## Feedback {current}/{total} - {priorité_emoji} {priorité}

**Thread ID :** {discussion_id}
**Reviewer :** @{author}
**Fichier :** `{file}:{line}` (ou "Commentaire général")

---

### 💬 Commentaire original

> {contenu complet du commentaire}

{Si suggestion de code présente :}
### 💡 Suggestion de code proposée
```diff
- {ancien code}
+ {nouveau code suggéré}
```

---

### 📊 Analyse

**Pertinence :** {pertinence_emoji} {pertinence}
**Raison :** {explication courte de l'analyse}

{Si le fichier existe, montrer le contexte :}
### 📄 Code actuel (contexte)
```{lang}
{5 lignes avant}
→ {ligne concernée}  // ← ICI
{5 lignes après}
```

{Si pertinence = DISCUTABLE ou AMBIGU :}
### ⚠️ Points d'attention
- {raison 1 pourquoi c'est discutable}
- {raison 2 si applicable}

---
```

#### Étape 2.2 : Demander l'action

```
AskUserQuestion avec options :
```

| Option | Description |
|--------|-------------|
| **Corriger + Fermer** | Implémenter le fix, commit fixup, répondre, résoudre le thread |
| **Appliquer suggestion** | Si suggestion présente : appliquer le diff suggéré directement |
| **Répondre seulement** | Écrire une réponse sans modifier le code |
| **Passer** | Ignorer ce feedback pour l'instant |
| **Marquer hors-scope** | Répondre que c'est hors-scope, proposer de créer une issue |
| **Demander clarification** | Poster une question au reviewer |

#### Étape 2.3 : Exécuter l'action choisie

**Si "Corriger + Fermer" :**

1. **Lire** le fichier concerné entièrement
2. **Comprendre** le contexte (fonction, tests liés)
3. **Implémenter** la correction avec `Edit`
4. **Vérifier** :
   ```bash
   # Syntax check selon le langage
   # Ex pour TypeScript :
   npx tsc --noEmit {file}
   ```
5. **Commit fixup** :
   ```bash
   # Trouver le commit qui a introduit cette ligne
   git log --oneline -1 --follow -p -- {file} | head -1
   # Ou si on ne trouve pas, utiliser le dernier commit de la branche
   git commit --fixup={commit_sha} -m "fix: {description courte}"
   ```
6. **Préparer réponse** : "Corrigé en {commit_sha_court}."
7. **Poster réponse** via `create_merge_request_discussion_note`
8. **Résoudre thread** via `resolve_merge_request_thread`

**Si "Appliquer suggestion" :**

1. Extraire le code suggéré du bloc `suggestion`
2. Appliquer avec `Edit` (remplacement exact)
3. Commit fixup
4. Répondre : "Suggestion appliquée."
5. Résoudre thread

**Si "Répondre seulement" :**

1. Demander à l'utilisateur le contenu de la réponse
2. Poster via `create_merge_request_discussion_note`
3. Ne PAS résoudre le thread

**Si "Passer" :**

1. Marquer comme "skipped" dans le suivi interne
2. Passer au feedback suivant

**Si "Marquer hors-scope" :**

1. Demander si créer une issue GitLab
2. Si oui → `mcp__gitlab-enhanced__create_issue`
3. Répondre : "Bonne idée ! C'est hors-scope de cette MR, j'ai créé l'issue #{n} pour tracker."
4. Ne PAS résoudre (le reviewer décidera)

**Si "Demander clarification" :**

1. Demander à l'utilisateur sa question
2. Poster : "Peux-tu préciser ce que tu entends par {X} ?"
3. Marquer comme "awaiting_response"
4. Passer au suivant

#### Étape 2.4 : Confirmer et continuer

Après chaque action :

```markdown
✅ Action effectuée pour feedback #{n}

Progression : {done}/{total} ({percent}%)
- Corrigés : {n}
- Répondus : {n}
- Passés : {n}
- En attente : {n}

Continuer avec le prochain feedback ?
```

---

## Phase 3 : Finalisation

### Étape 3.1 : Résumé des actions

```markdown
## 📊 Récapitulatif du traitement MR !{number}

### Actions effectuées
| # | Feedback | Action | Commit | Thread |
|---|----------|--------|--------|--------|
| 1 | @alice `api.ts:42` | Corrigé | `abc123` | ✅ Résolu |
| 2 | @bob `utils.ts:15` | Répondu | - | 💬 Ouvert |
| 3 | @alice `config.ts:3` | Passé | - | ⏸️ Skip |

### Commits créés
- `fixup! abc123` - fix null check in api.ts
- `fixup! def456` - improve error message

### Feedbacks en attente
- #4 : En attente de clarification de @bob
```

### Étape 3.2 : Proposer les actions finales

```
AskUserQuestion :
```

| Option | Description |
|--------|-------------|
| **Rebase autosquash** | `git rebase -i --autosquash` pour fusionner les fixups |
| **Push directement** | Push les commits fixup tels quels |
| **Voir les commits** | Afficher `git log --oneline` avant de décider |
| **Terminer sans push** | Garder les changements locaux |

**Si "Rebase autosquash" :**

```bash
# Compter les commits depuis la base
git rebase -i --autosquash origin/{target_branch}
```

Note : Le rebase interactif nécessite une intervention manuelle. Afficher les instructions :

```markdown
### Rebase interactif

Exécute cette commande :
```bash
git rebase -i --autosquash origin/{target_branch}
```

Dans l'éditeur qui s'ouvre, les commits `fixup!` seront déjà positionnés.
Sauvegarde et ferme l'éditeur pour appliquer.

Ensuite :
```bash
git push --force-with-lease
```
```

### Étape 3.3 : Message final

```markdown
## ✅ Traitement terminé

**MR !{number}** : {n} feedbacks traités sur {total}

### Prochaines étapes
- [ ] Exécuter le rebase si pas encore fait
- [ ] Push les changements
- [ ] Attendre les réponses des reviewers ({n} en attente)
- [ ] Re-demander une review si tous les threads sont résolus
```

---

## Comportements clés

### Ne jamais faire
- Résoudre un thread sans avoir corrigé ET confirmé
- Répondre "Done" ou "Fixed" sans vérifier que ça compile
- Deviner ce que veut le reviewer si c'est ambigu
- Implémenter une suggestion sans la montrer d'abord

### Toujours faire
- Montrer le code actuel avant de proposer une correction
- Expliquer pourquoi un feedback est jugé "discutable"
- Demander confirmation avant chaque action destructive
- Garder trace de ce qui a été fait (commits, réponses)

---

## Quick Reference

| Phase | Action | Outils |
|-------|--------|--------|
| 1 | Récupérer | `get_merge_request`, `mr_discussions` |
| 1 | Analyser | Logique interne |
| 2 | Corriger | `Edit`, `git commit --fixup` |
| 2 | Répondre | `create_merge_request_discussion_note` |
| 2 | Résoudre | `resolve_merge_request_thread` |
| 3 | Finaliser | `git rebase --autosquash`, `git push` |
