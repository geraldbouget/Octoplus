from issues import Issues
from notifUpdate import Notification
import pandas as pd
from itertools import chain
import time
pd.set_option('display.width', None)
issues = Issues()
notif = Notification()


class policeUpdate:
    def __init__(self, connexion, annee_update):
        # df de base pour checks et MAJ dep/services/directions
        self.annee = annee_update
        self.df_police = pd.read_csv(
            'data/police_for_update.csv',
            index_col=[0],
            header=[0, 1, 2])
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write('Mise à jour des données police pour l\'année '
                           + f'{self.annee}\r\n')

        # renommage colonnes df police et seul entete = services pour
        # check et update infractions
        self.df_police_v2 = pd.read_csv(
            'data/police_for_update.csv',
            index_col=[0],
            header=[2]).reset_index().rename(
            columns={"Libellé index \\ CSP": 'libelle',
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
        # liste des directions uniques présents dans la bd
        self.mybase_du_liste = []
        # liste des services uniques présents dans le fichier source web
        self.su_source_liste = []
        # liste des directions uniques présentes dans le fichier source web
        self.du_source_liste = []
        # liste tuple (departement, direction, service) du fichier source web
        self.dep_du_su_liste = []
        # liste des nouveaux services présents dans le fichier source web
        # et pas dans bd
        self.new_service_liste = []
        # liste des nouvelles directions présentes dans fichier source web
        # et pas dans bd
        self.new_direction_liste = []
        # liste des index et infractions listés dans la base
        self.mybase_libelle_liste = []
        # liste des départments présents dans fichier online et pas dansbase
        self.liste_dep_absents = []

    def checkDepartement(self):
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write('Check cohérence liste départements Police\r\n')

        self.r_dep = 'SELECT DISTINCT numDep from departement'
        self.mybase_dep = self.connect.engine.execute(self.r_dep)
        self.result = self.mybase_dep.fetchall()
        for dep in self.result:
            self.mybase_dep_liste.append(dep[0])
        for i in range(1, len(self.df_police.columns)):
            if self.df_police.columns[i][0] not in self.source_liste_dep:
                self.source_liste_dep.append(self.df_police.columns[i][0])
        # on ch ce qui est dans source liste et pas dans base list
        for ele in list(set(self.source_liste_dep).difference(set(self.mybase_dep_liste))):  # noqa
            self.liste_dep_absents.append(ele)
        if len(self.liste_dep_absents) == 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Table département police à jour.\r\n')

        else:
            issues.liste_erreurs.append('Les départements police suivants ne '
                                        + 'sont pas dans la base de'
                                        + f'de données :\r\n{self.liste_dep_absents}'
                                        + '\r\nIl faut vérifier s\'il s\'agit d\'une erreur'
                                        + 'dans le fichier source ou si la nomencalture INSEE'
                                        + 'des département a subi un changment\r\n')

    def checkDirServ(self):
        self.r_service_unique = '''SELECT DISTINCT nomService from service as s
        WHERE s.idAdm=1'''
        self.r_direction_unique = '''SELECT DISTINCT nomDirection, nomComplet
        from direction as d WHERE d.idAdm=1'''
        # création liste unique service
        self.mybase_su = self.connect.engine.execute(self.r_service_unique)
        self.result_su = self.mybase_su.fetchall()

        for service in self.result_su:
            self.mybase_su_liste.append(service[0])

        # création liste unique directions
        self.mybase_du = self.connect.engine.execute(self.r_direction_unique)
        self.result_du = self.mybase_du.fetchall()

        for direction in self.result_du:
            self.mybase_du_liste.append(direction)

        # df_maj_police est multi index. Je me sers de l'attribut
        # df.columns pour aller chercher les listes
        # de service et direction (df_maj_police.columns[i][2]
        # correspond à l'index des noms de service)
        for i in range(1, len(self.df_police.columns)):
            # iteration pour avoir liste unique des service
            if self.df_police.columns[i][2] not in self.su_source_liste:
                self.su_source_liste.append(self.df_police.columns[i][2])
            # iteration pour avoir liste unique des directions
            if self.df_police.columns[i][1] not in self.du_source_liste:
                self.du_source_liste.append(self.df_police.columns[i][1])
            # iteration pour avoir liste des tuples(dep-direction-service)
            self.dep_du_su_liste.append(self.df_police.columns[i])
        # pour vérifier qu'il n'y a pas de nouvelle direction,
        # j'itère à la fois dans nomDirection et nomComplet de la base mysql
        for ele in list(set(self.su_source_liste).difference(set(self.mybase_su_liste))):  # noqa
            self.new_service_liste.append(ele)
        # liste chainee direction de la base de données
        self.mybase_dir_chain = list(chain.from_iterable(self.mybase_du_liste))
        # lister les différences entre liste base de données et liste source
        # on regarde ce qui est dans source et pas dans base
        for ele1 in list(set(self.du_source_liste).difference(set(self.mybase_dir_chain))):  # noqa
            self.new_direction_liste.append(ele1)
        # check si doublon dans tuple (dep, direction, service)
        for i in self.dep_du_su_liste:
            if self.dep_du_su_liste.count(i) > 1:
                issues.liste_erreurs.append('Problèmes doublons tuples  police :'
                                            + f'{i}')  # fin du programmes

    def updateDirServ(self):
        if len(self.new_direction_liste) > 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Mise à jour de la table direction'
                               + '\r\nNouvelles lignes insérées dans la base: \r\n')

            for new_dir in self.new_direction_liste:
                with open('maj_octoplus.txt', 'a') as log_file:
                    log_file.write('\r\n nouvelle direction insérée: ' + str(new_dir)+'\r\n')

                sql = '''INSERT INTO direction (nomDirection, idAdm)
                VALUES (new_dir,1)'''
                self.connect.engine.execute(sql)
        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('\r\nLa table direction Police est déjà à jour\r\n')

        if len(self.new_service_liste) > 0:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('Mise à jour de la table Service'
                               + '\r\nNouvelles lignes insérées dans la base: \r\n')

            for i in range(len(self.dep_du_su_liste)):
                # pour chaque element du tuple, gérer celui
                # où il y a new service
                if self.dep_du_su_liste[i][2] in self.new_service_liste:
                    r_get_dir = '''
                    SELECT d.idDirection, d.nomComplet, d.nomDirection
                    FROM direction AS d
                    JOIN service as s ON s.idDirection=d.idDirection
                    WHERE d.nomDirection=%s or d.nomComplet=%s
                    '''
                    # étape pour requeter les noms de direction qui peuvent
                    # se trouver soir dans la colonne nomDirection
                    # soit dans la colonne nomComplet
                    data = (self.dep_du_su_liste[i][1],
                            self.dep_du_su_liste[i][1])
                    result = self.connect.engine.execute(r_get_dir, data)
                    # je récupère l'id direction de la direction du loop
                    id_dir = result.fetchone()[0]

                    r_insert = '''
                        INSERT INTO service(nomService,numDep,
                        idDirection,idAdm)
                        VALUES (%s,%s,%s,%s)'''
                    val = (self.dep_du_su_liste[i][2],
                           str(self.dep_du_su_liste[i][0]), id_dir, 1)
                    self.connect.engine.execute(r_insert, val)
                    with open('maj_octoplus.txt', 'a') as log_file:
                        log_file.write(f'{val}\r\n')

        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('La table service police est déjà à jour\r\n')

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
            [self.df_police_v2[['codeIndex', 'libelle']],
             self.df_mybase_libelle[['codeIndex',
                                     'libelle']]]).drop_duplicates(keep=False)
        if len(self.df_check_identique) > 0:
            issues.liste_erreurs.append('Il y a un problème de concordances'
                                        + 'sur les lignes suivantes index/libelle : \r\n'
                                        + f'{self.df_check_identique}\r\n')
        else:
            with open('maj_octoplus.txt', 'a') as log_file:
                log_file.write('La concordance index/libelle entre le '
                               + 'fichier source et la base de données Police est bonne\r\n')

    def updatePointage(self):
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write("Mise à jour de la table 'pointage Police'.\r\n")

        # on restructure df police en mode 'stack' pour avoir
        # nbreInfraction dans une seule colonne
        # on définit nouvel index qui ne sera pas restructurer
        self.df_police_stack = self.df_police_v2.set_index(
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
        self.df_merge_service = self.df_police_stack.merge(
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
        end = time.time()
        with open('maj_octoplus.txt', 'a') as log_file:
            log_file.write(
                f'nombre de lignes insérées dans la table pointage :{len(self.df_toInsert)}\r\n')
