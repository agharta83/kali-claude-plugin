#!/bin/bash

# Terminal Title Hook - PostToolUse
# Met à jour le titre du terminal en fonction de l'activité de Claude Code

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
    if echo "$tool_input" | grep -qE '(test|pytest|jest|vitest|npm test|npm run test)'; then
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
