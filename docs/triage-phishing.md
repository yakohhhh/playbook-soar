# Triage d'email de phishing

Prend un email signalé, enrichit ses artefacts en réutilisant le playbook d'enrichissement générique,
puis pose un verdict de triage et une sévérité. Répond au ticket
[#2](https://github.com/yakohhhh/playbook-soar/issues/2).

Fichier : [../playbooks/triage-phishing.yml](../playbooks/triage-phishing.yml)

## Ce qu'il fait

1. Retient l'expéditeur de l'email.
2. Appelle en sous-playbook `Enrichissement d'indicateurs (générique)` sur les URLs et les hash de
   pièces jointes.
3. Selon le verdict d'enrichissement, conclut à un email `Malveillant`, `Suspect` ou `Bénin`, et pose
   une sévérité correspondante.

Si l'email n'a ni URL ni pièce jointe, l'enrichissement ne trouve rien et le triage conclut à un email
bénin, sans erreur.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Le playbook `Enrichissement d'indicateurs (générique)` doit être présent sur l'instance (il est
  appelé en sous-playbook).
- Une intégration de réputation pour que l'enrichissement soit utile.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `URLs` | `${incident.emailurlclicked}` | URLs présentes dans l'email. |
| `HashesFichiers` | vide | Hash des pièces jointes, s'il y en a. |
| `ExpediteurEmail` | `${incident.emailfrom}` | Adresse de l'expéditeur. |

Les valeurs par défaut pointent vers les champs d'un incident de type phishing. Sur un autre type
d'incident, renseigner les entrées à la main.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Phishing.Verdict` | string | `Malveillant`, `Suspect` ou `Bénin`. |
| `Phishing.Severite` | string | `Élevée`, `Moyenne` ou `Faible`. |
| `Phishing.Expediteur` | string | Adresse de l'expéditeur. |

Le verdict brut de l'enrichissement reste disponible sous `Enrichissement.Verdict`.

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Retenir l'expéditeur | script `Set` | `Phishing.Expediteur`. |
| 3 | Enrichir les artefacts | sous-playbook | Appelle l'enrichissement générique (URLs, hash). |
| 4 | Verdict malveillant ? | condition | `Enrichissement.Verdict = Malveillant`. |
| 7 | Verdict suspect ? | condition | `Enrichissement.Verdict = Suspect`. |
| 5, 8, 10 | Verdict ... | script `Set` | Écrit `Phishing.Verdict`. |
| 6, 9, 11 | Sévérité ... | script `Set` | Écrit `Phishing.Severite`. |
| 12 | Fin du triage | titre | Convergence. |

## Tester

1. Sur un incident de phishing avec une URL malveillante connue, lancer le playbook.
2. Vérifier `Phishing.Verdict` (Malveillant) et `Phishing.Severite` (Élevée).
3. Rejouer sur un email sans URL ni pièce jointe : le triage conclut à `Bénin` sans erreur.

## Pour aller plus loin

- Extraire aussi les URLs directement du corps de l'email (script d'extraction) avant l'enrichissement.
- Poser la sévérité calculée sur l'incident avec `setIncident`, ou clôturer les emails bénins.
- Enchaîner sur le playbook de blocage pour les indicateurs malveillants confirmés.
