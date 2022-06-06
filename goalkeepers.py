import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import dash_daq as daq
import pandas as pd

import plotly.graph_objs as go

import plotly.express as px


app = dash.Dash(__name__, suppress_callback_exceptions=True)


                                                          
        
stat_names = ['Save %',
              'Penalty save %',
              'Saves held per 90', 
              'Saves parried per 90',
              'Saves tipped per 90',
              'Conceded per 90',
              'Pass completion ratio',
              'Passes attempted per 90'
              ]

#if fm20 == True:
#        stat_names.remove('xG per 90')
#        stat_names.remove('Clear cut chances created per 90')

stat_names.sort()
percentile_stat_names = stat_names.copy()


styles = {
    
         'primary': '#444444',
         'text': '#FFFFFF',
         'secondary': '#1d1d1d'
    
}

app.layout = html.Div([
        dcc.Tabs([
                dcc.Tab(label='Settings', style={'color': styles['text'], 'backgroundColor': styles['secondary'],}, selected_style={'color': styles['text'], 'backgroundColor': styles['secondary'],}, children=[
                         
                         dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A(children='Select Files', id="fileLink")
                                ]),
                                style={
                                    'width': '98%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderColor': styles['text'],
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px',
                                    'font': {
                                            'color': styles['text']
                                    }
                                },
                                multiple=True
                            ),
                        ]),
                dcc.Tab(label='Results', style={'color': styles['text'], 'backgroundColor': styles['secondary'],}, selected_style={'color': styles['text'], 'backgroundColor': styles['secondary'],},children=[
                    html.Div([
                        html.P("Horizontal axis"),
                        dcc.Dropdown(
                                stat_names,
                                stat_names[0],
                                id='xaxis-column',
                                clearable=False,
                        )], style={'width': '49%', 'display': 'inline-block', }),

                    html.Div([
                        html.P("Vertical axis"),
                        dcc.Dropdown(
                                stat_names,
                                stat_names[1],
                                id='yaxis-column',
                                clearable=False,
                        )], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

          
      
   
                    html.Div([
                            html.Div([
                                    html.P("Stats for all players"),
                                    dcc.Graph(id="scattergram",
                                              figure={
                                                      'layout':
                                                      {
                                                            'hovermode': 'closest',
                                                            'plot_bgcolor': styles['secondary'],
                                                            'paper_bgcolor': styles['secondary'],
                                                            'font': {
                                                                'color': styles['text']
                                                            },
                                                            
                                                      }
                                              }),
                                    ], style={'width': '53%', 'display': 'inline-block'}),
                            html.Div([
                                    html.P("Stats for selected player"),
                                      dcc.Dropdown(
                                        percentile_stat_names,
                                        [percentile_stat_names[0], percentile_stat_names[1], percentile_stat_names[2]],
                                        id='radar-type',
                                        clearable=False,
                                        multi = True
                                    ),

                                    dcc.Graph(id='radar', figure={
                                                      'layout':
                                                      {
                                                            'hovermode': 'closest',
                                                            'plot_bgcolor': styles['secondary'],
                                                            'paper_bgcolor': styles['secondary'],
                                                            'font': {
                                                                'color': styles['text']
                                                            },
                                                            
                                                      }
                                              })
                                      ], style={'width': '47%', 'display': 'inline-block'})
                            ]),
                      html.Div([
                              html.P("Minutes played"),
                              dcc.RangeSlider(
                              id='minutes-slider',
                              min=0, max=1000,
                              value=[40, 500]
                              )], style={'width': '47%', 'display': 'inline-block'}),
                     html.Div([
                              html.P("Age"),
                              dcc.RangeSlider(
                              id='age-slider',
                              min=15, max=45,
                              step=1,
                              value=[15, 45]
                              )], style={'width': '47%', 'display': 'inline-block'})
                    ])
                ])
                
    
])



@app.callback(
    Output("scattergram", "figure"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('minutes-slider', 'value'),
    Input('age-slider', 'value')
)
def update_graph(contents, filename, xaxis_column_name, yaxis_column_name, minutes, age):
        contents = contents[0]
        filename = filename[0]

        
        filtered_players = parse_data(contents, filename)
        
        filtered_players=filtered_players[filtered_players['Minutes played'] >= minutes[0]]
        filtered_players=filtered_players[filtered_players['Minutes played'] <= minutes[1]]
        filtered_players=filtered_players[filtered_players[xaxis_column_name] > 0]
        filtered_players=filtered_players[filtered_players[yaxis_column_name] > 0]

        #TODO: handle empty filtered_players

        global filtered
        filtered = filtered_players.copy()
        
        global percentiles
        percentiles = filtered_players.drop(columns=['Name', 'Division', 'Minutes played', 'Age'])

        for i in percentiles.columns:
            percentiles[i] = percentiles[i].rank(pct=True)

         
        percentiles['Conceded per 90'] = percentiles['Conceded per 90'].rank(pct=True, ascending=False)
      


        percentiles['Name'] = filtered_players['Name']
        percentiles['Division'] = filtered_players['Division']
        percentiles['Minutes played'] = filtered_players['Minutes played']
        percentiles['Age'] = filtered_players['Age']

        filtered_players=filtered_players[filtered_players['Age'] >= age[0]]
        filtered_players=filtered_players[filtered_players['Age'] <= age[1]]

        percentiles=percentiles[percentiles['Age'] >= age[0]]
        percentiles=percentiles[percentiles['Age'] <= age[1]]
        
        fig = px.scatter(filtered_players, x=filtered_players[xaxis_column_name],
                     y=filtered_players[yaxis_column_name],
                     color=filtered_players['Division'],
                     hover_name=filtered_players['Name'],
                     trendline="ols", 
                     trendline_scope="overall",
                )

        fig.update_layout(
                    hovermode='closest',
                    plot_bgcolor=styles['secondary'],
                    paper_bgcolor=styles['secondary'],
                    font={
                        'color': styles['text']
                    })
        
        
        fig.update_xaxes(title=xaxis_column_name,
                         type='linear')

        fig.update_yaxes(title=yaxis_column_name,
                         type='linear')
         
        return fig
       

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
         
                all_players = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
                all_players = all_players.replace({'%': ''}, regex=True)
                all_players = all_players.replace({'-': 0}, regex=False)

                
                all_players['Mins'] = all_players['Mins'].replace({',': ''}, regex=True)
                
                all_players['Mins'] = all_players['Mins'].astype(float)

           
                all_players['Matches'] = all_players['Mins'] / 90.0
              
               
                all_players = all_players.drop(columns='Inf')
               
                
                all_players['Division'] = all_players['Division'].astype(str)

               

                all_players['Pass completion ratio'] = all_players['Pas %'].astype(float) / 100.0
                all_players = all_players.drop(columns="Pas %")

        

                all_players['Ps A/90'] = all_players['Ps A/90'].replace({',': '.'}, regex=True)
                all_players['Passes attempted per 90'] = all_players['Ps A/90'].astype(float) 
                all_players = all_players.drop(columns="Ps A/90")

                all_players['Saves'] = all_players['Svh'] + all_players['Svt'] + all_players['Svp']
                all_players['Shots faced'] = all_players['Conc'] + all_players['Saves']
                
                all_players['Save %'] = all_players['Saves'] / all_players['Shots faced']
                all_players['Penalty save %'] = all_players['Pens Saved'] / all_players['Pens Faced']

                all_players['Conceded per 90'] = all_players['Conc'] / all_players['Matches']

                all_players['Saves held per 90'] = all_players['Svh'] / all_players['Matches']
                all_players['Saves tipped per 90'] = all_players['Svt'] / all_players['Matches']
                all_players['Saves parried per 90'] = all_players['Svp'] / all_players['Matches']
                
                
                all_players = all_players.sort_index(axis=1)
              

                all_players = all_players.rename(columns={"Mins": "Minutes played"})
       
        
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return all_players

@app.callback(
    Output('radar', 'figure'),
    Input('radar-type', 'value'),
    Input('scattergram', 'clickData'),
    )

def update_radar(position, clickData):
    name = clickData['points'][0]['hovertext']
    player = percentiles[percentiles['Name'] == name].iloc[0]
    player_val = filtered[filtered['Name'] == name].iloc[0]

    r = []
    for i in range(len(position)):
            r.append(player[position[i]])
    #theta = position
    theta = []
    for i in range(len(position)):
            theta.append(position[i] + ": " + str(player_val[position[i]])[:4] )

    figb = px.line_polar(player, r, theta, line_close=True, title=name, range_r=[0.0, 1.0])
    figb.update_traces(fill='toself')
    figb.update_layout(margin={'l': 80, 'b': 80, 't': 80, 'r': 80},
                paper_bgcolor=styles['secondary'],
                font={
                    'color': styles['text']
                }
            )
    figb.update_polars(bgcolor=styles['primary'])
    return figb

@app.callback(Output('minutes-slider', 'min'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename"),
              )
def update_slider_minutes_min(contents, filename):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename)
        min_value = min(unfiltered['Minutes played'])
        return min_value

@app.callback(Output('minutes-slider', 'max'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename"),
              )
def update_slider_minutes_max(contents, filename):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename)
        max_value = max(unfiltered['Minutes played'])
        return max_value

@app.callback(Output('minutes-slider', 'value'),
                [Input('minutes-slider', 'min'),
               Input('minutes-slider', 'max')])
def update_slider_minutes_value(min_value, max_value): 
        return [min_value, max_value]

@app.callback(Output('age-slider', 'min'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename")
              )
def update_slider_age_min(contents, filename):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename)
        min_value = min(unfiltered['Age'])
        return min_value

@app.callback(Output('age-slider', 'max'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename")
              )
def update_slider_age_max(contents, filename):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename)
        max_value = max(unfiltered['Age'])
        return max_value

@app.callback(Output('age-slider', 'value'),
                [Input('age-slider', 'min'),
               Input('age-slider', 'max')])
def update_slider_age_value(min_value, max_value): 
        return [min_value, max_value]


if __name__ == '__main__':
    app.run_server(host='localhost',port=8080, debug=False, use_reloader=False)
