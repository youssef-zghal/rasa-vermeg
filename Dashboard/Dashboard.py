import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt
import pyodbc
import plotly.express as px
import traceback

# Définir les informations de connexion
server = 'DESKTOP-8MJF8PH\\MSSQLSERVER1'  # Notez les doubles antislash pour l'instance
database = 'STAGE_VERMEG'

# Chaîne de connexion
connection_string = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    # Se connecter à la base de données
    conn = pyodbc.connect(connection_string)
    
    # Exécuter une requête SQL pour récupérer les données
    query = """SELECT [etat], [montant], [date] ,[type],[fournisseur] FROM [dbo].[fait] f
            JOIN dbo.[Dimension fournisseur] fournisseur ON f.FK_Fournisseur = fournisseur.Pk_fournisseur
            JOIN dbo.[Dimensions facture] facture ON f.FK_facture = facture.PK_facture
            JOIN dbo.[Dimension_dates] date ON f.FK_Date = Date.DateKey
    """
    montant = pd.read_sql(query, conn)
#     # Convertir la colonne 'Date' en format de date
    montant['date'] = pd.to_datetime(montant['date'])
except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {str(e)}")

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div(
    style={'background-color': 'rgb(25,25,112)'},
    children=[
        html.Div(
            children=[
                html.H3('InvoiceBot', style={'color': 'white'}),
                html.P('Année', className='fix_label', style={'color': 'white'}),
                dcc.Slider(
                    id='select_year',
                    tooltip={'always_visible': True},
                    min=2021,
                    max=2023,
                    step=1,
                    value=2023,
                    marks={str(yr): str(yr) for yr in range(2021, 2024)},
                    className='dcc_compon'
                ),
                html.P('État', className='fix_label', style={'color': 'white'}),
                dcc.RadioItems(
                    id='radio_items',
                    labelStyle={"display": "inline-block"},
                    value='créé',
                    options=[{'label': i, 'value': i} for i in montant['etat'].unique()],
                    style={'text-align': 'center', 'color': 'white'},
                    className='dcc_compon'
                ),
                html.Div(
                    children=[
                        dcc.RadioItems(
                            id='radio_items1',
                            labelStyle={"display": "inline-block"},
                            value='montant',
                            options=[{'label': 'fournisseur', 'value': 'montant'}],
                            style={'text-align': 'center', 'color': 'white'},
                            className='dcc_compon'
                        ),
                        html.P("Nombre de fournisseurs à afficher :", style={'color': 'white'}),
                        dcc.Slider(
                            id='supplier_slider',
                            min=1,
                            max=10,
                            step=2,
                            value=5,
                            marks={i: str(i) for i in range(1, len(montant['fournisseur'].unique()) + 1)}
                        )
                    ],
                    className='create_container2'
                )
            ],
            className="one-third column",
            id="title1"
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id='bar-chart')
                    ],
                    style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '40%'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(id='pie-chart')
                    ],
                    style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '36%'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(id='pie-chart1')
                    ],
                    style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '33%'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(id='line-chart')
                     ],
                    style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '49%'}
                ),
              
            ],
        
            className="six columns"
        )
    ]
)


# Définir la logique de mise à jour du graphique en fonction des entrées de l'utilisateur pour le bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('select_year', 'value'),
     Input('radio_items', 'value'),
     Input('supplier_slider', 'value')]
)
def update_bar_graph(selected_year, selected_state, selected_suppliers):
    filtered_data = montant[(montant['date'].dt.year == selected_year) & (montant['etat'] == selected_state)]
    top_suppliers = filtered_data.groupby('fournisseur')['montant'].sum().sort_values(ascending=True).head(selected_suppliers).reset_index()
    bar_fig = px.bar(top_suppliers, x='montant', y='fournisseur', title=f'Montant par fournisseur en {selected_year} ({selected_state})')
    bar_fig.update_layout(
        plot_bgcolor='rgb(25,25,112)',  # Couleur de fond
        paper_bgcolor='rgb(25,25,112)',  # Couleur de fond du papier
        xaxis=dict(
            tickfont=dict(color='white'),  # Couleur du texte sur l'axe des x
            title=dict(font=dict(color='white'))  # Couleur du titre de l'axe des x
        ),
        yaxis=dict(
            tickfont=dict(color='white'),  # Couleur du texte sur l'axe des y
            title=dict(font=dict(color='white'))  # Couleur du titre de l'axe des y
        ),
        title=dict(
            font=dict(color='white')  # Couleur du titre du graphique
        )
    )
    return bar_fig

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('select_year', 'value'),
     Input('radio_items', 'value')]
)
def update_pie_graph_percentage(selected_year, selected_state):
    filtered_data = montant[(montant['date'].dt.year == selected_year) & (montant['etat'] == selected_state)]
    pie_fig = px.pie(filtered_data, names='type', title=f'Pourcentage des types de fournisseurs en {selected_year} ({selected_state})')
    pie_fig.update_layout(
        plot_bgcolor='rgb(25,25,112)',  # Couleur de fond
        paper_bgcolor='rgb(25,25,112)',  # Couleur de fond du papier
       
  # Couleur de fond du papier
        xaxis=dict(
            tickfont=dict(color='white')  # Couleur du texte sur l'axe des x
        ),
        yaxis=dict(
            tickfont=dict(color='white')  # Couleur du texte sur l'axe des y
        ),
        title=dict(
            font=dict(color='white')  # Couleur du titre
        ),
        legend=dict(
            title=dict(font=dict(color='white')),  # Couleur du titre de la légende
            font=dict(color='white')  # Couleur du texte de la légende
        )
    )   
    pie_fig.update_traces(
        textinfo='percent+label',
        insidetextorientation='radial',
        textfont=dict(color='white')  # Couleur du texte des pourcentages
    )
    return pie_fig

@app.callback(
    Output('pie-chart1', 'figure'),
    [Input('select_year', 'value')]
)
def update_pie_graph_total(selected_year):
    try:
        filtered_data = montant[(montant['date'].dt.year == selected_year)]
        total_amount_by_state = filtered_data.groupby('etat')['montant'].sum().reset_index()
        pie_fig1 = px.pie(total_amount_by_state, values='montant', names='etat', title=f'Montant total par état en {selected_year}')
        pie_fig1.update_layout(
            plot_bgcolor='rgb(25,25,112)',  # Couleur de fond
            paper_bgcolor='rgb(25,25,112)',  # Couleur de fond du papier
            font=dict(color='white')  # Couleur du texte
        )
        return pie_fig1
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique à secteurs : {str(e)}")
        return go.Figure()
    
@app.callback(
    Output('line-chart', 'figure'),
    [Input('select_year', 'value')]
)
def update_line_graph(selected_year):
    try:
        filtered_data = montant[montant['date'].dt.year == selected_year]
        monthly_amount = filtered_data.groupby(filtered_data['date'].dt.month)['montant'].sum().reset_index()
        line_fig = px.line(monthly_amount, x='date', y='montant', title=f'Évolution mensuelle des montants en {selected_year}')
        line_fig.update_layout(
            plot_bgcolor='rgb(25,25,112)',  # Couleur de fond
            paper_bgcolor='rgb(25,25,112)',  # Couleur de fond du papier
            xaxis=dict(
                tickfont=dict(color='white'),  # Couleur du texte sur l'axe des x
                title=dict(font=dict(color='white'))
            ),
            yaxis=dict(
                tickfont=dict(color='white'),  # Couleur du texte sur l'axe des y
                title=dict(font=dict(color='white'))
            ),
            title=dict(
                font=dict(color='white')  # Couleur du titre
            ),
            legend=dict(
                title=dict(font=dict(color='white')),  # Couleur du titre de la légende
                font=dict(color='white')  # Couleur du texte de la légende
            )
        )
        return line_fig
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique à lignes : {str(e)}")
        return go.Figure()


if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
