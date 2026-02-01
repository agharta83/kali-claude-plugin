---
name: docs-update
description: Mettre à jour et maintenir la documentation projet pour les changements de code locaux en utilisant un workflow multi-agent avec des agents tech-writer. Couvre docs/, READMEs, JSDoc, et documentation API.
argument-hint: Répertoire cible optionnel, type de documentation (api, guides, readme, jsdoc), ou zone de focus spécifique
---

# Mise à jour de la documentation pour les changements locaux

<task>
Tu es un spécialiste de la documentation technique qui maintient une documentation vivante répondant aux vrais besoins des utilisateurs. Ta mission est de créer une documentation claire, concise et utile tout en évitant impitoyablement la surcharge documentaire et la dette de maintenance.
</task>

<context>
Références:
- Agent Tech Writer : references/tech-writer.md
- Skill d'analyse : /docs/analysis (pour l'analyse préalable des lacunes)
- Skill de gestion d'agents : /subagent-driven-development
- Context7 MCP pour la collecte d'informations techniques précises
</context>

## Arguments utilisateur

L'utilisateur peut fournir des zones de focus spécifiques ou des types de documentation :

```text
$ARGUMENTS
```

Si rien n'est fourni, se concentrer sur tous les besoins de documentation pour les changements non commités. Si tout est commité, couvrir le dernier commit.

## Contexte

Après l'implémentation de nouvelles fonctionnalités ou le refactoring de code existant, la documentation doit être mise à jour pour refléter les changements. Cette commande orchestre des mises à jour de documentation automatisées en utilisant des agents tech-writer spécialisés.

## Objectif

S'assurer que tous les changements de code sont correctement documentés avec une documentation claire et maintenable qui aide les utilisateurs à accomplir des tâches réelles.

## Contraintes importantes

- **Se concentrer sur l'impact utilisateur** - tous les changements de code ne nécessitent pas de documentation
- **Préserver le style de documentation existant** - suivre les patterns établis
- **Analyser la complexité des changements** :
  - S'il y a 3+ fichiers modifiés affectant la documentation, ou des changements d'API significatifs → **Utiliser le workflow multi-agent**
  - S'il y a 1-2 changements simples → **Écrire la documentation soi-même**
- **La documentation doit justifier son existence** - éviter la surcharge et la dette de maintenance

## Workflow

### Étape 1 : Analyse préalable (optionnel)

Si tu n'as pas encore d'analyse des lacunes de documentation :
- Exécuter le skill `/docs/analysis` pour obtenir un rapport complet
- Ou faire une analyse rapide des changements git

### Étape 2 : Identifier les changements

```bash
# Voir les fichiers modifiés
git status -u

# Si tout est commité, voir le dernier commit
git show --name-status
```

Filtrer pour identifier les changements impactant la documentation :
- APIs publiques nouvelles/modifiées
- Structures de modules modifiées
- Options de configuration mises à jour
- Nouvelles fonctionnalités ou workflows

### Étape 3 : Décider du mode d'exécution

**Mode simple (1-2 changements)** : Écrire la documentation directement en suivant les guidelines du tech-writer.

**Mode multi-agent (3+ changements)** : Dispatcher des agents spécialisés.

### Étape 4 : Écriture de la documentation

#### Mode simple

1. Lire les guidelines de l'Agent Tech Writer depuis `references/tech-writer.md`
2. Examiner les fichiers modifiés et comprendre l'impact
3. Identifier quelle documentation nécessite des mises à jour
4. Faire des mises à jour ciblées en suivant les conventions projet
5. Vérifier que tous les liens et exemples fonctionnent
6. S'assurer que la documentation répond aux vrais besoins des utilisateurs

#### Mode multi-agent

Lire le skill `/subagent-driven-development` pour les bonnes pratiques de gestion des agents.

**Pour chaque zone de documentation identifiée, dispatcher un agent tech-writer :**

```markdown
Tu es un tech-writer spécialisé. Lis les guidelines dans references/tech-writer.md.

Zone de documentation : {ZONE}
Fichiers modifiés : {LISTE_FICHIERS}
Git diff résumé : {DIFF}

Ta tâche :
1. Analyser l'impact des changements sur la documentation
2. Créer/mettre à jour la documentation appropriée
3. Inclure des exemples de code fonctionnels
4. Suivre les conventions projet existantes

Fichiers cibles : {FICHIERS_DOC}
```

### Étape 5 : Revue qualité

Après chaque mise à jour de documentation :

- [ ] Tous les exemples de code testés et fonctionnels
- [ ] Liens vérifiés (pas de 404)
- [ ] Objectif du document clairement énoncé
- [ ] Suit les conventions projet
- [ ] Pas de duplication avec la doc existante

### Étape 6 : Mise à jour des documents index

Vérifier si les documents index nécessitent des mises à jour :

| Document | Mettre à jour quand |
|----------|---------------------|
| `README.md` racine | Nouvelles fonctionnalités, modules |
| `README.md` de module | API, exports, objectif changent |
| `docs/index.md` | Nouvelles pages de documentation |
| `SUMMARY.md` / `_sidebar.md` | Structure de navigation change |

## Types de documentation

### README de projet

```markdown
# Nom du projet

Brève description (1-2 phrases max).

## Démarrage rapide
[Chemin le plus rapide vers le succès - <5 minutes]

## Documentation
- [Référence API](./docs/api/)
- [Guides](./docs/guides/)

## Statut
[État actuel, limitations connues]
```

### README de module

```markdown
# Nom du module

**Objectif** : Une phrase décrivant pourquoi ce module existe.

**Exports clés** : Fonctions/classes principales.

**Utilisation** : Un exemple minimal.

Voir : [Documentation principale](../docs/)
```

### JSDoc (documenter seulement le code non évident)

```typescript
/**
 * Traite le paiement avec logique de retry et détection de fraude.
 *
 * @param payment - Détails du paiement
 * @param options - Configuration pour retries
 * @returns Promise avec résultat de transaction
 * @throws PaymentError si échec après retries
 *
 * @example
 * const result = await processPayment({ amount: 100 });
 */
```

## Critères de succès

- Tous les changements côté utilisateur ont une documentation appropriée ✅
- Les exemples de code sont précis et testés ✅
- La documentation suit les conventions projet ✅
- Pas de liens ou références cassés ✅
- Pas de surcharge documentaire inutile ✅

## Template de résumé

```markdown
## Mises à jour de documentation complétées

### Fichiers mis à jour
- [ ] README.md (racine/modules)
- [ ] docs/ organisation
- [ ] Documentation API
- [ ] Commentaires JSDoc

### Documents index mis à jour
- [ ] README.md racine
- [ ] Fichiers README.md de modules
- [ ] docs/index.md ou SUMMARY.md

### Changements documentés
- [Lister les changements de code documentés]

### Revue qualité
- [ ] Exemples testés et fonctionnels
- [ ] Liens vérifiés
- [ ] Suit les conventions projet
```
