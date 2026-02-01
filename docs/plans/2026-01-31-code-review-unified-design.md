# Design: Skill Code Review Unifié

**Date**: 2026-01-31
**Status**: Validé

## Objectif

Fusionner les deux commandes séparées (`local.md` et `pr.md`) en un seul skill `/code-review` avec un flag `--mr` pour le mode Merge Request GitLab.

## Syntaxe

```bash
/code-review [--mr <number>] [aspects...]
```

### Exemples

```bash
/code-review                     # Local (défaut), tous les agents
/code-review security bugs       # Local, focus sécurité + bugs
/code-review --mr 123            # MR GitLab #123, tous les agents
/code-review --mr #123 security  # MR #123, focus sécurité
```

## Frontmatter

```yaml
---
description: Code review multi-agents pour changements locaux ou MR GitLab
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "AskUserQuestion", "ToolSearch"]
argument-hint: "[--mr <number>] [review-aspects]"
---
```

## Workflow

### Phase 1 : Préparation (commune)

1. **Parser les arguments**
   - Extraire le mode (local ou MR) et le numéro de MR si présent
   - Extraire les aspects de review demandés

2. **Collecter les fichiers de contexte projet** (agent Haiku)
   - Chercher : `CLAUDE.md`, `AGENTS.md`, `**/constitution.md`, `README.md` racine

3. **Déterminer le scope des changements**

   **Mode local :**
   ```bash
   git status --short
   git diff --name-only
   git diff --stat
   ```

   **Mode MR :** (via MCP GitLab)
   - `mcp__gitlab-enhanced__get_merge_request` → détails de la MR
   - `mcp__gitlab-enhanced__get_merge_request_diffs` → fichiers modifiés
   - Vérifier si MR draft/closed/merged

4. **Générer le résumé des changements** (agents Haiku en parallèle)

5. **Sortie anticipée si aucun changement ou MR non éligible**

### Phase 2 : Recherche des problèmes (agents spécialisés)

Lancement de jusqu'à 6 agents Sonnet en parallèle.

**Agents disponibles :**

| Agent | Applicable si... |
|-------|------------------|
| `bug-hunter` | Toujours (sauf cosmétique pur) |
| `security-auditor` | Toujours (sauf cosmétique pur) |
| `code-quality-reviewer` | Changements de code/logique |
| `test-coverage-reviewer` | Fichiers de tests modifiés |
| `contracts-reviewer` | Types, API, modèles de données modifiés |
| `historical-context-reviewer` | Changements complexes |

**Filtrage par aspects :**
- Si l'utilisateur spécifie `security` → uniquement `security-auditor`
- Si aucun aspect spécifié → tous les agents applicables

### Phase 3 : Scoring de confiance et filtrage

**Score de Confiance (0-100) :**
- 0 : Faux positif évident
- 25 : Peut-être réel, non vérifié
- 50 : Réel mais nitpick
- 75 : Vérifié, impacte la fonctionnalité
- 100 : Certain, se produira fréquemment

**Score d'Impact (0-100) :** *(Mode MR uniquement)*
- 0-20 : Code smell mineur
- 21-40 : Qualité/maintenabilité
- 41-60 : Erreurs edge cases, performance
- 61-80 : Casse features, corrompt données
- 81-100 : Crash, faille sécurité, perte données

**Seuils de filtrage :**

| Mode | Règle |
|------|-------|
| Local | Garder si confiance ≥ 80 |
| MR | Seuil progressif selon impact |

### Phase 4 : Output selon le mode

#### Mode Local → Rapport markdown structuré

```markdown
# 📋 Local Changes Review Report

## 🎯 Quality Assessment
**Quality Gate**: ⬜ READY TO COMMIT / ⬜ NEEDS FIXES

## 🚫 Must Fix Before Commit
## ⚠️ Better to Fix Before Commit
## 💡 Consider for Future
## 🐛 Found Issues & Bugs
## ✨ Code Improvements
```

#### Mode MR → Review interactive

Pour chaque issue, afficher une prévisualisation et demander via `AskUserQuestion` :
1. **Envoyer** - Poster ce commentaire tel quel
2. **Modifier** - Éditer le commentaire avant envoi
3. **Ignorer** - Passer sans poster

Poster via :
- `mcp__gitlab-enhanced__create_merge_request_note` pour commentaires généraux
- `mcp__gitlab-enhanced__create_merge_request_thread` pour commentaires sur lignes

## Structure des fichiers

```
skills/code-review/
├── SKILL.md                 # Skill principal unifié (nouveau)
├── README.md                # Documentation (mise à jour)
└── references/
    ├── bug-hunter.md              # Conservé
    ├── security-auditor.md        # Conservé
    ├── code-quality-reviewer.md   # Conservé
    ├── contract-reviewer.md       # Conservé
    ├── test-coverage-reviewer.md  # Conservé
    └── historical-context-reviewer.md  # Conservé
```

**À supprimer :**
- `local.md`
- `pr.md`

## Décisions clés

| Aspect | Décision |
|--------|----------|
| Mode défaut | Local |
| Flag MR | `--mr <number>` |
| Aspects | Arguments positionnels après le flag |
| Structure | Un seul SKILL.md avec sections conditionnelles |
| Output MR | Review interactive avec confirmation par commentaire |
| Backend | MCP GitLab (`mcp__gitlab-enhanced__*`) |
