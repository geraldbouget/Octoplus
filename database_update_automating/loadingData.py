import pandas as pd
import re
# récupération du dataset à jour surle site data.gouv
# utilisatoin de pd.ExcelFile pour pouvoir récupérer facilement
# le nom des sheetnmanes dans main

df_source = pd.ExcelFile('https://www.data.gouv.fr/fr/\
datasets/r/d792092f-b1f7-4180-a367-d043200c1520')


# def loading():
#     try:
#         df_source = pd.ExcelFile('https://www.data.gouv.fr/fr/\
#         datasets/r/d792092f-b1f7-4180-a367-d043200c1520')
#     except Exception as e:
#         with open('maj_octoplus.log', 'a') as log_file:
#             log_file.write('Le fichier excel n\a pas pu être téléchargé.\r\n'
#                            + 'L\erreur suivante s\'est produite: \r\n'
#                            + f'{e}'+'\r\n')
#     else:
#         return df_source
