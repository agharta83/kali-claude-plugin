---
name: impact-analysis
description: Use when modifying API endpoints, events, or data schemas in Obat microservices. Scans all 19 services to identify consumers of your changes and coordination requirements.
---

# Impact Analysis

Analyse l'impact d'un changement sur les autres services Obat en scannant leur code source.

**Principe** : Scanner les repos locaux → Détecter les consommateurs d'APIs et events → Lister les services à coordonner

**Annonce au démarrage** : "J'utilise le skill impact-analysis pour identifier les services impactés par vos changements."

## Arguments

```
/impact-analysis                              # Analyse le diff courant
/impact-analysis --file <path>                # Fichier spécifique
/impact-analysis --endpoint "GET /api/users"  # Endpoint REST
/impact-analysis --event UserDeactivatedEvent # Event RabbitMQ
/impact-analysis --service obat-user          # Tous les consommateurs d'un service
/impact-analysis --verbose                    # Rapport détaillé
```

## Phase 1 : Initialisation

### 1.1 Détecter le service courant

```bash
# Identifier le service depuis le répertoire
SERVICE=$(basename $(git rev-parse --show-toplevel))
# Exemple : "operation" → "obat-operation"
```

### 1.2 Vérifier le submodule api-contracts

```bash
ls api-contracts/docs/
```

Si absent → Stopper : "Submodule api-contracts non trouvé. Exécutez `git submodule update --init`."

### 1.3 Lister les services disponibles

```bash
# Services depuis api-contracts (source de vérité)
ls -d api-contracts/docs/obat-*/ | xargs -n1 basename

# Vérifier les repos locaux disponibles
for service in $(ls -d api-contracts/docs/obat-*/ | xargs -n1 basename); do
  if [ -d ~/Obat/${service#obat-} ]; then
    echo "OK: $service → ~/Obat/${service#obat-}"
  else
    echo "MISSING: $service"
  fi
done
```

Afficher :
```
Services Obat : 19 trouvés dans api-contracts/
Repos locaux disponibles : 15/19
Repos manquants : obat-inventory, obat-legacy, obat-archive, obat-tools
```

## Phase 2 : Extraction des éléments à analyser

### 2.1 Mode diff (par défaut)

```bash
git diff --name-only HEAD
git diff HEAD
```

Filtrer les fichiers pertinents :

| Pattern | Type |
|---------|------|
| `src/**/Controller/**` | Endpoint REST |
| `src/**/Action/**` | Endpoint REST |
| `src/**/Event/**` | Event (producteur) |
| `src/**/Message/**` | Message RabbitMQ |
| `src/**/DTO/**` | Schéma de données |

Pour chaque Controller/Action :
1. Lire les annotations `#[Route('/api/...')]`
2. Extraire method + path
3. Ajouter à la liste des éléments à rechercher

Pour chaque Event/Message :
1. Extraire le nom de la classe
2. Ajouter à la liste des éléments à rechercher

### 2.2 Mode --file

Analyser le fichier spécifié :
- Si Controller/Action → extraire les routes
- Si Event/Message → extraire le nom de classe
- Si DTO/Entity → trouver les endpoints qui l'utilisent

### 2.3 Mode --endpoint

Recherche directe de l'endpoint dans les clients des autres services.

### 2.4 Mode --event

Recherche directe du nom d'event/message dans les handlers des autres services.

### 2.5 Mode --service

Lister tous les éléments exposés par le service :
- Tous les endpoints depuis les Controllers
- Tous les events/messages depuis `src/**/Event/` et `src/**/Message/`

## Phase 3 : Scan des services consommateurs

Pour chaque service disponible (sauf le service courant) :

### 3.1 Préparer le scan

```bash
SERVICE_PATH=~/Obat/${service#obat-}
cd $SERVICE_PATH

# Noter la branche courante
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Warning: $service est sur la branche $CURRENT_BRANCH (pas main)"
fi
```

### 3.2 Scanner les consommateurs d'API

Chercher dans `vendor/obat/http-client/src/Api/{ServiceCourant}/` :

```bash
# Pattern pour détecter les appels HTTP
grep -rn '\$this->\(get\|post\|put\|delete\|patch\)\s*(' \
  vendor/obat/http-client/src/Api/
```

**Regex** : `\$this->(get|post|put|delete|patch)\s*\(\s*["']([^"']+)["']`

Extraire :
- Méthode HTTP (get, post, etc.)
- URL appelée
- Fichier et ligne

### 3.3 Scanner les consommateurs d'events

Chercher dans `src/**/Infrastructure/Messenger/Handler/` :

```bash
# Pattern pour détecter les handlers de messages
grep -rn 'function __invoke' \
  src/*/Infrastructure/Messenger/Handler/
```

**Regex** : `function\s+__invoke\s*\(\s*(\w+Message)\s+\$`

Extraire :
- Nom du Message consommé
- Fichier et ligne du handler

### 3.4 Mapper au service source

Utiliser les conventions de nommage :
- `UserXxxMessage` → `obat-user`
- `ResourceXxxMessage` → `obat-operation`
- `InvoiceXxxMessage` → `obat-accounting`

Si convention insuffisante, consulter `references/message-service-mapping.md`.

## Phase 4 : Génération du rapport

### 4.1 Rapport synthétique (par défaut)

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

### Repos non scannés (4)

- obat-inventory : repo non trouvé dans ~/Obat/
- obat-legacy : repo non trouvé dans ~/Obat/
- obat-archive : repo non trouvé dans ~/Obat/
- obat-tools : repo non trouvé dans ~/Obat/
```

### 4.2 Rapport verbose (--verbose)

Ajouter pour chaque service impacté :

```markdown
---

### obat-operation (détails)

**API consommée :**
| Endpoint | Fichier | Ligne |
|----------|---------|-------|
| `GET /v1/external/users/{id}` | [UserClient.php](~/Obat/operation/vendor/obat/http-client/src/Api/User/UserClient.php#L45) | 45 |
| `POST /api/users` | [UserClient.php](~/Obat/operation/vendor/obat/http-client/src/Api/User/UserClient.php#L62) | 62 |

**Events consommés :**
| Message | Handler | Ligne |
|---------|---------|-------|
| `UserDeactivatedMessage` | [UserDeactivatedHandler.php](~/Obat/operation/src/Resource/Infrastructure/Messenger/Handler/UserDeactivatedHandler.php#L12) | 12 |
```

### 4.3 Cas sans impact

```markdown
## Impact Analysis

### Aucun service impacté

**Service analysé** : obat-user
**Éléments modifiés** : 1 endpoint (GET /api/health)

Aucun autre service ne consomme les éléments modifiés.
Vous pouvez merger sans coordination externe.
```

## Intégration

**Appelé par :**
- `/finish-branch --strict` - Gate obligatoire en mode strict
- Manuellement avant modification d'API/events

**Fonctionne avec :**
- `/contract-check` - Vérifie les contrats OpenAPI (complémentaire)
- `/code-review` - Peut suggérer de lancer `/impact-analysis`

## Gestion des erreurs

| Erreur | Action |
|--------|--------|
| `api-contracts/` absent | Stop : "Exécutez `git submodule update --init`" |
| Repo service non trouvé | Warning + listé dans "Repos non scannés" |
| Branche != main | Info : "Warning: {service} sur branche {branch}" |
| Aucun changement détecté | "Aucun endpoint/event modifié dans le diff" |
| Git error dans un repo | Warning + skip ce service |

## Évolutions futures

- **AsyncAPI** : Quand les contrats events seront dans `api-contracts/`
- **Cache** : Index optionnel pour accélérer les scans répétés
- **CI/CD** : Intégration dans le pipeline GitLab
- **Graphe** : Visualisation des dépendances inter-services
