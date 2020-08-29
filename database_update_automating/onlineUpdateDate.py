

import re
import requests
from bs4 import BeautifulSoup
# import dateparser


# parsing la page web du dataset pour récupérer
# la date de la dernièr emise à jour
def OnlineCheck():
    src = requests.get('''https://www.data.gouv.fr/fr/datasets/crimes-
    et-delits-enregistres-par-les-services-de-gendarmerie-et-de-police
    -depuis-2012/''').text
    soup = BeautifulSoup(src, features="lxml")
    content_links = soup.find_all('div', class_='panel-body')
    link1 = content_links[1]
    link2 = link1('li')[5].text
    french_date_string = re.sub(r'[\r\n]|(\s{2,})', '', link2)
    # french_date_format = (
    #                     dateparser.parse(french_date_string).date())
    with open('maj_octoplus.txt', 'a') as log_file:
        log_file.write('\r\nla dernière mise à jour du dataset a été mise en ligne le '
                       + f'{french_date_string}\r\n')


# print(OnlineUpdateDate())
