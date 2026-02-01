---
name: notify-cr
description: "Poste une demande de code review dans Slack et fait la transition Jira."
---

# Notify CR

Poste une demande de code review dans le channel Slack configuré et fait la transition Jira vers "Code Review".

**Annonce au démarrage :** "Je prépare la notification de code review."

## Usage

```bash
/notify-cr !123        # Par numéro de MR
/notify-cr DEL-456     # Par ID Jira
```

## Étape 1 : Vérifier la configuration Slack

Vérifier que le MCP Slack est disponible.

Si non disponible :
```
❌ MCP Slack non configuré

Pour activer les notifications Slack, voir le README :
1. Installer un MCP Slack
2. Créer ~/.claude/config/obat-slack.yaml
3. Configurer le channel dans config/plugin-config.yaml
```

Stopper.

## Étape 2 : Charger la configuration

Charger `config/plugin-config.yaml` pour récupérer :
- `slack.code_review_channel`
- `slack.cr_messages`
- `slack.jokes`

Charger `~/.claude/config/obat-slack.yaml` pour récupérer :
- `slack.user_id`

Si `code_review_channel` absent → Erreur : "Channel Slack non configuré dans plugin-config.yaml"

## Étape 3 : Parser l'argument et récupérer la MR

Même logique que `/check-pipeline` (Étapes 1 et 2).

Extraire de la MR :
- `iid` : numéro de MR
- `title` : titre de la MR
- `web_url` : URL de la MR
- `head_pipeline.status` : statut du pipeline

## Étape 4 : Vérifier le statut du pipeline

Si `head_pipeline.status` n'est pas `success` :

```
⚠️ Le pipeline de la MR !{mr_iid} n'est pas encore passé (status: {status})

Voulez-vous quand même demander une review ?
1. Oui (poster quand même)
2. Non (attendre)
```

Si "Non" → Stopper.

## Étape 5 : Extraire l'ID Jira

Pattern : `#([A-Z]+-\d+)` dans le titre de la MR.

Exemple : `feat: #DEL-456 Add login` → `DEL-456`

Si pas d'ID trouvé → Continuer sans transition Jira.

## Étape 6 : Construire le message Slack

1. Choisir un template aléatoire parmi `slack.cr_messages`
2. Remplacer les placeholders :
   - `{mr_id}` → numéro de MR
   - `{title}` → titre de la MR
   - `{url}` → URL de la MR
3. Avec 20% de chance, ajouter une blague aléatoire de `slack.jokes`

## Étape 7 : Poster dans Slack

Utiliser le MCP Slack pour poster le message dans `slack.code_review_channel`.

## Étape 8 : Transition Jira (si ID trouvé)

Si un ID Jira a été extrait :

1. `mcp__atlassian__jira_get_transitions` pour lister les transitions disponibles
2. Chercher une transition vers "Code Review" ou "In Review" (insensible à la casse)
3. Si trouvée → `mcp__atlassian__jira_transition_issue`
4. Si non trouvée → Afficher un warning mais continuer

## Étape 9 : Afficher le résumé

```
✅ Demande de CR envoyée !

Slack : Message posté dans #code-reviews
Jira  : {JIRA-ID} → Code Review

Bonne review ! 🤞
```

Ou si pas de Jira :

```
✅ Demande de CR envoyée !

Slack : Message posté dans #code-reviews

Bonne review ! 🤞
```

## Prérequis

- MCP `gitlab-enhanced` configuré
- MCP Slack configuré (niveau utilisateur)
- MCP `atlassian` configuré (pour transition Jira)
- Configuration dans `config/plugin-config.yaml` et `~/.claude/config/obat-slack.yaml`

## Erreurs courantes

**MCP Slack non configuré**
- Problème : Aucun MCP Slack disponible
- Solution : Installer et configurer un MCP Slack

**Channel non configuré**
- Problème : `slack.code_review_channel` absent
- Solution : Ajouter dans `config/plugin-config.yaml`

**Transition Jira non trouvée**
- Problème : Pas de transition vers "Code Review"
- Solution : Vérifier le workflow Jira du projet
