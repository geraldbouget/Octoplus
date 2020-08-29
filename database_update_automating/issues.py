import smtplib
from email.message import EmailMessage
from datetime import datetime


class Issues:
    liste_erreurs = []

    def issuesReply(self):
        if len(self.liste_erreurs) != 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Tentative de mise à jour du :'
                               + datetime.strftime(datetime.now(), '%B %d %Y') + '\r\n'
                               + 'Les erreurs suivants ont été relevées avant insertion :\r\n')
            for i in self.liste_erreurs:
                with open('maj_octoplus.txt', 'a') as log_file:
                    log_file.write(f'{i}\r\n'
                                   + '\r\n Le programme s\'est terminé mais aucune donnée n\'a '
                                   + 'été insérée dans la base')
            msg = EmailMessage()
            msg["From"] = 'gerald.bouget@sfr.fr'
            msg["Subject"] = "Voici le résumé de la mise à jour de la base"
            msg["To"] = 'gerald.bouget@sfr.fr'
            msg.set_content("Mise à jour de la base de données")
            msg.add_attachment(open("maj_octoplus.txt", "r").read())

            s = smtplib.SMTP('smtp.sfr.fr', 587)
            s.ehlo()
            s.starttls()
            s.send_message(msg)
            s.quit()
            file = open("maj_octoplus.txt", "r+")
            file.truncate(0)
            file.close()
            exit()
