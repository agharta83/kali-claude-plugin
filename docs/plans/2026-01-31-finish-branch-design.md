# Finish Branch Skill - Design

**Date :** 2026-01-31
**Statut :** Validé

## Objectif

Finaliser une branche de développement selon le workflow Obat : vérifier les tests et outils qualité, créer une MR GitLab, et proposer la transition Jira vers "In Review".

## Différences avec le skill original

| Aspect | Original (superpowers) | Adapté (Obat) |
|--------|------------------------|---------------|
| Git hosting | GitHub (`gh`) | GitLab (MCP `gitlab-enhanced`) |
| Options | 4 (merge local, PR, keep, discard) | 3 (MR, keep, discard) |
| Vérifications | Tests génériques | make test/phpstan/fix-cs/rector/deptrac |
| Intégration | Aucune | Jira (transition "In Review") |
| Conventions | Libres | Commits et branches normés |

## Conventions Obat

**Commits :**
```
^(fixup! )?(?:tech|feat|doc|fix|hotfix|chore):\s#(?:[A-Z]+-)?\d+\s.*
```
Exemple : `feat: #DEL-123 Add user authentication`

**Branches :**
```
(feat|tech|fix|hotfix)/DEL-XXXX
```
Exemple : `feat/DEL-123`

## Flux du skill

```
1. Vérifier qu'on est sur une branche feature (pas main/develop)
2. Extraire l'ID Jira depuis le nom de branche (ex: feat/DEL-123 → DEL-123)
3. Détecter le type de projet (Makefile + composer.json = PHP backend)
4. Exécuter les vérifications :
   - make test
   - make phpstan
   - make fix-cs
   - make rector
   - make deptrac
5. Si échec → afficher erreur, stopper
6. Présenter les options :
   1. Créer une MR
   2. Garder la branche (je m'en occupe plus tard)
   3. Abandonner
7. Exécuter le choix
```

## Option 1 : Créer une MR

**Demander le mode draft :**
```
Créer la MR en mode Draft ?
1. Oui (Draft - travail en cours)
2. Non (Prête pour review)
```

**Étapes :**
1. Push la branche : `git push -u origin <branch>`
2. Créer MR via `mcp__gitlab-enhanced__create_merge_request` :
   - `source_branch` : branche courante
   - `target_branch` : main (ou develop)
   - `title` : `Draft: type: #PROJET-XXX Description` si draft, sinon `type: #PROJET-XXX Description`
   - `description` : résumé des commits
   - `draft` : true/false selon choix utilisateur
3. Proposer transition Jira (seulement si pas draft) :
   ```
   MR créée : https://gitlab.obat.fr/...

   Voulez-vous passer le ticket DEL-123 en "In Review" ?
   1. Oui
   2. Non
   ```
   Note : Si MR en draft, ne pas proposer la transition (travail pas prêt pour review).
4. Si oui :
   - `mcp__atlassian__jira_get_transitions` pour trouver la transition
   - `mcp__atlassian__jira_transition_issue` pour l'exécuter
5. Nettoyer worktree si applicable

## Option 2 : Garder la branche

Afficher : "Branche conservée. Worktree préservé."

Ne rien faire.

## Option 3 : Abandonner

**Avec confirmation :**
```
Cela supprimera définitivement :
- Branche feat/DEL-123
- Tous les commits non mergés
- Worktree (si applicable)

Tapez 'abandonner' pour confirmer.
```

Si confirmé :
1. `git checkout main`
2. `git branch -D <branch>`
3. Nettoyer worktree si applicable

## Vérifications backend PHP

**Détection :** `Makefile` + `composer.json` présents

**Commandes :**
```bash
make test       # Tests PHPUnit
make phpstan    # Analyse statique
make fix-cs     # Code style (PHP CS Fixer)
make rector     # Refactoring automatique
make deptrac    # Vérification des dépendances
```

**Affichage :**
```
Vérifications en cours...
✓ Tests PHPUnit
✓ PHPStan
✓ PHP CS Fixer
✓ Rector
✓ Deptrac

Toutes les vérifications passent.
```

## Nettoyage worktree

Si on est dans un worktree (`git worktree list`) :
- **Option MR** : proposer de supprimer le worktree après création
- **Option Abandonner** : supprimer le worktree
- **Option Garder** : ne rien faire

## Prérequis

- MCP `gitlab-enhanced` configuré
- MCP `atlassian` (Jira) configuré
- Configuration utilisateur dans `~/.claude/config/obat-jira.yaml`

## Évolutions futures

Voir [IDEA.md](../../IDEA.md) :
- Notification Slack après succès pipeline
