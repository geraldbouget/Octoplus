
# from itertools import chain
from notifUpdate import Notification
from issues import Issues
import time
import pandas as pd
pd.set_option('display.width', None)
issues = Issues()
notif = Notification()


class gendarmerieUpdate:
    def __init__(self, connexion, annee_update):
        self.annee = annee_update
        # df de base pour checks et MAJ dep/services/directions
        self.df_gendarmerie = pd.read_csv(
            'data/gendarmerie_for_update.csv',
            index_col=[0],
            header=[0, 1])

        # renommage colonnes df police et seul entete = services pour
        # check et update infractions
        self.df_gendarmerie_v2 = pd.read_csv(
            'data/gendarmerie_for_update.csv',
            index_col=[0],
            header=[1]).reset_index().rename(
            columns={"Libellé index \\ CGD": 'libelle',
                     'Code index': 'codeIndex'},
            level=0)

        # connexion à mysql database - argument renvoie à main
        # qui renvoie lui-même à connexionMySql
        self.connect = connexion
        # list unique des départements de la base de données
        self.mybase_dep_liste = []
        # liste unique des départements du fichier source internet
        self.source_liste_dep = []
        # liste des services uniques présents dans la bd
        self.mybase_su_liste = []
        # liste des services uniques présents dans le fichier source web
        self.su_source_liste = []
        # liste tuple (departement, service)
        # du fichier source web
        self.dep_su_liste = []
        # liste des nouveaux services présents dans le fichier source web
        # et pas dans bd
        self.new_service_liste = []
        # liste des index et infractions listés dans la base
        self.mybase_libelle_liste = []
        # liste des départments présents dans fichier online
        # et pas dansbase
        self.liste_dep_absents = []

    def checkDepartement(self):
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write("Check cohérence liste départements Gendarmerie.\r\n")

        self.r_dep = 'SELECT DISTINCT numDep from departement'
        self.mybase_dep = self.connect.engine.execute(self.r_dep)
        self.result = self.mybase_dep.fetchall()
        for dep in self.result:
            self.mybase_dep_liste.append(dep[0])

        for i in range(1, len(self.df_gendarmerie.columns)):
            if self.df_gendarmerie.columns[i][0] not in self.source_liste_dep:
                self.source_liste_dep.append(self.df_gendarmerie.columns[i][0])
        # on ch ce qui est dans source liste et pas dans base list
        for ele in list(set(self.source_liste_dep).difference(set(self.mybase_dep_liste))):  # noqa
            self.liste_dep_absents.append(ele)
        if len(self.liste_dep_absents) == 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Table département Gendarmerie à jour\r\n')

        else:
            issues.liste_erreurs.append('Les départements gendarmerie suivants ne '
                                        + 'sont pas dans la base de'
                                        + f'de données :\r\n{self.liste_dep_absents}'
                                        + '\r\nIl faut vérifier s\'il s\'agit d\'une erreur'
                                        + 'dans le fichier source ou si la nomencalture INSEE'
                                        + 'des département a subi un changment\r\n')

    def checkService(self):
        # requete services uniques gendarmerie
        self.r_service_unique = '''SELECT DISTINCT nomService from service as s
        WHERE s.idAdm=2'''
        # création liste unique service
        self.mybase_su = self.connect.engine.execute(self.r_service_unique)
        self.result_su = self.mybase_su.fetchall()
        for service in self.result_su:
            self.mybase_su_liste.append(service[0])

        for i in range(1, len(self.df_gendarmerie.columns)):
            # iteration pour avoir liste unique des service
            if self.df_gendarmerie.columns[i][1] not in self.su_source_liste:
                self.su_source_liste.append(self.df_gendarmerie.columns[i][1])
        # iteration pour avoir liste des tuples(dep-service)
            self.dep_su_liste.append(self.df_gendarmerie.columns[i])

        # j'itère à la fois dans nomDirection et nomComplet de la base mysql
        for ele in list(set(self.su_source_liste).difference(set(self.mybase_su_liste))):  # noqa
            self.new_service_liste.append(ele)

        # check si doublon dans tuple (dep, direction, service)
        for j in self.dep_su_liste:
            if self.dep_su_liste.count(j) > 1:
                issues.liste_erreurs.append('Problèmes doublons service/dep dans gendarmerie :'
                                            + f'{i}')

    def updateService(self):
        if len(self.new_service_liste) > 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Mise à jour de la table Service gendarmerie'
                               + '\r\nNouvelles lignes insérées dans la base: \r\n')
            for i in range(len(self.dep_su_liste)):
                # pour chaque element du tuple, gérer celui
                # où il y a new service
                if self.dep_su_liste[i][1] in self.new_service_liste:
                    r_insert = '''
                        INSERT INTO service(nomService,numDep,
                        idDirection,idAdm)
                        VALUES (%s,%s,%s,%s)'''
                    val = (self.dep_su_liste[i][1],
                           # None pour avoir une valeur nulle dans mysql
                           # car pas de direction dans gendarmerie
                           str(self.dep_su_liste[i][0]), None, 2)
                    self.connect.engine.execute(r_insert, val)
                    with open('maj_octoplus.txt', 'a') as log_file:
                        log_file.write(f'{val}\r\n')
        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('La table service gendarmerie est déjà à jour\r\n')

    def checkInfractions(self):
        # check liste infraction et code index correcte :
        # récupération df clean codeindex/libelle
        self.r_mybase_libelle = '''SELECT codeIndex, libelle FROM infraction'''
        # query = self.connect.engine.execute(r_mybase_libelle)
        # result = query.fetchall()
        # for r in result:
        #     self.mybase_libelle_liste.append(r)
        self.df_mybase_libelle = pd.read_sql(self.r_mybase_libelle,
                                             self.connect.engine)

        self.df_check_identique = pd.concat(
            [self.df_gendarmerie_v2[['codeIndex', 'libelle']],
             self.df_mybase_libelle[['codeIndex',
                                     'libelle']]]).drop_duplicates(keep=False)

        if len(self.df_check_identique) > 0:
            issues.liste_erreurs.append('Il y a un problème de concordances '
                                        + 'sur les lignes suivantes index/libelle : \r\n'
                                        + f'{self.df_check_identique}\r\n')
        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('La concordance index/libelle entre le '
                               + 'fichier source et la base de données gendarmerie est bonne\r\n')

    def updatePointage(self):
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write("Mise à jour de la table 'pointage' gendarmerie\r\n")

        # on restructure df police en mode 'stack' pour avoir
        # nbreInfraction dans une seule colonne
        # on définit nouvel index qui ne sera pas restructurer
        self.df_gendarmerie_stack = self.df_gendarmerie_v2.set_index(
            ['codeIndex', 'libelle']).stack().reset_index().rename(
                columns={'level_2': 'nomService',
                         0: 'nbreInfractions'})
        # requête pour récupérer idservce et nom service
        self.r_service = '''
        SELECT DISTINCT idService,
        nomService FROM service'''
        # df en vue d'un merge avec df source restructuré 'stack)'
        self.df_mybase_service = pd.read_sql(self.r_service,
                                             self.connect.engine)
        # merge sur idservice afin de liers les new Services
        # à l'idservice correspondant
        self.df_merge_service = self.df_gendarmerie_stack.merge(
            self.df_mybase_service,
            how='left',
            on='nomService')
        self.df_merge_service['annee'] = int(self.annee)
        self.df_toInsert = self.df_merge_service[['annee',
                                                  'nbreInfractions',
                                                  'idService',
                                                  'codeIndex']]
        self.df_toInsert.to_sql('pointage',
                                index=False,
                                con=self.connect.engine,
                                if_exists='append')
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write(f'nombre de lignes insérées: {len(self.df_toInsert)}\r\n')
