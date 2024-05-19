import dash
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt
from dash import dcc, html, State
import plotly.graph_objs as go
import pyodbc
import plotly.express as px
from dash.exceptions import PreventUpdate
from flask import Flask, request, jsonify
import requests
from flask import jsonify, request
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
# Définir les informations de connexion
server = 'DESKTOP-8MJF8PH\\MSSQLSERVER1'  # Notez les doubles antislash pour l'instance
database = 'STAGE_VERMEG'

# Chaîne de connexion
connection_string = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes;'


    # Se connecter à la base de données
conn = pyodbc.connect(connection_string)
    
    # Exécuter une requête SQL pour récupérer les données
query = """SELECT [etat], [montant], [date] ,[type],[fournisseur],[Facture] FROM [dbo].[fait] f
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
    """
montant = pd.read_sql(query, conn)
etat_query = "SELECT DISTINCT [Etat] FROM [dbo].[Dimensions Facture]"
etat_df = pd.read_sql(etat_query, conn)
options = [{'label': etat_, 'value': etat_} for etat_ in etat_df['Etat']]

#     # Convertir la colonne 'Date' en format de date
montant['date'] = pd.to_datetime(montant['date'])
# Convertir la colonne 'date' en format de chaîne de caractères avec le format 'yyyy-mm-dd'
montant['date_str'] = montant['date'].dt.strftime('%d-%m-%YYYY')

# Extraire la sous-chaîne de caractères correspondant aux six premiers caractères à partir de l'index 1
montant['date_substr'] = montant['date_str'].str[0:10]

# Récupérer les fournisseurs uniques depuis la base de données
fournisseurs_query = "SELECT DISTINCT [Fournisseur] FROM [dbo].[Dimension fournisseur]"
fournisseurs_df = pd.read_sql(fournisseurs_query, conn)
options_fournisseurs = [{'label': fournisseur_, 'value': fournisseur_} for fournisseur_ in fournisseurs_df['Fournisseur']]

# Récupérer les types uniques depuis la base de données
types_query = "SELECT DISTINCT [Type] FROM [dbo].[Dimension fournisseur]"
types_df = pd.read_sql(types_query, conn)
options_types = [{'label': type_, 'value': type_} for type_ in types_df['Type']]

# Récupérer les types uniques depuis la base de données
Factures_query = "SELECT DISTINCT [facture] FROM [dbo].[Dimensions Facture]"
Factures_df = pd.read_sql(Factures_query, conn)
options_factures = [{'label': Facture_, 'value': Facture_} for Facture_ in Factures_df['facture']]

num_invoices = len(montant)
total_amount = montant['montant'].sum()
total_types = montant['type'].nunique()
total_fournisseurs = montant['fournisseur'].nunique()

# Initialize Flask server

flask_app = Flask(__name__)
supplier_name = None
app = dash.Dash(__name__, server=flask_app, meta_tags=[{"name": "viewport", "content": "width=device-width"}], suppress_callback_exceptions=True)
# Flask route for receiving data from Rasa
@flask_app.route('/', methods=['POST'])
def update_filter():
    global supplier_name
    data = request.get_json()
    supplier_name = data.get('fournisseur')
    # Write to a file
    with open('supplier_name.txt', 'w') as f:
        f.write(supplier_name)
    return jsonify({'message': 'Supplier updated successfully'})

# Initialize Dash app with Flask server

app.layout = html.Div([
    dcc.Store(id='supplier_store'),  # Store component for supplier name
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Interval component to check every second
    
    html.Div([
        html.H1('InvoiceBot', style={'margin-top': '40px'}),
    ], className="one-third column", id="title1"),
    
    html.Div([        
        html.P('Fournisseurs', className='fix_label', style={'color': 'white','margin-left': '20px'}),
         dcc.Dropdown(id='dropdown_fournisseurs',
                 options=options_fournisseurs,
                 value=[],  # Valeur par défaut
                 multi=True,
                 style={'color': 'black'}, className='dcc_compon'),
    ])
])


html.Div([
    # Première ligne
    html.Div([
        # Premier graphique bar chart
        html.Div([
            html.Button('Aggrandir', id='aggrandir_button1', n_clicks=0, style={'position': 'absolute', 'top': '8px', 'left': '8px'}),
            dcc.Store(id='state_aggrandir1', data=False),
            dcc.RadioItems(
                id='radio_items1',
                labelStyle={"display": "inline-block"},
                value='fournisseur',
                options=[
                    {'label': 'Fournisseur', 'value': 'fournisseur'},
                    {'label': 'Type', 'value': 'type'}
                ],
                style={'text-align': 'center', 'color': 'white'},
                className='dcc_compon'
            ),
            dcc.Graph(
                id='bar_chart1',
                config={'displayModeBar': 'hover'},
                style={'height': '280px', 'padding-top': '27px'}
            ),
        ], className='create_container2 six-third columns', style={'height': '350px'}, id='Block_div1')
        ], className='create_container2 six-third  columns', style={'height': '350px'}, id='Block_div4'),
    ], className="row flex-display"),



@app.callback(
    Output('bar_chart1', 'figure'),
    [Input('dropdown_fournisseurs', 'value')]
)
def update_graph(selected_fournisseurs):
    if not selected_fournisseurs:
        raise PreventUpdate

    filtered_df = montant[montant['fournisseur'].isin(selected_fournisseurs)]

    fig = go.Figure(data=[
        go.Bar(
            x=filtered_df['fournisseur'],
            y=filtered_df['montant'],
            text=filtered_df['montant'],
            textposition='auto'
        )
    ])

    fig.update_layout(title='Montant par Fournisseur',
                      xaxis_title='Fournisseur',
                      yaxis_title='Montant')

    return fig




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8053, debug=True)
