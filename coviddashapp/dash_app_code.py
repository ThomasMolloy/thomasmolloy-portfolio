import pandas as pd
import datetime
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
import plotly.express as px

# -----Read World Data-----
full_world_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
cols_world_df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-codebook.csv')

# -----Read USA Data-----
full_usa_df = pd.read_csv('https://api.covidtracking.com/v1/states/daily.csv')

# -----Preprocessing USA Data-----
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

# -----Preprocessing World Data-----
countries_list = full_world_df['location'].unique()
def get_important_countries(countries_list):
    cl=[]
    for country in countries_list:
        if len(full_world_df.loc[full_world_df.location == country]) > 200:
            cl.append(country)
    return cl

imp_countries = get_important_countries(countries_list)

line_graph_cols = ['total_cases','new_cases_smoothed','total_deaths','new_deaths_smoothed','total_tests','new_tests_smoothed','total_cases_per_million','new_cases_smoothed_per_million','total_deaths_per_million','new_deaths_smoothed_per_million','total_tests_per_thousand','new_tests_smoothed_per_thousand']

def get_country_df(country):
    return full_world_df[full_world_df['location'] == country]

# -----DASH APP CODE-----

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

covidapp = DjangoDash('dash_app_id', external_stylesheets=external_stylesheets)

covidapp.layout = html.Div([
    html.H1('Covid Dashboard', style={'text-align': 'center'}),

    dcc.Tabs([

        dcc.Tab(label='World', children=[

            html.Div([
                html.P('Select Country: '),

                dcc.Dropdown(
                    id='country',
                    options=[{'label': i, 'value': i} for i in imp_countries],
                    value='United States'
                )

            ], style={'width': '40%', 'display': 'inline-block'}),

            html.Div([
                html.P('Select Metric: '),

                dcc.RadioItems(
                    id='total_percapita',
                    options=[{'label': i, 'value': i} for i in ['Total', 'Per Capita']],
                    value='Total',
                    labelStyle={'display': 'inline-block', 'text-align': 'justify'}
                )
            ], style={'width': '40%', 'display': 'inline-block', 'float': 'right'}),

            dcc.Graph(id='totalcases_line'),
            html.P('Source: European Centre for Disease Prevention and Control',
                   style={'fontSize': 10, 'text-align': 'center'}),
            dcc.Graph(id='newcases_line'),
            html.P('Source: European Centre for Disease Prevention and Control',
                   style={'fontSize': 10, 'text-align': 'center'}),
            dcc.Graph(id='totaldeaths_line'),
            html.P('Source: European Centre for Disease Prevention and Control',
                   style={'fontSize': 10, 'text-align': 'center'}),
            dcc.Graph(id='newdeaths_line'),
            html.P('Source: European Centre for Disease Prevention and Control',
                   style={'fontSize': 10, 'text-align': 'center'}),
            dcc.Graph(id='totaltests_line'),
            html.P('Source: National government reports', style={'fontSize': 10, 'text-align': 'center'}),
            dcc.Graph(id='newtests_line'),
            html.P('Source: National government reports', style={'fontSize': 10, 'text-align': 'center'})

        ]),

        dcc.Tab(label='United States', children=[

            html.Div([
                dcc.Dropdown(
                    id='choropleth_dropdown',
                    options=[{'label': i, 'value': i} for i in dropdownoptions],
                    value='Total Positive Cases'
                )
            ]),

            dcc.Graph(id='choropleth'),

            html.Div([
                dcc.Slider(
                    id='choropleth_slider',
                    min=convert_to_unixtime(usa_df['date'].min()),
                    max=convert_to_unixtime(usa_df['date'].max()),
                    value=convert_to_unixtime(usa_df['date'].max()),
                    step=86400
                )
            ]),
            html.Div(id='selected_date'),

            html.Div([
                dcc.Dropdown(
                    id='state',
                    options=[{'label': i, 'value': i} for i in us_state_abbrev_dict.values()],
                    value='New Jersey'
                )
            ]),

            dcc.Graph(id='total_positive_line'),
            dcc.Graph(id='new_positive_line'),
            dcc.Graph(id='total_death_line'),
            dcc.Graph(id='new_death_line'),
            dcc.Graph(id='total_ventilator_line'),
            dcc.Graph(id='total_negative_line'),
            dcc.Graph(id='total_recovered_line'),
            dcc.Graph(id='total_test_line'),
            dcc.Graph(id='new_test_line')

        ])

    ])
])

@covidapp.callback(
    [Output('totalcases_line', 'figure'),
     Output('newcases_line', 'figure'),
     Output('totaldeaths_line', 'figure'),
     Output('newdeaths_line', 'figure'),
     Output('totaltests_line', 'figure'),
     Output('newtests_line', 'figure')],
    [Input('country', 'value'),
     Input('total_percapita', 'value')])
def update_world_graphs(country, total_percapita):
    country_df = get_country_df(country)

    if total_percapita == 'Total':

        totalcases_fig = px.line(country_df, x='date', y='total_cases', title=f'{country} Total Cases')
        totalcases_fig.update_xaxes(title='Date')
        totalcases_fig.update_yaxes(title='Total Cases')

        newcases_fig = px.line(country_df, x='date', y='new_cases_smoothed', title=f'{country} New Cases')
        newcases_fig.update_xaxes(title='Date')
        newcases_fig.update_yaxes(title='New Cases')

        totaldeaths_fig = px.line(country_df, x='date', y='total_deaths', title=f'{country} Total Deaths')
        totaldeaths_fig.update_xaxes(title='Date')
        totaldeaths_fig.update_yaxes(title='Total Deaths')

        newdeaths_fig = px.line(country_df, x='date', y='new_deaths_smoothed', title=f'{country} New Deaths')
        newdeaths_fig.update_xaxes(title='Date')
        newdeaths_fig.update_yaxes(title='New Deaths')

        totaltests_fig = px.line(country_df, x='date', y='total_tests', title=f'{country} Total Tests')
        totaltests_fig.update_xaxes(title='Date')
        totaltests_fig.update_yaxes(title='Total Tests')

        newtests_fig = px.line(country_df, x='date', y='new_tests_smoothed', title=f'{country} New Tests')
        newtests_fig.update_xaxes(title='Date')
        newtests_fig.update_yaxes(title='New Tests')

        return totalcases_fig, newcases_fig, totaldeaths_fig, newdeaths_fig, totaltests_fig, newtests_fig

    else:

        pc_totalcases_fig = px.line(country_df, x='date', y='total_cases_per_million',
                                    title=f'{country} Total Cases Per Million')
        pc_totalcases_fig.update_xaxes(title='Date')
        pc_totalcases_fig.update_yaxes(title='Total Cases (per million people)')

        pc_newcases_fig = px.line(country_df, x='date', y='new_cases_smoothed_per_million',
                                  title=f'{country} New Cases Per Million')
        pc_newcases_fig.update_xaxes(title='Date')
        pc_newcases_fig.update_yaxes(title='New Cases(per million people)')

        pc_totaldeaths_fig = px.line(country_df, x='date', y='total_deaths_per_million',
                                     title=f'{country} Total Deaths Per Million')
        pc_totaldeaths_fig.update_xaxes(title='Date')
        pc_totaldeaths_fig.update_yaxes(title='Total Deaths (per million people)')

        pc_newdeaths_fig = px.line(country_df, x='date', y='new_deaths_smoothed_per_million',
                                   title=f'{country} New Deaths Per Million')
        pc_newdeaths_fig.update_xaxes(title='Date')
        pc_newdeaths_fig.update_yaxes(title='New Deaths (per million people)')

        pc_totaltests_fig = px.line(country_df, x='date', y='total_tests_per_thousand',
                                    title=f'{country} Total Tests Per Thousand')
        pc_totaltests_fig.update_xaxes(title='Date')
        pc_totaltests_fig.update_yaxes(title='Total Tests (per thousand people)')

        pc_newtests_fig = px.line(country_df, x='date', y='new_tests_smoothed_per_thousand',
                                  title=f'{country} New Tests Per Thousand')
        pc_newtests_fig.update_xaxes(title='Date')
        pc_newtests_fig.update_yaxes(title='New Tests (per thousand people)')

        return pc_totalcases_fig, pc_newcases_fig, pc_totaldeaths_fig, pc_newdeaths_fig, pc_totaltests_fig, pc_newtests_fig


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
                               projection='albers usa')

    # Line graphs
    state_df = get_state_df(usa_df, us_state_abbrev[state])
    usa_line_graphs = []
    for option in dropdownoptions:
        usa_line_graphs.append(px.line(state_df, x='date', y=option, title=f'{state} {option}'))

    date_selection_string = f'Selected Date: {dt.month_name()} {dt.day}, {dt.year}'

    return choropleth, date_selection_string, usa_line_graphs[0], usa_line_graphs[1], usa_line_graphs[2], \
           usa_line_graphs[3], usa_line_graphs[4], usa_line_graphs[5], usa_line_graphs[6], usa_line_graphs[7], \
           usa_line_graphs[8]


if __name__ == '__main__':
    covidapp.run_server(debug=True, use_reloader=False)