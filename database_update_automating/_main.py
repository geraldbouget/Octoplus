
# This Python file uses the following encoding: utf-8
import re
import pandas as pd
from policeUpdate import policeUpdate
import onlineUpdateDate  # noqa
# import checkDepartement
from loadingData import df_source
from connexionMySql import ConnexionBase
from gendarmerieUpdate import gendarmerieUpdate
import dashQueryUpdate
from issues import Issues
from dashIssues import DashIssues
from notifUpdate import Notification
issues = Issues()
notif = Notification()
# issues.issuesReply()


class OctoplusUpdate:
    def __init__(self, mybase):
        self.connexion = ConnexionBase(mybase)

    def check_update(self):
        # comparaison dernière annéee base de données et dernière
        # année présente dans les onglets du dataset online
        r_annee = '''SELECT DISTINCT annee
            FROM pointage
            order by annee DESC LIMIT 1'''
        self.last_update_request = self.connexion.engine.execute(r_annee)

        for d in self.last_update_request:
            self.last_update = int(d[0])
        self.sn = df_source.sheet_names
        self.liste_annees = []
        self.p_annee = re.compile(r'(\d\d\d\d)')

        for services in self.sn:
            s = self.p_annee.search(services)
            if s is not None:
                self.liste_annees.append(int(s.group()))

        if sorted(self.liste_annees)[-1] == self.last_update:
            onlineUpdateDate.OnlineCheck()
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write(f'\r\nla base est à jour à {self.last_update}\r\n')
            notif.notifReply()

        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('La base de données n\'est pas à jour.\r\n'
                               + f'\r\nLes données de l\'année {self.liste_annees[-1]} doivent être intégrées\r\n')

            self.df_police_source = pd.read_excel(
                df_source,
                'Services PN '+str(self.liste_annees[-1]),
                index_col=[0],
                header=[0, 1, 2]).to_csv('data/police_for_update.csv')
            self.df_gendarmerie_source = pd.read_excel(
                df_source,
                'Services GN '+str(self.liste_annees[-1]),
                index_col=[0],
                header=[0, 1]).to_csv('data/gendarmerie_for_update.csv')

            update_police = policeUpdate(self.connexion,
                                         self.liste_annees[-1])
            update_gendarmerie = gendarmerieUpdate(self.connexion,
                                                   self.liste_annees[-1])
            onlineUpdateDate.OnlineCheck()
            # update_police.checkDepartement()
            update_gendarmerie.checkDepartement()
            # update_police.checkDirServ()
            update_gendarmerie.checkService()
            # update_police.checkInfractions()
            update_gendarmerie.checkInfractions()
            # les update dessus vérifient juste si pb de concordance entre base et fichier
            # si pb la classe issues est lancée et le programmé arrêté
            issues.issuesReply()
            update_police.updateDirServ()
            update_police.updatePointage()
            update_gendarmerie.updateService()
            update_gendarmerie.updatePointage()
            update_dash = dashQueryUpdate.DashQueryUpdate()
            notif_dash=DashIssues()
            notif_dash.dashIssuesReply()
            notif.notifReply()


if __name__ == '__main__':
    d = OctoplusUpdate('fictif')
    d.check_update()
