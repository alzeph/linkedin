from dataclasses import dataclass
import os
import inquirer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import requests
import hashlib

console = Console()


@dataclass
class EncryptConfig:
    file_path: str
    password: str
    confirm: bool = False
    output_path: Optional[str] = None


class FileEncryptor:
    HEADER_SIGNATURE = b"YJCHGCM1"
    HEADER_LEN = len(HEADER_SIGNATURE)
    IV_LEN = 12  # nonce size for AES-GCM

    def __init__(self, config: EncryptConfig):
        self.config = config

    def run(self) -> None:
        action = self._show_menu()
        if action == "encrypt":
            self._handle_encrypt()
        elif action == "decrypt":
            self._handle_decrypt()
        else:
            console.print("[red]Fermeture du programme.[/red]")

    def _show_menu(self) -> str:
        questions = [
            inquirer.List(
                "action",
                message="Que souhaitez-vous faire ?",
                choices=[
                    ("🔐 Chiffrer un fichier", "encrypt"),
                    ("🔓 Déchiffrer un fichier", "decrypt"),
                    ("❌ Quitter", "quit"),
                ],
            )
        ]
        answers = inquirer.prompt(questions)
        return answers.get("action", "quit")

    def _is_already_encrypted(self, path: str) -> bool:
        try:
            with open(path, "rb") as f:
                header = f.read(self.HEADER_LEN)
                return header == self.HEADER_SIGNATURE
        except FileNotFoundError:
            console.print(f"[red]Fichier introuvable : {path}[/red]")
            return False

    def _handle_encrypt(self) -> None:
        path = self._ask_file_path()
        if not path or not os.path.isfile(path):
            console.print(f"[red]Fichier non trouvé : {path}[/red]")
            return

        if self._is_already_encrypted(path):
            console.print("[yellow]Ce fichier semble déjà chiffré. Impossible de chiffrer à nouveau.[/yellow]")
            return

        password = self._ask_password_and_verify()

        output_path = f"{path}.yjch"
        if os.path.exists(output_path):
            if self._confirm(f"Le fichier {output_path} existe. Écraser ?") is False:
                console.print("[yellow]Opération annulée par l'utilisateur.[/yellow]")
                return

        key = self._derive_key(password)
        iv = os.urandom(self.IV_LEN)
        aesgcm = AESGCM(key)

        file_size = os.path.getsize(path)
        chunk_size = 64 * 1024

        with open(path, "rb") as fin:
            data = fin.read()

        # Chiffrement complet en mémoire (AES-GCM nécessite tout d'un coup)
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Chiffrement en cours...", total=file_size)
            # Simuler progression (car tout en mémoire)
            encrypted = aesgcm.encrypt(iv, data, None)
            progress.update(task, advance=file_size)

        with open(output_path, "wb") as fout:
            fout.write(self.HEADER_SIGNATURE)
            fout.write(iv)
            fout.write(encrypted)  # ciphertext + tag à la fin automatiquement

        console.print(f"[bold green]Fichier chiffré créé :[/bold green] {output_path}")

        if self._confirm(f"Supprimer le fichier original {path} ?"):
            os.remove(path)
            console.print("[bold red]Fichier original supprimé.[/bold red]")

    def _handle_decrypt(self) -> None:
        path = self._ask_file_path()
        if not path or not os.path.isfile(path):
            console.print(f"[red]Fichier non trouvé : {path}[/red]")
            return

        if not self._is_already_encrypted(path):
            console.print("[yellow]Ce fichier ne semble pas être chiffré par ce programme.[/yellow]")
            return

        output_default = path.rsplit(".yjch", 1)[0]
        output_path = self._ask_output_path(output_default)

        while True:
            password = self._ask_password()
            if not password:
                console.print("[red]Mot de passe vide, réessayez.[/red]")
                continue
            key = self._derive_key(password)

            try:
                with open(path, "rb") as fin:
                    fin.seek(self.HEADER_LEN)
                    iv = fin.read(self.IV_LEN)
                    encrypted_data = fin.read()

                aesgcm = AESGCM(key)

                with Progress(
                    SpinnerColumn(),
                    "[progress.description]{task.description}",
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("[cyan]Déchiffrement en cours...", total=len(encrypted_data))
                    # Déchiffrement complet en mémoire
                    decrypted = aesgcm.decrypt(iv, encrypted_data, None)
                    progress.update(task, advance=len(encrypted_data))

                with open(output_path, "wb") as fout:
                    fout.write(decrypted)
                break  # succès => sortir boucle

            except Exception:
                console.print("[red]Mot de passe incorrect ou fichier corrompu.[/red]")
                if not self._confirm("Réessayer avec un autre mot de passe ?"):
                    console.print("[yellow]Déchiffrement annulé.[/yellow]")
                    return

        console.print(f"[bold green]Fichier déchiffré créé :[/bold green] {output_path}")

        if self._confirm(f"Supprimer le fichier chiffré {path} ?"):
            os.remove(path)
            console.print("[bold red]Fichier chiffré supprimé.[/bold red]")

    def _ask_file_path(self) -> Optional[str]:
        question = [inquirer.Text("file_path", message="Chemin du fichier")]
        answer = inquirer.prompt(question)
        return answer.get("file_path")

    def _ask_password(self) -> str:
        question = [inquirer.Password("password", message="Mot de passe")]
        answer = inquirer.prompt(question)
        return answer.get("password")

    def _ask_password_and_verify(self) -> str:
        while True:
            password = self._ask_password()
            if not password:
                console.print("[red]Mot de passe vide, réessayez.[/red]")
                continue

            if self._check_password_pwned(password):
                console.print("[bold red]Attention : Ce mot de passe a été compromis ![/bold red]")
                if self._confirm("Voulez-vous utiliser ce mot de passe quand même ?") is False:
                    continue
            return password

    def _ask_output_path(self, default_path: str) -> str:
        question = [inquirer.Text("output", message="Chemin fichier de sortie", default=default_path)]
        answer = inquirer.prompt(question)
        return answer.get("output", default_path)

    def _confirm(self, message: str) -> bool:
        question = [inquirer.Confirm("confirm", message=message, default=False)]
        answer = inquirer.prompt(question)
        return answer.get("confirm", False)

    def _derive_key(self, password: str) -> bytes:
        return hashlib.sha256(password.encode("utf-8")).digest()

    def _check_password_pwned(self, password: str) -> bool:
        sha1_pw = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1_pw[:5], sha1_pw[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                console.print("[red]Erreur API HaveIBeenPwned[/red]")
                return False
            hashes = (line.split(":")[0] for line in response.text.splitlines())
            return suffix in hashes
        except Exception:
            console.print("[red]Erreur de connexion à l'API HaveIBeenPwned[/red]")
            return False


def main() -> None:
    fe = FileEncryptor(EncryptConfig(file_path="", password=""))
    fe.run()


if __name__ == "__main__":
    main()
