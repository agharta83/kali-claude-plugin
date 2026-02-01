#!/usr/bin/env python3
"""
Skill Initializer - Crée un nouveau skill à partir d'un template

Usage:
    init_skill.py <skill-name> --path <path> [--type <workflow|hook|custom>]

Types de skills:
    workflow : Skill avec processus étapé (ex: brainstorm, plan)
    hook     : Skill avec scripts déclenchés par événements Claude Code
    custom   : Structure minimale à personnaliser

Exemples:
    init_skill.py mon-skill --path skills/
    init_skill.py mon-workflow --path skills/ --type workflow
    init_skill.py terminal-hook --path skills/ --type hook
"""

import sys
from pathlib import Path


# Template pour les skills de type WORKFLOW
WORKFLOW_TEMPLATE = """---
name: {skill_name}
description: "[TODO: Description du skill et quand l'utiliser. Exemple: Brainstorming pour définir une feature.]"
---

# {skill_title}

## Routage

Analyser la requête utilisateur pour déterminer le mode :

### Mode standard
[TODO: Décrire quand ce mode s'active]

### Mode alternatif (optionnel)
[TODO: Si le skill a plusieurs modes, les décrire ici. Sinon, supprimer cette section.]

---

## Processus

### Étape 1 : Comprendre le contexte

[TODO: Comment le skill doit explorer et comprendre la demande]
- Explorer l'état actuel du projet
- Poser des questions pour clarifier

### Étape 2 : Exécuter

[TODO: Les actions principales du skill]

### Étape 3 : Finaliser

[TODO: Comment conclure (génération de fichiers, propositions, etc.)]

---

## Principes clés

- **[TODO]** - [Description]
- **YAGNI** - Ne pas ajouter de fonctionnalités inutiles
- **Validation incrémentale** - Vérifier à chaque étape

---

## Après l'exécution

[TODO: Ce qui se passe après (commit, sync, proposition de suite...)]
"""

# Template pour les skills de type HOOK
HOOK_TEMPLATE = """---
name: {skill_name}
description: "[TODO: Description du hook et ce qu'il fait automatiquement.]"
---

# {skill_title}

[TODO: Description courte de ce que fait le hook]

## Format

[TODO: Décrire le format de sortie/comportement]

## Événements déclencheurs

| Événement | Déclencheur |
|-----------|-------------|
| [TODO] | [Description] |

## Installation

Le hook est configuré automatiquement à l'installation du plugin.

Pour une installation manuelle, ajoutez dans vos settings Claude Code :

```json
{{
  "hooks": {{
    "[TODO: PostToolUse|PreToolUse|etc]": [
      {{
        "matcher": ".*",
        "hooks": [
          {{
            "type": "command",
            "command": "bash path/to/skills/{skill_name}/hooks/[TODO].sh"
          }}
        ]
      }}
    ]
  }}
}}
```

## Prérequis

- [TODO: Dépendances nécessaires]
"""

# Template pour les skills de type CUSTOM (minimal)
CUSTOM_TEMPLATE = """---
name: {skill_name}
description: "[TODO: Description complète du skill et quand l'utiliser.]"
---

# {skill_title}

## Overview

[TODO: 1-2 phrases décrivant ce que ce skill permet]

## Utilisation

[TODO: Comment utiliser ce skill]

## Ressources

[TODO: Décrire les fichiers/dossiers inclus si nécessaire, ou supprimer cette section]
"""

# Ancien template générique pour compatibilité
SKILL_TEMPLATE = CUSTOM_TEMPLATE

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Script utilitaire pour {skill_name}

Ce script est un placeholder à remplacer ou supprimer.

Exemples de scripts dans d'autres skills :
- pdf/scripts/fill_fillable_fields.py - Remplit les champs d'un PDF
- pdf/scripts/convert_pdf_to_images.py - Convertit un PDF en images
"""

def main():
    print("Script exemple pour {skill_name}")
    # TODO: Ajouter la logique du script ici

if __name__ == "__main__":
    main()
'''

EXAMPLE_HOOK = '''#!/bin/bash
# Hook pour {skill_name}
#
# Ce script est exécuté automatiquement par Claude Code.
# Supprimer ou modifier selon vos besoins.
#
# Variables disponibles :
#   $CLAUDE_TOOL_NAME - Nom de l'outil utilisé
#   $CLAUDE_WORKING_DIR - Répertoire de travail

# TODO: Implémenter la logique du hook
echo "Hook {skill_name} exécuté"
'''

EXAMPLE_REFERENCE = """# Documentation de référence pour {skill_title}

Ce fichier est un placeholder pour la documentation détaillée.
À remplacer ou supprimer selon les besoins.

## Quand utiliser les références

Les fichiers de référence sont utiles pour :
- Documentation d'API
- Guides de workflow détaillés
- Processus complexes multi-étapes
- Information trop longue pour SKILL.md
- Contenu nécessaire seulement dans certains cas

## Structure suggérée

### Exemple API
- Vue d'ensemble
- Authentification
- Endpoints avec exemples
- Codes d'erreur

### Exemple Workflow
- Prérequis
- Instructions étape par étape
- Patterns courants
- Dépannage
"""

EXAMPLE_ASSET = """# Fichier asset exemple

Les assets sont des fichiers utilisés dans les outputs de Claude,
pas chargés en contexte.

Exemples d'assets :
- Templates : .pptx, .docx, boilerplate de projet
- Images : .png, .jpg, .svg
- Fonts : .ttf, .woff2
- Données : .csv, .json

Ce fichier placeholder peut être supprimé.
"""


def title_case_skill_name(skill_name):
    """Convertit un nom-en-kebab en Titre Avec Majuscules."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def get_template_for_type(skill_type):
    """Retourne le template approprié selon le type de skill."""
    templates = {
        'workflow': WORKFLOW_TEMPLATE,
        'hook': HOOK_TEMPLATE,
        'custom': CUSTOM_TEMPLATE,
    }
    return templates.get(skill_type, CUSTOM_TEMPLATE)


def init_skill(skill_name, path, skill_type='custom'):
    """
    Initialise un nouveau répertoire de skill avec template SKILL.md.

    Args:
        skill_name: Nom du skill (kebab-case)
        path: Chemin où créer le répertoire du skill
        skill_type: Type de skill (workflow, hook, custom)

    Returns:
        Chemin du répertoire créé, ou None si erreur
    """
    # Déterminer le chemin du skill
    skill_dir = Path(path).resolve() / skill_name

    # Vérifier si le répertoire existe déjà
    if skill_dir.exists():
        print(f"❌ Erreur : Le répertoire existe déjà : {skill_dir}")
        return None

    # Créer le répertoire du skill
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Répertoire créé : {skill_dir}")
    except Exception as e:
        print(f"❌ Erreur création répertoire : {e}")
        return None

    # Créer SKILL.md à partir du template
    skill_title = title_case_skill_name(skill_name)
    template = get_template_for_type(skill_type)
    skill_content = template.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print(f"✅ SKILL.md créé (type: {skill_type})")
    except Exception as e:
        print(f"❌ Erreur création SKILL.md : {e}")
        return None

    # Créer les répertoires selon le type de skill
    try:
        if skill_type == 'hook':
            # Pour les hooks : créer hooks/ avec un script exemple
            hooks_dir = skill_dir / 'hooks'
            hooks_dir.mkdir(exist_ok=True)
            example_hook = hooks_dir / 'post-tool-use.sh'
            example_hook.write_text(EXAMPLE_HOOK.format(skill_name=skill_name))
            example_hook.chmod(0o755)
            print("✅ hooks/post-tool-use.sh créé")

        elif skill_type == 'workflow':
            # Pour les workflows : créer references/ seulement
            references_dir = skill_dir / 'references'
            references_dir.mkdir(exist_ok=True)
            example_reference = references_dir / 'guide.md'
            example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
            print("✅ references/guide.md créé")

        else:  # custom
            # Pour custom : structure minimale, pas de dossiers par défaut
            print("ℹ️  Aucun dossier supplémentaire créé (type: custom)")
            print("   Ajoutez scripts/, hooks/, references/ ou assets/ selon vos besoins")

    except Exception as e:
        print(f"❌ Erreur création ressources : {e}")
        return None

    # Afficher les prochaines étapes
    print(f"\n✅ Skill '{skill_name}' initialisé dans {skill_dir}")
    print("\nProchaines étapes :")
    print("1. Compléter les TODO dans SKILL.md")
    print("2. Ajouter les ressources nécessaires")
    print("3. Valider avec quick_validate.py")

    return skill_dir


def parse_args(args):
    """Parse les arguments de la ligne de commande."""
    skill_name = None
    path = None
    skill_type = 'custom'

    i = 0
    while i < len(args):
        if args[i] == '--path' and i + 1 < len(args):
            path = args[i + 1]
            i += 2
        elif args[i] == '--type' and i + 1 < len(args):
            skill_type = args[i + 1]
            i += 2
        elif not args[i].startswith('--') and skill_name is None:
            skill_name = args[i]
            i += 1
        else:
            i += 1

    return skill_name, path, skill_type


def main():
    if len(sys.argv) < 4:
        print("Usage: init_skill.py <skill-name> --path <path> [--type <workflow|hook|custom>]")
        print("\nTypes de skills :")
        print("  workflow : Skill avec processus étapé (ex: brainstorm, plan)")
        print("  hook     : Skill avec scripts déclenchés par événements Claude")
        print("  custom   : Structure minimale à personnaliser (défaut)")
        print("\nConventions de nommage :")
        print("  - Kebab-case (ex: 'mon-skill')")
        print("  - Lettres minuscules, chiffres, tirets uniquement")
        print("  - Max 40 caractères")
        print("\nExemples :")
        print("  init_skill.py mon-skill --path skills/")
        print("  init_skill.py mon-workflow --path skills/ --type workflow")
        print("  init_skill.py terminal-hook --path skills/ --type hook")
        sys.exit(1)

    skill_name, path, skill_type = parse_args(sys.argv[1:])

    if not skill_name or not path:
        print("❌ Erreur : skill-name et --path sont requis")
        sys.exit(1)

    if skill_type not in ('workflow', 'hook', 'custom'):
        print(f"❌ Erreur : type '{skill_type}' invalide (workflow, hook, custom)")
        sys.exit(1)

    print(f"🚀 Création du skill : {skill_name}")
    print(f"   Chemin : {path}")
    print(f"   Type : {skill_type}")
    print()

    result = init_skill(skill_name, path, skill_type)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()