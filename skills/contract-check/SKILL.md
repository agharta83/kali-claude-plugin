---
name: contract-check
description: Use when modifying API endpoints or data schemas in Obat microservices. Detects breaking changes by comparing code with centralized OpenAPI contracts in api-contracts submodule.
---

# Contract Check

Valide la compatibilité des changements locaux avec les contrats OpenAPI centralisés.

**Principe :** Comparer le diff avec les contrats dans `api-contracts/` → Détecter breaking changes → Lister les services impactés

**Annonce au démarrage :** "J'utilise le skill contract-check pour vérifier la compatibilité des contrats."

## Arguments

```
/contract-check                          # Analyse le diff courant
/contract-check POST /api/users          # Endpoint spécifique
/contract-check --service obat-user      # Service spécifique
```

## Structure Obat

Le submodule `api-contracts/` contient les contrats centralisés :

```
api-contracts/
└── docs/
    ├── obat-user/
    │   ├── internal.openapi.yaml   # API interne (service-to-service)
    │   ├── public.openapi.yaml     # API publique (sans auth)
    │   ├── external.openapi.yaml   # API externe (clients authentifiés)
    │   └── partners.openapi.yaml   # API partenaires
    ├── obat-operation/
    │   ├── internal.openapi.yaml
    │   └── public.openapi.yaml
    ├── obat-accounting/
    ├── obat-notification/
    ├── obat-sales/
    └── ...
```

## Phase 1 : Localiser les contrats

### 1.1 Détecter le service courant

```bash
# Identifier le service depuis le répertoire
basename $(git rev-parse --show-toplevel)
# Exemple : "operation" → "obat-operation"
```

### 1.2 Vérifier le submodule

```bash
ls api-contracts/docs/
```

Si absent → Stopper : "Submodule api-contracts non trouvé. Exécutez `git submodule update --init`."

### 1.3 Lister les contrats du service

```bash
ls api-contracts/docs/obat-${SERVICE}/
```

Afficher :
```
Service : obat-operation
Contrats trouvés :
- internal.openapi.yaml (190 KB)
- public.openapi.yaml (26 KB)
```

## Phase 2 : Analyser le diff

### 2.1 Récupérer les changements

```bash
git diff --name-only HEAD
git diff HEAD
```

### 2.2 Filtrer les fichiers pertinents

| Pattern | Impact |
|---------|--------|
| `src/**/Controller/**` | Endpoints REST |
| `src/**/Action/**` | Endpoints REST |
| `src/**/DTO/**` | Schémas request/response |
| `src/**/Model/**` | Schémas de données |
| `src/**/Entity/**` | Schémas de données |

### 2.3 Mapper aux endpoints

Pour chaque Controller/Action modifié :
1. Lire les annotations de route (`#[Route('/api/...')]`)
2. Extraire method + path
3. Chercher dans les fichiers OpenAPI correspondants

## Phase 3 : Détecter les breaking changes

Lire `references/breaking-change-rules.md` pour les règles complètes.

### 3.1 Comparer code vs contrat

Pour chaque endpoint modifié :

**Request body :**
- Nouveau champ requis → 🔴 Breaking
- Champ supprimé → ✅ OK (serveur ignore)
- Type modifié → 🔴 Breaking

**Response body :**
- Champ supprimé → 🔴 Breaking
- Nouveau champ → ✅ OK (clients ignorent)
- Type modifié → 🔴 Breaking
- Nullable → non-nullable → ✅ OK
- Non-nullable → nullable → 🔴 Breaking

**Paramètres :**
- Nouveau param requis → 🔴 Breaking
- Param optionnel → requis → 🔴 Breaking
- Param supprimé → 🟡 Risky

### 3.2 Détecter les drifts contrat ↔ code

Vérifier si le code a divergé du contrat :
- Endpoint dans le code mais pas dans le contrat
- Champs dans le code mais pas dans le contrat
- Types différents entre code et contrat

## Phase 4 : Identifier les consommateurs

### 4.1 Analyser les types de contrats

| Type | Consommateurs |
|------|---------------|
| `internal.openapi.yaml` | Autres microservices Obat |
| `public.openapi.yaml` | Frontend, apps sans auth |
| `external.openapi.yaml` | Clients authentifiés |
| `partners.openapi.yaml` | Partenaires externes |

### 4.2 Estimer l'impact

- **internal** : Coordination avec équipes backend requise
- **public/external** : Impact frontend, communication client potentielle
- **partners** : Impact contractuel, préavis obligatoire

## Phase 5 : Générer le rapport

```markdown
## Contract Check Report

### Service : obat-operation
### Contrats analysés : internal.openapi.yaml, public.openapi.yaml

---

### Breaking changes détectés 🔴

| Endpoint | Changement | Type contrat | Impact |
|----------|------------|--------------|--------|
| `POST /api/resources` | Champ `category` supprimé en response | internal | Services consommateurs |
| `GET /api/events/{id}` | Type `date` changé (string → DateTime) | public | Frontend |

### Drifts contrat ↔ code 🟡

| Endpoint | Problème |
|----------|----------|
| `PUT /api/resources/{id}` | Présent dans le code, absent du contrat |
| `POST /api/events` | Champ `metadata` dans le code, pas dans le contrat |

### Changements compatibles ✅

| Endpoint | Changement |
|----------|------------|
| `GET /api/resources` | Nouveau champ optionnel `tags` |

---

### Actions requises

1. **Mettre à jour le contrat** `api-contracts/docs/obat-operation/internal.openapi.yaml`
2. **Coordonner** avec les services consommateurs si breaking change intentionnel
3. **Versionner** l'endpoint si changement majeur (`/v2/resources`)

### Commandes utiles

```bash
# Mettre à jour le submodule après modification
cd api-contracts && git add . && git commit -m "Update obat-operation contracts"

# Voir le diff du contrat
git diff api-contracts/docs/obat-operation/
```
```

### Cas sans problème

```markdown
## Contract Check Report

### ✅ Aucun breaking change détecté

Service : obat-operation
Fichiers analysés : 5
Contrats vérifiés : 2

Les changements sont compatibles avec les contrats existants.
```

## Intégration

**Appelé par :**
- `/finish-branch --strict` - Gate obligatoire en mode strict
- Manuellement avant toute modification d'API

**Fonctionne avec :**
- `/impact-analysis` - Analyse cross-service plus approfondie
- `/code-review` - Le `contracts-reviewer` vérifie la qualité du design

## Évolutions futures

- **AsyncAPI** : Quand les events seront documentés dans `api-contracts/`
- **consumers.yaml** : Mapping explicite des dépendances inter-services
- **CI/CD** : Intégration dans le pipeline GitLab

## Erreurs courantes

**Submodule pas à jour**
- Symptôme : Contrats obsolètes
- Solution : `git submodule update --remote api-contracts`

**Drift non détecté**
- Symptôme : Code et contrat divergent silencieusement
- Solution : Exécuter `/contract-check` régulièrement

**Breaking change non coordonné**
- Symptôme : Service consommateur cassé après déploiement
- Solution : Toujours vérifier les consommateurs avant merge
