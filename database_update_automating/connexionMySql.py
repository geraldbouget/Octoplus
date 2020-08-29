import logging
logging.basicConfig(filename = 'app.log', level = logging.INFO)
import mysql.connector
from sqlalchemy import create_engine, types
import security
from issues import Issues
issues = Issues()


class ConnexionBase:
    def __init__(self, nombase):
        try:
            self.nombase = nombase
            MYSQL_USER = security.MYSQL_USER
            MYSQL_PASSWORD = security.MYSQL_PASSWORD
            MYSQL_HOST_IP = '127.0.0.1'
            MYSQL_DATABASE = self.nombase
            self.engine = create_engine('mysql+mysqlconnector://' + MYSQL_USER +
                                        ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST_IP
                                        + '/' + MYSQL_DATABASE)
        except Exception as e:
            logging.exception(str(e))
            issues.liste_erreurs.append('La connexion à la base de données n\'a pu se faire. Voir fichier log')
            issues.issuesReply()
