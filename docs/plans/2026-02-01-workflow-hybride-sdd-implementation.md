# Workflow Hybride SDD - Plan d'implémentation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transformer les commands SDD en skills structurés et modifier brainstorm pour le routage par complexité.

**Architecture:** Structure `skills/sdd/` avec sous-dossiers par commande + references partagées. Modification de `/brainstorm` pour détecter la complexité et router vers SDD.

**Tech Stack:** Markdown, YAML frontmatter pour les skills

---

## Tâche 1 : Créer la structure skills/sdd/

**Fichiers :**
- Créer : `skills/sdd/setup/SKILL.md`
- Créer : `skills/sdd/specify/SKILL.md`
- Créer : `skills/sdd/plan/SKILL.md`
- Créer : `skills/sdd/tasks/SKILL.md`
- Créer : `skills/sdd/implement/SKILL.md`
- Créer : `skills/sdd/document/SKILL.md`
- Créer : `skills/sdd/references/` (dossier)

**Étape 1 : Créer l'arborescence des dossiers**

```bash
mkdir -p skills/sdd/setup skills/sdd/specify skills/sdd/plan skills/sdd/tasks skills/sdd/implement skills/sdd/document skills/sdd/references
```

**Étape 2 : Vérifier la création**

```bash
ls -la skills/sdd/
```

Attendu : 7 dossiers (setup, specify, plan, tasks, implement, document, references)

---

## Tâche 2 : Déplacer les references

**Fichiers :**
- Déplacer : `skills/spec-driven-development/references/*.md` → `skills/sdd/references/`

**Étape 1 : Copier les fichiers references**

```bash
cp skills/spec-driven-development/references/*.md skills/sdd/references/
```

**Étape 2 : Vérifier le contenu**

```bash
ls skills/sdd/references/
```

Attendu : business-analyst.md, code-explorer.md, developer.md, researcher.md, software-architect.md, tech-lead.md, tech-writer.md

---

## Tâche 3 : Transformer 00-setup.md en skills/sdd/setup/SKILL.md

**Fichiers :**
- Source : `skills/spec-driven-development/commands/00-setup.md`
- Créer : `skills/sdd/setup/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Copier le contenu de `00-setup.md` et adapter le frontmatter YAML :

```yaml
---
name: sdd/setup
description: "Initialiser le projet SDD avec la constitution et les templates"
---
```

Le reste du contenu reste identique.

**Étape 2 : Vérifier le fichier**

```bash
head -20 skills/sdd/setup/SKILL.md
```

---

## Tâche 4 : Transformer 01-specify.md en skills/sdd/specify/SKILL.md

**Fichiers :**
- Source : `skills/spec-driven-development/commands/01-specify.md`
- Créer : `skills/sdd/specify/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Adapter le frontmatter :

```yaml
---
name: sdd/specify
description: "Créer la spécification d'une feature avec l'agent business-analyst"
---
```

**Étape 2 : Ajouter la section pour accepter un design.md en input**

Après la section "## User Input", ajouter :

```markdown
## Design Input (optionnel)

Si un fichier `docs/plans/*-design.md` existe pour cette feature (généré par `/brainstorm --sdd`), l'utiliser comme contexte initial :

1. Lire le design.md existant
2. Extraire les décisions de design déjà validées
3. Les intégrer comme contraintes dans la spécification
4. Éviter de reposer les questions déjà répondues
```

---

## Tâche 5 : Transformer 02-plan.md en skills/sdd/plan/SKILL.md

**Fichiers :**
- Source : `skills/spec-driven-development/commands/02-plan.md`
- Créer : `skills/sdd/plan/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Adapter le frontmatter :

```yaml
---
name: sdd/plan
description: "Planifier le développement avec research, architecture et design"
---
```

Le reste du contenu reste identique.

---

## Tâche 6 : Transformer 03-tasks.md en skills/sdd/tasks/SKILL.md

**Fichiers :**
- Source : `skills/spec-driven-development/commands/03-tasks.md`
- Créer : `skills/sdd/tasks/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Adapter le frontmatter :

```yaml
---
name: sdd/tasks
description: "Découper la spécification en tâches exécutables avec l'agent tech-lead"
---
```

Le reste du contenu reste identique.

---

## Tâche 7 : Transformer 04-implement.md en skills/sdd/implement/SKILL.md avec review rapide

**Fichiers :**
- Source : `skills/spec-driven-development/commands/04-implement.md`
- Créer : `skills/sdd/implement/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Adapter le frontmatter :

```yaml
---
name: sdd/implement
description: "Implémenter les tâches avec TDD et review rapide entre phases"
---
```

**Étape 2 : Ajouter la review rapide niveau 1 après chaque phase**

Modifier la section "### Phase Execution" pour ajouter après l'étape 1 :

```markdown
1b. **Review rapide niveau 1** (après chaque phase) :

   Lancer 3 agents en parallèle pour une review rapide :

   - **code-quality-reviewer** : patterns, lisibilité, DRY
   - **test-coverage-reviewer** : couverture des acceptance criteria
   - **contracts-reviewer** : respect des interfaces définies dans contract.md

   Seuil : confidence ≥ 70%

   - Si TOUS passent → CONTINUE vers la phase suivante
   - Si UN échoue → CORRIGER AVANT SUITE (lancer `developer` agent pour fix)
```

**Étape 3 : Modifier Stage 9 pour préciser qu'il s'agit du niveau 2**

Renommer "## Stage 9: Quality Review" en "## Stage 9: Quality Review (Niveau 2 - Complet)"

Ajouter en début de section :

```markdown
**Note:** Cette review complète (niveau 2) s'ajoute aux reviews rapides (niveau 1) effectuées entre chaque phase. Elle utilise les 6 agents du `/code-review` standard pour une validation approfondie avant merge.
```

---

## Tâche 8 : Transformer 05-document.md en skills/sdd/document/SKILL.md

**Fichiers :**
- Source : `skills/spec-driven-development/commands/05-document.md`
- Créer : `skills/sdd/document/SKILL.md`

**Étape 1 : Créer le fichier SKILL.md**

Adapter le frontmatter :

```yaml
---
name: sdd/document
description: "Documenter la feature complétée avec l'agent tech-writer"
---
```

Le reste du contenu reste identique.

---

## Tâche 9 : Modifier brainstorm/SKILL.md pour la détection de complexité

**Fichiers :**
- Modifier : `skills/brainstorm/SKILL.md`

**Étape 1 : Ajouter le flag --sdd dans la section Routage**

Après "### Mode Jira activé si :", ajouter :

```markdown
### Mode SDD activé si :
1. Le flag `--sdd` est présent
2. La détection automatique suggère SDD ET l'utilisateur accepte

Si mode SDD → Suivre la section "Mode SDD" ci-dessous.
```

**Étape 2 : Modifier la section Routage pour inclure l'analyse de complexité**

Après "### Mode standard si :", modifier :

```markdown
### Mode standard si :
Aucun flag --jira, --sdd et aucun ID Jira détecté.

Si mode standard :
1. Effectuer l'analyse de complexité (voir section "Détection de complexité")
2. Si score ≥ 4 → Suggérer le mode SDD à l'utilisateur
3. Si utilisateur accepte → Mode SDD
4. Sinon → Suivre la section "Processus de brainstorming", puis "Après le design (mode standard)"
```

**Étape 3 : Ajouter la section "Détection de complexité"**

Après la section "## Routage", ajouter :

```markdown
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
```

**Étape 4 : Ajouter la section "Mode SDD"**

Avant la section "# Mode Jira", ajouter :

```markdown
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
```

---

## Tâche 10 : Copier les templates

**Fichiers :**
- Copier : `skills/spec-driven-development/templates/spec-checklist.md` → `skills/sdd/templates/spec-checklist.md`

**Étape 1 : Créer le dossier templates et copier**

```bash
mkdir -p skills/sdd/templates
cp skills/spec-driven-development/templates/spec-checklist.md skills/sdd/templates/
```

---

## Tâche 11 : Nettoyer l'ancien dossier

**Fichiers :**
- Supprimer : `skills/spec-driven-development/`

**Étape 1 : Supprimer l'ancien dossier**

```bash
rm -rf skills/spec-driven-development/
```

**Étape 2 : Vérifier la structure finale**

```bash
find skills/sdd -type f -name "*.md" | head -20
```

Attendu :
```
skills/sdd/setup/SKILL.md
skills/sdd/specify/SKILL.md
skills/sdd/plan/SKILL.md
skills/sdd/tasks/SKILL.md
skills/sdd/implement/SKILL.md
skills/sdd/document/SKILL.md
skills/sdd/references/business-analyst.md
skills/sdd/references/code-explorer.md
skills/sdd/references/developer.md
skills/sdd/references/researcher.md
skills/sdd/references/software-architect.md
skills/sdd/references/tech-lead.md
skills/sdd/references/tech-writer.md
skills/sdd/templates/spec-checklist.md
```

---

## Récapitulatif

| Tâche | Fichiers | Action |
|-------|----------|--------|
| 1 | skills/sdd/* | Créer structure |
| 2 | references/*.md | Déplacer |
| 3 | sdd/setup/SKILL.md | Transformer |
| 4 | sdd/specify/SKILL.md | Transformer + design input |
| 5 | sdd/plan/SKILL.md | Transformer |
| 6 | sdd/tasks/SKILL.md | Transformer |
| 7 | sdd/implement/SKILL.md | Transformer + review rapide |
| 8 | sdd/document/SKILL.md | Transformer |
| 9 | brainstorm/SKILL.md | Modifier (détection + --sdd) |
| 10 | sdd/templates/ | Copier |
| 11 | spec-driven-development/ | Supprimer |
