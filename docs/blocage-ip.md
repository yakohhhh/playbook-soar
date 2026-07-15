# Blocage d'IP malveillante

Bloque une IP après deux garde-fous : un contrôle de liste d'exclusion et une validation analyste.
Répond au ticket [#3](https://github.com/yakohhhh/playbook-soar/issues/3).

Fichier : [../playbooks/blocage-ip.yml](../playbooks/blocage-ip.yml)

## Ce qu'il fait

1. Vérifie si l'IP appartient à une plage d'exclusion (script `IsIPInRanges`).
2. Si oui, refuse le blocage et s'arrête.
3. Sinon, demande une validation à l'analyste.
4. Sur accord, la règle de blocage est appliquée et le statut journalisé. Sur refus, rien n'est fait.

Aucune IP n'est bloquée sans passer par la validation, et les adresses internes ou partenaires sont
écartées d'entrée.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le script `IsIPInRanges` (fourni dans le pack Common Scripts, présent par défaut).
- Pour automatiser le blocage, une intégration pare-feu (Panorama, Check Point...). Sinon, l'étape de
  blocage est une tâche manuelle à cocher par l'analyste.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `IP` | vide | Adresse IP à évaluer pour un blocage. |
| `PlagesExclusion` | plages privées + boucle locale | Plages CIDR qu'on ne bloque jamais. |

La valeur par défaut de `PlagesExclusion` couvre `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` et
`127.0.0.0/8`. Ajoutez-y vos plages partenaires.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Blocage.Statut` | string | `Bloqué`, `Annulé par l'analyste`, ou `Refusé - IP dans une plage exclue`. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Plage exclue ? | script `IsIPInRanges` | Renseigne `IP.InRange`. |
| 3 | IP exclue ? | condition | `IP.InRange = yes` mène au refus. |
| 4 | Blocage refusé | script `Set` | Statut de refus. |
| 5 | Valider le blocage | condition (communication) | Attend "Bloquer" ou "Annuler" de l'analyste. |
| 6 | Pousser la règle de blocage | manuelle | Applique le blocage sur la solution réseau. |
| 7 | Blocage annulé | script `Set` | Statut annulé. |
| 8 | Blocage effectué | script `Set` | Statut bloqué. |
| 9 | Fin | titre | Convergence. |

La tâche 5 attend la réponse de l'analyste ; c'est volontaire, on ne bloque ni n'annule tout seul.

## Tester

1. Lancer avec une IP publique (par exemple `203.0.113.10`) : la validation apparaît dans le plan de
   travail. Répondre "Bloquer" et vérifier `Blocage.Statut = Bloqué`.
2. Rejouer et répondre "Annuler" : `Blocage.Statut = Annulé par l'analyste`.
3. Lancer avec une IP interne (`10.1.2.3`) : le blocage est refusé sans demander de validation.

## Pour aller plus loin

- Remplacer la tâche manuelle de blocage par la commande de l'intégration pare-feu, ou par le
  sous-playbook générique de blocage d'IP.
- Enrichir l'IP avant le blocage (playbook d'enrichissement) pour n'ouvrir la validation que sur les
  IP réellement malveillantes.
