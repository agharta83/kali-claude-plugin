# Mode Subagent pour /execute-plan - Design

**Objectif :** Ajouter un mode `--subagent` à `/execute-plan` qui dispatch un subagent frais par tâche avec code review automatique entre les tâches.

**Architecture :** Exécution séquentielle avec isolation de contexte par tâche, review systématique, et correction automatique des problèmes critiques.

**Stack technique :** Task tool (general-purpose, superpowers:code-reviewer), TodoWrite, Git

---

## Décisions prises

| Question | Réponse |
|----------|---------|
| Granularité du code review | Après chaque tâche |
| Gestion des problèmes critiques | Correction automatique via subagent fix |
| Compatibilité avec --loop | Non, modes mutuellement exclusifs |
| Comportement en cas d'échec | Retry 1x avec contexte d'erreur, puis stop |

---

## Flux d'exécution

```
execute-plan --subagent
    │
    ├── Phase 1 : Chargement
    │   ├── Charger le plan markdown
    │   ├── Créer TodoWrite
    │   └── Sauvegarder SHA initial
    │
    ├── Phase 2 : Boucle (par tâche)
    │   ├── Marquer in_progress
    │   ├── Sauvegarder base_sha
    │   ├── Dispatch subagent implémentation
    │   ├── Dispatch subagent code-reviewer
    │   ├── Si Critical → Dispatch subagent fix → Re-review
    │   ├── Si échec après retry → STOP
    │   └── Marquer completed
    │
    └── Phase 3 : Finalisation
        ├── Afficher résumé
        └── Proposer /finish-branch
```

---

## Prompts des subagents

### Subagent implémentation

```markdown
Tu implémentes la Tâche N du plan [chemin/vers/plan.md].

Instructions :
1. Lis la tâche dans le plan (section "Tâche N")
2. Suis chaque étape exactement (TDD : test → implémentation → vérification)
3. Commite ton travail après chaque étape logique
4. Rapporte : ce que tu as fait, fichiers modifiés, résultat des tests

Répertoire de travail : [directory]

Convention commits Obat :
Format : type: #PROJET-XXX description
Types autorisés : tech, feat, doc, fix, hotfix, chore

IMPORTANT : Ne modifie QUE ce qui est spécifié dans la tâche.
```

### Subagent code-reviewer

```markdown
Review les changements de la Tâche N.

Commits à reviewer : de [base_sha] à HEAD
Plan de référence : [chemin/vers/plan.md], section "Tâche N"

Vérifie :
- [ ] La tâche est implémentée selon le plan
- [ ] Tests présents et passants
- [ ] Pas de code mort, console.log, ou debug oublié
- [ ] Conventions Obat respectées (commits, nommage)
- [ ] Pas de régressions introduites

Retourne :
- Strengths : Points positifs
- Issues : Liste avec sévérité (Critical/Important/Minor)
- Assessment : "Ready" ou "Needs Work"
```

### Subagent fix

```markdown
Corrige les problèmes identifiés par le code review pour la Tâche N.

Issues à corriger :
[Liste des issues du code-reviewer]

Instructions :
1. Corrige chaque issue listée
2. Commite tes corrections (format: fixup! type: #ID description)
3. Rapporte ce que tu as corrigé

IMPORTANT : Ne corrige QUE les issues listées, rien d'autre.
```

---

## Gestion des erreurs

### Matrice de décision

| Situation | Action |
|-----------|--------|
| Subagent implémentation échoue | Retry 1x avec contexte d'erreur |
| Retry échoue | STOP, rapport d'erreur, attendre intervention |
| Code review : Critical issues | Dispatch fix, re-review |
| Code review : Important/Minor only | Dispatch fix, pas de re-review |
| Fix ne résout pas Critical | STOP, afficher issues, attendre intervention |

---

## Combinaisons de flags

| Commande | Comportement |
|----------|--------------|
| `/execute-plan` | Mode standard (batches de 3) |
| `/execute-plan --subagent` | Mode subagent |
| `/execute-plan --worktree` | Standard + worktree isolé |
| `/execute-plan --subagent --worktree` | Subagent + worktree isolé |
| `/execute-plan --loop` | Ralph Loop |
| `/execute-plan --subagent --loop` | INVALIDE (mutuellement exclusifs) |

---

## Fichier modifié

- `skills/execute-plan/SKILL.md` : Ajout du routage et de la section Mode Subagent
