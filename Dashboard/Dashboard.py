import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt
import pyodbc
import plotly.express as px
import traceback
from dash import dash_table


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
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=['assets/style1.css'])

num_invoices = len(montant)
total_amount = montant['montant'].sum()
total_types = montant['type'].nunique()

app.layout = html.Div(style={'background-color': 'rgb(25,25,112)', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'}, children=[
    html.H3('InvoiceBot', style={'color': 'white', 'text-align': 'left', 'font-family': "inherit", "font-size": "30px", "margin-bottom": "20px", "margin-left": "20px"}),
    html.Div(style={'width': '65%', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'}, children=[
        html.Div(children=[
            html.P('État', style={'color': 'white', 'font-size': '25px', 'text-align': 'center'}), 
            dcc.RadioItems(
                id='radio_items',
                labelStyle={"display": "inline-block"},
                value='tous',
                options=[{'label': 'Tous', 'value': 'tous'}] + [{'label': i, 'value': i} for i in montant['etat'].unique()],
                style={'color': 'white', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'gap': '2px'},
                inputStyle={"margin-right": "5px"}  # Adding this line to reduce space between name and radio buttons
            ),
        ], style={'flex': '1'}),
        html.Div(children=[
            html.P('Année',  style={'color': 'white', 'font-size': '20px', 'text-align': 'left','height': '10px'}),
            html.Div(dcc.Checklist(
                id='select_year',
                options=[
                    {'label': '2022', 'value': 2022},
                    {'label': '2023', 'value': 2023}
                ],
                value=[2022, 2023],  # Définir les valeurs initiales pour 2022 et 2023 sélectionnées
                className='dcc_compon1',
            ), style={'width': '100%', 'margin': 'auto', 'padding': '10px 0', 'margin-bottom': '20px'}),  # Ajuster la largeur de la liste et la centrer
        ], style={'flex': '1'}),
        html.Div(children=[  # Ajoutez la liste déroulante pour le filtre du mois
            html.P('Mois', style={'color': 'white', 'font-size': '20px', 'text-align': 'left','height': '10px'}),
            dcc.Dropdown(
                id='select_month',
                options=[
                    {'label': 'Janvier', 'value': 1},
                    {'label': 'Février', 'value': 2},
                    {'label': 'Mars', 'value': 3},
                    {'label': 'Avril', 'value': 4},
                    {'label': 'Mai', 'value': 5},
                    {'label': 'Juin', 'value': 6},
                    {'label': 'Juillet', 'value': 7},
                    {'label': 'Août', 'value': 8},
                    {'label': 'Septembre', 'value': 9},
                    {'label': 'Octobre', 'value': 10},
                    {'label': 'Novembre', 'value': 11},
                    {'label': 'Décembre', 'value': 12},
                ],
                value=list(range(1, 1)),  # Ajustez la valeur par défaut selon vos besoins
                multi=True,  # Pour autoriser la sélection multiple des mois
                className='dcc_compon1'
            ),
        ],  style={'width': '20%', 'margin': 'auto', 'padding': '10px 0', 'margin-bottom': '20px'}), # Ajuster la largeur de la liste et la centrer
    ]),
    html.Div(style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', 'margin-bottom': '20px'}, children=[
        html.P("Nombre de fournisseurs ou de types", style={'font-size': '20px','color': 'white', 'text-align': 'center', 'margin-bottom': '10px', 'margin-left': '590px'}),  
        html.Div(style={'width': '100%', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'}, children=[
            # Ajout des cartes graphiques pour le nombre d'invoices et le montant total
            html.Div(
                style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between','margin-right': '150px','margin-top': '-70px'},
                children=[
                    html.Div(
                        style={'background-color': 'rgb(25,25,112)', 'color': 'white', 'padding': '20px', 'border-radius': '10px', 'flex': '1', 'margin-left': '20px', 'text-align': 'center','font-size': '14px'},
                        children=[
                            html.H4('invoices'),
                            html.H2(f'{num_invoices}')
                        ]
                    ),
                    html.Div(
                        style={'background-color': 'rgb(25,25,112)', 'color': 'white', 'padding': '20px', 'border-radius': '10px', 'flex': '1', 'margin-left': '20px', 'text-align': 'center','font-size': '14px'},
                        children=[
                            html.H4('Montant total'),
                            html.H2(f'{total_amount}')
                        ]
                    ),
                    html.Div(
                        style={'background-color': 'rgb(25,25,112)', 'color': 'white', 'padding': '20px', 'border-radius': '10px', 'flex': '1', 'margin-left': '20px', 'text-align': 'center','font-size': '14px'},
                        children=[
                            html.H4('types'),
                            html.H2(f'{total_types}')  # Mettez la valeur totale des types ici
                        ]
                    )
                ]
            ),
            html.Div(dcc.Dropdown(
            id='supplier_dropdown',
            options=[{'label': str(i), 'value': i} for i in range(1, 11)],
            value=5,
            multi=False,  # Sélection unique
            searchable=False,  # Désactiver la recherche
            ), style={'width': '20%', 'margin': 'auto', 'padding': '10px', 'margin-bottom': '10px','flex': '1'})
        ]),
    ]),
    dcc.RadioItems(
        id='radio_items1',
        labelStyle={"display": "inline-block"},
        value='fournisseur',
        options=[{'label': 'Fournisseur', 'value': 'fournisseur'}, {'label': 'Type', 'value': 'type'}],
        style={'text-align': 'left', 'color': 'white'},
        className='dcc_compon'
    ), 

    html.Div(
        className="six columns",
        children=[
            html.Div(
                children=[
                    html.Button('Masquer/Afficher Bar Chart', id='toggle-bar-chart-button', n_clicks=0),
                    dcc.Graph(id='bar-chart')
                ],
                style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '47%'}
            ),
            html.Div(
                children=[
                    html.Button('Masquer/Afficher Pie Chart', id='toggle-pie-chart-button', n_clicks=0),
                    dcc.Graph(id='pie-chart')
                ],
                style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '38%'}
            ),
            html.Div(
                children=[
                    html.Button('Masquer/Afficher Pie Chart 1', id='toggle-pie-chart1-button', n_clicks=0),
                    dcc.Graph(id='pie-chart1')
                ],
                style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '36%'}
            ),
            html.Div(
                children=[
                    html.Button('Masquer/Afficher Line Chart', id='toggle-line-chart-button', n_clicks=0),
                    dcc.Graph(id='line-chart')
                 ],
                style={'border': '2px solid white', 'margin': '5px', 'flex': '1', 'display': 'inline-block', 'width': '49%'}
            ),              
        ],        
    )
])


# Callbacks pour mettre à jour les graphiques
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('radio_items', 'value'),
     Input('radio_items1', 'value'),
     Input('supplier_dropdown', 'value')]
)
def update_bar_graph(selected_years, selected_months, selected_state, selected_radio, selected_suppliers):
    try:
        if not selected_months:
            selected_months = list(range(1, 13))

        filtered_data = montant[
            montant['date'].dt.year.isin(selected_years) & 
            montant['date'].dt.month.isin(selected_months)
        ]
    
        if selected_state == 'tous':
            filtered_data = filtered_data
        else:
            filtered_data = filtered_data[filtered_data['etat'] == selected_state]
    
        if selected_radio == 'fournisseur':
            top_suppliers = filtered_data.groupby('fournisseur')['montant'].sum().sort_values(ascending=True).tail(selected_suppliers).reset_index()
            bar_fig = px.bar(top_suppliers, x='montant', y='fournisseur', title=f'Montant par fournisseur en {", ".join(map(str, selected_years))} ({selected_state})')
        else:
            top_types = filtered_data.groupby('type')['montant'].sum().sort_values(ascending=True).tail(selected_suppliers).reset_index()
            bar_fig = px.bar(top_types, x='montant', y='type', title=f'Montant par type en {", ".join(map(str, selected_years))} ({selected_state})')
        
        bar_fig.update_layout(
            plot_bgcolor='rgb(25,25,112)',
            paper_bgcolor='rgb(25,25,112)',
            xaxis=dict(
                tickfont=dict(color='white'),
                title=dict(font=dict(color='white'))
            ),
            yaxis=dict(
                tickfont=dict(color='white'),
                title=dict(font=dict(color='white'))
            ),
            title=dict( 
                font=dict(color='white')
            )
        )
        return bar_fig
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique à barres : {str(e)}")
        return go.Figure()



@app.callback(
    Output('pie-chart', 'figure'),
    [Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('radio_items', 'value')]
)
def update_pie_graph_percentage(selected_years, selected_months, selected_state):
    try:
        if not selected_months:  # Si aucun mois n'est sélectionné, utiliser tous les mois de l'année
            selected_months = list(range(1, 13))  # Liste des mois de janvier à décembre
        
        filtered_data = montant[
            montant['date'].dt.year.isin(selected_years) & 
            montant['date'].dt.month.isin(selected_months)  
        ]  

        if selected_state == 'tous':  
            filtered_data = filtered_data
        else:
            filtered_data = filtered_data[filtered_data['etat'] == selected_state]
        
        total_montant = filtered_data['montant'].sum()
        filtered_data['percentage'] = filtered_data['montant'] / total_montant * 100
        filtered_data = filtered_data[filtered_data['percentage'] > 1]
        
        pie_fig = px.pie(filtered_data, names='type', values='percentage', title=f'Pourcentage des types de fournisseurs en {", ".join(map(str, selected_years))} ({selected_state})')
        pie_fig.update_layout(
            plot_bgcolor='rgb(25,25,112)',  
            paper_bgcolor='rgb(25,25,112)',  
            xaxis=dict(
                tickfont=dict(color='white')  
            ),
            yaxis=dict(
                tickfont=dict(color='white')  
            ),
            title=dict(
                font=dict(color='white')  
            ),
            legend=dict(
                title=dict(font=dict(color='white')),  
                font=dict(color='white')  
            )
        )   
        pie_fig.update_traces(
            textinfo='percent+label',
            insidetextorientation='radial',
            textfont=dict(color='white')  
        )
        return pie_fig
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique circulaire : {str(e)}")
        return go.Figure()



@app.callback(
    Output('pie-chart1', 'figure'),
    [Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('radio_items', 'value')]
)
def update_pie_graph_total(selected_years, selected_months, selected_state):
    try:
        if not selected_months:  # Si aucun mois n'est sélectionné, utiliser tous les mois de l'année
            selected_months = list(range(1, 13))  # Liste des mois de janvier à décembre
        
        filtered_data = montant[
            montant['date'].dt.year.isin(selected_years) & 
            montant['date'].dt.month.isin(selected_months)  
        ]  

        if selected_state == 'tous':  
            filtered_data = filtered_data
        else:
            filtered_data = filtered_data[filtered_data['etat'] == selected_state]
            
        total_amount_by_state = filtered_data.groupby('etat')['montant'].sum().reset_index()
        pie_fig1 = px.pie(total_amount_by_state, values='montant', names='etat', title=f'Montant total par {selected_state} en {", ".join(map(str, selected_years))}')
        pie_fig1.update_layout(
            plot_bgcolor='rgb(25,25,112)',  
            paper_bgcolor='rgb(25,25,112)',  
            font=dict(color='white')  
        )
        return pie_fig1
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique à secteurs : {str(e)}")
        return go.Figure()
    
@app.callback(
    Output('line-chart', 'figure'),
    [Input('select_year', 'value'),
     Input('select_month', 'value')]
)
def update_line_graph(selected_years, selected_months):
    try:
        if not selected_months:  # Si aucun mois n'est sélectionné, utiliser tous les mois de l'année
            selected_months = list(range(1, 13))  # Liste des mois de janvier à décembre
        
        filtered_data = montant[
            montant['date'].dt.year.isin(selected_years) & 
            montant['date'].dt.month.isin(selected_months)  
        ]  

        monthly_amount = filtered_data.groupby(filtered_data['date'].dt.month)['montant'].sum().reset_index()
        line_fig = px.line(monthly_amount, x='date', y='montant', title=f'Évolution mensuelle des montants en {", ".join(map(str, selected_years))}')
        line_fig.update_layout(
            plot_bgcolor='rgb(25,25,112)',  
            paper_bgcolor='rgb(25,25,112)',  
            xaxis=dict(
                tickfont=dict(color='white'),  
                title=dict(font=dict(color='white'))
            ),
            yaxis=dict(
                tickfont=dict(color='white'),  
                title=dict(font=dict(color='white'))
            ),
            title=dict(
                font=dict(color='white')  
            ),
            legend=dict(
                title=dict(font=dict(color='white')),  
                font=dict(color='white')  
            )
        )
        return line_fig
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique en ligne : {str(e)}")
        return go.Figure()

@app.callback(
    Output('bar-chart', 'style'),
    [Input('toggle-bar-chart-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_bar_chart(n_clicks):
    if n_clicks % 2 == 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('pie-chart', 'style'),
    [Input('toggle-pie-chart-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_pie_chart(n_clicks):
    if n_clicks % 2 == 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('pie-chart1', 'style'),
    [Input('toggle-pie-chart1-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_pie_chart1(n_clicks):
    if n_clicks % 2 == 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('line-chart', 'style'),
    [Input('toggle-line-chart-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_line_chart(n_clicks):
    if n_clicks % 2 == 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True, port=8053)