---
name: setup-worktree
description: "Crée un worktree isolé pour le développement. Utilisé par /execute-plan --worktree ou directement."
---

# Setup Worktree

Crée un worktree Git isolé pour travailler sur une feature sans affecter le workspace principal.

**Principe :** Sélection du répertoire + vérification sécurité + création branche

**Annonce au démarrage :** "Je crée un worktree isolé pour cette implémentation."

## Détection du contexte

Détecter si on est dans un contexte Obat :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

| Contexte | Comportement |
|----------|--------------|
| Obat détecté | Conventions Obat pour le nom de branche (`type/PROJET-ID`) |
| Hors Obat | Format libre, demande un nom de branche |
| `--obat` flag | Forcer les conventions Obat |
| `--no-obat` flag | Forcer le format libre |

## Étape 1 : Collecter les informations

### Mode Obat (contexte détecté ou `--obat`)

**Demander l'ID Jira :**
```
Quel est l'ID du ticket Jira ? (ex: DEL-123)
```

**Demander le type de branche :**
```
Quel type de branche ?
1. feat (nouvelle fonctionnalité)
2. tech (refactoring, dette technique)
3. fix (correction de bug)
4. hotfix (correction urgente)
```

**Demander une description courte (optionnel) :**
```
Description courte pour la branche ? (optionnel, ex: "auth-flow")
Appuyez sur Entrée pour ignorer.
```

### Mode générique (hors Obat)

**Demander le nom de branche :**
```
Nom de la branche à créer ? (ex: feature/my-feature)
```

## Étape 2 : Construire le nom de branche

### Mode Obat

**Format :**
```
<type>/<PROJET>-<ID>[-description]
```

**Exemples :**
- `feat/DEL-123`
- `feat/DEL-123-auth-flow`
- `tech/OBAT-456-refactor-db`
- `fix/DEL-789-login-bug`

### Mode générique

Utiliser directement le nom de branche fourni par l'utilisateur.

## Étape 3 : Sélectionner le répertoire worktree

**Ordre de priorité :**

### 1. Vérifier les répertoires existants

```bash
ls -d .worktrees 2>/dev/null     # Préféré (caché)
ls -d worktrees 2>/dev/null      # Alternative
```

Si trouvé : Utiliser ce répertoire. Si les deux existent, `.worktrees` gagne.

### 2. Vérifier CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

Si préférence spécifiée : L'utiliser sans demander.

### 3. Demander à l'utilisateur

```
Aucun répertoire worktree trouvé. Où créer les worktrees ?

1. .worktrees/ (local au projet, caché)
2. ~/worktrees/<nom-projet>/ (global)
```

## Étape 4 : Vérification sécurité

**Pour les répertoires locaux (.worktrees ou worktrees) :**

Vérifier que le répertoire est ignoré par git :

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**Si NON ignoré :**
1. Ajouter au .gitignore
2. Commiter le changement
3. Continuer

**Pourquoi :** Évite de commiter accidentellement le contenu du worktree.

## Étape 5 : Créer le worktree

```bash
# Déterminer le chemin complet
project=$(basename "$(git rev-parse --show-toplevel)")

case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/worktrees/*)
    path="~/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# Créer le worktree avec nouvelle branche
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

## Étape 6 : Setup projet (backend PHP)

**Détection :** Si `Makefile` + `composer.json` présents

```bash
# Installer les dépendances
make install  # ou composer install

# Vérifier que tout fonctionne
make test
```

**Autres projets :**
```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```

## Étape 7 : Vérifier le baseline

Exécuter les tests pour s'assurer que le worktree démarre propre :

```bash
# Backend PHP
make test && make phpstan
```

**Si les tests échouent :** Signaler et demander si on continue.

**Si les tests passent :** Signaler prêt.

## Étape 8 : Rapport

```
Worktree prêt !
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chemin : /home/user/projet/.worktrees/feat/DEL-123-auth
Branche : feat/DEL-123-auth
Tests : ✓ (47 tests, 0 échecs)

Prêt pour l'implémentation.
```

## Conventions de nommage

### Contexte Obat

| Type | Pattern | Exemple |
|------|---------|---------|
| Feature | `feat/<PROJET>-<ID>[-desc]` | `feat/DEL-123-auth` |
| Tech | `tech/<PROJET>-<ID>[-desc]` | `tech/DEL-456-refactor` |
| Fix | `fix/<PROJET>-<ID>[-desc]` | `fix/DEL-789-login` |
| Hotfix | `hotfix/<PROJET>-<ID>[-desc]` | `hotfix/OBAT-101-crash` |

### Hors contexte Obat

Pas de convention imposée. Exemples courants :
- `feature/my-feature`
- `bugfix/fix-login`
- `refactor/clean-db`

### Worktrees

Le worktree est créé avec le même nom que la branche :
```
.worktrees/feat/DEL-123-auth/   # Obat
.worktrees/feature/my-feature/  # Générique
```

## Référence rapide

| Situation | Action |
|-----------|--------|
| `.worktrees/` existe | L'utiliser (vérifier ignoré) |
| `worktrees/` existe | L'utiliser (vérifier ignoré) |
| Les deux existent | Utiliser `.worktrees/` |
| Aucun n'existe | Vérifier CLAUDE.md → Demander |
| Répertoire non ignoré | Ajouter au .gitignore + commit |
| Tests échouent au baseline | Signaler + demander |

## Erreurs courantes

**Sauter la vérification gitignore**
- Problème : Le contenu du worktree est tracké, pollue git status
- Solution : Toujours `git check-ignore` avant création

**Nom de branche invalide**
- Problème : Ne respecte pas la convention Obat
- Solution : Valider le format `type/PROJET-ID[-desc]`

**Continuer avec des tests qui échouent**
- Problème : On ne peut pas distinguer nouveaux bugs des pré-existants
- Solution : Signaler les échecs, demander permission explicite

## Intégration

**Appelé par :**
- `/execute-plan --worktree` - Avant d'exécuter un plan
- `/brainstorm` - Après validation du design (optionnel)
- `/subagent-driven-development` - Avant d'éxécuter des taches

**Fonctionne avec :**
- `/finish-branch` - Nettoie le worktree après le travail
- `/execute-plan` - Le travail se fait dans ce worktree
