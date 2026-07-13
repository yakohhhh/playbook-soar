# Notification et escalade

Prévient le destinataire correspondant à la sévérité de l'incident et attend son accusé de réception.
Sans réponse dans le délai, l'incident est escaladé vers un autre contact. Répond au ticket
[#9](https://github.com/yakohhhh/playbook-soar/issues/9).

Fichier : [../playbooks/notification-et-escalade.yml](../playbooks/notification-et-escalade.yml)

## Ce qu'il fait

1. Compare la sévérité de l'incident au seuil `SeuilEscalade` et retient le destinataire prioritaire
   ou le destinataire standard.
2. Demande un accusé de réception au destinataire retenu, via une tâche de communication native XSOAR.
3. Réponse "Acquitté" : le statut est marqué et le playbook s'arrête.
4. Réponse "Escalader maintenant", ou pas de réponse dans le délai : le contact d'escalade est
   notifié et l'incident est marqué comme escaladé.
5. En option, une tâche de création de ticket ITSM apparaît sur la branche d'escalade.

Le canal n'est pas figé dans le playbook. Par défaut le destinataire répond depuis le plan de travail
de l'incident, sans aucune intégration à installer. Pour pousser la demande sur un canal externe,
renseignez la méthode d'envoi de la tâche (Email, Slack ou Mattermost). Les destinataires viennent des
entrées, rien n'est codé en dur.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Facultatif : une intégration de messagerie (Email, Slack ou Mattermost) si vous voulez que la
  demande d'accusé parte sur un canal plutôt que d'être traitée depuis le plan de travail.
- Facultatif : une intégration ITSM pour automatiser la création de ticket à la place de la tâche
  manuelle.

## Le point à régler après l'import : l'escalade sur délai

Une tâche de communication XSOAR se termine sur la réponse choisie par le destinataire. Elle ne bascule
pas toute seule sur sa branche par défaut quand personne ne répond : sans réglage, elle reste en
attente. Deux options pour déclencher l'escalade automatiquement au bout du délai :

- Sur la tâche 5, onglet Timing, cocher "Complete task on SLA breach" et pointer la continuation vers
  la branche par défaut. C'est le réglage prévu pour ça, mais il se coche dans l'éditeur, pas dans le
  YAML.
- Ou associer un timer SLA à l'incident dont le script de dépassement est `CompleteTaskOnTimerBreach`,
  et le démarrer sur une tâche en amont.

En attendant, la réponse "Escalader maintenant" permet à un analyste de forcer l'escalade tout de
suite. Le délai lui-même est porté par le SLA de la tâche 5, fixé à 1 heure ; ajustez le bloc `sla`
de cette tâche pour le changer.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `SeuilEscalade` | `3` | Sévérité à partir de laquelle on vise le destinataire prioritaire. Échelle XSOAR : 0 = Inconnue, 0.5 = Informative, 1 = Faible, 2 = Moyenne, 3 = Élevée, 4 = Critique. |
| `DestinatairePrioritaire` | `${incident.owner}` | Destinataire pour les incidents au-dessus du seuil. À pointer vers l'équipe d'astreinte. |
| `DestinataireStandard` | `${incident.owner}` | Destinataire sous le seuil. |
| `DestinataireEscalade` | `${incident.owner}` | Contact prévenu en cas d'escalade (responsable, lead SOC). |
| `CreerTicketITSM` | `false` | Si `true`, ajoute la tâche manuelle de création de ticket ITSM. |

Les trois destinataires valent par défaut le propriétaire de l'incident, pour que le playbook tourne
tout de suite. En usage réel, remplacez-les par de vrais canaux ou utilisateurs.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Notification.Destinataire` | string | Destinataire retenu selon la sévérité. |
| `Notification.Statut` | string | `Accusé reçu` ou `Escalade - pas d'accusé dans le délai`. |
| `Notification.TicketITSM` | string | Renseigné si un ticket ITSM a été ouvert. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0 | Départ | start | Point d'entrée. |
| 1 | Notification et escalade | titre | Séparateur visuel. |
| 2 | Sévérité au-dessus du seuil ? | condition | `incident.severity >= inputs.SeuilEscalade`. |
| 3 | Cibler le destinataire prioritaire | script `Set` | `Notification.Destinataire = DestinatairePrioritaire`. |
| 4 | Cibler le destinataire standard | script `Set` | `Notification.Destinataire = DestinataireStandard`. |
| 5 | Demander l'accusé de réception | condition (communication) | Envoie la demande, attend "Acquitté" (vers 6). "Escalader maintenant" ou branche par défaut sur dépassement de SLA (vers 7). |
| 6 | Marquer l'accusé reçu | script `Set` | `Notification.Statut = Accusé reçu`. |
| 7 | Notifier le contact d'escalade | commande `send-notification` | Notifie `DestinataireEscalade`. Ignorée si aucune intégration ne fournit la commande. |
| 8 | Marquer l'escalade | script `Set` | `Notification.Statut = Escalade - pas d'accusé dans le délai`. |
| 9 | Créer un ticket ITSM ? | condition | Teste `inputs.CreerTicketITSM`. |
| 10 | Créer le ticket ITSM | manuelle | L'analyste crée le ticket et complète la tâche. |
| 11 | Marquer le ticket ITSM | script `Set` | `Notification.TicketITSM = Créé (tâche manuelle)`. |
| 12 | Fin | titre | Convergence des branches. |

## Tester

1. Créer un incident de test, s'en attribuer la propriété pour que `${incident.owner}` soit rempli.
2. Lancer le playbook. La demande d'accusé apparaît dans le plan de travail de l'incident (ou sur le
   canal configuré).
3. Répondre "Acquitté" et vérifier que `Notification.Statut` vaut `Accusé reçu`.
4. Rejouer et répondre "Escalader maintenant" (ou laisser le SLA se dépasser une fois la complétion sur
   SLA activée) : le contact d'escalade est notifié et le statut passe à
   `Escalade - pas d'accusé dans le délai`.
5. Rejouer avec `CreerTicketITSM = true` pour voir apparaître la tâche manuelle de ticket.

## Pour aller plus loin

- Remplacer la tâche manuelle de ticket par une commande automatisée (`jira-create-issue`,
  `servicenow-create-record`) selon l'outil ITSM en place.
- Étendre le routage au-delà de deux niveaux avec une liste XSOAR qui associe chaque sévérité à une
  équipe, à la place de la simple condition.
- Câbler le timer SLA et `CompleteTaskOnTimerBreach` pour une escalade entièrement automatique, sans
  intervention.
