# Prise en main XSOAR - Triage

Playbook d'initiation pour découvrir la mécanique d'un playbook Cortex XSOAR sans dépendre d'une
intégration externe. Il reprend les briques qu'on retrouve dans presque tous les playbooks : une
entrée paramétrable, un script natif qui écrit dans le contexte, une condition qui aiguille le flux,
et une trace dans le War Room.

Fichier : [../playbooks/prise-en-main-xsoar.yml](../playbooks/prise-en-main-xsoar.yml)

## Ce qu'il fait

Sur un incident, le playbook :

1. relève la date de création de l'incident et la range dans le contexte,
2. compare la sévérité de l'incident au seuil passé en entrée,
3. part sur une branche d'escalade si la sévérité est au-dessus du seuil, sinon sur une branche de
   traitement standard,
4. écrit la décision dans le contexte et un message dans le War Room.

Il ne ferme pas l'incident et ne modifie aucun champ sensible. L'idée est de rester lisible et sans
effet de bord pour un premier essai.

## Prérequis

- Une instance Cortex XSOAR 6.5 ou plus récente (champ `fromversion` du playbook).
- Aucune intégration à installer : `Set`, `Print` et la tâche conditionnelle sont fournis en natif.

## Entrée

| Nom | Défaut | Rôle |
| --- | --- | --- |
| `SeuilSeverite` | `3` | Seuil qui déclenche l'escalade. Échelle XSOAR : 0 = Inconnue, 0.5 = Informative, 1 = Faible, 2 = Moyenne, 3 = Élevée, 4 = Critique. |

## Sorties

| Chemin de contexte | Type | Contenu |
| --- | --- | --- |
| `Triage.RecuLe` | date | Date de création de l'incident, relevée au début du triage. |
| `Triage.Decision` | string | `Escalade` ou `Traitement standard` selon la branche empruntée. |

## Déroulé des tâches

| # | Tâche | Type | Détail |
| --- | --- | --- | --- |
| 0 | Départ | start | Point d'entrée du playbook. |
| 1 | Triage | titre | Séparateur visuel, sans action. |
| 2 | Enregistrer la date de réception | script `Set` | Écrit `${incident.created}` dans `Triage.RecuLe`. |
| 3 | Sévérité au-dessus du seuil ? | condition | `incident.severity >= inputs.SeuilSeverite`. Branche `yes` vers 4, sinon vers 6. |
| 4 | Décision - escalade | script `Set` | `Triage.Decision = Escalade`. |
| 5 | Journaliser l'escalade | script `Print` | Message d'escalade dans le War Room. |
| 6 | Décision - traitement standard | script `Set` | `Triage.Decision = Traitement standard`. |
| 7 | Journaliser le traitement standard | script `Print` | Message standard dans le War Room. |
| 8 | Fin du triage | titre | Convergence des deux branches. |

## Importer le playbook

Deux options :

- Interface : Playbooks > Upload, puis sélectionner `playbooks/prise-en-main-xsoar.yml`.
- Ligne de commande avec `demisto-sdk` :

  ```
  demisto-sdk upload -i playbooks/prise-en-main-xsoar.yml
  ```

## Tester

1. Créer un incident de test avec une sévérité `Élevée` (3) ou plus.
2. Lancer le playbook sur cet incident (bouton Run ou en le rattachant au type d'incident).
3. Vérifier la branche empruntée dans l'onglet Work Plan, la valeur de `Triage.Decision` dans le
   contexte, et le message dans le War Room.
4. Rejouer avec une sévérité `Faible` (1) pour valider l'autre branche.

## Pour aller plus loin

- Brancher un vrai enrichissement (réputation IP/URL) à la place du script `Set`, puis décider sur
  le `DBotScore` renvoyé.
- Remplacer les messages `Print` par `setIncident` pour poser un tag ou changer un champ, et par
  `closeInvestigation` pour clôturer les incidents à faible enjeu.
- Ajouter une tâche manuelle (data collection) pour demander une validation analyste avant l'escalade.
