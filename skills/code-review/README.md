# Code Review Plugin

Système de code review multi-agents qui examine le code sous plusieurs angles spécialisés pour détecter bugs, failles de sécurité et problèmes de qualité avant la production.

## Points forts

- **Analyse multi-perspectives** - Six agents spécialisés examinent le code sous différents angles
- **Détection précoce** - Attraper les bugs avant les commits et merge requests
- **Audit sécurité** - Identifier vulnérabilités et vecteurs d'attaque
- **Qualité** - Maintenir les standards et bonnes pratiques

## Utilisation

```bash
# Review des changements locaux (défaut)
/code-review

# Review avec focus sur certains aspects
/code-review security
/code-review bugs tests

# Review d'une Merge Request GitLab
/code-review --mr 123

# Review MR avec focus sécurité
/code-review --mr 123 security
```

### Arguments

| Argument | Description |
|----------|-------------|
| `--mr <number>` | Numéro de la MR GitLab à reviewer |
| `--generate-tasks` | Génère des todos depuis les issues (mode local uniquement) |
| `--tasks`, `-t` | Alias pour `--generate-tasks` |
| `security` | Focus sur l'audit sécurité |
| `bugs` | Focus sur la détection de bugs |
| `tests` | Focus sur la couverture de tests |
| `quality` | Focus sur la qualité du code |
| `contracts` | Focus sur les contrats API/types |
| `history` | Focus sur le contexte historique |

## Modes de fonctionnement

### Mode Local (défaut)

Review des changements non committés dans le répertoire de travail.

**Output :** Rapport markdown structuré avec :
- Quality Gate (READY TO COMMIT / NEEDS FIXES)
- Issues bloquantes vs suggestions
- Scores de qualité par catégorie

```bash
/code-review
/code-review security bugs
```

### Génération de todos (mode local)

Transforme automatiquement les issues détectées en todos pour faciliter le suivi des corrections.

```bash
/code-review --generate-tasks
/code-review security --generate-tasks
```

**Comportement :**
- Affiche le rapport complet (comme d'habitude)
- Génère ensuite un todo par issue (max 15)
- Todos préfixés par sévérité : `[Critical]`, `[High]`, `[Medium]`, `[Low]`
- Triés par priorité décroissante

**Note :** Ce flag est ignoré en mode MR (les threads GitLab sont déjà des actions).

### Mode Merge Request

Review d'une MR GitLab avec workflow interactif.

**Output :** Commentaires inline sur la MR après validation utilisateur.

Pour chaque issue détectée :
1. Prévisualisation du commentaire proposé
2. Choix : Envoyer / Modifier / Ignorer
3. Résumé final des actions

```bash
/code-review --mr 123
/code-review --mr #456 security
```

## Architecture des agents

```
/code-review
    │
    ├──> Bug Hunter (parallel)
    ├──> Security Auditor (parallel)
    ├──> Test Coverage Reviewer (parallel)
    ├──> Code Quality Reviewer (parallel)
    ├──> Contracts Reviewer (parallel)
    └──> Historical Context Reviewer (parallel)
            │
            ▼
    Scoring & Filtrage
            │
            ▼
    Output (Rapport / Commentaires MR)
```

## Agents spécialisés

### Bug Hunter

**Focus :** Bugs potentiels et edge cases via analyse root cause

- Null pointer exceptions
- Off-by-one errors
- Race conditions
- Memory/resource leaks
- Erreurs non gérées
- Erreurs logiques

### Security Auditor

**Focus :** Vulnérabilités de sécurité et vecteurs d'attaque

- SQL injection
- XSS vulnerabilities
- CSRF protection manquante
- Bypass auth/authz
- Secrets exposés
- Cryptographie insécure

### Test Coverage Reviewer

**Focus :** Qualité et couverture des tests

- Gaps de couverture
- Tests edge cases manquants
- Besoins en tests d'intégration
- Qualité des tests

### Code Quality Reviewer

**Focus :** Structure et maintenabilité du code

- Complexité du code
- Conventions de nommage
- Duplication
- Design patterns
- Code smells

### Contracts Reviewer

**Focus :** Contrats API et interfaces

- Définitions d'endpoints
- Schemas request/response
- Breaking changes
- Backward compatibility
- Type safety

### Historical Context Reviewer

**Focus :** Changements vs historique du codebase

- Cohérence avec patterns existants
- Patterns de bugs précédents
- Drift architectural
- Indicateurs de dette technique

## Scoring et filtrage

### Score de confiance (0-100)

| Score | Signification |
|-------|---------------|
| 0 | Faux positif évident |
| 25 | Peut-être réel, non vérifié |
| 50 | Réel mais nitpick |
| 75 | Vérifié, impacte la fonctionnalité |
| 100 | Certain, se produira fréquemment |

### Score d'impact (MR uniquement)

| Score | Signification |
|-------|---------------|
| 0-20 | Code smell mineur |
| 21-40 | Qualité/maintenabilité |
| 41-60 | Erreurs edge cases |
| 61-80 | Casse features |
| 81-100 | Crash, faille sécurité |

### Seuils de filtrage

**Mode Local :** Confiance >= 80

**Mode MR :** Seuil progressif selon impact
- Critical (81-100) : confiance >= 50
- High (61-80) : confiance >= 65
- Medium (41-60) : confiance >= 75
- Low (0-20) : jamais posté

## Prérequis

### Mode MR

- MCP `gitlab-enhanced` configuré
- Accès à l'API GitLab

## Structure des fichiers

```
skills/code-review/
├── SKILL.md                 # Skill principal
├── README.md                # Cette documentation
└── references/
    ├── bug-hunter.md
    ├── security-auditor.md
    ├── code-quality-reviewer.md
    ├── contract-reviewer.md
    ├── test-coverage-reviewer.md
    └── historical-context-reviewer.md
```
