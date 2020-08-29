from connexionMySql import ConnexionBase
import logging
from dashIssues import DashIssues
logging.basicConfig(filename = 'app.log', level = logging.INFO)


class DashQueryUpdate:
    def __init__(self):

        self.connexion = ConnexionBase('fictif')
        self.connection = self.connexion.engine.raw_connection()

        try:
            self.dash_drop_table = 'TRUNCATE query_dash_main'
            self.r_dash_query = '''
            INSERT INTO query_dash_main
            SELECT dp.numDep, dp.nomDep,ic.nomIndicLight, i.libelle, annee, sum(p.nbreInfractions) AS cumulInfraction,
        	d.nbrePopulation,d.densite, SUM((nbreInfractions/nbrePopulation)*1000) AS InfPour1000
        	FROM pointage AS p
        	JOIN service AS s ON p.idService=s.idService
        	JOIN infraction as i ON i.codeIndex=p.codeIndex
        	JOIN indicateur as ic ON ic.idIndic=i.idIndic
        	JOIN departement AS dp ON s.numDep=dp.numDep
        	JOIN demographie AS d ON dp.numDep=d.numDep
        	GROUP BY dp.numDep, dp.nomDep, ic.nomIndicLight, i.libelle, annee, d.nbrePopulation, d.densite'''
            self.drop_table = self.connexion.engine.execute(self.dash_drop_table)
            self.dash_call = self.connexion.engine.execute(self.r_dash_query)

        except Exception as e:
            logging.exception(str(e))
            DashIssues.liste_dash_erreurs.append('La mise à jour de la requête query_dash_main n\'a pas pu se faire. Voir fichier log')

        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('\r\nLMise à jour requête query_dash_main ok \r\n')

        try:
            self.dash_drop_table = 'TRUNCATE query_dash_demographie'
            self.r_dash_query = '''
            INSERT INTO query_dash_demographie
            SELECT  age_15,age_15_29,age_20,age_30_44,age_45_59,age_60_74,age_75,anneeRecensement,
            densite,nbreCommunes,nbrePopulation,d.numDep,nomDep,partCom_10000_plus,partCom_200_9999,
            partCom_moins_200,partPop_10000_plus,partPop_200_9999,partPop_moins_200
            FROM demographie AS dem
            JOIN departement AS d
            ON d.numDep=dem.numDep
            '''
            self.drop_table = self.connexion.engine.execute(self.dash_drop_table)
            self.dash_call = self.connexion.engine.execute(self.r_dash_query)
        except Exception as e:
            logging.exception(str(e))
            DashIssues.liste_dash_erreurs.append('La mise à jour de la requête query_dash_demographie n\'a pas pu se faire. Voir fichier log')

        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('\r\nLMise à jour requête query_dash_demographie ok \r\n')

        self.connection.close()


#d = dashQueryUpdate()
