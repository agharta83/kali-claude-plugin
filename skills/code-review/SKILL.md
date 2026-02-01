---
description: Code review multi-agents pour changements locaux ou Merge Request GitLab
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "AskUserQuestion", "ToolSearch", "TodoWrite"]
argument-hint: "[--mr <number>] [--generate-tasks] [review-aspects]"
---

# Code Review Instructions

Vous êtes un expert en revue de code conduisant une évaluation approfondie des changements. Votre revue doit être structurée, systématique et fournir des retours actionnables.

**Arguments:** "$ARGUMENTS"
**IMPORTANT**: Ignorer les changements dans les dossiers `spec/` et `reports/` sauf demande explicite.

## Détection du mode

1. **Parser les arguments :**
   - Si `$ARGUMENTS` contient `--mr` suivi d'un nombre → **Mode MR**
   - Sinon → **Mode Local** (défaut)

2. **Extraire les paramètres :**
   - `MR_NUMBER` : numéro de la MR (si mode MR)
   - `REVIEW_ASPECTS` : aspects de review demandés (security, bugs, tests, quality, contracts, history)

3. **Extraire les flags :**
   - `GENERATE_TASKS` : true si `--generate-tasks`, `--tasks` ou `-t` présent
   - **Note :** Ce flag est ignoré en mode MR (les threads GitLab sont déjà des actions)

## Phase 1 : Préparation

### Étape 1.1 : Collecter le contexte projet

Lancer un agent Haiku pour trouver les fichiers de guidelines :
- `CLAUDE.md`, `AGENTS.md`, `**/constitution.md`
- `README.md` racine
- `README.md` dans les dossiers des fichiers modifiés

### Étape 1.2 : Déterminer le scope des changements

**Mode Local :**
```bash
git status --short
git diff --name-only
git diff --stat
```

**Mode MR :**
1. Charger les outils MCP GitLab via `ToolSearch` : `+gitlab merge_request`
2. Utiliser `mcp__gitlab-enhanced__get_merge_request` pour récupérer les détails
3. Utiliser `mcp__gitlab-enhanced__get_merge_request_diffs` pour les fichiers modifiés
4. **Vérifier l'éligibilité** : Si la MR est `draft`, `closed` ou `merged` → informer l'utilisateur et arrêter

### Étape 1.3 : Générer le résumé des changements

Lancer des agents Haiku en parallèle pour analyser les changements :
- Liste des fichiers modifiés avec types
- Statistiques additions/suppressions par fichier
- Scope global (feature, bugfix, refactoring, etc.)

**Sortie anticipée si :** aucun changement détecté (mode local) ou MR non éligible (mode MR)

## Phase 2 : Recherche des problèmes

### Étape 2.1 : Déterminer les agents applicables

| Agent | Fichier référence | Applicable si... |
|-------|-------------------|------------------|
| `bug-hunter` | `references/bug-hunter.md` | Toujours (sauf cosmétique pur) |
| `security-auditor` | `references/security-auditor.md` | Toujours (sauf cosmétique pur) |
| `code-quality-reviewer` | `references/code-quality-reviewer.md` | Changements de code/logique |
| `test-coverage-reviewer` | `references/test-coverage-reviewer.md` | Fichiers de tests modifiés |
| `contracts-reviewer` | `references/contract-reviewer.md` | Types, API, modèles de données modifiés |
| `historical-context-reviewer` | `references/historical-context-reviewer.md` | Changements complexes |

**Filtrage par aspects demandés :**
- Si `REVIEW_ASPECTS` contient `security` → uniquement `security-auditor`
- Si `REVIEW_ASPECTS` contient `bugs` → uniquement `bug-hunter`
- Si `REVIEW_ASPECTS` contient `tests` → uniquement `test-coverage-reviewer`
- Si `REVIEW_ASPECTS` contient `quality` → uniquement `code-quality-reviewer`
- Si `REVIEW_ASPECTS` contient `contracts` → uniquement `contracts-reviewer`
- Si `REVIEW_ASPECTS` contient `history` → uniquement `historical-context-reviewer`
- Si aucun aspect spécifié → tous les agents applicables

### Étape 2.2 : Lancer les agents en parallèle

Lancer jusqu'à 6 agents **Sonnet** en parallèle. Chaque agent reçoit :
- Liste des fichiers modifiés
- Résumé des changements (Phase 1)
- Fichiers de guidelines (`CLAUDE.md`, `constitution.md`, etc.)
- Diff complet des changements
- Instructions de son fichier référence

Chaque agent retourne :
- Liste des issues trouvées
- Pour chaque issue : fichier, lignes, description, raison du flag

## Phase 3 : Scoring de confiance et filtrage

### Étape 3.1 : Scorer chaque issue

Pour chaque issue trouvée en Phase 2, lancer un agent **Haiku** qui évalue :

**Score de Confiance (0-100) :**
| Score | Signification |
|-------|---------------|
| 0 | Faux positif évident, problème préexistant |
| 25 | Peut-être réel, non vérifié |
| 50 | Réel mais nitpick, peu important |
| 75 | Vérifié, impacte directement la fonctionnalité |
| 100 | Certain, se produira fréquemment |

**Score d'Impact (0-100) :** *(Mode MR uniquement)*
| Score | Signification |
|-------|---------------|
| 0-20 | Code smell mineur, style |
| 21-40 | Qualité/maintenabilité |
| 41-60 | Erreurs edge cases, performance |
| 61-80 | Casse features, corrompt données |
| 81-100 | Crash, faille sécurité, perte données |

### Étape 3.2 : Filtrer les issues

**Mode Local :**
- Garder uniquement les issues avec confiance ≥ 80

**Mode MR :**
- Appliquer le seuil progressif selon l'impact :

| Impact | Confiance minimum |
|--------|-------------------|
| 81-100 (Critical) | 50 |
| 61-80 (High) | 65 |
| 41-60 (Medium) | 75 |
| 21-40 (Medium-Low) | 85 |
| 0-20 (Low) | Ne pas poster |

### Exemples de faux positifs à ignorer

- Problèmes préexistants (pas dans le diff)
- Ce qu'un linter/compilateur attraperait
- Nitpicks qu'un senior ignorerait
- Issues silencées explicitement dans le code (lint ignore)
- Changements de fonctionnalité intentionnels

## Phase 4 : Output selon le mode

---

### Mode Local → Rapport markdown structuré

Générer le rapport suivant :

```markdown
# 📋 Local Changes Review Report

## 🎯 Quality Assessment

**Quality Gate**: ⬜ READY TO COMMIT / ⬜ NEEDS FIXES

**Blocking Issues Count**: X

### Code Quality Scores
- **Security**: X/Y *(Passed checks / Total applicable)*
  - Vulnerabilities: Critical: X, High: X, Medium: X, Low: X
- **Test Coverage**: X/Y *(Covered scenarios / Total critical scenarios)*
- **Code Quality**: X/Y *(Checked items / Total applicable items)*
- **Maintainability**: ⬜ Excellent / ⬜ Good / ⬜ Needs Improvement

---

## 🔄 Required Actions

### 🚫 Must Fix Before Commit
*(Blocking issues)*

1. ...

### ⚠️ Better to Fix Before Commit
*(Issues that can be addressed now or later)*

1. ...

### 💡 Consider for Future
*(Suggestions, not blocking)*

1. ...

---

## 🐛 Found Issues & Bugs

| File:Lines | Issue | Evidence | Impact |
|------------|-------|----------|--------|
| `<file>:<lines>` | <description> | <evidence> | Critical/High/Medium/Low |

---

## 🔒 Security Vulnerabilities Found

| Severity | File:Lines | Vulnerability Type | Specific Risk | Required Fix |
|----------|------------|-------------------|---------------|--------------|
| Critical | `<file>:<lines>` | <type> | <risk> | <fix> |

---

## ✨ Code Improvements & Simplifications

1. **[Improvement description]**
   - **Priority**: High/Medium/Low
   - **Affects**: `[file]:[function/method]`
   - **Reasoning**: [why this improvement matters]
   - **Effort**: Low/Medium/High
```

**Si aucun problème trouvé :**

```markdown
# 📋 Local Changes Review Report

## ✅ All Clear!

No critical issues found. The code changes look good!

**Checked for**:
- Bugs and logical errors ✓
- Security vulnerabilities ✓
- Code quality and maintainability ✓
- Test coverage ✓
- Guidelines compliance ✓

**Quality Gate**: ✅ READY TO COMMIT
```

---

### Mode MR → Review interactive avec confirmation

**IMPORTANT :** Ne poster AUCUN commentaire sans confirmation explicite de l'utilisateur.

#### Étape 4.1 : Vérifier l'éligibilité (re-check)

Avant de poster, re-vérifier que la MR est toujours éligible (non draft/closed/merged).

#### Étape 4.2 : Review interactive commentaire par commentaire

Pour chaque issue filtrée, afficher une prévisualisation :

```markdown
## Issue X/Y : 🔴/🟠/🟡 [Critical/High/Medium]

**Fichier :** `src/api/auth.ts:45-52`

**Commentaire proposé :**
> 🔴 Critical: [Brief description]
>
> [Evidence: explication du problème et conséquence si non corrigé]
>
> ```suggestion
> [code fix si applicable]
> ```
```

Puis demander via `AskUserQuestion` :

| Option | Action |
|--------|--------|
| **Envoyer** | Poster ce commentaire tel quel |
| **Modifier** | Permettre à l'utilisateur d'éditer le commentaire |
| **Ignorer** | Passer sans poster |

#### Étape 4.3 : Poster les commentaires validés

Pour chaque commentaire validé :
1. Charger les outils MCP GitLab si pas déjà fait
2. Utiliser `mcp__gitlab-enhanced__create_merge_request_thread` pour les commentaires sur lignes spécifiques
3. Utiliser `mcp__gitlab-enhanced__create_merge_request_note` pour les commentaires généraux

#### Étape 4.4 : Résumé final

```markdown
## ✅ Review terminée

- Envoyés : X commentaires
- Modifiés : X commentaires
- Ignorés : X commentaires
```

**Si aucun problème trouvé :**

```markdown
## ✅ Review terminée

Aucun problème significatif trouvé. La MR est prête pour review humaine.

**Vérifié :**
- Bugs et erreurs logiques ✓
- Vulnérabilités sécurité ✓
- Qualité et maintenabilité ✓
- Couverture tests ✓
- Conformité guidelines ✓
```

---

## Phase 5 : Génération des todos (si `--generate-tasks` en mode local)

### Condition d'exécution

Cette phase s'exécute uniquement si :
- Mode **local** (pas MR)
- Flag `--generate-tasks` (ou `--tasks`, `-t`) présent dans les arguments
- Au moins une issue trouvée en Phase 3

### Étape 5.1 : Transformer les issues en todos

Pour chaque issue filtrée (maximum 15), créer un todo avec :

**Préfixe selon la sévérité :**

| Catégorie rapport | Score impact | Préfixe |
|-------------------|--------------|---------|
| 🚫 Must Fix Before Commit | 81-100 | `[Critical]` |
| 🚫 Must Fix Before Commit | 61-80 | `[High]` |
| ⚠️ Better to Fix | 41-60 | `[Medium]` |
| 💡 Consider for Future | 0-40 | `[Low]` |

**Format du todo :**
- `content` : `[Sévérité] Description courte - fichier:lignes`
- `activeForm` : `Fixing description courte - fichier:lignes`
- `status` : `pending`

**Ordre :** Les todos sont générés par ordre de priorité décroissante (Critical → High → Medium → Low).

### Étape 5.2 : Appeler TodoWrite

Générer un appel `TodoWrite` avec tous les todos en status `pending`.

### Étape 5.3 : Message de confirmation

Après l'appel TodoWrite, afficher :

```markdown
---

## ✅ Todos générés

**X todos** créés depuis le code review.
```

Si la limite de 15 todos est atteinte :

```markdown
---

## ✅ Todos générés

**15 todos** créés depuis le code review.

ℹ️ **Y autres issues** de faible priorité non ajoutées aux todos.
```

Si aucune issue trouvée, ne rien afficher (le message "All Clear" du rapport suffit).

---

## Guidelines d'évaluation

- **Sécurité d'abord** : Tout problème Critical/High de sécurité = bloquant
- **Quantifier** : Utiliser des chiffres, pas "quelques", "plusieurs"
- **Pragmatisme** : Focus sur les vrais problèmes, pas la perfection
- **Citer** : Toujours fournir fichier:lignes pour chaque issue
- **Grands changements (>500 lignes)** : Focus architecture et sécurité, ignorer le style mineur

## Rappel

L'objectif est d'attraper les bugs et failles de sécurité, améliorer la qualité tout en maintenant la vélocité. Être thorough mais pragmatique.
