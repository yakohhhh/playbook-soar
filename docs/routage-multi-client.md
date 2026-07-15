# Routage multi-client d'un incident (SOC managé)

Aiguille un incident vers le bon client et cloisonne sa visibilité. Répond au ticket
[#25](https://github.com/yakohhhh/playbook-soar/issues/25).

Fichier : [../playbooks/routage-multi-client.yml](../playbooks/routage-multi-client.yml)

## Contexte

Une ESN qui opère un SOC managé traite depuis une même plateforme les incidents de plusieurs clients.
Chaque incident doit atterrir chez le bon client, et surtout ne jamais être visible des autres.

## Ce qu'il fait

1. Vérifie que le client a été identifié (à partir de l'actif, en amont).
2. Affecte l'incident au propriétaire du client et restreint sa visibilité au rôle du client
   (`setIncident owner` + `roles`) : c'est ce cloisonnement par rôle qui évite le mélange de données.
3. Pose le tag client et notifie le client en réutilisant le playbook de notification.
4. Si le client n'est pas identifié, l'incident part en routage manuel.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le playbook `Notification et escalade` présent sur l'instance.
- Des rôles XSOAR par client configurés pour que la restriction de visibilité ait un sens.

## Entrées

| Nom | Rôle |
| --- | --- |
| `Client` | Client déterminé depuis l'actif (domaine, plage IP, tag). |
| `ProprietaireClient` | Propriétaire ou équipe à qui affecter l'incident. |
| `RoleClient` | Rôle XSOAR du client, pour restreindre la visibilité. |
| `DestinataireClient` | Destinataire ou canal de notification du client. |

Aucun client n'est codé en dur : tout vient des entrées, alimentées par votre table de routage.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Routage.Client` | string | Client vers lequel l'incident a été routé. |
| `Routage.Statut` | string | `Routé vers le client`, ou `Client non identifié - routage manuel`. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Client identifié ? | condition | `Client` non vide. |
| 3 | Affecter et cloisonner | commande `setIncident` | Owner + roles. |
| 4 | Poser le tag client | script `Set` | `Routage.Client`. |
| 5 | Notifier le client | sous-playbook | Notification et escalade. |
| 6 | Incident routé | script `Set` | Statut routé. |
| 7 | Client non identifié | script `Set` | Routage manuel. |
| 8 | Fin | titre | Convergence. |

## Tester

1. Renseigner `Client`, `ProprietaireClient`, `RoleClient`, `DestinataireClient` et lancer : l'incident
   est affecté, restreint au rôle, tagué et notifié ; `Routage.Statut = Routé vers le client`.
2. Lancer sans `Client` : `Routage.Statut = Client non identifié - routage manuel`.

## Pour aller plus loin

- Identifier le client dans le playbook à partir d'une liste XSOAR (actif vers client) plutôt qu'en
  entrée.
- Router aussi vers un tenant ou un espace de travail dédié quand la plateforme est multi-tenant.
