---
name: brainstorm
description: "Brainstorming avec support Jira et SDD optionnels. Utilisez --jira pour le contexte Jira, --sdd pour le workflow enrichi."
---

# Brainstorming avec support Jira optionnel

## Détection du contexte

Détecter si on est dans un contexte Obat :

```bash
git remote -v | grep -q "gitlab.obat.fr"
```

| Contexte | Comportement |
|----------|--------------|
| Obat détecté | ADR au format Obat, `/obat/jira-sync` proposé |
| Hors Obat | ADR au format standard, pas de sync Jira Obat |

## Routage

Analyser la requête utilisateur pour déterminer le mode :

### Mode SDD activé si :
1. Le flag `--sdd` est présent
2. La détection automatique suggère SDD ET l'utilisateur accepte

Si mode SDD → Suivre la section "Mode SDD" ci-dessous.

### Mode Jira activé si :
1. Le flag `--jira` est présent (avec ou sans ID)
2. Un ID Jira est détecté dans le texte (pattern : lettres majuscules + tiret + chiffres, ex: OBAT-123, PROJ-42)

Si mode Jira → Suivre la section "Mode Jira" ci-dessous.

### Mode standard si :
Aucun flag --jira, --sdd et aucun ID Jira détecté.

Si mode standard :
1. Effectuer l'analyse de complexité (voir section "Détection de complexité")
2. Si score ≥ 4 → Suggérer le mode SDD à l'utilisateur
3. Si utilisateur accepte → Mode SDD
4. Sinon → Suivre la section "Processus de brainstorming", puis "Après le design (mode standard)"

---

# Détection de complexité

## Signaux analysés

Pendant le brainstorming initial, analyser la requête et le contexte pour détecter :

| Catégorie | Signaux | Poids |
|-----------|---------|-------|
| **Scope technique** | Nouvelle intégration externe, changement d'architecture, nouveau domaine/module, migration de données | +2 chaque |
| **Scope fonctionnel** | >3 user stories, acceptance criteria avec dépendances, impact multi-équipes, nouveau parcours utilisateur complet | +2 chaque |
| **Incertitude** | >2 questions ouvertes majeures, plusieurs approches viables, technologie inconnue, besoin de recherche | +1 chaque |

## Seuil et suggestion

Si score ≥ 4, présenter à l'utilisateur :

```text
Ce projet présente des signaux de complexité :
- [liste des signaux détectés]

Score : X/10

Voulez-vous activer le workflow SDD enrichi ?
→ Agents spécialisés (architect, researcher, business-analyst)
→ Artifacts formels (spec.md, contract.md, data-model.md)
→ Phases structurées avec validation

[Oui, activer SDD] [Non, continuer en mode léger]
```

Si l'utilisateur choisit "Oui" → Mode SDD
Si l'utilisateur choisit "Non" → Mode standard

---

# Processus de brainstorming

## Overview

Transformer des idées en designs complets à travers un dialogue collaboratif naturel.

Commencer par comprendre le contexte du projet, puis poser des questions une par une pour affiner l'idée. Une fois compris ce qu'on construit, présenter le design en petites sections (200-300 mots), en vérifiant après chaque section si ça correspond.

## Le processus

**Comprendre l'idée :**
- Explorer l'état actuel du projet (fichiers, docs, commits récents)
- Poser des questions une par une pour affiner l'idée
- Préférer les questions à choix multiples quand possible, mais les questions ouvertes sont aussi acceptables
- Une seule question par message - si un sujet nécessite plus d'exploration, le diviser en plusieurs questions
- Se concentrer sur : objectif, contraintes, critères de succès

**Explorer les approches :**
- Proposer 2-3 approches différentes avec leurs trade-offs
- Présenter les options de manière conversationnelle avec une recommandation et son raisonnement
- Commencer par l'option recommandée et expliquer pourquoi

**Présenter le design :**
- Une fois qu'on pense comprendre ce qu'on construit, présenter le design
- Le découper en sections de 200-300 mots
- Demander après chaque section si ça correspond jusqu'ici
- Couvrir : architecture, composants, flux de données, gestion des erreurs, tests
- Être prêt à revenir en arrière et clarifier si quelque chose n'est pas clair

## Principes clés

- **Une question à la fois** - Ne pas submerger avec plusieurs questions
- **Choix multiples préférés** - Plus facile à répondre que les questions ouvertes quand possible
- **YAGNI sans pitié** - Retirer les fonctionnalités inutiles de tous les designs
- **Explorer les alternatives** - Toujours proposer 2-3 approches avant de décider
- **Validation incrémentale** - Présenter le design en sections, valider chacune
- **Être flexible** - Revenir en arrière et clarifier quand quelque chose n'est pas clair

---

# Après le design (mode standard)

**Documentation :**
- Écrire le design validé dans `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commiter le document de design

**Implémentation (si on continue) :**
- Demander : "Prêt à passer à l'implémentation ?"
- Proposer de créer un plan d'implémentation détaillé

---

# Mode SDD : Workflow enrichi

## Overview

Active le workflow Specification Driven Development avec agents spécialisés et artifacts formels.

## Déclenchement

Ce mode s'active quand :
1. Flag explicite : `/brainstorm --sdd "feature description"`
2. Détection automatique : Score de complexité ≥ 4 ET utilisateur accepte

## Phase 1 : Brainstorming initial

Suivre le processus de brainstorming standard (section "Processus de brainstorming") pour :
- Comprendre l'idée
- Explorer les approches
- Présenter le design

## Phase 2 : Sauvegarde du design

Sauvegarder dans `docs/plans/YYYY-MM-DD-<topic>-design.md` avec le design validé.

## Phase 3 : Transition vers SDD

Après la sauvegarde du design, proposer :

```text
Design sauvegardé dans `docs/plans/<filename>-design.md`.

Mode SDD activé. Prochaine étape : `/sdd/specify`

Ce skill va :
1. Créer la structure specs/<feature>/
2. Transformer le design en spécification formelle
3. Utiliser l'agent business-analyst pour enrichir

Lancer `/sdd/specify` maintenant ?
```

Si l'utilisateur accepte, invoquer le skill `sdd/specify` en passant le chemin du design.md comme contexte.

## Après le design (mode SDD)

Proposer :
```text
Design sauvegardé. Workflow SDD prêt.

Prochaines étapes :
1. `/sdd/specify` - Créer la spécification formelle
2. `/sdd/plan` - Planifier l'architecture
3. `/sdd/tasks` - Découper en tâches
4. `/sdd/implement` - Implémenter avec TDD
5. `/sdd/document` - Documenter

Lancer `/sdd/specify` ?
```

---

# Mode Jira : Brainstorming avec contexte Jira

## Overview

Étend le brainstorming standard avec la récupération et l'analyse du contexte Jira. Récupère la hiérarchie complète d'un ticket (epic → stories → tasks → subtasks) pour informer le design.

## Déclenchement

Ce mode s'active quand :
1. Flag explicite : `/brainstorm --jira OBAT-123`
2. Flag sans ID : `/brainstorm --jira` (demander l'ID)
3. Détection auto : Un ID Jira (pattern `[A-Z]+-\d+`) est mentionné

## Phase 1 : Vérification de la configuration utilisateur

Avant toute récupération Jira, vérifier que `~/.claude/config/obat-jira.yaml` existe.

Si absent, guider l'utilisateur :

> "Je n'ai pas trouvé votre configuration Jira personnelle.
> Créez le fichier `~/.claude/config/obat-jira.yaml` avec :
> ```yaml
> jira:
>   default_project: OBAT    # Votre projet par défaut
>   board_id: 42             # ID de votre board Jira
>   default_assignee: ""     # Votre email (optionnel)
>   default_priority: Medium
> ```
> Puis relancez la commande."

## Phase 2 : Récupération du contexte Jira

Utiliser les outils MCP Jira dans cet ordre :

1. **Récupérer le ticket source** avec `mcp__atlassian__jira_get_issue`
2. **Identifier le type** (Epic, Story, Task, Subtask)
3. **Remonter la hiérarchie** jusqu'à l'Epic parent
4. **Descendre la hiérarchie** pour récupérer tous les enfants

Pour chaque ticket, récupérer :
- Titre, description, statut, type
- Acceptance criteria (champ customfield si applicable)
- Commentaires récents
- Story points, sprint, labels
- Assignee, priorité
- Liens (blocks, is blocked by, relates to)

## Phase 3 : Analyse et confirmation

Présenter un résumé :

> "J'ai récupéré la hiérarchie Jira :
> - Epic : OBAT-100 - Refonte authentification
>   - Story : OBAT-123 - Implémenter OAuth (votre ticket)
>     - Task : OBAT-124 - Configurer provider
>     - Task : OBAT-125 - Créer middleware
>   - Story : OBAT-126 - Tests E2E
>
> Total : 1 epic, 2 stories, 2 tasks analysés.
>
> Souhaitez-vous brainstormer au niveau de la **Story OBAT-123**, ou remonter à l'**Epic OBAT-100** ?"

## Phase 4 : Brainstorming structuré

Suivre le processus de brainstorming standard (section "Processus de brainstorming" ci-dessus).

**Avec le contexte Jira en tête :**
- Éviter de proposer des éléments qui existent déjà
- S'aligner sur la terminologie et structure existante
- Référencer les tickets liés quand pertinent

## Phase 5 : Génération du document

Sauvegarder dans `docs/plans/<TICKET-ID>-design.md` avec :

1. **Frontmatter YAML** contenant les métadonnées Jira
2. **Section Contexte Jira** résumant la hiérarchie analysée
3. **Section Design** avec le résultat du brainstorming
4. **Section Suggestions Jira** avec :
   - Nouveaux tickets à créer (type, parent, description, acceptance criteria)
   - Modifications suggérées sur tickets existants

## Format des suggestions Jira

```markdown
## Suggestions Jira

### Nouveaux tickets à créer

#### [Story] Implémenter le refresh token
- **Parent:** OBAT-123
- **Description:** Ajouter le support du refresh token OAuth pour maintenir les sessions utilisateur.
- **Acceptance criteria:**
  - [ ] Le refresh token est stocké de façon sécurisée
  - [ ] Le token est renouvelé automatiquement avant expiration
  - [ ] En cas d'échec, l'utilisateur est redirigé vers login
- **Labels:** feature, security
- **Story points:** 3

#### [Task] Créer le service TokenRefreshService
- **Parent:** (story ci-dessus)
- **Description:** Service responsable du renouvellement automatique des tokens.

### Modifications suggérées

#### OBAT-124 - Configurer provider
- **Ajouter à la description:** Inclure la configuration du refresh token endpoint
- **Ajouter acceptance criteria:**
  - [ ] Le refresh endpoint est configuré
```

## Phase 6 : Proposition d'ADR

Après le design, évaluer si un ADR est pertinent. Proposer un ADR si le brainstorming implique :

- **Nouvelle brique technique** (ex: cache Redis, queue RabbitMQ, nouveau service)
- **Choix d'une librairie critique** (ex: ORM, framework de test, lib d'authentification)
- **Modification d'un flux existant** (ex: Auth, paiement, notifications)
- **Plusieurs approches explorées** (comparaison d'options avec trade-offs)

Si un ou plusieurs critères sont remplis, proposer :

> "Ce brainstorming implique [critère détecté]. Voulez-vous que je génère un ADR pour documenter cette décision ?"

### Format de l'ADR

Le format dépend du contexte :

#### Format Obat (si contexte Obat détecté)

Si l'utilisateur accepte, générer `docs/plans/ADR-XXXX-titre-kebab-case.md` conforme au template Obat :

```markdown
# [ADR-XXXX] [Titre Court de la Décision]

* **Statut :** Proposed
* **Date :** YYYY-MM-DD
* **Auteurs :** [Nom de l'utilisateur si connu]
* **Tags :** #Tag1 #Tag2

## 1. Contexte & Problème
[Extraire du brainstorming : quel problème résout-on ? Quelles contraintes ?]

## 2. Options Considérées

### Option A : [Nom]
* Description : ...
* Avantages : ...
* Inconvénients : ...

### Option B : [Nom]
...

## 3. Décision
Nous choisissons l'**Option X**.

**Justification :**
[Extraire du brainstorming : pourquoi cette option ?]

## 4. Conséquences & Trade-offs

**Ce qu'on gagne :**
* ...

**Le prix à payer :**
* ...

## 5. Liens / Réf
* Design doc : `docs/plans/<TICKET-ID>-design.md`
* Ticket Jira : <TICKET-ID>
```

> **Note :** Le numéro XXXX est un placeholder. Avant de déplacer l'ADR vers `blueprint/adr/`, remplacez-le par le prochain numéro disponible.

#### Format standard (hors contexte Obat)

```markdown
# ADR: [Titre de la Décision]

**Date:** YYYY-MM-DD
**Status:** Proposed

## Context
[Problème à résoudre]

## Decision
[Décision prise]

## Consequences
[Impacts de la décision]
```

## Phase 7 : Proposition de PRD (Ralph Loop)

Si le ticket est une **Story**, **Task** ou **Subtask** (pas une Epic), proposer la génération d'un PRD :

> "Ce ticket contient des critères d'acceptation et/ou des sous-tâches. Voulez-vous générer un `prd.json` pour lancer une boucle Ralph Loop ?"

### Si l'utilisateur accepte

Invoquer le skill `plan` avec le flag `--prd` pour générer `docs/plans/<TICKET-ID>-prd.json`.

Le PRD sera alimenté par :
- Les acceptance criteria du ticket Jira
- Les sous-tickets existants (tasks/subtasks)
- Les suggestions du brainstorming (section "Nouveaux tickets à créer")

### Configuration Ralph par défaut

Les valeurs par défaut sont dans `config/plugin-config.yaml` :
- `max_iterations: 20`
- `completion_promise: "ALL_STORIES_PASS"`

## Après le design (mode Jira)

### Si contexte Obat

Proposer :
> "Design sauvegardé dans `docs/plans/OBAT-123-design.md`.
>
> Pour synchroniser les suggestions vers Jira, utilisez `/obat/jira-sync OBAT-123`.
>
> [Si ADR généré] ADR sauvegardé dans `docs/plans/ADR-XXXX-titre.md`. Pensez à le déplacer vers `blueprint/adr/` après validation.
>
> [Si PRD généré] PRD sauvegardé dans `docs/plans/<TICKET-ID>-prd.json`. Lancez `/execute-plan --loop` pour démarrer l'implémentation."

### Hors contexte Obat

Proposer :
> "Design sauvegardé dans `docs/plans/<TICKET-ID>-design.md`.
>
> [Si ADR généré] ADR sauvegardé dans `docs/plans/ADR-titre.md`.
>
> [Si PRD généré] PRD sauvegardé. Lancez `/execute-plan --loop` pour démarrer l'implémentation."
