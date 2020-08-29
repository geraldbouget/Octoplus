import smtplib
from email.message import EmailMessage
from datetime import datetime


class DashIssues:
    liste_dash_erreurs = []

    def dashIssuesReply(self):
        if len(self.liste_dash_erreurs) != 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Tentative de mise à jour des requêtes dash du :'
                               + datetime.strftime(datetime.now(), '%B %d %Y') + '\r\n'
                               + 'Les erreurs suivants ont été relevées :\r\n')
            for i in self.liste_dash_erreurs:
                with open('maj_octoplus.txt', 'a') as log_file:
                    log_file.write(f'{i}\r\n')
