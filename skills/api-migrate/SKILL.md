---
name: api-migrate
description: Use when migrating API Platform endpoints from the Obat monorepo (core) to microservices. Analyzes controllers, extensions, providers, filters, normalizers, voters and generates migration report with improvement suggestions and BC checklist.
---

# API Migrate

Migrer des endpoints API Platform depuis le monorepo `core` vers les microservices Obat.

**Annonce au démarrage :** "J'utilise le skill api-migrate pour analyser et migrer l'endpoint."

## Arguments

```bash
# Analyse d'un endpoint (rapport uniquement)
/api-migrate GET /api/documents --target accounting

# Analyse + génération de code
/api-migrate POST /api/cdn_files --target user --generate

# Endpoint avec paramètre
/api-migrate GET /api/documents/{uuid} --target accounting

# Opération custom API Platform
/api-migrate PUT /api/documents/change_status/{uuid} --target accounting --domain Document
```

| Argument | Requis | Description |
|----------|--------|-------------|
| `METHOD` | Oui | GET, POST, PUT, PATCH, DELETE |
| `PATH` | Oui | Chemin de l'endpoint |
| `--target` | Oui | Service cible (accounting, operation, user, etc.) |
| `--generate` | Non | Génère le code dans le service cible |
| `--domain` | Non | Domaine cible (sinon demandé interactivement) |

## Phase 1 : Localiser l'endpoint

### 1.1 Scanner le monorepo

Chercher dans `/home/audrey/Obat/core/src/Entity/**/*.php` les annotations `@ApiResource`.

### 1.2 Parser les opérations

Extraire de l'annotation `@ApiResource` :
- `collectionOperations` (GET list, POST)
- `itemOperations` (GET item, PATCH, DELETE)
- Opérations custom avec `path` explicite

### 1.3 Matcher l'endpoint

Comparer `METHOD + PATH` avec les opérations déclarées.

Si non trouvé → Stopper : "Endpoint non trouvé dans le monorepo."

Afficher :
```
📍 Endpoint trouvé
Entité : src/Entity/Invoicing/Document.php
Opération : get (collection)
```

## Phase 2 : Découvrir les composants

### 2.1 Composants à analyser

| Composant | Répertoire | Pattern de détection |
|-----------|------------|---------------------|
| Controller | `src/ApiPlatform/Controller/` | Référencé dans `controller=` |
| Extension | `src/ApiPlatform/Extension/` | Implémente `QueryCollectionExtensionInterface`, supporte l'entité |
| DataProvider | `src/ApiPlatform/DataProvider/` | `supports()` retourne true pour l'entité |
| DataPersister | `src/ApiPlatform/DataPersister/` | `supports()` retourne true pour l'entité |
| Filter | `src/ApiPlatform/Filter/` | Déclaré via `@ApiFilter` sur l'entité |
| Normalizer | `src/ApiPlatform/Normalizer/` | `supportsNormalization()` pour l'entité |
| Transformer | `src/ApiPlatform/DataTransformer/` | `supportsTransformation()` pour l'entité |
| Validator | `src/ApiPlatform/Validator/` | Constraint appliquée à l'entité |
| Voter | `src/Security/Voter/` | `supports()` pour l'entité |
| DTO | `src/ApiPlatform/DTO/` | Référencé dans `input=` ou `output=` |

### 2.2 Analyser les dépendances

Pour chaque composant trouvé, lire le constructeur et identifier :
- Services injectés
- Repositories utilisés
- Autres entités référencées

## Phase 3 : Analyser la sécurité

### 3.1 Expressions de sécurité

Extraire de l'opération :
- `security` - Vérifié avant désérialisation
- `security_post_denormalize` - Vérifié après désérialisation

### 3.2 Voter analysis

Lire le Voter associé et documenter :
- Attributs supportés (CREATE, READ, UPDATE, DELETE)
- Logique de `voteOnAttribute()`
- Permissions vérifiées

### 3.3 Multi-tenancy

Identifier si `BaseCheckCompanyExtension` s'applique :
- Filtrage par company
- Vérification subscription planning

## Phase 4 : Vérifier le contrat

### 4.1 Localiser le contrat

```bash
ls api-contracts/docs/obat-{target}/
```

Types de contrats :
- `internal.openapi.yaml` - API interne
- `external.openapi.yaml` - API externe
- `public.openapi.yaml` - API publique

### 4.2 Comparer avec la source

Pour chaque aspect, comparer source vs contrat :

| Aspect | Source | Contrat |
|--------|--------|---------|
| Path | Annotation | paths.{path} |
| Method | Annotation | paths.{path}.{method} |
| Request body | Input DTO + groups | requestBody.content.schema |
| Response | Output groups | responses.200.content.schema |
| Query params | Filters déclarés | parameters |
| Status codes | Voter + validation | responses |

### 4.3 Identifier les écarts

Marquer chaque différence :
- ✅ Match
- ⚠️ À vérifier (différence mineure)
- 🔴 Breaking change potentiel

## Phase 5 : Générer le rapport

### Structure du rapport

Lire `references/component-mapping.md` pour le mapping détaillé.

```markdown
## Analyse de migration : {METHOD} {PATH}

### Source (monorepo core)

**Entité :** {entity_path}
**Opération :** {operation_name}

---

### Composants détectés

| Type | Fichier | Rôle |
|------|---------|------|
| ... | ... | ... |

---

### Mapping vers {target}

| Source | Cible | Type |
|--------|-------|------|
| ... | ... | ... |

**Architecture cible :**
```
src/{Domain}/
├── Application/
│   ├── Query/ ou Command/
│   └── Handler/
├── Domain/
│   ├── Model/
│   └── Port/
├── Infrastructure/
│   └── Doctrine/
└── UI/
    └── Controller/
```

---

### Suggestions d'amélioration

Lire `references/modernization-rules.md`.

**Modernisation PHP 8 :**
- ...

**Architecture CQRS :**
- ...

---

### Vérification BC

Lire `references/bc-checklist.md`.

| Contrat | Source | Status |
|---------|--------|--------|
| ... | ... | ... |

**Checklist :**
- [ ] ...
```

## Phase 6 : Générer le code (si --generate)

### 6.1 Demander le domaine

Si `--domain` non fourni :
```
Domaine cible dans {target} ? (ex: Document, Calendar, User)
> _
```

### 6.2 Déterminer le type CQRS

| Opération source | Type CQRS |
|------------------|-----------|
| GET collection | Query |
| GET item | Query |
| POST | Command |
| PUT/PATCH | Command |
| DELETE | Command |
| Custom read-only | Query |
| Custom avec effet | Command |

### 6.3 Générer les fichiers

Utiliser `/cqrs-generate` pour créer :
- Query/Command avec les champs appropriés
- Handler avec TODO pour la logique
- Controller REST si nécessaire

### 6.4 Rapport de génération

```
✅ Fichiers créés dans /home/audrey/Obat/{target} :
   - src/{Domain}/Application/Query/Get{Entity}Query.php
   - src/{Domain}/Application/Handler/Get{Entity}Handler.php
   - src/{Domain}/UI/Controller/Get{Entity}Controller.php

📋 Prochaines étapes :
   1. Implémenter la logique dans le Handler
   2. Porter la logique des Extensions/Providers
   3. Configurer les filtres
   4. Vérifier la compatibilité avec le contrat
   5. Tester avec les mêmes requêtes que le monorepo
```

## Intégration

**Utilisé avec :**
- `/contract-check` - Vérifier le contrat après migration
- `/impact-analysis` - Identifier les consommateurs
- `/cqrs-generate` - Générer les composants CQRS

**Appelé depuis :**
- Manuellement lors des migrations

## Erreurs courantes

**Endpoint non trouvé**
- Symptôme : "Endpoint non trouvé dans le monorepo"
- Solution : Vérifier le path exact (avec ou sans `/api/` prefix)

**Composant non détecté**
- Symptôme : Extension ou Provider manquant dans le rapport
- Solution : Vérifier si le composant utilise `supports()` dynamique

**Contrat inexistant**
- Symptôme : Pas de comparaison BC
- Solution : Créer d'abord le contrat dans `api-contracts/`
