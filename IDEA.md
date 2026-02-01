# Ideas pour évolutions futures

## ~~Notification Slack après succès pipeline~~ ✅ IMPLÉMENTÉ

Voir [design](docs/plans/2026-02-01-slack-notification-design.md)

---

## Priorisation globale

### Skills communs (réutilisables hors Obat)

| Priorité | Skill | Raison |
|----------|-------|--------|
| ~~🔴 P1~~ | ~~`/workflow`~~ | ✅ IMPLÉMENTÉ - Orchestration bout-en-bout |
| ~~🔴 P1~~ | ~~Quality gates dans `/finish-branch`~~ | ✅ IMPLÉMENTÉ - Auto-détection, --strict, --skip-gates |
| ~~🔴 P1~~ | ~~`/code-review --generate-tasks`~~ | ✅ IMPLÉMENTÉ - Ferme la boucle review → action |
| ~~🟠 P2~~ | ~~Hook pre-commit~~ | ✅ IMPLÉMENTÉ - Détection précoce des problèmes |
| 🟠 P2 | `/sdd/acceptance` | Phase test formelle pour SDD |
| 🟠 P2 | `/docs/watch` | Documentation as Code automatique |
| 🟡 P3 | `/metrics` | Insights sur les patterns récurrents |
| 🟡 P3 | `/mr-feedback` amélioré | Détection patterns, batch mode |

### Skills Obat-spécifiques (microservices hexa/CQRS)

| Priorité | Skill | Raison |
|----------|-------|--------|
| 🟢 WIP | `/contract-check` | Critique pour 19 services, évite breaking changes - **CRÉÉ** |
| 🟢 WIP | `/impact-analysis` | Coordination cross-service obligatoire - **CRÉÉ** |
| ~~🔴 P1~~ | ~~`/cqrs-generate`~~ | ✅ CRÉÉ - Usage quotidien, conventions Obat |
| 🟠 P2 | `/onboard-service` | Facilite découverte des 19 services |
| 🟠 P2 | `/consumer-health` | Monitoring RabbitMQ essentiel |
| 🟠 P2 | `/event-trace` | Debug inter-services |
| 🟡 P3 | `/test-contract` | Génération tests depuis OpenAPI |
| 🟡 P3 | `/service-scaffold` | Rare (nouveau service) |
| 🟡 P3 | `/hexa-refactor` | Migration progressive du legacy |
| 🟡 P3 | `/migration-helper` | Upgrades PHP/Symfony ponctuels |

---

## Skills communs (réutilisables)

### ~~`/workflow` - Orchestration automatique des skills~~ ✅ IMPLÉMENTÉ

Voir [skills/workflow/SKILL.md](skills/workflow/SKILL.md)

---

### ~~Quality gates dans `/finish-branch`~~ ✅ IMPLÉMENTÉ

Voir [design](docs/plans/2026-02-01-quality-gates-design.md) et [skills/finish-development-branch/SKILL.md](skills/finish-development-branch/SKILL.md)

**Usage :**
```bash
/finish-branch              # Gates auto-détectées
/finish-branch --strict     # + contract-check, impact-analysis
/finish-branch --skip-gates # Bypass avec justification obligatoire
```

---

### ~~`/code-review --generate-tasks`~~ ✅ IMPLÉMENTÉ

Voir [design](docs/plans/2026-02-01-code-review-generate-tasks-design.md)

**Usage :**
```bash
/code-review --generate-tasks     # Rapport + todos
/code-review --tasks              # Alias court
/code-review -t security          # Avec focus
```

---

### ~~Hook pre-commit~~ ✅ IMPLÉMENTÉ

Voir [design](docs/plans/2026-02-01-pre-commit-hook-design.md)

Hook `PreToolUse` qui intercepte les `git commit` de Claude et lance les vérifications de qualité.

**Fonctionnalités :**
- Auto-fix (cs-fixer, rector) puis vérifications (phpstan, deptrac)
- Bloque si erreurs non-fixables
- Détection automatique du type de projet (PHP Obat, PHP simple, Node)

**Configuration :** Automatique via `.claude/settings.local.json`

---

### `/sdd/acceptance` - Phase de test d'acceptance

**Contexte :** SDD couvre specify → implement → document, mais pas de validation formelle spec ↔ code.

**Fonctionnalités :**
- Génère des tests d'acceptance depuis les specs
- Valide que tous les critères de la spec sont couverts
- Produit un rapport de conformité
- Identifie les specs non implémentées ou partiellement couvertes

**Usage :**
```bash
# Après /sdd/implement
/sdd/acceptance

# Pour une spec spécifique
/sdd/acceptance specs/042-user-auth/
```

**Output :**
```markdown
## Rapport d'acceptance - specs/042-user-auth

### Critères couverts ✅
- [x] User can login with email/password
- [x] User receives error on invalid credentials
- [x] Session expires after 24h

### Critères partiellement couverts ⚠️
- [ ] User can reset password (test missing for expired token case)

### Critères non couverts ❌
- [ ] User can enable 2FA (not implemented)

**Score de conformité : 75%**

Générer les tests manquants ? [Y/n]
```

---

### `/docs/watch` - Documentation as Code

**Contexte :** `/docs/analysis` et `/docs/update` sont réactifs, pas proactifs.

**Fonctionnalités :**
- Se déclenche automatiquement quand `src/` change
- Met à jour README/CHANGELOG en background
- Alerte si documentation désynchronisée
- Génère des suggestions de mise à jour

**Configuration :**
```yaml
docs:
  watch:
    enabled: true
    paths: ["src/", "config/"]
    ignore: ["*.test.ts", "*.spec.php"]
    auto-update: false  # true = update auto, false = suggestions seulement
    stale-threshold: 7d  # Alerte si doc pas mise à jour depuis 7 jours
```

**Usage :**
```bash
# Activer le watch
/docs/watch --enable

# Voir l'état de synchronisation
/docs/watch --status

# Appliquer les suggestions en attente
/docs/watch --apply
```

---

### `/metrics` - Métriques et insights

**Contexte :** Pas de suivi des patterns récurrents dans le workflow.

**Fonctionnalités :**
- Temps moyen par phase SDD
- Types de findings récurrents (code review)
- Ratio complexity score → SDD utilisé
- Taux de succès pipeline par type de branche
- Évolution de la qualité dans le temps

**Usage :**
```bash
# Dashboard global
/metrics

# Métriques d'une période
/metrics --since "2 weeks ago"

# Focus sur un aspect
/metrics --focus code-review
/metrics --focus pipeline
/metrics --focus sdd
```

**Output :**
```markdown
## Métriques - 2 dernières semaines

### Code Review
| Type de finding | Count | Trend |
|-----------------|-------|-------|
| Security | 3 | ↓ -40% |
| Test coverage | 12 | ↑ +20% |
| Code quality | 8 | → stable |

### Pipeline
- Taux de succès : 87% (↑ +5%)
- Temps moyen : 4m32s
- Échecs fréquents : PHPStan (45%), Tests (30%)

### SDD Usage
- Projets avec SDD : 4/7 (57%)
- Complexity score moyen : 5.2
- Conformité spec moyenne : 82%
```

**Stockage :** `.claude/metrics/` (fichiers JSON par semaine)

---

### `/mr-feedback` amélioré

**Améliorations proposées :**

1. **Détection de patterns**
   - Identifie si un feedback est similaire à un précédent
   - Suggère des réponses basées sur l'historique
   - Alerte sur les reviewers avec patterns récurrents

2. **Mode batch**
   - Traite plusieurs feedbacks similaires en une fois
   - Applique la même correction à plusieurs occurrences

3. **Templates de réponse**
   - Bibliothèque de réponses pour feedbacks courants
   - Personnalisable par équipe

**Usage :**
```bash
# Mode standard
/mr-feedback

# Mode batch (groupe les similaires)
/mr-feedback --batch

# Avec suggestions de templates
/mr-feedback --templates
```

---

## Skills Obat-spécifiques (microservices hexa/CQRS)

### `/contract-check` - Vérifier les contrats OpenAPI ✅ CRÉÉ

Voir [skills/contract-check/SKILL.md](skills/contract-check/SKILL.md)

Vérifie la compatibilité des changements avec les contrats centralisés dans le submodule `api-contracts/`.

**Usage :**
```bash
/contract-check                      # Analyse le diff courant
/contract-check POST /api/users      # Endpoint spécifique
/contract-check --service obat-user  # Service spécifique
```

**Intégration :** Appelé par `/finish-branch --strict`

---

### `/impact-analysis` - Analyser l'impact cross-service - CRÉÉ

Voir [skills/impact-analysis/SKILL.md](skills/impact-analysis/SKILL.md) et [design](docs/plans/2026-02-01-impact-analysis-design.md)

Analyse l'impact d'un changement sur les autres services en scannant leur code source.

**Usage :**
```bash
/impact-analysis                              # Analyse le diff courant
/impact-analysis --file <path>                # Fichier spécifique
/impact-analysis --endpoint "GET /api/users"  # Endpoint REST
/impact-analysis --event UserDeactivatedEvent # Event RabbitMQ
/impact-analysis --service obat-user          # Tous les consommateurs d'un service
/impact-analysis --verbose                    # Rapport détaillé
```

**Intégration :** Appelé par `/finish-branch --strict`

---

### ~~`/cqrs-generate` - Générer Command/Query/Event~~ ✅ CRÉÉ

Voir [skills/cqrs-generate/SKILL.md](skills/cqrs-generate/SKILL.md) et [design](docs/plans/2026-02-01-cqrs-generate-design.md)

Scaffolde du code CQRS avec les conventions Obat.

**Fonctionnalités :**
- Génère Command + Handler + Tests
- Génère Query + Handler + Tests
- Génère Event + Subscribers
- Configure le routing dans messenger.yaml
- Ajoute les validations Symfony

**Usage :**
```bash
# Générer une command
/cqrs-generate command CreateUser --service user --fields "email:string, name:string"

# Générer une query
/cqrs-generate query GetUserById --service user --fields "id:Uuid"

# Générer un event async (RabbitMQ)
/cqrs-generate event UserCreated --service user --async

# Générer un event sync (même service)
/cqrs-generate event PasswordChanged --service user
```

**Fichiers générés (pour une command) :**
```
src/User/Application/
├── Command/
│   └── CreateUserCommand.php
├── Handler/
│   └── CreateUserHandler.php
tests/User/Application/
└── Handler/
    └── CreateUserHandlerTest.php
config/packages/messenger.yaml (updated)
```

---

### `/onboard-service` - S'approprier un service

Pour découvrir rapidement un service inconnu.

**Fonctionnalités :**
- Cartographie les domaines/bounded contexts
- Liste les endpoints et leurs usages
- Identifie les dépendances entrantes/sortantes
- Résume l'architecture et les patterns utilisés
- Liste les events produits/consommés
- Génère un schéma des flux de données

**Usage :**
```bash
# Découvrir un service
/onboard-service operation

# Focus sur un domaine spécifique
/onboard-service operation --domain Calendar
```

**Output :**
```markdown
## Service: operation

### Overview
Service de gestion des ressources, calendriers et chantiers.

### Bounded Contexts
- **Resource** : Gestion des ressources (véhicules, matériel)
- **Calendar** : Planification et événements
- **Worksite** : Gestion des chantiers

### Endpoints principaux
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/resources | Liste des ressources |
| POST | /api/calendar/events | Créer un événement |
| ... | ... | ... |

### Dépendances
**Consomme :**
- user (GET /api/users, UserDeactivatedEvent)
- accounting (GET /api/invoices)

**Expose :**
- ResourceCreatedEvent → notification, accounting

### Stack technique
- Symfony 6.2, PHP 8.0
- Doctrine ORM, MariaDB
- RabbitMQ (async events)
- Mercure (real-time)
```

---

### `/consumer-health` - Santé des consumers RabbitMQ

Diagnostic de l'état des consumers.

**Fonctionnalités :**
- État de chaque consumer par service
- Nombre de messages en attente par queue
- Messages en erreur (DLQ)
- Lag de traitement estimé
- Suggestions de scaling si backlog important
- Alertes sur consumers down

**Usage :**
```bash
# Vue globale
/consumer-health

# Détail d'un service
/consumer-health user

# Surveiller en temps réel
/consumer-health --watch
```

**Output :**
```markdown
## Consumer Health Report

| Service | Queue | Pending | DLQ | Consumers | Status |
|---------|-------|---------|-----|-----------|--------|
| user | user_external | 12 | 0 | 2 | ✅ OK |
| operation | operation_queue | 1,523 | 5 | 1 | ⚠️ Backlog |
| accounting | accounting_queue | 0 | 0 | 1 | ✅ OK |
| notification | notification_queue | 89 | 12 | 1 | 🔴 DLQ |

### Recommandations
- **operation** : Backlog important, considérer scaling horizontal
- **notification** : 12 messages en DLQ, investiguer les erreurs
```

---

### `/event-trace` - Tracer les events RabbitMQ

Debug les messages inter-services.

**Fonctionnalités :**
- Liste les queues et leur état (messages pending, consumers)
- Trace un event spécifique à travers les services
- Identifie les consumers bloqués/en erreur
- Affiche les messages dans la DLQ (Dead Letter Queue)
- Propose de replay un message depuis la DLQ

**Usage :**
```bash
# Voir l'état global
/event-trace status

# Tracer un type d'event
/event-trace UserCreatedEvent

# Voir la DLQ d'un service
/event-trace dlq user

# Replay un message
/event-trace replay <message-id>
```

**Prérequis :** Accès RabbitMQ management API

---

### `/test-contract` - Générer tests de contrat

Génère des tests PHPUnit à partir des contrats OpenAPI.

**Fonctionnalités :**
- Parse le contrat OpenAPI de l'endpoint
- Génère les tests PHPUnit correspondants
- Crée les fixtures nécessaires
- Couvre les cas : success, validation errors, auth errors, not found
- Vérifie la couverture des cas du contrat

**Usage :**
```bash
# Générer tests pour un endpoint
/test-contract POST /api/users

# Générer tests pour tout un domaine
/test-contract --domain User

# Vérifier la couverture
/test-contract --coverage
```

**Output :**
```php
// tests/User/UI/Controller/CreateUserControllerTest.php

class CreateUserControllerTest extends ApiTestCase
{
    public function testCreateUserSuccess(): void { ... }
    public function testCreateUserValidationError(): void { ... }
    public function testCreateUserUnauthorized(): void { ... }
    public function testCreateUserDuplicateEmail(): void { ... }
}
```

---

### `/service-scaffold` - Créer un nouveau microservice

Scaffolde un nouveau service avec la structure hexa/CQRS standard.

**Fonctionnalités :**
- Génère la structure `Domain/Application/Infrastructure/UI`
- Configure les buses (command.bus, query.bus, event.bus)
- Setup Docker (compose.yaml, Dockerfile)
- Génère Makefile avec targets standards
- Configure CI/CD (.gitlab-ci.yml)
- Ajoute le service dans contracts/ et blueprints/
- Configure la connexion RabbitMQ

**Usage :**
```bash
/service-scaffold inventory --domain "Gestion des stocks"
```

**Fichiers générés :**
```
inventory/
├── src/
│   └── Inventory/
│       ├── Domain/
│       │   ├── Model/
│       │   ├── Repository/
│       │   └── Event/
│       ├── Application/
│       │   ├── Command/
│       │   ├── Query/
│       │   └── Handler/
│       ├── Infrastructure/
│       │   ├── Doctrine/
│       │   ├── Messenger/
│       │   └── Http/
│       └── UI/
│           └── Controller/
├── config/
├── tests/
├── compose.yaml
├── Makefile
└── .gitlab-ci.yml
```

---

### `/hexa-refactor` - Refactorer vers architecture hexagonale

Aide à migrer du code legacy (notamment depuis core) vers architecture hexa.

**Fonctionnalités :**
- Analyse une classe/module existant
- Identifie les responsabilités (domain, application, infrastructure)
- Propose le découpage Domain/Application/Infrastructure
- Génère les interfaces (ports)
- Crée les adapters
- Suggère les tests à ajouter

**Usage :**
```bash
# Analyser une classe
/hexa-refactor src/Legacy/UserService.php

# Refactorer vers un nouveau domaine
/hexa-refactor src/Legacy/UserService.php --target src/User/
```

**Output :**
```markdown
## Analyse de UserService.php

### Responsabilités identifiées
- **Domain** : UserEntity, validation rules
- **Application** : CreateUser, UpdateUser commands
- **Infrastructure** : DoctrineUserRepository, EmailNotifier

### Découpage proposé
src/User/
├── Domain/
│   ├── Model/User.php (entity pure)
│   ├── Repository/UserRepositoryInterface.php (port)
│   └── Service/UserValidator.php
├── Application/
│   ├── Command/CreateUserCommand.php
│   └── Handler/CreateUserHandler.php
└── Infrastructure/
    ├── Doctrine/DoctrineUserRepository.php (adapter)
    └── Notification/EmailUserNotifier.php (adapter)

Procéder au refactoring ?
```

---

### `/migration-helper` - Aide aux migrations

Aide aux migrations Doctrine, PHP, Symfony.

**Fonctionnalités :**
- Génère les migrations Doctrine avec diff intelligent
- Vérifie la compatibilité PHP 8.x (détecte deprecations)
- Guide les upgrades Symfony (5.4 → 6.x → 7.x)
- Analyse les breaking changes des dépendances
- Suggère les fixes pour les deprecations

**Usage :**
```bash
# Générer une migration Doctrine
/migration-helper doctrine

# Vérifier compatibilité PHP 8.4
/migration-helper php 8.4

# Guide upgrade Symfony
/migration-helper symfony 7.0

# Analyser les deprecations
/migration-helper deprecations
```

---

## Bouton interactif Slack pour CR

**Contexte :** Actuellement, après le MP "Pipeline OK", l'utilisateur doit lancer `/notify-cr` manuellement. Idéalement, un bouton dans le MP permettrait de poster directement dans le channel.

**Implémentation possible :**
- Créer une Slack App avec Interactive Components
- Héberger un endpoint HTTP (Lambda, Cloud Function, ou serveur)
- Le bouton envoie un payload à l'endpoint
- L'endpoint poste dans le channel + fait la transition Jira

**Complexité :** Nécessite infrastructure externe (hosting de l'endpoint)

**Alternative explorée :** Slack Workflow Builder (limité, pas d'appel API externe)

**Priorité :** 🟡 P3 (nice-to-have, gain marginal vs `/notify-cr`)
