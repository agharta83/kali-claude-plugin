# Message → Service Mapping

Ce fichier définit le mapping entre les Messages RabbitMQ et leurs services sources.

## Convention principale

Le préfixe du Message indique généralement le service source :

| Préfixe | Service |
|---------|---------|
| `User*` | obat-user |
| `Company*` | obat-user |
| `Membership*` | obat-user |
| `Resource*` | obat-operation |
| `Calendar*` | obat-operation |
| `Planning*` | obat-operation |
| `Worksite*` | obat-operation |
| `WorkHours*` | obat-operation |
| `Invoice*` | obat-accounting |
| `Quote*` | obat-sales |
| `Contact*` | obat-sales |
| `Notification*` | obat-notification |

## Exceptions et cas particuliers

Certains messages ne suivent pas la convention de nommage :

| Message | Service source | Raison |
|---------|----------------|--------|
| `CollaboratorCreatedMessage` | obat-operation | Collaborator est lié aux ressources |
| `HourlyCostUpdatedMessage` | obat-operation | Coûts horaires gérés par operation |

## Comment mettre à jour ce fichier

1. Si un nouveau message ne suit pas la convention, l'ajouter dans "Exceptions"
2. Si un nouveau domaine est créé, l'ajouter dans "Convention principale"
3. Vérifier périodiquement que les mappings sont toujours corrects

## Utilisation par le skill

Le skill `/impact-analysis` utilise ce fichier comme fallback quand :
1. Le préfixe du message n'est pas reconnu
2. Le namespace du message ne permet pas de déduire le service
3. Une ambiguïté existe entre plusieurs services possibles
