---
name: terminal-title
description: "Met à jour automatiquement le titre du terminal pour refléter l'activité courante de Claude Code."
---

# Terminal Title

Met à jour le titre de votre terminal en fonction de ce que fait Claude Code. Idéal pour gérer plusieurs sessions Claude Code dans différents terminaux.

## Format

```
dossier | Activité
```

Exemples :
- `kali-tools | Coding`
- `mon-projet | Testing`
- `api-backend | Exploring`

## Activités détectées

| Activité | Déclencheur |
|----------|-------------|
| Exploring | Lecture de fichiers, recherche |
| Coding | Édition de fichiers |
| Testing | Exécution de tests |
| Git | Commandes git |
| Running | Autres commandes bash |
| Researching | Agents de recherche |
| Working | Autres outils |

## Installation

Le hook est configuré automatiquement à l'installation du plugin.

Pour une installation manuelle, ajoutez dans vos settings Claude Code :

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash path/to/skills/terminal-title/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

## Prérequis

- `jq` installé sur le système (`sudo apt install jq` ou `brew install jq`)
- Terminal compatible ANSI (iTerm2, Terminal.app, GNOME Terminal, Windows Terminal, etc.)
