# Design : /api-migrate

**Date :** 2026-02-01
**Statut :** Validé
**Priorité :** P1 (migration monorepo → microservices)

## Objectif

Faciliter la migration d'endpoints API Platform depuis le monorepo `core` vers les microservices Obat, avec analyse complète des composants, suggestions d'amélioration, et garantie de non-régression.

## Décisions de design

| Aspect | Décision |
|--------|----------|
| Nom | `/api-migrate` |
| Identification endpoint | Par URL : `METHOD /path` |
| Service cible | Paramètre obligatoire `--target` |
| Analyse | Complète (tous composants API Platform) |
| Génération | Rapport par défaut, code avec `--generate` |
| Vérification BC | Checklist + comparaison OpenAPI |
| Suggestions | Modernisation PHP 8 + architecture hexa/CQRS |

## Interface utilisateur

### Syntaxe de base

```bash
# Analyse d'un endpoint (rapport uniquement)
/api-migrate GET /api/documents --target accounting

# Analyse + génération de code
/api-migrate POST /api/cdn_files --target user --generate

# Endpoint avec paramètre
/api-migrate GET /api/documents/{uuid} --target accounting

# Opération custom API Platform
/api-migrate PUT /api/documents/change_status/{uuid} --target accounting
```

### Paramètres

| Argument | Requis | Description |
|----------|--------|-------------|
| `METHOD` | Oui | GET, POST, PUT, PATCH, DELETE |
| `PATH` | Oui | Chemin de l'endpoint (ex: `/api/documents`) |
| `--target` | Oui | Service cible (ex: `accounting`, `operation`) |
| `--generate` | Non | Génère le code dans le service cible |
| `--domain` | Non | Domaine cible dans le service (sinon demandé) |

## Analyse de l'endpoint source

### Phase 1 : Localiser l'endpoint

Le skill cherche dans `/home/audrey/Obat/core` :

1. **Trouver l'entité** via les annotations `@ApiResource`
   - Scanner `src/Entity/**/*.php`
   - Matcher le path dans `collectionOperations` ou `itemOperations`

2. **Extraire la configuration** de l'opération :
   - Method, path, controller custom
   - Security expressions
   - Input/Output DTOs
   - Serialization groups
   - Filters déclarés

### Phase 2 : Découvrir les composants liés

| Composant | Où chercher |
|-----------|-------------|
| **Controller** | `src/ApiPlatform/Controller/` |
| **Extensions Doctrine** | `src/ApiPlatform/Extension/` |
| **Data Providers** | `src/ApiPlatform/DataProvider/` |
| **Data Persisters** | `src/ApiPlatform/DataPersister/` |
| **Filters** | `src/ApiPlatform/Filter/` |
| **Normalizers** | `src/ApiPlatform/Normalizer/` |
| **Transformers** | `src/ApiPlatform/DataTransformer/` |
| **Validators** | `src/ApiPlatform/Validator/` |
| **Voters** | `src/Security/Voter/` |
| **DTOs** | `src/ApiPlatform/DTO/` |

### Phase 3 : Analyser les dépendances

Pour chaque composant trouvé :
- Services injectés (repositories, autres services)
- Entités liées (relations Doctrine)
- Events dispatchés

## Rapport d'analyse

### Structure du rapport

```markdown
## Analyse de migration : GET /api/documents

### Source (monorepo core)

**Entité :** `src/Entity/Invoicing/Document.php`
**Opération :** `get` (collection)

---

### Composants détectés

| Type | Fichier | Rôle |
|------|---------|------|
| Extension | `DocumentExtension.php` | Filtre par company + permissions |
| Extension | `BaseCheckCompanyExtension.php` | Multi-tenancy |
| Filter | `CustomClientNameDocumentFilter.php` | Recherche client |
| Filter | `CompanyUuidFilter.php` | Filtre company |
| Normalizer | `DocumentNormalizer.php` | Enrichit la response |
| Voter | `DocumentVoter.php` | Autorisations READ/UPDATE |

---

### Sécurité

| Expression | Niveau |
|------------|--------|
| `is_granted('ROLE_USER')` | Ressource |
| `is_granted('READ', object)` | Item |

**Permissions vérifiées (DocumentVoter) :**
- `client.all_data` ou `invoice.access`
- Appartenance à la company

---

### Serialization

| Context | Groups |
|---------|--------|
| Output | `Document:output`, `Document:list` |
| Input | `Document:input` |

**Champs exposés :** uuid, reference, status, client, site, totalHt, totalTtc, ...

---

### Filtres disponibles

| Filtre | Paramètre | Type |
|--------|-----------|------|
| SearchFilter | `client.uuid` | exact |
| SearchFilter | `site.uuid` | exact |
| OrderFilter | `reference`, `status`, `updatedAt` | asc/desc |
| DateFilter | `createdAt`, `updatedAt` | range |
| CustomFreeSearchFilter | `free.search` | fulltext |
```

## Mapping vers le microservice

### Transformation source → cible

| Source (core) | Cible (microservice) | Type |
|---------------|---------------------|------|
| Entity + GET collection | `GetDocumentsQuery` | Query CQRS |
| Entity + GET item | `GetDocumentByIdQuery` | Query CQRS |
| Entity + POST | `CreateDocumentCommand` | Command CQRS |
| Entity + PATCH | `UpdateDocumentCommand` | Command CQRS |
| Entity + DELETE | `DeleteDocumentCommand` | Command CQRS |
| Custom operation | Command ou Query selon sémantique | CQRS |
| Extension Doctrine | Logic dans Handler | Handler |
| Voter | Middleware + Handler | Security |
| Normalizer | Model + Serialization | Model |
| Filter | Query params dans Controller | Filter |
| DataProvider | Handler + Repository | Infrastructure |
| DataPersister | Handler + Repository | Infrastructure |
| DataTransformer | Input DTO mapping | Application |

### Architecture cible proposée

```
src/{Domain}/
├── Application/
│   ├── Query/
│   │   └── Get{Entity}Query.php
│   ├── Command/
│   │   └── Create{Entity}Command.php
│   └── Handler/
│       ├── Get{Entity}Handler.php
│       └── Create{Entity}Handler.php
├── Domain/
│   ├── Model/
│   │   └── {Entity}Model.php
│   └── Port/
│       └── {Entity}RepositoryInterface.php
├── Infrastructure/
│   └── Doctrine/
│       └── Doctrine{Entity}Repository.php
└── UI/
    └── Controller/
        └── {Entity}Controller.php
```

### Suggestions d'amélioration

**Modernisation PHP 8 :**
- `readonly class` pour Query, Command et Model
- Attributs au lieu d'annotations (`#[Route]`, `#[IsGranted]`)
- Constructor property promotion
- Named arguments pour clarté
- Union types et nullable types explicites

**Architecture CQRS :**
- Query/Command séparée du Controller (SRP)
- Handler avec injection de dépendances explicite
- Model de retour typé (pas d'array)
- Repository interface dans Domain (ports)
- Pas de couplage direct à Doctrine dans Application

## Vérification de non-régression

### Comparaison avec le contrat OpenAPI

Si `api-contracts/docs/obat-{service}/` existe :

```markdown
### Vérification du contrat OpenAPI

**Contrat :** `api-contracts/docs/obat-accounting/external.openapi.yaml`

| Aspect | Contrat | Source | Status |
|--------|---------|--------|--------|
| Path | `GET /api/documents` | `GET /api/documents` | ✅ Match |
| Response 200 | `DocumentCollection` | Groups: `Document:output` | ⚠️ Vérifier |
| Pagination | `page`, `itemsPerPage` | Server-side 25 | ✅ Match |
| Filter `client.uuid` | query param | SearchFilter | ✅ Match |
| Filter `status` | query param | Non déclaré | 🔴 Manquant |

**Actions requises :**
1. Ajouter le filtre `status` dans le service cible
2. Vérifier que tous les champs de `DocumentCollection` sont présents
```

### Checklist de non-régression

```markdown
### Checklist BC

**Response :**
- [ ] Même structure JSON (champs, types, nesting)
- [ ] Mêmes status codes (200, 400, 401, 403, 404)
- [ ] Même format de pagination (`hydra:member`, `hydra:totalItems`)
- [ ] Mêmes headers (Content-Type, Cache-Control)

**Filtres :**
- [ ] Tous les query params supportés
- [ ] Même comportement de recherche (exact, partial, iexact)
- [ ] Même tri par défaut

**Sécurité :**
- [ ] Mêmes rôles requis (`ROLE_USER`)
- [ ] Même logique d'accès (company, permissions)
- [ ] Mêmes cas de 403

**Performance :**
- [ ] Pagination identique
- [ ] Pas de N+1 queries introduites
```

## Workflow d'exécution

```
1. PARSE ARGUMENTS
   ├── Method + Path
   ├── --target (service cible)
   └── --generate, --domain (optionnels)

2. LOCATE ENDPOINT (dans core)
   ├── Scanner src/Entity/**/*.php
   ├── Parser @ApiResource annotations
   └── Matcher l'opération (method + path)

3. DISCOVER COMPONENTS
   ├── Controllers, Extensions, Providers
   ├── Filters, Normalizers, Transformers
   ├── Voters, Validators, DTOs
   └── Dépendances (services, repositories)

4. ANALYZE SECURITY
   ├── Expressions security/security_post_denormalize
   ├── Voters et permissions
   └── Multi-tenancy (company filtering)

5. CHECK CONTRACT (si existe)
   ├── Lire api-contracts/docs/obat-{target}/
   ├── Comparer avec l'endpoint source
   └── Identifier les écarts

6. GENERATE REPORT
   ├── Composants détectés
   ├── Mapping source → cible
   ├── Suggestions d'amélioration
   └── Checklist BC

7. GENERATE CODE (si --generate)
   ├── Query/Command + Handler
   ├── Controller
   ├── Model
   └── Repository interface
```

## Structure du skill

```
skills/api-migrate/
├── SKILL.md
└── references/
    ├── component-mapping.md    # Mapping API Platform → CQRS
    ├── modernization-rules.md  # Règles PHP 8 / attributs
    └── bc-checklist.md         # Checklist complète BC
```

## Intégration

**Utilisé avec :**
- `/contract-check` - Vérifier le contrat après migration
- `/impact-analysis` - Identifier les consommateurs de l'endpoint
- `/cqrs-generate` - Peut être appelé pour générer les composants CQRS

**Remplace :**
- `/hexa-refactor` - Ce skill est plus spécifique et adapté à la migration API Platform

## Architecture API Platform du monorepo (référence)

### Composants clés

| Composant | Rôle | Exemple |
|-----------|------|---------|
| `@ApiResource` | Définition des endpoints | `Document.php` |
| Controller | Logique custom | `CdnFileUploadAction.php` |
| Extension | Modification des queries | `DocumentExtension.php` |
| DataProvider | Source de données custom | `UserParameterDataProvider.php` |
| DataPersister | Persistance custom | `ContactDataPersister.php` |
| Filter | Filtrage des collections | `CustomFreeSearchFilter.php` |
| Normalizer | Transformation output | `DocumentNormalizer.php` |
| Transformer | Transformation input | `DocumentChangeStatusDataTransformer.php` |
| Voter | Autorisation | `DocumentVoter.php` |
| Validator | Validation métier | `DocumentDeleteValidator.php` |

### Patterns de sécurité

```php
// Niveau ressource
attributes={"security"="is_granted('ROLE_USER')"}

// Niveau opération
"security" = "is_granted('READ', object)"
"security_post_denormalize" = "is_granted('CREATE', object)"
```

### Multi-tenancy

`BaseCheckCompanyExtension` applique automatiquement le filtrage par company sur toutes les entités.
