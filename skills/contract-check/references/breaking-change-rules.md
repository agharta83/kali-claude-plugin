# Breaking Change Rules

Règles de détection des breaking changes pour OpenAPI et AsyncAPI.

## Principes fondamentaux

### Robustness Principle (Postel's Law)

> Be conservative in what you send, be liberal in what you accept.

**Pour les producteurs (serveurs/publishers) :**
- Ajouter des champs → OK (consommateurs doivent ignorer l'inconnu)
- Supprimer des champs → BREAKING
- Modifier des types → BREAKING

**Pour les consommateurs (clients/subscribers) :**
- Nouveaux champs requis en entrée → BREAKING
- Nouveaux champs optionnels en entrée → OK
- Champs supprimés en sortie → BREAKING

## OpenAPI - Breaking Changes

### Endpoints

| Changement | Breaking | Raison |
|------------|----------|--------|
| Endpoint supprimé | 🔴 Oui | Clients existants échouent |
| Méthode HTTP changée | 🔴 Oui | Clients utilisent l'ancienne méthode |
| Path modifié | 🔴 Oui | Clients utilisent l'ancien path |
| Nouvel endpoint | ✅ Non | Pas d'impact sur l'existant |

### Paramètres (path, query, header)

| Changement | Breaking | Raison |
|------------|----------|--------|
| Paramètre requis ajouté | 🔴 Oui | Requêtes existantes invalides |
| Paramètre optionnel → requis | 🔴 Oui | Requêtes sans ce param échouent |
| Paramètre supprimé (requis) | 🟡 Risky | Clients envoient encore, ignoré ou erreur ? |
| Paramètre supprimé (optionnel) | ✅ Non | Clients l'envoyant → ignoré |
| Nouveau paramètre optionnel | ✅ Non | Backward compatible |
| Valeur par défaut ajoutée | ✅ Non | Améliore la compatibilité |
| Valeur par défaut modifiée | 🟡 Risky | Comportement change silencieusement |

### Request Body

| Changement | Breaking | Raison |
|------------|----------|--------|
| Champ requis ajouté | 🔴 Oui | Requêtes existantes invalides |
| Champ optionnel → requis | 🔴 Oui | Requêtes sans ce champ échouent |
| Champ supprimé | ✅ Non | Serveur ignore les champs inconnus |
| Type de champ modifié | 🔴 Oui | Validation échoue |
| Nouveau champ optionnel | ✅ Non | Backward compatible |
| Enum : valeur supprimée | 🔴 Oui | Requêtes avec cette valeur échouent |
| Enum : valeur ajoutée | ✅ Non | Nouvelles options disponibles |

### Response Body

| Changement | Breaking | Raison |
|------------|----------|--------|
| Champ supprimé | 🔴 Oui | Clients attendent ce champ |
| Champ requis → optionnel | 🔴 Oui | Clients supposent présence |
| Type de champ modifié | 🔴 Oui | Parsing client échoue |
| Nouveau champ | ✅ Non | Clients ignorent l'inconnu |
| Champ nullable → non-nullable | ✅ Non | Plus de garanties |
| Champ non-nullable → nullable | 🔴 Oui | Clients ne gèrent pas null |
| Enum : valeur ajoutée | 🟡 Risky | Client peut ne pas gérer |
| Enum : valeur supprimée | ✅ Non | Ne sera plus retournée |

### Status Codes

| Changement | Breaking | Raison |
|------------|----------|--------|
| Nouveau code d'erreur | 🟡 Risky | Clients doivent le gérer |
| Code de succès modifié (200 → 201) | 🟡 Risky | Clients vérifient le code exact |
| Code d'erreur supprimé | ✅ Non | Moins de cas d'erreur |

## AsyncAPI - Breaking Changes

### Channels/Events

| Changement | Breaking | Raison |
|------------|----------|--------|
| Event/channel supprimé | 🔴 Oui | Subscribers n'écoutent plus |
| Event renommé | 🔴 Oui | Équivalent à suppression + création |
| Nouvel event | ✅ Non | Pas d'impact sur l'existant |
| Channel renommé | 🔴 Oui | Routing cassé |

### Payload (message body)

| Changement | Breaking | Raison |
|------------|----------|--------|
| Champ supprimé | 🔴 Oui | Subscribers attendent ce champ |
| Champ requis ajouté | 🔴 Oui* | Anciens messages invalides |
| Type de champ modifié | 🔴 Oui | Parsing subscriber échoue |
| Nouveau champ optionnel | ✅ Non | Subscribers ignorent l'inconnu |
| Champ non-nullable → nullable | 🔴 Oui | Subscribers ne gèrent pas null |

*Note : Pour les events asynchrones, même un champ "requis" ajouté est breaking car les anciens messages en file d'attente n'auront pas ce champ.

### Headers/Metadata

| Changement | Breaking | Raison |
|------------|----------|--------|
| Header requis ajouté | 🔴 Oui | Anciens messages sans header |
| Header supprimé | 🟡 Risky | Si subscribers l'utilisaient |
| Nouveau header optionnel | ✅ Non | Backward compatible |

## Stratégies de migration

### Pour OpenAPI (REST APIs)

**Versionning d'URL :**
```
/api/v1/users  → version actuelle
/api/v2/users  → nouvelle version avec breaking changes
```

**Deprecation headers :**
```yaml
headers:
  Deprecation:
    description: Date de fin de support
    example: "2025-06-01"
  Sunset:
    description: Date de suppression
    example: "2025-09-01"
```

**Expansion progressive :**
```yaml
# Étape 1 : Ajouter nouveau champ optionnel
phone:
  type: string
  nullable: true
  deprecated: false

# Étape 2 : Marquer ancien champ deprecated
phone_number:
  type: string
  deprecated: true
  description: "DEPRECATED: Use 'phone' instead"

# Étape 3 : Supprimer après période de migration
```

### Pour AsyncAPI (Events)

**Versionning d'events :**
```yaml
UserCreatedEvent:    # v1 - maintenu pour backward compatibility
UserCreatedEventV2:  # v2 - nouveau format
```

**Dual publishing (période de transition) :**
```php
// Publier les deux versions pendant la migration
$bus->dispatch(new UserCreatedEvent($user));      // v1
$bus->dispatch(new UserCreatedEventV2($user));    // v2
```

**Schema evolution avec Avro/Protobuf :**
- Utiliser des schémas avec évolution forward/backward compatible
- Les champs ont des IDs, pas des noms (renommage possible)

## Checklist avant merge

- [ ] Tous les breaking changes sont-ils intentionnels ?
- [ ] Les services consommateurs sont-ils identifiés ?
- [ ] Un plan de migration existe-t-il ?
- [ ] Les équipes concernées sont-elles informées ?
- [ ] La période de deprecation est-elle définie ?
- [ ] Les contrats dans `contracts/` sont-ils mis à jour ?
- [ ] Le `consumers.yaml` est-il à jour ?

## Outils de validation

### OpenAPI

```bash
# Comparer deux versions d'un fichier OpenAPI
openapi-diff old.yaml new.yaml --fail-on-incompatible

# Oat (OpenAPI breaking changes)
oat diff old.yaml new.yaml
```

### AsyncAPI

```bash
# AsyncAPI CLI
asyncapi diff old.yaml new.yaml
```

### Intégration CI

```yaml
# .gitlab-ci.yml
contract-check:
  script:
    - openapi-diff contracts/api.yaml contracts/api.yaml.bak --fail-on-incompatible
  only:
    changes:
      - contracts/**
      - src/**/Controller/**
      - src/**/Event/**
```
