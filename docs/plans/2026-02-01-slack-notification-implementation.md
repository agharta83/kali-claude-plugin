# Slack Notification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Notifier sur Slack quand un pipeline GitLab passe, pour faciliter les demandes de code review.

**Architecture:** Trois nouveaux skills (`/check-pipeline`, `/notify-cr`) + modification de `/finish-branch`. Utilisation des MCP gitlab-enhanced, atlassian et slack. Configuration dans `plugin-config.yaml` et `~/.claude/config/obat-slack.yaml`.

**Tech Stack:** Claude Code skills (Markdown), MCP Slack, MCP gitlab-enhanced, MCP Jira

**Design doc:** [2026-02-01-slack-notification-design.md](2026-02-01-slack-notification-design.md)

---

## Task 1: Configuration plugin-config.yaml

**Files:**
- Modify: `config/plugin-config.yaml`

**Step 1: Ajouter la section slack**

Ajouter après la section `ralph:` :

```yaml
# Configuration Slack
slack:
  # Channel pour les demandes de code review
  code_review_channel: "#code-reviews"

  # Messages aléatoires pour les demandes de CR
  cr_messages:
    - template: |
        👀 Qui veut review ma MR ?
        {title}
        → {url}
    - template: |
        🎯 CR disponible !
        MR !{mr_id} - {title}
        Premier arrivé, premier servi 🏃
        → {url}
    - template: |
        🚀 Pipeline vert, MR prête !
        ✨ {title}
        🔗 {url}
        Merci d'avance ! 🙏
    - template: |
        ☕ Une petite review ?
        MR !{mr_id} - {title}
        → {url}

  # Blagues optionnelles (20% de chance d'apparaître)
  jokes:
    - "Je promets qu'il n'y a que 2 fichiers changés... par commit 😅"
    - "J'ai écrit des tests, je le jure 🤞"
    - "Pas de force push cette fois, promis"
    - "Le code est auto-documenté (dit-il, confiant)"
    - "Fonctionne sur ma machine ™️"
```

**Step 2: Vérifier le fichier**

Lire le fichier pour confirmer que la syntaxe YAML est correcte.

---

## Task 2: Créer le skill /check-pipeline

**Files:**
- Create: `skills/check-pipeline/SKILL.md`

**Step 1: Créer le répertoire et le fichier SKILL.md**

```markdown
---
name: check-pipeline
description: "Vérifie le statut d'un pipeline GitLab pour une MR."
---

# Check Pipeline

Vérifie le statut du pipeline d'une Merge Request GitLab.

**Annonce au démarrage :** "Je vérifie le statut du pipeline."

## Usage

```bash
/check-pipeline !123        # Par numéro de MR
/check-pipeline DEL-456     # Par ID Jira (trouve la MR associée)
```

## Étape 1 : Parser l'argument

Analyser l'argument fourni :
- Si commence par `!` → Numéro de MR (ex: `!123` → `123`)
- Si match `[A-Z]+-\d+` → ID Jira (ex: `DEL-456`)
- Sinon → Erreur : "Format non reconnu. Utilisez !123 (MR) ou DEL-456 (Jira)."

## Étape 2 : Récupérer la MR

### Si numéro de MR

1. Détecter le projet GitLab courant :
   ```bash
   git remote get-url origin
   ```
2. Extraire `group/project` de l'URL
3. Utiliser `mcp__gitlab-enhanced__get_merge_request` avec :
   - `project_id`: group/project
   - `merge_request_iid`: numéro de MR

### Si ID Jira

1. Chercher la branche associée :
   ```bash
   git branch -a | grep -i "<JIRA-ID>"
   ```
2. Si trouvée, chercher la MR via `mcp__gitlab-enhanced__list_merge_requests` avec :
   - `source_branch`: nom de la branche
3. Si non trouvée → Erreur : "Aucune branche trouvée pour <JIRA-ID>."

## Étape 3 : Récupérer le statut du pipeline

Depuis la MR récupérée, extraire :
- `head_pipeline.status` : `success`, `failed`, `running`, `pending`, `canceled`
- `head_pipeline.id` : ID du pipeline
- `head_pipeline.web_url` : URL du pipeline

Si pas de pipeline → Afficher : "Aucun pipeline trouvé pour cette MR."

## Étape 4 : Afficher le résultat

### Si success

```
Pipeline MR !{mr_iid} : ✅ success
  {mr_title}

→ Vous pouvez lancer /notify-cr !{mr_iid} pour demander une review
```

### Si running

```
Pipeline MR !{mr_iid} : 🔄 running
  {mr_title}

→ Relancez /check-pipeline !{mr_iid} dans quelques minutes
```

### Si failed

```
Pipeline MR !{mr_iid} : ❌ failed
  {mr_title}

→ Voir les logs : {pipeline_web_url}
```

### Si pending

```
Pipeline MR !{mr_iid} : ⏳ pending
  {mr_title}

→ Le pipeline n'a pas encore démarré
```

## Prérequis

- MCP `gitlab-enhanced` configuré

## Erreurs courantes

**Projet GitLab non détecté**
- Problème : `git remote get-url origin` échoue
- Solution : Vérifier qu'on est dans un repo Git avec un remote origin

**MR non trouvée**
- Problème : Le numéro de MR n'existe pas
- Solution : Vérifier le numéro avec `git log` ou l'interface GitLab
```

---

## Task 3: Créer le skill /notify-cr

**Files:**
- Create: `skills/notify-cr/SKILL.md`

**Step 1: Créer le répertoire et le fichier SKILL.md**

```markdown
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
```

---

## Task 4: Modifier /finish-branch pour la surveillance

**Files:**
- Modify: `skills/finish-development-branch/SKILL.md`

**Step 1: Ajouter la proposition de surveillance après création MR**

Après l'étape 5.4 (Proposer transition Jira), ajouter une nouvelle section **5.5 Proposer notification Slack** :

```markdown
**5.5 Proposer notification Slack :**

Vérifier si le MCP Slack est disponible. Si oui :

```
MR créée : <URL>

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

Si MCP Slack non disponible → Ne pas proposer, continuer directement.
```

**Step 2: Mettre à jour la section Prérequis**

Ajouter à la section Prérequis :

```markdown
- MCP Slack configuré (optionnel, pour notifications pipeline)
```

**Step 3: Renommer l'ancienne section 5.5 en 5.6**

L'ancienne section "5.5 Nettoyage worktree" devient "5.6 Nettoyage worktree".

---

## Task 5: Mettre à jour le README

**Files:**
- Modify: `README.md`

**Step 1: Ajouter la documentation de /check-pipeline**

Après la section `/finish-branch`, ajouter :

```markdown
### /check-pipeline

Vérifie le statut du pipeline d'une Merge Request GitLab.

```bash
/check-pipeline !123        # Par numéro de MR
/check-pipeline DEL-456     # Par ID Jira
```

**Output :**
- ✅ success → Propose `/notify-cr`
- 🔄 running → Suggère de relancer plus tard
- ❌ failed → Affiche le lien vers les logs

**Prérequis :** MCP `gitlab-enhanced` configuré

### /notify-cr

Poste une demande de code review dans Slack et fait la transition Jira.

```bash
/notify-cr !123        # Par numéro de MR
/notify-cr DEL-456     # Par ID Jira
```

**Actions :**
1. Poste un message fun dans le channel `#code-reviews`
2. Fait la transition Jira vers "Code Review" (si ID Jira dans le titre)

**Prérequis :** MCP `gitlab-enhanced`, MCP Slack, MCP `atlassian`
```

**Step 2: Ajouter la section prérequis MCP Slack**

Après la section "Configuration utilisateur (requise)", ajouter :

```markdown
### Configuration Slack (optionnelle)

Pour les notifications de pipeline et demandes de CR :

1. Installer un MCP Slack (ex: `@anthropic/mcp-slack` ou autre)
2. Configurer dans `~/.claude/settings.json`
3. Créer `~/.claude/config/obat-slack.yaml` :
   ```yaml
   slack:
     user_id: "U1234567890"  # Votre ID Slack
   ```
4. Le channel est configuré dans `config/plugin-config.yaml` :
   ```yaml
   slack:
     code_review_channel: "#code-reviews"
   ```

**Pour trouver votre ID Slack :** Profil → ⋮ → Copy member ID
```

**Step 3: Mettre à jour la structure des fichiers**

Dans la section "Structure", ajouter :

```
├── check-pipeline/SKILL.md              # Vérification pipeline
├── notify-cr/SKILL.md                   # Notification CR Slack + Jira
```

---

## Task 6: Mettre à jour la documentation finish-branch dans README

**Files:**
- Modify: `README.md`

**Step 1: Ajouter la mention de la surveillance Slack**

Dans la section `/finish-branch`, après "Propose de passer le ticket Jira en 'In Review'", ajouter :

```markdown
- Propose une surveillance du pipeline avec notification Slack (si MCP Slack configuré)
```

---

## Résumé des fichiers

| Fichier | Action |
|---------|--------|
| `config/plugin-config.yaml` | Modifier - ajouter section slack |
| `skills/check-pipeline/SKILL.md` | Créer |
| `skills/notify-cr/SKILL.md` | Créer |
| `skills/finish-development-branch/SKILL.md` | Modifier - ajouter surveillance |
| `README.md` | Modifier - ajouter docs + prérequis |
