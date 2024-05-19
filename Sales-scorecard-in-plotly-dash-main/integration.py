import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt
from dash import dcc, html
import pyodbc
import plotly.express as px
from dash.exceptions import PreventUpdate
from flask import Flask, request, jsonify

# Initialize Flask server
flask_app = Flask(__name__)

# Database connection
server = 'DESKTOP-8MJF8PH\\MSSQLSERVER1'  # Notez les doubles antislash pour l'instance
database = 'STAGE_VERMEG'
connection_string = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Se connecter à la base de données
conn = pyodbc.connect(connection_string)

# Exécuter une requête SQL pour récupérer les données
query = """
SELECT [etat], [montant], [date], [type], [fournisseur], [Facture]
FROM [dbo].[fait] f
JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
"""
montant = pd.read_sql(query, conn)
etat_query = "SELECT DISTINCT [Etat] FROM [dbo].[Dimensions Facture]"
etat_df = pd.read_sql(etat_query, conn)
options = [{'label': etat_, 'value': etat_} for etat_ in etat_df['Etat']]

# Convertir la colonne 'Date' en format de date
montant['date'] = pd.to_datetime(montant['date'])
# Convertir la colonne 'date' en format de chaîne de caractères avec le format 'yyyy-mm-dd'
montant['date_str'] = montant['date'].dt.strftime('%d-%m-%YYYY')

# Extraire la sous-chaîne de caractères correspondant aux six premiers caractères à partir de l'index 1
montant['date_substr'] = montant['date_str'].str[0:10]

# Récupérer les fournisseurs uniques depuis la base de données
fournisseurs_query = "SELECT DISTINCT [Fournisseur] FROM [dbo].[Dimension fournisseur]"
fournisseurs_df = pd.read_sql(fournisseurs_query, conn)
options_fournisseurs = [{'label': fournisseur_, 'value': fournisseur_} for fournisseur_ in fournisseurs_df['Fournisseur']]

supplier_name = None  # Variable globale temporaire pour stocker le fournisseur

# Flask route for receiving data from Rasa
@flask_app.route('/', methods=['POST'])
def update_filter():
    global supplier_name
    data = request.get_json()
    supplier_name = data.get('fournisseur')
    print("Données reçues:", data)
    return jsonify({'message': 'Fournisseur mis à jour'})

# Initialize Dash app with Flask server
app = dash.Dash(__name__, server=flask_app, meta_tags=[{"name": "viewport", "content": "width=device-width"}], suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id='supplier_store'),  # Store component for supplier name
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Interval component to check every second
    
    html.Div([
        html.H1('InvoiceBot', style={'margin-top': '40px'}),
    ], className="one-third column", id="title1"),
    
    html.Div([
        html.P('Fournisseurs', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(id='dropdown_fournisseurs',
                     options=options_fournisseurs,  # Initial options
                     value=None,  # Default value
                     multi=False,  # Assuming single selection for setting active
                     style={'color': 'black'}, className='dcc_compon'),
    ])
])



# Dash callback to update the supplier store and dropdown options
@app.callback(
    Output('supplier_store', 'data'),
    Output('dropdown_fournisseurs', 'options'),
    Output('dropdown_fournisseurs', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_supplier_store_and_dropdown(n_intervals):
    global supplier_name
    print("Updating supplier_store with:", supplier_name)  # Debug log
    if supplier_name:
        options = [{'label': supplier_name, 'value': supplier_name}]
        value = supplier_name
        print("Options and value updated with supplier:", supplier_name)  # Debug log
    else:
        options = options_fournisseurs  # If no supplier data, use initial options
        value = [] 
        print("No supplier data, options and value set to default")  # Debug log
    return supplier_name, options, value


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8053, debug=True)
