# Triage d'exfiltration de données

Qualifie une alerte d'exfiltration et propose une réponse, en écartant d'abord les partages internes.
Répond au ticket [#26](https://github.com/yakohhhh/playbook-soar/issues/26).

Fichier : [../playbooks/triage-exfiltration.yml](../playbooks/triage-exfiltration.yml)

## Contexte

Une ESN manipule des données clients sensibles. Un partage externe massif ou un envoi vers une adresse
personnelle doit être trié vite, d'autant plus s'il vient d'un consultant sur le départ.

## Ce qu'il fait

1. Écarte les destinations internes, souvent des partages métier légitimes.
2. Enrichit l'utilisateur (playbook d'enrichissement de compte) pour savoir s'il est à privilèges.
3. Selon le volume comparé au seuil, conclut à une exfiltration probable ou à un cas à confirmer, et
   propose une réponse.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le playbook `Enrichissement de compte utilisateur` présent sur l'instance.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `Utilisateur` | vide | Utilisateur à l'origine du transfert. |
| `Ressource` | vide | Ressource ou fichier concerné. |
| `Destination` | vide | Destination du transfert. |
| `Volume` | `0` | Volume transféré. |
| `SeuilVolume` | `100` | Seuil au-delà duquel l'exfiltration devient probable. |
| `DomaineInterne` | vide | Domaine interne, pour écarter les destinations internes. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Exfiltration.Verdict` | string | `Faux positif`, `À confirmer`, ou `Exfiltration probable`. |
| `Exfiltration.Reponse` | string | Réponse recommandée. |
| `Compte.APrivileges` | string | Si l'utilisateur est à privilèges. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Destination interne ? | condition | Domaine interne renseigné et présent dans la destination. |
| 3 | Faux positif | script `Set` | Destination interne. |
| 4 | Enrichir l'utilisateur | sous-playbook | Contexte du compte. |
| 5 | Volume au-dessus du seuil ? | condition | `Volume >= SeuilVolume`. |
| 6, 7 | Verdict ... | script `Set` | Exfiltration probable / à confirmer. |
| 8, 9 | Réponse ... | script `Set` | Contenir / vérifier. |
| 10 | Fin | titre | Convergence. |

## Tester

1. `Destination` contenant le `DomaineInterne` : `Exfiltration.Verdict = Faux positif`.
2. Destination externe, `Volume = 500`, `SeuilVolume = 100` : `Exfiltration probable`, réponse de
   confinement.
3. Destination externe, `Volume = 10` : `À confirmer`, réponse de vérification.

## Pour aller plus loin

- Croiser avec le playbook d'offboarding pour repérer les départs récents.
- Enchaîner sur le gel du compte quand l'exfiltration est probable.
