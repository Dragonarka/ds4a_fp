import dash
import dash_html_components as html
import dash_core_components as dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([ 
  html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            '     Medellin, Colombia - Team 8 ',

                        ),
                        html.H4(
                            '                 System for blackout prediction of the Colombian power system',
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

    dcc.Tabs([
        dcc.Tab(label='Map',
       
         children=[
            html.Div(                 
    children=[html.Iframe(className="full-page extra-padding",
    style={'width': '100%', 'height': '70vh'},
     src=app.get_asset_url("kepler_final.html"))])


        ]),
        dcc.Tab(label='Model', children=[
                html.Img(
                    src='/assets/t2.jpeg'
                ),
                html.Img(
                    src='/assets/t3.jpeg'
                ),
                html.Img(
                    src='/assets/t4.jpeg'
                )
        ]),
        dcc.Tab(label='Statistics', children=[
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [2, 4, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [5, 4, 3],
                         'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            )
        ]),
    ])
])



if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8085)