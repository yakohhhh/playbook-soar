# Enrichissement de vulnérabilité (CVE)

À partir d'un identifiant CVE, récupère les détails via la commande générique `!cve` et propose une
priorité de traitement. Répond au ticket
[#10](https://github.com/yakohhhh/playbook-soar/issues/10).

Fichier : [../playbooks/enrichissement-cve.yml](../playbooks/enrichissement-cve.yml)

## Ce qu'il fait

1. Interroge la CVE avec `!cve` (commande générique, sans fournisseur codé en dur).
2. Si rien ne revient (CVE inexistante ou mal formée), termine avec la priorité `CVE introuvable`.
3. Sinon, calcule une priorité à partir du score CVSS. Un exploit public connu, signalé en entrée,
   force la priorité au niveau critique quel que soit le CVSS.

Grille de priorité :

- exploit public connu : `Critique (exploit public connu)`
- CVSS >= 9 : `Critique`
- CVSS >= 7 : `Élevée`
- CVSS >= 4 : `Moyenne`
- en dessous : `Faible`

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Une intégration qui répond à `!cve` (VulnDB, CVE Search, un TIP...). Sans elle, la CVE est
  considérée comme introuvable et le playbook se termine proprement.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `cve_id` | vide | Identifiant de la CVE à enrichir (par exemple CVE-2021-44228). |
| `ExploitConnu` | `false` | `true` si un exploit public est connu. Le renseigner depuis une source comme la CISA KEV. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `CVE_Triage.Priorite` | string | Priorité proposée, ou `CVE introuvable`. |
| `CVE` | object | Détails renvoyés par l'intégration (CVSS, description, dates). |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0-1 | Départ, titre | start / titre | Entrée du playbook. |
| 2 | Rechercher la CVE | commande `!cve` | Enrichit la CVE. |
| 3 | CVE trouvée ? | condition | `CVE.ID` existe. Sinon branche "introuvable" (13). |
| 4 | Exploit public connu ? | condition | `inputs.ExploitConnu` vaut `true`. |
| 5, 7, 9, 11, 12 | Priorité ... | script `Set` | Écrit le niveau retenu dans `CVE_Triage.Priorite`. |
| 6, 8, 10 | CVSS >= 9 / 7 / 4 ? | condition | Cascade sur `CVE.CVSS`. |
| 13 | CVE introuvable | script `Set` | Priorité `CVE introuvable`. |
| 14 | Fin | titre | Convergence. |

## Tester

1. Renseigner `cve_id` avec une CVE connue à fort CVSS (par exemple CVE-2021-44228) et lancer.
2. Vérifier `CVE_Triage.Priorite` et le contenu de `CVE`.
3. Rejouer avec `ExploitConnu = true` : la priorité passe à `Critique (exploit public connu)`.
4. Rejouer avec un identifiant bidon (`CVE-0000-0000`) : le playbook se termine en `CVE introuvable`.

## Pour aller plus loin

- Alimenter `ExploitConnu` automatiquement en croisant la CVE avec la liste CISA KEV.
- Remonter la priorité dans un champ d'incident (`setIncident`) pour piloter le tri.
