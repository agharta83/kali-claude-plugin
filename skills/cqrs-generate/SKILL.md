---
name: cqrs-generate
description: Use when scaffolding CQRS code (Commands, Queries, Events) in Obat microservices. Generates PHP classes following hexagonal architecture conventions with proper interfaces, handlers, and subscribers.
---

# CQRS Generate

Scaffolder du code CQRS selon les conventions Obat.

**Annonce au démarrage :** "J'utilise le skill cqrs-generate pour scaffolder du code CQRS."

## Arguments

```bash
# Commands
/cqrs-generate command CreateUser --fields "email:string, name:string"
/cqrs-generate command DeactivateUser --domain User --fields "userId:UserUuid, reason:?string"

# Queries
/cqrs-generate query GetUserById --fields "userId:UserUuid"
/cqrs-generate query ListUsers --domain User --fields "companyUuid:CompanyUuid, page:int"

# Events (sync interne par défaut)
/cqrs-generate event PasswordChanged --fields "userId:string"

# Events async (RabbitMQ interne)
/cqrs-generate event UserCreated --async --fields "userUuid:string, email:string"

# Events externes (cross-service via ExternalJsonMessageSerializer)
/cqrs-generate event UserDeactivated --external --fields "userUuid:string, reason:string"
```

## Phase 1 : Parser les arguments

### 1.1 Extraire les composants

| Argument | Requis | Description |
|----------|--------|-------------|
| Type | Oui | `command`, `query`, ou `event` |
| Nom | Oui | PascalCase sans suffixe (ex: `CreateUser`, pas `CreateUserCommand`) |
| `--domain` | Non | Domaine cible (ex: `Calendar`, `User`) |
| `--fields` | Non | Champs avec types (ex: `"email:string, id:?UserUuid"`) |
| `--async` | Non | Event asynchrone (RabbitMQ interne) |
| `--external` | Non | Event externe (cross-service) |

### 1.2 Valider la syntaxe des champs

Format : `nom:Type` ou `nom:?Type` (nullable)

Types supportés :
- Primitifs : `string`, `int`, `float`, `bool`, `array`
- DateTime : `DateTimeImmutable`
- ValueObjects : `*Uuid`, `*Id`, ou tout type custom

## Phase 2 : Détecter le contexte

### 2.1 Auto-détecter le service

```bash
basename $(git rev-parse --show-toplevel)
```

Exemple : `operation` → service `operation`

### 2.2 Déterminer le domaine

Si `--domain` fourni → utiliser directement

Sinon → demander interactivement :
```
Domaine cible ? (ex: Calendar, Resource, User)
> _
```

### 2.3 Valider le domaine

Vérifier que `src/{Domain}/` existe :
```bash
ls src/{Domain}/
```

Si absent → proposer de le créer ou lister les domaines existants.

## Phase 3 : Résoudre les types

### 3.1 Parser les champs

Transformer `--fields "email:string, userId:?UserUuid"` en :

```php
[
    ['name' => 'email', 'type' => 'string', 'nullable' => false],
    ['name' => 'userId', 'type' => 'UserUuid', 'nullable' => true],
]
```

### 3.2 Résoudre les imports

Pour chaque type non-primitif (ex: `UserUuid`) :

1. Chercher `src/{Domain}/Domain/ValueObject/{Type}.php`
2. Si absent → `src/Shared/Domain/ValueObject/{Type}.php`
3. Si absent → `src/*/Domain/ValueObject/{Type}.php`
4. Si absent → marquer `// TODO: fix import`

### 3.3 Types primitifs (pas d'import)

`string`, `int`, `float`, `bool`, `array`, `\DateTimeImmutable`

## Phase 4 : Générer les fichiers

Lire les templates dans `references/templates.md` et générer les fichiers.

### 4.1 Pour une Command

| Fichier | Chemin |
|---------|--------|
| Command | `src/{Domain}/Application/Command/{Name}Command.php` |
| Handler | `src/{Domain}/Application/Handler/{Name}Handler.php` |

### 4.2 Pour une Query

| Fichier | Chemin |
|---------|--------|
| Query | `src/{Domain}/Application/Query/{Name}Query.php` |
| Handler | `src/{Domain}/Application/Handler/{Name}Handler.php` |

### 4.3 Pour un Event

| Fichier | Chemin |
|---------|--------|
| Event | `src/{Domain}/Domain/Event/{Name}Event.php` |
| Subscriber | `src/{Domain}/Application/EventSubscriber/{Name}Event/Handle{Name}Subscriber.php` |

### 4.4 Interfaces selon le type

| Type | Interface Event | Interface Handler |
|------|-----------------|-------------------|
| sync (défaut) | `Obat\Common\Shared\Event\EventInterface` | `EventHandlerInterface` |
| `--async` | `App\Shared\Domain\Event\AsyncEventInterface` | `EventHandlerInterface` |
| `--external` | `App\Shared\Domain\Event\AsyncEventInterface` | `EventHandlerInterface` |

## Phase 5 : Mettre à jour messenger.yaml

### 5.1 Quand modifier ?

| Type | Action |
|------|--------|
| Command/Query | Aucune (auto-registered via `_instanceof`) |
| Event sync | Aucune |
| Event `--async` | Aucune (routed via `AsyncEventInterface`) |
| Event `--external` | Ajouter routing explicite |

### 5.2 Pour `--external`

Lire `config/packages/messenger.yaml` et ajouter sous `framework.messenger.routing` :

```yaml
# Added by /cqrs-generate
'App\{Domain}\Domain\Event\{Name}Event': external_event_rabbitmq
```

## Phase 6 : Rapport final

Afficher :

```
🔍 Service détecté : {service}
📁 Domaine : {domain}

✅ Fichiers créés :
   - src/{Domain}/Application/Command/{Name}Command.php
   - src/{Domain}/Application/Handler/{Name}Handler.php

📋 Prochaines étapes :
   1. Implémenter la logique dans {Name}Handler
   2. Injecter les dépendances nécessaires (repositories, services)
   3. Écrire les tests
```

Pour les events `--external` :
```
✅ messenger.yaml mis à jour : routing vers external_event_rabbitmq
```

## Conventions Obat

### Nommage

| Composant | Pattern | Exemple |
|-----------|---------|---------|
| Command | `{Action}{Entity}Command` | `CreateUserCommand` |
| Query | `Get{Entity}Query` | `GetCalendarEventsQuery` |
| Handler | `{Name}Handler` | `CreateUserHandler` |
| Event | `{Entity}{Action}Event` | `UserCreatedEvent` |
| Subscriber | `Handle{Name}Subscriber` | `HandleUserCreatedSubscriber` |

### Interfaces

```php
// Commands
use Obat\Common\Shared\Command\CommandInterface;
use Obat\Common\Shared\Command\CommandHandlerInterface;

// Queries
use Obat\Common\Shared\Query\QueryInterface;
use Obat\Common\Shared\Query\QueryHandlerInterface;

// Events sync
use Obat\Common\Shared\Event\EventInterface;

// Events async
use App\Shared\Domain\Event\AsyncEventInterface;

// Subscribers
use Obat\Common\Shared\Event\EventHandlerInterface;
```

### Structure des classes

Toutes les classes CQRS sont :
- `final readonly`
- Avec constructeur à promotion de propriétés
- Sans setters

## Erreurs courantes

**Domaine inexistant**
- Symptôme : `src/{Domain}/` n'existe pas
- Solution : Créer la structure ou choisir un domaine existant

**Type non résolu**
- Symptôme : `// TODO: fix import` dans le code généré
- Solution : Créer le ValueObject ou corriger le type

**Event externe sans routing**
- Symptôme : Event non dispatché vers RabbitMQ
- Solution : Vérifier que messenger.yaml a été mis à jour
