# Pre-commit Hook

Hook automatique qui lance les vérifications de qualité avant chaque `git commit` effectué par Claude Code.

## Fonctionnement

Quand Claude exécute une commande `git commit`, le hook :

1. **Auto-fix** — Lance les fixers automatiques (cs-fixer, rector)
2. **Re-stage** — Ajoute les fichiers modifiés au staging
3. **Vérifie** — Lance les vérifications (phpstan, deptrac)
4. **Bloque ou autorise** — Si erreurs, bloque le commit

## Détection du contexte

Le hook détecte automatiquement si vous êtes dans un contexte Obat :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

## Détection du type de projet

| Contexte | Détection | Type | Checks |
|----------|-----------|------|--------|
| Obat | `composer.json` + `Makefile` | PHP Obat | fix-cs, rector, phpstan, deptrac |
| Générique | `composer.json` | PHP simple | phpstan |
| Générique | `package.json` | Node | npm run lint |
| Générique | Autre | Inconnu | Aucun (laisser passer) |

**Note :** Les checks complets (fix-cs, rector, deptrac) ne sont exécutés que dans un contexte Obat avec Makefile.

## Cas ignorés

Le hook ne se déclenche pas pour :
- `git commit --amend`
- `git commit --allow-empty`
- `git commit --no-verify`

## Output

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
  Running phpstan...
  ✗ phpstan FAILED

  ------ ------------------------------------------------
   Line   src/User/Service.php
  ------ ------------------------------------------------
   45     Parameter $id expects int, string given
  ------ ------------------------------------------------

❌ Pre-commit checks FAILED
Fix the errors above before committing.
```

## Installation

Le hook est configuré automatiquement à l'installation du plugin.

Pour une installation manuelle, ajoutez dans vos settings Claude Code :

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash path/to/skills/pre-commit/hooks/pre-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

## Prérequis

- `jq` installé sur le système (`sudo apt install jq` ou `brew install jq`)
- Pour PHP Obat : `Makefile` avec targets `fix-cs`, `rector`, `phpstan`, `deptrac`
- Pour PHP simple : `vendor/bin/phpstan`
- Pour Node : script `lint` dans `package.json`
