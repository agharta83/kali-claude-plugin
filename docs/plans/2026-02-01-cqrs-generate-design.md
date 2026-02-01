# Design : /cqrs-generate

**Date :** 2026-02-01
**Statut :** Validé
**Priorité :** P1 (usage quotidien Obat)

## Objectif

Scaffolder du code CQRS (Commands, Queries, Events) selon les conventions Obat, en respectant l'architecture hexagonale des microservices.

## Décisions de design

| Aspect | Décision |
|--------|----------|
| Détection service/domaine | Hybride : auto-détection service, demande domaine si absent |
| Types d'events | Flags explicites : `--async`, `--external`, sync par défaut |
| Tests | Pas de génération automatique |
| Définition des champs | Inline : `--fields "email:string, userId:UserUuid"` |
| messenger.yaml | Modification automatique pour events `--external` |
| Subscribers | Toujours générés avec les events |

## Interface utilisateur

### Syntaxe de base

```bash
# Commands
/cqrs-generate command CreateUser --fields "email:string, name:string"
/cqrs-generate command DeactivateUser --domain User --fields "userId:UserUuid, reason:?string"

# Queries
/cqrs-generate query GetUserById --fields "userId:UserUuid"
/cqrs-generate query ListUsersByCompany --domain User --fields "companyUuid:CompanyUuid, page:int, limit:int"

# Events (sync interne par défaut)
/cqrs-generate event PasswordChanged --fields "userId:string, changedAt:DateTimeImmutable"

# Events async (RabbitMQ interne)
/cqrs-generate event UserCreated --async --fields "userUuid:string, email:string"

# Events externes (cross-service)
/cqrs-generate event UserDeactivated --external --fields "userUuid:string, reason:string"
```

### Comportement interactif

Si `--domain` n'est pas spécifié, le skill demande :
```
Domaine cible ? (ex: Calendar, Resource, User)
> _
```

Le service est auto-détecté depuis le répertoire git courant.

## Fichiers générés

### Command `CreateUser` (domaine `User`)

```
src/User/Application/
├── Command/
│   └── CreateUserCommand.php
└── Handler/
    └── CreateUserHandler.php
```

**CreateUserCommand.php :**
```php
<?php

declare(strict_types=1);

namespace App\User\Application\Command;

use Obat\Common\Shared\Command\CommandInterface;

final readonly class CreateUserCommand implements CommandInterface
{
    public function __construct(
        public string $email,
        public string $name,
    ) {}
}
```

**CreateUserHandler.php :**
```php
<?php

declare(strict_types=1);

namespace App\User\Application\Handler;

use App\User\Application\Command\CreateUserCommand;
use Obat\Common\Shared\Command\CommandHandlerInterface;

final readonly class CreateUserHandler implements CommandHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    public function __invoke(CreateUserCommand $command): void
    {
        // TODO: implement
    }
}
```

### Query `GetUserById` (domaine `User`)

Même structure avec `QueryInterface` et `QueryHandlerInterface`.

### Event `UserCreated --async` (domaine `User`)

```
src/User/
├── Domain/
│   └── Event/
│       └── UserCreatedEvent.php
└── Application/
    └── EventSubscriber/
        └── UserCreatedEvent/
            └── HandleUserCreatedSubscriber.php
```

**UserCreatedEvent.php :**
```php
<?php

declare(strict_types=1);

namespace App\User\Domain\Event;

use App\Shared\Domain\Event\AsyncEventInterface;

final readonly class UserCreatedEvent implements AsyncEventInterface
{
    public \DateTimeImmutable $occurredAt;

    public function __construct(
        public string $userUuid,
        public string $email,
    ) {
        $this->occurredAt = new \DateTimeImmutable();
    }
}
```

**HandleUserCreatedSubscriber.php :**
```php
<?php

declare(strict_types=1);

namespace App\User\Application\EventSubscriber\UserCreatedEvent;

use App\User\Domain\Event\UserCreatedEvent;
use Obat\Common\Shared\Event\EventHandlerInterface;

final readonly class HandleUserCreatedSubscriber implements EventHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    public function __invoke(UserCreatedEvent $event): void
    {
        // TODO: implement
    }
}
```

### Interfaces selon le type d'event

| Flag | Interface | Transport |
|------|-----------|-----------|
| (aucun) | `EventInterface` | Sync, même process |
| `--async` | `AsyncEventInterface` | `event_rabbitmq` |
| `--external` | `AsyncEventInterface` + serializer | `external_event_rabbitmq` |

## Mise à jour messenger.yaml

### Quand modifier ?

| Type | Action sur messenger.yaml |
|------|---------------------------|
| Command/Query | Aucune (auto-registered via `_instanceof`) |
| Event sync | Aucune |
| Event `--async` | Aucune (routed via `AsyncEventInterface`) |
| Event `--external` | **Ajoute le routing explicite** |

### Pour un Event `--external`

Le skill ajoute dans `config/packages/messenger.yaml` :

```yaml
framework:
    messenger:
        routing:
            # Added by /cqrs-generate
            'App\User\Domain\Event\UserDeactivatedEvent': external_event_rabbitmq
```

## Parsing des champs

### Syntaxe

```
--fields "nom:Type, nom2:?Type2, nom3:Type3"
```

- `:` sépare nom et type
- `?` préfixe = nullable
- `,` sépare les champs

### Mapping des types

| Input | PHP Type | Import nécessaire |
|-------|----------|-------------------|
| `string` | `string` | - |
| `int` | `int` | - |
| `float` | `float` | - |
| `bool` | `bool` | - |
| `array` | `array` | - |
| `DateTimeImmutable` | `\DateTimeImmutable` | - |
| `UserUuid` | `UserUuid` | `App\User\Domain\ValueObject\UserUuid` |
| `CompanyUuid` | `CompanyUuid` | `App\Shared\Domain\ValueObject\CompanyUuid` |
| `*Uuid` | Pattern détecté | Cherche dans le domaine ou `Shared` |

### Résolution des imports

Pour un type comme `UserUuid` dans le domaine `Calendar` :

1. Chercher `src/Calendar/Domain/ValueObject/UserUuid.php`
2. Si absent, chercher `src/Shared/Domain/ValueObject/UserUuid.php`
3. Si absent, chercher `src/*/Domain/ValueObject/UserUuid.php`
4. Si toujours absent, utiliser le namespace du domaine cible avec un `// TODO: fix import`

## Workflow d'exécution

```
1. PARSE ARGUMENTS
   ├── Type : command | query | event
   ├── Nom : CreateUser, GetUserById, UserCreated...
   ├── Flags : --async, --external, --domain
   └── Champs : --fields "..."

2. DETECT CONTEXT
   ├── Service : depuis git root (operation, user...)
   ├── Domaine : depuis --domain ou demande interactive
   └── Valider que src/{Domain}/ existe

3. RESOLVE TYPES
   ├── Parser les champs
   ├── Résoudre les imports (ValueObjects)
   └── Détecter les types inconnus

4. GENERATE FILES
   ├── Command/Query : 2 fichiers (message + handler)
   └── Event : 2 fichiers (event + subscriber)

5. UPDATE CONFIG (si --external)
   └── Ajouter routing dans messenger.yaml

6. REPORT
   └── Liste des fichiers créés/modifiés
```

## Output type

```
🔍 Service détecté : operation
📁 Domaine : Calendar

✅ Fichiers créés :
   - src/Calendar/Application/Command/CreateCalendarEventCommand.php
   - src/Calendar/Application/Handler/CreateCalendarEventHandler.php

📋 Prochaines étapes :
   1. Implémenter la logique dans CreateCalendarEventHandler
   2. Injecter les dépendances nécessaires (repositories, services)
   3. Écrire les tests
```

## Structure du skill

```
skills/cqrs-generate/
├── SKILL.md                 # Instructions principales
└── references/
    └── templates.md         # Templates PHP pour génération
```

## Architecture de référence (service operation)

Basé sur l'analyse de `/home/audrey/Obat/operation` :

### Conventions de nommage

| Composant | Pattern | Exemple |
|-----------|---------|---------|
| Command | `{Action}{Entity}Command` | `CreateUserCommand` |
| Query | `Get{Entity}Query` | `GetCalendarEventsQuery` |
| Handler | `{Action}{Entity}Handler` | `CreateUserHandler` |
| Event | `{Entity}{Action}Event` | `CalendarEventCreatedEvent` |
| Subscriber | `Handle{Event}Subscriber` | `HandleUserCreatedSubscriber` |

### Interfaces Obat

- `Obat\Common\Shared\Command\CommandInterface`
- `Obat\Common\Shared\Command\CommandHandlerInterface`
- `Obat\Common\Shared\Query\QueryInterface`
- `Obat\Common\Shared\Query\QueryHandlerInterface`
- `Obat\Common\Shared\Event\EventInterface`
- `App\Shared\Domain\Event\AsyncEventInterface`
- `Obat\Common\Shared\Event\EventHandlerInterface`

### Auto-registration (services.yaml)

```yaml
_instanceof:
  Obat\Common\Shared\Command\CommandHandlerInterface:
    tags: [{ name: messenger.message_handler, bus: command.bus }]
  Obat\Common\Shared\Query\QueryHandlerInterface:
    tags: [{ name: messenger.message_handler, bus: query.bus }]
  Obat\Common\Shared\Event\EventHandlerInterface:
    tags: [{ name: messenger.message_handler, bus: event.bus }]
```

## Intégration

**Utilisé avec :**
- `/workflow` - Peut être appelé pendant l'implémentation
- `/impact-analysis` - Vérifier l'impact des nouveaux events

**Non intégré à :**
- `/finish-branch` - Pas de gate automatique (scaffolding manuel)
