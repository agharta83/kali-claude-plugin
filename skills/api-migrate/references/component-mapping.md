# Mapping des composants API Platform → CQRS

## Vue d'ensemble

| Source (API Platform) | Cible (Microservice CQRS) |
|----------------------|---------------------------|
| Entity + @ApiResource | Query/Command + Handler |
| Controller custom | Controller REST |
| Extension Doctrine | Logic dans Handler |
| DataProvider | Handler + Repository |
| DataPersister | Handler + Repository |
| Filter | Query params + Handler |
| Normalizer | Model + Serialization |
| Transformer | Input mapping dans Handler |
| Voter | Middleware + Handler |
| Validator | Validation dans Command/Query |
| DTO | Input/Output DTOs |

---

## Mapping détaillé

### Entity + @ApiResource → Query/Command

| Opération API Platform | CQRS |
|------------------------|------|
| `GET` collection | `Get{Entities}Query` + Handler |
| `GET` item | `Get{Entity}ByIdQuery` + Handler |
| `POST` | `Create{Entity}Command` + Handler |
| `PUT` | `Update{Entity}Command` + Handler |
| `PATCH` | `Update{Entity}Command` + Handler (partiel) |
| `DELETE` | `Delete{Entity}Command` + Handler |
| Custom read-only | Query + Handler |
| Custom avec effet | Command + Handler |

### Controller custom → Controller REST

**Source :**
```php
// src/ApiPlatform/Controller/DocumentToggleAction.php
class DocumentToggleAction {
    public function __invoke(Document $document, Request $request): Document {
        // Logic
        return $document;
    }
}
```

**Cible :**
```php
// src/Document/UI/Controller/ToggleDocumentController.php
#[Route('/api/documents/{uuid}/toggle', methods: ['PUT'])]
final readonly class ToggleDocumentController
{
    public function __construct(
        private CommandBusInterface $commandBus,
    ) {}

    public function __invoke(string $uuid): JsonResponse
    {
        $this->commandBus->dispatch(new ToggleDocumentCommand(
            documentUuid: new DocumentUuid($uuid),
        ));

        return new JsonResponse(null, Response::HTTP_NO_CONTENT);
    }
}
```

### Extension Doctrine → Handler logic

**Source :**
```php
// src/ApiPlatform/Extension/DocumentExtension.php
class DocumentExtension implements QueryCollectionExtensionInterface {
    public function applyToCollection(QueryBuilder $qb, ...): void {
        $qb->andWhere('o.company = :company')
           ->setParameter('company', $this->getCompany());

        if (!$this->hasPermission('invoice.access')) {
            $qb->andWhere('o.createdBy = :user');
        }
    }
}
```

**Cible :**
```php
// src/Document/Application/Handler/GetDocumentsHandler.php
final readonly class GetDocumentsHandler implements QueryHandlerInterface
{
    public function __invoke(GetDocumentsQuery $query): array
    {
        // Logic portée depuis Extension
        $filter = new DocumentFilter(
            companyId: $query->companyId,
            createdBy: $this->hasPermission('invoice.access')
                ? null
                : $query->userId,
        );

        return $this->repository->findByFilter($filter);
    }
}
```

### DataProvider → Handler + Repository

**Source :**
```php
// src/ApiPlatform/DataProvider/StatsDataProvider.php
class StatsDataProvider implements CollectionDataProviderInterface {
    public function getCollection(string $resourceClass, ...): iterable {
        return $this->repository->getStats($this->getCompanyId());
    }
}
```

**Cible :**
```php
// Handler délègue au Repository
public function __invoke(GetStatsQuery $query): StatsModel
{
    return $this->repository->getStats($query->companyId);
}
```

### DataPersister → Handler + Repository

**Source :**
```php
// src/ApiPlatform/DataPersister/ContactDataPersister.php
class ContactDataPersister implements DataPersisterInterface {
    public function persist($data, array $context = []) {
        // Validation custom
        // Transformation
        $this->em->persist($data);
        $this->em->flush();
        // Dispatch events
        return $data;
    }
}
```

**Cible :**
```php
// Handler gère tout
public function __invoke(CreateContactCommand $command): ContactModel
{
    // Validation dans Command
    $contact = Contact::create(
        name: $command->name,
        email: $command->email,
    );

    $this->repository->save($contact);
    // Events dispatchés par le repository

    return ContactModel::fromEntity($contact);
}
```

### Filter → Query params

**Source :**
```php
// @ApiFilter(SearchFilter::class, properties={"client.uuid": "exact"})
// @ApiFilter(CustomFreeSearchFilter::class)
```

**Cible :**
```php
// Controller extrait les params
#[Route('/api/documents')]
public function __invoke(Request $request): JsonResponse
{
    $query = new GetDocumentsQuery(
        companyUuid: $request->get('company'),
        clientUuid: $request->get('client.uuid'),
        search: $request->get('free.search'),
        page: (int) $request->get('page', 1),
    );

    return new JsonResponse($this->queryBus->handle($query));
}

// Handler applique les filtres
public function __invoke(GetDocumentsQuery $query): array
{
    $filter = new DocumentFilter(
        clientUuid: $query->clientUuid,
        search: $query->search,
    );

    return $this->repository->findByFilter($filter, $query->page);
}
```

### Normalizer → Model + Serialization

**Source :**
```php
// src/ApiPlatform/Normalizer/DocumentNormalizer.php
class DocumentNormalizer implements NormalizerInterface {
    public function normalize($object, ...): array {
        $data = $this->normalizer->normalize($object, ...);

        // Computed properties
        $data['invoiceInfo'] = $this->getInvoiceInfo($object);
        $data['isOverdue'] = $object->isOverdue();

        return $data;
    }
}
```

**Cible :**
```php
// Model inclut les propriétés calculées
final readonly class DocumentModel
{
    public function __construct(
        public string $uuid,
        public string $reference,
        public DocumentStatus $status,
        public InvoiceInfo $invoiceInfo,  // Computed
        public bool $isOverdue,           // Computed
    ) {}

    public static function fromEntity(Document $doc): self
    {
        return new self(
            uuid: (string) $doc->uuid,
            reference: $doc->reference,
            status: $doc->status,
            invoiceInfo: InvoiceInfo::fromDocument($doc),
            isOverdue: $doc->isOverdue(),
        );
    }
}
```

### Voter → Middleware + Handler

**Source :**
```php
// src/Security/Voter/DocumentVoter.php
class DocumentVoter extends Voter {
    protected function voteOnAttribute($attribute, $subject, $token): bool {
        return match($attribute) {
            'READ' => $this->canRead($subject, $token->getUser()),
            'UPDATE' => $this->canUpdate($subject, $token->getUser()),
        };
    }

    private function canRead(Document $doc, User $user): bool {
        return $user->hasCompany($doc->getCompany())
            && ($this->hasPermission('invoice.access')
                || $doc->getCreatedBy() === $user);
    }
}
```

**Cible :**
```php
// Middleware vérifie les permissions générales
// services.yaml
command.bus:
    middleware:
        - App\Security\Middleware\CheckUserPermissionsMiddleware

// Handler vérifie les règles métier
public function __invoke(GetDocumentQuery $query): DocumentModel
{
    $document = $this->repository->find($query->documentUuid);

    // Check accès (logique du Voter)
    if (!$this->canAccess($document, $query->userId)) {
        throw new AccessDeniedException();
    }

    return DocumentModel::fromEntity($document);
}
```

### Transformer → Input mapping

**Source :**
```php
// src/ApiPlatform/DataTransformer/DocumentChangeStatusTransformer.php
class DocumentChangeStatusTransformer implements DataTransformerInterface {
    public function transform($object, string $to, array $context = []) {
        $document = $context[AbstractNormalizer::OBJECT_TO_POPULATE];
        $document->setStatus($object->status);
        return $document;
    }
}
```

**Cible :**
```php
// Controller mappe l'input vers Command
public function __invoke(string $uuid, Request $request): JsonResponse
{
    $data = json_decode($request->getContent(), true);

    $command = new ChangeDocumentStatusCommand(
        documentUuid: new DocumentUuid($uuid),
        status: DocumentStatus::from($data['status']),
    );

    $this->commandBus->dispatch($command);

    return new JsonResponse(null, Response::HTTP_NO_CONTENT);
}
```

---

## Patterns de transformation

### Collection → Pagination

**Source :**
```php
@ApiResource(
    attributes={
        "pagination_items_per_page"=25,
        "pagination_client_items_per_page"=true
    }
)
```

**Cible :**
```php
final readonly class GetDocumentsQuery implements QueryInterface
{
    public function __construct(
        public int $page = 1,
        public int $limit = 25,
    ) {}
}

// Handler retourne PaginatedResult
public function __invoke(GetDocumentsQuery $query): PaginatedResult
{
    return $this->repository->findPaginated(
        page: $query->page,
        limit: min($query->limit, 100), // Max cap
    );
}
```

### Serialization Groups → Model properties

**Source :**
```php
#[Groups(['Document:output', 'Document:list'])]
private string $reference;

#[Groups(['Document:output'])] // Pas dans list
private string $description;
```

**Cible :**
```php
// Deux Models selon le contexte
final readonly class DocumentListItemModel { ... }  // Sans description
final readonly class DocumentModel { ... }          // Avec description

// Ou attributs de serialization
#[Groups(['list', 'detail'])]
public string $reference;

#[Groups(['detail'])]
public string $description;
```
