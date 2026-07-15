# Clôture automatique des faux positifs connus

Compare une valeur de l'incident à une allow-list de faux positifs déjà catalogués. Si ça correspond,
l'incident est clôturé en faux positif avec une note qui garde la trace du motif. Sinon, l'incident
continue son parcours normal. Répond au ticket
[#8](https://github.com/yakohhhh/playbook-soar/issues/8).

Fichier : [../playbooks/cloture-faux-positifs.yml](../playbooks/cloture-faux-positifs.yml)

## Ce qu'il fait

1. Teste `ValeurAComparer` (par défaut le nom de l'incident) contre l'allow-list `MotifsFauxPositifs`.
2. Si la valeur figure dans l'allow-list (comparaison insensible à la casse), enregistre le motif,
   marque le statut et clôture l'incident en "False Positive" avec une note.
3. Sans correspondance, marque simplement le statut et laisse l'incident suivre son cours.

La clôture n'a lieu que sur une correspondance explicite : la condition exige à la fois une valeur non
vide et sa présence dans l'allow-list. Une liste vide n'entraîne donc aucune clôture.

## Prérequis

- Cortex XSOAR 6.5 ou plus récent.
- Aucune intégration : `Set`, la condition et la commande `closeInvestigation` (Builtin) sont natives.

## Entrées

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `MotifsFauxPositifs` | vide | Allow-list des motifs de faux positifs, séparés par des virgules. Comparaison insensible à la casse. |
| `ValeurAComparer` | `${incident.name}` | Valeur de l'incident testée contre l'allow-list. |
| `MotifCloture` | Texte par défaut | Note ajoutée à la clôture, après le motif reconnu. |

L'allow-list est un simple champ séparé par des virgules, pratique pour démarrer. En pratique, on la
tient souvent dans une liste XSOAR mise à jour au fil de l'eau, dont on branche le contenu sur
`MotifsFauxPositifs`.

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `FauxPositifs.Statut` | string | `Clôturé - faux positif connu` ou `Pas de correspondance - traitement normal`. |
| `FauxPositifs.Motif` | string | Motif reconnu, en cas de correspondance. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0 | Départ | start | Point d'entrée. |
| 1 | Clôture des faux positifs connus | titre | Séparateur visuel. |
| 2 | Faux positif connu ? | condition | `ValeurAComparer` non vide ET présente dans `MotifsFauxPositifs`. Vrai vers 3, sinon vers 6. |
| 3 | Retenir le motif | script `Set` | `FauxPositifs.Motif = ValeurAComparer`. |
| 4 | Marquer la clôture | script `Set` | `FauxPositifs.Statut = Clôturé - faux positif connu`. |
| 5 | Clôturer l'incident | commande `closeInvestigation` | Clôture en `False Positive`, motif conservé dans la note. |
| 6 | Laisser suivre le flux normal | script `Set` | `FauxPositifs.Statut = Pas de correspondance - traitement normal`. |
| 7 | Fin | titre | Convergence des deux branches. |

## Tester

1. Créer un incident de test dont le nom vaut un motif connu, par exemple `EICAR Test File`.
2. Renseigner `MotifsFauxPositifs` avec ce motif (`EICAR Test File`) et lancer le playbook.
3. Vérifier que l'incident est clôturé en faux positif, que la note reprend le motif, et que
   `FauxPositifs.Statut` vaut `Clôturé - faux positif connu`.
4. Rejouer avec un incident dont le nom n'est pas dans la liste : il reste ouvert et le statut passe à
   `Pas de correspondance - traitement normal`.

## Pour aller plus loin

- Comparer un champ plus stable que le nom (règle, signature, catégorie) en changeant `ValeurAComparer`.
- Pour suivre le volume traité, une tâche de journalisation ou une statistique sur les incidents
  clôturés automatiquement rend le gain visible.
