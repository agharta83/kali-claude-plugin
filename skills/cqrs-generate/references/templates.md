# Templates CQRS

Templates PHP pour la génération de code CQRS.

## Placeholders

| Placeholder | Description | Exemple |
|-------------|-------------|---------|
| `{{DOMAIN}}` | Nom du domaine | `Calendar` |
| `{{NAME}}` | Nom sans suffixe | `CreateUser` |
| `{{IMPORTS}}` | Use statements | `use App\User\Domain\ValueObject\UserUuid;` |
| `{{FIELDS}}` | Propriétés du constructeur | `public string $email,` |
| `{{EVENT_INTERFACE}}` | Interface de l'event | `AsyncEventInterface` |
| `{{EVENT_INTERFACE_IMPORT}}` | Import de l'interface | `use App\Shared\Domain\Event\AsyncEventInterface;` |

---

## Command

### CommandClass

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Application\Command;

{{IMPORTS}}
use Obat\Common\Shared\Command\CommandInterface;

final readonly class {{NAME}}Command implements CommandInterface
{
    public function __construct(
{{FIELDS}}
    ) {}
}
```

### CommandHandler

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Application\Handler;

use App\{{DOMAIN}}\Application\Command\{{NAME}}Command;
use Obat\Common\Shared\Command\CommandHandlerInterface;

final readonly class {{NAME}}Handler implements CommandHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    public function __invoke({{NAME}}Command $command): void
    {
        // TODO: implement
    }
}
```

---

## Query

### QueryClass

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Application\Query;

{{IMPORTS}}
use Obat\Common\Shared\Query\QueryInterface;

final readonly class {{NAME}}Query implements QueryInterface
{
    public function __construct(
{{FIELDS}}
    ) {}
}
```

### QueryHandler

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Application\Handler;

use App\{{DOMAIN}}\Application\Query\{{NAME}}Query;
use Obat\Common\Shared\Query\QueryHandlerInterface;

final readonly class {{NAME}}Handler implements QueryHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    /**
     * @return mixed // TODO: specify return type
     */
    public function __invoke({{NAME}}Query $query): mixed
    {
        // TODO: implement
    }
}
```

---

## Event

### EventClass (sync)

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Domain\Event;

{{IMPORTS}}
use Obat\Common\Shared\Event\EventInterface;

final readonly class {{NAME}}Event implements EventInterface
{
    public function __construct(
{{FIELDS}}
    ) {}
}
```

### EventClass (async)

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Domain\Event;

{{IMPORTS}}
use App\Shared\Domain\Event\AsyncEventInterface;

final readonly class {{NAME}}Event implements AsyncEventInterface
{
    public \DateTimeImmutable $occurredAt;

    public function __construct(
{{FIELDS}}
    ) {
        $this->occurredAt = new \DateTimeImmutable();
    }
}
```

### EventClass (external)

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Domain\Event;

{{IMPORTS}}
use App\Shared\Domain\Event\AsyncEventInterface;

final readonly class {{NAME}}Event implements AsyncEventInterface
{
    public \DateTimeImmutable $occurredAt;

    public function __construct(
{{FIELDS}}
    ) {
        $this->occurredAt = new \DateTimeImmutable();
    }

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return [
{{TO_ARRAY_FIELDS}}
            'occurredAt' => $this->occurredAt->format('Y-m-d H:i:s'),
        ];
    }
}
```

### EventSubscriber

```php
<?php

declare(strict_types=1);

namespace App\{{DOMAIN}}\Application\EventSubscriber\{{NAME}}Event;

use App\{{DOMAIN}}\Domain\Event\{{NAME}}Event;
use Obat\Common\Shared\Event\EventHandlerInterface;

final readonly class Handle{{NAME}}Subscriber implements EventHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    public function __invoke({{NAME}}Event $event): void
    {
        // TODO: implement
    }
}
```

---

## Exemples de génération

### Exemple 1 : Command avec ValueObjects

Input :
```bash
/cqrs-generate command CreateCalendarEvent --domain Calendar --fields "calendarTypeUuid:CalendarTypeUuid, startDate:DateTimeImmutable, description:?string"
```

Génère :

**src/Calendar/Application/Command/CreateCalendarEventCommand.php**
```php
<?php

declare(strict_types=1);

namespace App\Calendar\Application\Command;

use App\Calendar\Domain\ValueObject\CalendarTypeUuid;
use Obat\Common\Shared\Command\CommandInterface;

final readonly class CreateCalendarEventCommand implements CommandInterface
{
    public function __construct(
        public CalendarTypeUuid $calendarTypeUuid,
        public \DateTimeImmutable $startDate,
        public ?string $description,
    ) {}
}
```

### Exemple 2 : Event async

Input :
```bash
/cqrs-generate event CalendarEventCreated --domain Calendar --async --fields "calendarEventUuid:string, userUuid:string"
```

Génère :

**src/Calendar/Domain/Event/CalendarEventCreatedEvent.php**
```php
<?php

declare(strict_types=1);

namespace App\Calendar\Domain\Event;

use App\Shared\Domain\Event\AsyncEventInterface;

final readonly class CalendarEventCreatedEvent implements AsyncEventInterface
{
    public \DateTimeImmutable $occurredAt;

    public function __construct(
        public string $calendarEventUuid,
        public string $userUuid,
    ) {
        $this->occurredAt = new \DateTimeImmutable();
    }
}
```

**src/Calendar/Application/EventSubscriber/CalendarEventCreatedEvent/HandleCalendarEventCreatedSubscriber.php**
```php
<?php

declare(strict_types=1);

namespace App\Calendar\Application\EventSubscriber\CalendarEventCreatedEvent;

use App\Calendar\Domain\Event\CalendarEventCreatedEvent;
use Obat\Common\Shared\Event\EventHandlerInterface;

final readonly class HandleCalendarEventCreatedSubscriber implements EventHandlerInterface
{
    public function __construct(
        // TODO: inject dependencies
    ) {}

    public function __invoke(CalendarEventCreatedEvent $event): void
    {
        // TODO: implement
    }
}
```

### Exemple 3 : Event external

Input :
```bash
/cqrs-generate event UserDeactivated --domain User --external --fields "userUuid:string, reason:string"
```

Génère les mêmes fichiers que `--async` plus :

**Mise à jour de config/packages/messenger.yaml** :
```yaml
framework:
    messenger:
        routing:
            # Added by /cqrs-generate
            'App\User\Domain\Event\UserDeactivatedEvent': external_event_rabbitmq
```

---

## Règles de formatage

### Indentation des champs

Chaque champ sur sa propre ligne avec 8 espaces d'indentation :

```php
    public function __construct(
        public string $field1,
        public ?int $field2,
        public UserUuid $field3,
    ) {}
```

### Ordre des imports

1. Imports du même domaine (`App\{Domain}\...`)
2. Imports de Shared (`App\Shared\...`)
3. Imports de Obat Common (`Obat\Common\...`)

Chaque groupe séparé par une ligne vide.

### Trailing comma

Toujours ajouter une virgule après le dernier paramètre du constructeur.
