# Checklist de non-régression (BC)

## Vue d'ensemble

Cette checklist garantit que l'endpoint migré se comporte exactement comme l'original pour les clients existants.

---

## 1. Response Structure

### 1.1 Format JSON

- [ ] Même structure de base (`hydra:member` pour collections)
- [ ] Mêmes noms de champs (camelCase vs snake_case)
- [ ] Même nesting des objets
- [ ] Mêmes types de données (string vs int vs bool)

**Vérification :**
```bash
# Comparer les réponses
diff <(curl -s old-api/documents | jq -S .) <(curl -s new-api/documents | jq -S .)
```

### 1.2 Champs obligatoires

- [ ] Tous les champs présents dans l'ancien endpoint existent dans le nouveau
- [ ] Pas de champs manquants qui casseraient les clients
- [ ] Nouveaux champs en plus = OK (additifs)

### 1.3 Types de données

| Champ | Type attendu | Vérifier |
|-------|--------------|----------|
| uuid | string (UUID v4) | Format exact |
| dates | ISO 8601 | Timezone, format |
| montants | float/string | Précision décimale |
| enums | string | Valeurs exactes |
| relations | IRI ou objet | Format Hydra |

### 1.4 Null handling

- [ ] Champs nullable identiques
- [ ] `null` vs champ absent = même comportement
- [ ] Valeurs par défaut identiques

---

## 2. Status Codes

### 2.1 Success codes

| Opération | Code attendu |
|-----------|--------------|
| GET collection | 200 |
| GET item | 200 |
| POST | 201 |
| PUT/PATCH | 200 |
| DELETE | 204 |

### 2.2 Error codes

- [ ] 400 Bad Request - Même validation
- [ ] 401 Unauthorized - Même auth
- [ ] 403 Forbidden - Même autorisations
- [ ] 404 Not Found - Même comportement
- [ ] 422 Unprocessable Entity - Même validation
- [ ] 500 Internal Error - Pas de nouvelles erreurs

### 2.3 Format des erreurs

```json
{
    "@context": "/api/contexts/Error",
    "@type": "hydra:Error",
    "hydra:title": "An error occurred",
    "hydra:description": "..."
}
```

- [ ] Même format d'erreur
- [ ] Mêmes messages (ou équivalents)
- [ ] Mêmes codes de violation

---

## 3. Pagination

### 3.1 Paramètres

- [ ] `page` - Même comportement
- [ ] `itemsPerPage` - Même limite par défaut
- [ ] Limite max identique

### 3.2 Response pagination

```json
{
    "hydra:totalItems": 150,
    "hydra:view": {
        "@id": "/api/documents?page=1",
        "@type": "hydra:PartialCollectionView",
        "hydra:first": "/api/documents?page=1",
        "hydra:last": "/api/documents?page=6",
        "hydra:next": "/api/documents?page=2"
    }
}
```

- [ ] `hydra:totalItems` correct
- [ ] `hydra:view` avec liens de navigation
- [ ] Même nombre d'items par page par défaut

---

## 4. Filtres

### 4.1 Query parameters

| Filtre source | Paramètre | Comportement |
|---------------|-----------|--------------|
| SearchFilter exact | `?field=value` | Match exact |
| SearchFilter partial | `?field=val` | LIKE %val% |
| SearchFilter ipartial | `?field=VAL` | Case insensitive |
| DateFilter | `?field[after]=...` | Range dates |
| BooleanFilter | `?field=true` | Boolean |
| OrderFilter | `?order[field]=asc` | Tri |

- [ ] Tous les filtres supportés
- [ ] Même syntaxe de paramètres
- [ ] Même comportement de recherche

### 4.2 Tri par défaut

- [ ] Même ordre par défaut si aucun tri spécifié
- [ ] Mêmes colonnes triables
- [ ] Même direction (asc/desc)

### 4.3 Filtres combinés

- [ ] Combinaison AND entre filtres
- [ ] Même logique de combinaison

---

## 5. Sécurité

### 5.1 Authentication

- [ ] Même méthode d'auth (JWT, API Key, etc.)
- [ ] Mêmes headers requis
- [ ] Même format de token

### 5.2 Authorization

| Rôle | Accès attendu |
|------|---------------|
| ROLE_USER | Base |
| ROLE_ADMIN | Étendu |
| Permissions custom | Identiques |

- [ ] Mêmes rôles requis
- [ ] Même logique d'accès par company
- [ ] Mêmes restrictions par permission

### 5.3 Multi-tenancy

- [ ] Filtrage par company identique
- [ ] Pas de fuite de données cross-company
- [ ] Mêmes vérifications subscription

---

## 6. Headers

### 6.1 Request headers

- [ ] `Content-Type: application/json` accepté
- [ ] `Content-Type: application/ld+json` accepté
- [ ] Mêmes headers d'auth

### 6.2 Response headers

- [ ] `Content-Type` identique
- [ ] `Cache-Control` si applicable
- [ ] CORS headers si applicable

---

## 7. Performance

### 7.1 Temps de réponse

- [ ] Temps de réponse comparable (< 2x)
- [ ] Pas de dégradation significative

### 7.2 Requêtes SQL

- [ ] Pas de N+1 queries introduites
- [ ] Mêmes JOINs ou équivalents
- [ ] Index utilisés

### 7.3 Charge

- [ ] Même comportement sous charge
- [ ] Pagination limite la mémoire

---

## 8. Tests de validation

### 8.1 Tests automatisés

```php
// Test de non-régression
public function testGetDocumentsMatchesLegacy(): void
{
    $legacyResponse = $this->callLegacyApi('GET', '/api/documents');
    $newResponse = $this->callNewApi('GET', '/api/documents');

    // Structure identique
    $this->assertSameStructure(
        $legacyResponse->toArray(),
        $newResponse->toArray()
    );
}
```

### 8.2 Tests manuels

1. **Collection vide**
   - [ ] Même réponse quand aucun résultat

2. **Collection avec données**
   - [ ] Même structure de réponse
   - [ ] Même pagination

3. **Item existant**
   - [ ] Tous les champs présents
   - [ ] Mêmes relations chargées

4. **Item inexistant**
   - [ ] 404 avec même format d'erreur

5. **Filtres**
   - [ ] Chaque filtre testé individuellement
   - [ ] Combinaisons de filtres

6. **Tri**
   - [ ] Chaque colonne triable testée
   - [ ] Tri ascendant et descendant

7. **Sécurité**
   - [ ] Sans auth → 401
   - [ ] Sans permission → 403
   - [ ] Autre company → 404 ou 403

---

## 9. Documentation

### 9.1 Contrat OpenAPI

- [ ] Endpoint documenté dans api-contracts
- [ ] Schema request/response à jour
- [ ] Paramètres documentés
- [ ] Codes d'erreur documentés

### 9.2 Changelog

- [ ] Breaking changes documentés (idéalement aucun)
- [ ] Nouvelles features documentées
- [ ] Date de migration notée

---

## 10. Rollback plan

### 10.1 Préparation

- [ ] Ancien endpoint reste disponible temporairement
- [ ] Feature flag pour basculer
- [ ] Monitoring des erreurs

### 10.2 Critères de rollback

- [ ] Taux d'erreur > X%
- [ ] Temps de réponse > Y ms
- [ ] Plaintes utilisateurs

### 10.3 Procédure

1. Désactiver le nouveau endpoint
2. Réactiver l'ancien
3. Analyser les logs
4. Corriger et redéployer
