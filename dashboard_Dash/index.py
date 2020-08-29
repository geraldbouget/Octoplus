from apps import app1
from app import app
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
from urllib.request import urlopen
import json
import time
import plotly.express as px
import indexRequest
from indexRequest import Map1
df_request = Map1()


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://fonts.googleapis.com/css2',
                        {'href': "https://fonts.googleapis.com/css2?family=Lato:wght@900&display=swap",
                         'rel': "stylesheet"},
                        dbc.themes.BOOTSTRAP]

# couleurs projet:
colors = {'bgindex': '#F2F2F2',
          'bgnavbar': '#AD2E25',
          'police': 'white'}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Informations", href="/apps/app1"))
        #dbc.NavItem(dbc.NavLink("Informations", href="apps/app2"))
    ],
    brand="Crimes et délits enregistrés par les services de gendarmerie et de police depuis 2012",
    brand_href="/",
    color=colors['bgnavbar'],
    dark=True,
    brand_style={'font-size': 28},
    fluid=True
)
# creation map1
geojson = 'https://france-geojson.gregoiredavid.fr/repo/departements.geojson'
with urlopen(geojson) as response:
    dep = json.load(response)
# main data_frame
df = df_request.df1
# demographie data_frame
df_demo = df_request.df_demo
df_paris = df_request.parisReformat()
gpd_paris = df_request.geojsonParisReformat()
gpd_paris.to_file("assets/paris_geojson.geojson", driver='GeoJSON')
with open("assets/paris_geojson.geojson") as f:
    paris = json.load(f)

main_table = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='indicateurs',
                options=[{'label': str(i), 'value': i} for i in df.nomIndicLight.unique()],
                value=df.nomIndicLight.unique()[0],
                style={'width': '100%',
                       'text-align': 'left'
                       },
                placeholder='Choisir une catégorie',
                optionHeight=45
            ),
            width=2,

        ),
        dbc.Col(
            dcc.Dropdown(
                id='annee',
                options=[{'label': str(i), 'value': i}
                         for i in df.annee.sort_values().unique()],
                value=df.annee.sort_values().unique()[0],
                style={'width': '100%',
                       'text-align': 'left'
                       },
                placeholder='Choisir une année',
                # optionHeight=45
            ),
            width=1,
            # align='start'
        ),
        dbc.Col(
            dcc.Dropdown(
                id='carte',
                options=[{'label': 'Fance', 'value': 'france'},
                         {'label': 'Ile de France', 'value': 'idf'},
                         {'label': 'Paris', 'value': 'paris'}
                         ],
                value='france',
                style={'width': '100%',
                       'text-align': 'left'
                       },
                placeholder='Choisir une carte',
                # optionHeight=45
            ),
            width=1,
        ),
        dbc.Col(
            dcc.Dropdown(
                id='echelle',
                options=[{'label': 'Nbre cumulé d\'infractions', 'value': 'cumul'},
                         {'label': 'Nbre d\'infractions pour 1000 hbts.', 'value': 'pourcentage'}
                         ],
                value='cumul',
                optionHeight=45,
                style={'width': 160,
                       'text-align': 'left'
                       },
                placeholder='Choisir une échelle',
                # optionHeight=45
            ),
            width=2,
        ),
        dbc.Col(
            html.H6('Click + SHIFT sur la carte pour comparer plusieurs dépt. ou arrt.')
        )

    ],
        style={'margin-top': '30px',
               'margin-bottom': '15px'},
        # justify='around'
    ),
    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='map1'
            ),
            width=5,
            align='start'
        ),
        dbc.Col([
            dbc.Row(id='graph1',
                    no_gutters=False,
                    style={'margin-bottom': '10px'}
                    ),
            dbc.Row(id='graph2',
                    no_gutters=False,
                    style={'margin-top': '10px'}

                    )],
                width=6,
                align='end'
                )
    ],
        justify='between'
        # no_gutters=False
    ),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='criteres',
                options=[{'label': str(i), 'value': i} for i in list(df_demo.columns[0::])],
                value=['numDep',
                       'nom département',
                       'anneeRecensement',
                       'densite',
                       'nbrePopulation',
                       'Nombre de communes'
                       ],
                style={'width': '100%',
                       'text-align': 'left'
                       },
                placeholder='Choisir un critère',
                optionHeight=45,
                multi=True
            )
        ],
            width=10,
            align='start'
        )
    ],
        justify='start',
        style={'margin-top': '30px',
               'margin-bottom': '15px'}),
    dbc.Row([
        dbc.Col(id='tab_demo',
                width=11
                )
    ],
        justify='start')
]
)

app.layout = html.Div(dbc.Container([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content',
             style={'margin-right': '60px',
                    'margin-left': '60px'}
             )
],
    style={'background-color': colors['bgindex']},
    fluid=True))


@ app.callback(Output('page-content', 'children'),
               [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/' or pathname == '/index':
        return main_table
    elif pathname == '/apps/Nomenclature_Etat_4001.jpg':
        return html.Div(html.Img('/apps/Nomenclature_Etat_4001.jpg'))
    else:
        return '404'


@ app.callback(
    Output('map1', 'figure'),
    [Input('indicateurs', 'value'),
     Input('annee', 'value'),
     Input('carte', 'value'),
     Input('echelle', 'value')
     ])
def map(indicateur, annee, choix_carte, choix_echelle):
    if choix_echelle == 'cumul':
        colorscale = 'cumulInfraction'
    elif choix_echelle == 'pourcentage':
        colorscale = 'InfPour1000'

    if choix_carte == 'france' or choix_carte == None:
        df_filter = df[(df.nomIndicLight == indicateur) & (df.annee == annee)]
        df_filter = df_filter.groupby(['nomIndicLight', 'annee', 'numDep', 'nomDep',
                                       'nbrePopulation', 'densite']).sum().reset_index()
        fig = px.choropleth_mapbox(
            data_frame=df_filter,
            locations=df_filter['numDep'],  # Spatial coordinates
            color=df_filter[colorscale],
            geojson=dep,
            featureidkey="properties.code",
            hover_data={'nomDep': True,
                        'densite': True,
                        'cumulInfraction': True,
                        'numDep': False,
                        'nomIndicLight': '.2s',
                        'annee': True,
                        'InfPour1000': True},
            labels={'densite': 'Densité (hbts/km2)',
                    'nomDep': 'Département',
                    "cumulInfraction": 'Nbre d\'infractions',
                    'InfPour1000': 'Nbre d\'inf. / 1000 hbts',
                    'nomIndicLight': 'Cat. Infraction',
                    'annee': 'Année'},
            width=800,
            height=600,
            color_continuous_scale='matter'
        )
        fig.update_layout(mapbox_style='basic',
                          mapbox_accesstoken='pk.eyJ1IjoibWF2ZXJpY2s3NTAyMCIsImEiOiJjazlweTltbHAwYzNoM2x0Z3l0MmI3cWs4In0.8HJebuUvfbF9cU5ydJzecg',
                          mapbox_zoom=4.6,
                          mapbox_center={'lat': 47, 'lon': 2.344467863359848},
                          showlegend=False,
                          width=700,
                          height=600,
                          margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                          paper_bgcolor=colors['bgindex'],
                          title={'text': '<b>Nombre d\'infractions<br>enregistré par département</b></br>',
                                 'font': {'size': 18},
                                 'y': 0.97},
                          clickmode="event+select",
                          coloraxis={'colorbar': {'x': 0.05,
                                                  'y': 0.25,
                                                  'len': 0.5}}
                          # annotations=[
                          #     dict(
                          #         text='Ckick + SHIFT pour sélectionner plusieurs dept.',
                          #         align='left',
                          #         x=0.25,
                          #         y=0.8
                          #     )
                          # ]
                          )
        # remplacement signe = par : pour texte hover
        for data in fig.data:
            data.hovertemplate = data.hovertemplate.replace("=", " :   ")

    elif choix_carte == 'paris':
        df_paris_filter = df_paris[(df_paris.nomIndicLight == indicateur)
                                   & (df_paris.annee == annee)]
        df_paris_filter = df_paris_filter.groupby(['nomIndicLight', 'annee', 'c_ar'
                                                   ]).sum().reset_index()

        fig = px.choropleth_mapbox(
            data_frame=df_paris_filter,
            locations=df_paris_filter['c_ar'],  # Spatial coordinates
            color=df_paris_filter[colorscale],
            geojson=paris,
            featureidkey="properties.c_ar",
            hover_data={'c_ar': True,
                        'cumulInfraction': True,
                        'nomIndicLight': '.2s',
                        'annee': True,
                        'InfPour1000': True},
            labels={
                'c_ar': 'Arrondissement',
                "cumulInfraction": 'Nbre d\'infractions',
                'InfPour1000': 'Nbre d\'infractions / 1000 hbts',
                'nomIndicLight': 'Cat. Infraction',
                'annee': 'Année'},
            width=800,
            height=600,
            color_continuous_scale='matter'
        )

        fig.update_layout(mapbox_style='light',
                          mapbox_accesstoken='pk.eyJ1IjoibWF2ZXJpY2s3NTAyMCIsImEiOiJjazlweTltbHAwYzNoM2x0Z3l0MmI3cWs4In0.8HJebuUvfbF9cU5ydJzecg',
                          mapbox_zoom=10.8,
                          mapbox_center={'lat': 48.8534, 'lon': 2.3488},
                          showlegend=False,
                          width=700,
                          height=600,
                          margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                          paper_bgcolor=colors['bgindex'],
                          title={'text': '<b>Nombre d\'infractions<br>enregistré à Paris</b></br>',
                                 'font': {'size': 18},
                                 'y': 0.97},
                          clickmode="event+select",
                          coloraxis={'colorbar': {'x': 0.05,
                                                  'y': 0.15,
                                                  'len': 0.3,
                                                  'bgcolor': 'white'}
                                     }
                          )
        # remplacement signe = par : pour texte hover
        for data in fig.data:
            data.hovertemplate = data.hovertemplate.replace("=", " :   ")

    elif choix_carte == 'idf':
        df_idf_filter = df[(df.nomIndicLight == indicateur) &
                           (df.annee == annee) & (
            (df.numDep == '92')
            | (df.numDep == '93')
            | (df.numDep == '94')
            | (df.numDep == '75')
            | (df.numDep == '77')
            | (df.numDep == '91')
            | (df.numDep == '95')
            | (df.numDep == '78'))]
        df_idf_filter = df_idf_filter.groupby(['nomIndicLight', 'annee', 'numDep', 'nomDep',
                                               'nbrePopulation', 'densite']).sum().reset_index()

        fig = px.choropleth_mapbox(
            data_frame=df_idf_filter,
            locations=df_idf_filter['numDep'],  # Spatial coordinates
            color=df_idf_filter[colorscale],
            geojson=dep,
            featureidkey="properties.code",
            hover_data={'nomDep': True,
                        'densite': True,
                        'cumulInfraction': True,
                        'numDep': False,
                        'nomIndicLight': '.2s',
                        'annee': True,
                        'InfPour1000': True},
            labels={'densite': 'Densité (hbts/km2)',
                    'nomDep': 'Département',
                    "cumulInfraction": 'Nbre d\'infractions',
                    'InfPour1000': 'Nbre d\'inf. / 1000 hbts',
                    'nomIndicLight': 'Cat. Infraction',
                    'annee': 'Année'},
            width=800,
            height=600,
            color_continuous_scale='matter'
        )

        fig.update_layout(mapbox_style='streets',
                          mapbox_accesstoken='pk.eyJ1IjoibWF2ZXJpY2s3NTAyMCIsImEiOiJjazlweTltbHAwYzNoM2x0Z3l0MmI3cWs4In0.8HJebuUvfbF9cU5ydJzecg',
                          mapbox_zoom=7.5,
                          mapbox_center={'lat': 48.8534, 'lon': 2.3488},
                          showlegend=False,
                          width=700,
                          height=600,
                          margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                          paper_bgcolor=colors['bgindex'],
                          title={'text': '<b>Nombre d\'infractions<br>enregistré par département - Ile de France</b></br>',
                                 'font': {'size': 18},
                                 'y': 0.97},
                          clickmode="event+select",
                          coloraxis={'colorbar': {'x': 0.05,
                                                  'y': 0.60,
                                                  'len': 0.5}}
                          )
        # remplacement signe = par : pour texte hover
        for data in fig.data:
            data.hovertemplate = data.hovertemplate.replace("=", " :   ")

    return fig


@ app.callback(
    Output(component_id='graph1', component_property='children'),
    [Input('map1', 'selectedData'),
     Input('indicateurs', 'value'),
     Input('carte', 'value'),
     Input('echelle', 'value')
     ])
def graph1(select, indicateur, choix_carte, choix_echelle):
    if choix_echelle == 'cumul':
        echelle = 'cumulInfraction'
    elif choix_echelle == 'pourcentage':
        echelle = 'InfPour1000'

    if choix_carte == 'france' or choix_carte == None:

        df_graph1 = df[['annee',
                        'nomIndicLight', echelle]].query('nomIndicLight==@indicateur')
        if select is None:
            data = []
            # le df de base contient une ligne par departement donc si je pivoter
            # directement je vais avoir duplicate en index. Faut donc d'abord
            # filtrer df sans nomdep et sans numdep puis faire groupby
            # data = []

            df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
            df_graph1_pivot = df_graph1.pivot(
                index='nomIndicLight',
                columns='annee',
                values=echelle)
            data.append(df_graph1_pivot.iloc[0].to_list())
            titleGraph1 = 'pour la France entière'

        elif len(select['points']) == 1:
            if select['points'][0]['location'] not in str(df['numDep'].tolist()):
                data = []
                # le df de base contient une ligne par departement donc si je pivoter
                # directement je vais avoir duplicate en index. Faut donc d'abord
                # filtrer df sans nomdep et sans numdep puis faire groupby
                # data = []

                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = 'pour la France entière'

            if select['points'][0]['location'] in str(df['numDep'].tolist()):
                data = []
                df_graph1 = df[['nomDep', 'numDep', 'annee',
                                'nomIndicLight', echelle]]
                # pivoter table pour visualisation en mode bar/stac
                dep = select['points'][0]['location']
                q = 'nomIndicLight==@indicateur & numDep==@dep'
                df_graph1 = df_graph1.query(q).groupby(
                    ['nomDep', 'numDep', 'annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                titleGraph1 = f'''pour le département: {select['points'][0]['customdata'][0]}'''
                data.append(df_graph1_pivot.iloc[0].to_list())

        elif len(select['points']) > 1:
            if select['points'][0]['location'] not in str(df['numDep'].tolist()):
                data = []
                # le df de base contient une ligne par departement donc si je pivoter
                # directement je vais avoir duplicate en index. Faut donc d'abord
                # filtrer df sans nomdep et sans numdep puis faire groupby
                # data = []

                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = 'pour la France entière'

            if select['points'][0]['location'] in str(df['numDep'].tolist()):
                data = []
                deps = []
                # data = []
                for i in range(len(select['points'])):
                    if select['points'][i]['location'] not in deps:
                        deps.append(select['points'][i]['location'])

                for dep in deps:
                    q = 'nomIndicLight==@indicateur & numDep==@dep'
                    df_graph1 = df[['nomDep', 'numDep', 'annee',
                                    'nomIndicLight', echelle]]
                    df_graph1 = df_graph1.query(q).groupby(
                        ['nomDep', 'numDep', 'annee', 'nomIndicLight']).sum().reset_index()
                    df_graph1_pivot = df_graph1.pivot(
                        index='nomIndicLight',
                        columns='annee',
                        values=echelle)
                    # titleGraph1 = f'''par indicateur et par année - Territoire : {select['points'][0]['customdata'][0]}'''
                    data.append(df_graph1_pivot.iloc[0].to_list())
                    titleGraph1 = '''pour les départements sélectionnés'''

    elif choix_carte == 'idf':

        df_idf_filter = df[
            (df.numDep == '92')
            | (df.numDep == '93')
            | (df.numDep == '94')
            | (df.numDep == '75')
            | (df.numDep == '77')
            | (df.numDep == '91')
            | (df.numDep == '95')
            | (df.numDep == '78')]
        df_graph1 = df_idf_filter[['annee',
                                   'nomIndicLight', echelle]].query('nomIndicLight==@indicateur')

        if select is None:
            data = []
            # le df de base contient une ligne par departement donc si je pivoter
            # directement je vais avoir duplicate en index. Faut donc d'abord
            # filtrer df sans nomdep et sans numdep puis faire groupby
            # data = []

            df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
            df_graph1_pivot = df_graph1.pivot(
                index='nomIndicLight',
                columns='annee',
                values=echelle)
            data.append(df_graph1_pivot.iloc[0].to_list())
            titleGraph1 = 'en Île de France'

        elif len(select['points']) == 1:
            if select['points'][0]['location'] not in str(df_idf_filter['numDep'].tolist()):
                data = []
                # le df de base contient une ligne par departement donc si je pivoter
                # directement je vais avoir duplicate en index. Faut donc d'abord
                # filtrer df sans nomdep et sans numdep puis faire groupby
                # data = []

                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = 'en Île de France'

            if select['points'][0]['location'] in str(df_idf_filter['numDep'].tolist()):
                data = []
                df_graph1 = df_idf_filter[['nomDep', 'numDep', 'annee',
                                           'nomIndicLight', echelle]]
                # pivoter table pour visualisation en mode bar/stac
                dep = select['points'][0]['location']
                q = 'nomIndicLight==@indicateur & numDep==@dep'
                df_graph1 = df_graph1.query(q).groupby(
                    ['nomDep', 'numDep', 'annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                titleGraph1 = f'''pour le département: {select['points'][0]['customdata'][0]}'''
                data.append(df_graph1_pivot.iloc[0].to_list())

        elif len(select['points']) > 1:
            if select['points'][0]['location'] not in str(df_idf_filter['numDep'].tolist()):
                data = []
                # le df de base contient une ligne par departement donc si je pivoter
                # directement je vais avoir duplicate en index. Faut donc d'abord
                # filtrer df sans nomdep et sans numdep puis faire groupby
                # data = []

                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = 'en Île de France'

            if select['points'][0]['location'] in str(df_idf_filter['numDep'].tolist()):
                data = []
                deps = []
                # data = []
                for i in range(len(select['points'])):
                    if select['points'][i]['location'] not in deps:
                        deps.append(select['points'][i]['location'])

                for dep in deps:
                    q = 'nomIndicLight==@indicateur & numDep==@dep'
                    df_graph1 = df_idf_filter[['nomDep', 'numDep', 'annee',
                                               'nomIndicLight', echelle]]
                    df_graph1 = df_graph1.query(q).groupby(
                        ['nomDep', 'numDep', 'annee', 'nomIndicLight']).sum().reset_index()
                    df_graph1_pivot = df_graph1.pivot(
                        index='nomIndicLight',
                        columns='annee',
                        values=echelle)
                    # titleGraph1 = f'''par indicateur et par année - Territoire : {select['points'][0]['customdata'][0]}'''
                    data.append(df_graph1_pivot.iloc[0].to_list())
                    titleGraph1 = f'''pour les départements sélectionnés'''

    elif choix_carte == 'paris':
        # data = []

        if select is None:
            data = []

            # le df de base contient une ligne par departement donc si je pivoter
            # directement je vais avoir duplicate en index. Faut donc d'abord
            # filtrer df sans nomdep et sans numdep puis faire groupby
            # data = []
            df_graph1 = df_paris[['annee',
                                  'nomIndicLight', echelle]].query('nomIndicLight==@indicateur')
            df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
            df_graph1_pivot = df_graph1.pivot(
                index='nomIndicLight',
                columns='annee',
                values=echelle)
            data.append(df_graph1_pivot.iloc[0].to_list())
            titleGraph1 = '''pour tout Paris'''

        elif len(select['points']) == 1:
            # condition pour cas ou selection faite sur précedente carte
            # si point en mémoire pas arr de paris on affiche graph pour tout
            # paris :
            if select['points'][0]['location'] not in str(df_paris['c_ar'].tolist()):

                data = []
                df_graph1 = df_paris[['annee',
                                      'nomIndicLight', echelle]].query('nomIndicLight==@indicateur')
                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = '''pour tout Paris'''

            elif select['points'][0]['location'] in str(df_paris['c_ar'].tolist()):

                data = []
                df_graph1 = df_paris[['c_ar', 'annee',
                                      'nomIndicLight', echelle]]
                # pivoter table pour visualisation en mode bar/stac
                arr = select['points'][0]['location']
                q = 'nomIndicLight==@indicateur & c_ar==@arr'
                df_graph1 = df_graph1.query(q).groupby(
                    ['c_ar', 'annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                titleGraph1 = f'''pour l'arrondissement: {select['points'][0]['customdata'][0]}'''
                data.append(df_graph1_pivot.iloc[0].to_list())

        elif len(select['points']) > 1:
            if select['points'][0]['location'] not in str(df_paris['c_ar'].tolist()):
                data = []
                df_graph1 = df_paris[['annee',
                                      'nomIndicLight', echelle]].query('nomIndicLight==@indicateur')
                df_graph1 = df_graph1.groupby(['annee', 'nomIndicLight']).sum().reset_index()
                df_graph1_pivot = df_graph1.pivot(
                    index='nomIndicLight',
                    columns='annee',
                    values=echelle)
                data.append(df_graph1_pivot.iloc[0].to_list())
                titleGraph1 = '''pour tout Paris'''
            elif select['points'][0]['location'] in str(df_paris['c_ar'].tolist()):
                data = []
                arrt = []
                # data = []
                for i in range(len(select['points'])):
                    if select['points'][i]['location'] not in arrt:
                        arrt.append(select['points'][i]['location'])

                for arr in arrt:
                    q = 'nomIndicLight==@indicateur & c_ar ==@arr'
                    df_graph1 = df_paris[['c_ar', 'annee',
                                          'nomIndicLight', echelle]]
                    df_graph1 = df_graph1.query(q).groupby(
                        ['c_ar', 'annee', 'nomIndicLight']).sum().reset_index()
                    df_graph1_pivot = df_graph1.pivot(
                        index='nomIndicLight',
                        columns='annee',
                        values=echelle)
                    # titleGraph1 = f'''par indicateur et par année - Territoire : {select['points'][0]['customdata'][0]}'''
                    data.append(df_graph1_pivot.iloc[0].to_list())
                    titleGraph1 = f'''pour les arrondissements sélectionnés'''

    x = list(df.annee.unique())

    # liste d'iteration de chaque ligne de df pivot

    fig = go.Figure()
    for j in range(len(data)):
        if select is None:
            fig.add_trace(go.Scatter(
                mode='lines',
                # name='France entière',  # nom de chaque infraction
                x=x,  # liste années
                y=data[j],  # nbre d'infractions par année
                # largeurs lines en fonction de la différence de valeur entre 2012 et 2019
                line=dict(color=px.colors.qualitative.Dark24[j], width=4),
                hoverinfo='name+y',
                hoverlabel=dict(namelength=-1)
                # line=dict(width=4)
            ))
        else:
            fig.add_trace(go.Scatter(
                mode='lines',
                name=select['points'][j]['customdata'][0],  # nom de chaque infraction
                x=x,  # liste années
                y=data[j],  # nbre d'infractions par année
                # largeurs lines en fonction de la différence de valeur entre 2012 et 2019
                line=dict(color=px.colors.qualitative.Dark24[j], width=4),
                hoverinfo='name+y',
                hoverlabel=dict(namelength=-1)
            ))

    fig.update_layout(barmode='stack',
                      # legend=dict(bgcolor='#07B0F2'),
                      width=800,
                      height=300,
                      # margin=dict(pad=10),
                      #             ),
                      title=dict(text='<b>Évolution du nombre des infractions enregistrées :</b>'
                                 + '<br><b>'+df_graph1_pivot.index[0]+'</b>'
                                 + '<b>'+' - '+str(titleGraph1)+'</b></br>',
                                 font=dict(size=17),
                                 x=0.1
                                 ),
                      plot_bgcolor='#B6D6F2',
                      paper_bgcolor='#B6D6F2',
                      xaxis=dict(
                          showgrid=False,
                          # gridwidth=0.5,
                          zeroline=False),
                      yaxis=dict(
                          showgrid=False,
                          gridwidth=0,
                          zeroline=False),
                      xaxis_title='Années',
                      yaxis_title='Nbre. cumulé des infractions'
                      )

    return dcc.Graph(figure=fig)


@ app.callback(
    Output(component_id='graph2', component_property='children'),
    [Input('map1', 'clickData'),
     Input('indicateurs', 'value'),
     Input('annee', 'value'),
     Input('carte', 'value')
     ])
def graph2(click, indicateur, year, choix_carte):
    if choix_carte == None or choix_carte == 'france':
        titre1_graph = 'dans la France entière depuis 2012'

        if click is None:
            df_graph2 = df[['libelle', 'nomIndicLight', 'cumulInfraction']
                           ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()
            titre_graph = (f'{str(indicateur)}'
                           + f' {titre1_graph}')
        elif click is not None:
            if click['points'][0]['location'] not in str(df.numDep.tolist()):
                if choix_carte == 'france':
                    titre1_graph = 'dans la France entière depuis 2012'
                elif choix_carte == 'idf':
                    titre1_graph = 'en Île de France depuis 2012'

                df_graph2 = df[['libelle', 'nomIndicLight', 'cumulInfraction']
                               ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()
                titre_graph = (f'{str(indicateur)}'
                               + f' {titre1_graph}')

            if click['points'][0]['location'] in str(df.numDep.tolist()):
                gv = click['points'][0]['location']
                q = "annee == @year & nomIndicLight == @indicateur & numDep == @gv"
                df_graph2 = df.query(q)
                titre_graph = (f'{str(indicateur)}'
                               + f" en {str(year)}. Département {click['points'][0]['customdata'][0]}")

    if choix_carte == 'idf':
        df_idf_filter = df[
            (df.numDep == '92')
            | (df.numDep == '93')
            | (df.numDep == '94')
            | (df.numDep == '75')
            | (df.numDep == '77')
            | (df.numDep == '91')
            | (df.numDep == '95')
            | (df.numDep == '78')]
        if click is None:
            titre1_graph = 'en Île de France depuis 2012'
            titre_graph = (f'{str(indicateur)}'
                           + f' {titre1_graph}')

            df_graph2 = df_idf_filter[['annee',
                                       'nomIndicLight', 'cumulInfraction']].query('nomIndicLight==@indicateur')
            df_graph2 = df[['libelle', 'nomIndicLight', 'cumulInfraction']
                           ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()

        elif click is not None:
            if click['points'][0]['location'] not in str(df_idf_filter.numDep.tolist()):
                titre1_graph = 'en Île de France depuis 2012'

                df_graph2 = df_idf_filter[['libelle', 'nomIndicLight', 'cumulInfraction']
                                          ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()
                titre_graph = (f'{str(indicateur)}'
                               + f' {titre1_graph}')

            if click['points'][0]['location'] in str(df_idf_filter.numDep.tolist()):
                gv = click['points'][0]['location']
                q = "annee == @year & nomIndicLight == @indicateur & numDep == @gv"
                df_graph2 = df_idf_filter.query(q)
                titre_graph = (f'{str(indicateur)}'
                               + f" en {str(year)}. Département {click['points'][0]['customdata'][0]}")

    elif choix_carte == 'paris':

        if click is None:
            df_graph2 = df_paris[['libelle', 'nomIndicLight', 'cumulInfraction']
                                 ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()
            titre_graph = (f'{str(indicateur)}'
                           + ' sur Paris depuis 2012')
        else:
            if click['points'][0]['location'] not in df_paris.c_ar.tolist():
                df_graph2 = df_paris[['libelle', 'nomIndicLight', 'cumulInfraction']
                                     ].groupby(['libelle', 'nomIndicLight']).sum().reset_index()
                titre_graph = (f'{str(indicateur)}'
                               + ' sur Paris depuis 2012')

            if click['points'][0]['location'] in df_paris.c_ar.tolist():
                gv = click['points'][0]['location']
                q = "annee == @year & nomIndicLight == @indicateur & c_ar == @gv"
                df_graph2 = df_paris.query(q)
                titre_graph = titre_graph = (f'{str(indicateur)}'
                                             + f" en {str(year)}. Arrondissement n° {click['points'][0]['location']}")

    # libelle trop longs parfois depasse sur pie >> on donne longueur max au string
    lab = [label[0:65]
           for label in df_graph2[df_graph2.nomIndicLight == indicateur].libelle]
    lab_full = [label for label in df_graph2[df_graph2.nomIndicLight == indicateur].libelle]
    fig_pie = go.Figure(data=[go.Pie(labels=lab,
                                     values=[p for p in df_graph2[df_graph2.nomIndicLight == indicateur].cumulInfraction])])

    fig_pie.update_traces(
        hoverinfo='label+percent',
        # text=df_repart_index_indic[df_repart_index_indic.nomIndicLight==indicateur].libelle,
        textposition='inside',
        textinfo='percent',
        insidetextfont=dict(family="Courier New"),
        textfont_size=20,
        marker=dict(line=dict(color='#000000', width=2),
                    colors=px.colors.qualitative.Dark24),
        # domain=dict(x=[1,1]),
        showlegend=True,
        title=dict(text='',
                   position='top left',
                   font=dict(size=15))
    )

    fig_pie.update_layout(
        showlegend=True,
        width=800,
        height=300,
        margin=dict(l=20,
                    b=5,
                    r=5,
                    t=50),
        title=dict(
            text=('<b>Répartition moyenne des infractions dans la catégorie </b>'
                  + '<b>'+'<br>'+titre_graph+'</b></br>')),
        paper_bgcolor='#B6D6F2',
        legend=dict(orientation='v',
                    xanchor='left',
                    x=-1,
                    y=0.5
                    )
    )
    return dcc.Graph(figure=fig_pie)


@ app.callback(
    Output(component_id='tab_demo', component_property='children'),
    [Input('map1', 'selectedData'),
     Input('criteres', 'value'),
     Input('carte', 'value')])
def tab_demo(select, crits, choix_carte):
    cellFillColor_1 = '#A7D5F2'
    cellFillColor_2 = '#D5E7F2'
    if choix_carte != 'paris':
        if select is None:
            # gv = click['points'][0]['location']
            # q = "numDep == @gv"
            df_demo1 = df_demo[crits]
            fig_tab1 = go.Figure(
                data=[
                    go.Table(
                        header=dict(values=list(df_demo1.columns),
                                    fill_color='#115D8C',
                                    align='left',
                                    line_color='rgb(49, 130, 189)',
                                    font=dict(color='white', size=12)
                                    ),
                        cells=dict(values=[df_demo1[col] for col in df_demo1.columns],
                                   fill_color=[[cellFillColor_1, cellFillColor_2]*len(df_demo1)],
                                   line_color='#115D8C',
                                   align='left'
                                   ),
                        columnwidth=10,
                    )
                ]
            )
            fig_tab1.update_layout(
                margin=dict(
                    t=0,
                    l=0,
                    r=0,
                    b=0),
                paper_bgcolor='#F2F2F2'
            )
        if select is not None:
            deps = []
            for i in range(len(select['points'])):
                deps.append(select['points'][i]['location'])
            q = "numDep==@deps"
            df_demo1 = df_demo.query(q)
            fig_tab1 = go.Figure(
                data=[
                    go.Table(
                        header=dict(values=crits,
                                    fill_color='#115D8C',
                                    align='left',
                                    line_color='rgb(49, 130, 189)',
                                    font=dict(color='white', size=12)
                                    ),
                        cells=dict(values=[df_demo1[col] for col in crits],
                                   fill_color=[[cellFillColor_1, cellFillColor_2]*len(df_demo1)],
                                   line_color='#115D8C',
                                   align='left'
                                   )
                    )
                ]
            )
            fig_tab1.update_layout(
                margin=dict(
                    t=0,
                    l=0,
                    r=0,
                    b=0),
                paper_bgcolor='#F2F2F2')

    if choix_carte == 'paris':
        df_demo1 = df_demo.query("numDep=='75'")
        fig_tab1 = go.Figure(
            data=[
                go.Table(
                    header=dict(values=crits,
                                fill_color='#115D8C',
                                align='left',
                                line_color='rgb(49, 130, 189)',
                                font=dict(color='white', size=12)
                                ),
                    cells=dict(values=[df_demo1[col] for col in crits],
                               fill_color=[[cellFillColor_1, cellFillColor_2]*len(df_demo1)],
                               line_color='#115D8C',
                               align='left'
                               )
                )
            ]
        )
        fig_tab1.update_layout(
            margin=dict(
                t=0,
                l=0,
                r=0,
                b=0),
            paper_bgcolor='#F2F2F2')

    return dcc.Graph(figure=fig_tab1)


@ app.callback(
    Output(component_id='essai', component_property='children'),
    [dash.dependencies.Input('graph1', 'value')])
def essai(click):

    # print(len(sel))
    return json.dumps(click, indent=2)
    # w = []
    # for i in range(len(sel['points'])):
    #     w.append(sel['points'][i]['location'])
    # return w


if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='127.0.0.1')
