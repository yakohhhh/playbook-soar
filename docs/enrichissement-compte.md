# Enrichissement de compte utilisateur

Résout un compte dans l'Active Directory et remonte les attributs utiles au triage. Répond au ticket
[#4](https://github.com/yakohhhh/playbook-soar/issues/4).

Fichier : [../playbooks/enrichissement-compte.yml](../playbooks/enrichissement-compte.yml)

## Ce qu'il fait

1. Interroge l'AD avec `ad-get-user` sur l'identifiant fourni.
2. Si le compte existe, remonte ses groupes, sa valeur `userAccountControl` (pour lire l'état activé
   ou désactivé) et un drapeau compte à privilèges.
3. Si rien n'est trouvé, marque le compte comme introuvable et s'arrête.

Le drapeau à privilèges se base sur un mot-clé de groupe : dès qu'un groupe du compte contient ce
mot-clé (par défaut "Admin"), le compte est signalé à privilèges.

## Une note sur l'état désactivé

`userAccountControl` est un champ de bits. Un compte est désactivé quand le bit 2 est positionné :
les valeurs courantes sont 514 (désactivé) contre 512 (actif), 66050 contre 66048, etc. Le playbook
remonte la valeur brute dans `Compte.UAC` ; à l'analyste ou à une étape suivante de l'interpréter, ou
de s'appuyer sur le champ dédié de l'intégration si elle en expose un.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Une intégration Active Directory qui répond à `ad-get-user`. Sans elle, le compte est considéré
  comme introuvable et le playbook se termine proprement.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `NomUtilisateur` | vide | Identifiant du compte (login, avec ou sans domaine). |
| `MotifGroupePrivilegie` | `Admin` | Mot-clé cherché dans les groupes pour signaler un compte à privilèges. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Compte.Statut` | string | `Trouvé` ou `Introuvable`. |
| `Compte.Groupes` | array | Groupes d'appartenance. |
| `Compte.UAC` | | Valeur `userAccountControl` pour lire l'état activé/désactivé. |
| `Compte.APrivileges` | string | `Oui` ou `Non`. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Interroger l'Active Directory | commande `ad-get-user` | Récupère le compte. |
| 3 | Compte trouvé ? | condition | `ActiveDirectory.Users.dn` existe. |
| 4-6 | Compte trouvé, groupes, état | script `Set` | Remonte statut, groupes et UAC. |
| 7 | Compte à privilèges ? | condition | Un groupe contient le mot-clé. |
| 8, 10 | Compte à privilèges / standard | script `Set` | Drapeau `Compte.APrivileges`. |
| 9 | Compte introuvable | script `Set` | Statut introuvable. |
| 11 | Fin | titre | Convergence. |

## Tester

1. Renseigner `NomUtilisateur` avec un compte existant et lancer.
2. Vérifier `Compte.Statut`, `Compte.Groupes` et `Compte.APrivileges`.
3. Rejouer avec un identifiant bidon : `Compte.Statut = Introuvable`, sans erreur.

## Pour aller plus loin

- Ajouter la résolution du manager et de la dernière connexion selon les attributs disponibles.
- Interpréter `userAccountControl` dans une condition pour poser directement un drapeau désactivé.
- Étendre à Azure AD / un annuaire IAM en ajoutant une commande de repli.
