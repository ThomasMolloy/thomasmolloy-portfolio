import pandas as pd
import datetime
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
import plotly.express as px

#-----------------------------------------------------------------------------------------------------------------------
#                                       -----Read World Data-----
#-----------------------------------------------------------------------------------------------------------------------

full_world_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
cols_world_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-codebook.csv')

#-----------------------------------------------------------------------------------------------------------------------
#                                       -----Read USA Data-----
#-----------------------------------------------------------------------------------------------------------------------

full_usa_df = pd.read_csv('https://api.covidtracking.com/v1/states/daily.csv')

#-----------------------------------------------------------------------------------------------------------------------
#                                   -----Preprocessing USA Data-----
#-----------------------------------------------------------------------------------------------------------------------

imp_features = ['date','state','death','deathIncrease','lastUpdateEt','negative','onVentilatorCurrently','positive','positiveIncrease','recovered','totalTestResults','totalTestResultsIncrease']
full_usa_df = full_usa_df[imp_features]
full_usa_df.rename(columns={'death':'Total Deaths','deathIncrease':'New Deaths','negative':'Total Negative Cases','onVentilatorCurrently':'Total Currently On Ventilator','positive':'Total Positive Cases','positiveIncrease':'New Positive Cases','recovered':'Total Recovered','totalTestResults':'Total Test Results','totalTestResultsIncrease':'New Test Results'}, inplace=True)
# Dict from this repo: https://gist.github.com/rogerallen/1583593
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
full_usa_df = full_usa_df[full_usa_df['state'].isin(us_state_abbrev.values())]
#flip dictionary
us_state_abbrev_dict = {value : key for (key, value) in us_state_abbrev.items()}

def get_state_df(df, state):
    return df[df['state'] == state]

dropdownoptions = ['Total Positive Cases','New Positive Cases','Total Deaths','New Deaths','Total Currently On Ventilator','Total Negative Cases','Total Recovered','Total Test Results','New Test Results']

full_usa_df['date'] = pd.to_datetime(full_usa_df['date'], format='%Y%m%d')

def convert_to_unixtime(dt):
    return int(time.mktime(dt.timetuple()))

def convert_to_datetime(dt):
    return datetime.datetime.fromtimestamp(int(dt)).strftime('%Y-%m-%d %H:%M:%S')

usa_df = full_usa_df
usa_table_df = usa_df.loc[usa_df.date == usa_df.date.max()].round(1)

last_update = usa_df.date.max()

#-----------------------------------------------------------------------------------------------------------------------
#                               -----Preprocessing World Data-----
#-----------------------------------------------------------------------------------------------------------------------

important_cols = ['total_cases','new_cases','new_cases_smoothed','total_deaths','new_deaths','new_deaths_smoothed','total_tests','new_tests','new_tests_smoothed','total_cases_per_million','new_cases_per_million','new_cases_smoothed_per_million','total_deaths_per_million','new_deaths_per_million','new_deaths_smoothed_per_million','total_tests_per_thousand','new_tests_per_thousand','new_tests_smoothed_per_thousand']
MAIN_cols = ['Total Cases','New Cases', 'Total Deaths', 'New Deaths', 'Total Tests', 'New Tests', 'Total Cases Per Million', 'New Cases Per Million', 'Total Deaths Per Million', 'New Deaths Per Million', 'Total Tests Per Thousand', 'New Tests Per Thousand']
lg_cols = ['total_cases','new_cases_smoothed','total_deaths','new_deaths_smoothed','total_tests','new_tests_smoothed','total_cases_per_million','new_cases_smoothed_per_million','total_deaths_per_million','new_deaths_smoothed_per_million','total_tests_per_thousand','new_tests_smoothed_per_thousand']
tb_cols = ['total_cases','new_cases','total_deaths','new_deaths','total_tests','new_tests','total_cases_per_million','new_cases_per_million','total_deaths_per_million','new_deaths_per_million','total_tests_per_thousand','new_tests_per_thousand']
total_line_graph_cols = ['Total Cases','New Cases', 'Total Deaths', 'New Deaths', 'Total Tests', 'New Tests']
per_capita_line_graph_cols = ['Total Cases Per Million', 'New Cases Per Million', 'Total Deaths Per Million', 'New Deaths Per Million', 'Total Tests Per Thousand', 'New Tests Per Thousand']
MAIN_total_cols = ['Date', 'Country'] + MAIN_cols

# Only use countries that recorded enough data, change 'date' and 'location' column names, and forward fill na values
def get_important_countries(countries_list):
    cl=[]
    for country in countries_list:
        if len(full_world_df.loc[full_world_df.location == country]) > 250:
            cl.append(country)
    return cl

countries_list = full_world_df['location'].unique()
imp_countries = get_important_countries(countries_list)

full_world_df = full_world_df.loc[full_world_df.location.isin(imp_countries)]
full_world_df.rename(columns={'date':'Date', 'location':'Country'}, inplace=True)

#Create DF for Line Graphs
line_world_df = full_world_df.rename(columns={i:j for i,j in zip(lg_cols, MAIN_cols)})
line_world_df = line_world_df[MAIN_total_cols]

def get_country_df(country):
    return line_world_df[line_world_df['Country'] == country]

#Create DF for World Table
world_table_df = full_world_df.rename(columns={i:j for i,j in zip(tb_cols, MAIN_cols)})
world_table_df = world_table_df[MAIN_total_cols]
world_table_df = world_table_df.loc[world_table_df.Date == world_table_df.Date.max()].round(1)

#-----------------------------------------------------------------------------------------------------------------------
#                                       -----DASH APP LAYOUT-----
#-----------------------------------------------------------------------------------------------------------------------

covidapp = DjangoDash('dash_app_id', external_stylesheets=[dbc.themes.DARKLY], add_bootstrap_links=True)

covidapp.layout = html.Div([

    dbc.Row(
        html.H1('Covid-19 Dashboard'),
        justify='center',
        className='text-light',
        style={'padding-top':20, 'padding-bottom':20}
    ),

    dbc.Row(
        html.Div(id='last_update', style={'color':'white','padding-bottom':20}),
        justify='center',
    ),

    dbc.Tabs([

# --------------------------------------------- WORLD TABS --------------------------------------------------------------

        dbc.Tab(label='World', children=[
            dbc.Tabs([
                dbc.Tab(label='Graphs', children=[

                    dbc.Row([
                        dbc.Col(
                            dbc.FormGroup([
                                dbc.Label('Select Country: ', color='light', align='center'),
                                dcc.Dropdown(
                                    id='country',
                                    options=[{'label': i, 'value': i} for i in imp_countries],
                                    value='United States'
                                ),
                            ]),
                            width=4
                        ),
                        dbc.Col(
                            dbc.FormGroup([
                                dbc.Label('Select Metric: ', color='light', align='center'),
                                dcc.RadioItems(
                                    id='total_percapita',
                                    options=[{'label': i, 'value': i} for i in ['Total', 'Per Capita']],
                                    value='Total',
                                    labelStyle={'display': 'inline-block', 'text-align': 'justify'},
                                    inputStyle={'margin-right':5, 'margin-left':30}
                                ),
                            ]),
                            width=4
                        )
                    ],
                    form=True,
                    justify='around',
                    style={'margin-top':20, 'margin-bottom':20}),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='totalcases_line', style={'margin': 'auto'}),
                                html.P('Source: European Centre for Disease Prevention and Control', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor':'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='newcases_line', style={'margin': 'auto'}),
                                html.P('Source: European Centre for Disease Prevention and Control', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor':'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='totaldeaths_line', style={'margin': 'auto'}),
                                html.P('Source: European Centre for Disease Prevention and Control', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='newdeaths_line', style={'margin': 'auto'}),
                                html.P('Source: European Centre for Disease Prevention and Control', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='totaltests_line', style={'margin': 'auto'}),
                                html.P('Source: National government reports', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='newtests_line', style={'margin': 'auto'}),
                                html.P('Source: National government reports', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'padding-bottom':30}
                    ),
                ], tab_style={'width':'25%'}, label_style={'text-align':'center', 'font-size':'18px'}),

                dbc.Tab(label='Table', children=[
                    dbc.Table.from_dataframe(world_table_df, striped=True, bordered=True, hover=True, className='table-primary')
                ], tab_style={'width':'25%'}, label_style={'text-align':'center', 'font-size':'18px'})
            ]),

        ], tab_style={'width':'50%'}, label_style={'text-align':'center', 'font-size':'24px'}),

# --------------------------------------------- USA TAB ----------------------------------------------------------------

        dbc.Tab(label='United States', children=[
            dbc.Tabs([
                dbc.Tab(label='Graphs', children=[

                    dbc.Row(
                        dbc.Col(
                            dcc.Dropdown(
                                id='choropleth_dropdown',
                                options=[{'label': i, 'value': i} for i in dropdownoptions],
                                value='Total Positive Cases'
                            ),
                            width=6,
                        ),
                        form=True,
                        justify='around',
                        style={'margin-top':20, 'margin-bottom':20}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='choropleth', style={'margin': 'auto'}),
                                html.Div(id='selected_date', style={'text-align':'center', 'color':'white', 'padding-bottom':10}),
                                dcc.Slider(
                                    id='choropleth_slider',
                                    min=convert_to_unixtime(usa_df['date'].min()),
                                    max=convert_to_unixtime(usa_df['date'].max()),
                                    value=convert_to_unixtime(usa_df['date'].max()),
                                    step=86400
                                ),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'}),
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':20, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dcc.Dropdown(
                                id='state',
                                options=[{'label': i, 'value': i} for i in us_state_abbrev_dict.values()],
                                value='New Jersey'
                            ),
                            width=6,
                        ),
                        form=True,
                        justify='around',
                        style={'margin-top':20, 'margin-bottom':20}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_positive_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='new_positive_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_death_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='new_death_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_ventilator_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_negative_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_recovered_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='total_test_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'margin-bottom':30}
                    ),

                    dbc.Row(
                        dbc.Col(
                            dbc.Card([
                                dcc.Graph(id='new_test_line', style={'margin': 'auto'}),
                                html.P('Source: The Covid Tracking Project', style={'fontSize': 10, 'text-align': 'center', 'color':'white'})
                            ], style={'backgroundColor': 'rgb(17,17,17)'}),
                            width={'size': 10, 'offset': 1}
                        ),
                        style={'margin-top':30, 'padding-bottom':30}
                    ),
                ], tab_style={'margin-left':'auto','width':'25%'}, label_style={'text-align':'center', 'font-size':'18px'}),

                dbc.Tab(label='Table', children=[
                    dbc.Table.from_dataframe(usa_table_df, striped=True, bordered=True, hover=True, className='table-primary')
                ], tab_style={'width':'25%'}, label_style={'text-align':'center', 'font-size':'18px'})
            ]),

        ], tab_style={'width':'50%'}, label_style={'text-align':'center', 'font-size':'24px'})

    ])
], style={'backgroundColor':'#444'})

#-----------------------------------------------------------------------------------------------------------------------
#                                       ----- DASH APP CALLBACKS -----
#-----------------------------------------------------------------------------------------------------------------------

@covidapp.callback(
    [Output('last_update', 'children'),
     Output('totalcases_line', 'figure'),
     Output('newcases_line', 'figure'),
     Output('totaldeaths_line', 'figure'),
     Output('newdeaths_line', 'figure'),
     Output('totaltests_line', 'figure'),
     Output('newtests_line', 'figure')],
    [Input('country', 'value'),
     Input('total_percapita', 'value')])

def update_world_graphs(country, total_percapita):
    last_update_string = f'Last Updated: {last_update}'
    country_df = get_country_df(country)

    world_line_graphs = []

    if total_percapita == 'Total':

        for option in total_line_graph_cols:
            world_line_graphs.append(px.line(country_df, x='Date', y=option, title=f'{country} {option}', template='plotly_dark', width=1000))

        return last_update_string, world_line_graphs[0], world_line_graphs[1], world_line_graphs[2], world_line_graphs[3], world_line_graphs[4], world_line_graphs[5]

    else:

        for option in per_capita_line_graph_cols:
            world_line_graphs.append(px.line(country_df, x='Date', y=option, title=f'{country} {option}', template='plotly_dark', width=1000))

        return last_update_string, world_line_graphs[0], world_line_graphs[1], world_line_graphs[2], world_line_graphs[3], world_line_graphs[4], world_line_graphs[5]


@covidapp.callback(
    [Output('choropleth', 'figure'),
     Output('selected_date', 'children'),
     Output('total_positive_line', 'figure'),
     Output('new_positive_line', 'figure'),
     Output('total_death_line', 'figure'),
     Output('new_death_line', 'figure'),
     Output('total_ventilator_line', 'figure'),
     Output('total_negative_line', 'figure'),
     Output('total_recovered_line', 'figure'),
     Output('total_test_line', 'figure'),
     Output('new_test_line', 'figure')],
    [Input('choropleth_dropdown', 'value'),
     Input('choropleth_slider', 'value'),
     Input('state', 'value')])
def update_USA_graphs(choropleth_dropdown, choropleth_slider, state):
    # Choropleth
    dt = pd.to_datetime(convert_to_datetime(choropleth_slider)).normalize()
    day_df = usa_df.loc[usa_df['date'] == dt]
    choropleth = px.choropleth(day_df, locations='state', locationmode='USA-states', color=choropleth_dropdown,
                               projection='albers usa', template='plotly_dark', width=1000, title=f'{choropleth_dropdown} In The United States')

    # Line graphs
    state_df = get_state_df(usa_df, us_state_abbrev[state])
    usa_line_graphs = []
    for option in dropdownoptions:
        usa_line_graphs.append(px.line(state_df, x='date', y=option, title=f'{state} {option}', template='plotly_dark', width=1000))

    date_selection_string = f'Selected Date: {dt.month_name()} {dt.day}, {dt.year}'

    return choropleth, date_selection_string, usa_line_graphs[0], usa_line_graphs[1], usa_line_graphs[2], \
           usa_line_graphs[3], usa_line_graphs[4], usa_line_graphs[5], usa_line_graphs[6], usa_line_graphs[7], \
           usa_line_graphs[8]