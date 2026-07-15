# Détection de connexion impossible (voyage impossible)

Qualifie une alerte de voyage impossible : deux connexions d'un même compte depuis des lieux
incompatibles. Répond au ticket
[#23](https://github.com/yakohhhh/playbook-soar/issues/23).

Fichier : [../playbooks/voyage-impossible.yml](../playbooks/voyage-impossible.yml)

## Contexte

Les consultants d'une ESN se connectent depuis des sites clients, en télétravail, en déplacement. Une
alerte de voyage impossible est fréquente mais souvent explicable par un VPN. Ce playbook fait le tri.

## Ce qu'il fait

1. Écarte l'IP source si elle est dans une plage connue (VPN, sites) : déplacement légitime.
2. Sinon, enrichit l'IP source et le compte.
3. Si le voyage impossible est confirmé et l'IP malveillante : compromission probable. Confirmé sans IP
   malveillante : à surveiller. Non confirmé : RAS.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Les playbooks `Enrichissement d'indicateurs (générique)` et `Enrichissement de compte utilisateur`.
- `IsIPInRanges` (pack Common Scripts, présent par défaut).

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `Compte` | vide | Compte concerné. |
| `IPSource` | vide | IP source de la connexion suspecte. |
| `PlagesVPN` | vide | Plages CIDR connues (VPN, sites) à renseigner. |
| `VoyageImpossible` | `false` | `true` si l'alerte source a détecté un voyage impossible. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Connexion.Verdict` | string | `Déplacement légitime`, `À surveiller`, `Compromission probable`, ou `RAS`. |
| `Enrichissement.Verdict` | string | Réputation de l'IP source. |
| `Compte.Statut` | string | Résultat de l'enrichissement du compte. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | IP connue ? | script `IsIPInRanges` | Compare aux plages VPN/sites. |
| 3 | IP connue ? | condition | `IP.InRange = yes` mène au déplacement légitime. |
| 4 | Déplacement légitime | script `Set` | Verdict légitime. |
| 5 | Enrichir l'IP source | sous-playbook | Réputation de l'IP. |
| 6 | Enrichir le compte | sous-playbook | Contexte du compte. |
| 7 | Voyage impossible confirmé ? | condition | `VoyageImpossible = true`. |
| 8 | IP source malveillante ? | condition | `Enrichissement.Verdict = Malveillant`. |
| 9, 10, 11 | Verdict ... | script `Set` | Compromission / surveiller / RAS. |
| 12 | Fin | titre | Convergence. |

## Tester

1. Renseigner `PlagesVPN` avec vos plages, `IPSource` dans une de ces plages : verdict `Déplacement
   légitime`.
2. IP hors plages, `VoyageImpossible = true`, IP malveillante connue : `Compromission probable`.
3. IP hors plages, `VoyageImpossible = true`, IP propre : `À surveiller`.

## Pour aller plus loin

- Calculer réellement la distance et la vitesse entre les deux connexions avec un script de géodistance.
- Enchaîner sur le blocage d'IP ou la réinitialisation du compte quand la compromission est probable.
