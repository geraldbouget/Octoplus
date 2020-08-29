import pandas as pd
import warnings
import re
from geopandas import GeoSeries
import geopandas as gpd

import mysql.connector
from sqlalchemy import create_engine, types


class Map1:

    def __init__(self):
        self.MYSQL_USER = 'heroku-user'
        self.MYSQL_PASSWORD = 'atb225-R'
        self.MYSQL_HOST_IP = 'octoplus-db.cmzfn1ssngra.eu-west-3.rds.amazonaws.com'
        self.MYSQL_DATABASE = 'octoplus'
        self.engine = create_engine('mysql+mysqlconnector://' + self.MYSQL_USER +
                                    ':' + self.MYSQL_PASSWORD + '@' + self.MYSQL_HOST_IP
                                    + '/' + self.MYSQL_DATABASE,
                                    connect_args={'auth_plugin': 'mysql_native_password',
                                                  'ssl_ca': 'rds-ca-2019-root.pem'})
        self.conn = self.engine.connect()

        self.df1 = pd.read_sql('SELECT * FROM query_dash_main', self.engine)
        self.df_demo_temp = pd.read_sql('SELECT * FROM query_dash_demographie', self.engine)
        self.df_demo = self.df_demo_temp.rename(
            columns={
                'nomDep': 'nom département',
                'nbreCommunes': 'Nombre de communes',
                'partCom_moins_200': 'Part des com. de moins de 200 hab. (en %)',
                'partPop_moins_200': 'Part de la pop. vivant dans des com. de moins de 200 hab. (en %)',
                'partCom_200_9999': 'Part des com. de 200 à 9999 hab. (en %)',
                'partPop_200_9999': 'Part de la pop. vivant dans des com. de 200 à 9999 hab. (en %)',
                'partCom_10000_plus': 'Part des com. de 10000 hab. ou plus (en %)',
                'partPop_10000_plus': 'Part de la pop. vivant dans des com. de 10000 hab. ou plus (en %)',
                'age_15': 'Part des moins de 15 ans 2016',
                'age_15_29': 'Part des 15-29 ans (en %)',
                'age_30_44': 'Part des 30-44 ans (en %)',
                'age_45_59': 'Part des 45-59 ans (en %)',
                'age_60_74': 'Part des 60-74 ans (en %)',
                'age_75': 'Part des 75 ans et plus (en %)',
                'age_20': 'Part des moins de 20 ans (en %)'
            }
        )

        self.df_paris = pd.read_sql('SELECT * FROM query_dash_paris', self.engine)
        self.conn.close()

    def parisReformat(self):
        warnings.filterwarnings("ignore")
        # définition d'un 1er pattern
        self.a = re.compile(r'(\dEME)|(PARIS CENTRE)|(01ER)')
        # Filtrer la table pour n'avoir que lignes comportant
        # numéro d'arrondissement
        self.df_paris_filter = self.df_paris[(
            self.df_paris.nomDirection == 'DSPAP') & (
            self.df_paris.nomService.str.contains(
                self.a))]
        # retrait de tout ce qui n'est pas un numéro d'arrondissment
        self.df_paris_filter.nomService = self.df_paris_filter.nomService.apply(
            lambda x: re.sub(
                r'(DTSP75\s)|(\sARRONDISSEMENT)|(EME)|(ER)', '', x))
        # renommer cells en '56' pour indiquer que correspond à 56
        self.df_paris_filter.nomService = self.df_paris_filter.nomService.apply(
            lambda x: '5-6' if x == '05 ET 06S' else x)
        self.p = re.compile(r'^0\d')
        # suppression 0 devant 04, 03...

        # df_paris_filter.nomService=df_paris_filter.nomService.apply(lambda x:re.sub(r'0', '', x))
        self.df_paris_filter.nomService = self.df_paris_filter.nomService.apply(
            lambda x: re.sub(
                r'0', '', x) if self.p.match(x)
            else x)

        # renommage colonne nomService en c_ar
        self.df_paris_filter.rename(columns={'nomService': 'c_ar'}, inplace=True)

        self.df_paris_filter.c_ar.replace('6', '5-6', inplace=True)
        self.df_paris_filter.c_ar.replace('PARIS CENTRE', '1', inplace=True)

        self.df_paris_clean = (self.df_paris_filter.groupby(
            ['annee', 'nomIndicLight', 'libelle', 'c_ar'])
            ['cumulInfraction', 'InfPour1000'].sum())

        self.df_paris_clean = self.df_paris_clean.reset_index()
        self.df_paris_clean.c_ar = self.df_paris_clean.c_ar.apply(
            lambda x: x+'eme' if x != '1' else x+'er')
        return self.df_paris_clean

    def geojsonParisReformat(self):
        # chargement dataset Geojson / paris arrondissements
        self.geojson_paris = gpd.read_file(
            'https://www.data.gouv.fr/fr/datasets/r/4765fe48-35fd-4536-b029-4727380ce23c')  # noqa
        # suppression col + tri par ar + resetindex avec drop de l'ancien
        self.geojson_paris = self.geojson_paris.drop(
            self.geojson_paris.iloc[:, :7], axis=1).sort_values(
            by='c_ar').reset_index(drop=True)
        # selection ar 5 et 6 en une seule série
        self.s_ar_5_6 = self.geojson_paris.iloc[[4, 5], 1]
        # formatage serie en geoseries
        self.s_ar_5_6_geos = gpd.GeoSeries(self.s_ar_5_6)
        # merge des coordonnées
        self.s_ar_5_6_union = self.s_ar_5_6_geos.unary_union
        # modification valeur geometry du 5 ar (now comporte 5 et 6)
        self.geojson_paris.iloc[4, 1] = self.s_ar_5_6_union
        # renommage colonne ar pour 5 et 6
        self.geojson_paris.iloc[4, 0] = '5-6'
        # conversion c_ar en str pour merge avec df paris
        self.geojson_paris.c_ar = self.geojson_paris.c_ar.apply(lambda x: str(x))
        self.geojson_paris.c_ar = self.geojson_paris.c_ar.apply(
            lambda x: x+'eme' if x != '1' else x+'er')
        return self.geojson_paris


# dfn = Map1()
# df = dfn.df1
# df_idf_filter = df[
#     (df.numDep == '92')
#     | (df.numDep == '93')
#     | (df.numDep == '94')
#     | (df.numDep == '75')
#     | (df.numDep == '77')
#     | (df.numDep == '91')
#     | (df.numDep == '95')
#     | (df.numDep == '78')]

# df_graph1 = df_idf_filter[['annee',
#                            'nomIndicLight', 'cumulInfraction']].query("nomIndicLight=='Homicides'")
#
# df_idf_filter.info()
