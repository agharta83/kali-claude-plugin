# Design: `/code-review --generate-tasks`

**Date**: 2026-02-01
**Status**: Validé

## Objectif

Ajouter un flag `--generate-tasks` au skill `/code-review` pour transformer automatiquement les findings en todos TodoWrite, permettant de "fermer la boucle" review → action.

## Contraintes

- **Mode local uniquement** : Le flag est ignoré en mode MR (les threads GitLab sont déjà des actions)
- **Opt-in** : Comportement actuel inchangé sans le flag

## Syntaxe

```bash
# Comportement actuel (inchangé)
/code-review                      # Rapport local
/code-review --mr 123             # Review MR interactive

# Nouveau flag (mode local uniquement)
/code-review --generate-tasks     # Rapport + génération todos
/code-review security --generate-tasks  # Focus sécurité + todos
```

### Alias

- `--generate-tasks` (forme longue)
- `--tasks` (alias court)
- `-t` (alias minimal)

## Flow

```
┌─────────────────────┐
│  /code-review       │
│  --generate-tasks   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Phase 1-3          │
│  (existantes)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Phase 4 : Rapport  │
│  markdown (existant)│
└──────────┬──────────┘
           │
           ▼  (si --generate-tasks + mode local)
┌─────────────────────┐
│  Phase 5 : Génération│
│  TodoWrite          │
└─────────────────────┘
```

## Génération des todos

### Mapping issues → todos

Chaque issue du rapport devient un todo :

| Champ TodoWrite | Valeur |
|-----------------|--------|
| `content` | `[Critical] Fix SQL injection in UserRepository.php:45` |
| `activeForm` | `Fixing SQL injection in UserRepository.php:45` |
| `status` | `pending` |

### Préfixes par sévérité

| Catégorie rapport | Préfixe todo |
|-------------------|--------------|
| 🚫 Must Fix Before Commit (impact 81-100) | `[Critical]` |
| 🚫 Must Fix Before Commit (impact 61-80) | `[High]` |
| ⚠️ Better to Fix (impact 41-60) | `[Medium]` |
| 💡 Consider for Future (impact 0-40) | `[Low]` |

### Ordre et limite

- Todos générés par ordre de priorité (Critical → High → Medium → Low)
- Maximum **15 todos** pour éviter de surcharger la liste
- Si plus d'issues : message informatif "X autres issues de faible priorité non ajoutées"

## Modifications du SKILL.md

### Phase 1 : Parsing des arguments

Ajouter l'extraction du flag :

```markdown
3. **Extraire les flags :**
   - `GENERATE_TASKS` : true si `--generate-tasks`, `--tasks` ou `-t` présent
   - **Note :** Ce flag est ignoré en mode MR
```

### Nouvelle Phase 5 : Génération des todos

```markdown
## Phase 5 : Génération des todos (si --generate-tasks en mode local)

### Condition d'exécution
- Mode local uniquement
- Flag `--generate-tasks` présent
- Au moins une issue trouvée

### Étape 5.1 : Transformer les issues en todos

Pour chaque issue (max 15), créer un todo :
- Préfixe selon sévérité : [Critical], [High], [Medium], [Low]
- Format content : `[Sévérité] Description courte - fichier:lignes`
- Format activeForm : `Fixing description courte - fichier:lignes`

### Étape 5.2 : Appeler TodoWrite

Générer un appel TodoWrite avec tous les todos en status `pending`.

### Étape 5.3 : Message de confirmation

- Si todos générés : "✅ X todos générés depuis le code review"
- Si limite atteinte : "ℹ️ Y autres issues de faible priorité non ajoutées aux todos"
- Si aucune issue : Pas de message supplémentaire (le rapport "All Clear" suffit)
```

## Décisions clés

| Aspect | Décision | Raison |
|--------|----------|--------|
| Déclenchement | Flag explicite `--generate-tasks` | Comportement actuel préservé, opt-in |
| Mode MR | Flag ignoré | Les threads GitLab sont déjà des actions |
| Format todos | Un todo par issue | Granularité maximale, progression visible |
| Limite | 15 todos max | Éviter surcharge de la liste |
| Intégration Jira | Non incluse | YAGNI - peut être ajoutée plus tard si besoin |

## Évolutions futures possibles

- `--jira-critical` : Créer des tickets Jira pour les issues Critical/High
- `--auto-fix` : Tenter de corriger automatiquement les issues simples
- Persistance dans un fichier `TODO-review.md`
