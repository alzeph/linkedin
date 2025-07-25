from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from imapclient import IMAPClient
from InquirerPy import inquirer
import email
from email.header import decode_header
from dateutil.parser import parse as parse_date


@dataclass
class MailCleanConfig:
    server: str
    email: str
    password: str
    dry_run: bool = True
    confirm: bool = False
    days_limit: int = 90
    use_spam_filter: bool = True


class MailCleaner:
    def __init__(self, config: MailCleanConfig):
        self.config = config
        self.client = None

    def connect(self):
        print(f"Connexion à {self.config.server}...")
        self.client = IMAPClient(self.config.server, ssl=True)
        self.client.login(self.config.email, self.config.password)
        print("Connecté avec succès.")

    def search_mails(self):
        self.client.select_folder('INBOX')
        date_cutoff = (datetime.now() -
                       timedelta(days=self.config.days_limit)).date()
        criteria = ['BEFORE', date_cutoff.strftime('%d-%b-%Y')]
        if self.config.use_spam_filter:
            #on ignore les spams
            pass
        messages = self.client.search(criteria)
        return messages

    def fetch_mail_subject(self, uid):
        raw = self.client.fetch([uid], ['RFC822'])[uid][b'RFC822']
        msg = email.message_from_bytes(raw)
        subject, encoding = decode_header(msg.get('Subject'))[0]
        if isinstance(subject, bytes):
            try:
                subject = subject.decode(encoding or 'utf-8')
            except:
                subject = subject.decode('utf-8', errors='ignore')
        return subject

    def simulate(self, messages):
        print(f"[Simulation] {len(messages)} mails correspondent aux règles :")
        for uid in messages[:10]:
            subject = self.fetch_mail_subject(uid)
            print(f"- UID {uid}: {subject}")
        if len(messages) > 10:
            print(f"... et {len(messages)-10} autres mails.")

    def confirm_action(self, uid):
        if not self.config.confirm:
            return True
        subject = self.fetch_mail_subject(uid)
        answer = inquirer.confirm(
            message=f"Supprimer mail UID {uid} sujet: '{subject}' ?", default=False).execute()
        return answer

    def delete_mails(self, messages):
        to_delete = []
        for uid in messages:
            if self.confirm_action(uid):
                to_delete.append(uid)
        if self.config.dry_run:
            print(f"[Dry-run] {len(to_delete)} mails seraient supprimés.")
        else:
            self.client.delete_messages(to_delete)
            self.client.expunge()
            print(f"{len(to_delete)} mails supprimés.")

    def summarize(self, messages):
        print(f"Résumé des {len(messages)} mails ciblés (10 premiers) :")
        for uid in messages[:10]:
            subject = self.fetch_mail_subject(uid)
            print(f"- {subject}")

    def get_archive_folder(self):
        server = self.config.server.lower()
        if "gmail" in server:
            return "[Gmail]/All Mail"
        elif "outlook" in server or "office365" in server:
            return "Archive"
        elif "yahoo" in server:
            return "Archive"
        else:
            return "Archive"

    def archive_mails(self, messages):
        archive_folder = self.get_archive_folder()
        self.client.select_folder('INBOX')

        if self.config.dry_run:
            print(
                f"[Dry-run] {len(messages)} mails seraient déplacés vers '{archive_folder}'.")
            return

        folders = [folder_info[-1]
                   for folder_info in self.client.list_folders()]
        if archive_folder not in folders:
            try:
                self.client.create_folder(archive_folder)
            except Exception as e:
                print(
                    f"Erreur lors de la création du dossier '{archive_folder}': {e}")
                return

        to_move = []
        for uid in messages:
            if self.config.confirm:
                subject = self.fetch_mail_subject(uid)
                answer = inquirer.confirm(
                    message=f"Archiver mail UID {uid} sujet: '{subject}' ?", default=False).execute()
                if not answer:
                    continue
            to_move.append(uid)

        if to_move:
            self.client.move(to_move, archive_folder)
            print(f"{len(to_move)} mails déplacés vers '{archive_folder}'.")
        else:
            print("Aucun mail archivé.")

    def main_menu(self):
        while True:
            action = inquirer.select(
                message="Choisissez une action :",
                choices=[
                    "Lister mails",
                    "Archiver mails",
                    "Supprimer mails",
                    "Résumé mails",
                    "Quitter"
                ],
            ).execute()

            messages = self.search_mails()

            if action == "Lister mails":
                self.simulate(messages)
            elif action == "Supprimer mails":
                self.delete_mails(messages)
            elif action == "Résumé mails":
                self.summarize(messages)
            elif action == "Archiver mails":
                self.archive_mails(messages)
            elif action == "Quitter":
                print("Au revoir !")
                break


def main():
    server_map = {
        'gmail': 'imap.gmail.com',
        'outlook': 'outlook.office365.com',
        'yahoo': 'imap.mail.yahoo.com'
    }

    provider = inquirer.select(
        message="Type de compte email:",
        choices=['gmail', 'outlook', 'yahoo', 'autre'],
    ).execute()

    if provider in server_map:
        server = server_map[provider]
    else:
        server = inquirer.text(message="Entrez le serveur IMAP:").execute()

    email_user = inquirer.text(message="Email:").execute()
    password_user = inquirer.secret(
        message="Mot de passe d'application:").execute()

    dry_run = inquirer.confirm(
        message="Mode simulation (dry-run) ?", default=True).execute()
    confirm = inquirer.confirm(
        message="Confirmation ligne par ligne ?", default=False).execute()
    days_limit = int(inquirer.text(
        message="Nombre de jours limite (ex: 30):", default="30").execute())

    config = MailCleanConfig(
        server=server,
        email=email_user,
        password=password_user,
        dry_run=dry_run,
        confirm=confirm,
        days_limit=days_limit,
        use_spam_filter=True
    )

    cleaner = MailCleaner(config)
    try:
        cleaner.connect()
        cleaner.main_menu()
    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    main()
