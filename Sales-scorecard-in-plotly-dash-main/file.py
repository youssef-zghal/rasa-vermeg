import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from dash import dash_table as dt
from dash import dcc, html, callback_context
from dash import dcc, html, State
import plotly.graph_objs as go
import pyodbc
import plotly.express as px
from dash.exceptions import PreventUpdate
from flask import Flask, request, jsonify
import requests
import warnings
# Suppress specific warnings from pandas
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

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
options_fournisseurs = [{'label': str(fournisseur_), 'value': str(fournisseur_)} for fournisseur_ in fournisseurs_df['Fournisseur']]

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
user_cleared_selection = False
supplier_name = None

# ---------------------------------------------------------------------------------------------------------------------------------
flask_app = Flask(__name__, static_folder='static')
app = dash.Dash(__name__, server=flask_app, meta_tags=[{"name": "viewport", "content": "width=device-width"}], suppress_callback_exceptions=True)

@flask_app.route('/', methods=['POST'])
def update_supplier():
    global supplier_name
    data = request.get_json()
    supplier_name = data.get('fournisseur')
    print("Données reçues:", data)
    return jsonify({'message': 'Fournisseur mis à jour'})



app.layout = html.Div((
 
    html.Div([
        html.Div([
        html.Img(src='/static/bot-removebg.png', style={'width': '100px', 'height': '100px'}),
        # html.H1('InvoiceBot', style={'margin-top': '40px'}),
        ], className="one-third column", id="title1"),

        html.Div([
              html.Div(id='text1'),
        ], className="create_container2 one-third column", id='title5'),
        html.Div([
              html.Div(id='text2'),
        ], className="create_container2 one-third column", id='title6'),
        html.Div([
              html.Div(id='text3'),
        ], className="create_container2 one-third column", id='title7'),
        html.Div([
              html.Div(id='text4'),
        ], className="create_container2 one-third column", id='title8'),


    ], id = "header", className = "row flex-display"),

html.Div([
    html.Div([
        html.P('Factures', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(id='dropdown_Factures',
                 options=options_factures,
                 value=None,
                 multi=True,   # Valeur par défaut
                 style={'color': 'black'}, className='dcc_compon'),

        dcc.Store(id='supplier_store'),
        dcc.Store(id='reset_store'),
            dcc.Store(id='user_cleared_selection_store', data=False) ,

  # Store component for supplier name
        dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),  
        html.P('Fournisseurs', className='fix_label', style={'color': 'white','margin-left': '20px'}),
         dcc.Dropdown(id='dropdown_fournisseurs',
                 options=options_fournisseurs,
                 value=None,  # Valeur par défaut
                 multi=True,
                 style={'color': 'black'}, className='dcc_compon'),
        html.P('Types', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(id='dropdown_types',
                 options=options_types,
                 value=None,
                 multi=True,   # Valeur par défaut
                 style={'color': 'black'}, className='dcc_compon'),
        html.P('Etats', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(id='dropdown_items',
                options=options,
                value=[],  # valeurs sélectionnées par défaut
                multi=True,
                style={'color': 'black'}, className='dcc_compon',  # Permet la sélection multiple
            ),
            html.Div([
            html.P('Année', className='fix_label', style={'color': 'white','margin-left': '20px'}),
            dcc.Dropdown(
                id='select_year',
                options=[{'label': str(yr), 'value': yr} for yr in range(2021, 2024)],
                value=[],
                multi=True,  # Permet la sélection multiple
                className='dcc_compon'
            ),
        ], style={'margin-top': '0px'}),
        html.P('Mois', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(
            id='select_month',
            options=[
                {'label': 'January', 'value': 1},
                {'label': 'February', 'value': 2},
                {'label': 'March', 'value': 3},
                {'label': 'April', 'value': 4},
                {'label': 'May', 'value': 5},
                {'label': 'June', 'value': 6},
                {'label': 'July', 'value': 7},
                {'label': 'August', 'value': 8},
                {'label': 'September', 'value': 9},
                {'label': 'October', 'value': 10},
                {'label': 'November', 'value': 11},
                {'label': 'December', 'value': 12}
            ],
            value=None,  # Sélectionner le mois par défaut
            multi=True,  
            className='dcc_compon'
        ),
        html.P('Top', className='fix_label', style={'color': 'white','margin-left': '20px'}),
        dcc.Dropdown(
        id='top_list_slider',
        options=[{'label': str(i), 'value': i} for i in range(1, 136)],
        value=None,    
        clearable=False, 
        style={'color': 'black'}, className='dcc_compon', # Pour empêcher de vider la liste déroulante
    ),
        dcc.Link(html.Button('Afficher Base De Donnée',id='afficher_button', style={'margin-top':'18px', 'text-align': 'center', 'font-size': '11px','margin-left': '20px'}), href='/'),  # Ajouter un href pour le lien
        dcc.Store(id='bouton_clicke', data=False),  # Pour suivre l'état du bouton
    ], className='dcc_compon one columns', style={'width': '200px' , 'margin-right':'110px'}),

# -----------------------------------------------------------------
html.Div([
    dt.DataTable(id='my_datatable',
                columns=[{'name': i, 'id': i} for i in
                        montant.loc[:, ['Facture','fournisseur','montant','etat','type', 'date_substr']]],
                  sort_action="native",
                  sort_mode="multi",
                  style_table={
                          "width": "100%",
                          "height": "1000px"},
                  virtualization=True,
                  style_cell={'textAlign': 'left',
                              'min-width': '100px',
                              'backgroundColor': '#1f2c56',
                              'color': '#FEFEFE',
                              'border-bottom': '0.01rem solid #19AAE1',
                              },
                  style_as_list_view=True,
                  style_header={
                    'backgroundColor': '#1f2c56',
                    'fontWeight': 'bold',
                    'font': 'Lato, sans-serif',
                    'color': 'orange',
                    'border': '#1f2c56',
                },
                style_data={'textOverflow': 'hidden', 'color': 'white'},
                fixed_rows={'headers': True},
                )
], className='create_container2 nine columns', style={'height': '700px'}, id='Block_div5'),


# -----------------------------------------------------------------
    
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
        ], className='create_container2 six-third columns', style={'height': '350px'}, id='Block_div1'),

        # Deuxième graphique donut chart
        html.Div([
            html.Button('Aggrandir', id='aggrandir_button2', n_clicks=0, style={'position': 'absolute', 'top': '8px', 'left': '8px'}),
            dcc.Store(id='state_aggrandir2', data=False),
            dcc.Graph(
                id='donut_chart',
                config={'displayModeBar': 'hover'},
                style={'height': '280px', 'padding-top': '38px'}
            ),
        ], className='create_container2 six-third  columns', style={'height': '350px'}, id='Block_div2'),
    ], className="row flex-display"),

    # Deuxième ligne
    html.Div([
        # Troisième graphique pie chart
        html.Div([
            html.Button('Aggrandir', id='aggrandir_button3', n_clicks=0, style={'position': 'absolute', 'top': '6px', 'left': '6px'}),
            dcc.Store(id='state_aggrandir3', data=False),
            dcc.Graph(
                id='pie_chart',
                config={'displayModeBar': 'hover'},
                style={'height': '280px', 'padding-top': '38px'}
            ),
        ], className='create_container2 six-third  columns', style={'height': '350px'}, id='Block_div3'),

        # Quatrième graphique line chart
        html.Div([
            html.Button('Aggrandir', id='aggrandir_button4', n_clicks=0, style={'position': 'absolute', 'top': '8px', 'left': '8px'}),
            dcc.Store(id='state_aggrandir4', data=False),
            dcc.Graph(
                id='line_chart',
                config={'displayModeBar': 'hover'},
                style={'height': '300px', 'padding-top': '38px'}
            ),
        ], className='create_container2 six-third  columns', style={'height': '350px'}, id='Block_div4'),
    ], className="row flex-display"),
], id="mainContainer", style={"display": "flex", "flex-direction": "column"})

])
))
# -------------------BOUTTON!!!!!!----------------------------------------
# Callback pour mettre à jour l'état du bouton lorsque le bouton est cliqué
@app.callback(Output('bouton_clicke', 'data'),
              [Input('afficher_button', 'n_clicks')],
              [State('bouton_clicke', 'data')])
def update_button_state(n_clicks, current_state):
    if n_clicks:
        return not current_state
    return current_state
# Callbacks pour mettre à jour les graphiques en fonction de l'état du bouton
@app.callback(
    [Output('Block_div1', 'style'),
     Output('Block_div2', 'style'),
     Output('Block_div3', 'style'),
     Output('Block_div4', 'style'),
     Output('Block_div5', 'style'),
     Output('afficher_button', 'children')],
    [Input('bouton_clicke', 'data')]
)
def update_graph_visibility(button_state):
    button_text = "Retourner à La Dashboard" if button_state else "Afficher Base De Donnée"
    if button_state:
        return [{'display': 'none'}] * 4 + [{'display': 'block'}, button_text]
    # Sinon, afficher les Block_div sauf Block_div5
    return [{'display': 'block'}] * 4 + [{'display': 'none'}, button_text]

# ------------------------------------------------------------------
# Callback pour contrôler l'état d'agrandissement des graphiques

@app.callback(
    [Output('bar_chart1', 'style'),
     Output('donut_chart', 'style'),
     Output('pie_chart', 'style'),
     Output('line_chart', 'style')],
    [Input('aggrandir_button1', 'n_clicks'),
     Input('aggrandir_button2', 'n_clicks'),
     Input('aggrandir_button3', 'n_clicks'),
     Input('aggrandir_button4', 'n_clicks')],
    [State('bar_chart1', 'style'),
     State('donut_chart', 'style'),
     State('pie_chart', 'style'),
     State('line_chart', 'style')]
)
def toggle_graph_visibility(n_clicks1, n_clicks2, n_clicks3, n_clicks4, style_bar, style_donut, style_pie, style_line):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'aggrandir_button1':
        if n_clicks1 % 2 == 1:
            return [{'height': '600px', 'padding-top': '27px'}, style_donut, style_pie, style_line]
        else:
            return [{'height': '280px', 'padding-top': '27px'}, style_donut, style_pie, style_line]
    elif button_id == 'aggrandir_button2':
        if n_clicks2 % 2 == 1:
            return [style_bar, {'height': '600px', 'padding-top': '38px'}, style_pie, style_line]
        else:
            return [style_bar, {'height': '280px', 'padding-top': '38px'}, style_pie, style_line]
    elif button_id == 'aggrandir_button3':
        if n_clicks3 % 2 == 1:
            return [style_bar, style_donut, {'height': '600px', 'padding-top': '38px'}, style_line]
        else:
            return [style_bar, style_donut, {'height': '280px', 'padding-top': '38px'}, style_line]
    elif button_id == 'aggrandir_button4':
        if n_clicks4 % 2 == 1:
            return [style_bar, style_donut, style_pie, {'height': '600px', 'padding-top': '38px'}]
        else:
            return [style_bar, style_donut, style_pie, {'height': '300px', 'padding-top': '38px'}]
    else:
        return [style_bar, style_donut, style_pie, style_line]

# -------------------------------------------------------------------
@app.callback(
    Output('bar_chart1', 'figure'),
    [
        Input('select_year', 'value'),
        Input('select_month', 'value'),
        Input('radio_items1', 'value'),
        Input('top_list_slider', 'value'),
        Input('dropdown_fournisseurs', 'value'),
        Input('dropdown_types', 'value'),
        Input('dropdown_items', 'value'),
        Input('dropdown_Factures', 'value')  # Add the dropdown for invoices as an input
    ]
)
def update_graph(select_years, select_months, radio_items1, top_count, fournisseur_value, type_value, dropdown_value, selected_invoices):
    # Initialize filtered_df
    filtered_df = montant
    
    # Filter data based on selected_invoices
    if selected_invoices is not None and selected_invoices != []:
        filtered_df = filtered_df[filtered_df['Facture'].isin(selected_invoices)]
    
    # Filter data based on selected years
    if select_years:
        filtered_df = filtered_df[filtered_df['date'].dt.year.isin(select_years)]
    
    # Filter data based on selected months
    if select_months:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_months)]
    
    # Filter data based on dropdown values
    if dropdown_value is not None and dropdown_value != []:
        filtered_df = filtered_df[filtered_df['etat'].isin(dropdown_value)]
    
    # Check if 'fournisseur_value' is a string and if so, convert it to a list
    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]
    
    # Apply filter for 'fournisseur_value' if it is not empty
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]
    
    # Apply additional filters or calculations as necessary
    if not top_count:
        top_count = 5  # Default to top 5 if no count provided

    if radio_items1 == 'fournisseur':
        # Group by 'fournisseur' and sum 'montant'
        sales1 = filtered_df.groupby(['fournisseur'])['montant'].sum().reset_index()
        # Get top 'top_count' entries sorted by 'montant'
        sales2 = sales1.sort_values(by='montant', ascending=False).head(top_count)

        return {
            'data': [go.Bar(
                x=sales2['montant'],
                y=sales2['fournisseur'],
                text=sales2['montant'],
                texttemplate='%{text:.2s} DT',
                textposition='auto',
                orientation='h',
                marker=dict(color='#19AAE1'),

                hoverinfo='text',
                hovertext=
                '<b>Year</b>: ' + ', '.join(str(year) for year in select_years) + '<br>' +
                '<b>Fournisseur</b>: ' + sales2['fournisseur'].astype(str) + '<br>' +
                '<b>Montant</b>:' + [f'{x:,.2f}' for x in sales2['montant']]+' DT' + '<br>'

            )],

            'layout': go.Layout(
                plot_bgcolor='#1f2c56',
                paper_bgcolor='#1f2c56',
                title={
                    'text': 'Achats Par Fournisseur En: ' + ', '.join(str(year) for year in select_years),
                    'y': 0.99,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                titlefont={
                    'color': 'white',
                    'size': 15},

                hovermode='closest',
                margin=dict(t=40, r=0),

                xaxis=dict(title='<b></b>',
                           color='orange',
                           showline=True,
                           showgrid=True,
                           showticklabels=True,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Arial',
                               size=12,
                               color='orange')
                           ),

                yaxis=dict(title='<b></b>',
                           autorange='reversed',
                           color='orange',
                           showline=False,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Arial',
                               size=10,
                               color='orange')
                           ),

                legend={
                    'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'x': 0.5,
                    'y': 1.25,
                    'xanchor': 'center',
                    'yanchor': 'top'},

                font=dict(
                    family="sans-serif",
                    size=15,
                    color='white'),


            )
        }
    elif radio_items1 == 'type':
        if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]
        sales3 = filtered_df.groupby(['type'])['montant'].sum().reset_index()
        sales4 = sales3.sort_values(by=['montant'], ascending=False).nlargest(top_count, columns=['montant'])

        return {
            'data': [go.Bar(
                x=sales4['montant'],
                y=sales4['type'],
                text=sales4['montant'],
                texttemplate=  '%{text:.2s} DT',
                textposition='auto',
                orientation='h',
                marker=dict(color='#19AAE1'),

                hoverinfo='text',
                hovertext=
                '<b>Year</b>: ' + ', '.join(str(year) for year in select_years) + '<br>' +
                '<b>Type</b>: ' + sales4['type'].astype(str) + '<br>' +
                '<b>Montant</b>:' + [f'{x:,.2f}' for x in sales4['montant']]+' DT' + '<br>'

            )],

            'layout': go.Layout(
                plot_bgcolor='#1f2c56',
                paper_bgcolor='#1f2c56',
                title={
                    'text': 'Achats Par Type En ' + ', '.join(str(year) for year in select_years),

                    'y': 0.99,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                titlefont={
                    'color': 'white',
                    'size': 12},

                hovermode='closest',
                margin=dict(t=40, r=0),

                xaxis=dict(title='<b></b>',
                           color='orange',
                           showline=True,
                           showgrid=True,
                           showticklabels=True,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Arial',
                               size=12,
                               color='orange')
                           ),

                yaxis=dict(title='<b></b>',
                           autorange='reversed',
                           color='orange',
                           showline=False,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Arial',
                               size=12,
                               color='orange')
                           ),

                legend={
                    'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'x': 0.5,
                    'y': 1.25,
                    'xanchor': 'center',
                    'yanchor': 'top'},

                font=dict(
                    family="sans-serif",
                    size=15,
                    color='white'),
            )
        }



@app.callback(Output('donut_chart', 'figure'),
             [Input('select_year', 'value')],
             [Input('select_month', 'value')],
             [Input('dropdown_fournisseurs', 'value')],
             [Input('dropdown_types', 'value')])
def update_graph(select_year, select_month, fournisseur_value, type_value):

    if not select_year:
        filtered_df = montant
    else:
        # Filtrer les données en fonction des années sélectionnées
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    # Si un fournisseur est sélectionné, filtrer les données en fonction de ce fournisseur
        if fournisseur_value is not None and fournisseur_value != []:
            filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]

    # Si un type est sélectionné, filtrer les données en fonction de ce type
        if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]
    
    # Calculer les montants par état
    etat_amounts = filtered_df.groupby('etat')['montant'].sum().reset_index()

    
    # Créer le graphique Donut
    colors = ['#30C9C7', '#7A45D1', 'orange']
    fig = go.Figure(data=[go.Pie(
        labels=etat_amounts['etat'],
        values=etat_amounts['montant'],
        marker=dict(colors=colors),
        hoverinfo='label+value+percent',
        textinfo='label+value',
        textfont=dict(size=13),
        texttemplate='%{label} <br>%{value:,.2f} DT',
        textposition='auto',
        hole=0.7,
        rotation=160,
        insidetextorientation='radial',
    )])

    fig.update_layout(
        plot_bgcolor='#1f2c56',
        paper_bgcolor='#1f2c56',
        hovermode='x',
        title={
            'text': f'Etats par année: {", ".join(str(year) for year in select_year)}',
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        titlefont={
            'color': 'white',
            'size': 15
        },
        legend={
            'orientation': 'h',
            'bgcolor': '#1f2c56',
            'xanchor': 'center',
            'x': -0.2,
            'y': -0.15
        },
        font=dict(
            family="sans-serif",
            size=12,
            color='white'
        )
    )

    return fig



@app.callback(
    Output('text1', 'children'),
    [Input('dropdown_items', 'value'),
     Input('dropdown_fournisseurs', 'value'),
     Input('dropdown_types', 'value'),
     Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('dropdown_Factures', 'value')]
)
def update_text(dropdown_value, fournisseur_value, type_value,select_year, select_month,selected_invoices):
    # Filtrer les données en fonction des valeurs sélectionnées
    filtered_df = montant

    if selected_invoices is not None and selected_invoices != []:
        # Filter data based on selected_invoices
        filtered_df = montant[montant['Facture'].isin(selected_invoices)]

    if select_year:
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    # Check if 'fournisseur_value' is a string and if so, convert it to a list
    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]


    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]

    # Si des valeurs sont sélectionnées dans la liste déroulante, filtrer les données en fonction de ces valeurs
    if dropdown_value:
        filtered_df = filtered_df[filtered_df['etat'].isin(dropdown_value)]

    # Nombre de lignes dans la table "montant"
    num_rows = len(filtered_df)
  
    return [
        html.H6(children='Nombre de factures',
                style={'textAlign': 'center','color': 'white' ,'fontSize': '18px'}
        ),

        html.P(num_rows,
               style={'textAlign': 'center',
                      'color': 'orange',
                      'fontSize': 20,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(
    Output('text2', 'children'),
    [Input('dropdown_items', 'value'),
     Input('dropdown_fournisseurs', 'value'),
     Input('dropdown_types', 'value'),
     Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('dropdown_Factures', 'value')]
)
def update_text(dropdown_value, fournisseur_value, type_value,select_year, select_month,selected_invoices):
    # Filtrer les données en fonction des valeurs sélectionnées
    filtered_df = montant

    if selected_invoices is not None and selected_invoices != []:
        # Filter data based on selected_invoices
        filtered_df = montant[montant['Facture'].isin(selected_invoices)]

    if select_year:
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]

    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]

    if dropdown_value:
        filtered_df = filtered_df[filtered_df['etat'].isin(dropdown_value)]

    # Montant total de toute la base
    total_amount = filtered_df['montant'].sum()
    return [
        html.H6(children='Montant total',
                style={'textAlign': 'center', 'color': 'white','fontSize': '18px'}
        ),

        html.P('{0:,.2f} DT'.format(total_amount),
               style={'textAlign': 'center',
                      'color': 'orange',
                      'fontSize': 20,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(
    Output('text3', 'children'),
    [Input('dropdown_items', 'value'),
     Input('dropdown_fournisseurs', 'value'),
     Input('dropdown_types', 'value'),
     Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('dropdown_Factures', 'value')]
)
def update_text(dropdown_value, fournisseur_value, type_value,select_year, select_month,selected_invoices):
    # Filtrer les données en fonction des valeurs sélectionnées
    filtered_df = montant

    if selected_invoices is not None and selected_invoices != []:
        # Filter data based on selected_invoices
        filtered_df = montant[montant['Facture'].isin(selected_invoices)]

    if select_year:
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]

    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]

    if dropdown_value:
        filtered_df = filtered_df[filtered_df['etat'].isin(dropdown_value)]

    # Nombre de types différents
    num_types = filtered_df['type'].nunique()
    
    return [
        html.H6(children='Nombre total des types',
                style={'textAlign': 'center', 'color': 'white','fontSize': '18px'}
        ),

        html.P(num_types,
               style={'textAlign': 'center',
                      'color': 'orange',
                      'fontSize': 20,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(
    Output('text4', 'children'),
    [Input('dropdown_items', 'value'),
     Input('dropdown_fournisseurs', 'value'),
     Input('dropdown_types', 'value'),
     Input('select_year', 'value'),
     Input('select_month', 'value'),
     Input('dropdown_Factures', 'value')]
)
def update_text(dropdown_value, fournisseur_value, type_value,select_year, select_month,selected_invoices):
    # Filtrer les données en fonction des valeurs sélectionnées
    filtered_df = montant

    if selected_invoices is not None and selected_invoices != []:
        # Filter data based on selected_invoices
        filtered_df = montant[montant['Facture'].isin(selected_invoices)]

    if select_year:
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]

    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]

    if dropdown_value:
        filtered_df = filtered_df[filtered_df['etat'].isin(dropdown_value)]

    # Nombre de types différents
    total_fournisseurs = filtered_df['fournisseur'].nunique()
    
    return [
        html.H6(children='Nombre total des Fournisseurs',
                style={'textAlign': 'center', 'color': 'white','fontSize': '18px'}
        ),

        html.P(total_fournisseurs,
               style={'textAlign': 'center',
                      'color': 'orange',
                      'fontSize': 20,
                      'margin-top': '-10px'}
        ),
    ]


import plotly.graph_objs as go

@app.callback(Output('pie_chart', 'figure'),
             [Input('select_year', 'value')],
             [Input('select_month', 'value')],
             [Input('dropdown_fournisseurs', 'value')],
             [Input('dropdown_types', 'value')])
def update_horizontal_bar_chart(select_year, select_month, fournisseur_value, type_value):

    if not select_year:
        filtered_df = montant
    else:
        # Filtrer les données en fonction des années sélectionnées
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    # Calculer les montants par type
    type_amounts = filtered_df.groupby('type')['montant'].sum().reset_index()

    # Calculer le pourcentage des montants par type
    total_amount = type_amounts['montant'].sum()
    type_amounts['percentage'] = (type_amounts['montant'] / total_amount) * 100

    # Filtrer les types avec un pourcentage supérieur à 2%
    type_amounts_filtered = type_amounts[type_amounts['percentage'] > 1]

    # Créer le graphique à secteurs
    colors = ['#30C9C7', '#7A45D1', 'orange']  # Ajouter plus de couleurs si nécessaire
    fig = go.Figure(data=[go.Pie(
        labels=type_amounts_filtered['type'],
        values=type_amounts_filtered['percentage'],
        marker=dict(colors=colors),
        hoverinfo='label+percent',
        textinfo='label+percent',
        textfont=dict(size=13),
        textposition='inside',
        hole=0.4,
    )])

    fig.update_layout(
        plot_bgcolor='#1f2c56',
        paper_bgcolor='#1f2c56',
        hovermode='closest',
        title={
            'text': f'Types par année: {", ".join(str(year) for year in select_year)}',
            'y':0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 15}
        },
        legend={
            'orientation': 'h',
            'bgcolor': '#1f2c56',
            'x': 0.5,
            'y': -0.15,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family="sans-serif",
            size=15,
            color='white'
        ),
        margin=dict(t=40, r=0)  # Ajuster la marge supérieure pour l'affichage du titre
    )

    return fig


@app.callback(Output('line_chart', 'figure'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              [Input('dropdown_fournisseurs', 'value')],
              [Input('dropdown_types', 'value')])
def update_graph(select_year, select_month, fournisseur_value, type_value):

    if not select_year:
        filtered_df = montant
    else:
        # Filtrer les données en fonction des années sélectionnées
        filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]

    # Si un fournisseur est sélectionné, filtrer les données en fonction de ce fournisseur
# Check if 'fournisseur_value' is a string and if so, convert it to a list
    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_df = filtered_df[filtered_df['fournisseur'].isin(fournisseur_value)]


    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_df = filtered_df[filtered_df['type'].isin(type_value)]

    # Regrouper les données par mois et calculer les montants mensuels
    monthly_sales = filtered_df.groupby(filtered_df['date'].dt.to_period("M"))['montant'].sum().reset_index()
    monthly_sales['date'] = monthly_sales['date'].dt.to_timestamp()

    return {
        'data':[
            go.Scatter(
                x=monthly_sales['date'],
                y=monthly_sales['montant'],
                name='Sales',
                mode='lines+markers',
                line=dict(width=3, color='orange'),
                marker=dict(size=10, symbol='circle', color='#19AAE1',
                            line=dict(color='#19AAE1', width=2)
                            ),
                hoverinfo='y+text',
                hovertext=[f'Sales: {sales:.2f}DT' for sales in monthly_sales['montant']],
                textposition='bottom center'
            )],

        'layout': go.Layout(
             plot_bgcolor='#1f2c56',
             paper_bgcolor='#1f2c56',
             title={
                'text': f'Achats Par Année: {", ".join(str(year) for year in select_year)}',
                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                'color': 'white',
                'size': 15},
             hovermode='closest',
             margin=dict(t=50, l=0, r=0),

             xaxis=dict(title='<b>Mois</b>',
                        visible=True,
                        color='orange',
                        showline=True,
                        showgrid=False,
                        showticklabels=True,
                        linecolor='orange',
                        linewidth=1,
                        ticks='outside',
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='orange')
                        ),

             yaxis=dict(title='<b>Montants</b>',
                        visible=True,
                        color='orange',
                        showline=False,
                        showgrid=True,
                        showticklabels=True,
                        linecolor='orange',
                        linewidth=1,
                        ticks='',
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='orange')
                        ),

            legend={
                'orientation': 'h',
                'bgcolor': '#1f2c56',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'
                },

                

            font=dict(
                family="sans-serif",
                size=12,
                color='white'),
        )
    }


@app.callback(
    Output('my_datatable', 'data'),
    [Input('select_year', 'value')],
    [Input('select_month', 'value')],
    [Input('dropdown_fournisseurs', 'value')],
    [Input('dropdown_types', 'value')],
    [Input('dropdown_items', 'value'),
    Input('dropdown_Factures', 'value')]# Ajoutez cette ligne pour inclure le filtre d'état
)
def display_table(select_year, select_month, fournisseur_value, type_value, dropdown_value,selected_invoices):
    
    if not select_year:
        filtered_data = montant
    else:
        # Filtrer les données en fonction des années sélectionnées
        filtered_data = montant[montant['date'].dt.year.isin(select_year)]

    if selected_invoices is not None and selected_invoices != []:
        # Filter data based on selected_invoices
        filtered_data = montant[montant['Facture'].isin(selected_invoices)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_data = filtered_data[filtered_data['date'].dt.month.isin(select_month)]

    # Check if 'fournisseur_value' is a string and if so, convert it to a list
    if isinstance(fournisseur_value, str):
        fournisseur_value = [fournisseur_value]

    # Now use 'fournisseur_value' which is guaranteed to be a list-like object
    if fournisseur_value is not None and fournisseur_value != []:
        filtered_data = filtered_data[filtered_data['fournisseur'].isin(fournisseur_value)]


    # Si un type est sélectionné, filtrer les données en fonction de ce type
    if type_value is not None and type_value != []:
            filtered_data = filtered_data[filtered_data['type'].isin(type_value)]

    # Si un état est sélectionné, filtrer les données en fonction de cet état
    if dropdown_value is not None and dropdown_value != []:  
        # Filtrer les données uniquement si des valeurs sont sélectionnées dans la liste déroulante
        filtered_data = filtered_data[filtered_data['etat'].isin(dropdown_value)]
    else:
        # Utiliser toutes les valeurs d'état si la liste déroulante est vide
        filtered_data = filtered_data
   
    return filtered_data.to_dict('records')



# --------Integration dropdown_fournisseur-------------

@app.callback(
    [Output('supplier_store', 'data'),
     Output('dropdown_fournisseurs', 'options'),
     Output('dropdown_fournisseurs', 'value')],
    [Input('interval-component', 'n_intervals'),
     Input('dropdown_fournisseurs', 'value')],
    [State('supplier_store', 'data')]
)
def update_supplier_store_and_dropdown(n_intervals, selected_supplier, supplier_store):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Si le déclencheur vient de l'intervalle, vérifier si un nouveau fournisseur doit être ajouté
    if triggered_id == 'interval-component':
        if supplier_name and (supplier_name != supplier_store):
            # Si un nouveau fournisseur est détecté, mettre à jour le store et la sélection
            return supplier_name, options_fournisseurs, supplier_name
        else:
            raise PreventUpdate

    # Si le déclencheur vient du dropdown, gérer la sélection/désélection
    elif triggered_id == 'dropdown_fournisseurs':
        if selected_supplier:
            # Si l'utilisateur a sélectionné un fournisseur, mettre à jour le store et garder la sélection
            return supplier_store, options_fournisseurs, selected_supplier
        else:
            # Si l'utilisateur a désélectionné, ne pas forcer une nouvelle sélection
            return supplier_store, options_fournisseurs, None

    # Maintenir l'état actuel si aucune action spécifique n'est nécessaire
    return supplier_store, options_fournisseurs, supplier_store




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8053, debug=True)
