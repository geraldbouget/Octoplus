import smtplib
from email.message import EmailMessage
from datetime import datetime


class Notification:
    liste_maj = []

    def notifReply(self):

        msg = EmailMessage()
        msg["From"] = 'gerald.bouget@sfr.fr'
        msg["Subject"] = "Voici le résumé de la mise à jour de la base"
        msg["To"] = 'gerald.bouget@sfr.fr'
        msg.set_content("This is the message body")
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
