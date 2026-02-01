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
