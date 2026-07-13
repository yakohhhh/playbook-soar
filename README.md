# playbook-soar

Playbooks Cortex XSOAR versionnés dans ce dépôt. Le contenu SOAR reste au format YAML : on le relit et
on le réimporte d'une instance à l'autre sans repasser par des exports manuels.

Le premier playbook sert de prise en main : il n'utilise que des scripts natifs XSOAR, donc il tourne
sur une instance vierge sans installer d'intégration.

## Contenu

| Playbook | Fichier | Doc |
| --- | --- | --- |
| Prise en main XSOAR - Triage | [playbooks/prise-en-main-xsoar.yml](playbooks/prise-en-main-xsoar.yml) | [docs/prise-en-main-xsoar.md](docs/prise-en-main-xsoar.md) |
| Notification et escalade | [playbooks/notification-et-escalade.yml](playbooks/notification-et-escalade.yml) | [docs/notification-et-escalade.md](docs/notification-et-escalade.md) |

## Organisation

```
playbook-soar/
├── playbooks/   # les playbooks au format YAML XSOAR
├── docs/        # une doc par playbook (contexte, entrées/sorties, déroulé)
└── README.md
```

## Importer un playbook dans XSOAR

- Interface : Playbooks > Upload, puis choisir le fichier `.yml`.
- `demisto-sdk` :

  ```
  demisto-sdk upload -i playbooks/prise-en-main-xsoar.yml
  ```

## Conventions

- Un playbook = un fichier YAML dans `playbooks/`, plus une page correspondante dans `docs/`.
- On garde les identifiants de tâches (`taskid`) stables pour que les diffs restent lisibles.
- On privilégie les scripts natifs quand c'est possible, pour limiter les dépendances au moment de
  l'import.

## Prérequis pour manipuler le contenu en local

- Cortex XSOAR 6.5 ou plus récent côté serveur.
- `demisto-sdk` si on veut valider ou pousser depuis la ligne de commande (`pip install demisto-sdk`).
