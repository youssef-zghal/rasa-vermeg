import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt
from dash import dcc, html
import plotly.graph_objs as go
import pyodbc
import plotly.express as px


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


# app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=['assets/style1.css'])
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

num_invoices = len(montant)
total_amount = montant['montant'].sum()
total_types = montant['type'].nunique()



# ----------





app.layout = html.Div((

    html.Div([
        # html.Div([
        #     html.Div([
        #         html.H3('InvoiceBot', style = {'margin-bottom': '0px', 'color': 'white'}),
        #     ])
        # ], className = "one third column", id = "title1"),



        html.Div([


        ], className = "one-third column", id = 'title3'),

    ], id = "header", className = "row flex-display", style = {"margin-bottom": "25px"}),

html.Div([
    html.Div([
        dcc.RadioItems(id='radio_items1',
                       labelStyle={"display": "inline-block"},
                       value='fournisseur',  # Définir la valeur par défaut sur fournisseur
                        options=[{'label': 'Fournisseur', 'value': 'fournisseur'},
                                    {'label': 'Type', 'value': 'type'}],  # Ajouter l'option de type
                   
                       style={'text-align': 'center', 'color': 'white'}, className='dcc_compon'),
        dcc.Graph(id='bar_chart1',
                  config={'displayModeBar': 'hover'}, style={'height': '280px'}),

    ], className='create_container2 five columns', style={'height': '330px'}),

    
        html.Div([
            dcc.Graph(id = 'line_chart',
                      config = {'displayModeBar': 'hover'}, style = {'height': '300px'}),

        ], className = 'create_container2 six columns', style = {'height': '330px'}),

        html.Div([
            dcc.Graph(id = 'donut_chart',
                      config = {'displayModeBar': 'hover'}, style = {'height': '280px'}),

        ], className = 'create_container2 six columns', style = {'height': '330px'}),



        html.Div([
              html.Div(id='text1'),
              html.Div(id='text2'),
              html.Div(id='text3'),

         ], className = 'create_container2 one column', style = {'width': '190px','height': '330px'}),



    ], className = "row flex-display"),

    html.Div((
                    html.Div([
            dcc.Graph(id = 'pie_chart',
                    config = {'displayModeBar': 'hover'}, style = {'height': '280px'}),

        ], className = 'create_container2 four columns', style = {'height': '330px'}),
        
html.Div([
    dt.DataTable(id='my_datatable',
                columns=[{'name': i, 'id': i} for i in
                        montant.loc[:, ['Facture','fournisseur','montant','etat','type', 'date_substr'  ]]],
                  sort_action="native",
                  sort_mode="multi",
                  style_table={
                  #         "width": "100%",
                          "height": "330px"},
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
], className='create_container2 five columns', style={'height': '330px'}),
        html.Div([
    html.Div([
                    html.P('Etats', className = 'fix_label', style = {'color': 'white'}),
            dcc.RadioItems(id = 'radio_items',
                           labelStyle = {"display": "inline-block"},
                           value = 'Prét pour paiement',
                           options = options,
                           style = {'text-align': 'center', 'color': 'white'}, className = 'dcc_compon'),
        html.Div([
            html.P('Year', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(
                id='select_year',
                options=[{'label': str(yr), 'value': yr} for yr in range(2020, 2025)],
                value=2023,
                multi=True,  # Permet la sélection multiple
                className='dcc_compon'
            ),
        ], style={'margin-top': '0px'}),
        html.P('Month', className='fix_label', style={'color': 'white'}),
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
            value=1,  # Sélectionner le mois par défaut
            multi=True,  
            className='dcc_compon'
        ),
        
    ], className='create_container2 three columns', style={'width': '400px'}),

], className="row flex-display"),

), className="row flex-display"),

), id="mainContainer", style={"display": "flex", "flex-direction": "column"})



@app.callback(Output('bar_chart1', 'figure'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              [Input('radio_items1', 'value'),
               Input('radio_items', 'value')])
def update_graph(select_years, select_months, radio_items1, radio_items):
    # Convertir select_years en liste si ce n'est pas déjà le cas
    if not isinstance(select_years, list):
        select_years = [select_years]

    # Convertir select_months en liste si ce n'est pas déjà le cas
    if not isinstance(select_months, list):
        select_months = [select_months]

    # Si aucune année n'est sélectionnée, utilisez toutes les années
    if not select_years:
        filtered_df = montant[montant['etat'] == radio_items]
    else:
        # Filtrer les données en fonction des années sélectionnées
        filtered_df = montant[montant['date'].dt.year.isin(select_years)]

        # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
        if select_months:
            filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_months)]

        # Filtrer également en fonction de l'état choisi
        filtered_df = filtered_df[filtered_df['etat'] == radio_items]

    if radio_items1 == 'fournisseur':
        sales1 = filtered_df.groupby(['fournisseur'])['montant'].sum().reset_index()
        sales2 = sales1.sort_values(by=['montant'], ascending=False).nlargest(5, columns=['montant'])

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
                    'text': 'Achats par Fournisseur en ' + ', '.join(str(year) for year in select_years),

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
        sales3 = filtered_df.groupby(['type'])['montant'].sum().reset_index()
        sales4 = sales3.sort_values(by=['montant'], ascending=False).nlargest(5, columns=['montant'])

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
                    'text': 'Achats par Type en ' + ', '.join(str(year) for year in select_years),

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
             [Input('select_month', 'value')])
def update_graph(select_year, select_month):
    # Convertir select_year en liste si ce n'est pas déjà le cas
    if not isinstance(select_year, list):
        select_year = [select_year]

    # Convertir select_month en liste si ce n'est pas déjà le cas
    if not isinstance(select_month, list):
        select_month = [select_month]

    # Filtrer les données en fonction des années sélectionnées
    filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]
    
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
            'text': f'Etat par année: {", ".join(str(year) for year in select_year)}',
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
    [Input('radio_items', 'value')]
)
def update_text(radio_items_value):
    # Nombre de lignes dans la table "fait"
    num_rows = len(montant)
    
    return [
        html.H6(children='Nombre de factures',
                style={'textAlign': 'center', 'color': 'white'}
        ),

        html.P(num_rows,
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(
    Output('text2', 'children'),
    [Input('radio_items', 'value')]
)
def update_text(radio_items_value):
    # Montant total de toute la base
    total_amount = montant['montant'].sum()
    
    return [
        html.H6(children='Montant total',
                style={'textAlign': 'center', 'color': 'white'}
        ),

        html.P('{0:,.2f} DT'.format(total_amount),
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(
    Output('text3', 'children'),
    [Input('radio_items', 'value')]
)
def update_text(radio_items_value):
    # Nombre de types différents
    num_types = montant['type'].nunique()
    
    return [
        html.H6(children='Nombre total des types',
                style={'textAlign': 'center', 'color': 'white'}
        ),

        html.P(num_types,
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'}
        ),
    ]

@app.callback(Output('pie_chart', 'figure'),
             [Input('select_year', 'value')],
             [Input('select_month', 'value')])
def update_pie_chart(select_year, select_month):
    # Convertir select_year en liste si ce n'est pas déjà le cas
    if not isinstance(select_year, list):
        select_year = [select_year]

    # Convertir select_month en liste si ce n'est pas déjà le cas
    if not isinstance(select_month, list):
        select_month = [select_month]

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
    type_amounts_filtered = type_amounts[type_amounts['percentage'] > 2]
    
    # Créer le graphique en secteurs (pie chart)
    colors = ['#30C9C7', '#7A45D1', 'orange']  # Ajouter plus de couleurs si nécessaire
    fig = go.Figure(data=[go.Pie(
        labels=type_amounts_filtered['type'],
        values=type_amounts_filtered['percentage'],
        marker=dict(colors=colors),
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        textfont=dict(size=11),
        rotation=220,
        insidetextorientation='horizontal',
    )])

    fig.update_layout(
        plot_bgcolor='#1f2c56',
        paper_bgcolor='#1f2c56',
        hovermode='x',
        title={
            'text': f'Types par année: {", ".join(str(year) for year in select_year)}',
            'y':0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        titlefont={
            'color': 'white',
            'size': 15
        },
        legend={
            'orientation': 'h',  # Garder l'orientation verticale
            'bgcolor': '#1f2c56',
            'x': -0.2,
            'y': -0.35,
            'traceorder': 'normal',  # Légende dans l'ordre d'apparition des tracés
            'font': {'size': 12},  # Ajuster la taille de police
            'itemsizing': 'constant'  # Garder la taille des éléments de légende constante
        },
        font=dict(
            family="sans-serif",
            size=12,
            color='white'
        )
    )
    
    return fig

@app.callback(Output('line_chart', 'figure'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')])
def update_graph(select_year, select_month):
    # Convertir select_year en liste si ce n'est pas déjà le cas
    if not isinstance(select_year, list):
        select_year = [select_year]

    # Convertir select_month en liste si ce n'est pas déjà le cas
    if not isinstance(select_month, list):
        select_month = [select_month]

    # Filtrer les données en fonction des années sélectionnées
    filtered_df = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_df = filtered_df[filtered_df['date'].dt.month.isin(select_month)]
    
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
                'text': f'Sales Trend in Years: {", ".join(str(year) for year in select_year)}',
                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                'color': 'white',
                'size': 15},
             hovermode='closest',
             margin=dict(t=5, l=0, r=0),

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
                'yanchor': 'top'},

            font=dict(
                family="sans-serif",
                size=12,
                color='white'),
        )
    }


@app.callback(
    Output('my_datatable', 'data'),
    [Input('select_year', 'value')],
    [Input('select_month', 'value')])
def display_table(select_year, select_month):
    # Convertir select_year en liste si ce n'est pas déjà le cas
    if not isinstance(select_year, list):
        select_year = [select_year]

    # Convertir select_month en liste si ce n'est pas déjà le cas
    if not isinstance(select_month, list):
        select_month = [select_month]

    # Filtrer les données en fonction des années sélectionnées
    filtered_data = montant[montant['date'].dt.year.isin(select_year)]

    # Si des mois spécifiques sont sélectionnés, filtrer les données en fonction de ces mois
    if select_month:
        filtered_data = filtered_data[filtered_data['date'].dt.month.isin(select_month)]
    
    return filtered_data.to_dict('records')


        


if __name__ == '__main__':
    app.run_server(debug=True, port=8053    )
