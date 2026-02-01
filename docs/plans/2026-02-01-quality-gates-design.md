# Quality Gates dans `/finish-branch`

**Date :** 2026-02-01
**Statut :** Validé

## Contexte

Le skill `/finish-branch` a des vérifications hardcodées (make test, phpstan, etc.) mais pas de système de gates configurable. Ce design ajoute :
- Flexibilité par type de projet
- Intégration de nouveaux skills (contract-check, impact-analysis)
- Contrôle du comportement (bloquant vs bypass)

## Vue d'ensemble

Le système de quality gates ajoute une couche de vérifications configurables avant la création d'une MR.

```bash
/finish-branch              # Gates rapides (auto-détectées)
/finish-branch --strict     # Gates rapides + analyses approfondies
/finish-branch --skip-gates # Bypass (urgence uniquement)
```

**Principes :**
- **Auto-détection** : Le type de projet est détecté via les fichiers présents
- **Tout ou rien** : Une gate qui échoue = pas de MR
- **Deux niveaux** : Gates rapides par défaut, `--strict` pour les analyses longues

**Flux :**
```
1. Détecter le type de projet (PHP, Node, Python...)
2. Charger les gates correspondantes
3. Si --strict : ajouter les gates supplémentaires
4. Exécuter chaque gate séquentiellement
5. Si échec → stopper avec message d'erreur
6. Si succès → continuer vers création MR
```

## Détection du type de projet

**Règles de détection :**

```
SI composer.json + Makefile présents :
  → Type = php-backend
  → Gates = [make test, make phpstan, make fix-cs, make rector, make deptrac]

SI composer.json SANS Makefile :
  → Type = php-simple
  → Gates = [composer test, composer phpstan] (si scripts définis)

SI package.json présent :
  → Type = node
  → Gates = [npm test, npm run lint] (si scripts définis)

SI pyproject.toml OU requirements.txt présent :
  → Type = python
  → Gates = [pytest, ruff check] (si installés)

SI aucun fichier reconnu :
  → Type = unknown
  → Gates = [] (aucune gate, juste warning)
```

**Vérification des gates disponibles :**

Avant d'exécuter une gate, vérifier qu'elle existe :
- Pour `make X` : vérifier que la target existe dans le Makefile
- Pour `npm run X` : vérifier que le script existe dans package.json
- Pour les commandes directes : vérifier que l'exécutable est disponible

Si une gate configurée n'est pas disponible → **warning** (pas d'erreur) et skip.

**Affichage au démarrage :**

```
Détection du projet...
Type : php-backend
Gates actives : tests, phpstan, cs-fixer, rector, deptrac

Exécution des vérifications...
```

## Mode `--strict`

**Comportement :**

```bash
/finish-branch          # Gates de base uniquement
/finish-branch --strict # Gates de base + gates strict
```

**Gates strict (analyses approfondies) :**

| Gate | Description | Condition |
|------|-------------|-----------|
| `contract-check` | Vérifie les contrats OpenAPI/AsyncAPI | Si `/contracts` existe |
| `impact-analysis` | Analyse impact cross-service | Si `/contracts` existe |

Ces gates sont des **skills** invoqués (pas des commandes make). Elles ne sont exécutées que si :
1. Le flag `--strict` est présent
2. Les prérequis sont remplis (dossier contracts, etc.)

**Affichage mode strict :**

```
Mode strict activé

Gates de base :
✓ Tests PHPUnit
✓ PHPStan
✓ PHP CS Fixer
✓ Rector
✓ Deptrac

Gates additionnelles :
⏳ Contract check...
✓ Contract check (aucun breaking change)
⏳ Impact analysis...
✓ Impact analysis (2 services impactés, aucun critique)

Toutes les vérifications passent.
```

**Si une gate strict échoue :**

```
✗ Contract check a échoué

Breaking changes détectés :
- POST /api/users : champ 'phone' supprimé (requis par: operation)

Corrigez les breaking changes avant de continuer.
```

## Flag `--skip-gates`

**Bypass d'urgence :**

```bash
/finish-branch --skip-gates
```

Comportement :
1. Affiche un **warning** visible
2. Demande une **justification obligatoire**
3. La justification est incluse dans la description de la MR

```
⚠️  Mode skip-gates activé

Les quality gates ne seront PAS exécutées.
Ce mode est réservé aux situations d'urgence (hotfix critique).

Justification obligatoire :
> Hotfix critique - fuite de données en prod

La justification sera ajoutée à la description de la MR.
Continuer ? [o/N]
```

## Configuration

**Dans `plugin-config.yaml` :**

```yaml
finish-branch:
  # Gates par type de projet (auto-détecté)
  project-types:
    php-backend:
      gates:
        - make test
        - make phpstan
        - make fix-cs
        - make rector
        - make deptrac
    node:
      gates:
        - npm test
        - npm run lint
    python:
      gates:
        - pytest
        - ruff check

  # Gates additionnelles pour --strict
  strict-gates:
    - skill: contract-check
      condition: contracts-dir-exists
    - skill: impact-analysis
      condition: contracts-dir-exists
```

## Résumé des flags

| Flag | Comportement |
|------|--------------|
| (aucun) | Gates de base auto-détectées |
| `--strict` | Gates de base + analyses approfondies |
| `--skip-gates` | Bypass avec justification obligatoire |

## Implémentation

### Modifications requises

1. **`skills/finish-development-branch/SKILL.md`** : Ajouter la logique de quality gates
2. **`config/plugin-config.yaml`** : Ajouter la section `finish-branch` avec les gates
3. **Skills à créer** (futurs) : `/contract-check`, `/impact-analysis`

### Ordre d'implémentation suggéré

1. Refactorer le code existant pour utiliser la détection de type
2. Ajouter le support de la configuration YAML
3. Implémenter `--strict` (avec placeholder pour les skills)
4. Implémenter `--skip-gates`
5. (Plus tard) Créer les skills contract-check et impact-analysis
