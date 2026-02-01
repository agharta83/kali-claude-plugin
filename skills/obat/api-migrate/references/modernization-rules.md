# Règles de modernisation PHP 8 / Symfony

## Vue d'ensemble

Lors de la migration, appliquer ces modernisations pour profiter des features PHP 8+ et des best practices Symfony.

---

## PHP 8 Features

### Readonly classes

**Avant (annotations) :**
```php
final class GetDocumentsQuery
{
    private string $companyUuid;
    private ?string $clientUuid;

    public function __construct(string $companyUuid, ?string $clientUuid = null)
    {
        $this->companyUuid = $companyUuid;
        $this->clientUuid = $clientUuid;
    }

    public function getCompanyUuid(): string { return $this->companyUuid; }
    public function getClientUuid(): ?string { return $this->clientUuid; }
}
```

**Après (PHP 8.2+) :**
```php
final readonly class GetDocumentsQuery implements QueryInterface
{
    public function __construct(
        public string $companyUuid,
        public ?string $clientUuid = null,
    ) {}
}
```

### Constructor property promotion

**Avant :**
```php
public function __construct(
    DocumentRepositoryInterface $repository,
    EventBusInterface $eventBus
) {
    $this->repository = $repository;
    $this->eventBus = $eventBus;
}
```

**Après :**
```php
public function __construct(
    private readonly DocumentRepositoryInterface $repository,
    private readonly EventBusInterface $eventBus,
) {}
```

### Named arguments

**Avant :**
```php
$command = new CreateDocumentCommand(
    $uuid,
    $reference,
    $status,
    null,  // clientUuid
    null,  // siteUuid
    true   // notify
);
```

**Après :**
```php
$command = new CreateDocumentCommand(
    uuid: $uuid,
    reference: $reference,
    status: $status,
    notify: true,
);
```

### Enums

**Avant :**
```php
class DocumentStatus
{
    public const DRAFT = 'draft';
    public const SENT = 'sent';
    public const PAID = 'paid';
}

// Usage
$status = DocumentStatus::DRAFT;
```

**Après :**
```php
enum DocumentStatus: string
{
    case Draft = 'draft';
    case Sent = 'sent';
    case Paid = 'paid';
}

// Usage
$status = DocumentStatus::Draft;
```

### Match expressions

**Avant :**
```php
switch ($status) {
    case 'draft':
        return 'En brouillon';
    case 'sent':
        return 'Envoyé';
    default:
        return 'Inconnu';
}
```

**Après :**
```php
return match($status) {
    DocumentStatus::Draft => 'En brouillon',
    DocumentStatus::Sent => 'Envoyé',
    default => 'Inconnu',
};
```

### Nullsafe operator

**Avant :**
```php
$name = $document->getClient() !== null
    ? $document->getClient()->getName()
    : null;
```

**Après :**
```php
$name = $document->getClient()?->getName();
```

---

## Symfony Attributs (vs Annotations)

### Routes

**Avant (annotation) :**
```php
/**
 * @Route("/api/documents", methods={"GET"})
 */
public function list(): Response
```

**Après (attribut) :**
```php
#[Route('/api/documents', methods: ['GET'])]
public function list(): Response
```

### Security

**Avant :**
```php
/**
 * @IsGranted("ROLE_USER")
 * @Security("is_granted('READ', document)")
 */
```

**Après :**
```php
#[IsGranted('ROLE_USER')]
#[IsGranted('READ', subject: 'document')]
```

### Validation

**Avant :**
```php
/**
 * @Assert\NotBlank()
 * @Assert\Length(min=3, max=255)
 */
private string $name;
```

**Après :**
```php
#[Assert\NotBlank]
#[Assert\Length(min: 3, max: 255)]
public string $name;
```

### Serialization Groups

**Avant :**
```php
/**
 * @Groups({"document:read", "document:list"})
 */
private string $reference;
```

**Après :**
```php
#[Groups(['document:read', 'document:list'])]
public string $reference;
```

### Doctrine ORM

**Avant :**
```php
/**
 * @ORM\Entity(repositoryClass=DocumentRepository::class)
 * @ORM\Table(name="documents")
 */
class Document
{
    /**
     * @ORM\Id
     * @ORM\Column(type="uuid")
     */
    private UuidInterface $uuid;

    /**
     * @ORM\ManyToOne(targetEntity=Client::class)
     * @ORM\JoinColumn(nullable=false)
     */
    private Client $client;
}
```

**Après :**
```php
#[ORM\Entity(repositoryClass: DocumentRepository::class)]
#[ORM\Table(name: 'documents')]
class Document
{
    #[ORM\Id]
    #[ORM\Column(type: 'uuid')]
    private UuidInterface $uuid;

    #[ORM\ManyToOne(targetEntity: Client::class)]
    #[ORM\JoinColumn(nullable: false)]
    private Client $client;
}
```

---

## Architecture CQRS Best Practices

### Séparation Query/Command

**Principe :** Une Query ne modifie jamais l'état, une Command ne retourne jamais de données (sauf ID).

```php
// Query - lecture seule
final readonly class GetDocumentQuery implements QueryInterface
{
    public function __construct(
        public DocumentUuid $documentUuid,
    ) {}
}

// Command - modification
final readonly class UpdateDocumentCommand implements CommandInterface
{
    public function __construct(
        public DocumentUuid $documentUuid,
        public string $reference,
        public DocumentStatus $status,
    ) {}
}
```

### Handlers sans logique de présentation

**Mauvais :**
```php
public function __invoke(GetDocumentQuery $query): array
{
    $doc = $this->repository->find($query->uuid);
    return [
        'uuid' => (string) $doc->uuid,
        'reference' => $doc->reference,
        // Logique de sérialisation dans le handler
    ];
}
```

**Bon :**
```php
public function __invoke(GetDocumentQuery $query): DocumentModel
{
    $doc = $this->repository->find($query->uuid);
    return DocumentModel::fromEntity($doc);
}
```

### Injection de dépendances explicite

**Mauvais :**
```php
public function __invoke(CreateDocumentCommand $command): void
{
    $repository = $this->container->get(DocumentRepository::class);
    // Service locator anti-pattern
}
```

**Bon :**
```php
public function __construct(
    private readonly DocumentRepositoryInterface $repository,
    private readonly EventBusInterface $eventBus,
) {}

public function __invoke(CreateDocumentCommand $command): void
{
    // Dépendances injectées
}
```

### Ports dans Domain

**Structure :**
```
src/Document/
├── Domain/
│   └── Port/
│       ├── DocumentRepositoryInterface.php  # Port
│       └── NotificationServiceInterface.php # Port
└── Infrastructure/
    ├── Doctrine/
    │   └── DoctrineDocumentRepository.php   # Adapter
    └── Notification/
        └── EmailNotificationService.php      # Adapter
```

### Value Objects pour les IDs

**Mauvais :**
```php
public function __construct(
    public string $documentUuid,
    public string $clientUuid,
)
```

**Bon :**
```php
public function __construct(
    public DocumentUuid $documentUuid,
    public ClientUuid $clientUuid,
)
```

---

## Checklist de modernisation

### PHP 8

- [ ] `final readonly class` pour Query/Command/Model
- [ ] Constructor property promotion
- [ ] Named arguments pour constructeurs > 3 params
- [ ] Enums pour les statuts et types
- [ ] Match expressions au lieu de switch
- [ ] Nullsafe operator (`?->`)
- [ ] Union types explicites
- [ ] Trailing comma dans les listes

### Symfony

- [ ] Attributs au lieu d'annotations
- [ ] `#[Route]` avec named parameters
- [ ] `#[IsGranted]` pour la sécurité
- [ ] `#[Assert\*]` pour la validation
- [ ] `#[Groups]` pour la sérialisation

### Architecture

- [ ] Query/Command immutables (readonly)
- [ ] Handler avec `__invoke()` typé
- [ ] Model au lieu d'array en retour
- [ ] Repository interface dans Domain
- [ ] Value Objects pour les IDs
- [ ] Pas de `$this->container->get()`
