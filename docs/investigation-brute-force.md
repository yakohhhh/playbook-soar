# Investigation de connexions suspectes / brute force

Investigue une série d'échecs d'authentification, enrichit l'IP source et le compte, puis tranche entre
bruit, brute force et compromission. Répond au ticket
[#6](https://github.com/yakohhhh/playbook-soar/issues/6).

Fichier : [../playbooks/investigation-brute-force.yml](../playbooks/investigation-brute-force.yml)

## Ce qu'il fait

1. Enrichit l'IP source (playbook d'enrichissement générique) et le compte visé (playbook
   d'enrichissement de compte).
2. Compare le nombre de tentatives au seuil de brute force.
3. Rend un verdict :
   - en dessous du seuil : `Bruit - échec isolé`
   - au-dessus du seuil, sans succès : `Brute force à surveiller`
   - au-dessus du seuil, avec une connexion réussie : `Compromission probable`

Le nombre de tentatives et l'indication d'une connexion réussie viennent de l'alerte source, passés en
entrée.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Les playbooks `Enrichissement d'indicateurs (générique)` et `Enrichissement de compte utilisateur`
  présents sur l'instance (appelés en sous-playbooks).

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `CompteCible` | vide | Compte visé par les tentatives. |
| `IPSource` | vide | IP source des tentatives. |
| `NombreTentatives` | `0` | Nombre d'échecs observés. |
| `SeuilBruteForce` | `10` | Seuil à partir duquel on parle de brute force. |
| `ConnexionReussie` | `false` | `true` si une connexion a réussi après les échecs. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `BruteForce.Verdict` | string | `Bruit - échec isolé`, `Brute force à surveiller`, ou `Compromission probable`. |
| `Enrichissement.Verdict` | string | Réputation de l'IP source. |
| `Compte.Statut` | string | Résultat de l'enrichissement du compte. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Enrichir l'IP source | sous-playbook | Enrichissement générique de l'IP. |
| 3 | Enrichir le compte | sous-playbook | Enrichissement du compte visé. |
| 4 | Motif de brute force ? | condition | `NombreTentatives >= SeuilBruteForce`. |
| 5 | Connexion réussie ? | condition | `ConnexionReussie = true`. |
| 6, 7, 8 | Verdict ... | script `Set` | Écrit `BruteForce.Verdict`. |
| 9 | Fin | titre | Convergence. |

## Tester

1. Lancer avec `NombreTentatives = 3` (sous le seuil) : verdict `Bruit - échec isolé`.
2. Rejouer avec `NombreTentatives = 25` et `ConnexionReussie = false` : `Brute force à surveiller`.
3. Rejouer avec `NombreTentatives = 25` et `ConnexionReussie = true` : `Compromission probable`.

## Pour aller plus loin

- Récupérer directement le nombre de tentatives depuis le SIEM plutôt que de le passer en entrée.
- Intégrer la réputation de l'IP source (`Enrichissement.Verdict`) dans la décision.
- Enchaîner sur le blocage d'IP ou la réinitialisation du compte quand la compromission est probable.
