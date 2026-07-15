# Déduplication et corrélation d'incidents

Cherche les incidents similaires à l'ouverture d'un incident, lie l'incident courant à ceux qu'il
trouve, puis clôture l'incident courant comme doublon. Répond au ticket
[#7](https://github.com/yakohhhh/playbook-soar/issues/7).

Fichier : [../playbooks/deduplication-incidents.yml](../playbooks/deduplication-incidents.yml)

## Ce qu'il fait

1. Lance `SearchIncidentsV2` avec la requête de similarité fournie, en excluant l'incident courant.
2. Si au moins un incident similaire est trouvé, lie l'incident courant à ces incidents
   (`linkIncidents`) puis le clôture en `Duplicate` avec une note.
3. Sinon, marque le statut et laisse l'incident suivre son cours.

C'est toujours l'incident courant qui est clôturé. La commande de clôture ne reçoit aucun identifiant,
donc elle ne peut pas fermer les incidents trouvés par erreur.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Les scripts `SearchIncidentsV2` et la commande `linkIncidents` (fournis par défaut).

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `RequeteSimilarite` | `status:active and type:${incident.type}` | Requête de recherche qui définit un incident similaire. |
| `NombreMax` | `10` | Nombre maximum d'incidents similaires à récupérer. |

La requête par défaut est volontairement large (même type, actifs). Affine-la avec de vrais critères de
doublon (mêmes indicateurs, même hôte, fenêtre de temps) avant de l'utiliser en production, sinon des
incidents seulement voisins seront traités comme des doublons.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Dedup.Statut` | string | `Doublon - lié et clôturé` ou `Pas de doublon - traitement normal`. |
| `Dedup.IncidentsLies` | array | Identifiants des incidents auxquels l'incident courant a été lié. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Rechercher les incidents similaires | script `SearchIncidentsV2` | Exclut l'incident courant. |
| 3 | Doublon trouvé ? | condition | `foundIncidents.id` existe. |
| 4 | Retenir les incidents liés | script `Set` | `Dedup.IncidentsLies`. |
| 5 | Lier au(x) incident(s) parent(s) | commande `linkIncidents` | Lie le courant aux trouvés. |
| 6 | Marquer le doublon | script `Set` | Statut doublon. |
| 7 | Clôturer le doublon | commande `closeInvestigation` | Ferme l'incident courant en `Duplicate`. |
| 8 | Pas de doublon | script `Set` | Statut normal. |
| 9 | Fin | titre | Convergence. |

## Tester

1. Créer deux incidents de même type, puis lancer le playbook sur le second.
2. Vérifier que le second est lié au premier, clôturé en doublon, et que `Dedup.IncidentsLies` contient
   l'ID du premier. Le premier reste ouvert.
3. Lancer sur un incident sans similaire : `Dedup.Statut = Pas de doublon - traitement normal`.

## Pour aller plus loin

- Resserrer `RequeteSimilarite` sur les indicateurs partagés (hash, IP) plutôt que le seul type.
- Copier des éléments de l'incident courant vers le parent avant de clôturer (pièces jointes, notes).
