# Offboarding sécurisé d'un collaborateur

Coupe les accès d'un collaborateur à son départ, mais seulement une fois le départ confirmé. Répond au
ticket [#22](https://github.com/yakohhhh/playbook-soar/issues/22).

Fichier : [../playbooks/offboarding-collaborateur.yml](../playbooks/offboarding-collaborateur.yml)

## Contexte

Dans une ESN, les consultants tournent vite. Un départ mal traité laisse des accès résiduels vers le SI
interne, parfois vers les environnements clients. Ce playbook sert de check-list traçable pour couper
proprement les accès.

## Ce qu'il fait

1. Vérifie que le départ est confirmé. Sinon, il ne fait rien.
2. Enrichit le compte (playbook d'enrichissement de compte) pour connaître son état.
3. Déroule les actions : désactivation et déconnexion, révocation des accès, gestion de la boîte mail.
4. Journalise la fin de l'offboarding.

Chaque action est une tâche à cocher dans le plan de travail, donc tracée pour la sécurité et les RH.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le playbook `Enrichissement de compte utilisateur` présent sur l'instance.
- Pour automatiser les actions, une intégration AD ou IAM. Sinon, ce sont des tâches manuelles.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `Collaborateur` | vide | Identifiant du collaborateur qui part. |
| `Manager` | vide | Manager qui récupère la délégation de boîte mail. |
| `DepartConfirme` | `false` | `true` seulement quand le départ est confirmé. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Offboarding.Statut` | string | `Accès coupés`, ou `Départ non confirmé - aucune action`. |
| `Compte.Statut` | string | État du compte relevé par l'enrichissement. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Départ confirmé ? | condition | `DepartConfirme = true`. |
| 3 | Enrichir le compte | sous-playbook | État du compte. |
| 4 | Désactiver le compte | manuelle | Désactivation et déconnexion des sessions. |
| 5 | Révoquer les accès | manuelle | Tokens et groupes sensibles. |
| 6 | Gérer la boîte mail | manuelle | Délégation ou transfert au manager. |
| 7 | Accès coupés | script `Set` | Statut de fin. |
| 8 | Départ non confirmé | script `Set` | Aucune action. |
| 9 | Fin | titre | Convergence. |

## Tester

1. Lancer avec `DepartConfirme = false` : `Offboarding.Statut = Départ non confirmé - aucune action`.
2. Rejouer avec `DepartConfirme = true` : les tâches d'offboarding s'ouvrent et le statut passe à
   `Accès coupés` une fois cochées.

## Pour aller plus loin

- Remplacer les tâches manuelles par les commandes AD/IAM (désactivation, révocation de sessions).
- Chercher les accès résiduels (partages, applications SaaS) et les lister dans le contexte.
