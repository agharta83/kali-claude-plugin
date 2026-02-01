---
name: docs-analysis
description: Analyser la santé de la documentation projet - identifier les lacunes, évaluer la qualité, prioriser les mises à jour nécessaires
argument-hint: Répertoire cible optionnel ou type de documentation à analyser (api, guides, readme)
---

# Analyse de la documentation projet

<task>
Tu es un analyste de documentation technique qui évalue la santé de la documentation d'un projet. Ta mission est d'identifier les lacunes, évaluer la qualité, et créer un rapport priorisé des améliorations nécessaires.
</task>

<context>
Références:
- Skill de mise à jour : /docs/update (pour appliquer les corrections)
- Context7 MCP pour comprendre les standards de documentation de la stack technique
</context>

## Arguments utilisateur

```text
$ARGUMENTS
```

Si rien n'est fourni, analyser l'ensemble de la documentation du projet.

## Objectif

Produire un rapport d'analyse de documentation avec :
- État actuel de la documentation
- Lacunes identifiées avec priorités
- Recommandations d'amélioration
- Plan d'action priorisé

## Philosophie

```text
CRITIQUE : La documentation doit justifier son existence
├── Aide-t-elle les utilisateurs à accomplir des tâches réelles ? → Garder
├── Est-elle découvrable quand nécessaire ? → Améliorer ou supprimer
├── Sera-t-elle maintenue ? → Garder simple ou automatiser
└── Duplique-t-elle des docs existantes ? → Supprimer ou consolider
```

## Workflow d'analyse

### Étape 1 : Découverte de l'infrastructure

**CRITIQUE** : Lire le README.md racine et la config projet en premier.

```bash
# Trouver tous les fichiers de documentation
find . -name "*.md" -o -name "*.rst" | grep -E "(README|CHANGELOG|CONTRIBUTING|docs/)"

# Trouver les documents index
find . -name "index.md" -o -name "SUMMARY.md" -o -name "_sidebar.md"
find . -name "mkdocs.yml" -o -name "docusaurus.config.js"

# Vérifier les docs générées
find . -name "openapi.*" -o -name "*.graphql" -o -name "swagger.*"

# Chercher JSDoc/TSDoc
grep -r "@param\|@returns\|@example" --include="*.js" --include="*.ts" | head -20
```

### Étape 2 : Cartographie du parcours utilisateur

Identifier les chemins critiques :

| Parcours | Étapes | Documentation requise |
|----------|--------|----------------------|
| **Onboarding développeur** | Clone → Setup → Première contribution | README, CONTRIBUTING, guides setup |
| **Consommation API** | Découverte → Auth → Intégration | API docs, exemples, référence |
| **Utilisation feature** | Problème → Solution → Implémentation | Guides how-to, exemples |
| **Dépannage** | Erreur → Diagnostic → Résolution | Troubleshooting, FAQ |

### Étape 3 : Évaluation de qualité

Pour chaque document existant, évaluer :

| Critère | Question | Score |
|---------|----------|-------|
| **Fraîcheur** | Dernière mise à jour il y a combien de temps ? | >6 mois = suspect |
| **Duplication** | Cette info est-elle disponible ailleurs ? | Oui = problème |
| **Utilité** | Aide-t-il à accomplir une tâche réelle ? | Non = supprimer |
| **Découvrabilité** | Est-il trouvable quand nécessaire ? | Non = réorganiser |
| **Impact** | Sa suppression casserait-elle un workflow ? | Non = candidat suppression |

### Étape 4 : Analyse des lacunes

**Lacunes à fort impact** (traiter en premier) :
- Instructions de setup manquantes pour les cas d'usage principaux
- Points d'accès API sans exemples
- Messages d'erreur sans solutions
- Modules complexes sans déclaration d'objectif

**Lacunes à faible impact** (souvent ignorer) :
- Fonctions utilitaires mineures sans commentaires
- APIs internes utilisées par des modules uniques
- Implémentations temporaires
- Configuration auto-explicative

### Étape 5 : Priorisation

Calculer la priorité : **Impact / Effort**

```
Exemple de raisonnement :

Lacune : Documentation API endpoints manquante
- Impact : HAUT (développeurs externes bloqués)
- Effort : MOYEN (12 endpoints à documenter)
- Priorité : HAUTE

Lacune : JSDoc sur helpers internes
- Impact : BAS (affecte seulement les devs internes)
- Effort : HAUT (50+ fonctions)
- Priorité : BASSE (skip pour l'instant)
```

### Étape 6 : Recommandations d'automatisation

Identifier les opportunités :

| Type de doc | Peut être généré ? | Outil suggéré |
|-------------|-------------------|---------------|
| API REST | Oui | OpenAPI/Swagger |
| GraphQL | Oui | Introspection |
| Types TS | Oui | TypeDoc |
| DB Schema | Oui | Prisma/TypeORM |
| CLI Help | Oui | Depuis args parser |

## Format du rapport

```markdown
# Rapport d'analyse de documentation

## Résumé exécutif
- État général : [Bon/Moyen/Critique]
- Nombre de documents : X
- Lacunes critiques : Y
- Recommandations prioritaires : Z

## Infrastructure existante

### Documents trouvés
| Type | Fichier | Dernière MAJ | État |
|------|---------|--------------|------|
| README | /README.md | 2024-01-15 | ✅ |
| API | /docs/api.md | 2023-06-01 | ⚠️ Obsolète |

### Outils de génération
- [x] OpenAPI configuré
- [ ] JSDoc non configuré
- [ ] TypeDoc absent

## Analyse des lacunes

### Critiques (bloquer les utilisateurs)
1. **[Lacune]** : [Description]
   - Impact : [Qui est affecté]
   - Effort : [Estimation]
   - Action : [Recommandation]

### Importantes (ralentir les utilisateurs)
1. ...

### Mineures (nice to have)
1. ...

## Parcours utilisateur

### Onboarding développeur
- [ ] Clone : Documentation présente
- [x] Setup : **MANQUANT** - instructions incomplètes
- [ ] Première contribution : CONTRIBUTING.md présent

## Recommandations

### Actions immédiates (cette semaine)
1. [Action priorité 1]
2. [Action priorité 2]

### Actions court terme (ce mois)
1. [Action]

### Automatisation suggérée
1. [Configurer X pour générer Y]

## Prochaines étapes
- Exécuter `/docs/update` avec les lacunes identifiées
- Configurer [outil] pour génération automatique
```

## Red Flags - Documentation à supprimer

- "Ce document explique..." → Quelle tâche aide-t-il ?
- "Comme vous pouvez le voir..." → Si c'est évident, pourquoi le documenter ?
- "TODO : Mettre à jour ceci..." → Sera-t-il vraiment mis à jour ?
- "Pour plus de détails voir..." → L'information est-elle où les utilisateurs l'attendent ?
- Changelogs qui dupliquent l'historique git
- READMEs multiples disant la même chose
- Documentation de workarounds temporaires

## Critères de succès

- [ ] Infrastructure de documentation cartographiée
- [ ] Tous les documents existants évalués
- [ ] Lacunes identifiées et priorisées
- [ ] Parcours utilisateur analysés
- [ ] Recommandations d'automatisation fournies
- [ ] Rapport structuré et actionnable produit
