# Design: Hook Pre-commit pour Claude Code

**Date**: 2026-02-01
**Status**: Validé

## Objectif

Créer un hook `PreToolUse` qui intercepte les commandes `git commit` de Claude et lance automatiquement les vérifications de qualité (cs-fixer, rector, phpstan, deptrac) avant de permettre le commit.

## Principe

```
Claude: git commit -m "feat: add auth"
        │
        ▼
┌─────────────────────┐
│  Hook PreToolUse    │
│  (détecte git commit)│
└──────────┬──────────┘
        │
        ▼
┌─────────────────────┐
│  1. Auto-fix        │
│  - make fix-cs      │
│  - make rector      │
└──────────┬──────────┘
        │
        ▼
┌─────────────────────┐
│  2. Vérification    │
│  - make phpstan     │
│  - make deptrac     │
└──────────┬──────────┘
        │
    ┌───┴───┐
    │       │
   ✅       ❌
    │       │
 Commit   Bloque
 OK       + erreurs
```

## Structure des fichiers

```
skills/pre-commit/
├── hooks/
│   └── pre-tool-use.sh   # Script shell du hook
└── README.md             # Documentation
```

## Configuration

Le hook est déclaré dans le manifest du plugin (`manifest.yaml` ou équivalent) :

```yaml
hooks:
  PreToolUse:
    - matcher: Bash
      command: skills/pre-commit/hooks/pre-tool-use.sh
```

## Logique du script

### Déclenchement

Le hook s'active uniquement si :
- Outil = `Bash`
- Commande contient `git commit`
- Commande ne contient PAS `--amend`, `--allow-empty`, ou `--no-verify`

### Détection du type de projet

Réutilise la même logique que `/finish-branch` :

| Détection | Type | Checks |
|-----------|------|--------|
| `composer.json` + `Makefile` | php-obat | fix-cs, rector, phpstan, deptrac |
| `composer.json` seul | php-simple | phpstan |
| `package.json` | node | lint |
| Autre | inconnu | Aucun (laisser passer) |

### Séquence d'exécution

1. **Fixers (auto-correction)** — `make fix-cs`, `make rector`
2. **Re-stage** — `git add -u` (les fichiers modifiés par les fixers)
3. **Vérifications** — `make phpstan`, `make deptrac`
4. **Résultat** — `exit 0` (OK) ou `exit 1` (bloque)

### Script complet

```bash
#!/bin/bash
set -e

# Parser l'input JSON de Claude Code
COMMAND=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command // empty')

# Vérifier si c'est un git commit
if [[ -z "$COMMAND" ]] || [[ ! "$COMMAND" =~ git\ commit ]]; then
    exit 0
fi

# Ignorer certains cas
if [[ "$COMMAND" =~ --amend ]] || [[ "$COMMAND" =~ --allow-empty ]] || [[ "$COMMAND" =~ --no-verify ]]; then
    exit 0
fi

echo "🔍 Pre-commit checks..."

# Détecter le type de projet
if [[ -f "composer.json" && -f "Makefile" ]]; then
    PROJECT_TYPE="php-obat"
elif [[ -f "composer.json" ]]; then
    PROJECT_TYPE="php-simple"
elif [[ -f "package.json" ]]; then
    PROJECT_TYPE="node"
else
    echo "✅ Unknown project type, skipping checks"
    exit 0
fi

FAILED=0

case $PROJECT_TYPE in
    php-obat)
        # Auto-fix
        echo "  Running fix-cs..."
        make fix-cs 2>/dev/null && echo "  ✓ fix-cs applied" || true

        echo "  Running rector..."
        make rector 2>/dev/null && echo "  ✓ rector applied" || true

        # Re-stage modified files
        git add -u

        # Verify
        echo "  Running phpstan..."
        if ! make phpstan 2>&1; then
            echo "  ✗ phpstan FAILED"
            FAILED=1
        else
            echo "  ✓ phpstan OK"
        fi

        echo "  Running deptrac..."
        make deptrac 2>/dev/null && echo "  ✓ deptrac OK" || echo "  ⚠ deptrac skipped"
        ;;

    php-simple)
        echo "  Running phpstan..."
        if ! vendor/bin/phpstan analyse 2>&1; then
            echo "  ✗ phpstan FAILED"
            FAILED=1
        else
            echo "  ✓ phpstan OK"
        fi
        ;;

    node)
        echo "  Running lint..."
        if ! npm run lint 2>&1; then
            echo "  ✗ lint FAILED"
            FAILED=1
        else
            echo "  ✓ lint OK"
        fi
        ;;
esac

if [[ $FAILED -eq 1 ]]; then
    echo ""
    echo "❌ Pre-commit checks FAILED"
    echo "Fix the errors above before committing."
    exit 1
fi

echo ""
echo "✅ Pre-commit checks passed"
exit 0
```

## Messages

### Succès

```
🔍 Pre-commit checks...
  Running fix-cs...
  ✓ fix-cs applied
  Running rector...
  ✓ rector applied
  Running phpstan...
  ✓ phpstan OK
  Running deptrac...
  ✓ deptrac OK

✅ Pre-commit checks passed
```

### Échec

```
🔍 Pre-commit checks...
  Running fix-cs...
  ✓ fix-cs applied
  Running rector...
  ✓ rector applied
  Running phpstan...

  ------ ------------------------------------------------
   Line   src/User/Service.php
  ------ ------------------------------------------------
   45     Parameter $id expects int, string given
  ------ ------------------------------------------------

  ✗ phpstan FAILED

❌ Pre-commit checks FAILED
Fix the errors above before committing.
```

## Cas particuliers

| Commande | Comportement |
|----------|--------------|
| `git commit -m "msg"` | Hook actif |
| `git commit --amend` | Hook ignoré |
| `git commit --allow-empty` | Hook ignoré |
| `git commit --no-verify` | Hook ignoré |
| `git commit -m "msg" && git push` | Hook actif sur le commit |

## Décisions clés

| Aspect | Décision | Raison |
|--------|----------|--------|
| Type de hook | PreToolUse sur Bash | Seul moyen d'intercepter avant exécution |
| Auto-fix | Oui (cs-fixer, rector) | Évite les allers-retours inutiles |
| Blocage | Oui si phpstan échoue | Les vraies erreurs doivent être corrigées |
| Détection projet | Réutilise /finish-branch | Évite la duplication de logique |
| deptrac | Non-bloquant | Peut avoir des faux positifs |
