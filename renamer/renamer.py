from typing import Optional, List
from dataclasses import dataclass
import os
import re
import argparse
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


@dataclass
class RenameConfig:
    """
    Représente la configuration du processus de renommage.
    """

    path: str
    pattern: Optional[str] = None
    dry_run: bool = True
    replace: Optional[str] = None  # format attendu : 'ancien:nouveau'
    exclude: Optional[List[str]] = None
    confirm: bool = False
    sort_mode: str = "alpha"  # 'alpha' ou 'date'
    index_format: str = "{:02}"  # ex: '{:03}' pour index à 3 chiffres
    start_index: int = 0


class FileRenamer:
    """Classe principale pour renommer des fichiers avec différentes fonctionnalités."""

    def __init__(self, config: RenameConfig):
        self.config = config
        self.path = config.path
        self.dry_run = config.dry_run
        self.pattern = config.pattern
        self.replace = self._parse_replace(config.replace)
        self.exclude = config.exclude or []
        self.confirm = config.confirm
        self.sort_mode = config.sort_mode
        self.index_format = config.index_format
        self.files = []

    def _parse_replace(self, replace_str):
        """Transforme 'ancien:nouveau' en tuple ('ancien', 'nouveau')."""
        if replace_str and ':' in replace_str:
            return tuple(replace_str.split(':', 1))
        return None

    def _list_files(self):
        """Liste les fichiers du dossier, triés selon la méthode choisie."""
        files = [f for f in os.listdir(self.path)
                 if os.path.isfile(os.path.join(self.path, f))
                 and f not in self.exclude]

        if self.sort_mode == "date":
            files.sort(key=lambda f: os.path.getmtime(
                os.path.join(self.path, f)))
        else:
            files.sort()
        self.files = files

    def _format_name(self, filename, index):
        """Génère le nouveau nom du fichier selon le pattern."""
        name, ext = os.path.splitext(filename)
        new_name = self.pattern or "{name}_{index}"
        new_name = new_name.format(
            name=name,
            date=datetime.now().strftime("%Y%m%d"),
            index=self.index_format.format(index)
        )
        return new_name + ext

    def _apply_replace(self, filename):
        """Applique le remplacement de texte si activé."""
        if not self.replace:
            return filename
        old, new = self.replace
        return filename.replace(old, new)

    def _confirm(self, old, new):
        """Demande confirmation à l'utilisateur avant de renommer."""
        while True:
            choice = input(f"Renommer {old} → {new} ? [y/n] : ").lower()
            if choice in ('y', 'n'):
                return choice == 'y'

    def rename(self):
        """Exécute le processus de renommage des fichiers."""
        self._list_files()
        for idx, filename in enumerate(self.files, 1):
            original_path = os.path.join(self.path, filename)
            new_name = self._format_name(filename, idx)
            new_name = self._apply_replace(new_name)
            new_path = os.path.join(self.path, new_name)

            if original_path == new_path:
                continue

            if self.dry_run:
                print(Fore.YELLOW + f"[DRY-RUN] {filename} → {new_name}")
            else:
                if self.confirm and not self._confirm(filename, new_name):
                    print(Fore.RED + f"Renommage annulé pour : {filename}")
                    continue
                os.rename(original_path, new_path)
                print(Fore.GREEN + f"Renommé : {filename} → {new_name}")


def parse_args():
    """Analyse les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Renommer des fichiers selon un pattern.")
    parser.add_argument(
        "path", help="Dossier contenant les fichiers à renommer")
    parser.add_argument(
        "--pattern", help="Pattern de renommage, ex: 'image_{index}_{date}'")
    parser.add_argument(
        "--replace", help="Remplacement de texte, ex: 'ancien:nouveau'")
    parser.add_argument("--dry-run", action="store_true",
                        help="Afficher les changements sans les appliquer")
    parser.add_argument("--confirm", action="store_true",
                        help="Demander confirmation utilisateur")
    parser.add_argument("--exclude", nargs="+",
                        help="Fichiers à exclure", default=[])
    parser.add_argument("--sort", choices=["alpha", "date"], default="alpha",
                        help="Méthode de tri des fichiers")
    parser.add_argument(
        "--index-format", default="{:02}", help="Format de l'index, ex: '{:03}'")
    return parser.parse_args()


def main():
    """Point d'entrée principal du script."""
    args = parse_args()

    config = RenameConfig(
        path=args.path,
        dry_run=args.dry_run,
        pattern=args.pattern,
        replace=args.replace,
        exclude=args.exclude,
        confirm=args.confirm,
        sort_mode=args.sort,
        index_format=args.index_format
    )

    renamer = FileRenamer(config)
    renamer.rename()


if __name__ == "__main__":
    main()
