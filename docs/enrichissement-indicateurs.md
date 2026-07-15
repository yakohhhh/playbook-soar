# Enrichissement d'indicateurs (générique)

Récupère la réputation d'indicateurs (IP, domaine, URL, hash) via les commandes de réputation
génériques de XSOAR, puis en tire un verdict consolidé. Conçu pour être appelé par d'autres playbooks.
Répond au ticket [#1](https://github.com/yakohhhh/playbook-soar/issues/1).

Fichier : [../playbooks/enrichissement-indicateurs.yml](../playbooks/enrichissement-indicateurs.yml)

## Ce qu'il fait

1. Lance `!ip`, `!domain`, `!url` et `!file` sur les indicateurs passés en entrée.
2. Chaque appel est générique : il part vers l'intégration de réputation installée, sans nom de
   fournisseur codé en dur, et il est ignoré si l'intégration manque ou si le type est absent.
3. Calcule un verdict à partir du DBotScore le plus élevé : `Malveillant` (score 3), `Suspect`
   (score 2), sinon `Non concluant`.

Comme les commandes portent `skipunavailable` et `continueonerror`, le playbook ne tombe jamais en
erreur si un type d'indicateur n'est pas fourni ou si aucune intégration ne répond.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Au moins une intégration de réputation (VirusTotal, AbuseIPDB, un TIP, etc.) pour obtenir des scores.
  Sans elle, le playbook s'exécute quand même et renvoie `Non concluant`.

## Entrées

| Nom | Rôle |
| --- | --- |
| `IP` | Une ou plusieurs adresses IP à enrichir. |
| `Domain` | Un ou plusieurs domaines. |
| `URL` | Une ou plusieurs URLs. |
| `FileHash` | Un ou plusieurs hash de fichiers. |

Toutes les entrées sont facultatives. On peut n'en renseigner qu'une.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Enrichissement.Verdict` | string | `Malveillant`, `Suspect` ou `Non concluant`. |
| `DBotScore` | array | Scores de réputation par indicateur, renseignés par les intégrations. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0 | Départ | start | Point d'entrée. |
| 1 | Enrichissement d'indicateurs | titre | Séparateur visuel. |
| 2 | Réputation IP | commande `!ip` | Enrichit les IP. |
| 3 | Réputation domaine | commande `!domain` | Enrichit les domaines. |
| 4 | Réputation URL | commande `!url` | Enrichit les URLs. |
| 5 | Réputation fichier | commande `!file` | Enrichit les hash. |
| 6 | Un indicateur malveillant ? | condition | `DBotScore.Score >= 3`. |
| 7 | Verdict malveillant | script `Set` | `Enrichissement.Verdict = Malveillant`. |
| 8 | Un indicateur suspect ? | condition | `DBotScore.Score >= 2`. |
| 9 | Verdict suspect | script `Set` | `Enrichissement.Verdict = Suspect`. |
| 10 | Verdict non concluant | script `Set` | `Enrichissement.Verdict = Non concluant`. |
| 11 | Fin | titre | Convergence. |

## Tester

1. Renseigner `IP` avec une adresse connue pour être malveillante par ton intégration de réputation.
2. Lancer le playbook et vérifier `Enrichissement.Verdict` et le contenu de `DBotScore`.
3. Rejouer avec une IP propre : le verdict doit passer à `Non concluant`.
4. Lancer sans aucune entrée : le playbook se termine proprement en `Non concluant`.

## Pour aller plus loin

- Appeler ce playbook comme sous-playbook depuis un playbook de triage (phishing, alerte endpoint).
- Ajuster les seuils de verdict, ou pondérer selon la fiabilité (`DBotScore.Reliability`) des sources.
