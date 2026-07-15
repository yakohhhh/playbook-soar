#!/usr/bin/env python3
"""Valide les playbooks du dossier playbooks/ contre le schema officiel du format
playbook fourni par demisto-sdk, sans exiger la structure d'un depot content.

Usage (depuis la racine du depot, avec un venv ou demisto-sdk est installe) :
    python validate-playbooks.py
    python validate-playbooks.py playbooks/cloture-faux-positifs.yml   # un seul fichier
"""
import sys
import glob
import logging
import pathlib

import demisto_sdk
from pykwalify.core import Core

logging.getLogger("pykwalify").setLevel(logging.CRITICAL)

SCHEMA = pathlib.Path(demisto_sdk.__file__).parent / "commands/common/schemas/playbook.yml"


def valider(chemin):
    core = Core(source_file=chemin, schema_files=[str(SCHEMA)])
    try:
        core.validate(raise_exception=True)
        print(f"OK    {chemin}")
        return True
    except Exception as exc:
        print(f"ECHEC {chemin}")
        for ligne in str(exc).splitlines():
            if ligne.strip().startswith("-"):
                print(f"        {ligne.strip()}")
        return False


def main():
    fichiers = sys.argv[1:] or sorted(glob.glob("playbooks/*.yml"))
    if not fichiers:
        print("Aucun playbook trouve dans playbooks/.")
        return 1
    resultats = [valider(f) for f in fichiers]
    ok = sum(resultats)
    print(f"\n{ok}/{len(resultats)} playbook(s) conforme(s) au schema.")
    return 0 if ok == len(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
