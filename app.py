# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math

#import requests
import pandas as pd
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

app = dash.Dash(__name__)
server = app.server

# Create controls
county_options = [{'label': str(COUNTIES[county]), 'value': str(county)}
                  for county in COUNTIES]

well_status_options = [{'label': str(WELL_STATUSES[well_status]),
                        'value': str(well_status)}
                       for well_status in WELL_STATUSES]

well_type_options = [{'label': str(WELL_TYPES[well_type]),
                      'value': str(well_type)}
                     for well_type in WELL_TYPES]


# Load data
df = pd.read_csv('data/wellspublic.csv')
df['Date_Well_Completed'] = pd.to_datetime(df['Date_Well_Completed'])
df = df[df['Date_Well_Completed'] > dt.datetime(1960, 1, 1)]

trim = df[['API_WellNo', 'Well_Type', 'Well_Name']]
trim.index = trim['API_WellNo']
dataset = trim.to_dict(orient='index')

points = pickle.load(open("data/points.pkl", "rb"))


# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiZHJhZ29uYXJrYSIsImEiOiJjazM5b3c0M24wNG1jM2RvMWR1YjM1OWg2In0.hnjZZ_Lp9EtJyzn0Of3jkA'

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Satellite Overview',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            'Colombia Team 8 ',

                        ),
                        html.H4(
                            'Production Overview',
                        )
                    ],

                    className='eight columns'
                ),
                html.Img(
                    src="data:image/png;base64,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",
                    className='two columns',
                ),
                html.A(
                    html.Button(
                        "Learn More",
                        id="learnMore"

                    ),
                    href="https://ds4a-colombia.correlation1.com/",
                    className="two columns"
                )
            ],
            id="header",
            className='row',
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            'Filter by construction date (or select range in histogram):',
                            className="control_label"
                        ),
                        dcc.RangeSlider(
                            id='year_slider',
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className="dcc_control"
                        ),
                        html.P(
                            'Filter by well status:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='well_status_selector',
                            options=[
                                {'label': 'All ', 'value': 'all'},
                                {'label': 'Active only ', 'value': 'active'},
                                {'label': 'Customize ', 'value': 'custom'}
                            ],
                            value='active',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                        dcc.Dropdown(
                            id='well_statuses',
                            options=well_status_options,
                            multi=True,
                            value=list(WELL_STATUSES.keys()),
                            className="dcc_control"
                        ),
                        dcc.Checklist(
                            id='lock_selector',
                            options=[
                                {'label': 'Lock camera', 'value': 'locked'}
                            ],
                            values=[],
                            className="dcc_control"
                        ),
                        html.P(
                            'Filter by well type:',
                            className="control_label"
                        ),
                        dcc.RadioItems(
                            id='well_type_selector',
                            options=[
                                {'label': 'All ', 'value': 'all'},
                                {'label': 'Productive only ',
                                    'value': 'productive'},
                                {'label': 'Customize ', 'value': 'custom'}
                            ],
                            value='productive',
                            labelStyle={'display': 'inline-block'},
                            className="dcc_control"
                        ),
                        dcc.Dropdown(
                            id='well_types',
                            options=well_type_options,
                            multi=True,
                            value=list(WELL_TYPES.keys()),
                            className="dcc_control"
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("No. of Wells"),
                                        html.H6(
                                            id="well_text",
                                            className="info_text"
                                        )
                                    ],
                                    id="wells",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P("Gas"),
                                                html.H6(
                                                    id="gasText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="gas",
                                            className="pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                html.P("Oil"),
                                                html.H6(
                                                    id="oilText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="oil",
                                            className="pretty_container"
                                        ),
                                        html.Div(
                                            [
                                                html.P("Water"),
                                                html.H6(
                                                    id="waterText",
                                                    className="info_text"
                                                )
                                            ],
                                            id="water",
                                            className="pretty_container"
                                        ),
                                    ],
                                    id="tripleContainer",
                                )

                            ],
                            id="infoContainer",
                            className="row"
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id='count_graph',
                                )
                            ],
                            id="countGraphContainer",
                            className="pretty_container"
                        )
                    ],
                    id="rightCol",
                    className="eight columns"
                )
            ],
            className="row"
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='pretty_container eight columns',
                ),
                html.Div(
                    [
                        dcc.Graph(id='individual_graph')
                    ],
                    className='pretty_container four columns',
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='pie_graph')
                    ],
                    className='pretty_container seven columns',
                ),
                html.Div(
                    [
                        dcc.Graph(id='aggregate_graph')
                    ],
                    className='pretty_container five columns',
                ),
            ],
            className='row'
        ),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


# Helper functions
def human_format(num):

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000**magnitude)))
    return mantissa + ['', 'K', 'M', 'G', 'T', 'P'][magnitude]


def filter_dataframe(df, well_statuses, well_types, year_slider):
    dff = df[df['Well_Status'].isin(well_statuses)
             & df['Well_Type'].isin(well_types)
             & (df['Date_Well_Completed'] > dt.datetime(year_slider[0], 1, 1))
             & (df['Date_Well_Completed'] < dt.datetime(year_slider[1], 1, 1))]
    return dff


def fetch_individual(api):
    try:
        points[api]
    except:
        return None, None, None, None

    index = list(range(min(points[api].keys()), max(points[api].keys()) + 1))
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api][year]['Gas Produced, MCF'])
        except:
            gas.append(0)
        try:
            oil.append(points[api][year]['Oil Produced, bbl'])
        except:
            oil.append(0)
        try:
            water.append(points[api][year]['Water Produced, bbl'])
        except:
            water.append(0)

    return index, gas, oil, water


def fetch_aggregate(selected, year_slider):

    index = list(range(max(year_slider[0], 1985), 2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api in selected:
            try:
                count_gas += points[api][year]['Gas Produced, MCF']
            except:
                pass
            try:
                count_oil += points[api][year]['Oil Produced, bbl']
            except:
                pass
            try:
                count_water += points[api][year]['Water Produced, bbl']
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)

    return index, gas, oil, water


# Create callbacks
@app.callback(Output('aggregate_data', 'data'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value')])
def update_production_text(well_statuses, well_types, year_slider):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    selected = dff['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)
    return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]

# Radio -> multi


@app.callback(Output('well_statuses', 'value'),
              [Input('well_status_selector', 'value')])
def display_status(selector):
    if selector == 'all':
        return list(WELL_STATUSES.keys())
    elif selector == 'active':
        return ['AC']
    else:
        return []


# Radio -> multi
@app.callback(Output('well_types', 'value'),
              [Input('well_type_selector', 'value')])
def display_type(selector):
    if selector == 'all':
        return list(WELL_TYPES.keys())
    elif selector == 'productive':
        return ['GD', 'GE', 'GW', 'IG', 'IW', 'OD', 'OE', 'OW']
    else:
        return []


# Slider -> count graph
@app.callback(Output('year_slider', 'value'),
              [Input('count_graph', 'selectedData')])
def update_year_slider(count_graph_selected):

    if count_graph_selected is None:
        return [1990, 2010]
    else:
        nums = []
        for point in count_graph_selected['points']:
            nums.append(int(point['pointNumber']))

        return [min(nums) + 1960, max(nums) + 1961]


# Selectors -> well text
@app.callback(Output('well_text', 'children'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value')])
def update_well_text(well_statuses, well_types, year_slider):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    return dff.shape[0]


@app.callback(Output('gasText', 'children'),
              [Input('aggregate_data', 'data')])
def update_gas_text(data):
    return data[0] + " mcf"


@app.callback(Output('oilText', 'children'),
              [Input('aggregate_data', 'data')])
def update_oil_text(data):
    return data[1] + " bbl"


@app.callback(Output('waterText', 'children'),
              [Input('aggregate_data', 'data')])
def update_oil_text(data):
    return data[2] + " bbl"

# Selectors -> main graph


@app.callback(Output('main_graph', 'figure'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value')],
              [State('lock_selector', 'values'),
               State('main_graph', 'relayoutData')])
def make_main_figure(well_statuses, well_types, year_slider,
                     selector, main_graph_layout):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    traces = []
    for well_type, dfff in dff.groupby('Well_Type'):
        trace = dict(
            type='scattermapbox',
            lon=dfff['Surface_Longitude'],
            lat=dfff['Surface_latitude'],
            text=dfff['Well_Name'],
            customdata=dfff['API_WellNo'],
            name=WELL_TYPES[well_type],
            marker=dict(
                size=4,
                opacity=0.6,
            )
        )
        traces.append(trace)

    if (main_graph_layout is not None and 'locked' in selector):

        lon = float(main_graph_layout['mapbox']['center']['lon'])
        lat = float(main_graph_layout['mapbox']['center']['lat'])
        zoom = float(main_graph_layout['mapbox']['zoom'])
        layout['mapbox']['center']['lon'] = lon
        layout['mapbox']['center']['lat'] = lat
        layout['mapbox']['zoom'] = zoom
    else:
        lon = -78.05
        lat = 42.54
        zoom = 7

    figure = dict(data=traces, layout=layout)
    return figure


# Main graph -> individual graph
@app.callback(Output('individual_graph', 'figure'),
              [Input('main_graph', 'hoverData')])
def make_individual_figure(main_graph_hover):

    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {'points': [{'curveNumber': 4,
                                        'pointNumber': 569,
                                        'customdata': 31101173130000}]}

    chosen = [point['customdata'] for point in main_graph_hover['points']]
    index, gas, oil, water = fetch_individual(chosen[0])

    if index is None:
        annotation = dict(
            text='No data available',
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        layout_individual['annotations'] = [annotation]
        data = []
    else:
        data = [
            dict(
                type='scatter',
                mode='lines+markers',
                name='Gas Produced (mcf)',
                x=index,
                y=gas,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#fac1b7'
                ),
                marker=dict(symbol='diamond-open')
            ),
            dict(
                type='scatter',
                mode='lines+markers',
                name='Oil Produced (bbl)',
                x=index,
                y=oil,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#a9bb95'
                ),
                marker=dict(symbol='diamond-open')
            ),
            dict(
                type='scatter',
                mode='lines+markers',
                name='Water Produced (bbl)',
                x=index,
                y=water,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#92d8d8'
                ),
                marker=dict(symbol='diamond-open')
            )
        ]
        layout_individual['title'] = dataset[chosen[0]]['Well_Name']

    figure = dict(data=data, layout=layout_individual)
    return figure


# Selectors, main graph -> aggregate graph
@app.callback(Output('aggregate_graph', 'figure'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value'),
               Input('main_graph', 'hoverData')])
def make_aggregate_figure(well_statuses, well_types, year_slider,
                          main_graph_hover):

    layout_aggregate = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {'points': [{'curveNumber': 4, 'pointNumber': 569,
                                        'customdata': 31101173130000}]}

    chosen = [point['customdata'] for point in main_graph_hover['points']]
    well_type = dataset[chosen[0]]['Well_Type']
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff[dff['Well_Type'] == well_type]['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)

    data = [
        dict(
            type='scatter',
            mode='lines',
            name='Gas Produced (mcf)',
            x=index,
            y=gas,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#F9ADA0'
            )
        ),
        dict(
            type='scatter',
            mode='lines',
            name='Oil Produced (bbl)',
            x=index,
            y=oil,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#849E68'
            )
        ),
        dict(
            type='scatter',
            mode='lines',
            name='Water Produced (bbl)',
            x=index,
            y=water,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#59C3C3'
            )
        )
    ]
    layout_aggregate['title'] = 'Aggregate: ' + WELL_TYPES[well_type]

    figure = dict(data=data, layout=layout_aggregate)
    return figure


# Selectors, main graph -> pie graph
@app.callback(Output('pie_graph', 'figure'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value')])
def make_pie_figure(well_statuses, well_types, year_slider):

    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)

    aggregate = dff.groupby(['Well_Type']).count()

    data = [
        dict(
            type='pie',
            labels=['Gas', 'Oil', 'Water'],
            values=[sum(gas), sum(oil), sum(water)],
            name='Production Breakdown',
            text=['Total Gas Produced (mcf)', 'Total Oil Produced (bbl)',
                  'Total Water Produced (bbl)'],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=['#fac1b7', '#a9bb95', '#92d8d8']
            ),
            domain={"x": [0, .45], 'y':[0.2, 0.8]},
        ),
        dict(
            type='pie',
            labels=[WELL_TYPES[i] for i in aggregate.index],
            values=aggregate['API_WellNo'],
            name='Well Type Breakdown',
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=[WELL_COLORS[i] for i in aggregate.index]
            ),
            domain={"x": [0.55, 1], 'y':[0.2, 0.8]},
        )
    ]
    layout_pie['title'] = 'Production Summary: {} to {}'.format(
        year_slider[0], year_slider[1])
    layout_pie['font'] = dict(color='#777777')
    layout_pie['legend'] = dict(
        font=dict(color='#CCCCCC', size='10'),
        orientation='h',
        bgcolor='rgba(0,0,0,0)'
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


# Selectors -> count graph
@app.callback(Output('count_graph', 'figure'),
              [Input('well_statuses', 'value'),
               Input('well_types', 'value'),
               Input('year_slider', 'value')])
def make_count_figure(well_statuses, well_types, year_slider):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
    g = dff[['API_WellNo', 'Date_Well_Completed']]
    g.index = g['Date_Well_Completed']
    g = g.resample('A').count()

    colors = []
    for i in range(1960, 2018):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append('rgb(123, 199, 255)')
        else:
            colors.append('rgba(123, 199, 255, 0.2)')

    data = [
        dict(
            type='scatter',
            mode='markers',
            x=g.index,
            y=g['API_WellNo'] / 2,
            name='All Wells',
            opacity=0,
            hoverinfo='skip'
        ),
        dict(
            type='bar',
            x=g.index,
            y=g['API_WellNo'],
            name='All Wells',
            marker=dict(
                color=colors
            ),
        ),
    ]

    layout_count['title'] = 'Completed Wells/Year'
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['autosize'] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
