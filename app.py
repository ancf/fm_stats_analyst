import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import dash_daq as daq
import pandas as pd
import numpy as np

import plotly.graph_objs as go

import plotly.express as px


app = dash.Dash(__name__, suppress_callback_exceptions=True)

global fm20
fm20 = True
global exclude_pens
exclude_pens = True
                                                          
        
stat_names_fm21 = ['xG per 90',
            'Goals per 90',
            'Conversion Rate (%)',
            'Cross completion ratio',
            'Assists per 90',
            'Headers won ratio',
            'Average rating',
            'Crosses completed per 90',
            'Crosses attempted per 90',
            'Clear cut chances created per 90',
            'Aerial attempts per 90',
            'Dribbles made per game',
            'Pass completion ratio',
            'Shots on target ratio',
            'Key passes per 90',
            'Key tackles per 90',
            'Key headers per 90',
            'Shots on target per 90',
            'Passes completed per 90',
            'Passes attempted per 90',
            'Headers won per 90',
            'Shots per 90',
            'Tackles won per 90',
            'Distance per 90',
            'Interceptions per 90',
            'Tackles attempted per 90',
            'Tackles won ratio',
            'Chances created per 90',
            'Offsides per 90',
            'Mistakes leading to goal per 90',
            'Penalties',
            'Penalties scored',
            'Fouls per 90']
stat_names_fm20 = [
            'Goals per 90',
            'Conversion Rate (%)',
            'Cross completion ratio',
            'Assists per 90',
            'Headers won ratio',
            'Average rating',
            'Crosses completed per 90',
            'Crosses attempted per 90',
            'Aerial attempts per 90',
            'Dribbles made per game',
            'Pass completion ratio',
            'Shots on target ratio',
            'Key passes per 90',
            'Key tackles per 90',
            'Key headers per 90',
            'Shots on target per 90',
            'Passes completed per 90',
            'Passes attempted per 90',
            'Headers won per 90',
            'Shots per 90',
            'Tackles won per 90',
            'Distance per 90',
            'Interceptions per 90',
            'Tackles attempted per 90',
            'Tackles won ratio',
            'Chances created per 90',
            'Offsides per 90',
            'Mistakes leading to goal per 90',
            'Penalties',
            'Penalties scored',
            'Fouls per 90']
#if fm20 == True:
#        stat_names.remove('xG per 90')
#        stat_names.remove('Clear cut chances created per 90')
stat_names = []
stat_names = stat_names_fm20.copy()
stat_names.sort()
percentile_stat_names = stat_names.copy()
percentile_stat_names.remove('Average rating')

styles = {
    
         'primary': '#444444',
         'text': '#FFFFFF',
         'secondary': '#1d1d1d'
    
}

app.layout = html.Div([
        dcc.Tabs([
                dcc.Tab(label='Settings', style={'color': styles['text'], 'backgroundColor': styles['secondary'],}, selected_style={'color': styles['text'], 'backgroundColor': styles['secondary'],}, children=[
                         html.Div([
                                 
                                 daq.BooleanSwitch(id='version-switch', on=False, style={'display': 'inline-block', 'marginRight': '10px'}),
                                 html.P("FM20", id="version-desc", style={'display': 'inline-block'}),
                                 ]),
                         html.Div([
                                 daq.BooleanSwitch(id='pens-switch', on=False, style={'display': 'inline-block', 'marginRight': '10px'}),
                                 html.P("Include penalties in stats", id="pens-desc", style={'display': 'inline-block'}),
                                 
                                 ]), 
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
    Input('age-slider', 'value'),
    Input('pens-switch', 'on'),
    Input('version-switch', 'on')
)
def update_graph(contents, filename, xaxis_column_name, yaxis_column_name, minutes, age, pens, fm20):
        contents = contents[0]
        filename = filename[0]
        
        filtered_players = parse_data(contents, filename, pens, fm20)
        
        filtered_players=filtered_players[filtered_players['Minutes played'] >= minutes[0]]
        filtered_players=filtered_players[filtered_players['Minutes played'] <= minutes[1]]
        filtered_players=filtered_players[filtered_players[xaxis_column_name] > 0]
        filtered_players=filtered_players[filtered_players[yaxis_column_name] > 0]

        #TODO: handle empty filtered_players

        global filtered
        filtered = filtered_players.copy()
        
        global percentiles
        percentiles = filtered_players.drop(columns=['Name', 'Division', 'Average rating', 'Minutes played', 'Age'])

        for i in percentiles.columns:
            percentiles[i] = percentiles[i].rank(pct=True)

         
        percentiles['Fouls per 90'] = percentiles['Fouls per 90'].rank(pct=True, ascending=False)
        percentiles['Offsides per 90'] = percentiles['Offsides per 90'].rank(pct=True, ascending=False)
        percentiles['Mistakes leading to goal per 90'] = percentiles['Mistakes leading to goal per 90'].rank(pct=True, ascending=False)
        


        percentiles['Name'] = filtered_players['Name']
        percentiles['Division'] = filtered_players['Division']
        percentiles['Average rating'] = filtered_players['Average rating']
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
       

def parse_data(contents, filename, pens, fm20):
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
               
                if fm20 == False:
                     
                        all_players = all_players.drop(columns='Rec')
                        all_players['xG'] = all_players['xG'].replace({',': '.'}, regex=True)
                        all_players['xG'] = all_players['xG'].astype(float)
                        
                        if pens == True:
                                all_players['xG per 90'] = (all_players['xG'] - 0.76 * all_players['Pens'].astype(float))/ all_players['Matches']
                        else:
                                all_players['xG per 90'] = all_players['xG'] / all_players['Matches']
                                
                        all_players['xG per 90'] = all_players['xG per 90'].apply(lambda x: max(x, 0.0))
                        all_players = all_players.drop(columns="xG")
                        all_players['Clear cut chances created per 90'] = all_players['CCC'].astype(float) /all_players['Matches']
                        all_players = all_players.drop(columns="CCC")
                        

               
                
                all_players['Fouls per 90'] = all_players['Fls'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="Fls")

               
                if pens == True:
                        all_players['Npg'] = all_players['Gls'].astype(float) - all_players['Pens S'].astype(float) #non penalty goals
                        all_players['Nps'] = all_players['Shots'].astype(float) - all_players['Pens'].astype(float) #non penalty shots
                        all_players['Goals per 90'] = all_players['Npg']/all_players['Matches']
                        all_players['Conversion Rate (%)'] = all_players['Npg'].div(all_players['Nps'].replace(0, np.nan)).fillna(0)
                else:
                        all_players['Goals per 90'] = (all_players['Gls'].astype(float))/all_players['Matches']
                        all_players['Conversion Rate (%)'] = all_players['Gls'].div(all_players['Shots'].replace(0, np.nan)).fillna(0)

                all_players = all_players.drop(columns="Gls")

                all_players['Division'] = all_players['Division'].astype(str)

                all_players['Cross completion ratio'] = all_players['Cr C/A'].astype(float) / 100.0
                all_players = all_players.drop(columns="Cr C/A")

                all_players['Asts/90'] = all_players['Asts/90'].replace({',': '.'}, regex=True)
                all_players['Assists per 90'] = all_players['Asts/90'].astype(float) 
                all_players = all_players.drop(columns="Asts/90")

                all_players['Headers won ratio'] = all_players['Hdr %'].astype(float) / 100.0
                all_players = all_players.drop(columns="Hdr %")

                all_players['Pass completion ratio'] = all_players['Pas %'].astype(float) / 100.0
                all_players = all_players.drop(columns="Pas %")

                all_players['Shots on target ratio'] = all_players['Shot %'].astype(float) / 100.0
                all_players = all_players.drop(columns="Shot %")

                all_players['K Ps/90'] = all_players['K Ps/90'].replace({',': '.'}, regex=True)
                all_players['Key passes per 90'] = all_players['K Ps/90'].astype(float) 
                all_players = all_players.drop(columns="K Ps/90")

                all_players['Key tackles per 90'] = all_players['K Tck'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="K Tck")

                all_players['Key headers per 90'] = all_players['K Hdrs'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="K Hdrs")

                all_players['ShT/90'] = all_players['ShT/90'].replace({',': '.'}, regex=True)
                all_players['Shots on target per 90'] = all_players['ShT/90'].astype(float) 
                all_players = all_players.drop(columns="ShT/90")

                all_players['Ps C/90'] = all_players['Ps C/90'].replace({',': '.'}, regex=True)
                all_players['Passes completed per 90'] = all_players['Ps C/90'].astype(float)
                all_players = all_players.drop(columns="Ps C/90")

                all_players['Ps A/90'] = all_players['Ps A/90'].replace({',': '.'}, regex=True)
                all_players['Passes attempted per 90'] = all_players['Ps A/90'].astype(float) 
                all_players = all_players.drop(columns="Ps A/90")

                all_players['Hdrs W/90'] = all_players['Hdrs W/90'].replace({',': '.'}, regex=True)
                all_players['Headers won per 90'] = all_players['Hdrs W/90'].astype(float) 
                all_players = all_players.drop(columns="Hdrs W/90")

                all_players['Shot/90'] = all_players['Shot/90'].replace({',': '.'}, regex=True)
                all_players['Shots per 90'] = all_players['Shot/90'].astype(float)
                all_players = all_players.drop(columns="Shot/90")

             
                all_players['Tackles won per 90'] = all_players['Tck W'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="Tck W")

                all_players['Distance'] = all_players['Distance'].replace({'km': ''}, regex=True)
                all_players['Distance'] = all_players['Distance'].replace({',': '.'}, regex=True)
                all_players['Distance'] = all_players['Distance'].astype(float)
                all_players['Distance per 90'] = all_players['Distance'] /all_players['Matches']
                all_players = all_players.drop(columns="Distance")

                all_players['Int/90'] = all_players['Int/90'].replace({',': '.'}, regex=True)
                all_players['Interceptions per 90'] = all_players['Int/90'].astype(float) 
                all_players = all_players.drop(columns="Int/90")

                all_players['Tackles won ratio'] = all_players['Tck R'].astype(float) / 100.0
                all_players = all_players.drop(columns="Tck R")

                all_players['Aer A/90'] = all_players['Aer A/90'].replace({',': '.'}, regex=True)
                all_players['Aerial attempts per 90'] = all_players['Aer A/90'].astype(float) 
                all_players = all_players.drop(columns="Aer A/90")

                all_players['Ch C/90'] = all_players['Ch C/90'].replace({',': '.'}, regex=True)
                all_players['Chances created per 90'] = all_players['Ch C/90'].astype(float) 
                all_players = all_players.drop(columns="Ch C/90")

                all_players['Offsides per 90'] = all_players['Off'].astype(float) / all_players['Matches']
                all_players = all_players.drop(columns="Off")

                all_players['Mistakes leading to goal per 90'] = all_players['Gl Mst'].astype(float)/all_players['Matches']
                all_players = all_players.drop(columns="Gl Mst")



                all_players['Penalties'] = all_players['Pens'].astype(float)
                all_players = all_players.drop(columns="Pens")

                all_players['Penalties scored'] = all_players['Pens S'].astype(float)
                all_players = all_players.drop(columns="Pens S")

                all_players['DrbPG'] = all_players['DrbPG'].replace({',': '.'}, regex=True)
                all_players['Dribbles made per game'] = all_players['DrbPG'].astype(float) 
                all_players = all_players.drop(columns="DrbPG")

            

                all_players['Crosses attempted per 90'] = all_players['Cr A'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="Cr A")


                all_players['Crosses completed per 90'] = all_players['Cr C'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="Cr C")

                all_players['Av Rat'] = all_players['Av Rat'].astype(float)

                all_players['Tackles attempted per 90'] = all_players['Tck A'].astype(float) /all_players['Matches']
                all_players = all_players.drop(columns="Tck A")

                #all_players = all_players.drop(columns="Tck")
             

                all_players = all_players.rename(columns={"Av Rat": "Average rating"})
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
              Input('pens-switch', 'on'),
              Input('version-switch', 'on')
              )
def update_slider_minutes_min(contents, filename, pens, fm20):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename, pens, fm20)
        min_value = min(unfiltered['Minutes played'])
        return min_value

@app.callback(Output('minutes-slider', 'max'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename"),
              Input('pens-switch', 'on'),
              Input('version-switch', 'on'))
def update_slider_minutes_max(contents, filename, pens, fm20):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename, pens, fm20)
        max_value = max(unfiltered['Minutes played'])
        return max_value

@app.callback(Output('minutes-slider', 'value'),
                [Input('minutes-slider', 'min'),
               Input('minutes-slider', 'max')])
def update_slider_minutes_value(min_value, max_value): 
        return [min_value, max_value]

@app.callback(Output('age-slider', 'min'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename"),
              Input('pens-switch', 'on'),
              Input('version-switch', 'on'))
def update_slider_age_min(contents, filename, pens, fm20):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename, pens, fm20)
        min_value = min(unfiltered['Age'])
        return min_value

@app.callback(Output('age-slider', 'max'),
              Input("upload-data", "contents"),
              Input("upload-data", "filename"),
              Input('pens-switch', 'on'),
              Input('version-switch', 'on'))
def update_slider_age_max(contents, filename, pens, fm20):
        contents = contents[0]
        filename = filename[0]
        
        unfiltered = parse_data(contents, filename, pens, fm20)
        max_value = max(unfiltered['Age'])
        return max_value

@app.callback(Output('age-slider', 'value'),
                [Input('age-slider', 'min'),
               Input('age-slider', 'max')])
def update_slider_age_value(min_value, max_value): 
        return [min_value, max_value]
@app.callback(

    Output('xaxis-column', 'options'),
    Output('yaxis-column', 'options'),
    Output('radar-type', 'options'),
    Output('xaxis-column', 'value'),
    Output('yaxis-column', 'value'),
    Output('radar-type', 'value'),
    Output('version-desc', 'children'),
    Input('version-switch', 'on')
)
def update_switch(on):
        fm20 = on
        if fm20 == True:
                stat_names = stat_names_fm20.copy()
                version_desc = "FM20"
        else:
                stat_names = stat_names_fm21.copy()
                version_desc = "FM21"

        stat_names.sort()
        percentile_stat_names = stat_names.copy()
        percentile_stat_names.remove('Average rating')    
        
        return stat_names, stat_names, percentile_stat_names, stat_names[0], stat_names[1], [percentile_stat_names[0], percentile_stat_names[1],
                                                                                             percentile_stat_names[2]], version_desc

@app.callback(
    Output('pens-desc', 'children'),
    Input('pens-switch', 'on'),
)
def update_switch(on):
        exclude_pens = on
        
        if exclude_pens == True:
                #stat_names = stat_names_fm20.copy()
                pens_desc = "Exclude penalties in stats"
        else:
                #stat_names = stat_names_fm21.copy()
                pens_desc = "Include penalties in stats"


        
        return pens_desc

if __name__ == '__main__':
    app.run_server(host='localhost',port=8080, debug=False, use_reloader=False)
