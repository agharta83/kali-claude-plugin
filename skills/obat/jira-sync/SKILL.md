---
name: obat/jira-sync
description: "Synchronise un document de design vers Jira - crée les nouveaux tickets et applique les modifications depuis la section Suggestions Jira"
---

# Synchronisation vers Jira

## Prérequis : Contexte Obat

Ce skill nécessite un contexte Obat. Vérifier :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

Si hors contexte Obat → Afficher :
```
⚠️ Ce skill nécessite un contexte Obat (remote gitlab.obat.fr).
   Utilisez --obat pour forcer l'exécution.
```

Si `--obat` fourni → Continuer malgré l'absence de contexte.

---

## Vue d'ensemble

Lit un document de design généré par jira-brainstorming et synchronise les suggestions vers Jira : création de nouveaux tickets et modifications des tickets existants.

## Usage

```
/jira-sync                    # Sync le dernier design doc Jira trouvé
/jira-sync OBAT-123          # Sync le design doc docs/plans/OBAT-123-design.md
/jira-sync --dry-run         # Prévisualise sans créer/modifier
```

## Phase 1 : Localisation du document

1. Si un ID est fourni : chercher `docs/plans/<ID>-design.md`
2. Sinon : trouver le design doc Jira le plus récent dans `docs/plans/`
3. Si aucun trouvé : informer l'utilisateur

## Phase 2 : Parsing du document

Extraire du frontmatter YAML :
- `jira.source_ticket` : ticket de référence
- `jira.project` : projet cible
- `jira.default_assignee`, `jira.priority`, etc.

Parser la section `## Suggestions Jira` :
- Identifier les blocs `### Nouveaux tickets à créer`
- Identifier les blocs `### Modifications suggérées`

## Phase 3 : Validation

Vérifier via MCP Jira :
- Le projet existe et est accessible
- Les tickets parents référencés existent
- L'utilisateur a les permissions de création

## Phase 4 : Prévisualisation

Afficher un résumé des actions :

```
📋 Actions prévues pour OBAT-123-design.md :

CRÉATIONS :
  ├── [Story] Implémenter le refresh token
  │   └── Parent: OBAT-123
  │   └── Story points: 3
  ├── [Task] Créer le service TokenRefreshService
  │   └── Parent: (story ci-dessus)

MODIFICATIONS :
  └── OBAT-124 - Configurer provider
      └── Ajouter acceptance criteria (1 item)

Confirmer ? [o/N]
```

Si `--dry-run` : s'arrêter ici.

## Phase 5 : Exécution

Pour chaque nouveau ticket :
1. Utiliser `mcp__atlassian__jira_create_issue`
2. Stocker l'ID créé pour les références parent
3. Si le parent est "(story ci-dessus)", utiliser l'ID créé à l'étape précédente

Pour chaque modification :
1. Utiliser `mcp__atlassian__jira_get_issue` pour récupérer l'état actuel
2. Merger les modifications (append, pas replace)
3. Utiliser `mcp__atlassian__jira_update_issue`

## Phase 6 : Mise à jour du document

Après création réussie, mettre à jour le design doc :

```markdown
#### [Story] Implémenter le refresh token
- ✅ **Créé:** OBAT-150
- **Parent:** OBAT-123
...
```

Ajouter en bas du document :

```markdown
---
## Historique de synchronisation

- **2026-01-30 14:30** : Créé OBAT-150, OBAT-151. Modifié OBAT-124.
```

## Gestion des erreurs

- **Permission refusée** : Lister les tickets non créés, suggérer de contacter l'admin
- **Ticket parent inexistant** : Proposer de créer sous un autre parent ou skip
- **Champ requis manquant** : Demander la valeur à l'utilisateur

## Rollback

Ce skill ne supprime jamais de tickets. En cas d'erreur partielle :
- Les tickets créés restent dans Jira
- Le document est mis à jour avec les IDs créés
- Les tickets non créés restent marqués sans checkmark
