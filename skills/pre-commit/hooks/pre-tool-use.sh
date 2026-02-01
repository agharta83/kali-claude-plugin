#!/bin/bash

# Pre-commit Hook - PreToolUse
# Lance les vérifications de qualité avant chaque git commit de Claude Code

# Lire le JSON depuis stdin
input=$(cat)

# Extraire la commande
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Vérifier si c'est un git commit
if [[ -z "$command" ]] || [[ ! "$command" =~ git[[:space:]]+commit ]]; then
    exit 0
fi

# Ignorer certains cas
if [[ "$command" =~ --amend ]] || [[ "$command" =~ --allow-empty ]] || [[ "$command" =~ --no-verify ]]; then
    exit 0
fi

echo "🔍 Pre-commit checks..." >&2

# Détecter le contexte Obat
IS_OBAT_CONTEXT=0
if git remote -v 2>/dev/null | grep -q "gitlab.obat.fr"; then
    IS_OBAT_CONTEXT=1
fi

# Détecter le type de projet
if [[ -f "composer.json" && -f "Makefile" && $IS_OBAT_CONTEXT -eq 1 ]]; then
    PROJECT_TYPE="php-obat"
elif [[ -f "composer.json" ]]; then
    PROJECT_TYPE="php-simple"
elif [[ -f "package.json" ]]; then
    PROJECT_TYPE="node"
else
    echo "✅ Unknown project type, skipping checks" >&2
    exit 0
fi

# Afficher le contexte
if [[ $IS_OBAT_CONTEXT -eq 1 ]]; then
    echo "  Context: Obat ($PROJECT_TYPE)" >&2
else
    echo "  Context: Generic ($PROJECT_TYPE)" >&2
fi

FAILED=0

case $PROJECT_TYPE in
    php-obat)
        # Auto-fix
        echo "  Running fix-cs..." >&2
        if make fix-cs >/dev/null 2>&1; then
            echo "  ✓ fix-cs applied" >&2
        fi

        echo "  Running rector..." >&2
        if make rector >/dev/null 2>&1; then
            echo "  ✓ rector applied" >&2
        fi

        # Re-stage modified files
        git add -u 2>/dev/null

        # Verify
        echo "  Running phpstan..." >&2
        phpstan_output=$(make phpstan 2>&1)
        if [[ $? -ne 0 ]]; then
            echo "  ✗ phpstan FAILED" >&2
            echo "" >&2
            echo "$phpstan_output" >&2
            FAILED=1
        else
            echo "  ✓ phpstan OK" >&2
        fi

        echo "  Running deptrac..." >&2
        if make deptrac >/dev/null 2>&1; then
            echo "  ✓ deptrac OK" >&2
        else
            echo "  ⚠ deptrac skipped or failed (non-blocking)" >&2
        fi
        ;;

    php-simple)
        echo "  Running phpstan..." >&2
        phpstan_output=$(vendor/bin/phpstan analyse 2>&1)
        if [[ $? -ne 0 ]]; then
            echo "  ✗ phpstan FAILED" >&2
            echo "" >&2
            echo "$phpstan_output" >&2
            FAILED=1
        else
            echo "  ✓ phpstan OK" >&2
        fi
        ;;

    node)
        echo "  Running lint..." >&2
        lint_output=$(npm run lint 2>&1)
        if [[ $? -ne 0 ]]; then
            echo "  ✗ lint FAILED" >&2
            echo "" >&2
            echo "$lint_output" >&2
            FAILED=1
        else
            echo "  ✓ lint OK" >&2
        fi
        ;;
esac

if [[ $FAILED -eq 1 ]]; then
    echo "" >&2
    echo "❌ Pre-commit checks FAILED" >&2
    echo "Fix the errors above before committing." >&2
    exit 1
fi

echo "" >&2
echo "✅ Pre-commit checks passed" >&2
exit 0
