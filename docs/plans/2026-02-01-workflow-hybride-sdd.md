# Workflow Hybride SDD - Design

**Date :** 2026-02-01
**Objectif :** Fusionner le workflow superpowers (brainstorm/plan/execute-plan) avec spec-driven-development pour avoir le meilleur des deux mondes.

---

## Architecture générale

```
                            /brainstorm [--sdd]
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
              Score < 4                    Score ≥ 4 ou --sdd
                    │                              │
                    ▼                              ▼
            MODE LÉGER                      MODE SDD ENRICHI
                    │                              │
    ┌───────────────┼───────────────┐              │
    ▼               ▼               ▼              ▼
 /plan      /execute-plan    /code-review    /sdd/specify
    │               │            (6 agents)       │
    ▼               ▼               ▲              ▼
 docs/plans/    Implémentation      │         /sdd/plan
                    │               │              │
                    └───────────────┘              ▼
                                             /sdd/tasks
                                                  │
                                                  ▼
                                            /sdd/implement
                                            (review rapide
                                             entre phases)
                                                  │
                                                  ▼
                                            /code-review
                                            (6 agents)
                                                  │
                                                  ▼
                                           /sdd/document
```

**Principe :** `/brainstorm` est le point d'entrée. Il analyse la complexité et propose de basculer vers SDD si nécessaire. Le flag `--sdd` force le mode enrichi.

---

## Détection de complexité

### Signaux analysés

| Catégorie | Signaux | Poids |
|-----------|---------|-------|
| **Scope technique** | Nouvelle intégration externe, changement d'architecture, nouveau domaine/module, migration de données | +2 chaque |
| **Scope fonctionnel** | >3 user stories, acceptance criteria avec dépendances, impact multi-équipes, nouveau parcours utilisateur complet | +2 chaque |
| **Incertitude** | >2 questions ouvertes majeures, plusieurs approches viables, technologie inconnue, besoin de recherche | +1 chaque |

### Seuil

- **Score ≥ 4** → Suggère le mode SDD
- **Flag `--sdd`** → Force le mode SDD sans analyse

### Message de suggestion

```
Ce ticket présente des signaux de complexité :
- [liste des signaux détectés]

Score : X/10

Voulez-vous activer le workflow SDD enrichi ?
→ Agents spécialisés (architect, researcher, business-analyst)
→ Artifacts formels (spec.md, contract.md, data-model.md)
→ Phases structurées avec validation

[Oui, activer SDD] [Non, continuer en mode léger]
```

---

## Mode léger (inchangé)

```
/brainstorm ──► /plan ──► /execute-plan ──► /code-review
     │              │            │               │
     ▼              ▼            ▼               ▼
 design.md     plan.md      Implémentation   6 agents
 (+ ADR)       ou prd.json  batch/subagent   complets
```

**Artifacts** dans `docs/plans/` :
- `YYYY-MM-DD-<topic>-design.md`
- `YYYY-MM-DD-<topic>.md` (plan) ou `<TICKET>-prd.json`
- `ADR-XXXX-<title>.md` (si applicable)

**Aucune modification** aux skills existants.

---

## Mode SDD enrichi

```
/brainstorm --sdd ──► /sdd/specify ──► /sdd/plan ──► /sdd/tasks ──► /sdd/implement ──► /sdd/document
       │                   │               │             │              │                │
       ▼                   ▼               ▼             ▼              ▼                ▼
   Détection          business-       researcher    tech-lead      developer        tech-writer
   + transition       analyst         architect     (découpe)      (TDD + review    (docs)
                      (spec.md)       code-explorer               rapide)
                                      (plan.md)
```

**Artifacts** dans `specs/<NNN>-<feature>/` :
- `spec.md` - Spécification formelle (business-analyst)
- `research.md` - Recherche technique (researcher)
- `plan.md` - Architecture et approche (software-architect)
- `data-model.md` - Modèle de données
- `contract.md` - Contrats API
- `tasks.md` - Tâches découpées (tech-lead)

**Transition fluide :** Le design.md initial est automatiquement utilisé comme input pour `/sdd/specify`.

---

## Review à deux niveaux

### Niveau 1 : Review rapide (pendant l'implémentation SDD)

Après chaque phase de `/sdd/implement` :

```
3 agents rapides :
  - Code quality (patterns, lisibilité)
  - Test coverage (couverture des AC)
  - Contracts (respect des interfaces définies dans contract.md)

Seuil : confidence ≥ 70%
Résultat : CONTINUE ou CORRIGER AVANT SUITE
```

### Niveau 2 : Review complète (avant merge)

```
/code-review (6 agents) :
  - bug-hunter
  - security-auditor
  - code-quality-reviewer
  - test-coverage-reviewer
  - contracts-reviewer
  - historical-context-reviewer

Seuil : confidence ≥ 80%
Résultat : READY TO MERGE ou NEEDS FIXES
```

**Mode léger** : Uniquement niveau 2
**Mode SDD** : Niveau 1 entre phases + niveau 2 à la fin

---

## Structure des skills SDD

```
skills/sdd/
├── setup/
│   └── SKILL.md
├── specify/
│   └── SKILL.md
├── plan/
│   └── SKILL.md
├── tasks/
│   └── SKILL.md
├── implement/
│   └── SKILL.md
├── document/
│   └── SKILL.md
└── references/
    ├── business-analyst.md
    ├── software-architect.md
    ├── researcher.md
    ├── code-explorer.md
    ├── developer.md
    ├── tech-lead.md
    └── tech-writer.md
```

**Invocation :** `/sdd/specify`, `/sdd/plan`, `/sdd/tasks`, etc.

---

## Modifications à apporter

### Skills à modifier

| Skill | Modification |
|-------|--------------|
| `/brainstorm` | Analyse complexité + flag `--sdd` + suggestion + transition vers `/sdd/specify` |
| `/sdd/specify` | Accepter design.md en input |
| `/sdd/implement` | Review rapide (3 agents) après chaque phase |

### Skills à créer

Transformer `spec-driven-development/commands/` en `skills/sdd/` :

| Source | Destination |
|--------|-------------|
| `commands/00-setup.md` | `skills/sdd/setup/SKILL.md` |
| `commands/01-specify.md` | `skills/sdd/specify/SKILL.md` |
| `commands/02-plan.md` | `skills/sdd/plan/SKILL.md` |
| `commands/03-tasks.md` | `skills/sdd/tasks/SKILL.md` |
| `commands/04-implement.md` | `skills/sdd/implement/SKILL.md` |
| `commands/05-document.md` | `skills/sdd/document/SKILL.md` |

### References à déplacer

`spec-driven-development/references/` → `skills/sdd/references/`

---

## Flux avec passerelles

### Scénario A : Feature simple

```
/brainstorm "ajouter un bouton logout"
     │
     ├─ Score 2/10 → Mode léger
     │
     └─► /plan → /execute-plan → /code-review
```

### Scénario B : Feature complexe (détection)

```
/brainstorm "refonte authentification OAuth"
     │
     ├─ Score 6/10 → Suggestion SDD
     │
     └─► User accepte → /sdd/specify → /sdd/plan → ...
```

### Scénario C : Feature complexe (flag)

```
/brainstorm --sdd "migration BDD"
     │
     └─► Mode SDD direct → /sdd/specify → ...
```

### Passerelle retour

Si en `/sdd/specify` on réalise que c'est simple → basculer vers `/plan` directement.
