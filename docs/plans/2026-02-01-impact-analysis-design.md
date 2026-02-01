# Design `/impact-analysis`

**Date** : 2026-02-01
**Statut** : Validé

## Vue d'ensemble

**Objectif** : Analyser l'impact d'un changement sur les 19 services Obat en scannant le code source pour identifier les consommateurs d'APIs et d'events.

**Modes d'utilisation** :
```bash
/impact-analysis                              # Analyse le diff courant
/impact-analysis --file <path>                # Fichier spécifique
/impact-analysis --endpoint "GET /api/users"  # Endpoint REST
/impact-analysis --event UserDeactivatedEvent # Event RabbitMQ
/impact-analysis --service obat-user          # Tous les consommateurs d'un service
/impact-analysis --verbose                    # Rapport détaillé
```

**Sources de données** :
1. **Liste des services** : `api-contracts/docs/obat-*/` (source de vérité)
2. **Code des services** : `~/Obat/{service-name}/` (scan à la demande)
3. **Branche scannée** : `main` par défaut, branche courante si le service local n'est pas sur main

**Détection des consommateurs** :
- **API REST** : Scan de `vendor/obat/http-client/src/Api/` et clients locaux
- **Events RabbitMQ** : Scan des `*MessageHandler` dans `src/*/Infrastructure/Messenger/Handler/`

**Intégration** :
- Appelé par `/finish-branch --strict`
- Complémentaire à `/contract-check` (contrats vs code réel)

---

## Flux d'exécution

### Phase 1 : Initialisation

1. Détecter le service courant (basename du repo git)
2. Vérifier que `api-contracts/` existe (sinon erreur)
3. Lister les services depuis `api-contracts/docs/obat-*/`
4. Vérifier les repos locaux disponibles dans `~/Obat/`

### Phase 2 : Extraction des éléments à analyser

Selon le mode :

| Mode | Extraction |
|------|------------|
| `(diff)` | Parse `git diff HEAD` → endpoints modifiés + events modifiés |
| `--file` | Analyse le fichier → détermine si Controller/Event/DTO |
| `--endpoint` | Recherche directe dans les clients des autres services |
| `--event` | Recherche directe dans les MessageHandlers |
| `--service` | Liste tous les endpoints + events exposés par ce service |

### Phase 3 : Scan des services consommateurs

```
Pour chaque service dans api-contracts/ (sauf le service courant) :
  1. Vérifier si ~/Obat/{service}/ existe
  2. git checkout main (ou noter la branche courante)
  3. Scanner :
     - vendor/obat/http-client/src/Api/{ServiceCourant}/**/*.php
     - src/**/Infrastructure/Messenger/Handler/**/*Handler.php
  4. Extraire les dépendances (endpoints appelés, events consommés)
```

### Phase 4 : Génération du rapport

- Croiser les éléments modifiés avec les consommateurs trouvés
- Générer le rapport (synthétique ou verbose)

---

## Patterns de détection

### Détection des endpoints consommés (API REST)

Dans `vendor/obat/http-client/src/Api/{Service}/` :

```php
// Pattern à détecter
$this->get("/v1/external/memberships/companies/$companyUuid/users/$userUuid/additional-services");
$this->post("/api/users", $data);
$this->delete("/api/resources/{id}");
```

**Regex** : `\$this->(get|post|put|delete|patch)\s*\(\s*["']([^"']+)["']`

### Détection des events consommés (RabbitMQ)

Dans `src/**/Infrastructure/Messenger/Handler/**/*Handler.php` :

```php
// Pattern à détecter - le type du paramètre __invoke
public function __invoke(UserUpdatedMessage $message): void
```

**Regex sur le `__invoke`** : `function\s+__invoke\s*\(\s*(\w+Message)\s+\$`

### Mapping Message → Service source

1. **Convention de nommage** : `UserXxxMessage` → `obat-user` (préfixe)
2. **Analyse du namespace** : Si convention insuffisante
3. **Fichier de mapping** : `references/message-service-mapping.md` en fallback

---

## Format du rapport

### Rapport synthétique (par défaut)

```markdown
## Impact Analysis

**Service analysé** : obat-user
**Éléments modifiés** : 2 endpoints, 1 event

---

### Services impactés (3)

| Service | Type | Dépendances | Fichiers |
|---------|------|-------------|----------|
| obat-operation | API + Event | 2 | [voir détails](#obat-operation) |
| obat-accounting | Event | 1 | [voir détails](#obat-accounting) |
| obat-notification | Event | 1 | [voir détails](#obat-notification) |

### Actions recommandées

1. **Coordination requise** avec 3 équipes avant merge
2. **Event `UserDeactivatedEvent`** : 3 consumers à notifier
3. **Endpoint `DELETE /api/users/{id}`** : utilisé par obat-operation

### Repos non scannés (2)

- obat-inventory : repo non trouvé dans ~/Obat/
- obat-legacy : repo non trouvé dans ~/Obat/
```

### Ajouts avec `--verbose`

```markdown
### obat-operation (détails)

**API consommée :**
- `GET /v1/external/users/{id}`
  → [UserClient.php:45](~/Obat/operation/vendor/obat/http-client/src/Api/User/UserClient.php#L45)

**Events consommés :**
- `UserDeactivatedMessage`
  → [UserDeactivatedHandler.php:12](~/Obat/operation/src/.../UserDeactivatedHandler.php#L12)
```

---

## Intégration

| Skill | Interaction |
|-------|-------------|
| `/finish-branch --strict` | Gate obligatoire, bloque si services impactés non documentés |
| `/contract-check` | Complémentaire : contrats (théorie) vs code (réalité) |
| `/code-review` | Le reviewer peut suggérer de lancer `/impact-analysis` |
| `/workflow` | Inclus dans le workflow si changements d'API/events détectés |

---

## Gestion des erreurs

| Erreur | Comportement |
|--------|--------------|
| `api-contracts/` absent | Stop + message "Exécutez `git submodule update --init`" |
| Repo service non trouvé | Warning + listé dans "Repos non scannés" |
| Repo sur branche != main | Info + scan quand même avec warning |
| Aucun changement détecté | Message "Aucun endpoint/event modifié détecté" |
| Aucun consommateur trouvé | Message positif "Aucun service impacté" |

---

## Structure du skill

```
skills/impact-analysis/
├── SKILL.md                           # Instructions principales
└── references/
    └── message-service-mapping.md     # Mapping Message → Service (fallback)
```

---

## Choix techniques

| Aspect | Choix | Raison |
|--------|-------|--------|
| Scope | API + Events + Code | Couverture complète des dépendances |
| Liste services | `api-contracts/docs/` | Cohérent avec `/contract-check` |
| Repos locaux | `~/Obat/{service}/` | Convention multi-repos existante |
| Branche | `main` par défaut | Représente l'état stable |
| Rapport | Synthétique + verbose | Flexibilité selon le besoin |
