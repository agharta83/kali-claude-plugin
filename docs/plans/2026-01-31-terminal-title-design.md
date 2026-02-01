# Terminal Title Skill - Design

**Date :** 2026-01-31
**Statut :** Validé

## Objectif

Mettre à jour automatiquement le titre du terminal pour refléter l'activité courante de Claude Code. Utile pour les développeurs gérant plusieurs sessions Claude Code dans différents terminaux.

## Format du titre

```
dossier | Activité
```

Exemples :
- `obat-tools | Coding`
- `mon-projet | Testing`
- `api-backend | Exploring`

## Mécanisme

- Hook `PostToolUse` qui s'exécute après chaque appel d'outil
- Analyse l'outil utilisé pour déterminer l'activité
- Met à jour le titre via séquence d'échappement ANSI (`\033]0;titre\007`)
- Sans état persistant - recalculé à chaque appel

## Catégories d'activité

| Outils | Activité |
|--------|----------|
| `Read`, `Glob`, `Grep` | Exploring |
| `Edit`, `Write` | Coding |
| `Bash` + test/pytest/jest/vitest/npm test | Testing |
| `Bash` + git | Git |
| `Bash` autre | Running |
| `Task` | Researching |
| Autre | Working |

## Structure des fichiers

```
skills/
└── terminal-title/
    ├── SKILL.md
    └── hooks/
        └── post-tool-use.sh
```

## Configuration du hook

Dans `.claude/settings.local.json` ou settings utilisateur :

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash skills/terminal-title/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

## Script du hook

```bash
#!/bin/bash

# Lire le JSON depuis stdin
input=$(cat)

# Extraire tool_name et tool_input
tool_name=$(echo "$input" | jq -r '.tool_name')
tool_input=$(echo "$input" | jq -r '.tool_input // empty')

# Déterminer l'activité
case "$tool_name" in
  Read|Glob|Grep)
    activity="Exploring"
    ;;
  Edit|Write)
    activity="Coding"
    ;;
  Task)
    activity="Researching"
    ;;
  Bash)
    # Analyser la commande
    if echo "$tool_input" | grep -qE '(test|pytest|jest|vitest|npm test)'; then
      activity="Testing"
    elif echo "$tool_input" | grep -qE '^git '; then
      activity="Git"
    else
      activity="Running"
    fi
    ;;
  *)
    activity="Working"
    ;;
esac

# Récupérer le nom du dossier
folder=$(basename "$PWD")

# Mettre à jour le titre du terminal
echo -ne "\033]0;${folder} | ${activity}\007"
```

## Prérequis

- `jq` installé sur le système
- Terminal compatible ANSI (iTerm2, Terminal.app, GNOME Terminal, Windows Terminal, etc.)

## Mises à jour requises

1. Créer `skills/terminal-title/SKILL.md`
2. Créer `skills/terminal-title/hooks/post-tool-use.sh`
3. Mettre à jour `README.md` avec la documentation du skill
4. Configurer le hook dans les settings
