# kali-tools

Plugin Claude Code pour l'équipe Kali.

## Prérequis

Pour utiliser `/execute-plan --loop`, ce plugin nécessite [ralph-loop](https://github.com/obra/ralph-loop) :

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install ralph-loop@superpowers-marketplace
```

> **Note :** Tous les skills fonctionnent sans dépendances externes, sauf le mode `--loop` de `/execute-plan`.

## Installation

```bash
/plugin marketplace add https://gitlab.obat.fr/tools/obat-claude-plugins
/plugin install kali-tools@kali-marketplace
```

## Détection de contexte

Ce plugin détecte automatiquement si vous êtes dans un contexte Obat :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

| Contexte | Skills disponibles | Comportement |
|----------|-------------------|--------------|
| **Obat** | Tous (génériques + `obat/*`) | Conventions Obat, quality gates complets |
| **Générique** | Génériques uniquement | Format libre, quality gates basiques |

**Flags de surcharge :**
- `--obat` : Force le contexte Obat
- `--no-obat` : Force le contexte générique

## Skills génériques

Ces skills fonctionnent dans tous les contextes.

### /workflow

Orchestration automatique du cycle de développement complet. Enchaîne les skills appropriés avec détection intelligente des transitions.

```bash
# Mode guidé - cycle complet avec checkpoints
/workflow "ajouter un bouton de déconnexion"

# Mode partiel - phases spécifiques uniquement
/workflow --from plan --to code-review

# Mode autopilot - tâches simples, minimal interaction
/workflow --autopilot "fix typo in README"

# Voir l'état d'un workflow en cours
/workflow --status

# Reprendre un workflow interrompu
/workflow --resume
```

#### Phases du cycle

```
brainstorm → plan → execute-plan → code-review → finish-branch
```

| Phase | Skill invoqué | Condition de sortie |
|-------|---------------|---------------------|
| `brainstorm` | `/brainstorm` | Design document sauvegardé |
| `plan` | `/plan` | Plan markdown ou PRD généré |
| `execute-plan` | `/execute-plan` | Toutes les tâches complétées |
| `code-review` | `/code-review` | Review terminée |
| `finish-branch` | `/finish-branch` | MR créée |

#### Mode guidé (par défaut)

- **Checkpoints configurables** : validation utilisateur après `plan` et `code-review`
- **Détection automatique** : contexte Jira, complexité pour SDD, suggestion worktree
- **Sauvegarde d'état** : reprise possible après interruption

#### Mode autopilot

Activé uniquement si :
- Score de complexité < 3
- Pas d'ID Jira détecté
- Description courte (<100 caractères)

Exécution rapide sans brainstorming ni plan formel.

#### Configuration

```yaml
# config/plugin-config.yaml
workflow:
  default-flow: [brainstorm, plan, execute-plan, code-review, finish-branch]
  checkpoints: [plan, code-review]
  autopilot-threshold: 3
  default-execution-mode: standard
  auto-suggest-worktree: true
```

### /brainstorm

Brainstorming avec support Jira et SDD (Specification Driven Development) optionnels.

```bash
# Mode standard
/brainstorm créer une API de notifications

# Mode SDD - workflow enrichi avec agents spécialisés
/brainstorm --sdd refonte du système d'authentification

# Mode Jira - avec flag explicite
/brainstorm --jira OBAT-123

# Mode Jira - détection automatique
/brainstorm améliorer le ticket OBAT-123
```

#### Détection automatique de complexité

En mode standard, Claude analyse la complexité de la feature et suggère le workflow SDD si le score ≥ 4 :

| Catégorie | Signaux | Poids |
|-----------|---------|-------|
| Scope technique | Nouvelle intégration externe, changement d'architecture, nouveau domaine | +2 |
| Scope fonctionnel | >3 user stories, impact multi-équipes, nouveau parcours utilisateur | +2 |
| Incertitude | Plusieurs approches viables, technologie inconnue, besoin de recherche | +1 |

#### Mode SDD (`--sdd`)

Active le workflow Specification Driven Development avec :
- Agents spécialisés (business-analyst, architect, researcher, developer)
- Artifacts formels (spec.md, contract.md, data-model.md)
- Phases structurées avec validation

Après le brainstorming, propose de lancer `/sdd/specify` pour créer la spécification formelle.

#### Mode Jira

En mode Jira, Claude :
1. Récupère le ticket et toute sa hiérarchie (epic → stories → tasks → subtasks)
2. Analyse le contexte existant
3. Guide le brainstorming avec cette connaissance
4. Génère un design doc avec suggestions Jira
5. Propose un ADR si pertinent (voir ci-dessous)

#### Génération d'ADR

À la fin du brainstorming, Claude propose de générer un ADR si le contexte l'exige :

- Nouvelle brique technique (ex: cache Redis, nouveau service)
- Choix d'une librairie critique
- Modification d'un flux existant (ex: Auth, paiement)
- Plusieurs approches explorées avec trade-offs

L'ADR est créé dans `docs/plans/ADR-XXXX-titre.md` au format Obat. Pensez à le déplacer vers `blueprint/adr/` après validation.

### /obat/jira-sync

Synchronise les suggestions d'un design doc vers Jira.

```bash
# Sync un design doc spécifique
/obat/jira-sync OBAT-123

# Sync le dernier design doc Jira
/obat/jira-sync

# Prévisualiser sans créer
/obat/jira-sync --dry-run
```

### /plan

Création de plans d'implémentation détaillés.

```bash
# Mode standard - plan markdown avec tâches détaillées
/plan implémenter le système de cache

# Mode PRD - génère un prd.json pour Ralph Loop
/plan --prd OBAT-123

# Voir le statut d'un PRD existant
/plan status
/plan status OBAT-123
```

#### Mode standard

Génère un plan d'implémentation détaillé en markdown (`docs/plans/YYYY-MM-DD-<feature>.md`) avec :
- Tâches découpées en étapes de 2-5 minutes
- Code complet pour chaque étape
- Commandes exactes avec sortie attendue
- Approche TDD (test → implémentation → commit)

#### Mode PRD (Ralph Loop)

Avec le flag `--prd`, génère un `prd.json` pour Ralph Loop :

1. Extrait les acceptance criteria du ticket Jira
2. Récupère les sous-tickets existants
3. Intègre les suggestions du brainstorming
4. Analyse les dépendances et ordonne les stories

Le PRD est sauvegardé dans `docs/plans/OBAT-123-prd.json`.

### /execute-plan

Exécution de plans d'implémentation.

```bash
# Mode standard - exécute un plan markdown par batches
/execute-plan
/execute-plan docs/plans/2026-01-30-feature.md

# Mode subagent - un agent frais par tâche + code review automatique
/execute-plan --subagent
/execute-plan --subagent docs/plans/2026-01-30-feature.md

# Mode worktree - crée un worktree isolé puis exécute
/execute-plan --worktree
/execute-plan --subagent --worktree

# Mode Ralph Loop - exécute un prd.json de manière autonome
/execute-plan --loop
/execute-plan --loop OBAT-123
```

#### Mode standard

Exécute un plan markdown (`docs/plans/*.md`) par batches de 3 tâches avec checkpoints :
- Revue critique du plan avant exécution
- Rapport après chaque batch
- Pause pour feedback entre les batches

#### Mode subagent (`--subagent`)

Exécute un plan en dispatchant un **agent frais par tâche** avec **code review automatique** :
- Élimine la pollution de contexte sur les plans longs (5+ tâches)
- Code review après chaque tâche (Critical/Important/Minor)
- Correction automatique des problèmes critiques
- Retry 1x en cas d'échec, puis stop pour intervention

**Quand l'utiliser :**
- Plans avec 5+ tâches
- Tâches complexes nécessitant un focus isolé
- Besoin de review systématique

#### Flag `--worktree`

Crée un worktree isolé avant l'exécution :
- Demande l'ID Jira et le type de branche
- Crée la branche au format Obat (`feat/DEL-123`, `tech/DEL-456`, etc.)
- Installe les dépendances et vérifie les tests
- Exécute le plan dans ce worktree

**Note :** Combinable avec `--subagent`, mais pas avec `--loop`.

#### Mode Ralph Loop (`--loop`)

Lance une boucle Ralph Loop autonome avec un `prd.json` :
- Détecte automatiquement le fichier prd.json
- Applique les paramètres de `config/plugin-config.yaml`
- Exécute les stories jusqu'à complétion

**Note :** Non combinable avec `--subagent` (modes mutuellement exclusifs).

Pour arrêter la boucle :
```bash
/cancel-ralph
```

### /setup-worktree

Crée un worktree Git isolé pour le développement.

```bash
/setup-worktree
```

**Workflow :**
1. Demande l'ID Jira et le type de branche
2. Construit le nom de branche au format Obat
3. Crée le worktree dans `.worktrees/` ou `~/worktrees/`
4. Installe les dépendances et vérifie les tests

**Convention de nommage :**
| Type | Format | Exemple |
|------|--------|---------|
| Feature | `feat/<PROJET>-<ID>[-desc]` | `feat/DEL-123-auth` |
| Tech | `tech/<PROJET>-<ID>[-desc]` | `tech/DEL-456` |
| Fix | `fix/<PROJET>-<ID>[-desc]` | `fix/DEL-789-login` |
| Hotfix | `hotfix/<PROJET>-<ID>[-desc]` | `hotfix/OBAT-101` |

### /finish-branch

Finalise une branche de développement : quality gates configurables, création MR GitLab, transition Jira.

```bash
# Mode standard - gates auto-détectées selon le type de projet
/finish-branch

# Mode strict - gates + analyses approfondies (contract-check, impact-analysis)
/finish-branch --strict

# Bypass d'urgence - justification obligatoire
/finish-branch --skip-gates
```

#### Quality Gates

Les gates sont **auto-détectées** selon le type de projet :

| Type de projet | Détection | Gates |
|----------------|-----------|-------|
| PHP backend | `composer.json` + `Makefile` | test, phpstan, fix-cs, rector, deptrac |
| PHP simple | `composer.json` seul | composer test, phpstan |
| Node | `package.json` | npm test, lint |
| Python | `pyproject.toml` / `requirements.txt` | pytest, ruff |

**Comportement :** Une gate qui échoue = pas de MR (tout ou rien).

#### Flags

| Flag | Comportement |
|------|--------------|
| (aucun) | Gates de base auto-détectées |
| `--strict` | + contract-check, impact-analysis (si `/contracts` existe) |
| `--skip-gates` | Bypass avec justification obligatoire (incluse dans la MR) |

**Workflow :**
1. Vérifie qu'on est sur une branche feature
2. Extrait l'ID Jira depuis le nom de branche (`feat/DEL-123` → `DEL-123`)
3. Détecte le type de projet et exécute les quality gates
4. Propose les options :
   - Créer une MR (draft ou prête pour review)
   - Garder la branche
   - Abandonner

**Si MR créée :**
- Push la branche
- Crée la MR via MCP gitlab-enhanced
- Propose de passer le ticket Jira en "In Review" (si pas draft)
- Propose une surveillance du pipeline avec notification Slack (si MCP Slack configuré)

**Prérequis :** MCP `gitlab-enhanced` et `atlassian` configurés

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

### /code-review

Code review multi-agents pour changements locaux ou Merge Request GitLab.

```bash
# Review des changements locaux (défaut)
/code-review

# Review avec focus sur certains aspects
/code-review security
/code-review bugs tests

# Review + génération de todos (mode local uniquement)
/code-review --generate-tasks
/code-review -t security

# Review d'une Merge Request GitLab
/code-review --mr 123
/code-review --mr 123 security
```

**Mode Local :**
- Analyse les changements non committés
- Génère un rapport markdown structuré
- Quality Gate : READY TO COMMIT / NEEDS FIXES
- `--generate-tasks` : transforme les issues en todos (max 15, triés par sévérité)

**Mode MR :**
- Analyse une Merge Request GitLab
- Review interactive : prévisualisation de chaque commentaire
- Options par commentaire : Envoyer / Modifier / Ignorer
- Poste les commentaires validés via MCP gitlab-enhanced

**Agents spécialisés (jusqu'à 6 en parallèle) :**
- Bug Hunter - Détection de bugs et root cause analysis
- Security Auditor - Vulnérabilités et failles de sécurité
- Test Coverage Reviewer - Qualité et couverture des tests
- Code Quality Reviewer - Structure et maintenabilité
- Contracts Reviewer - Contrats API et types
- Historical Context Reviewer - Contexte historique du code

**Prérequis Mode MR :** MCP `gitlab-enhanced` configuré

## Skills Obat

Ces skills nécessitent un contexte Obat (remote `gitlab.obat.fr`). Hors contexte, ils affichent un message d'erreur sauf si `--obat` est utilisé.

### /obat/obat/contract-check

Vérifie la compatibilité des changements avec les contrats OpenAPI centralisés dans le submodule `api-contracts/`.

```bash
# Analyser le diff courant
/obat/contract-check

# Endpoint spécifique
/obat/contract-check POST /api/users

# Service spécifique
/obat/contract-check --service obat-user
```

**Détection :**
- Compare les Controllers/DTOs modifiés avec les fichiers OpenAPI
- Identifie les breaking changes (champs supprimés, types modifiés)
- Détecte les drifts contrat ↔ code

**Types de contrats analysés :**
| Fichier | Consommateurs |
|---------|---------------|
| `internal.openapi.yaml` | Autres microservices Obat |
| `public.openapi.yaml` | Frontend, apps sans auth |
| `external.openapi.yaml` | Clients authentifiés |
| `partners.openapi.yaml` | Partenaires externes |

**Output :**
- 🔴 Breaking changes (bloquants)
- 🟡 Drifts contrat ↔ code (warnings)
- ✅ Changements compatibles
- Actions requises et services impactés

**Intégration :** Appelé par `/finish-branch --strict`

**Prérequis :** Submodule `api-contracts/` initialisé

### /obat/impact-analysis

Analyse l'impact d'un changement sur les autres microservices Obat.

```bash
# Analyser le diff courant
/obat/impact-analysis

# Fichier spécifique
/obat/impact-analysis --file src/User/Domain/Event/UserDeactivatedEvent.php

# Endpoint REST
/obat/impact-analysis --endpoint "GET /api/users"

# Event RabbitMQ
/obat/impact-analysis --event UserDeactivatedEvent

# Tous les consommateurs d'un service
/obat/impact-analysis --service obat-user

# Rapport détaillé
/obat/impact-analysis --verbose
```

**Analyse :**
- Scan du code source des 19 services
- Détection des appels HTTP inter-services
- Détection des événements RabbitMQ consommés
- Identification des dépendances transitives

**Output :**
- Services impactés avec niveau de risque
- Endpoints/events concernés
- Actions de coordination requises

**Intégration :** Appelé par `/finish-branch --strict`

### /obat/cqrs-generate

Scaffolde du code CQRS (Commands, Queries, Events) selon les conventions Obat.

```bash
# Commands
/obat/cqrs-generate command CreateUser --fields "email:string, name:string"
/obat/cqrs-generate command DeactivateUser --domain User --fields "userId:UserUuid, reason:?string"

# Queries
/obat/cqrs-generate query GetUserById --fields "userId:UserUuid"
/obat/cqrs-generate query ListUsers --domain User --fields "companyUuid:CompanyUuid, page:int"

# Events sync (même process)
/obat/cqrs-generate event PasswordChanged --fields "userId:string"

# Events async (RabbitMQ interne)
/obat/cqrs-generate event UserCreated --async --fields "userUuid:string, email:string"

# Events externes (cross-service)
/obat/cqrs-generate event UserDeactivated --external --fields "userUuid:string, reason:string"
```

**Fichiers générés :**

| Type | Fichiers |
|------|----------|
| Command | `Command/{Name}Command.php` + `Handler/{Name}Handler.php` |
| Query | `Query/{Name}Query.php` + `Handler/{Name}Handler.php` |
| Event | `Domain/Event/{Name}Event.php` + `EventSubscriber/{Name}Event/Handle{Name}Subscriber.php` |

**Features :**
- Auto-détection du service, demande interactive du domaine
- Résolution automatique des imports (ValueObjects)
- Mise à jour de `messenger.yaml` pour events `--external`
- Classes `final readonly` avec constructor property promotion

### /obat/api-migrate

Migre des endpoints API Platform du monorepo `core` vers les microservices.

```bash
# Analyse seule (rapport de migration)
/obat/api-migrate GET /api/documents --target accounting

# Avec génération de code
/obat/api-migrate POST /api/cdn_files --target user --generate

# Opération custom API Platform
/obat/api-migrate PUT /api/documents/change_status/{uuid} --target accounting
```

**Analyse complète :**
- Controller, Extensions Doctrine, Providers, Persisters
- Filters, Normalizers, Transformers
- Voters, Validators, DTOs
- Security expressions et multi-tenancy

**Output :**
- Composants détectés avec leur rôle
- Mapping source → cible (architecture CQRS)
- Suggestions de modernisation (PHP 8, attributs Symfony)
- Comparaison avec contrat OpenAPI (si existe)
- Checklist de non-régression complète

**Flag `--generate` :**
Génère le code CQRS dans le service cible via `/obat/cqrs-generate`.

### /mr-feedback

Traitement interactif des feedbacks de code review reçus sur une Merge Request GitLab.

```bash
# Traiter les feedbacks d'une MR
/mr-feedback 123

# Avec projet explicite
/mr-feedback 123 --project group/monprojet
```

**Workflow en 3 phases :**

**Phase 1 - Vue d'ensemble :**
- Récupère tous les feedbacks non résolus
- Analyse priorité (🔴 Critical → 🟢 Low) et pertinence (✅/⚠️/❌/❓)
- Affiche un tableau récapitulatif trié

**Phase 2 - Traitement un par un :**
Pour chaque feedback, affiche :
- Commentaire original complet
- Suggestion de code si présente (diff)
- Code actuel avec contexte (±5 lignes)
- Analyse de pertinence avec justification

Puis propose les actions :
| Action | Description |
|--------|-------------|
| Corriger + Fermer | Fix + commit fixup + réponse + résolution thread |
| Appliquer suggestion | Applique le diff suggéré directement |
| Répondre seulement | Poste une réponse sans modifier le code |
| Passer | Ignore ce feedback pour l'instant |
| Marquer hors-scope | Répond + crée une issue optionnelle |
| Demander clarification | Poste une question au reviewer |

**Phase 3 - Finalisation :**
- Récapitulatif des actions effectuées
- Propose `git rebase -i --autosquash` pour fusionner les commits fixup
- Ou push direct des commits séparés

**Intégration Git :**
Chaque correction crée un commit `fixup!` référençant le commit original. À la fin :
```bash
git rebase -i --autosquash origin/main
```

**Prérequis :** MCP `gitlab-enhanced` configuré

### /docs/analysis

Analyse la santé de la documentation projet.

```bash
# Analyse complète du projet
/docs/analysis

# Analyser un répertoire spécifique
/docs/analysis src/payments/

# Analyser un type de documentation
/docs/analysis api
```

**Produit un rapport avec :**
- État actuel de la documentation
- Lacunes identifiées et priorisées (Impact/Effort)
- Parcours utilisateur analysés
- Recommandations d'automatisation (OpenAPI, JSDoc, etc.)

### /docs/update

Met à jour la documentation après des changements de code.

```bash
# Mettre à jour pour les changements non commités
/docs/update

# Cibler un répertoire
/docs/update src/auth/

# Cibler un type de documentation
/docs/update api
/docs/update readme
/docs/update jsdoc
```

**Workflow :**
1. Analyse les changements git (ou dernier commit)
2. Identifie les impacts sur la documentation
3. Mode simple (1-2 fichiers) : écrit directement
4. Mode multi-agent (3+ fichiers) : dispatch des agents tech-writer

**Référence :** Utilise l'agent tech-writer (`references/tech-writer.md`) pour les bonnes pratiques.

### /sdd/* (Specification Driven Development)

Workflow complet de développement piloté par spécifications, avec agents spécialisés et artifacts formels.

```bash
# Initialiser le projet SDD (constitution + templates)
/sdd/setup

# Créer une spécification formelle
/sdd/specify système de notifications push

# Planifier l'architecture (research + design)
/sdd/plan

# Découper en tâches exécutables
/sdd/tasks

# Implémenter avec TDD + review entre phases
/sdd/implement

# Documenter la feature complétée
/sdd/document
```

#### Workflow SDD

```
/sdd/specify → /sdd/plan → /sdd/tasks → /sdd/implement → /sdd/document
     │              │            │             │               │
     ▼              ▼            ▼             ▼               ▼
 business-      researcher   tech-lead    developer       tech-writer
 analyst        architect    (découpe)    (TDD + review)  (docs)
 (spec.md)      (plan.md)    (tasks.md)
```

#### Artifacts générés

Les artifacts sont créés dans `specs/<NNN>-<feature>/` :

| Fichier | Description | Agent |
|---------|-------------|-------|
| `spec.md` | Spécification formelle | business-analyst |
| `research.md` | Recherche technique | researcher |
| `plan.md` | Architecture et design | software-architect |
| `data-model.md` | Modèle de données | software-architect |
| `contract.md` | Contrats API | software-architect |
| `tasks.md` | Tâches découpées | tech-lead |

#### Review à deux niveaux

**Niveau 1 (entre phases)** : Review rapide avec 3 agents (code-quality, test-coverage, contracts) - seuil 70%

**Niveau 2 (avant merge)** : Review complète avec les 6 agents du `/code-review` - seuil 80%

#### Intégration avec /brainstorm

Le workflow SDD s'intègre naturellement avec `/brainstorm` :

1. `/brainstorm --sdd "feature"` → brainstorming + design.md
2. `/sdd/specify` → transforme le design en spec formelle
3. Suite du workflow SDD...

### pre-commit (hook)

Lance automatiquement les vérifications de qualité avant chaque `git commit` effectué par Claude Code.

**Fonctionnement :**
1. Auto-fix (cs-fixer, rector)
2. Re-stage des fichiers modifiés
3. Vérifications (phpstan, deptrac)
4. Bloque si erreurs

**Détection du type de projet :**
| Détection | Checks |
|-----------|--------|
| `composer.json` + `Makefile` | fix-cs, rector, phpstan, deptrac |
| `composer.json` seul | phpstan |
| `package.json` | npm run lint |

**Cas ignorés :** `--amend`, `--allow-empty`, `--no-verify`

**Prérequis :** `jq` installé, Makefile avec les targets appropriées

### terminal-title (hook)

Met à jour automatiquement le titre du terminal pour refléter l'activité courante de Claude Code. Idéal pour gérer plusieurs sessions dans différents terminaux.

**Format :** `dossier | Activité`

**Activités détectées :**
| Activité | Déclencheur |
|----------|-------------|
| Exploring | Lecture de fichiers, recherche |
| Coding | Édition de fichiers |
| Testing | Exécution de tests |
| Git | Commandes git |
| Running | Autres commandes bash |
| Researching | Agents de recherche |

**Prérequis :** `jq` installé (`sudo apt install jq` ou `brew install jq`)

## Structure

```
skills/
├── # ─── SKILLS GÉNÉRIQUES ───
├── workflow/SKILL.md                   # Orchestration cycle complet
├── brainstorm/SKILL.md                 # Brainstorming + mode Jira/SDD
├── plan/SKILL.md                       # Plans d'implémentation + PRD
├── execute-plan/SKILL.md               # Exécution de plans + Ralph Loop
├── setup-worktree/SKILL.md             # Création worktree isolé
├── finish-development-branch/SKILL.md  # Finalisation branche + MR
├── check-pipeline/SKILL.md             # Vérification pipeline GitLab
├── notify-cr/SKILL.md                  # Notification CR Slack + Jira
├── code-review/                        # Code review multi-agents
│   ├── SKILL.md
│   └── references/                     # Agents spécialisés
├── mr-feedback/SKILL.md                # Traitement feedbacks MR reçus
├── sdd/                                # Specification Driven Development
│   ├── setup/SKILL.md
│   ├── specify/SKILL.md
│   ├── plan/SKILL.md
│   ├── tasks/SKILL.md
│   ├── implement/SKILL.md
│   ├── document/SKILL.md
│   └── references/                     # Agents SDD
├── docs/
│   ├── analysis/SKILL.md               # Analyse santé documentation
│   └── update/SKILL.md                 # Mise à jour documentation
├── pre-commit/                         # Hook pre-commit
│   └── hooks/pre-tool-use.sh
├── terminal-title/                     # Hook titre terminal
│   └── hooks/post-tool-use.sh
│
├── # ─── SKILLS OBAT (contexte gitlab.obat.fr) ───
└── obat/
    ├── contract-check/SKILL.md         # Vérification contrats OpenAPI
    ├── impact-analysis/SKILL.md        # Analyse impact cross-service
    ├── cqrs-generate/SKILL.md          # Scaffolding CQRS
    ├── api-migrate/SKILL.md            # Migration API Platform → microservices
    └── jira-sync/SKILL.md              # Sync design doc → Jira Obat
```

## Configuration

### Configuration utilisateur (requise)

Créez `~/.claude/config/obat-jira.yaml` :

```yaml
jira:
  default_project: OBAT    # Votre projet Jira
  board_id: 42             # ID de votre board
  default_assignee: ""     # Votre email (optionnel)
  default_priority: Medium
```

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

### Configuration équipe

Les valeurs par défaut équipe sont dans `config/plugin-config.yaml`.
