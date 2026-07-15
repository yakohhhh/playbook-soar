# Consentement OAuth suspect (M365 / Google Workspace)

Trie une alerte de consentement OAuth et contient les applications à risque. Répond au ticket
[#24](https://github.com/yakohhhh/playbook-soar/issues/24).

Fichier : [../playbooks/oauth-suspect.yml](../playbooks/oauth-suspect.yml)

## Contexte

Les environnements d'une ESN sont très SaaS. Le phishing par consentement OAuth donne à une application
tierce un accès durable aux données, sans mot de passe et sans déclencher les alertes de connexion
classiques. Il faut trier vite et révoquer proprement.

## Ce qu'il fait

1. Si l'application est déjà approuvée, rien à faire.
2. Sinon, évalue le risque des permissions accordées (mails, fichiers, annuaire, accès hors ligne).
3. Sur permissions à risque, demande une validation puis révoque l'application et prévient
   l'utilisateur. Sur permissions limitées, marque l'application à surveiller.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Pour automatiser la révocation, une intégration Microsoft Graph ou Google Workspace. Sinon, la
  révocation et la notification sont des tâches manuelles.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `Application` | vide | Nom ou identifiant de l'application. |
| `Utilisateur` | vide | Utilisateur qui a consenti. |
| `Scopes` | vide | Permissions accordées. |
| `AppApprouvee` | `false` | `true` si l'application est déjà approuvée. |

Les permissions considérées à risque contiennent les mots-clés `Mail`, `Files`, `Directory`,
`full_access` ou `offline_access`. Ajustez la condition de la tâche 4 selon votre référentiel.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `OAuth.Statut` | string | `approuvée`, `révoquée`, `à surveiller`, ou `révocation non validée`. |
| `OAuth.Risque` | string | Niveau de risque des permissions. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Application approuvée ? | condition | `AppApprouvee = true`. |
| 4 | Permissions à risque ? | condition | Les scopes contiennent un mot-clé sensible. |
| 5 | Risque élevé | script `Set` | `OAuth.Risque = Élevé`. |
| 6 | Valider la révocation | condition (communication) | Attend "Révoquer" ou "Ignorer". |
| 7 | Révoquer l'application | manuelle | Révocation sur le fournisseur SaaS. |
| 8 | Prévenir l'utilisateur | manuelle | Notification. |
| 3, 9, 10, 11 | Statut ... | script `Set` | Écrit `OAuth.Statut`. |
| 12 | Fin | titre | Convergence. |

## Tester

1. `AppApprouvee = true` : `OAuth.Statut = Application approuvée - RAS`.
2. `AppApprouvee = false`, `Scopes = Mail.Read offline_access` : validation demandée, puis sur
   "Révoquer" le statut passe à `Application révoquée`.
3. `AppApprouvee = false`, `Scopes = User.Read` : `Application inconnue, scopes limités - à surveiller`.

## Pour aller plus loin

- Remplacer les tâches manuelles par les commandes de révocation Microsoft Graph / Google Workspace.
- Croiser l'application avec une liste d'applications approuvées maintenue dans une liste XSOAR.
