---
name: worktrees
description: "Utiliser pour travailler sur plusieurs branches simultanément, changer de contexte sans stash, reviewer des MR pendant le développement, tester en isolation, ou comparer des implémentations entre branches - fournit les commandes git worktree et patterns de workflow pour le développement parallèle avec plusieurs répertoires de travail."
---

# Git Worktrees

## Vue d'ensemble

Les git worktrees permettent de checkout plusieurs branches simultanément dans des répertoires séparés, tous partageant le même dépôt. Créer un worktree au lieu de stasher les changements ou cloner séparément.

**Principe fondamental :** Un worktree par branche active. Changer de contexte en changeant de répertoire, pas de branche.

## Concepts clés

| Concept | Description |
|---------|-------------|
| **Worktree principal** | Répertoire de travail original issu de `git clone` ou `git init` |
| **Worktree lié** | Répertoires additionnels créés avec `git worktree add` |
| **`.git` partagé** | Tous les worktrees partagent la même base de données d'objets Git (pas de duplication) |
| **Verrou de branche** | Chaque branche ne peut être checkout que dans UN SEUL worktree à la fois |
| **Métadonnées worktree** | Fichiers administratifs dans `.git/worktrees/` qui tracent les worktrees liés |

## Référence rapide

| Tâche | Commande |
|-------|----------|
| Créer worktree (branche existante) | `git worktree add <chemin> <branche>` |
| Créer worktree (nouvelle branche) | `git worktree add -b <branche> <chemin>` |
| Créer worktree (nouvelle branche depuis ref) | `git worktree add -b <branche> <chemin> <start>` |
| Créer worktree détaché | `git worktree add --detach <chemin> <commit>` |
| Lister tous les worktrees | `git worktree list` |
| Supprimer worktree | `git worktree remove <chemin>` |
| Forcer suppression worktree | `git worktree remove --force <chemin>` |
| Déplacer worktree | `git worktree move <ancien> <nouveau>` |
| Verrouiller worktree | `git worktree lock <chemin>` |
| Déverrouiller worktree | `git worktree unlock <chemin>` |
| Nettoyer worktrees obsolètes | `git worktree prune` |
| Réparer liens worktree | `git worktree repair` |
| Comparer fichiers entre worktrees | `diff ../worktree-a/fichier ../worktree-b/fichier` |
| Récupérer un fichier d'une autre branche | `git checkout <branche> -- <chemin>` |
| Récupérer des changements partiels | `git checkout -p <branche> -- <chemin>` |
| Cherry-pick un commit | `git cherry-pick <commit>` |
| Cherry-pick sans commiter | `git cherry-pick --no-commit <commit>` |
| Merge sans auto-commit | `git merge --no-commit <branche>` |

## Commandes essentielles

### Créer un Worktree

```bash
# Créer worktree avec branche existante
git worktree add ../feature-x feature-x

# Créer worktree avec nouvelle branche depuis HEAD actuel
git worktree add -b new-feature ../new-feature

# Créer worktree avec nouvelle branche depuis un commit spécifique
git worktree add -b hotfix-123 ../hotfix origin/main

# Créer worktree trackant une branche remote
git worktree add --track -b feature ../feature origin/feature

# Créer worktree avec HEAD détaché (pour expérimentations)
git worktree add --detach ../experiment HEAD~5
```

### Lister les Worktrees

```bash
# Liste simple
git worktree list

# Sortie verbose avec détails additionnels
git worktree list -v

# Format machine-readable (pour scripting)
git worktree list --porcelain
```

**Exemple de sortie :**

```
/home/user/projet           abc1234 [main]
/home/user/projet-feature   def5678 [feature-x]
/home/user/projet-hotfix    ghi9012 [hotfix-123]
```

### Supprimer un Worktree

```bash
# Supprimer worktree (le répertoire de travail doit être propre)
git worktree remove ../feature-x

# Forcer la suppression (abandonne les changements non commités)
git worktree remove --force ../feature-x
```

### Déplacer un Worktree

```bash
# Relocaliser worktree vers un nouveau chemin
git worktree move ../ancien-chemin ../nouveau-chemin
```

### Verrouiller/Déverrouiller les Worktrees

```bash
# Verrouiller worktree (empêche le pruning si sur stockage amovible)
git worktree lock ../feature-x
git worktree lock --reason "Sur clé USB" ../feature-x

# Déverrouiller worktree
git worktree unlock ../feature-x
```

### Nettoyer les Worktrees obsolètes

```bash
# Supprimer les métadonnées de worktree obsolètes (après suppression manuelle du répertoire)
git worktree prune

# Dry-run pour voir ce qui serait nettoyé
git worktree prune --dry-run

# Sortie verbose
git worktree prune -v
```

### Réparer les Worktrees

```bash
# Réparer les liens worktree après déplacement manuel des répertoires
git worktree repair

# Réparer un worktree spécifique
git worktree repair ../feature-x
```

## Patterns de workflow

### Pattern 1 : Feature + Hotfix en parallèle

Pour corriger un bug pendant qu'un travail de feature est en cours :

```bash
# Créer worktree pour hotfix depuis main
git worktree add -b hotfix-456 ../projet-hotfix origin/main

# Aller dans le répertoire hotfix, corriger, commiter, pusher
cd ../projet-hotfix
git add . && git commit -m "fix: résoudre bug critique #456"
git push origin hotfix-456

# Retourner au travail de feature
cd ../projet

# Nettoyer quand terminé
git worktree remove ../projet-hotfix
```

### Pattern 2 : Review de MR pendant le travail

Pour reviewer une MR sans affecter le travail en cours :

```bash
# Fetch la branche MR et créer worktree
git fetch origin merge-requests/123/head:mr-123
git worktree add ../projet-review mr-123

# Review : exécuter les tests, inspecter le code
cd ../projet-review

# Retourner au travail, puis nettoyer
cd ../projet
git worktree remove ../projet-review
git branch -d mr-123
```

### Pattern 3 : Comparer des implémentations

Pour comparer du code entre branches côte à côte :

```bash
# Créer worktrees pour différentes versions
git worktree add ../projet-v1 v1.0.0
git worktree add ../projet-v2 v2.0.0

# Diff, comparer, ou exécuter les deux simultanément
diff ../projet-v1/src/module.js ../projet-v2/src/module.js

# Nettoyer
git worktree remove ../projet-v1
git worktree remove ../projet-v2
```

### Pattern 4 : Tâches longues

Pour exécuter des tests/builds en isolation pendant qu'on continue le développement :

```bash
# Créer worktree pour tests type CI
git worktree add ../projet-test main

# Démarrer les tests longs en arrière-plan
cd ../projet-test && npm test &

# Continuer le développement dans le worktree principal
cd ../projet
```

### Pattern 5 : Référence stable

Pour maintenir un checkout main propre comme référence :

```bash
# Créer worktree permanent pour la branche main
git worktree add ../projet-main main

# Verrouiller pour éviter suppression accidentelle
git worktree lock --reason "Checkout de référence" ../projet-main
```

### Pattern 6 : Merge sélectif depuis plusieurs features

Pour combiner des changements spécifiques de plusieurs branches feature :

```bash
# Créer worktrees pour chaque feature à reviewer
git worktree add ../projet-feature-1 feature-1
git worktree add ../projet-feature-2 feature-2

# Reviewer les changements dans chaque worktree
diff ../projet/src/module.js ../projet-feature-1/src/module.js
diff ../projet/src/module.js ../projet-feature-2/src/module.js

# Depuis le worktree principal, prendre sélectivement les changements
cd ../projet
git checkout feature-1 -- src/moduleA.js src/utils.js
git checkout feature-2 -- src/moduleB.js
git commit -m "feat: combiner changements sélectionnés des branches feature"

# Ou cherry-pick des commits spécifiques
git cherry-pick abc1234  # de feature-1
git cherry-pick def5678  # de feature-2

# Nettoyer
git worktree remove ../projet-feature-1
git worktree remove ../projet-feature-2
```

## Comparer et merger des changements entre Worktrees

Comme tous les worktrees partagent le même dépôt Git, on peut comparer des fichiers, cherry-pick des commits, et merger sélectivement des changements entre eux.

### Comparer et reviewer les changements de fichiers

Comme les worktrees sont juste des répertoires, on peut comparer les fichiers directement :

```bash
# Comparer un fichier spécifique entre worktrees
diff ../projet-main/src/app.js ../projet-feature/src/app.js

# Utiliser git diff pour comparer les branches (fonctionne depuis n'importe quel worktree)
git diff main..feature-branch -- src/app.js

# Diff visuel avec l'outil préféré
code --diff ../projet-main/src/app.js ../projet-feature/src/app.js

# Comparer des répertoires entiers
diff -r ../projet-v1/src ../projet-v2/src
```

### Merger un seul fichier depuis un Worktree

On peut sélectivement récupérer un seul fichier d'une autre branche avec `git checkout` :

```bash
# Dans la branche courante, récupérer un fichier spécifique d'une autre branche
git checkout feature-branch -- chemin/vers/fichier.js

# Ou le récupérer depuis un commit spécifique
git checkout abc1234 -- chemin/vers/fichier.js

# Récupérer plusieurs fichiers spécifiques
git checkout feature-branch -- src/module.js src/utils.js
```

Pour des **changements partiels de fichier** (hunks/lignes spécifiques seulement) :

```bash
# Mode patch interactif - sélectionner quels changements prendre
git checkout -p feature-branch -- chemin/vers/fichier.js
```

Cela demande d'accepter/rejeter chaque hunk de changement individuellement avec les options :
- `y` - appliquer ce hunk
- `n` - sauter ce hunk
- `s` - diviser en hunks plus petits
- `e` - éditer manuellement le hunk

### Cherry-Pick de commits depuis les Worktrees

Le cherry-picking fonctionne au niveau des commits. Comme tous les worktrees partagent le même dépôt, on peut cherry-pick n'importe quel commit :

```bash
# Trouver le hash du commit (depuis n'importe quel worktree ou git log)
git log feature-branch --oneline

# Cherry-pick un commit spécifique dans la branche courante
git cherry-pick abc1234

# Cherry-pick plusieurs commits
git cherry-pick abc1234 def5678

# Cherry-pick une plage de commits
git cherry-pick abc1234^..def5678

# Cherry-pick sans commiter (stage les changements seulement)
git cherry-pick --no-commit abc1234
```

### Merger des changements de plusieurs Worktrees

On peut merger ou cherry-pick depuis plusieurs branches :

```bash
# Merger plusieurs branches séquentiellement
git merge feature-1
git merge feature-2

# Ou utiliser octopus merge pour plusieurs branches à la fois
git merge feature-1 feature-2 feature-3

# Cherry-pick des commits de plusieurs branches
git cherry-pick abc1234  # de feature-1
git cherry-pick def5678  # de feature-2
```

### Merge sélectif - Choisir quels changements inclure

#### Option 1 : Checkout sélectif de fichiers

```bash
# Récupérer des fichiers spécifiques de différentes branches
git checkout feature-1 -- src/moduleA.js
git checkout feature-2 -- src/moduleB.js
git commit -m "Merger fichiers sélectionnés des branches feature"
```

#### Option 2 : Sélection interactive de patch

```bash
# Sélectionner des hunks spécifiques d'un fichier
git checkout -p feature-1 -- src/shared.js
```

#### Option 3 : Cherry-Pick avec staging sélectif

```bash
# Appliquer les changements sans commiter
git cherry-pick --no-commit abc1234

# Unstage ce qu'on ne veut pas
git reset HEAD -- fichier-non-voulu.js
git checkout -- fichier-non-voulu.js

# Commiter seulement ce qu'on a gardé
git commit -m "Changements sélectionnés de feature-1"
```

#### Option 4 : Merge avec sélection manuelle

```bash
# Démarrer le merge mais ne pas auto-commiter
git merge --no-commit feature-1

# Reviewer et modifier les changements stagés
git status
git reset HEAD -- fichier-a-exclure.js
git checkout -- fichier-a-exclure.js

# Commiter la sélection
git commit -m "Merger changements sélectionnés de feature-1"
```

#### Option 5 : Utiliser git restore (Git 2.23+)

```bash
# Restaurer un fichier spécifique depuis une autre branche
git restore --source=feature-branch -- chemin/vers/fichier.js

# Restauration interactive avec sélection de patch
git restore -p --source=feature-branch -- chemin/vers/fichier.js
```

## Conventions de structure de répertoires

Organiser les worktrees de manière prévisible :

```
~/projets/
  mon-projet/              # Worktree principal (branche main/master)
  mon-projet-feature-x/    # Worktree branche feature
  mon-projet-hotfix/       # Worktree hotfix
  mon-projet-review/       # Worktree temporaire pour review MR
```

**Convention de nommage :** `<projet>-<but>` ou `<projet>-<branche>`

## Bonnes pratiques

| Pratique | Justification |
|----------|---------------|
| **Utiliser des répertoires frères** | Garder les worktrees au même niveau que le projet principal pour une navigation facile |
| **Nommer par but** | `projet-review` est plus clair que `projet-mr-123` |
| **Nettoyer rapidement** | Supprimer les worktrees quand terminé pour éviter la confusion |
| **Verrouiller les worktrees distants** | Éviter le pruning si le worktree est sur stockage réseau/USB |
| **Utiliser `--detach` pour les expérimentations** | Éviter de créer des branches jetables |
| **Commiter avant de supprimer** | Toujours commiter ou stasher avant `git worktree remove` |

## Problèmes courants et solutions

### Problème : "Branch is already checked out"

**Cause :** Tentative de checkout d'une branche active dans un autre worktree.

**Solution :**

```bash
# Trouver où la branche est checkout
git worktree list

# Soit travailler dans ce worktree, soit le supprimer d'abord
git worktree remove ../autre-worktree
```

### Problème : Worktree obsolète après suppression manuelle

**Cause :** Suppression du répertoire worktree sans utiliser `git worktree remove`.

**Solution :**

```bash
# Nettoyer les métadonnées obsolètes
git worktree prune
```

### Problème : Worktree déplacé manuellement

**Cause :** Déplacement du répertoire worktree sans utiliser `git worktree move`.

**Solution :**

```bash
# Réparer les liens worktree
git worktree repair
# Ou spécifier le nouveau chemin
git worktree repair /nouveau/chemin/vers/worktree
```

### Problème : Worktree sur disque retiré

**Cause :** Le worktree était sur un stockage amovible qui n'est plus connecté.

**Solution :**

```bash
# Si temporaire, le verrouiller pour éviter le pruning
git worktree lock ../usb-worktree

# Si permanent, le pruner
git worktree prune
```

## Erreurs courantes

| Erreur | Correction |
|--------|------------|
| Utiliser `rm -rf` pour supprimer un worktree | Toujours utiliser `git worktree remove`, puis `git worktree prune` si nécessaire |
| Oublier qu'une branche est verrouillée à un worktree | Exécuter `git worktree list` avant les erreurs de checkout |
| Ne pas nettoyer les worktrees temporaires | Supprimer les worktrees immédiatement après complétion de la tâche |
| Créer des worktrees dans des emplacements imbriqués | Utiliser des répertoires frères (`../projet-feature`) pas des sous-répertoires |
| Déplacer manuellement le répertoire worktree | Utiliser `git worktree move` ou exécuter `git worktree repair` après |

## Intégration workflow Agent

Pour isoler des tâches d'agent parallèles :

```bash
# Créer worktree pour tâche isolée
git worktree add -b task-123 ../projet-task-123
cd ../projet-task-123
# Faire les changements, exécuter les tests, retourner
cd ../projet
```

Pour expérimenter en sécurité avec HEAD détaché :

```bash
# Créer worktree détaché (pas de branche à nettoyer)
git worktree add --detach ../projet-experiment
cd ../projet-experiment
# Expérimenter, puis abandonner ou commiter sur nouvelle branche
git worktree remove --force ../projet-experiment
```

## Checklist de vérification

Avant d'utiliser les worktrees :

- [ ] Comprendre que les branches ne peuvent être checkout que dans un seul worktree
- [ ] Savoir où les worktrees seront créés (utiliser des répertoires frères)
- [ ] Planifier la stratégie de nettoyage pour les worktrees temporaires

Lors de la création de worktrees :

- [ ] Utiliser des noms de répertoires descriptifs
- [ ] Vérifier que la branche n'est pas déjà checkout ailleurs
- [ ] Considérer l'utilisation de `--detach` pour les expérimentations

Lors de la suppression de worktrees :

- [ ] Commiter ou stasher tous les changements non commités
- [ ] Utiliser `git worktree remove`, pas `rm -rf`
- [ ] Exécuter `git worktree prune` si le répertoire a été supprimé manuellement
