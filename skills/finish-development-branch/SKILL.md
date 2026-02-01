---
name: finish-branch
description: "Finalise une branche de développement : quality gates configurables, création MR GitLab, transition Jira."
---

# Finish Branch

Finalise une branche de développement.

**Principe :** Quality gates → Créer MR GitLab → Proposer transition Jira

**Annonce au démarrage :** "J'utilise le skill finish-branch pour finaliser cette branche."

## Détection du contexte

Détecter si on est dans un contexte Obat :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

| Contexte | Comportement |
|----------|--------------|
| Obat détecté | Charger `config.obat.finish-branch`, conventions Obat actives |
| Hors Obat | Charger `config.finish-branch` générique |
| `--obat` flag | Forcer le contexte Obat |
| `--no-obat` flag | Forcer le contexte générique |

## Routage

Analyser les flags pour déterminer le mode :

- `/finish-branch` → Mode standard (gates auto-détectées)
- `/finish-branch --strict` → Mode strict (gates + analyses approfondies)
- `/finish-branch --skip-gates` → Bypass (urgence, avec justification)

## Étape 1 : Vérifier la branche

Vérifier qu'on est sur une branche feature (pas main/develop) :

```bash
branch=$(git branch --show-current)
```

Si `main` ou `develop` → Stopper : "Vous êtes sur la branche principale. Créez une branche feature d'abord."

## Étape 2 : Extraire l'ID Jira

Extraire l'ID depuis le nom de branche :

```
feat/DEL-123-description → DEL-123
tech/DEL-456 → DEL-456
fix/OBAT-789-bugfix → OBAT-789
```

Pattern : `(feat|tech|fix|hotfix)/([A-Z]+-\d+)`

Si pas d'ID trouvé → Demander : "Quel est l'ID du ticket Jira associé ?"

## Étape 3 : Quality Gates

### 3.1 Vérifier le flag `--skip-gates`

Si `--skip-gates` est présent :

```
⚠️  Mode skip-gates activé

Les quality gates ne seront PAS exécutées.
Ce mode est réservé aux situations d'urgence (hotfix critique).

Justification obligatoire :
>
```

Attendre la justification. Si vide → redemander.
Stocker la justification pour l'ajouter à la description MR.
Passer directement à l'étape 4.

### 3.2 Détecter le type de projet

Appliquer ces règles dans l'ordre :

```
SI composer.json ET Makefile présents :
  → Type = php-backend
  → Gates = [make test, make phpstan, make fix-cs, make rector, make deptrac]

SI composer.json SANS Makefile :
  → Type = php-simple
  → Gates = [composer test, composer phpstan] (si scripts définis dans composer.json)

SI package.json présent :
  → Type = node
  → Gates = [npm test, npm run lint] (si scripts définis dans package.json)

SI pyproject.toml OU requirements.txt présent :
  → Type = python
  → Gates = [pytest, ruff check] (si commandes disponibles)

SINON :
  → Type = unknown
  → Gates = []
  → Afficher warning : "Type de projet non reconnu, aucune gate exécutée."
```

**Afficher le résultat de la détection :**

```
Détection du projet...
Type : php-backend
Gates actives : tests, phpstan, cs-fixer, rector, deptrac
```

### 3.3 Vérifier la disponibilité des gates

Avant d'exécuter, vérifier que chaque gate est disponible :

- Pour `make X` : `grep -q "^X:" Makefile`
- Pour `npm run X` : vérifier que le script existe dans package.json
- Pour commandes directes : `command -v <cmd>`

Si une gate n'est pas disponible → **warning** et skip (pas d'erreur).

### 3.4 Exécuter les gates de base

Exécuter chaque gate **séquentiellement** :

```
Exécution des vérifications...
⏳ Tests PHPUnit...
✓ Tests PHPUnit
⏳ PHPStan...
✓ PHPStan
⏳ PHP CS Fixer...
✓ PHP CS Fixer
⏳ Rector...
✓ Rector
⏳ Deptrac...
✓ Deptrac

Toutes les vérifications passent.
```

**Si une gate échoue :**

```
✗ PHPStan a échoué

[Afficher la sortie d'erreur]

Corrigez les erreurs avant de continuer.
```

**STOPPER immédiatement.** Ne pas continuer, ne pas proposer de créer la MR.

### 3.5 Exécuter les gates strict (si `--strict`)

Si le flag `--strict` est présent, après les gates de base :

```
Mode strict activé

Gates additionnelles :
```

**Prérequis :** `--strict` nécessite un contexte Obat.

Si hors contexte Obat et `--strict` demandé :
```
⚠️ Le mode --strict nécessite un contexte Obat (remote gitlab.obat.fr).
   Les gates contract-check et impact-analysis ne sont pas disponibles.

Options :
1. Continuer sans gates strict
2. Annuler
```

**Gate obat/contract-check :**
- Condition : le dossier `api-contracts/` existe
- Si condition remplie : invoquer le skill `/obat/contract-check`
- Si skill non disponible : afficher "⚠️ Skill obat/contract-check non disponible, skipped"

**Gate obat/impact-analysis :**
- Condition : le dossier `api-contracts/` existe
- Si condition remplie : invoquer le skill `/obat/impact-analysis`
- Si skill non disponible : afficher "⚠️ Skill obat/impact-analysis non disponible, skipped"

Si une gate strict échoue → STOPPER avec le message d'erreur.

## Étape 4 : Présenter les options

```
Vérifications terminées. Que souhaitez-vous faire ?

1. Créer une Merge Request
2. Garder la branche (je m'en occupe plus tard)
3. Abandonner ce travail
```

## Étape 5 : Exécuter le choix

### Option 1 : Créer une MR

**5.1 Demander le mode draft :**
```
Créer la MR en mode Draft ?
1. Oui (Draft - travail en cours)
2. Non (Prête pour review)
```

**5.2 Push la branche :**
```bash
git push -u origin <branch>
```

**5.3 Créer la MR via MCP gitlab-enhanced :**

Utiliser `mcp__gitlab-enhanced__create_merge_request` avec :
- `source_branch` : branche courante
- `target_branch` : `main` (ou `develop` selon le projet)
- `title` : Format convention commits
  - Si draft : `Draft: feat: #DEL-123 Description`
  - Si non-draft : `feat: #DEL-123 Description`
- `description` : Résumé des commits de la branche
  - Si `--skip-gates` utilisé, ajouter :
    ```
    ⚠️ **Quality gates bypassed**
    Justification : <justification fournie>
    ```

**5.4 Proposer transition Jira (si pas draft) :**

Si la MR n'est PAS en draft :
```
MR créée : <URL>

Voulez-vous passer le ticket <ID> en "In Review" ?
1. Oui
2. Non
```

Si oui :
1. `mcp__atlassian__jira_get_transitions` pour lister les transitions
2. Trouver celle vers "In Review" (ou équivalent)
3. `mcp__atlassian__jira_transition_issue` pour exécuter

Si draft → Ne pas proposer (travail pas prêt pour review)

**5.5 Proposer notification Slack (si MCP Slack disponible) :**

Vérifier si le MCP Slack est disponible. Si oui et si la MR n'est PAS en draft :

```
Voulez-vous être notifié sur Slack quand le pipeline passe ?
1. Oui (surveillance en background)
2. Non
```

Si "Oui" :
1. Lancer un agent en background avec le Task tool
2. L'agent fait un polling toutes les 30 secondes (max 15 minutes)
3. Récupère le statut du pipeline via `mcp__gitlab-enhanced__get_merge_request`
4. Si `success` → Envoyer MP Slack (voir ci-dessous)
5. Si `failed` → Envoyer MP Slack avec lien vers les logs
6. Si timeout (15 min) → Envoyer MP Slack "Pipeline toujours en cours"

**Message MP succès :**
```
✅ Pipeline OK !

MR !{mr_iid} - {mr_title}
→ {mr_web_url}

Lancez /notify-cr !{mr_iid} pour demander une review
```

**Message MP échec :**
```
❌ Pipeline failed

MR !{mr_iid} - {mr_title}
Étape échouée : {failed_job_name}

→ Voir les logs : {pipeline_web_url}
```

**Message MP timeout :**
```
⏳ Pipeline toujours en cours après 15 minutes

MR !{mr_iid} - {mr_title}

Utilisez /check-pipeline !{mr_iid} pour vérifier le statut
```

Si MCP Slack non disponible ou MR en draft → Ne pas proposer, continuer directement.

**5.6 Nettoyage worktree (si applicable) :**

Vérifier si on est dans un worktree :
```bash
git worktree list | grep $(git branch --show-current)
```

Si oui, proposer :
```
Voulez-vous supprimer le worktree ?
1. Oui
2. Non
```

### Option 2 : Garder la branche

Afficher : "Branche `<name>` conservée. Worktree préservé."

Ne rien faire.

### Option 3 : Abandonner

**Demander confirmation :**
```
Cela supprimera définitivement :
- Branche <name>
- Tous les commits non mergés
- Worktree (si applicable)

Tapez 'abandonner' pour confirmer.
```

Attendre la confirmation exacte.

Si confirmé :
```bash
git checkout main
git branch -D <branch>
```

Puis nettoyer le worktree si applicable.

## Résumé des flags

| Flag | Comportement |
|------|--------------|
| (aucun) | Gates de base auto-détectées, bloque si échec |
| `--strict` | Gates de base + contract-check + impact-analysis |
| `--skip-gates` | Bypass avec justification obligatoire |

## Conventions (contexte Obat)

Ces conventions s'appliquent uniquement si le contexte Obat est détecté.

### Commits
```
^(fixup! )?(?:tech|feat|doc|fix|hotfix|chore):\s#(?:[A-Z]+-)?\d+\s.*
```

Exemples valides :
- `feat: #DEL-123 Add user authentication`
- `fix: #OBAT-456 Fix login bug`
- `tech: #123 Refactor database layer`

### Branches
```
(feat|tech|fix|hotfix)/<PROJET>-<ID>
```

Exemples :
- `feat/DEL-123`
- `tech/DEL-456-refactor`
- `hotfix/OBAT-789`

### Hors contexte Obat

Pas de convention imposée pour les commits et branches.

## Prérequis

- MCP `gitlab-enhanced` configuré
- MCP `atlassian` (Jira) configuré
- Configuration utilisateur dans `~/.claude/config/obat-jira.yaml`
- MCP Slack configuré (optionnel, pour notifications pipeline)

## Erreurs courantes

**Continuer après échec de gate**
- Problème : Créer une MR avec du code cassé
- Solution : TOUJOURS stopper si une gate échoue

**Pas de justification pour skip-gates**
- Problème : Bypass sans trace
- Solution : Justification obligatoire, incluse dans la MR

**Pas de confirmation pour abandon**
- Problème : Supprimer du travail par accident
- Solution : Exiger "abandonner" tapé exactement

**Transition Jira sur draft**
- Problème : Mettre en review un travail pas fini
- Solution : Ne proposer la transition que si MR non-draft

## Intégration

**Appelé par :**
- `/execute-plan` - Après exécution complète d'un plan
- `/workflow` - Phase finale du cycle

**Fonctionne avec :**
- MCP `gitlab-enhanced` - Création des MR
- MCP `atlassian` - Transitions Jira
- `/obat/contract-check` - Gate strict (contexte Obat)
- `/obat/impact-analysis` - Gate strict (contexte Obat)
