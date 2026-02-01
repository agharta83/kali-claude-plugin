#!/usr/bin/env python3
"""
Script de validation rapide pour les skills
"""

import sys
import re
from pathlib import Path


def validate_skill(skill_path):
    """Validation basique d'un skill"""
    skill_path = Path(skill_path)

    # Vérifier que SKILL.md existe
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md non trouvé"

    # Lire et valider le frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "Frontmatter YAML manquant (doit commencer par ---)"

    # Extraire le frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Format du frontmatter invalide"

    frontmatter = match.group(1)

    # Vérifier les champs requis
    if 'name:' not in frontmatter:
        return False, "Champ 'name' manquant dans le frontmatter"
    if 'description:' not in frontmatter:
        return False, "Champ 'description' manquant dans le frontmatter"

    # Valider le nom
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        # Vérifier la convention kebab-case
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Le nom '{name}' doit être en kebab-case (minuscules, chiffres, tirets)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Le nom '{name}' ne peut pas commencer/finir par un tiret ou contenir des tirets consécutifs"

    # Valider la description
    desc_match = re.search(r'description:\s*(.+)', frontmatter)
    if desc_match:
        description = desc_match.group(1).strip()
        # Vérifier les chevrons (souvent signe de TODO non complété)
        if '<' in description or '>' in description:
            return False, "La description ne doit pas contenir de chevrons (< ou >)"
        # Vérifier si c'est un TODO non complété
        if '[TODO' in description:
            return False, "La description contient un TODO non complété"

    return True, "✅ Skill valide !"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <répertoire_skill>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)