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
| Clôture automatique des faux positifs connus | [playbooks/cloture-faux-positifs.yml](playbooks/cloture-faux-positifs.yml) | [docs/cloture-faux-positifs.md](docs/cloture-faux-positifs.md) |
| Enrichissement d'indicateurs (générique) | [playbooks/enrichissement-indicateurs.yml](playbooks/enrichissement-indicateurs.yml) | [docs/enrichissement-indicateurs.md](docs/enrichissement-indicateurs.md) |
| Enrichissement de vulnérabilité (CVE) | [playbooks/enrichissement-cve.yml](playbooks/enrichissement-cve.yml) | [docs/enrichissement-cve.md](docs/enrichissement-cve.md) |
| Triage d'email de phishing | [playbooks/triage-phishing.yml](playbooks/triage-phishing.yml) | [docs/triage-phishing.md](docs/triage-phishing.md) |
| Blocage d'IP malveillante | [playbooks/blocage-ip.yml](playbooks/blocage-ip.yml) | [docs/blocage-ip.md](docs/blocage-ip.md) |

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

## Valider les playbooks

`demisto-sdk validate` attend l'arborescence complète du dépôt "content" (un dossier `Packs/` à la
racine) et échoue ici avec `No such file or directory: 'Packs'`. Ce dépôt garde une structure simple,
donc on valide directement contre le schéma de playbook fourni par demisto-sdk :

```
python validate-playbooks.py                       # tous les playbooks de playbooks/
python validate-playbooks.py playbooks/xxx.yml     # un seul fichier
```

Le script a besoin d'un environnement où `demisto-sdk` est installé (il en réutilise le schéma et la
dépendance `pykwalify`). Il vérifie la conformité au format, pas le comportement à l'exécution.
