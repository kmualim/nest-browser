import os
import numpy as np
import time
import base64
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.plotly as py
import flask
import dash
from textwrap import dedent as d
from pandas.io.json import json_normalize
import json

app = dash.Dash('nest-data')
server = app.server

 # Generate default scatter plot
datasets=pd.read_csv("../data/nest_vizdf.csv", sep='\t')
data = []

celltypes = datasets['celltypes'].drop_duplicates()
UNIQUE_CELLTYPES = list(celltypes)

styles ={
    'pre' :{
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
        }
    }
# To add new markers to the dataset
# TODO: Append this to uploading a new file
def add_markers(figure_data, celltypes, plot_type='scatter3d'):# COLOR_FOR_POINTS, plot_type='scatter3d'):
    indices=[]
    color=[]
    nest_data = figure_data
    x=0
    for i in celltypes:
        hover_text = figure_data['celltypes']
        for j in range(len(hover_text)):
            if i==hover_text[j]:
                indices.append(j)#, COLOR_FOR_POINTS[x]])

    traces=[]
    for point_number in indices:
        trace=dict(
                x=[figure_data['EM_x'][point_number]],
                y=[figure_data['EM_y'][point_number]],
                marker=dict(
                    color=color,
                    size=16,
                    opacity=0.5,
                    symbol='cross'
                    ),
                type=plot_type
            )
        if plot_type == 'scatter3d':
            trace['z'] = [figure_data['EM_z'][point_number]]
        traces.append(trace)
    return traces

BACKGROUND = 'rgb(230, 230, 230)'
COLORSCALE = [ [0, "rgb(244, 236, 21)"], [0.3, "rgb(246, 210, 41)"], [0.4, "rgb(134,191,118)"],
                [0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"] ]

COLOR_FOR_POINTS = [ ["rgb(241,49,7)"], ["rgb(241,224,7)"], ["rgb(131,241,7)"], ["rgb(7,241,192)"], ["rgb(7,62,241)"], ["rgb(163,7,241)"], ["rgb(241,7,190)"], ["rgb(106,7,7)" ]]


def scatter_plot_3d(
        x = datasets['hUMAP_x'],
        y = datasets['hUMAP_y'],
        datasets = datasets,
        color = datasets['celltypes'],
        plot_type = 'scatter',
        colorset = COLOR_FOR_POINTS): # fill markers if new dataset

    def axis_template_3d(title, type='linear'):
        return dict(

             showbackground=True,
             backgroundcolor=BACKGROUND,
             gridcolor='rgb(255, 255, 255)',
             title = title,
             zerolinecolor = 'rgb(255, 255, 255)',
             type = type
         )

    def axis_template_2d(title):
        return dict(
            xgap=10, ygap=10,
            backgroundcolor=BACKGROUND,
            gridcolor='rgb(255, 255, 255)',
            title = title,
            zerolinecolor = 'rgb(255, 255, 255)',
            color = '#444'
        )

    def blackout_axis( axis ):
        axis['showgrid'] = False
        axis['zeroline'] = False
        axis['color']  = 'white'
        return axis


    #def normalize_counts (df_of_counts):
    # append color to dots
    def get_color(datasets, colorset):
        celltypes = datasets['celltypes'].drop_duplicates()
        datasets['color'] = 'black'
        unique_celltypes = list(celltypes)
        # there are only 7 celltypes for nest
        x =0
        for i in celltypes:
            matches = datasets.loc[(datasets['celltypes']==i)]
            indices = matches.index.values.astype('int')
            for i in indices:
                datasets.loc[i, 'color']= colorset[x]
            x+=1
        return datasets['color']
    #x=datasets['EM_x']
    #y=datasets['EM_y']
    #z=datasets['EM_z']
    #xlabel = x
    #ylabel = y
    #zlabel = z
    # The data is only being colored depending on its celltypes, maybe we can one-hot encode this
    data = [ dict(
        x = x,
        y = y,
       # z = z,
        mode = 'markers',
        marker = dict (
            color = get_color(datasets, colorset),
            size = 4
            ),
        #marker = dict(
        #        colorscale = COLORSCALE,
        #        colorbar = dict( title = "Counts" ),
        #        line = dict( color = '#444' ),
        #        reversescale = True,
        #        sizeref = 45,
        #        sizemode = 'diameter',
        #        opacity = 0.7,
        #        size = 4,
        #        color = color,
        #    ),
        # normalize counts to a range of 0-1
        #text = normalize_counts(datasets['n_counts']),
        text = datasets['celltypes'],
        type = plot_type,
    ) ]

    layout = dict(
        font = dict( family = 'Raleway' ),
        plot_bgcolor = " #000000",
        hovermode = 'closest',
        margin = dict( r=20, t=0, l=0, b=0 ),
        showlegend = False,
        #scene = dict(
        #    xaxis = axis_template_2d( xlabel ),
        #    yaxis = axis_template_2d( ylabel ),
            #zaxis = axis_template_3d( zlabel ),
        #    camera = dict(
        #        up=dict(x=0, y=0, z=1),
        #        center=dict(x=0, y=0, z=0),
        #        eye=dict(x=0.08, y=2.2, z=0.08)
        #    )
        #),
        clickmode= 'event+select'
    )

    #if plot_type in ['scatter']:
    #    layout['xaxis'] = axis_template_2d(xlabel)
    #    layout['yaxis'] = axis_template_2d(ylabel)
    #    layout['plot_bgcolor'] = BACKGROUND
    #    layout['paper_bgcolor'] = BACKGROUND
    #    data[0]['x'] = datasets['hUMAP_x']
    #    data[0]['y'] = datasets['hUMAP_y']
    #    del layout['scene']
    #    del data[0]['z']

    #if len(markers) > 0:
    #    scales = add_markers(datasets, markers, plot_type= plot_type)
    #    data = data + scales
    return dict( data=data, layout=layout )

FIGURE = scatter_plot_3d(x=datasets['hUMAP_x'], y=datasets['hUMAP_y'], datasets=datasets, plot_type = 'scatter')
STARTING_DATA = datasets

app.layout = html.Div( children=[
    # Row 1: Title of Graph
    html.Div([
        html.H2('Exploring Nest Data',
            style={
                'position' : 'relative',
                'top' : '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size' : '2.0em',
                'color' : '#4D637F'
                }),
            ],  className='row twelve columns', style={'position': 'relative'}),

    # TODO: could attempt to put heatmap here
    # alongside the Graph
    # Row 2: Hover Panel & Display Graph
    html.Div(className='five columns', children=[
        html.Div(className='row', children=[
            html.Div(className='five columns', children=[
                dcc.Dropdown(
                id='categories_of_celltypes',
                options=[{'label':i, 'value':i} for i in datasets['celltypes'].unique()],
                multi=True),
            ]),
            html.Div(className='five columns', children=[
                # Visualization for different strategies
                dcc.RadioItems(
                id='direction',
                options=[
                    {'label':'genomic_position', 'value':'X'},
                    {'label':'celltypes', 'value':'Y'},
                    {'label':'assay', 'value':'Z'}
                ],
                labelStyle = {'display':'inline-block'},
                value='X')
                ], style={'padding-top':'5px'}),
            ], style={'padding-bottom':'20px'}),

        html.Div(className='row', children=[
            dcc.Graph(id='clickable-graph',
                style=dict(width='700px'),
                hoverData=dict(points=[dict(pointNumber=0)]),
                figure=FIGURE),
            ]),

        html.Div(className='row', children=[
                dcc.Slider(
                    min=0,
                    max=5000,
                    step=1000,
                    value=1000,
                    id='n_counts_threshold',
                    marks={0:'0', 1000:'1000', 2000:'2000', 3000: '3000', 4000:'4000', 5000: '5000'})
                ], style={'padding-top':'5px'}),
        ])
    ]
)
#@app.callback(Output('clickable-graph', 'figure'),
#         [Input('n_counts_threshold', 'value')])
# def return_graph_threshold(threshold):
#     x_tmp = datasets.loc[(datasets['n_counts']>threshold)]
#     return scatter_plot_3d(x_tmp)

@app.callback(Output('clickable-graph', 'figure'),
            [Input('n_counts_threshold', 'value'),
            Input('categories_of_celltypes', 'value')])
def highlight_dataset(threshold, categories):
    if categories is None or categories == []:
        categories = UNIQUE_CELLTYPES
    print(categories)
    print(type(categories))
    print(threshold)
    x_tmp = STARTING_DATA[STARTING_DATA['celltypes'].isin(categories)]
    print("here",x_tmp[:5])
    x_tmp_threshold = x_tmp[(x_tmp>threshold).any('n_counts')]
    print(x_tmp_threshold[:5])
    return scatter_plot_3d(datasets=x_tmp_threshold)

# having a selection of stuff and things displayed
# could it be important to have an a similarity matrix etc
# TODO: figure out use case
#@app.callback(Output('selected-data', 'children'),
#        [Input('clickable-graph', 'selectedData')])
#def display_selected_data(selectedData):
#    x = json.dumps(selectedData, indent=2)
    # from json to pandas dataframe
    # could further characterize to different points
#    return x

# zooming in and having the range displayed
# TODO: could change properties of what is displayed
#@app.callback(Output('relayout-data', 'children'),
#        [Input('clickable-graph', 'relayoutData')])
#def display_selected_data(relayoutData):
#return json.dumps(relayoutData, indent=2)


if __name__  == "__main__":
    app.run_server(debug=True)
