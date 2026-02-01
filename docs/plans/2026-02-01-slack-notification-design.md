# Design : Notification Slack après succès pipeline

**Date :** 2026-02-01
**Statut :** Validé

## Objectif

Notifier sur Slack quand un pipeline GitLab passe, pour faciliter les demandes de code review.

## Composants

- **Modification de `/finish-branch`** - Propose de surveiller le pipeline après création MR
- **Nouveau skill `/check-pipeline`** - Vérifie le statut d'un pipeline et notifie en MP
- **Nouveau skill `/notify-cr`** - Poste une demande de CR dans le channel + transition Jira

## Flow utilisateur

```
/finish-branch
    ↓
MR créée → "Voulez-vous être notifié quand le pipeline passe ?"
    ↓ (oui)
Agent background surveille le pipeline (polling 30s, max 15min)
    ↓ (succès)
MP Slack → "✅ Pipeline OK pour MR !123 - feat: #DEL-456 Add login"
    ↓
/notify-cr !123
    ↓
1. Message dans #code-reviews (aléatoire + blague 20%)
2. Transition Jira DEL-456 → "Code Review"
```

## Configuration

### `config/plugin-config.yaml`

```yaml
slack:
  # Channel pour les demandes de code review
  code_review_channel: "#code-reviews"

  # Blagues optionnelles (20% de chance d'apparaître)
  jokes:
    - "Je promets qu'il n'y a que 2 fichiers changés... par commit 😅"
    - "J'ai écrit des tests, je le jure 🤞"
    - "Pas de force push cette fois, promis"
    - "Le code est auto-documenté (dit-il, confiant)"
    - "Fonctionne sur ma machine ™️"
```

### `~/.claude/config/obat-slack.yaml` (niveau user)

```yaml
slack:
  # ID Slack de l'utilisateur pour les MP
  user_id: "U1234567890"
```

## Skill `/check-pipeline`

**Fichier :** `skills/check-pipeline/SKILL.md`

**Usage :**
```bash
/check-pipeline !123        # Par numéro de MR
/check-pipeline DEL-456     # Par ID Jira (trouve la MR associée)
```

**Comportement :**

1. Récupérer la MR via MCP gitlab-enhanced
2. Récupérer le statut du pipeline
3. Afficher le résultat

**Outputs possibles :**

```
Pipeline MR !123 : ✅ success
  feat: #DEL-456 Add login
  Durée: 4m32s

→ Vous pouvez lancer /notify-cr !123 pour demander une review
```

```
Pipeline MR !123 : 🔄 running (étape: test)
  feat: #DEL-456 Add login

→ Relancez /check-pipeline !123 dans quelques minutes
```

```
Pipeline MR !123 : ❌ failed (étape: phpstan)
  feat: #DEL-456 Add login

→ Voir les logs : gitlab.com/.../pipelines/789
```

## Skill `/notify-cr`

**Fichier :** `skills/notify-cr/SKILL.md`

**Usage :**
```bash
/notify-cr !123        # Par numéro de MR
/notify-cr DEL-456     # Par ID Jira
```

**Comportement :**

1. Récupérer la MR via MCP gitlab-enhanced
2. Extraire l'ID Jira du titre (pattern `#[A-Z]+-\d+`)
3. Poster dans le channel Slack (message aléatoire + blague 20% du temps)
4. Si ID Jira trouvé → transition vers "Code Review" via MCP Jira
5. Afficher le résumé

**Messages Slack (aléatoire) :**

```
👀 Qui veut review ma MR ?
feat: #DEL-456 Add login
→ gitlab.com/...
```

```
🎯 CR disponible !
MR !123 - feat: #DEL-456 Add login
Premier arrivé, premier servi 🏃
→ gitlab.com/...
```

```
🚀 Pipeline vert, MR prête !
✨ feat: #DEL-456 Add login
🔗 gitlab.com/...
Merci d'avance ! 🙏
```

```
☕ Une petite review ?
MR !123 - feat: #DEL-456 Add login
→ gitlab.com/...
```

**Output console :**

```
✅ Demande de CR envoyée !

Slack : Message posté dans #code-reviews
Jira  : DEL-456 → Code Review

Bonne review ! 🤞
```

**Si pipeline pas encore vert :**

```
⚠️ Le pipeline de la MR !123 n'est pas encore passé (status: running)

Voulez-vous quand même demander une review ?
1. Oui (poster quand même)
2. Non (attendre)
```

## Modification de `/finish-branch`

**Ajout après création de MR (non-draft) :**

Après l'étape 5.3 (création MR), ajouter :

```
MR créée : gitlab.com/.../merge_requests/123

Voulez-vous être notifié sur Slack quand le pipeline passe ?
1. Oui (surveillance en background)
2. Non
```

**Si oui :**
- Lancer un agent en background via `Task` tool
- Polling toutes les 30 secondes (max 15 minutes)
- Si succès → MP Slack à l'utilisateur
- Si échec → MP Slack avec le lien vers les logs
- Si timeout → MP Slack "Pipeline toujours en cours, utilisez /check-pipeline !123"

**Message MP succès :**

```
✅ Pipeline OK !

MR !123 - feat: #DEL-456 Add login
→ gitlab.com/.../merge_requests/123

Lancez /notify-cr !123 pour demander une review
```

**Message MP échec :**

```
❌ Pipeline failed

MR !123 - feat: #DEL-456 Add login
Étape échouée : phpstan

→ Voir les logs : gitlab.com/.../pipelines/789
```

## Prérequis

### MCP Slack (niveau utilisateur)

1. Installer un MCP Slack (ex: `@anthropic/mcp-slack`)
2. Configurer dans `~/.claude/settings.json`
3. Créer `~/.claude/config/obat-slack.yaml` avec `user_id`
4. Configurer le channel dans `config/plugin-config.yaml`

Pour trouver l'ID Slack : Profil → ⋮ → Copy member ID

### Gestion si MCP Slack non configuré

- Dans `/finish-branch` : ne pas proposer la surveillance, continuer normalement
- Dans `/notify-cr` et `/check-pipeline` : erreur explicite avec lien vers README

## Décisions techniques

| Question | Décision |
|----------|----------|
| Quand notifier ? | Après succès pipeline uniquement |
| Comment surveiller ? | `/check-pipeline` manuel + background agent |
| Persistance background ? | Non (s'arrête si session termine) |
| Format message ? | Informatif orienté CR (pas de durée pipeline) |
| Qui notifier ? | Channel fixe dans config |
| Comment envoyer ? | MCP Slack (prérequis user) |
| Intégration finish-branch ? | Proposer après création MR non-draft |
| Transition Jira ? | Oui, via `/notify-cr` |

## Fichiers à créer/modifier

| Fichier | Action |
|---------|--------|
| `skills/check-pipeline/SKILL.md` | Créer |
| `skills/notify-cr/SKILL.md` | Créer |
| `skills/finish-development-branch/SKILL.md` | Modifier |
| `config/plugin-config.yaml` | Modifier |
| `README.md` | Modifier (prérequis) |
| `IDEA.md` | Modifier (amélioration future) |

## Amélioration future

### Bouton interactif Slack pour CR

Actuellement, après le MP "Pipeline OK", l'utilisateur doit lancer `/notify-cr` manuellement. Idéalement, un bouton dans le MP permettrait de poster directement dans le channel.

**Implémentation possible :**
- Créer une Slack App avec Interactive Components
- Héberger un endpoint HTTP (Lambda, Cloud Function, ou serveur)
- Le bouton envoie un payload à l'endpoint
- L'endpoint poste dans le channel + fait la transition Jira

**Complexité :** Nécessite infrastructure externe (hosting de l'endpoint)
