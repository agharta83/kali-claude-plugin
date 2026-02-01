# Design : Séparation des skills génériques et Obat

**Date :** 2026-02-01
**Objectif :** Clarifier l'utilisation en séparant les skills génériques (réutilisables sur tout projet) des skills spécifiques à Obat.

## Décisions

| Aspect | Décision |
|--------|----------|
| **Structure** | Un seul plugin, skills Obat sous `obat/` |
| **Nommage** | `/workflow`, `/plan` (génériques) vs `/obat/cqrs-generate` (spécifiques) |
| **Détection contexte** | Remote Git `gitlab.obat.fr` |
| **Skills hybrides** | Détection auto + flags `--obat` / `--no-obat` |
| **Configuration** | Section `obat:` dans `plugin-config.yaml`, ignorée hors contexte |
| **Rétrocompat** | Messages de redirection pour anciens noms |

## Structure des répertoires

```
skills/
├── # ─── SKILLS GÉNÉRIQUES ───
├── workflow/SKILL.md
├── brainstorm/SKILL.md
├── plan/SKILL.md
├── execute-plan/SKILL.md
├── finish-development-branch/SKILL.md
├── setup-worktree/SKILL.md
├── code-review/
├── check-pipeline/SKILL.md
├── notify-cr/SKILL.md
├── mr-feedback/SKILL.md
├── docs/
│   ├── analysis/SKILL.md
│   └── update/SKILL.md
├── sdd/
├── pre-commit/
├── terminal-title/
│
├── # ─── SKILLS OBAT (préfixés) ───
├── obat/
│   ├── contract-check/SKILL.md
│   ├── impact-analysis/SKILL.md
│   ├── cqrs-generate/SKILL.md
│   ├── api-migrate/SKILL.md
│   └── jira-sync/SKILL.md
```

## Détection automatique du contexte Obat

```bash
# Détection via remote Git
git remote -v | grep -q "gitlab.obat.fr"
```

### Comportement des skills hybrides

| Skill | Hors Obat | Dans Obat (auto-détecté) |
|-------|-----------|--------------------------|
| `/finish-branch` | Quality gates basiques (test, lint) | + `--strict` propose contract-check, impact-analysis |
| `/finish-branch --strict` | Erreur "pas de checks Obat disponibles" | Lance `/obat/contract-check` + `/obat/impact-analysis` |
| `/setup-worktree` | Demande format libre pour la branche | Propose conventions Obat (`feat/DEL-123`, `tech/...`) |
| `pre-commit` hook | Checks génériques (lint, test) | Checks Obat (`make fix-cs`, `rector`, `phpstan`, `deptrac`) |
| `/brainstorm --jira` | Fonctionne (Jira est générique) | Idem + suggestions ADR format Obat |

### Override explicite

- `--no-obat` : Force le mode générique même dans un repo Obat
- `--obat` : Force le mode Obat (utile pour tester hors contexte)

## Configuration centralisée

Le fichier `config/plugin-config.yaml` sera restructuré :

```yaml
# ─── CONFIGURATION GÉNÉRIQUE ───
workflow:
  default-flow: [brainstorm, plan, execute-plan, code-review, finish-branch]
  checkpoints: [plan, code-review]
  autopilot-threshold: 3

code-review:
  agents: [bug-hunter, security-auditor, code-quality, test-coverage, contracts, historical]
  parallel: true

finish-branch:
  project-types:
    php-backend: [test, phpstan]
    node: [npm test, npm run lint]
    python: [pytest, ruff check]

slack:
  code_review_channel: "#code-reviews"

# ─── CONFIGURATION OBAT (ignorée hors contexte) ───
obat:
  detection: gitlab.obat.fr

  finish-branch:
    project-types:
      php-backend: [make test, make phpstan, make fix-cs, make rector, make deptrac]
    strict-checks: [obat/contract-check, obat/impact-analysis]

  worktree:
    naming: "{type}/{PROJECT}-{ID}[-desc]"
    types: [feat, tech, fix, hotfix]

  jira:
    default_project: OBAT
    board_id: 42
```

## Implémentation dans les skills

Chaque skill hybride inclura un bloc de détection :

```markdown
## Détection du contexte

1. Vérifier le remote Git :
   ```bash
   git remote -v | grep -q "gitlab.obat.fr"
   ```
2. Si Obat détecté → charger `config.obat.<skill>`
3. Sinon → utiliser `config.<skill>` (générique)
```

Les skills purement Obat afficheront une erreur claire hors contexte :

```
⚠️ Ce skill nécessite un contexte Obat (remote gitlab.obat.fr).
   Utilisez --obat pour forcer l'exécution.
```

## Plan de migration

| Action | Fichiers concernés |
|--------|-------------------|
| **Déplacer** | `contract-check/` → `obat/contract-check/` |
| **Déplacer** | `impact-analysis/` → `obat/impact-analysis/` |
| **Déplacer** | `cqrs-generate/` → `obat/cqrs-generate/` |
| **Déplacer** | `api-migrate/` → `obat/api-migrate/` |
| **Déplacer** | `jira-sync/` → `obat/jira-sync/` |
| **Modifier** | `finish-development-branch/SKILL.md` - ajouter détection contexte |
| **Modifier** | `setup-worktree/SKILL.md` - ajouter détection contexte |
| **Modifier** | `pre-commit/hooks/pre-tool-use.sh` - ajouter détection contexte |
| **Modifier** | `brainstorm/SKILL.md` - conditionner ADR format Obat |
| **Restructurer** | `config/plugin-config.yaml` - séparer générique/obat |
| **Mettre à jour** | `README.md` - documenter les deux namespaces |
| **Mettre à jour** | `.claude-plugin/plugin.json` - description mise à jour |

### Rétrocompatibilité

Les anciens noms (`/contract-check`) afficheront un message :
```
Ce skill a été déplacé vers /obat/contract-check
```

## Résultat pour l'utilisateur

```bash
# Dans n'importe quel projet
/workflow              # ✅ Fonctionne
/code-review           # ✅ Fonctionne
/obat/cqrs-generate    # ⚠️ "Contexte Obat requis"

# Dans un repo Obat (gitlab.obat.fr)
/workflow              # ✅ Fonctionne avec features Obat auto-activées
/finish-branch --strict # ✅ Lance contract-check + impact-analysis
/obat/cqrs-generate    # ✅ Fonctionne
```
