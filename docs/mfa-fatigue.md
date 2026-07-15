# Réponse à une attaque MFA fatigue (push bombing)

Détecte une rafale de demandes MFA, confirme avec l'utilisateur, et ne protège le compte qu'en
l'absence de reconnaissance. Répond au ticket
[#27](https://github.com/yakohhhh/playbook-soar/issues/27).

Fichier : [../playbooks/mfa-fatigue.yml](../playbooks/mfa-fatigue.yml)

## Contexte

Les comptes cloud d'une ESN (Microsoft 365, fournisseur d'identité) sont protégés par MFA push. Une
rafale de demandes vise à faire approuver une connexion par lassitude de l'utilisateur.

## Ce qu'il fait

1. Enrichit le compte ciblé.
2. Compare le nombre de demandes MFA au seuil. Sous le seuil : rien à signaler.
3. Au-dessus, demande à l'utilisateur s'il est à l'origine des demandes.
4. S'il reconnaît : rien à faire. Sinon (ou sans réponse), gèle les sessions et force une
   réinitialisation MFA.

Le compte n'est jamais gelé tant que l'utilisateur n'a pas eu l'occasion de confirmer.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le playbook `Enrichissement de compte utilisateur` présent sur l'instance.
- Pour automatiser la protection, une intégration du fournisseur d'identité. Sinon, le gel et la
  réinitialisation sont des tâches manuelles.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `Compte` | vide | Compte ciblé. |
| `NombreDemandes` | `0` | Nombre de demandes MFA observées. |
| `SeuilDemandes` | `5` | Seuil à partir duquel on parle de rafale. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `MFA.Statut` | string | `Compte protégé`, `Demandes reconnues`, ou `Sous le seuil - RAS`. |
| `Compte.Statut` | string | Résultat de l'enrichissement du compte. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Enrichir le compte | sous-playbook | Contexte du compte. |
| 3 | Rafale de demandes ? | condition | `NombreDemandes >= SeuilDemandes`. |
| 4 | Confirmer avec l'utilisateur | condition (communication) | "Oui c'est moi" ou "Non". |
| 5 | Geler les sessions | manuelle | Révocation des sessions. |
| 6 | Réinitialiser la MFA | manuelle | Reset MFA. |
| 7, 8, 9 | Statut ... | script `Set` | Protégé / reconnu / sous le seuil. |
| 10 | Fin | titre | Convergence. |

## Tester

1. `NombreDemandes = 2`, `SeuilDemandes = 5` : `MFA.Statut = Sous le seuil - RAS`.
2. `NombreDemandes = 12` puis répondre "Oui c'est moi" : `Demandes reconnues par l'utilisateur - RAS`.
3. `NombreDemandes = 12` puis répondre "Non" : les tâches de protection s'ouvrent, puis
   `MFA.Statut = Compte protégé`.

## Pour aller plus loin

- Remplacer les tâches manuelles par les commandes du fournisseur d'identité (révocation de sessions,
  reset MFA).
- Activer la complétion sur SLA de la tâche de confirmation pour geler automatiquement sans réponse.
